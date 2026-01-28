from textual import events
from textual import on
from textual.reactive import reactive
from textual.widget import Widget


class MultiselectListItem(Widget, can_focus=False):
    """
    A widget that is an item within a `MultiselectListView`.

    A `MultiselectListItem` is designed for use within a
    [MultiselectListView][pve_tui.tui.widgets.multiselect_list_view.MultiselectListView], please see `MultiselectListView`'s
    documentation for more details on use.

    Attributes:
        highlighted (bool): Is this item highlighted?
        selected (bool): Is this item selected?
    """

    highlighted = reactive(False)
    selected = reactive(False)

    @on(events.Click)
    def _on_click(self, event: events.Click) -> None:
        self.log('Clicked on MultiselectListItem')
        self.selected = not self.selected

    def watch_selected(self, value: bool) -> None:
        self.set_class(value, '-selected')

    def watch_highlighted(self, value: bool) -> None:
        self.set_class(value, '-highlight')

    @on(events.Enter)
    @on(events.Leave)
    def on_enter_or_leave(self, event: events.Enter | events.Leave) -> None:
        event.stop()
        self.set_class(self.is_mouse_over, '-hovered')
