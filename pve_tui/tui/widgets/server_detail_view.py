from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Label
from textual.widgets import Static

from pve_tui.core import consts
from pve_tui.core import models

SHARED_CSS = """
    .detail-label {
        color: $text-muted;
        width: 1fr;
    }

    .detail-value {
        color: $text;
        width: 1fr;
        text-style: bold;
    }

    .detail-section {
        margin-bottom: 1;
        border: none $primary-darken-1;
        padding: 1;
    }

    .section-title {
        color: $primary;
        text-style: bold underline;
        margin-bottom: 1;
    }
"""


class BaseDetailView(Widget):
    """Base class for server detail views with shared functionality."""

    @staticmethod
    def _yield_basic_info(brief: models.ServerBrief, server_type: str) -> ComposeResult:
        """Yield basic information section."""
        yield Static('Basic Information', classes='section-title')
        yield Label(f'Name: {brief.name}')
        yield Label(f'VMID: {brief.server_id}')
        yield Label(f'Node: {brief.node}')
        yield Label(f'Status: {brief.status.value.upper()}')
        yield Label(f'Type: {server_type}')
        yield Static()  # Spacer

    @staticmethod
    def _yield_hardware_header() -> ComposeResult:
        """Yield hardware configuration section header."""
        yield Static('Hardware Configuration', classes='section-title')

    @staticmethod
    def _yield_common_hardware(
        brief: models.ServerBrief,
        server: models.ServerLXC | models.ServerQEMU,
    ) -> ComposeResult:
        """Yield common hardware configuration details."""
        yield Label(f'Architecture: {server.arch.value}')
        yield Label(f'CPUs: {brief.cpus}')
        yield Label(f'CPU Limit: {server.cpu_limit}%')
        yield Label(f'CPU Units: {server.cpu_units}')
        yield Label(f'Memory: {brief.memory / consts.GIGABYTES:.2f} GB')

    @staticmethod
    def _yield_boot_config(on_boot: bool) -> ComposeResult:
        """Yield boot configuration section."""
        yield Static('Boot Configuration', classes='section-title')
        yield Label(f'Boot on Startup: {"Yes" if on_boot else "No"}')

    @staticmethod
    def _format_uptime(uptime_seconds: int) -> str:
        """Format uptime from seconds to a human-readable string."""
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        return f'{days}d {hours}h {minutes}m'


class LXCDetailView(BaseDetailView):
    """A widget to display detailed information about an LXC container."""

    DEFAULT_CSS = f"""
    LXCDetailView {{
        padding: 2;
    }}
    {SHARED_CSS}
    """

    def __init__(self, server: models.ServerLXC, **kwargs) -> None:
        super().__init__(**kwargs)
        self.server = server

    def compose(self) -> ComposeResult:
        brief = self.server.brief

        yield from self._yield_basic_info(brief, 'LXC Container')
        yield from self._yield_hardware_header()
        yield from self._yield_common_hardware(brief, self.server)
        yield Label(f'Disk: {self.server.max_disk / consts.GIGABYTES:.2f} GB')
        yield Static()  # Spacer

        if brief.status == models.ServerStatus.Running:
            yield Static('Current Usage', classes='section-title')
            yield Label(f'CPU Usage: {brief.cpu_usage * 100:.2f}%')
            yield Label(f'Memory Used: {brief.memory_used / consts.GIGABYTES:.2f} GB')
            yield Label(f'Disk Used: {self.server.disk / consts.GIGABYTES:.2f} GB')
            yield Label(f'Uptime: {self._format_uptime(brief.uptime)}')
        else:
            yield Static('Container is offline', classes='detail-label')
        yield Static()  # Spacer

        yield from self._yield_boot_config(self.server.on_boot)


class QEMUDetailView(BaseDetailView):
    """A widget to display detailed information about a QEMU VM."""

    DEFAULT_CSS = f"""
    QEMUDetailView {{
        padding: 2;
    }}
    {SHARED_CSS}
    """

    def __init__(self, server: models.ServerQEMU, **kwargs) -> None:
        super().__init__(**kwargs)
        self.server = server

    def compose(self) -> ComposeResult:
        brief = self.server.brief

        yield from self._yield_basic_info(brief, 'QEMU Virtual Machine')
        yield from self._yield_hardware_header()
        yield Label(f'CPU Type: {self.server.cpu_type}')
        yield from self._yield_common_hardware(brief, self.server)
        yield Label(f'Balloon: {self.server.baloon / consts.GIGABYTES:.2f} GB')
        yield Static()  # Spacer

        if brief.status == models.ServerStatus.Running:
            yield Static('Current Usage', classes='section-title')
            yield Label(f'CPU Usage: {brief.cpu_usage * 100:.2f}%')
            yield Label(f'Memory Used: {brief.memory_used / consts.GIGABYTES:.2f} GB')
            yield Label(f'Uptime: {self._format_uptime(brief.uptime)}')
        else:
            yield Static('Virtual machine is offline', classes='detail-label')
        yield Static()  # Spacer

        yield from self._yield_boot_config(self.server.on_boot)


class ServerDetailView(Widget):
    """A widget to display detailed information about a server."""

    DEFAULT_CSS = """
    ServerDetailView {
        padding: 2;
    }

    .server-detail {
        color: $text;
    }
    """

    def __init__(self, server: models.ServerQEMU | models.ServerLXC, **kwargs) -> None:
        super().__init__(**kwargs)
        self.server = server

    def compose(self) -> ComposeResult:
        with VerticalScroll():  # TODO: fix vertical scroll not working
            if isinstance(self.server, models.ServerLXC):
                yield LXCDetailView(self.server)
            elif isinstance(self.server, models.ServerQEMU):
                yield QEMUDetailView(self.server)
            else:
                yield Static('Unknown server type', classes='server-detail')
