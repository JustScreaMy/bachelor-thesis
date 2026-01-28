from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label

from pve_tui.core import models


GIGABYTES = 1024 * 1024 * 1024


class ServerBrief(Widget):
    DEFAULT_CSS = """
        ServerBrief {
            height: auto;
            border: none $primary-darken-1;
            padding: 1;
        }

        ServerBrief:hover {
            background: $panel-lighten-3;
        }

        .server-header {
            width: 100%;
            height: 1;
        }

        .server-name {
            text-style: bold;
            color: $text;
        }

        .server-id {
            color: $text-muted;
        }

        .status-running {
            color: $success;
            text-style: bold;
        }

        .status-stopped {
            color: $error;
            text-style: bold;
        }

        .metrics {
            margin-top: 1;
            color: $text-muted;
        }
    """

    def __init__(self, server_info: models.ServerBrief, **kwargs) -> None:
        super().__init__(**kwargs)
        self.server_info = server_info

    def compose(self) -> ComposeResult:
        # Determine status class
        status_class = (
            'status-running'
            if self.server_info.status == models.ServerStatus.Running
            else 'status-stopped'
        )
        status_icon = (
            '●' if self.server_info.status == models.ServerStatus.Running else '○'
        )

        yield Horizontal(
            Label(f'{self.server_info.name}', classes='server-name'),
            Label(f' #{self.server_info.server_id}', classes='server-id'),
            Label(
                f' {status_icon} {self.server_info.status.value}',
                classes=f'server-status {status_class}',
            ),
            classes='server-header',
        )

        if self.server_info.status == models.ServerStatus.Running:
            metrics_text = (
                f'CPU: {self.server_info.cpu_usage * 100:.2f}% ({self.server_info.cpus}c) | '
                f'Mem: {int(self.server_info.memory_used / GIGABYTES)}G/{int(self.server_info.memory / GIGABYTES)}G'
            )
            yield Label(metrics_text, classes='metrics')
        else:
            yield Label('Offline', classes='metrics')
