# Implementation Plan: Add TV Theme

**Branch**: `007-add-tv-theme` | **Date**: 2026-06-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/007-add-tv-theme/spec.md`

**Summary**: Register a custom Textual theme named "tv" that uses a TurboVision-inspired 16-color palette, wire it into the existing theme-loading and toggling logic, and ensure the editor syntax theme remains readable against the dark-blue application background.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual (theme system, widgets, CSS variables), Rich, pygments
- **Storage**: `config.yaml` persists the user's selected theme name under `display/theme` or equivalent
- **Testing**: Manual verification via `uv run impactite`; no automated test suite yet
- **Target Platform**: Linux terminal (CachyOS), any terminal that supports Textual
- **Project Type**: Console TUI application
- **Performance Goals**: Theme switch completes in under 500 ms; startup with persisted TV theme is not measurably slower
- **Constraints**: No new packages; theme must be defined with Textual's `Theme` class; custom CSS respects the constitution's styling principles
- **Scale/Scope**: One new theme definition plus a few small adjustments to theme loading/toggling logic

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Technology Stack | ✓ PASS | Stays inside Textual/Rich; no new frameworks or dependencies |
| II. Architecture | ✓ PASS | Theme logic lives in `app.py`; no changes to `core.py` business logic |
| III. Styling | ✓ PASS | Uses Textual `Theme` and CSS variables; `DEFAULT_CSS` unaffected unless adding TV-specific overrides |
| IV. Data Management | ✓ PASS | Persistence reuses existing `config.yaml` theme field |
| V. Development Practices | ✓ PASS | User-facing labels go through `i18n.t`; colors are code-only constants |

**Potential concern**: Section III requires updating `_LIGHT_THEMES` if the new theme is light. The TV theme is dark, so no update is needed.

**Re-check after Phase 1**: Still passes. Theme added via `register_theme` and validated against registered themes.

## Project Structure

### Documentation (this feature)

```text
specs/007-add-tv-theme/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code

```text
src/impactite/
├── app.py              # Define TV theme, register it, update theme loading/toggle
├── core.py             # Possibly update `validate_theme` if custom themes are validated here
└── i18n.py             # Optional label keys if a theme picker is added
```

**Structure Decision**: The theme is defined in `app.py` as a `textual.theme.Theme` instance. Existing theme helpers in `core.py` are updated only if they need to recognize custom registered themes. No new modules.

## Phase 0: Research & Decisions

See `research.md` for the following resolved questions:

- How to define a custom Textual theme (subclass `Theme` or use constructor).
- How to register a custom theme so that `App.theme = "tv"` is valid.
- How to integrate the custom theme with `config.yaml` persistence and the `Ctrl+L` light/dark toggle.
- Which TurboVision colors to map to Textual theme tokens.
- Which pygments editor theme pairs well with a dark-blue TV background.

## Complexity Tracking

No complexity justifications needed.
