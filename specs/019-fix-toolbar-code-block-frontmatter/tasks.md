# Tasks: Fix toolbar code block insertion inside frontmatter

**Input**: Design documents from `specs/019-fix-toolbar-code-block-frontmatter/`

**Prerequisites**: plan.md, spec.md, research.md

## Phase 0 — Reproduce & lock behaviour

- [x] T001 Read `src/impactite/app.py` to locate the toolbar `code` action handler (`on_editor_toolbar_action`) and the current empty-insertion logic.
- [x] T002 Reproduce the bug with a temporary headless test: create a daily note and verify that an empty code block inserted at `(0, 0)` corrupts the frontmatter.
- [x] T003 Write a failing regression test in `test_toolbar_code_block.py` that creates a daily note, clicks `#toolbar-code`, and asserts the code block is inserted after the frontmatter.

## Phase 1 — Core helper

- [x] T004 Add a pure helper `location_after_frontmatter(text: str, location: tuple[int, int]) -> tuple[int, int]` to `src/impactite/core.py`.
  - Detects a YAML frontmatter block starting at line 0 (`---`) and closed by another `---` line.
  - If `location` is inside or before the closing fence, returns the first non-blank line after the fence, or the end of the document if only blank lines follow.
  - Otherwise returns the original `location`.
  - Handles unclosed frontmatter and notes without frontmatter gracefully.
- [x] T005 Add unit tests for `location_after_frontmatter` covering:
  - daily-note frontmatter with trailing blank lines,
  - frontmatter followed by content,
  - cursor after frontmatter unchanged,
  - note without frontmatter unchanged,
  - unclosed frontmatter unchanged.

## Phase 2 — UI fix

- [x] T006 Update `MarkdownEditorApp.on_editor_toolbar_action` in `src/impactite/app.py`.
  - In the `code` branch, when there is **no** selection, compute `safe_start = location_after_frontmatter(editor.text, start)`.
  - Insert ` ```\n\n``` ` at `safe_start` and move the cursor to the blank line inside the new block.
  - Leave the selection-wrapping branch unchanged.

## Phase 3 — Validation

- [x] T007 Run the regression test from T003 and verify it passes.
- [x] T008 Run the unit tests for `location_after_frontmatter` and verify they pass.
- [x] T009 Run `python -m compileall src`.
- [x] T010 Run `uv run python test_toolbar_code_block.py`.
- [x] T011 Revert any unintended changes to workspace `config.yaml`.
