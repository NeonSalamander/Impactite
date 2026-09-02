"""Todo tree panel and related widgets for Impactite.

The panel is intentionally isolated in this module so it can be imported and
tested without pulling in the whole application.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from textual import events
from textual.message import Message
from textual.widgets import Tree
from textual.widgets.tree import TreeNode

from impactite.i18n import _
from impactite.todo_parser import (
    TodoItem,
    close_todo,
    collect_open_todos,
    find_note_files,
)


class TodoTree(Tree):
    """Tree view showing open todos grouped by note file."""

    can_focus = True
    FOCUS_ON_CLICK = True

    class TodoClosed(Message):
        """Emitted after a todo was successfully closed in its source file."""

        def __init__(self, item: TodoItem) -> None:
            self.item = item
            super().__init__()

    def __init__(self, root_path: Path, **kwargs: Any) -> None:
        super().__init__(_("Open todos"), **kwargs)
        self.show_root = True
        self.root_path = root_path
        self._item_nodes: dict[str, TreeNode] = {}

    def build(self) -> None:
        """Rebuild the tree from current note files."""
        self.clear()
        self._item_nodes.clear()
        todos = collect_open_todos(find_note_files(self.root_path))
        if not todos:
            self.root.add(_("No open todos"), data={"type": "empty"})
            return

        grouped: dict[Path, list[TodoItem]] = {}
        for item in todos:
            grouped.setdefault(item.file_path, []).append(item)

        for file_path, items in sorted(
            grouped.items(),
            key=lambda kv: str(kv[0].relative_to(self.root_path)).lower(),
        ):
            rel = file_path.relative_to(self.root_path)
            file_node = self.root.add(f"📄 {rel.as_posix()}", data={"type": "file", "path": file_path})
            for item in items:
                node = file_node.add(item.line_text, data={"type": "todo", "item": item})
                self._item_nodes[item.id] = node

    async def _on_key(self, event: events.Key) -> None:
        """Space closes the selected todo if the event reaches us."""
        if event.key == "space":
            event.stop()
            self._close_selected()
            return
        await super()._on_key(event)

    def _close_selected(self) -> None:
        node = self.cursor_node
        if node is None:
            return
        data = node.data
        if not data or data.get("type") != "todo":
            return
        item: TodoItem | None = data.get("item")
        if item is None:
            return
        if close_todo(item):
            self.post_message(self.TodoClosed(item))
        else:
            self.notify(_("Could not close todo"), severity="error")

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Single-click on a file node opens the originating note; closing is via space."""
        data = event.node.data or {}
        if data.get("type") == "file":
            path = data.get("path")
            if isinstance(path, Path):
                self.post_message(self.FileSelected(path))

    class FileSelected(Message):
        """Request to open the originating note file."""

        def __init__(self, path: Path) -> None:
            self.path = path
            super().__init__()

    def remove_todo(self, item_id: str) -> None:
        """Remove a todo node from the tree after it was closed."""
        node = self._item_nodes.pop(item_id, None)
        if node is None:
            return
        parent = node.parent
        node.remove()
        if parent is not None and not parent.children:
            parent.remove()
        if not self.root.children:
            self.root.add(_("No open todos"), data={"type": "empty"})
