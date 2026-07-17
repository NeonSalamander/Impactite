# Implementation Plan: Visible Context-Menu Overlay

|**Branch**: `013-visible-context-menu-overlay` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/013-visible-context-menu-overlay/spec.md`

## Summary

Fix the directory context-menu overlay so the workspace behind it remains visible instead of being covered by a near-solid dark layer. Apply the same principle to modal dialogs for consistency. The change is purely visual/CSS and localized to `src/impactite/app.py`.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual 8.2.4
- **Storage**: N/A
- **Testing**: `python -m compileall src`, headless `App.run_test()` smoke tests
- **Target Platform**: Terminal/console (Linux, Windows Terminal)
- **Project Type**: console TUI application
- **Performance Goals**: N/A
- **Constraints**: Must not hide underlying widgets; must work in both dark and light themes.
- **Scale/Scope**: Single widget CSS change.

## Constitution Check

- **No new dependencies** — only existing Textual CSS features used.
- **UI code stays in `app.py`** — `core.py` unchanged.
- **No persistent data changes** — `config.yaml` not touched.
- **Localized CSS** — `DEFAULT_CSS` class variable.
- **Headless validation** — required by constitution.

*Gate passes.*

## Project Structure

### Documentation (this feature)

```text
specs/013-visible-context-menu-overlay/
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
├── app.py               # CSS overlay rules changed here
├── core.py              # No changes
├── i18n.py              # No changes
└── ...
```

**Structure Decision**: Only `app.py DEFAULT_CSS` changes. The shortest, least-risk fix is to make the `DirectoryContextMenu` overlay translucent/transparent and, if necessary, adjust the shared modal overlay value so dialogs remain subdued but not opaque.
