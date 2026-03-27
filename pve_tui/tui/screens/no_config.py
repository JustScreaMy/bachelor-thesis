from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center
from textual.containers import Middle
from textual.screen import Screen
from textual.widgets import Static


class NoConfigScreen(Screen):
    """Shown when no configuration file is found."""

    BINDINGS = [Binding('q', 'quit', 'Quit')]

    DEFAULT_CSS = """
    NoConfigScreen {
        align: center middle;
    }

    #no-config-box {
        width: 60;
        height: auto;
        border: solid $warning;
        background: $surface;
        padding: 2 4;
    }

    #no-config-title {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }

    #no-config-body {
        text-align: center;
        color: $text;
    }

    #no-config-hint {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-top: 1;
    }
    """

    def __init__(self, config_path: str) -> None:
        super().__init__()
        self._config_path = config_path

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                with Static(id='no-config-box'):
                    yield Static('No configuration found', id='no-config-title')
                    yield Static(
                        f'Expected config at:\n{self._config_path}',
                        id='no-config-body',
                    )
                    yield Static('Run  pve init  to create it.', id='no-config-hint')

    def action_quit(self) -> None:
        self.app.exit()
