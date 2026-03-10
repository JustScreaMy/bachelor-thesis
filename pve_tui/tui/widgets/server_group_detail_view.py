from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import DataTable
from textual.widgets import Label
from textual.widgets import Static

from pve_tui.core import models


class ServerGroupDetailView(VerticalScroll):
    """A widget to display detailed information about a server group."""

    DEFAULT_CSS = """
    ServerGroupDetailView {
        height: 100%;
        padding: 2;
    }

    .group-title {
        color: $primary;
        text-style: bold underline;
        margin-bottom: 1;
    }

    .group-info {
        margin-bottom: 1;
    }
    """

    def __init__(self, group: models.ServerGroupBrief, **kwargs) -> None:
        super().__init__(**kwargs)
        self.group = group

    def compose(self) -> ComposeResult:
        running_count = sum(
            1 for s in self.group.servers if s.status == models.ServerStatus.Running
        )
        total_count = len(self.group.servers)

        yield Static(f'Group: {self.group.name}', classes='group-title')
        yield Label(f'Total Servers: {total_count}', classes='group-info')
        yield Label(f'Online Servers: {running_count}', classes='group-info')
        yield Static()  # Spacer

        yield Static('Group Members', classes='group-title')
        table = DataTable()
        table.add_columns('ID', 'Name', 'Type', 'Status', 'Node')
        for s in self.group.servers:
            status_icon = '●' if s.status == models.ServerStatus.Running else '○'
            table.add_row(
                str(s.server_id),
                s.name,
                s.type.value.upper(),
                f'{status_icon} {s.status.value}',
                s.node,
            )
        yield table
