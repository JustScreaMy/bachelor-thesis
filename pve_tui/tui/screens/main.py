import random

from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem, Header, Footer
from textual.app import ComposeResult

from pve_tui.shared import models
from pve_tui.shared.api_client import APIClient
from pve_tui.tui.widgets import SplitView
from pve_tui.tui.widgets import ServerBrief


class MainScreen(Screen):
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

    def action_refresh(self) -> None:
        # We need to help him with typing here, because self.app is a Generic and not my instance
        api_client: APIClient = self.app.api_client

        self.log("Refreshing server list...")
        server_list = self.query_one("#server-list", ListView)
        server_list.clear()

        servers_data = api_client.get_servers_brief()

        self.log(api_client.get_nodes())

        self.log(servers_data)

        for server in servers_data:

            server_list.append(ListItem(ServerBrief(server)))

        if len(server_list) > 0:
            server_list.index = 0

        self.log("Refreshing server list finished")

    def on_mount(self) -> None:
        self.action_refresh()

    # def on_list_view_selected(self, event: ListView.Selected) -> None:
    #     self.log(f'Selected server: {event.item.children[0].content}')
