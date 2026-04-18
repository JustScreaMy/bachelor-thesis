from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center
from textual.containers import Middle
from textual.screen import Screen
from textual.widgets import Static


class AuthErrorScreen(Screen):
    """Shown when authentication with the Proxmox API fails."""

    BINDINGS = [Binding('q', 'quit', 'Quit')]

    DEFAULT_CSS = """
    AuthErrorScreen {
        align: center middle;
    }

    #auth-error-box {
        width: 70;
        height: auto;
        border: solid $error;
        background: $surface;
        padding: 2 4;
    }

    #auth-error-title {
        text-align: center;
        text-style: bold;
        color: $error;
        margin-bottom: 1;
    }

    #auth-error-body {
        text-align: center;
        color: $text;
    }

    #auth-error-hint {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-top: 1;
    }
    """

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                with Static(id='auth-error-box'):
                    yield Static('Authentication failed', id='auth-error-title')
                    yield Static(self._message, id='auth-error-body')
                    yield Static(
                        'Check your token_id and token in the configuration.',
                        id='auth-error-hint',
                    )

    def action_quit(self) -> None:
        self.app.exit()
