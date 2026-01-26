import random

from textual.screen import Screen
from textual.widgets import Static, ListView, ListItem
from textual.app import ComposeResult

from pve_tui.shared import models
from pve_tui.tui.widgets import SplitView
from pve_tui.tui.widgets import ServerBrief


class MainScreen(Screen):

    CSS = '''
        #server-list {
            scrollbar-visibility: hidden;
        }
    '''

    BINDINGS = [
        ('r', 'refresh', 'Refresh Server List'),
    ]

    def compose(self) -> ComposeResult:
        yield SplitView(
            left=ListView(id='server-list'),
            right=Static('Details Placeholder', id='details-view')
        )

    def action_refresh(self) -> None:
        self.log('Refreshing server list...')
        server_list = self.query_one('#server-list', ListView)

        server_list.clear()

        for i in range(25):
            random_status = random.choice(list(models.ServerStatus))
            random_id = random.randint(100,999)

            random_brief = models.ServerBrief(
                server_id=random_id,
                name=f'Server {random_id}',
                status=random_status,
                cpus=random.randint(1,16),
                cpu_usage=random.randint(0,100) if random_status == models.ServerStatus.Running else 0,
                memory=random.randint(2048,65536),
                memory_used=random.randint(1024,32768) if random_status == models.ServerStatus.Running else 0,
                uptime=random.randint(3600,86400) if random_status == models.ServerStatus.Running else 0,
            )
            server_list.append(ListItem(ServerBrief(random_brief)))

        if len(server_list) > 0:
            server_list.index = 0

    def on_mount(self) -> None:
        self.action_refresh()

    # def on_list_view_selected(self, event: ListView.Selected) -> None:
    #     self.log(f'Selected server: {event.item.children[0].content}')
