from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from pve_tui.core import models


class ServerGroupBrief(Widget):
    """A brief overview widget for a Proxmox VE server group."""

    DEFAULT_CSS = """
        ServerGroupBrief {
            height: auto;
            padding: 0 1;
        }

        .group-all-running {
            color: $success;
        }

        .group-partial {
            color: $warning;
        }

        .group-all-stopped {
            color: $text-muted;
        }

        .group-detail {
            color: $text-muted;
            padding: 0 0 0 2;
        }
    """

    def __init__(self, group_info: models.ServerGroupBrief, **kwargs) -> None:
        """Initialize the ServerGroupBrief widget."""
        super().__init__(**kwargs)
        self.group_info = group_info

    def _counts(self) -> tuple[int, int]:
        running = sum(
            1
            for s in self.group_info.servers
            if s.status == models.ServerStatus.Running
        )
        return running, len(self.group_info.servers)

    def _status_icon_and_class(self) -> tuple[str, str]:
        running, total = self._counts()
        if running == total:
            return '●', 'group-name group-all-running'
        elif running > 0:
            return '◐', 'group-name group-partial'
        else:
            return '○', 'group-name group-all-stopped'

    def _detail_text(self) -> str:
        running, total = self._counts()
        members = ', '.join(s.name for s in self.group_info.servers[:5])
        if len(self.group_info.servers) > 5:
            members += '...'
        return f'{running}/{total} online  {members}'

    def compose(self) -> ComposeResult:
        icon, cls = self._status_icon_and_class()
        yield Label(f'{icon} {self.group_info.name}', classes=cls)
        yield Label(self._detail_text(), classes='group-detail')

    def update(self, group_info: models.ServerGroupBrief) -> None:
        """Update the widget with new group information."""
        self.group_info = group_info

        icon, cls = self._status_icon_and_class()
        name_label = self.query_one('.group-name', Label)
        name_label.classes = cls
        name_label.update(f'{icon} {self.group_info.name}')

        self.query_one('.group-detail', Label).update(self._detail_text())
