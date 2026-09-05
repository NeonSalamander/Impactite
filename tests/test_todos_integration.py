"""End-to-end tests for the right-pane Open todos view."""

from __future__ import annotations

from pathlib import Path
from typing import cast

import pytest
import pytest_asyncio
from textual.widgets.tree import TreeNode

from impactite.app import LeftRibbon, MarkdownEditorApp, TodosTree, TodosView
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
        "# Project\n\n- [ ] top level todo\n- [x] done todo\n  - [ ] nested todo\n",
        encoding="utf-8",
    )
    (root / "inbox.md").write_text(
        "- [ ] inbox one\n- [ ] inbox two\n",
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
        "# Project\n\n- [ ] project todo\n",
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


@pytest.mark.asyncio
async def test_todo_panel_opens_from_binding(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await _open_todos_panel(pilot)
        assert app.query_one("#todos-view", TodosView).display is True


@pytest.mark.asyncio
async def test_todo_panel_opens_from_ribbon_button(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        ribbon = app.query_one("#left-ribbon", LeftRibbon)
        todos_btn = ribbon.query_one("#todos-mode-btn")
        await pilot.click(todos_btn)
        await pilot.pause()
        assert app.query_one("#todos-view", TodosView).display is True
        assert "active" in todos_btn.classes


@pytest.mark.asyncio
async def test_todo_panel_shows_open_todos_from_multiple_files(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        await _open_todos_panel(pilot)

        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        all_text = " ".join(_flatten_tree(tree.root))
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

        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        tree.root.expand()
        file_labels = [
            str(child.label.plain if hasattr(child.label, "plain") else child.label)
            for child in tree.root.children
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
    async with app.run_test(size=(80, 40)) as pilot:
        await pilot.pause()
        await _open_todos_panel(pilot)

        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        tree.focus()
        # Expand nodes so the cursor can land on real todo lines.
        await pilot.pause()
        tree.root.expand()
        for child in tree.root.children:
            child.expand()
        await pilot.pause()

        # Move the cursor to the first rendered todo line so the space binding
        # targets an actual todo node.
        line = None
        for i, tl in enumerate(tree._tree_lines):
            if tl.node.data and tl.node.data.get("type") == "todo":
                line = i
                break
        assert line is not None
        tree.move_cursor_to_line(line)
        await pilot.pause()

        todo_node = tree.cursor_node
        assert todo_node is not None
        assert todo_node.data is not None
        assert todo_node.data.get("type") == "todo"
        item = cast(TodoItem, todo_node.data["item"])

        initial_count = len(collect_open_todos(find_note_files(app.file_system.root_path)))
        await pilot.press("space")
        await pilot.pause()

        updated = collect_open_todos(find_note_files(app.file_system.root_path))
        assert len(updated) == initial_count - 1

        assert item not in updated
        closed_text = item.line_text.strip()
        all_text = " ".join(_flatten_tree(tree.root))
        assert closed_text not in all_text


@pytest.mark.asyncio
async def test_clicking_todo_closes_it_and_refreshes(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test(size=(80, 40)) as pilot:
        await pilot.pause()
        await _open_todos_panel(pilot)

        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        tree.focus()
        tree.root.expand()
        for child in tree.root.children:
            child.expand()
        await pilot.pause()

        line = None
        for i, tl in enumerate(tree._tree_lines):
            if tl.node.data and tl.node.data.get("type") == "todo":
                line = i
                break
        assert line is not None

        initial_count = len(collect_open_todos(find_note_files(app.file_system.root_path)))
        await pilot.click(tree, offset=(2, line))
        await pilot.pause()
        await pilot.pause()

        updated = collect_open_todos(find_note_files(app.file_system.root_path))
        assert len(updated) == initial_count - 1


@pytest.mark.asyncio
async def test_closing_last_todo_removes_note_from_tree(todos_app: MarkdownEditorApp):
    app = todos_app
    async with app.run_test(size=(80, 40)) as pilot:
        await pilot.pause()
        # Leave only one open todo across the whole vault.
        for p in app.file_system.root_path.rglob("*.md"):
            if p.name != "urgent.md":
                text = p.read_text(encoding="utf-8").replace("- [ ]", "- [x]")
                p.write_text(text, encoding="utf-8")

        await _open_todos_panel(pilot)
        todos_view = app.query_one("#todos-view", TodosView)
        tree = todos_view.query_one("#todos-view-tree", TodosTree)
        tree.root.expand()
        for child in tree.root.children:
            child.expand()
        await pilot.pause()

        todo_node = _first_todo_node(tree.root)
        assert todo_node is not None
        # Move the cursor to the rendered line instead of selecting the node,
        # because selecting a todo node triggers note navigation.
        for i, tl in enumerate(tree._tree_lines):
            if tl.node is todo_node:
                tree.move_cursor_to_line(i)
                break
        await pilot.pause()
        await pilot.press("space")
        await pilot.pause()

        assert not collect_open_todos(find_note_files(app.file_system.root_path))
        file_nodes = [
            child for child in tree.root.children
            if child.data and child.data.get("type") == "todo-file"
        ]
        assert file_nodes == []
