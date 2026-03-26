from textual.app import ComposeResult
from textual.containers import Center
from textual.containers import Middle
from textual.screen import ModalScreen
from textual.widgets import Button
from textual.widgets import Label
from textual.widgets import OptionList
from textual.widgets.option_list import Option


class SelectionModal(ModalScreen[str]):
    """A modal dialog for selecting from a list of options."""

    DEFAULT_CSS = """
    SelectionModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.5);
    }

    #modal-container {
        width: 60;
        height: auto;
        max-height: 80%;
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

    #modal-options {
        height: auto;
        max-height: 16;
        border: solid $primary-darken-1;
        background: $surface;
        margin-bottom: 1;
    }

    #modal-options > .option-list--option-highlighted {
        background: $accent;
        color: $text;
        text-style: bold;
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
        options: list[tuple[str, str]],
        **kwargs,
    ) -> None:
        """Initialize the selection modal.

        Args:
            title: The title displayed at the top of the modal.
            options: A list of (value, label) tuples for the selectable items.
        """
        super().__init__(**kwargs)
        self.title_text = title
        self.options = options

    def compose(self) -> ComposeResult:
        with Middle(id='modal-container'):
            yield Label(self.title_text, id='modal-title')
            yield OptionList(
                *[Option(label, id=value) for value, label in self.options],
                id='modal-options',
            )
            with Center(id='modal-buttons'):
                yield Button('Cancel', id='cancel-btn', variant='error')

    def on_mount(self) -> None:
        self.query_one(OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option_id)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == 'cancel-btn':
            self.dismiss('')
