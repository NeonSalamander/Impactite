# Implementation Plan: Directory Tree Colors

|**Branch**: `009-directory-tree-colors` | **Date**: 2026-06-26 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/009-directory-tree-colors/spec.md`

## Summary

Allow users to assign a custom background and label color to each directory in the file tree. Colors are persisted in `config.yaml` (keyed by directory path relative to the notes root) and applied immediately to the tree through a customized `FileTree` label renderer. A small modal collects the two color values and a dedicated action resets them.

## Technical Context

|**Language/Version**: Python 3.14+

|**Primary Dependencies**: Textual 8.2.4 (`Tree`, `TreeNode`, `ModalScreen`, `Style`), Rich (`Text`, `Color.parse`), PyYAML

|**Storage**: `config.yaml` top-level key `directory_colors`

|**Testing**: `python -m compileall src`, headless `App.run_test()` for the modal flow, and manual run verification

|**Target Platform**: Linux terminal/console (portable to any terminal with color support)

|**Project Type**: Textual TUI application

|**Performance Goals**: Directory tree refresh under 100 ms for 1,000 nodes; config save under 50 ms

|**Constraints**: No new dependencies, no new UI frameworks, persistence side effects limited to `config.yaml`

|**Scale/Scope**: Per-directory color mapping scoped to the active vault; expected mapping size bounded by the number of directories in the notes tree

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Stack**: PASS — no new frameworks; stays within Python/Textual/Rich/PyYAML.
- **II. Architecture**: PASS — UI rendering and modal live in `app.py`; persistence and the color data type live in `core.py`; widgets communicate via messages.
- **III. Styling**: PASS — directory colors are applied through Textual's `Tree.render_label`/`Style` API; no external CSS files.
- **IV. Data**: PASS — `config.yaml` is the only changed persistent artifact; disposable indexes are untouched.
- **V. Practices**: PASS — new user-facing strings are added through `impactite.i18n.t`; business logic remains testable without importing UI classes.

## Project Structure

### Documentation (this feature)

```text
specs/009-directory-tree-colors/
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
├── app.py   # FileTree directory-color rendering, DirectoryColorModal, actions
├── core.py  # DirectoryStyle dataclass, Config.directory_colors load/save
└── i18n.py  # New translations for color-modal labels
```

**Structure Decision**: All per-directory color data and persistence are kept in `core.py`; all rendering and user interaction are kept in `app.py`. The `FileTree` widget receives the color map during population and applies it internally.

## Complexity Tracking

No constitution violations.
