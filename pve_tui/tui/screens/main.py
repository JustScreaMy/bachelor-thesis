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

from pve_tui.tui.widgets import MultiselectListView, ServerDetailView
from pve_tui.tui.widgets import MultiselectListItem
from pve_tui.tui.widgets import SplitView
from pve_tui.tui.widgets import ServerBrief


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
            background: $surface;
            padding: 0 1;
        }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('r', 'refresh', 'Refresh Server List'),
        Binding('q', 'quit', 'Quit'),
    ]

    def action_quit(self) -> None:
        self.app.exit()

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
        cluster_service = self.app.cluster_service

        self.log('Refreshing server list...')
        server_list = self.query_one('#server-list', MultiselectListView)

        servers_data = await cluster_service.fetch_servers_brief()
        # Sort data to match expected display order
        servers_data.sort(key=lambda x: x.server_id)

        # Snapshot current children for reconciliation
        current_children = list(server_list.children)
        ui_index = 0

        for server in servers_data:
            item_id = f'{server.type}-{server.server_id}'
            inserted_or_updated = False

            while not inserted_or_updated:
                # If we exhausted the current UI list, append the remaining
                if ui_index >= len(current_children):
                    new_item = MultiselectListItem(ServerBrief(server), id=item_id)
                    await server_list.append(new_item)
                    inserted_or_updated = True
                    break

                current_child = current_children[ui_index]

                # Get current child ID
                current_id = current_child.id

                try:
                    if current_id and '-' in current_id:
                        parts = current_id.split('-')
                        current_type = parts[0]
                        current_sid = int(parts[1])
                    else:
                        raise ValueError('Invalid ID')
                except (ValueError, IndexError, AttributeError):
                    # Invalid or unexpected child, remove it
                    await current_child.remove()
                    current_children.pop(ui_index)
                    continue

                if current_sid == server.server_id and current_type == server.type:
                    brief = current_child.query_one(ServerBrief)
                    brief.update(server)

                    ui_index += 1

                    inserted_or_updated = True

                elif current_sid > server.server_id:
                    new_item = MultiselectListItem(ServerBrief(server), id=item_id)

                    await server_list.mount(new_item, before=current_child)

                    inserted_or_updated = True
                else:
                    await current_child.remove()

                    current_children.pop(ui_index)

        while ui_index < len(current_children):
            await current_children[ui_index].remove()
            ui_index += 1

        if len(server_list) > 0 and server_list.index is None:
            server_list.index = 0

        self.log('Refreshing server list finished')

    @on(MultiselectListView.Highlighted)
    def _handle_highlighted(self, message: MultiselectListView.Highlighted) -> None:
        """Handle when a server item is highlighted."""
        server_list = self.query_one('#server-list', MultiselectListView)

        # Only update if no servers are selected
        if len(server_list.selected_children) == 0 and message.item is not None:
            server_brief = message.item.query_one(ServerBrief).server_info
            split_view = self.query_one('#split-view', SplitView)
            self._fetch_and_display_server_details(server_brief, split_view)

    @on(MultiselectListItem.Selected)
    def _handle_selected(self, _message: MultiselectListItem.Selected) -> None:
        """Handle when a server item is selected/deselected."""
        server_list = self.query_one('#server-list', MultiselectListView)
        split_view = self.query_one('#split-view', SplitView)
        selected_children = server_list.selected_children

        if selected_children:
            selected_servers = [
                child.query_one(ServerBrief).server_info for child in selected_children
            ]
            split_view.set_right_pane(ServerActionList(selected_servers))
        else:
            highlighted_item = server_list.highlighted_child
            if highlighted_item is not None:
                server_brief = highlighted_item.query_one(ServerBrief).server_info
                self._fetch_and_display_server_details(server_brief, split_view)

    @work(exclusive=True)
    async def _fetch_and_display_server_details(
        self,
        server_brief: models.ServerBrief,
        split_view: SplitView,
    ) -> None:
        """Fetch full server details and display them in the detail view."""
        cluster_service = self.app.cluster_service

        try:
            if server_brief.type == models.ServerType.VM:
                server_details = await cluster_service.fetch_server_details_qemu(
                    server_brief.node,
                    server_brief.server_id,
                )
            else:  # LXC
                server_details = await cluster_service.fetch_server_details_lxc(
                    server_brief.node,
                    server_brief.server_id,
                )

            split_view.set_right_pane(ServerDetailView(server_details))
        except Exception as e:
            self.log(f'Error fetching server details: {e}')

    def on_mount(self) -> None:
        self.action_refresh()
