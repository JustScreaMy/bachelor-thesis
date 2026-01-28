from typing import TYPE_CHECKING

from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer
from textual.widgets import Header
from textual.widgets import Static


if TYPE_CHECKING:
    from pve_tui.tui.app import PveTuiApp

from pve_tui.tui.widgets import MultiselectListView
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


        #details-view {
            padding: 2;
            content-align: center middle;
            text-style: italic;
            color: $text-muted;
        }
    """

    BINDINGS = [
        ('r', 'refresh', 'Refresh Server List'),
        ('q', 'quit', 'Quit'),
    ]

    def action_quit(self) -> None:
        self.app.exit()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SplitView(
            left=MultiselectListView(id='server-list'),
            right=Static('Select a server to view details', id='details-view'),
            sidebar_width=1 / 3,
        )
        yield Footer()

    @work(exclusive=True)
    async def action_refresh(self) -> None:
        cluster_service = self.app.cluster_service

        self.log('Refreshing server list...')
        server_list = self.query_one('#server-list', MultiselectListView)

        servers_data = await cluster_service.get_servers_brief()
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

    def on_mount(self) -> None:
        self.action_refresh()
