# Implementation Plan: Remember User Theme

|**Branch**: `017-remember-user-theme` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/017-remember-user-theme/spec.md`

## Summary

Ensure the application saves the user's selected theme when it changes and restores that saved theme on the next startup, falling back to the default light theme only when no valid saved theme exists.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual 8.2.4, PyYAML
- **Storage**: Existing `config.yaml` (already holds `display.app_theme`)
- **Testing**: Headless Textual `App.run_test()` smoke/contract tests
- **Target Platform**: Linux terminal (TUI)
- **Project Type**: Python TUI desktop/console app
- **Performance Goals**: N/A
- **Constraints**: No new dependencies; preserve the existing theme-toggle (Ctrl+L) light/dark variant behaviour; configuration writes must not corrupt unrelated settings
- **Scale/Scope**: Single configuration persistence flow fix

## Constitution Check

- **I. Technology Stack**: The change uses only existing Python/Textual/YAML mechanisms — **PASS**.
- **II. Architecture**: `Config` (core.py) owns reading/writing `app_theme`; `app.py` owns applying the theme on startup and toggle interactions — **PASS**.
- **III. UI Styling**: No new CSS or styling logic beyond existing theme switching — **PASS**.
- **IV. Data Management**: Data is stored in the existing `config.yaml`, no new derived indexes — **PASS**.
- **V. Development Practices**: User-facing strings already localized where applicable; no new labels required — **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/017-remember-user-theme/
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
├── app.py               # Theme restore on startup and toggle guard
└── core.py              # Config save_theme / get_user_theme logic
```

**Structure Decision**: A core/app coordination fix; no new modules.

## Complexity Tracking

No constitution violations.
