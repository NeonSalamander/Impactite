"""Regression tests for toolbar code-block insertion near YAML frontmatter.

Run: uv run python test_toolbar_code_block.py
"""

import asyncio
import tempfile
from pathlib import Path

from textual.widgets import TextArea
from textual.widgets.text_area import Selection

from impactite.app import MarkdownEditorApp, EditorToolbar, ToolButton
from impactite.core import Config, location_after_frontmatter


def test_location_after_frontmatter_only_blank_lines():
    text = "---\ntype: daily_note\ndate: 2026-08-18\n---\n\n"
    assert location_after_frontmatter(text, (0, 0)) == (6, 0), "cursor at start should move to end"
    assert location_after_frontmatter(text, (1, 5)) == (6, 0), "cursor inside frontmatter should move to end"
    assert location_after_frontmatter(text, (3, 0)) == (6, 0), "cursor on closing fence should move to end"


def test_location_after_frontmatter_with_content():
    text = "---\ntype: note\n---\nSome content\nMore content\n"
    assert location_after_frontmatter(text, (0, 0)) == (3, 0), "cursor at start should move before content"
    assert location_after_frontmatter(text, (1, 0)) == (3, 0), "cursor inside frontmatter should move before content"
    assert location_after_frontmatter(text, (4, 0)) == (4, 0), "cursor after frontmatter should stay"


def test_location_after_frontmatter_no_frontmatter():
    text = "# Heading\n\nSome text\n"
    assert location_after_frontmatter(text, (2, 3)) == (2, 3)


def test_location_after_frontmatter_unclosed():
    text = "---\ntype: note\n\nSome text\n"
    assert location_after_frontmatter(text, (1, 0)) == (1, 0)


def make_config(root: Path) -> Config:
    config_path = root / "config.yaml"
    notes_path = root / "notes"
    notes_path.mkdir()
    config_path.write_text(
        f'''notes_path: "{notes_path.as_posix()}"
daily_notes_folder: "Daily notes"
language: "en"
hotkeys:
  open_file: "enter"
  edit_mode: "e"
  view_mode: "v"
  save_file: "ctrl+s"
  search_tags: "ctrl+t"
  close_search: "escape"
  quit: "ctrl+q"
  refresh: "ctrl+r"
  toggle_sidebar: "ctrl+b"
display:
  show_line_numbers: true
  word_wrap: true
  syntax_theme: "monokai"
  code_border: "round"
  app_theme: "textual-dark"
tags:
  show_cloud: true
  min_tag_size: 1
  max_tag_size: 3
''',
        encoding="utf-8",
    )
    return Config.load(str(config_path))


async def test_daily_note_code_block_after_frontmatter():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        config = make_config(root)
        app = MarkdownEditorApp(config=config)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app._create_daily_note()
            await pilot.pause()

            editor = app.query_one("#editor", TextArea)
            assert editor.selection.start == (0, 0), "cursor should start at top-left"

            toolbar = app.query_one("#editor-toolbar", EditorToolbar)
            code_btn = toolbar.query_one("#toolbar-code", ToolButton)
            code_btn.post_message(ToolButton.Pressed(code_btn.id))
            await pilot.pause()

            lines = editor.text.splitlines()
            assert lines[0] == "---", "opening frontmatter fence must be preserved"
            assert lines[1].startswith("type:"), "frontmatter type line must be preserved"
            assert lines[2].startswith("date:"), "frontmatter date line must be preserved"
            assert lines[3] == "---", "closing frontmatter fence must be preserved"
            assert "```" in lines[4:], "empty code block must appear after frontmatter"


async def test_code_block_wraps_selection():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        config = make_config(root)
        app = MarkdownEditorApp(config=config)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            app._create_daily_note()
            await pilot.pause()

            editor = app.query_one("#editor", TextArea)
            # Select the "type: daily_note" line.
            editor.selection = Selection((1, 0), (2, 0))
            editor.focus()
            await pilot.pause()

            toolbar = app.query_one("#editor-toolbar", EditorToolbar)
            code_btn = toolbar.query_one("#toolbar-code", ToolButton)
            code_btn.post_message(ToolButton.Pressed(code_btn.id))
            await pilot.pause()

            assert "```\ntype:" in editor.text, "selection must be wrapped in a code block"


def run_sync(coro):
    return asyncio.run(coro)


if __name__ == "__main__":
    test_location_after_frontmatter_only_blank_lines()
    test_location_after_frontmatter_with_content()
    test_location_after_frontmatter_no_frontmatter()
    test_location_after_frontmatter_unclosed()
    run_sync(test_daily_note_code_block_after_frontmatter())
    run_sync(test_code_block_wraps_selection())
    print("All tests passed.")
