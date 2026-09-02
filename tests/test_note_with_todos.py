from __future__ import annotations

from pathlib import Path

import pytest
import pytest_asyncio

from impactite.app import MarkdownEditorApp
from impactite.core import Config


@pytest_asyncio.fixture
async def note_with_todos_app(tmp_path: Path):
    """Create an app whose note has inline todos, then open it."""
    root = tmp_path / "notes"
    root.mkdir()
    (root / "project.md").write_text(
        "# Project\n\n"
        "- [ ] top level todo\n"
        "- [x] done todo\n"
        "  - [ ] nested todo\n",
        encoding="utf-8",
    )
    config = Config(notes_path=str(root), language="en")
    app = MarkdownEditorApp(config)
    app.current_file = root / "project.md"
    return app


@pytest.mark.asyncio
async def test_opening_note_with_todos_does_not_raise(
    note_with_todos_app: MarkdownEditorApp,
) -> None:
    app = note_with_todos_app
    async with app.run_test() as pilot:
        await pilot.pause()
        # Regression: this used to trigger UnboundLocalError in
        # MarkdownViewer.update_content when `_` was loaded before the first
        # loop assignment.
        app._load_file()
        await pilot.pause()
        assert app.current_file is not None
        assert app.current_file.name == "project.md"
