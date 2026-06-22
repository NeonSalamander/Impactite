# Implementation Plan: Add W311 Theme

**Branch**: `008-add-w311-theme` | **Date**: 2026-06-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/008-add-w311-theme/spec.md`

## Summary

Add a selectable application theme named "W311" that reproduces the classic Windows 3.11 color scheme (light gray chrome, dark blue title bars, black text). Because W311 is a light theme, it must be registered as a Textual theme and included in the existing light-theme tracking so the editor code block uses a light pygments theme.

## Technical Context

**Language/Version**: Python 3.14+

**Primary Dependencies**: Textual's `Theme`/`register_theme` API, Rich/pygments for code blocks

**Storage**: `config.yaml` key `display.app_theme`

**Testing**: Headless `App.run_test()` plus `python -m compileall src`

**Target Platform**: Linux terminal/console (portable to any terminal with color support)

**Project Type**: Textual TUI application

**Performance Goals**: Theme switch visible within one frame; startup theme resolution under 100 ms

**Constraints**: No new dependencies, no new UI frameworks, no persistent side effects outside `config.yaml`

**Scale/Scope**: One theme definition and minor validation logic changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Stack**: PASS — no new frameworks, stays within Python/Textual/Rich.
- **II. Architecture**: PASS — UI/theme definition lives in `app.py`; persistence reuses `Config` in `core.py`.
- **III. Styling**: PASS — uses Textual `Theme`/`DEFAULT_CSS`; light-theme tracking updated as required by constitution.
- **IV. Data**: PASS — `config.yaml` is the only changed persistent artifact; disposable indexes untouched.
- **V. Practices**: PASS — no new user-facing strings requiring i18n unless a theme picker is introduced.

## Project Structure

### Documentation (this feature)

```text
specs/008-add-w311-theme/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/impactite/
├── app.py   # Theme definition, registration, light-theme set, startup validation
├── core.py  # Config load/save for app_theme
└── i18n.py  # No changes expected
```

**Structure Decision**: Theme is defined and registered in `app.py` next to the existing `TV_THEME`. Persistence is handled via `Config.save_user_theme`/`get_user_theme` already used by other themes.

## Complexity Tracking

No constitution violations.
