# Implementation Plan: Fix Directory Tree Line Offset

|**Branch**: `014-fix-directory-tree-line-offset` | **Date**: 2026-06-27 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/014-fix-directory-tree-line-offset/spec.md`

## Summary

The directory tree uses emoji icons at the start of some nodes. Different terminals treat certain emoji/grapheme clusters as either 1 or 2 display cells, which shifts the rest of the line by one character on affected rows. The fix is to replace variable-width emoji prefixes with fixed-width terminal-safe glyphs so every row consumes exactly the same number of cells in any terminal.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual 8.2.4, Rich
- **Storage**: N/A
- **Testing**: `python -m compileall src`; headless smoke test with `App.run_test()`; visual manual check
- **Target Platform**: Terminal/console
- **Project Type**: console TUI application
- **Performance Goals**: N/A
- **Constraints**: Must keep tree labels readable and themable; must not increase line width beyond one cell for icons.
- **Scale/Scope**: Single widget fix in `src/impactite/app.py`.

## Constitution Check

- No new dependencies.
- UI change stays in `app.py`.
- No persistent data changes.
- Styles remain CSS-driven where possible; icon strings are defined in `app.py`.
- Headless validation required.

*Gate passes; no complexity-tracking entries needed.*

## Project Structure

### Documentation (this feature)

```text
specs/014-fix-directory-tree-line-offset/
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
├── app.py               # FileTree icon strings and rendering changed here
├── core.py              # No changes
├── i18n.py              # No changes
└── ...
```

**Structure Decision**: Only the `FileTree` icon strings and possibly `render_label` in `src/impactite/app.py` are changed. No new modules.
