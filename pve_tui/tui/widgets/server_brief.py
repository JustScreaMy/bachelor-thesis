from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from pve_tui.core import consts
from pve_tui.core import models


class ServerBrief(Widget):
    """A brief overview widget for a Proxmox VE server."""

    DEFAULT_CSS = """
        ServerBrief {
            height: auto;
            padding: 0 1;
        }

        .status-running {
            color: $success;
        }

        .status-stopped {
            color: $text-muted;
        }

        .server-detail {
            color: $text-muted;
            padding: 0 0 0 2;
        }
    """

    def __init__(self, server_info: models.ServerBrief, **kwargs) -> None:
        """Initialize the ServerBrief widget."""
        super().__init__(**kwargs)
        self.server_info = server_info

    def _status_icon(self) -> str:
        return '●' if self.server_info.status == models.ServerStatus.Running else '○'

    def _status_class(self) -> str:
        return (
            'status-running'
            if self.server_info.status == models.ServerStatus.Running
            else 'status-stopped'
        )

    def _detail_text(self) -> str:
        s = self.server_info
        parts = [f'{s.type.value}#{s.server_id}']
        if s.status == models.ServerStatus.Running:
            cpu = s.cpu_usage * 100
            mem_used = int(s.memory_used / consts.GIGABYTES)
            mem_total = int(s.memory / consts.GIGABYTES)
            parts.append(f'cpu {cpu:.0f}%')
            parts.append(f'mem {mem_used}/{mem_total}G')
        return '  '.join(parts)

    def compose(self) -> ComposeResult:
        yield Label(
            f'{self._status_icon()} {self.server_info.name}',
            classes=f'server-name {self._status_class()}',
        )
        yield Label(self._detail_text(), classes='server-detail')

    def update(self, server_info: models.ServerBrief) -> None:
        """Update the widget with new server information."""
        self.server_info = server_info

        name_label = self.query_one('.server-name', Label)
        name_label.classes = f'server-name {self._status_class()}'
        name_label.update(f'{self._status_icon()} {self.server_info.name}')

        self.query_one('.server-detail', Label).update(self._detail_text())
