from typing import ClassVar
from typing import Iterable
from typing import Optional

from textual._loop import loop_from_index  # noqa
from textual.await_complete import AwaitComplete
from textual.await_remove import AwaitRemove
from textual.binding import Binding
from textual.binding import BindingType
from textual.containers import VerticalScroll
from textual.events import Mount
from textual.message import Message
from textual.reactive import reactive
from textual.widget import AwaitMount
from typing_extensions import TypeGuard

from pve_tui.tui.widgets.multiselect_list_item import MultiselectListItem


class MultiselectListView(VerticalScroll, can_focus=True, can_focus_children=False):
    """A vertical list view widget.

    Displays a vertical list of `MultiselectListItem`s which can be highlighted and
    selected using the mouse or keyboard.

    Attributes:
        index: The index in the list that's currently highlighted.
    """

    ALLOW_MAXIMIZE = True

    DEFAULT_CSS = """
    MultiselectListView {
        background: $surface;
        & > MultiselectListItem {
            color: $foreground;
            height: auto;
            overflow: hidden hidden;
            width: 1fr;

            &.-hovered {
                background: $accent 20%;
            }

            &.-highlight {
                color: $text;
                background: $secondary-background-lighten-2;
                text-style: $block-cursor-text-style;
            }

            &.-selected {
                color: $text;
                background: $secondary-background-darken-2;
                text-style: $block-cursor-text-style;
            }
        }

        &:focus {
            background-tint: $foreground 5%;
            & > MultiselectListItem.-selected {
                color: $background;
                background: $primary-background-darken-2;
                text-style: $block-cursor-blurred-text-style;
            }
            & > MultiselectListItem.-highlight {
                color: $background;
                background: $primary-background-lighten-2;
                text-style: $block-cursor-blurred-text-style;
            }
        }
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding('space', 'select_cursor', 'Select'),
        Binding('up', 'cursor_up', 'Cursor up', show=False),
        Binding('down', 'cursor_down', 'Cursor down', show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | space | Select the current item. |
    | up | Move the cursor up. |
    | down | Move the cursor down. |
    """

    index = reactive[Optional[int]](None, init=False)
    """The index of the currently highlighted item."""

    class Highlighted(Message):
        """Posted when the highlighted item changes.

        Highlighted item is controlled using up/down keys.
        Can be handled using `on_multiselect_list_view_highlighted` in a subclass of `MultiselectListView`
        or in a parent widget in the DOM.
        """

        ALLOW_SELECTOR_MATCH = {'item'}
        """Additional message attributes that can be used with the [`on` decorator][textual.on]."""

        def __init__(
            self,
            list_view: MultiselectListView,
            item: MultiselectListItem | None,
        ) -> None:
            super().__init__()
            self.list_view: MultiselectListView = list_view
            """The view that contains the item highlighted."""
            self.item: MultiselectListItem | None = item
            """The highlighted item, if there is one highlighted."""

        @property
        def control(self) -> MultiselectListView:
            """The view that contains the item highlighted.

            This is an alias for [`Highlighted.list_view`][textual.widgets.ListView.Highlighted.list_view]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.list_view

    class Selected(Message):
        """Posted when a list item is selected, e.g. when you press the enter key on it.

        Can be handled using `on_list_view_selected` in a subclass of `ListView` or in
        a parent widget in the DOM.
        """

        ALLOW_SELECTOR_MATCH = {'item'}
        """Additional message attributes that can be used with the [`on` decorator][textual.on]."""

        def __init__(
            self,
            list_view: MultiselectListView,
            item: MultiselectListItem,
            index: int,
        ) -> None:
            super().__init__()
            self.list_view: MultiselectListView = list_view
            """The view that contains the item selected."""
            self.item: MultiselectListItem = item
            """The selected item."""
            self.index = index
            """Index of the selected item."""

        @property
        def control(self) -> MultiselectListView:
            """The view that contains the item selected.

            This is an alias for [`Selected.list_view`][textual.widgets.ListView.Selected.list_view]
            and is used by the [`on`][textual.on] decorator.
            """
            return self.list_view

    def __init__(
        self,
        *children: MultiselectListItem,
        initial_index: int | None = 0,
        name: str | None = None,
        id: str | None = None,  # noqa
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """
        Initialize a MultiselectListView.

        Args:
            *children: The MultiselectListItems to display in the list.
            initial_index: The index that should be highlighted when the list is first mounted.
            name: The name of the widget.
            id: The unique ID of the widget used in CSS/query selection.
            classes: The CSS classes of the widget.
            disabled: Whether the MultiselectListView is disabled or not.
        """
        super().__init__(
            *children,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )
        self._initial_index = initial_index

    def _on_mount(self, _: Mount) -> None:
        """Ensure the MultiselectListView is fully-settled after mounting."""

        if self._initial_index is not None and self.children:
            index = self._initial_index
            if index >= len(self.children):
                index = 0
            if self._nodes[index].disabled:
                for index, node in loop_from_index(self._nodes, index, wrap=True):
                    if not node.disabled:
                        break
            self.index = index

    @property
    def highlighted_child(self) -> MultiselectListItem | None:
        """The currently highlighted MultiselectListItem, or None if nothing is highlighted."""
        if self.index is not None and 0 <= self.index < len(self._nodes):
            list_item = self._nodes[self.index]
            assert isinstance(list_item, MultiselectListItem)
            return list_item
        else:
            return None

    @property
    def selected_children(self) -> list[MultiselectListItem]:
        """The currently selected MultiselectListItems."""
        selected_items = []
        for node in self._nodes:
            assert isinstance(node, MultiselectListItem)
            if node.selected:
                selected_items.append(node)
        return selected_items

    def validate_index(self, index: int | None) -> int | None:
        """Clamp the index to the valid range, or set to None if there's nothing to highlight.

        Args:
            index: The index to clamp.

        Returns:
            The clamped index.
        """
        if index is None or not self._nodes:
            return None
        elif index < 0:
            return 0
        elif index >= len(self._nodes):
            return len(self._nodes) - 1

        return index

    def _is_valid_index(self, index: int | None) -> TypeGuard[int]:
        """Determine whether the current index is valid into the list of children."""
        if index is None:
            return False
        return 0 <= index < len(self._nodes)

    def watch_index(self, old_index: int | None, new_index: int | None) -> None:
        """Updates the highlighting when the index changes."""

        if new_index is not None:
            selected_widget = self._nodes[new_index]
            if selected_widget.region:
                self.scroll_to_widget(self._nodes[new_index], animate=False)
            else:
                # Call after refresh to permit a refresh operation
                self.call_after_refresh(
                    self.scroll_to_widget,
                    selected_widget,
                    animate=False,
                )

        if self._is_valid_index(old_index):
            old_child = self._nodes[old_index]
            assert isinstance(old_child, MultiselectListItem)
            old_child.highlighted = False

        if (
            new_index is not None
            and self._is_valid_index(new_index)
            and not self._nodes[new_index].disabled
        ):
            new_child = self._nodes[new_index]
            assert isinstance(new_child, MultiselectListItem)
            new_child.highlighted = True
            self.post_message(self.Highlighted(self, new_child))
        else:
            self.post_message(self.Highlighted(self, None))

    def extend(self, items: Iterable[MultiselectListItem]) -> AwaitMount:
        """Append multiple new MultiselectListItems to the end of the MultiselectListView.

        Args:
            items: The MultiselectListItems to append.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child items.
        """
        await_mount = self.mount(*items)
        return await_mount

    def append(self, item: MultiselectListItem) -> AwaitMount:
        """Append a new MultiselectListItem to the end of the MultiselectListView.

        Args:
            item: The MultiselectListItem to append.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child item.
        """
        return self.extend([item])

    def clear(self) -> AwaitRemove:
        """Clear all items from the MultiselectListView.

        Returns:
            An awaitable that yields control to the event loop until
                the DOM has been updated to reflect all children being removed.
        """
        await_remove = self.query('MultiselectListView > MultiselectListItem').remove()
        self.index = None
        return await_remove

    def insert(self, index: int, items: Iterable[MultiselectListItem]) -> AwaitMount:
        """Insert new MultiselectListItem(s) to specified index.

        Args:
            index: index to insert new MultiselectListItem.
            items: The MultiselectListItems to insert.

        Returns:
            An awaitable that yields control to the event loop
                until the DOM has been updated with the new child item.
        """
        await_mount = self.mount(*items, before=index)
        return await_mount

    def pop(self, index: Optional[int] = None) -> AwaitComplete:
        """Remove last MultiselectListItem from MultiselectListView or
           Remove MultiselectListItem from MultiselectListView by index

        Args:
            index: index of MultiselectListItem to remove from MultiselectListView

        Returns:
            An awaitable that yields control to the event loop until
                the DOM has been updated to reflect item being removed.
        """
        if len(self) == 0:
            raise IndexError('pop from empty list')

        index = index if index is not None else -1
        item_to_remove = self.query('MultiselectListItem')[index]
        normalized_index = index if index >= 0 else index + len(self)

        async def do_pop() -> None:
            """Remove the item and update the highlighted index."""
            await item_to_remove.remove()
            if self.index is not None:
                if normalized_index < self.index:
                    self.index -= 1
                elif normalized_index == self.index:
                    old_index = self.index
                    # Force a re-validation of the index
                    self.index = self.index
                    # If the index hasn't changed, the watcher won't be called
                    # but we need to update the highlighted item
                    if old_index == self.index:
                        self.watch_index(old_index, self.index)

        return AwaitComplete(do_pop())

    def remove_items(self, indices: Iterable[int]) -> AwaitComplete:
        """Remove MultiselectListItems from MultiselectListView by indices

        Args:
            indices: index(s) of MultiselectListItems to remove from MultiselectListView

        Returns:
            An awaitable object that waits for the direct children to be removed.
        """
        items = self.query('MultiselectListItem')
        items_to_remove = [items[index] for index in indices]
        normalized_indices = set(
            index if index >= 0 else index + len(self) for index in indices
        )

        async def do_remove_items() -> None:
            """Remove the items and update the highlighted index."""
            await self.remove_children(items_to_remove)
            if self.index is not None:
                removed_before_highlighted = sum(
                    1 for index in normalized_indices if index < self.index
                )
                if removed_before_highlighted:
                    self.index -= removed_before_highlighted
                elif self.index in normalized_indices:
                    old_index = self.index
                    # Force a re-validation of the index
                    self.index = self.index
                    # If the index hasn't changed, the watcher won't be called
                    # but we need to update the highlighted item
                    if old_index == self.index:
                        self.watch_index(old_index, self.index)

        return AwaitComplete(do_remove_items())

    def action_select_cursor(self) -> None:
        """Select the current item in the list."""

        selected_child = self.highlighted_child
        if selected_child is None:
            return

        selected_child.selected = not selected_child.selected
        selected_child.post_message(MultiselectListItem.Selected(selected_child))

    def action_cursor_down(self) -> None:
        """Highlight the next item in the list."""
        if self.index is None:
            if self._nodes:
                self.index = 0
        else:
            index = self.index
            for index, item in loop_from_index(self._nodes, self.index, wrap=False):
                if not item.disabled:
                    self.index = index
                    break

    def action_cursor_up(self) -> None:
        """Highlight the previous item in the list."""
        if self.index is None:
            if self._nodes:
                self.index = len(self._nodes) - 1
        else:
            for index, item in loop_from_index(
                self._nodes,
                self.index,
                direction=-1,
                wrap=False,
            ):
                if not item.disabled:
                    self.index = index
                    break

    def __len__(self) -> int:
        """Compute the length (in number of items) of the list view."""
        return len(self._nodes)
