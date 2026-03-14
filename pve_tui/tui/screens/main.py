from enum import auto
from enum import Enum
from typing import ClassVar
from typing import TYPE_CHECKING

from textual import on
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.binding import BindingType
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header

from pve_tui.core import models
from pve_tui.tui.widgets.server_action_list import ServerActionList

if TYPE_CHECKING:
    from pve_tui.tui.app import PveTuiApp

from pve_tui.tui.widgets import (
    MultiselectListView,
    ServerDetailView,
    ServerGroupBrief,
    ServerGroupDetailView,
)
from pve_tui.tui.widgets import MultiselectListItem
from pve_tui.tui.widgets import SplitView
from pve_tui.tui.widgets import ServerBrief


class ViewMode(Enum):
    SERVERS = auto()
    GROUPS = auto()


class MainScreen(Screen):
    if TYPE_CHECKING:
        app: 'PveTuiApp'

    CSS = """
        Screen {
            layout: vertical;
        }

        #server-list {
            height: 100%;
            scrollbar-visibility: hidden;
            scrollbar-size: 0 0;
            background: $surface;
            padding: 0 1;
        }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('r', 'refresh', 'Refresh Server List'),
        Binding('g', 'toggle_view_mode', 'Toggle Servers/Groups'),
        Binding('q', 'quit', 'Quit'),
    ]

    current_view_mode: ViewMode = ViewMode.SERVERS
    _all_servers: list[models.ServerBrief] = []

    def action_quit(self) -> None:
        self.app.exit()

    async def action_toggle_view_mode(self) -> None:
        if self.current_view_mode == ViewMode.SERVERS:
            self.current_view_mode = ViewMode.GROUPS
        else:
            self.current_view_mode = ViewMode.SERVERS

        # Clear selections when switching modes
        server_list = self.query_one('#server-list', MultiselectListView)
        for child in server_list.selected_children:
            child.selected = False

        await self.refresh_list_ui()
        server_list.focus()

    def _get_groups(self) -> list[models.ServerGroupBrief]:
        groups_dict: dict[str, list[models.ServerBrief]] = {}
        for server in self._all_servers:
            for tag in server.tags:
                if tag.startswith('pve-tui-'):
                    group_name = tag[len('pve-tui-') :]
                    if group_name not in groups_dict:
                        groups_dict[group_name] = []
                    groups_dict[group_name].append(server)

        return [
            models.ServerGroupBrief(name=name, servers=servers)
            for name, servers in sorted(groups_dict.items())
        ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SplitView(
            left=MultiselectListView(id='server-list'),
            right=ServerActionList([]),
            sidebar_width=1 / 3,
            id='split-view',
        )
        yield Footer()

    @work(exclusive=True)
    async def action_refresh(self) -> None:
        discovery_service = self.app.discovery_service

        self.log('Refreshing server list...')
        try:
            self._all_servers = await discovery_service.fetch_all_servers()
        except Exception as e:
            self.log(f'Error during refresh: {e}')
            self.notify(
                f'Failed to refresh server list: {e}',
                severity='error',
            )
            return

        # Sort data to match expected display order
        self._all_servers.sort(key=lambda x: x.server_id)

        await self.refresh_list_ui()
        self.log('Refreshing server list finished')

    async def refresh_list_ui(self) -> None:
        server_list = self.query_one('#server-list', MultiselectListView)

        if self.current_view_mode == ViewMode.SERVERS:
            items_to_display = [
                (f'{s.type}-{s.server_id}', s) for s in self._all_servers
            ]
            widget_class = ServerBrief
        else:
            groups = self._get_groups()
            items_to_display = [(f'group-{g.name}', g) for g in groups]
            widget_class = ServerGroupBrief

        # Snapshot current children for reconciliation
        current_children = list(server_list.children)
        ui_index = 0

        for item_id, item_data in items_to_display:
            inserted_or_updated = False

            while not inserted_or_updated:
                # If we exhausted the current UI list, append the remaining
                if ui_index >= len(current_children):
                    new_item = MultiselectListItem(
                        widget_class(item_data),
                        id=item_id,
                    )
                    await server_list.append(new_item)
                    inserted_or_updated = True
                    break

                current_child = current_children[ui_index]
                current_id = current_child.id

                # Define a helper for comparison
                is_after = False
                if self.current_view_mode == ViewMode.SERVERS:
                    # item_id is f'{type}-{sid}'
                    try:
                        _, curr_sid_str = current_id.split('-')
                        _, item_sid_str = item_id.split('-')
                        is_after = int(curr_sid_str) > int(item_sid_str)
                    except (ValueError, AttributeError):
                        is_after = current_id > item_id
                else:
                    is_after = current_id > item_id

                if current_id == item_id:
                    brief = current_child.query_one(widget_class)
                    brief.update(item_data)

                    ui_index += 1
                    inserted_or_updated = True

                elif is_after:
                    new_item = MultiselectListItem(
                        widget_class(item_data),
                        id=item_id,
                    )

                    await server_list.mount(new_item, before=current_child)

                    inserted_or_updated = True
                else:
                    await current_child.remove()
                    current_children.pop(ui_index)

        while ui_index < len(current_children):
            await current_children[ui_index].remove()
            ui_index += 1

        if len(server_list) > 0:
            # Re-validate the index and force a highlight refresh
            current_index = server_list.index if server_list.index is not None else 0
            validated_index = server_list.validate_index(current_index)

            # If the index is already what we want, the watcher might not fire
            # if we just set it. We want to ensure it fires.
            server_list.index = None
            server_list.index = validated_index
        else:
            server_list.index = None

    @on(MultiselectListView.Highlighted)
    def _handle_highlighted(self, message: MultiselectListView.Highlighted) -> None:
        """Handle when an item is highlighted."""
        server_list = self.query_one('#server-list', MultiselectListView)
        split_view = self.query_one('#split-view', SplitView)

        # Only update if no items are selected
        if len(server_list.selected_children) == 0 and message.item is not None:
            if self.current_view_mode == ViewMode.SERVERS:
                server_brief = message.item.query_one(ServerBrief).server_info
                self._fetch_and_display_server_details(server_brief, split_view)
            else:
                group_info = message.item.query_one(ServerGroupBrief).group_info
                split_view.set_right_pane(ServerGroupDetailView(group_info))

    @on(MultiselectListItem.Selected)
    def _handle_selected(self, _message: MultiselectListItem.Selected) -> None:
        """Handle when an item is selected/deselected."""
        server_list = self.query_one('#server-list', MultiselectListView)
        split_view = self.query_one('#split-view', SplitView)
        selected_children = server_list.selected_children

        if selected_children:
            selected_servers = []
            if self.current_view_mode == ViewMode.SERVERS:
                selected_servers = [
                    child.query_one(ServerBrief).server_info
                    for child in selected_children
                ]
            else:
                for child in selected_children:
                    group_info = child.query_one(ServerGroupBrief).group_info
                    selected_servers.extend(group_info.servers)

            # De-duplicate servers if they are in multiple groups
            unique_servers = {s.server_id: s for s in selected_servers}.values()
            split_view.set_right_pane(ServerActionList(list(unique_servers)))
        else:
            highlighted_item = server_list.highlighted_child
            if highlighted_item is not None:
                if self.current_view_mode == ViewMode.SERVERS:
                    server_brief = highlighted_item.query_one(ServerBrief).server_info
                    self._fetch_and_display_server_details(server_brief, split_view)
                else:
                    group_info = highlighted_item.query_one(ServerGroupBrief).group_info
                    split_view.set_right_pane(ServerGroupDetailView(group_info))

    @work(exclusive=True)
    async def _fetch_and_display_server_details(
        self,
        server_brief: models.ServerBrief,
        split_view: SplitView,
    ) -> None:
        """Fetch full server details and display them in the detail view."""
        resource_service = self.app.resource_service

        try:
            if server_brief.type == models.ServerType.VM:
                server_details = await resource_service.fetch_server_details_qemu(
                    server_brief.node,
                    server_brief.server_id,
                )
            else:  # LXC
                server_details = await resource_service.fetch_server_details_lxc(
                    server_brief.node,
                    server_brief.server_id,
                )

            split_view.set_right_pane(ServerDetailView(server_details))
        except Exception as e:
            self.log(f'Error fetching server details: {e}')

    def on_mount(self) -> None:
        self.query_one('#server-list').focus()
        self.action_refresh()
