from textual.app import ComposeResult
from textual.widget import Widget
from textual import log

class SplitView(Widget):
    BINDINGS = [
        ('tab', 'focus_next_pane', 'Focus Next Pane'),
        ('shift+tab', 'focus_previous_pane', 'Focus Previous Pane'),
    ]

    DEFAULT_CSS = '''
    SplitView {
        layout: horizontal;
        height: 100%;
    }

    .split-pane {
        width: 1fr;
        height: 100%;
        border: solid gray;
        background: $panel;
    }

    /* Highlight the pane that contains the focus */
    .split-pane:focus-within {
        border: double green;
        background: $surface;
    }
    '''

    def __init__(self, left: Widget, right: Widget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.left = left
        self.right = right

        self.left.can_focus = True
        self.right.can_focus = True

        self.left.add_class('split-pane')
        self.right.add_class('split-pane')

    def compose(self) -> ComposeResult:
        yield self.left
        yield self.right

    def on_mount(self) -> None:
        self.left.focus()

    def action_focus_next_pane(self) -> None:
        if self.left.has_focus_within:
            self.right.focus()
        else:
            self.left.focus()

    def action_focus_previous_pane(self) -> None:
        if self.right.has_focus_within:
            self.left.focus()
        else:
            self.right.focus()
