from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import ListView

from pve_tui.core import models


class ServerActionList(Widget):
    servers: list[models.ServerBrief]

    def __init__(self, servers: list[models.ServerBrief], **kwargs) -> None:
        super().__init__(**kwargs)
        self.servers = servers

    def compose(self) -> ComposeResult:
        yield ListView()
