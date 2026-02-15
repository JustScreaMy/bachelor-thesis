from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from pve_tui.core import models


class ServerActionList(Widget):
    """Widget to display actions for selected servers."""

    DEFAULT_CSS = """
    ServerActionList {
        padding: 2;
        content-align: center middle;
    }

    .action-header {
        color: $text;
        text-style: italic;
    }
    """

    servers = reactive[list[models.ServerBrief]](list, recompose=True)
    """The list of currently selected servers to show actions for."""

    def __init__(
        self,
        servers: list[models.ServerBrief] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.servers = servers if servers is not None else []

    def compose(self) -> ComposeResult:
        for server in self.servers:
            yield Static(
                f'Actions for {server.name} (ID: {server.server_id})',
                classes='action-header',
            )
