"""Tests verifying i18n label and active highlight behavior for Open todos."""

from __future__ import annotations

from pathlib import Path

import pytest
import pytest_asyncio
from textual.widgets import Tree

from impactite.app import FileTree, MarkdownEditorApp
from impactite.core import Config
from impactite.i18n import set_language, t


@pytest_asyncio.fixture
async def todos_app_ru(tmp_path: Path):
    """App configured with Russian interface and a note containing a todo."""
    root = tmp_path / "notes"
    root.mkdir()
    (root / "project.md").write_text("# Project\n\n- [ ] todo one\n", encoding="utf-8")
    config = Config(notes_path=str(root), language="ru")
    return MarkdownEditorApp(config)


def test_russian_open_todos_translation() -> None:
    set_language("ru")
    assert t("Open todos") == "Открытые задачи"


def test_english_open_todos_translation() -> None:
    set_language("en")
    assert t("Open todos") == "Open todos"


def test_german_open_todos_translation() -> None:
    set_language("de")
    assert t("Open todos") == "Offene TODOs"


@pytest.mark.asyncio
async def test_sidebar_todos_node_label_in_russian(todos_app_ru: MarkdownEditorApp) -> None:
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        # Trigger a file-tree refresh so labels are rebuilt after set_language("ru").
        todos_app_ru._refresh_file_tree()
        await pilot.pause()
        file_tree = todos_app_ru.query_one("#file-tree", Tree)
        labels = [
            str(child.label.plain if hasattr(child.label, "plain") else child.label)
            for child in file_tree.root.children
        ]
        # After a refresh the predefined nodes are rebuilt using the current
        # language, so the Russian translation should now appear.
        assert any("Открытые задачи" in label for label in labels), labels


@pytest.mark.asyncio
async def test_todos_view_title_in_russian(todos_app_ru: MarkdownEditorApp) -> None:
    """The right-pane todos view uses the translated title."""
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()
        assert "Открытые задачи" in todos_app_ru.title


@pytest.mark.asyncio
async def test_todos_active_highlight_moves_cursor(todos_app_ru: MarkdownEditorApp) -> None:
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()
        file_tree = todos_app_ru.query_one("#file-tree", Tree)
        assert file_tree.cursor_node is not None
        assert file_tree.cursor_node.data is not None
        assert file_tree.cursor_node.data.get("type") == "todos-root"
        assert todos_app_ru.query_one("#todos-view").display is True


@pytest.mark.asyncio
async def test_todos_active_highlight_removed_on_file_select(todos_app_ru: MarkdownEditorApp) -> None:
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()

        file_tree = todos_app_ru.query_one("#file-tree", FileTree)
        # Start with the todos root highlighted.
        assert file_tree.cursor_node is not None
        assert file_tree.cursor_node.data.get("type") == "todos-root"

        # Move the highlight to a regular file node without raising a selection
        # event, which mimics what _highlight_sidebar_route("file") does.
        file_node = None
        for node in file_tree._walk_tree_nodes(file_tree.root):
            if isinstance(node.data, Path) and node.data.is_file():
                file_node = node
                break
        assert file_node is not None
        file_tree.highlight_node(file_node)
        await pilot.pause()

        assert file_tree.cursor_node is not None
        assert file_tree.cursor_node == file_node
        # Highlight is now on a file node, not the todos root.
        assert file_tree.cursor_node.data is not file_tree._todos_node.data


@pytest.mark.asyncio
async def test_selecting_file_from_todos_view_switches_to_viewer(todos_app_ru: MarkdownEditorApp) -> None:
    """Opening a note from the right-pane todos view hides the pane."""
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()

        todos_view = todos_app_ru.query_one("#todos-view")
        tree = todos_view.query_one("#todos-view-tree")
        file_node = None
        for child in tree.root.children:
            if child.data and child.data.get("type") == "todo-file":
                file_node = child
                break
        assert file_node is not None
        tree.select_node(file_node)
        await pilot.press("enter")
        await pilot.pause()

        assert todos_app_ru.current_file is not None
        assert todos_app_ru.query_one("#viewer").display is True
        assert todos_app_ru.query_one("#todos-view").display is False
