"""Tests for the right-pane TodosView."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
import pytest_asyncio
from textual.widgets.tree import TreeNode

from impactite.app import MarkdownEditorApp, TodosTree, TodosView
from impactite.core import Config
from impactite.todo_parser import TodoItem, collect_open_todos, find_note_files


@pytest_asyncio.fixture
async def todos_app(tmp_path: Path):
    """Create an app with a small vault containing open todos."""
    root = tmp_path / "notes"
    root.mkdir()
    (root / "project.md").write_text(
        "# Project\n\n- [ ] top level todo\n- [x] done todo\n  - [ ] nested todo\n",
        encoding="utf-8",
    )
    (root / "inbox.md").write_text(
        "- [ ] inbox one\n- [ ] inbox two\n",
        encoding="utf-8",
    )
    (root / "archive.md").write_text(
        "- [ ] archived todo\n",
        encoding="utf-8",
    )
    config = Config(notes_path=str(root), language="en")
    return MarkdownEditorApp(config)


def _flatten_tree(node: TreeNode) -> list[str]:
    results: list[str] = []
    label = node.label
    text = label.plain if hasattr(label, "plain") else str(label)
    results.append(text)
    for child in node.children:
        results.extend(_flatten_tree(child))
    return results


def _first_todo_node(node: TreeNode) -> TreeNode | None:
    for child in node.children:
        if child.data and child.data.get("type") == "todo":
            return child
        result = _first_todo_node(child)
        if result is not None:
            return result
    return None


def _first_todo_line(tree: TodosTree) -> int | None:
    for i, line in enumerate(tree._tree_lines):
        node = line.node
        if node.data and node.data.get("type") == "todo":
            return i
    return None


@pytest.mark.asyncio
async def test_todos_view_opens_from_binding(todos_app: MarkdownEditorApp):
    """F4 shows the right-pane todos view and hides other content views."""
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()

        todos_view = app.query_one("#todos-view", TodosView)
        assert todos_view.display is True
        viewer = app.query_one("#viewer")
        assert viewer.display is False
        graph = app.query_one("#graph-view")
        assert graph.display is False
        assert app.title.startswith("Impactite")


@pytest.mark.asyncio
async def test_todos_view_shows_open_todos_grouped_by_file(todos_app: MarkdownEditorApp):
    """The right pane lists open todos grouped by file."""
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()

        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        all_text = " ".join(_flatten_tree(tree.root))
        assert "top level todo" in all_text
        assert "inbox one" in all_text
        assert "inbox two" in all_text
        assert "archived todo" in all_text
        assert "nested todo" in all_text
        assert "done todo" not in all_text


@pytest.mark.asyncio
async def test_todos_view_sorted_by_relative_path_case_insensitive(todos_app: MarkdownEditorApp):
    """Files in the right pane are sorted case-insensitively by relative path."""
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()

        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        file_labels = [
            str(child.label.plain if hasattr(child.label, "plain") else child.label)
            for child in tree.root.children
            if child.data and child.data.get("type") == "todo-file"
        ]
        expected = [
            "📄 archive.md",
            "📄 inbox.md",
            "📄 project.md",
        ]
        assert file_labels == expected, file_labels


@pytest.mark.asyncio
async def test_todos_view_close_todo_updates_file_and_view(todos_app: MarkdownEditorApp):
    """Space in the right pane closes the selected todo and refreshes the view."""
    app = todos_app
    async with app.run_test(size=(80, 40)) as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()

        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        tree.focus()
        await pilot.pause()

        # Make sure the root and every file node are expanded so rendered lines
        # exist for the todo items.  Then move the cursor to the first todo line.
        tree.root.expand()
        for child in tree.root.children:
            if child.data and child.data.get("type") == "todo-file":
                child.expand()
        await pilot.pause()

        line = _first_todo_line(tree)
        assert line is not None
        tree.move_cursor_to_line(line)
        await pilot.pause()

        todo_node = tree.cursor_node
        assert todo_node is not None and todo_node.data is not None
        assert todo_node.data.get("type") == "todo"
        item = cast(TodoItem, todo_node.data["item"])

        initial_count = len(collect_open_todos(find_note_files(app.file_system.root_path)))
        await pilot.press("space")
        await pilot.pause()

        updated = collect_open_todos(find_note_files(app.file_system.root_path))
        assert len(updated) == initial_count - 1
        assert item not in updated
        all_text = " ".join(_flatten_tree(tree.root))
        assert item.line_text.strip() not in all_text


@pytest.mark.asyncio
async def test_todos_view_select_todo_opens_note(todos_app: MarkdownEditorApp):
    """Selecting a todo-file or todo node opens the corresponding note."""
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()

        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        for child in tree.root.children:
            if child.data and child.data.get("type") == "todo-file":
                tree.select_node(child)
                await pilot.press("enter")
                await pilot.pause()
                break
        else:
            pytest.fail("No todo-file node found")

        assert app.current_file is not None
