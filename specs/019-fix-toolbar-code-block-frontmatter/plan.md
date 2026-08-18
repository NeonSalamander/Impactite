# Implementation Plan: Fix toolbar code block insertion inside frontmatter

**Branch**: `019-fix-toolbar-code-block-frontmatter` | **Date**: 2026-08-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/019-fix-toolbar-code-block-frontmatter/spec.md`

## Summary

Move the empty code-block insertion out of YAML frontmatter by adding a small, testable helper in `core.py` that computes a safe insertion point, and use it in the `code` toolbar action handler in `app.py`. Keep the existing "wrap selection" behaviour unchanged.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual 8.2.4, PyYAML
- **Storage**: Markdown files in `notes_path`
- **Testing**: `pytest` with headless Textual `App.run_test()`
- **Target Platform**: Windows/Linux terminal (TUI)
- **Project Type**: Python TUI desktop/console app
- **Performance Goals**: N/A
- **Constraints**: No new dependencies; helper must be unit-testable without Textual imports
- **Scale/Scope**: Single toolbar action fix

## Constitution Check

- **I. Technology Stack**: The change uses only existing Python/Textual mechanisms — **PASS**.
- **II. Architecture**: Frontmatter detection lives in `core.py`; toolbar handling stays in `app.py` — **PASS**.
- **III. UI Styling**: No CSS changes — **PASS**.
- **IV. Data Management**: No new indexes or storage; only text insertion behaviour changes — **PASS**.
- **V. Development Practices**: User-facing strings are unchanged; pure helper can be unit-tested — **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/019-fix-toolbar-code-block-frontmatter/
├── plan.md              # This file
├── spec.md              # Feature specification
├── tasks.md             # Implementation tasks
└── research.md          # Reproduction notes
```

### Source Code (repository root)

```text
src/impactite/
├── core.py              # New helper: location_after_frontmatter
└── app.py               # Updated on_editor_toolbar_action code branch
```

### Tests

```text
test_toolbar_code_block.py   # Unit tests for helper + headless UI test
```

**Structure Decision**: A core/app coordination bugfix; no new modules.

## Complexity Tracking

No constitution violations.
