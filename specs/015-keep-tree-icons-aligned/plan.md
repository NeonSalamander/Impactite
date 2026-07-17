# Implementation Plan: Keep Tree Icons Aligned

|**Branch**: `015-keep-tree-icons-aligned` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/015-keep-tree-icons-aligned/spec.md`

## Summary

Restore the original emoji pictograms (📁, 📄, 📎, 🕸️, ⭐) on directory-tree nodes while keeping every row horizontally aligned. The implementation will ensure that all labels follow the same `icon + space + name` format so their cell widths match Rich/Textual expectations.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual 8.2.4, Rich
- **Storage**: N/A
- **Testing**: Headless Textual `App.run_test()` smoke tests
- **Target Platform**: Linux terminal (TUI)
- **Project Type**: Python TUI desktop/console app
- **Performance Goals**: N/A (rendering change only)
- **Constraints**: No new dependencies; original emoji characters must be preserved
- **Scale/Scope**: Local single-user file tree UI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Technology Stack**: The change stays within Textual/Rich rendering — **PASS**.
- **II. Architecture**: Rendering logic belongs in `app.py`; no `core.py` changes — **PASS**.
- **III. UI Styling**: Per-node colour handling already uses `render_label` with `Style`; we keep it — **PASS**.
- **IV. Data Management**: No new files/indexes — **PASS**.
- **V. Development Practices**: User-facing labels use existing translation keys; headless smoke tests continue — **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/015-keep-tree-icons-aligned/
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
├── app.py               # FileTree node labels and DirectoryContextMenu UI only
├── core.py              # Config / DirectoryStyle — unchanged
└── i18n.py              # Existing translations — unchanged
```

**Structure Decision**: A purely UI/rendering change scoped to `src/impactite/app.py`.

## Complexity Tracking

No constitution violations.
