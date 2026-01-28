from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label

from pve_tui.core import consts
from pve_tui.core import models


class ServerBrief(Widget):
    """A brief overview widget for a Proxmox VE server."""

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
        """Initialize the ServerBrief widget."""
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
            Label(
                f' {self.server_info.type.value}#{self.server_info.server_id}',
                classes='server-id',
            ),
            Label(
                f' {status_icon} {self.server_info.status.value}',
                classes=f'server-status {status_class}',
            ),
            classes='server-header',
        )

        if self.server_info.status == models.ServerStatus.Running:
            metrics_text = (
                f'CPU: {self.server_info.cpu_usage * 100:.2f}% ({self.server_info.cpus}c) | '
                f'Mem: {int(self.server_info.memory_used / consts.GIGABYTES)}G/{int(self.server_info.memory / consts.GIGABYTES)}G'
            )
            yield Label(metrics_text, classes='metrics')
        else:
            yield Label('Offline', classes='metrics')

    def update(self, server_info: models.ServerBrief) -> None:
        """Update the widget with new server information."""
        self.server_info = server_info

        # Update name and ID
        self.query_one('.server-name', Label).update(f'{self.server_info.name}')
        self.query_one('.server-id', Label).update(
            f' {server_info.type.value}#{self.server_info.server_id}',
        )

        # Update status
        status_class = (
            'status-running'
            if self.server_info.status == models.ServerStatus.Running
            else 'status-stopped'
        )
        status_icon = (
            '●' if self.server_info.status == models.ServerStatus.Running else '○'
        )

        status_label = self.query_one('.server-status', Label)
        status_label.classes = f'server-status {status_class}'
        status_label.update(f' {status_icon} {self.server_info.status.value}')

        # Update metrics
        metrics_label = self.query_one('.metrics', Label)
        if self.server_info.status == models.ServerStatus.Running:
            metrics_text = (
                f'CPU: {self.server_info.cpu_usage * 100:.2f}% ({self.server_info.cpus}c) | '
                f'Mem: {int(self.server_info.memory_used / consts.GIGABYTES)}G/{int(self.server_info.memory / consts.GIGABYTES)}G'
            )
            metrics_label.update(metrics_text)
        else:
            metrics_label.update('Offline')
