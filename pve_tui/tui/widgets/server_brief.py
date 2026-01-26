from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.widget import Widget
from textual.widgets import Static

from pve_tui.shared import models

class ServerBrief(Widget):
    DEFAULT_CSS = '''
        ServerBrief {
            height: auto;
            border: hkey gray;
        }
    '''

    can_focus = True

    def __init__(self, server_info: models.ServerBrief, **kwargs) -> None:
        super().__init__(**kwargs)
        self.server_info = server_info

    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Static(f'{self.server_info.name} (ID: {self.server_info.server_id})', classes='server-name'),
            Static(f'Status: {self.server_info.status.value}', classes='server-status'),
            Static(f'CPU: {self.server_info.cpus} cores, Usage: {self.server_info.cpu_usage}%', classes='server-cpu'),
            Static(f'Memory: {self.server_info.memory} MB, Used: {self.server_info.memory_used} MB',
                   classes='server-memory'),
            Static(f'Uptime: {self.server_info.uptime} seconds', classes='server-uptime'),
        )
