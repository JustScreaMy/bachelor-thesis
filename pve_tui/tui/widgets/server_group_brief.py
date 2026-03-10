from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label

from pve_tui.core import models


class ServerGroupBrief(Widget):
    """A brief overview widget for a Proxmox VE server group."""

    DEFAULT_CSS = """
        ServerGroupBrief {
            height: auto;
            border: none $primary-darken-1;
            padding: 1;
        }

        ServerGroupBrief:hover {
            background: $panel-lighten-3;
        }

        .group-header {
            width: 100%;
            height: 1;
        }

        .group-name {
            text-style: bold;
            color: $text;
        }

        .group-count {
            color: $text-muted;
        }

        .group-status {
            color: $success;
            text-style: bold;
        }

        .group-members {
            margin-top: 1;
            color: $text-muted;
        }
    """

    def __init__(self, group_info: models.ServerGroupBrief, **kwargs) -> None:
        """Initialize the ServerGroupBrief widget."""
        super().__init__(**kwargs)
        self.group_info = group_info

    def compose(self) -> ComposeResult:
        running_count = sum(
            1
            for s in self.group_info.servers
            if s.status == models.ServerStatus.Running
        )
        total_count = len(self.group_info.servers)

        yield Horizontal(
            Label(f'Group: {self.group_info.name}', classes='group-name'),
            Label(f' ({total_count} members)', classes='group-count'),
            Label(
                f' {running_count}/{total_count} online',
                classes='group-status',
            ),
            classes='group-header',
        )

        member_names = ', '.join([s.name for s in self.group_info.servers[:5]])
        if len(self.group_info.servers) > 5:
            member_names += '...'

        yield Label(f'Members: {member_names}', classes='group-members')

    def update(self, group_info: models.ServerGroupBrief) -> None:
        """Update the widget with new group information."""
        self.group_info = group_info

        running_count = sum(
            1
            for s in self.group_info.servers
            if s.status == models.ServerStatus.Running
        )
        total_count = len(self.group_info.servers)

        self.query_one('.group-name', Label).update(f'Group: {self.group_info.name}')
        self.query_one('.group-count', Label).update(f' ({total_count} members)')
        self.query_one('.group-status', Label).update(
            f' {running_count}/{total_count} online',
        )

        member_names = ', '.join([s.name for s in self.group_info.servers[:5]])
        if len(self.group_info.servers) > 5:
            member_names += '...'
        self.query_one('.group-members', Label).update(f'Members: {member_names}')
