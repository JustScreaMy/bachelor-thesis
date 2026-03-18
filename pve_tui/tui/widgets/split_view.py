from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.binding import BindingType
from textual.widget import Widget


class SplitView(Widget):
    """A split view widget with a left sidebar and right main area with configurable width."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('tab', 'focus_next_pane', 'Focus Next Pane'),
        Binding('shift+tab', 'focus_previous_pane', 'Focus Previous Pane'),
    ]

    DEFAULT_CSS = """
    SplitView {
        layout: horizontal;
        height: 100%;
        background: $surface;
    }

    .split-pane {
        height: 100%;
        padding: 0 1;
    }

    SplitView > .split-pane:first-child {
        border-right: solid $border;
        background: $panel;
    }

    SplitView > .split-pane:last-child {
        width: 1fr;
        background: $surface;
    }
    """

    def __init__(
        self,
        left: Widget,
        right: Widget,
        sidebar_width: str | int | float = '30%',
        **kwargs,
    ) -> None:
        """Initialize the SplitView with left and right panes and sidebar width."""
        super().__init__(**kwargs)
        self.left = left
        self.right = right

        self.left.can_focus = True
        self.right.can_focus = True

        self.left.add_class('split-pane')
        self.right.add_class('split-pane')

        # Handle float as percentage (e.g. 0.25 -> "25%")
        if isinstance(sidebar_width, float) and 0 < sidebar_width < 1:
            self.left.styles.width = f'{sidebar_width * 100:.1f}%'
        else:
            self.left.styles.width = sidebar_width

    def set_left_pane(self, widget: Widget) -> None:
        """Set the left pane widget."""
        old_left = self.left
        sidebar_width = old_left.styles.width

        widget.can_focus = True
        widget.add_class('split-pane')
        widget.styles.width = sidebar_width

        self.left = widget
        self.mount(widget, before=self.right)
        old_left.remove()

    def set_right_pane(self, widget: Widget) -> None:
        """Set the right pane widget."""
        old_right = self.right

        widget.can_focus = True
        widget.add_class('split-pane')

        self.right = widget
        self.mount(widget)
        old_right.remove()

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
