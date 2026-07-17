# Implementation Plan: Directory Context Menu

|**Branch**: `010-directory-context-menu` | **Date**: 2026-06-26 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/010-directory-context-menu/spec.md`

## Summary

Allow users to right-click a directory in the file tree to open a context menu. The menu offers a "Directory settings" option that opens the existing color dialog, and a "Reset directory color" option that removes saved colors. The feature reuses the per-directory color persistence introduced by feature `009-directory-tree-colors` and adds only the interaction layer.

## Technical Context

|**Language/Version**: Python 3.14+

|**Primary Dependencies**: Textual 8.2.4 (`Tree`, `TreeNode`, `MouseDown`, offset-based positioning), Rich (`Text`, `Color.parse`), PyYAML

|**Storage**: `config.yaml` top-level key `directory_colors` (managed by existing `Config` methods)

|**Testing**: `python -m compileall src`, headless `App.run_test()` for the context-menu flow, and manual run verification

|**Target Platform**: Linux terminal/console (portable to any terminal with mouse support)

|**Project Type**: Textual TUI application

|**Performance Goals**: Context menu opens within 100 ms of the right-click; color change applies within 1 second

|**Constraints**: No new dependencies, no new UI frameworks, context menu must appear near the pointer, persistence side effects limited to `config.yaml`

|**Scale/Scope**: Context menu actions are scoped to a single directory; only directories carry the `data=path` attribute used to identify them

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Stack**: PASS — no new frameworks; stays within Python/Textual/Rich/PyYAML.
- **II. Architecture**: PASS — UI interaction (menu and right-click handling) lives in `app.py`; persistence and color data remain in `core.py`; existing widgets communicate via messages.
- **III. Styling**: PASS — floating menu uses Textual/Rich styling and respects current theme; it does not introduce external CSS files.
- **IV. Data**: PASS — `config.yaml` remains the only changed persistent artifact; disposable indexes are untouched.
- **V. Practices**: PASS — new user-facing strings use `impactite.i18n.t`; business logic stays testable without UI classes.

## Project Structure

### Documentation (this feature)

```text
specs/010-directory-context-menu/
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
├── app.py   # FileTree right-click handler, DirectoryContextMenu, wiring to DirectoryColorModal/actions
├── core.py  # Reuses DirectoryStyle/Config.directory_colors from feature 009
└── i18n.py  # New translations for context menu labels
```

**Structure Decision**: All new interaction code stays in `app.py`. No additional business logic or persistence is required because feature 009 already provides the color data model and config storage. Right-click detection and the floating context menu are implemented as part of the `FileTree` widget.

## Complexity Tracking

No constitution violations.
