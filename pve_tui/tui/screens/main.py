from typing import TYPE_CHECKING

from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem, Header, Footer
from textual.app import ComposeResult
from textual import work

if TYPE_CHECKING:
    from pve_tui.tui.app import PveTuiApp

from pve_tui.tui.widgets import SplitView
from pve_tui.tui.widgets import ServerBrief


class MainScreen(Screen):
    if TYPE_CHECKING:
        app: "PveTuiApp"

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
        ("r", "refresh", "Refresh Server List"),
        ("q", "quit", "Quit"),
    ]

    def action_quit(self) -> None:
        self.app.exit()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield SplitView(
            left=ListView(id="server-list"),
            right=Static("Select a server to view details", id="details-view"),
            sidebar_width=1 / 3,
        )
        yield Footer()

    @work(exclusive=True)
    async def action_refresh(self) -> None:
        cluster_service = self.app.cluster_service

        self.log("Refreshing server list...")
        server_list = self.query_one("#server-list", ListView)

        # Clear on the main thread (safe since workers run in the same thread but different task,
        # but modifying UI is safe in Textual workers as they are asyncio tasks on the main loop)
        await server_list.clear()

        servers_data = await cluster_service.get_servers_brief()

        self.log(await cluster_service.get_nodes())

        self.log(servers_data)

        for server in sorted(servers_data, key=lambda x: x.server_id):
            await server_list.append(ListItem(ServerBrief(server)))

        if len(server_list) > 0:
            server_list.index = 0

        self.log("Refreshing server list finished")

    def on_mount(self) -> None:
        self.action_refresh()

    # def on_list_view_selected(self, event: ListView.Selected) -> None:
    #     self.log(f'Selected server: {event.item.children[0].content}')