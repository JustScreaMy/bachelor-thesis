from textual.app import ComposeResult
from textual.containers import Center
from textual.containers import Middle
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.widgets import Input
from textual.widgets import Static


class InputModal(ModalScreen[str]):
    """A modal dialog for simple text input."""

    DEFAULT_CSS = """
    InputModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }

    #modal-container {
        width: 60;
        height: auto;
        border: solid $primary;
        background: $panel;
        padding: 1 4;
    }

    #modal-title {
        text-align: center;
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    #modal-input {
        margin-bottom: 1;
        border: solid $primary-darken-1;
        background: $surface;
    }

    #modal-buttons {
        margin-top: 1;
        align: center middle;
        height: 3;
    }

    #modal-buttons Button {
        margin: 0 1;
        min-width: 12;
    }
    """

    def __init__(
        self,
        title: str,
        placeholder: str = '',
        initial_value: str = '',
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.title_text = title
        self.placeholder = placeholder
        self.initial_value = initial_value

    def compose(self) -> ComposeResult:
        with Middle(id='modal-container'):
            yield Static(self.title_text, id='modal-title')
            yield Input(
                value=self.initial_value,
                placeholder=self.placeholder,
                id='modal-input',
            )
            with Center(id='modal-buttons'):
                yield Button('Cancel', id='cancel-btn', variant='error')
                yield Button('OK', id='ok-btn', variant='primary')

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'ok-btn':
            value = self.query_one(Input).value.strip()
            self.dismiss(value)
        else:
            self.dismiss('')

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss(value)
