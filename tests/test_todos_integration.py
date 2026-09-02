"""End-to-end tests for the todo branch inside the file tree."""
from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
import pytest_asyncio
from textual.widgets.tree import TreeNode

from impactite.app import FileTree, MarkdownEditorApp
from impactite.core import Config
from impactite.todo_parser import (
    TodoItem,
    collect_open_todos,
    find_note_files,
)


@pytest_asyncio.fixture
async def todos_app(tmp_path: Path):
    """Create an app with a small vault containing open todos."""
    root = tmp_path / "notes"
    root.mkdir()
    (root / "project.md").write_text(
        "# Project\n\n"
        "- [ ] top level todo\n"
        "- [x] done todo\n"
        "  - [ ] nested todo\n",
        encoding="utf-8",
    )
    (root / "inbox.md").write_text(
        "- [ ] inbox one\n"
        "- [ ] inbox two\n",
        encoding="utf-8",
    )
    (root / "Inbox").mkdir()
    (root / "Inbox" / "urgent.md").write_text(
        "- [ ] inbox urgent\n",
        encoding="utf-8",
    )
    (root / "archive.md").write_text(
        "- [ ] archived todo\n",
        encoding="utf-8",
    )
    # On Windows it is not possible to create project.md and Project.md in the
    # same directory, so put the case-differing variant in a nested directory to
    # keep the test deterministic on case-insensitive filesystems.
    notes_sub = root / "notes"
    notes_sub.mkdir()
    (notes_sub / "Project.md").write_text(
        "# Project\n\n"
        "- [ ] project todo\n",
        encoding="utf-8",
    )
    config = Config(notes_path=str(root), language="en")
    return MarkdownEditorApp(config)


async def _open_todos_panel(pilot):
    await pilot.press("f4")
    await pilot.pause()


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


def _todos_root(file_tree: FileTree) -> TreeNode | None:
    return file_tree._todos_node


@pytest.mark.asyncio
async def test_todo_panel_opens_from_binding(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await _open_todos_panel(pilot)
        file_tree = app.query_one("#file-tree", FileTree)
        todos_root = _todos_root(file_tree)
        assert todos_root is not None
        assert todos_root.is_expanded


@pytest.mark.asyncio
async def test_todo_panel_shows_open_todos_from_multiple_files(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await _open_todos_panel(pilot)

        file_tree = app.query_one("#file-tree", FileTree)
        todos_root = _todos_root(file_tree)
        assert todos_root is not None
        all_text = " ".join(_flatten_tree(todos_root))
        assert "project todo" in all_text
        assert "top level todo" in all_text
        assert "inbox one" in all_text
        assert "inbox two" in all_text
        assert "archived todo" in all_text
        assert "inbox urgent" in all_text
        assert "done todo" not in all_text


@pytest.mark.asyncio
async def test_todo_tree_sorted_by_full_relative_path_case_insensitive(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await _open_todos_panel(pilot)

        file_tree = app.query_one("#file-tree", FileTree)
        todos_root = _todos_root(file_tree)
        assert todos_root is not None
        todos_root.expand()
        file_tree.build_todos_branch()
        file_labels = [
            str(child.label.plain if hasattr(child.label, "plain") else child.label)
            for child in todos_root.children
            if child.data and child.data.get("type") == "todo-file"
        ]
        expected = [
            "📄 archive.md",
            "📄 inbox.md",
            "📄 Inbox/urgent.md",
            "📄 notes/Project.md",
            "📄 project.md",
        ]
        assert file_labels == expected, file_labels


@pytest.mark.asyncio
async def test_close_todo_updates_file_and_tree(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await _open_todos_panel(pilot)

        file_tree = app.query_one("#file-tree", FileTree)
        file_tree.focus()
        # Expand nodes so the cursor can land on real todo lines.
        await pilot.pause()
        todos_root = _todos_root(file_tree)
        assert todos_root is not None
        todos_root.expand()
        file_tree.build_todos_branch()
        for child in todos_root.children:
            child.expand()
        await pilot.pause()

        todo_node = _first_todo_node(todos_root)
        assert todo_node is not None
        file_tree.select_node(todo_node)
        assert todo_node.data is not None
        item = cast(TodoItem, todo_node.data["item"])

        initial_count = len(collect_open_todos(find_note_files(app.file_system.root_path)))
        await pilot.press("space")
        await pilot.pause()

        updated = collect_open_todos(find_note_files(app.file_system.root_path))
        assert len(updated) == initial_count - 1

        assert item not in updated
        closed_text = item.line_text.strip()
        all_text = " ".join(_flatten_tree(todos_root))
        assert closed_text not in all_text
