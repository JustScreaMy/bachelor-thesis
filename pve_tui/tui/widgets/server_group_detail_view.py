from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import DataTable
from textual.widgets import Static

from pve_tui.core import models


class ServerGroupDetailView(VerticalScroll):
    """A widget to display detailed information about a server group."""

    DEFAULT_CSS = """
    ServerGroupDetailView {
        height: 100%;
        padding: 1 2;
    }

    .group-title {
        color: $primary-lighten-1;
        text-style: bold;
    }

    .group-summary {
        color: $text-muted;
        margin-bottom: 1;
    }

    ServerGroupDetailView DataTable {
        height: auto;
        margin-top: 1;
    }
    """

    def __init__(self, group: models.ServerGroupBrief, **kwargs) -> None:
        super().__init__(**kwargs)
        self.group = group

    def compose(self) -> ComposeResult:
        running = sum(
            1 for s in self.group.servers if s.status == models.ServerStatus.Running
        )
        total = len(self.group.servers)

        yield Static(self.group.name, classes='group-title')
        yield Static(f'{running}/{total} online', classes='group-summary')

        table = DataTable()
        table.add_columns('', 'ID', 'Name', 'Type', 'Node')
        for s in self.group.servers:
            icon = '●' if s.status == models.ServerStatus.Running else '○'
            table.add_row(
                icon,
                str(s.server_id),
                s.name,
                s.type.value.upper(),
                s.node,
            )
        yield table
