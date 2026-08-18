# Implementation Plan: Preserve file tree expansion when creating notes

**Branch**: `020-preserve-tree-expansion` | **Date**: 2026-08-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/020-preserve-tree-expansion/spec.md`

## Summary

Capture the expansion state of directory nodes and the currently selected directory before `FileTree.populate_tree` clears and rebuilds the tree, then restore that state after the rebuild. Keep the change inside the UI layer (`app.py`) because it deals with widget state.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual 8.2.4
- **Storage**: Markdown files in `notes_path`
- **Testing**: `pytest`-style standalone test run via `uv run python test_*.py`
- **Target Platform**: Windows/Linux terminal (TUI)
- **Project Type**: Python TUI desktop/console app
- **Performance Goals**: N/A
- **Constraints**: No new dependencies; minimal changes to existing tree logic
- **Scale/Scope**: Single widget behaviour fix

## Constitution Check

- **I. Technology Stack**: The change uses only Textual's existing `Tree`/`TreeNode` API — **PASS**.
- **II. Architecture**: The fix lives in the UI layer (`FileTree` in `app.py`) and does not call business-logic methods from core — **PASS**.
- **III. UI Styling**: No CSS changes — **PASS**.
- **IV. Data Management**: No new indexes or storage; only transient widget state is preserved — **PASS**.
- **V. Development Practices**: No new user-facing strings; change is testable in headless mode — **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/020-preserve-tree-expansion/
├── plan.md              # This file
├── spec.md              # Feature specification
├── tasks.md             # Implementation tasks
└── research.md          # Reproduction notes
```

### Source Code (repository root)

```text
src/impactite/
└── app.py               # FileTree.populate_tree and helpers
```

### Tests

```text
test_tree_expansion.py   # Headless regression tests
```

**Structure Decision**: A UI-only fix in the existing `FileTree` class; no new modules.

## Complexity Tracking

No constitution violations.
