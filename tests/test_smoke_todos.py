"""Smoke test for DOM."""

import pytest

from impactite.app import MarkdownEditorApp, TodosView
from impactite.core import Config


@pytest.mark.asyncio
async def test_todos_view_in_dom(tmp_path):
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "a.md").write_text("# A\n", encoding="utf-8")
    app = MarkdownEditorApp(Config(notes_path=str(tmp_path / "notes"), language="en"))
    async with app.run_test() as pilot:
        await pilot.pause()
        todos_view = app.query_one("#todos-view", TodosView)
        assert todos_view is not None
        assert todos_view.display is False
