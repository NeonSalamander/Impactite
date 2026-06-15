# Implementation Plan: Current Note In-Editor Search

**Branch**: `001-current-note-search` | **Date**: 2026-06-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-current-note-search/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add an in-note search capability that works in both view and edit modes for the currently open Markdown note. The user opens a compact overlay dialog with a configurable hotkey (default `F7`), types a query, and sees all occurrences highlighted. Existing previous/next result navigation controls move the selection through matches in the current document. The dialog must not dim the underlying note; it should appear with a shadow effect to preserve context.

## Technical Context

**Language/Version**: Python 3.14+

**Primary Dependencies**: Textual (TUI widgets, screens, CSS), Rich (inline markup, highlighting), PyYAML (configuration), python-markdown / pygments (rendering)

**Storage**: Plain Markdown files (UTF-8) in the configured notes directory; search state is ephemeral and kept in memory.

**Testing**: None currently in the project. New logic should be written so it can be tested in isolation (no Textual `App` dependency) as unit tests are introduced later.

**Target Platform**: Linux terminal / console; cross-platform where Textual + Python 3.14 are available.

**Project Type**: desktop TUI application (single-project layout)

**Performance Goals**:
- Open search dialog within 1 second of hotkey press.
- Highlight results within 500 ms for notes up to 10,000 words.
- Navigate to next/previous match within 500 ms.

**Constraints**:
- Must stay within Textual/Rich UI stack.
- Dialog must cover no more than ~20% of vertical viewing area.
- Must reuse existing previous/next result navigation controls.
- Must support both view and edit modes.

**Scale/Scope**:
- Target notes up to 10,000 words.
- Literal, case-insensitive substring search in the first version.
- Single-language UI strings (English canonical keys translated via `impactite.i18n`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Stack | Stay in Python + Textual/Rich | ✅ Pass | No new web/desktop frameworks introduced. |
| II. Architecture | UI in `app.py`, logic isolated | ✅ Pass | In-note search UI lives in `app.py`; match state/highlight helpers live in a dedicated helper module or `core.py`. |
| III. Styling | Textual CSS + Rich markup | ✅ Pass | Search dialog styled via Textual `DEFAULT_CSS` with translucent background and shadow. |
| IV. Data | UTF-8 Markdown files; no new persistent stores | ✅ Pass | Search state is transient in memory only. |
| V. Practices | i18n via `impactite.i18n`, graceful errors | ✅ Pass | All user-facing labels use canonical English keys; invalid/empty queries handled gracefully. |

## Project Structure

### Documentation (this feature)

```text
specs/001-current-note-search/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
└── impactite/
    ├── app.py              # New InNoteSearch dialog, wiring into MarkdownEditorApp
    ├── core.py             # SearchState / match-list helpers if not already present
    ├── i18n.py             # New translation keys for search labels
    └── table_engine.py     # unchanged

config.yaml                 # New hotkey entry `search_in_note`
```

**Structure Decision**: Keep all new UI code in `app.py` and extract pure substring-match/highlight logic into `core.py` so it remains testable without importing Textual. Hotkey configuration is added to `config.yaml` following the existing pattern.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected.
