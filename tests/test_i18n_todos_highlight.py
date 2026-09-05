"""Tests verifying i18n label and active highlight behavior for Open todos."""

from __future__ import annotations

from pathlib import Path

import pytest
import pytest_asyncio

from impactite.app import LeftRibbon, MarkdownEditorApp, TodosView
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
async def test_ribbon_todos_button_tooltip_in_russian(todos_app_ru: MarkdownEditorApp) -> None:
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        ribbon = todos_app_ru.query_one("#left-ribbon", LeftRibbon)
        todos_btn = ribbon.query_one("#todos-mode-btn")
        # The button tooltip is set via the translated i18n key.
        assert todos_btn.tooltip == "Открытые задачи"


@pytest.mark.asyncio
async def test_todos_view_title_in_russian(todos_app_ru: MarkdownEditorApp) -> None:
    """The right-pane todos view uses the translated title."""
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        await pilot.press("f4")
        await pilot.pause()
        assert "Открытые задачи" in todos_app_ru.title


@pytest.mark.asyncio
async def test_todos_ribbon_button_click_shows_pane(todos_app_ru: MarkdownEditorApp) -> None:
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        ribbon = todos_app_ru.query_one("#left-ribbon", LeftRibbon)
        todos_btn = ribbon.query_one("#todos-mode-btn")
        await pilot.click(todos_btn)
        await pilot.pause()
        assert todos_app_ru.query_one("#todos-view", TodosView).display is True
        assert "active" in todos_btn.classes


@pytest.mark.asyncio
async def test_todos_active_highlight_removed_on_file_select(todos_app_ru: MarkdownEditorApp) -> None:
    async with todos_app_ru.run_test() as pilot:
        await pilot.pause()
        ribbon = todos_app_ru.query_one("#left-ribbon", LeftRibbon)
        await pilot.click(ribbon.query_one("#todos-mode-btn"))
        await pilot.pause()

        todos_btn = ribbon.query_one("#todos-mode-btn")
        assert "active" in todos_btn.classes

        # Opening a note from the todos view should switch the ribbon back to files.
        todos_view = todos_app_ru.query_one("#todos-view", TodosView)
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
        assert "active" not in todos_btn.classes
        files_btn = ribbon.query_one("#files-mode-btn")
        assert "active" in files_btn.classes


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
