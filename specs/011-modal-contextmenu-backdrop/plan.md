# Implementation Plan: Modal and Context Menu Backdrop Dimming

|**Branch**: `011-modal-contextmenu-backdrop` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/011-modal-contextmenu-backdrop/spec.md`

## Summary

Reduce the darkness of modal-dialog and context-menu backdrops so the workspace behind them stays visible instead of turning black. The change is implemented purely through Textual/Rich styling; no new data model or persistent configuration is introduced. Every modal screen and the full-screen context-menu overlay use the same light dimming level, keeping the UI consistent across dark and light themes.

## Technical Context

|**Language/Version**: Python 3.14+

|**Primary Dependencies**: Textual 8.2.4 (`ModalScreen`, `Screen` CSS, `background` transparency via percentage), Rich (rendering)

|**Storage**: N/A — no new persistent data

|**Testing**: `python -m compileall src`, headless `App.run_test()` smoke tests to confirm dialogs/context menu still open and do not crash, manual visual verification

|**Target Platform**: Linux terminal/console (applies wherever Textual runs)

|**Project Type**: Textual TUI application

|**Performance Goals**: No measurable functional delay; only CSS opacity changes

|**Constraints**: No new dependencies, no new UI frameworks, must work for both dark and light themes, must cover all existing modal screens and the context menu overlay

|**Scale/Scope**: Visual change that applies globally to modal screens and one overlay widget introduced in feature 010

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Stack**: PASS — no new frameworks; remains within Python/Textual/Rich/CSS.
- **II. Architecture**: PASS — change is purely presentational, located in `app.py` `DEFAULT_CSS`; no business logic is affected.
- **III. Styling**: PASS — uses Textual CSS, respects current theme via `$background`, and defines a single shared dimming level.
- **IV. Data**: PASS — no persistent state or derived indexes change; only visual rendering changes.
- **V. Practices**: PASS — no new user-facing strings, no new UI framework dependencies, still passes `compileall`.

## Project Structure

### Documentation (this feature)

```text
specs/011-modal-contextmenu-backdrop/
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

**Structure Decision**: Because this feature only adjusts visual styling, the entire change lives in `app.py` `DEFAULT_CSS`. No new core logic, widgets, or data structures are required.

## Complexity Tracking

No constitution violations.
