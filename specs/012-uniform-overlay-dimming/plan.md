# Implementation Plan: Uniform 25% Overlay Dimming

|**Branch**: `012-uniform-overlay-dimming` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/012-uniform-overlay-dimming/spec.md`

## Summary

Ensure every modal dialog and context menu dims the workspace underneath by a uniform 25%, independent of the current theme. The fix is visual/CSS-only; it does not add data or user settings. The implementation must make dialogs visibly dimmed (currently not dimming) and context menus translucent (currently obscuring) by using a single shared backdrop color/opacity rule rather than a theme-colored overlay.

## Technical Context

|**Language/Version**: Python 3.14+

|**Primary Dependencies**: Textual 8.2.4 (`ModalScreen`, `Screen` CSS, `background` transparency via percentage), Rich (rendering)

|**Storage**: N/A — no new persistent data

|**Testing**: `python -m compileall src`, headless `App.run_test()` smoke tests confirming dialogs/context menu still open without crash, manual visual verification in both dark and light themes

|**Target Platform**: Linux terminal/console (Textual TUI)

|**Project Type**: TUI desktop application

|**Performance Goals**: No functional delay; only CSS/rendering change

|**Constraints**: No new dependencies, no new UI frameworks, must work for dark and light themes, must cover all existing modal screens and the context menu overlay

|**Scale/Scope**: Global styling fix affecting modal backdrops and one context-menu overlay

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Stack**: PASS — no new frameworks; remains within Python/Textual/Rich/CSS.
- **II. Architecture**: PASS — change is presentational, located in `app.py` `DEFAULT_CSS`; no business logic affected.
- **III. Styling**: PASS — uses Textual CSS, must consider both dark and light themes, and defines a single shared dimming rule.
- **IV. Data**: PASS — no persistent state or derived indexes change; only visual rendering changes.
- **V. Practices**: PASS — no new user-facing strings, new dependencies, or UI framework dependencies; passes `compileall`.

## Project Structure

### Documentation (this feature)

```text
specs/012-uniform-overlay-dimming/
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
└── app.py   # Global CSS rules for ModalScreen backdrops and DirectoryContextMenu overlay
```

**Structure Decision**: This is a pure styling correction; the entire change stays in `app.py` `DEFAULT_CSS`. No new core logic, widgets, or data structures are required.

## Complexity Tracking

No constitution violations.
