# Implementation Plan: Fix Theme Toggle

**Branch**: `003-fix-theme-toggle` | **Date**: 2026-06-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-fix-theme-toggle/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Fix the `Ctrl+L` theme toggle so that it switches between light and dark variants of the user's selected theme without overwriting the user's theme preference in `config.yaml`. Introduce a small, testable helper to resolve the counterpart theme for a given mode and suppress theme persistence while the toggle is in progress.

## Technical Context

**Language/Version**: Python 3.14+

**Primary Dependencies**: Textual, Rich, pygments

**Storage**: `config.yaml` (user configuration file)

**Testing**: `python -m compileall src` for syntax validation, manual end-to-end validation by launching `uv run impactite` and toggling `Ctrl+L`

**Target Platform**: Linux terminal / console TUI

**Project Type**: desktop TUI application

**Performance Goals**: Theme toggle must be instantaneous with no perceptible UI delay

**Constraints**: Stay within the Python 3.14 + Textual stack; keep UI code in `app.py`; keep pure theme-resolution logic in `core.py`; user-facing strings must use `impactite.i18n.t`

**Scale/Scope**: Single-user local configuration; no network or multi-user concerns

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Notes |
|-----------|-------|-------|
| I. Stack | PASS | No new frameworks or dependencies required; change remains inside Python/Textual. |
| II. Architecture | PASS | UI handling stays in `app.py`; theme-resolution logic moves to `core.py` as pure helpers; no widget calls cross into core. |
| III. Styling | PASS | Existing `_LIGHT_THEMES` set in `app.py` remains the source of truth for light themes. |
| IV. Data | PASS | Only `config.yaml` is modified; indexes are untouched. |
| V. Practices | PASS | New logic will be typed; errors surfaced via notifications/status bar; run `compileall` and launch check before commit. |

## Project Structure

### Documentation (this feature)

```text
specs/003-fix-theme-toggle/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/impactite/
├── app.py       # UI: reactive theme flag, toggle action, editor theme refresh
├── core.py      # Business logic: Config theme accessors, pure theme variant resolver
└── i18n.py      # Localization keys if user-facing messages are added

config.yaml     # display.app_theme remains the persisted user preference
```

**Structure Decision**: This is a focused bug fix within the existing single-project layout. The change touches `app.py` for the toggle behavior and `core.py` for testable theme-resolution helpers.

## Complexity Tracking

No constitution violations required.
