import random

from textual.screen import Screen
from textual.widgets import Static
from textual.app import ComposeResult
from textual.containers import VerticalScroll

from pve_tui.tui.widgets import SplitView


class MainScreen(Screen):

    BINDINGS = [
        ('r', 'refresh', 'Refresh Server List'),
    ]

    def compose(self) -> ComposeResult:
        yield SplitView(
            left=VerticalScroll(id='server-list'),
            right=Static('Details Placeholder', id='details-view')
        )

    def action_refresh(self) -> None:
        self.log('Refreshing server list...')
        server_list = self.query_one('#server-list', VerticalScroll)

        server_list.remove_children()

        for i in range(100):
            server_list.mount(Static(f'Server {i+random.randint(1,1000)}'))

    def on_mount(self) -> None:
        self.action_refresh()

    # def on_list_view_selected(self, event: ListView.Selected) -> None:
    #     self.log(f'Selected server: {event.item.children[0].content}')
