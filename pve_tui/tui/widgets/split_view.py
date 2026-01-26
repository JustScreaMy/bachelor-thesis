from textual.app import ComposeResult
from textual.widget import Widget

class SplitView(Widget):
    BINDINGS = [
        ('tab', 'focus_next_pane', 'Focus Next Pane'),
        ('shift+tab', 'focus_previous_pane', 'Focus Previous Pane'),
    ]

    DEFAULT_CSS = '''
    SplitView {
        layout: horizontal;
        height: 100%;
        border: solid gray;
    }

    .split-pane {
        width: 1fr;
        height: 100%;
        padding: 1;
        # border: solid gray;
        background: $panel;
    }

    .split-pane:focus-within {
        # border: green;
        padding: 1;
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
