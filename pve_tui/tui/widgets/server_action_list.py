from typing import TYPE_CHECKING

from textual import events
from textual import on
from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Label
from textual.widgets import OptionList
from textual.widgets import Static
from textual.widgets.option_list import Option

from pve_tui.core import models

if TYPE_CHECKING:
    from pve_tui.tui.app import PveTuiApp


class ServerActionList(Vertical):
    """Widget to display actions for selected servers/groups using OptionList."""

    can_focus = True

    if TYPE_CHECKING:
        app: 'PveTuiApp'

    DEFAULT_CSS = """
    ServerActionList {
        padding: 1 2;
        background: $surface;
    }

    .action-header {
        color: $text;
        text-style: bold;
        margin-bottom: 1;
        text-align: center;
    }

    #action-options {
        border: none;
        background: $surface;
        background-tint: transparent;
        height: auto;
        min-height: 4;
    }

    #action-options:focus {
        background: $surface;
        background-tint: transparent;
    }

    #action-options.-focused {
        background: $surface;
        background-tint: transparent;
    }

    #action-options > .option-list--option {
        padding: 0 1;
    }

    #action-options > .option-list--option.-highlight {
        background: $accent;
        color: $text;
        text-style: bold;
    }
    """

    servers = reactive[list[models.ServerBrief]](list, recompose=True)
    """The list of currently selected servers to show actions for."""

    groups = reactive[list[models.ServerGroupBrief]](list, recompose=True)
    """The list of currently selected groups."""

    def __init__(
        self,
        servers: list[models.ServerBrief] | None = None,
        groups: list[models.ServerGroupBrief] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.servers = servers if servers is not None else []
        self.groups = groups if groups is not None else []

    def compose(self) -> ComposeResult:
        if not self.servers and not self.groups:
            yield Static('No selection', classes='action-header')
            return

        if self.groups:
            header_text = (
                f'Actions for {len(self.groups)} groups'
                if len(self.groups) > 1
                else f'Actions for group {self.groups[0].name}'
            )
        else:
            header_text = (
                f'Actions for {len(self.servers)} servers'
                if len(self.servers) > 1
                else f'Actions for {self.servers[0].name}'
            )

        yield Label(header_text, classes='action-header')

        # Logic to enable/disable options based on current status
        can_start = any(s.status == models.ServerStatus.Stopped for s in self.servers)
        can_stop = any(s.status == models.ServerStatus.Running for s in self.servers)

        options = [
            Option('Start', id='start', disabled=not can_start),
            Option('Stop (Power Off)', id='stop', disabled=not can_stop),
            Option('Reboot', id='reboot', disabled=not can_stop),
            Option('Shutdown', id='shutdown', disabled=not can_stop),
            Option('---', disabled=True),
        ]

        if self.groups:
            options.append(Option('Remove Group(s)', id='remove_groups'))
        else:
            options.append(Option('Create Group', id='create_group'))
            if len(self.servers) == 1:
                # Add options to remove from existing groups
                server = self.servers[0]
                server_groups = [
                    t[len('pve-tui-') :]
                    for t in server.tags
                    if t.startswith('pve-tui-')
                ]
                for gname in server_groups:
                    options.append(
                        Option(f'Remove from {gname}', id=f'remove_from_group:{gname}'),
                    )

        options.append(Option('---', disabled=True))
        options.append(Option('Create Snapshot', id='create_snapshot'))
        options.append(Option('Rollback to Latest', id='rollback_latest'))

        yield OptionList(*options, id='action-options')

    def on_focus(self, event: events.Focus) -> None:
        """When the widget is focused, delegate focus to the OptionList."""
        try:
            self.query_one('#action-options', OptionList).focus()
        except Exception:
            pass

    @on(OptionList.OptionSelected, '#action-options')
    @work
    async def handle_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle when an action is selected from the list."""
        action_id = event.option_id
        if not action_id:
            return

        if action_id in ('start', 'stop', 'reboot', 'shutdown'):
            self.run_status_action(action_id)
        elif action_id == 'create_group':
            await self.prompt_create_group()
        elif action_id == 'remove_groups':
            self.run_remove_groups()
        elif action_id.startswith('remove_from_group:'):
            self.run_remove_from_group(action_id.split(':', 1)[1])
        elif action_id == 'create_snapshot':
            await self.prompt_create_snapshot()
        elif action_id == 'rollback_latest':
            self.run_rollback_latest()

    async def prompt_create_group(self) -> None:
        """Prompt for a group name and create it."""
        from pve_tui.tui.screens.input_modal import InputModal

        name = await self.app.push_screen_wait(
            InputModal('Create Group', placeholder='Group name...'),
        )
        if name:
            self.run_create_group(name)

    async def prompt_create_snapshot(self) -> None:
        """Prompt for a snapshot name and create it."""
        from pve_tui.tui.screens.input_modal import InputModal

        name = await self.app.push_screen_wait(
            InputModal('Create Snapshot', placeholder='Snapshot name...'),
        )
        if name:
            self.run_create_snapshot(name)

    def _get_target_servers(self) -> list[models.ServerBrief]:
        """Collects all unique servers from current selection or groups."""
        if self.groups:
            all_group_servers = []
            for g in self.groups:
                all_group_servers.extend(g.servers)
            # De-duplicate
            return list({s.server_id: s for s in all_group_servers}.values())
        return self.servers

    @work(exclusive=True)
    async def run_create_snapshot(self, name: str) -> None:
        """Creates a snapshot for all targeted servers."""
        target_servers = self._get_target_servers()
        if not target_servers:
            return

        self.notify(
            f"Creating snapshot '{name}' for {len(target_servers)} server(s)...",
        )
        successes, failures = await self.app.action_service.snapshots.create_many(
            target_servers,
            name,
        )

        if successes:
            self.notify(f"Snapshot '{name}' triggered for {len(successes)} server(s).")
        if failures:
            self.notify(
                f'Failed to create snapshot for {len(failures)} server(s).',
                severity='error',
            )

        await self._trigger_refresh()

    @work(exclusive=True)
    async def run_rollback_latest(self) -> None:
        """Rolls back all targeted servers to their latest snapshots."""
        target_servers = self._get_target_servers()
        if not target_servers:
            return

        self.notify(
            f'Rolling back {len(target_servers)} server(s) to latest snapshots...',
        )
        (
            successes,
            failures,
        ) = await self.app.action_service.snapshots.rollback_to_latest_many(
            target_servers,
        )

        if successes:
            self.notify(
                f'Successfully triggered rollback for {len(successes)} server(s).',
            )
        if failures:
            self.notify(
                f'Failed to rollback {len(failures)} server(s). Check if they have snapshots.',
                severity='error',
            )

        await self._trigger_refresh()

    @work(exclusive=True)
    async def run_create_group(self, name: str) -> None:
        """Adds all selected servers to the specified group."""
        self.notify(f"Adding servers to group '{name}'...")
        (
            successes,
            failures,
        ) = await self.app.action_service.groups.create_group_with_servers(
            self.servers,
            name,
        )

        if successes:
            self.notify(f"Group '{name}' updated for {len(successes)} server(s).")
        if failures:
            self.notify(
                f'Failed to update group for {len(failures)} server(s).',
                severity='error',
            )

        await self._trigger_refresh()

    @work(exclusive=True)
    async def run_remove_groups(self) -> None:
        """Removes the selected groups."""
        self.notify(f'Removing {len(self.groups)} group(s)...')
        successes, failures = await self.app.action_service.groups.remove_groups(
            self.groups,
        )

        if successes:
            self.notify(f'Successfully removed {len(self.groups)} group(s).')
        if failures:
            self.notify('Failed to remove some group tags.', severity='error')

        await self._trigger_refresh()

    @work(exclusive=True)
    async def run_remove_from_group(self, group_name: str) -> None:
        """Removes a single server from a specific group."""
        if not self.servers:
            return
        server = self.servers[0]
        self.notify(f"Removing {server.name} from group '{group_name}'...")
        try:
            await self.app.action_service.groups.remove_from_group(server, group_name)
            self.notify(f"Removed from group '{group_name}'.")
        except Exception as e:
            self.notify(f'Failed: {e}', severity='error')

        await self._trigger_refresh()

    @work(exclusive=True)
    async def run_status_action(self, action_name: str) -> None:
        """Executes the status action on all selected servers."""

        status_manager = self.app.action_service.status

        # Map action names to manager methods
        action_map = {
            'start': (models.ServerStatus.Stopped, status_manager.start_many),
            'stop': (models.ServerStatus.Running, status_manager.stop_many),
            'reboot': (models.ServerStatus.Running, status_manager.reboot_many),
            'shutdown': (models.ServerStatus.Running, status_manager.shutdown_many),
        }

        if action_name not in action_map:
            return

        target_status, action_func = action_map[action_name]

        # Filter servers that can actually perform this action
        target_servers = [s for s in self.servers if s.status == target_status]

        if not target_servers:
            return

        self.notify(f'Executing {action_name} on {len(target_servers)} server(s)...')

        successes, failures = await action_func(target_servers)

        if successes:
            self.notify(
                f'Successfully triggered {action_name} for {len(successes)} server(s).',
            )
        if failures:
            self.notify(
                f'Failed to {action_name} {len(failures)} server(s).',
                severity='error',
            )

        await self._trigger_refresh()

    async def _trigger_refresh(self) -> None:
        """Triggers refreshes of the main list."""
        import asyncio
        from typing import cast

        from pve_tui.tui.screens.main import MainScreen

        if isinstance(self.screen, MainScreen):
            main_screen = cast(MainScreen, self.screen)

            # Wait a moment for Proxmox to initiate the task
            await asyncio.sleep(1.5)
            main_screen.action_refresh()

            # Optional: Refresh again after a longer delay for slower transitions
            await asyncio.sleep(3.0)
            main_screen.action_refresh()
