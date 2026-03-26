from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.containers import VerticalScroll
from textual.widgets import Label
from textual.widgets import Static

from pve_tui.core import consts
from pve_tui.core import models

SHARED_CSS = """
    .section-title {
        color: $primary-lighten-1;
        text-style: bold;
        margin-top: 1;
    }

    .section-title:first-child {
        margin-top: 0;
    }

    .detail-row {
        height: 1;
        layout: horizontal;
    }

    .detail-key {
        color: $text-muted;
        width: auto;
    }

    .detail-val {
        color: $text;
        width: 1fr;
    }

    .detail-offline {
        color: $text-muted;
        margin-top: 1;
    }
"""


class BaseDetailView:
    """Base class for server detail views with shared functionality."""

    @staticmethod
    def _row(key: str, value: str) -> Horizontal:
        return Horizontal(
            Label(f'{key}: ', classes='detail-key'),
            Label(value, classes='detail-val'),
            classes='detail-row',
        )

    @staticmethod
    def _yield_basic_info(brief: models.ServerBrief, server_type: str) -> ComposeResult:
        status_icon = '●' if brief.status == models.ServerStatus.Running else '○'
        yield Static(
            f'{status_icon} {brief.name}',
            classes=('section-title'),
        )
        yield BaseDetailView._row('Type', server_type)
        yield BaseDetailView._row('VMID', str(brief.server_id))
        yield BaseDetailView._row('Node', brief.node)
        if brief.tags:
            yield BaseDetailView._row('Tags', ', '.join(brief.tags))

    @staticmethod
    def _yield_hardware(
        brief: models.ServerBrief,
        server: models.ServerLXC | models.ServerQEMU,
    ) -> ComposeResult:
        yield Static('Hardware', classes='section-title')
        yield BaseDetailView._row('Arch', server.arch.value)
        yield BaseDetailView._row('CPUs', str(brief.cpus))
        yield BaseDetailView._row('CPU Limit', f'{server.cpu_limit}%')
        yield BaseDetailView._row('CPU Units', str(server.cpu_units))
        yield BaseDetailView._row('Memory', f'{brief.memory / consts.GIGABYTES:.2f} GB')

    @staticmethod
    def _yield_usage(brief: models.ServerBrief) -> ComposeResult:
        yield Static('Usage', classes='section-title')
        yield BaseDetailView._row('CPU', f'{brief.cpu_usage * 100:.1f}%')
        yield BaseDetailView._row(
            'Memory',
            f'{brief.memory_used / consts.GIGABYTES:.2f} / {brief.memory / consts.GIGABYTES:.2f} GB',
        )
        yield BaseDetailView._row('Uptime', BaseDetailView._format_uptime(brief.uptime))

    @staticmethod
    def _yield_boot_config(on_boot: bool) -> ComposeResult:
        yield Static('Boot', classes='section-title')
        yield BaseDetailView._row('Start on boot', 'Yes' if on_boot else 'No')

    @staticmethod
    def _format_uptime(uptime_seconds: int) -> str:
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        return f'{days}d {hours}h {minutes}m'


class ServerDetailView(VerticalScroll, BaseDetailView):
    """A widget to display detailed information about a server."""

    DEFAULT_CSS = f"""
    ServerDetailView {{
        height: 100%;
        padding: 1 2;
    }}
    {SHARED_CSS}
    """

    def __init__(self, server: models.ServerQEMU | models.ServerLXC, **kwargs) -> None:
        super().__init__(**kwargs)
        self.server = server

    def compose(self) -> ComposeResult:
        brief = self.server.brief

        if isinstance(self.server, models.ServerLXC):
            yield from self._yield_basic_info(brief, 'LXC Container')
            yield from self._yield_hardware(brief, self.server)
            yield self._row('Disk', f'{self.server.max_disk / consts.GIGABYTES:.2f} GB')

            if brief.status == models.ServerStatus.Running:
                yield from self._yield_usage(brief)
                yield self._row(
                    'Disk Used',
                    f'{self.server.disk / consts.GIGABYTES:.2f} GB',
                )
            else:
                yield Static('Container is offline', classes='detail-offline')

            yield from self._yield_boot_config(self.server.on_boot)

        elif isinstance(self.server, models.ServerQEMU):
            yield from self._yield_basic_info(brief, 'QEMU Virtual Machine')
            yield from self._yield_hardware(brief, self.server)
            yield self._row('CPU Type', self.server.cpu_type)
            yield self._row(
                'Balloon',
                f'{self.server.balloon / consts.GIGABYTES:.2f} GB',
            )

            if brief.status == models.ServerStatus.Running:
                yield from self._yield_usage(brief)
            else:
                yield Static('Virtual machine is offline', classes='detail-offline')

            yield from self._yield_boot_config(self.server.on_boot)
