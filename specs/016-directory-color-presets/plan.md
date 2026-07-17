# Implementation Plan: Directory Color Presets

|**Branch**: `016-directory-color-presets` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/016-directory-color-presets/spec.md`

## Summary

Add a 16-colour preset palette to the existing directory colour modal. The palette will be compact and sit alongside the current background/text colour inputs. Clicking a preset fills the colour input that the user has last selected (background or text); the form must keep track of that selection even when a preset button receives focus for clicking. If neither input has been focused, the background input is filled by default. Manual entry remains fully supported.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual 8.2.4, Rich
- **Storage**: N/A (directory colours already saved in `config.yaml` through existing `DirectoryStyle` logic)
- **Testing**: Headless Textual `App.run_test()` smoke tests plus focused tests for the modal
- **Target Platform**: Linux terminal (TUI)
- **Project Type**: Python TUI desktop/console app
- **Performance Goals**: N/A
- **Constraints**: No new dependencies; keep the existing validation and persistence flow
- **Scale/Scope**: Single modal UI enhancement

## Constitution Check

- **I. Technology Stack**: The change uses only Textual/Rich widgets — **PASS**.
- **II. Architecture**: UI code remains in `app.py`; persistence logic already lives in `core.py` and is not modified — **PASS**.
- **III. UI Styling**: New widgets rely on existing `DEFAULT_CSS` / inline styles; theming is handled by Textual — **PASS**.
- **IV. Data Management**: No new indexes or files; `DirectoryStyle` already persisted in `config.yaml` — **PASS**.
- **V. Development Practices**: New user-facing labels require canonical English keys and translations in `i18n.py` (e.g., "Preset colors") — **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/016-directory-color-presets/
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
├── app.py               # DirectoryColorModal UI changes
└── i18n.py              # Translations for new labels
```

**Structure Decision**: A UI-only change within the existing directory colour modal.

## Complexity Tracking

No constitution violations.
