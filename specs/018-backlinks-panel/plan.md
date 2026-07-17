# Implementation Plan: Backlinks Panel

|**Branch**: `018-backlinks-panel` | **Date**: 2026-07-17 | **Spec**: [spec.md](spec.md)

|**Input**: Feature specification from `specs/018-backlinks-panel/spec.md`

## Summary

Show a fixed panel at the bottom of the note viewer listing all notes that link
to the currently open note (backlinks), with click-to-navigate. The LadybugDB
`LINKS_TO` graph already stores every `[[...]]` relation and is rebuilt
incrementally on save/refresh, so the feature is a new read query in `core.py`
plus a UI widget and wiring in `app.py` — no schema or storage changes.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: Textual, Rich, ladybug (all existing)
- **Storage**: Existing `.ladybug_index.lbug` — `LINKS_TO (FROM File TO File)`
  rel table (`core.py:667`), maintained by `TagIndex.rebuild_note_links`
- **Testing**: Pure core unit test for the backlink query + headless Textual
  `App.run_test()` smoke test; ad-hoc `test_*.py` script at repo root per
  project precedent
- **Target Platform**: Terminal (TUI)
- **Project Type**: Python TUI console app
- **Performance Goals**: Backlink lookup is a single indexed Cypher query;
  panel refresh must not add perceptible latency to note opening
- **Constraints**: No new dependencies; no widget calls from `core.py`;
  widgets communicate via Textual `Message`; strings via `impactite.i18n`
- **Scale/Scope**: ~30 lines in `core.py`, ~180 lines in `app.py`, ~6 i18n keys

## Constitution Check

- **I. Technology Stack**: Only existing Textual/Rich/ladybug mechanisms — **PASS**.
- **II. Architecture**: Backlink query lives in `TagIndex` (core.py); the panel
  is a widget in `app.py` emitting a `Message`; navigation reuses the existing
  app-level handler — **PASS**.
- **III. UI Styling**: Panel styles go into `DEFAULT_CSS`; must read correctly
  in both light and dark themes — **PASS** (verify manually in both themes).
- **IV. Data Management**: Read-only use of the existing derived graph index;
  no new storage, no schema change — **PASS**.
- **V. Development Practices**: New strings localized (en keys, ru/de
  translations); `python -m compileall src` + launch check before commit — **PASS**.

## Project Structure

### Documentation (this feature)

```text
specs/018-backlinks-panel/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/impactite/
├── core.py              # TagIndex.get_backlinks(path) — Cypher read query
├── app.py               # BacklinksPanel widget, MarkdownViewer layout, wiring
└── i18n.py              # ru/de translations for new strings
test_backlinks_panel.py  # Ad-hoc verification script (repo-root precedent)
```

**Structure Decision**: No new modules — the query belongs to `TagIndex`, the
panel is one more viewer-area widget next to `SearchResultsTree` & co.

## Implementation Outline

1. **Core** (`core.py`): add `TagIndex.get_backlinks(path: Path) -> List[Path]`
   built on the existing `run_read_cypher`:
   `MATCH (f:File)-[:LINKS_TO]->(t:File {path: $p}) RETURN f.path`, returning a
   sorted list with self-links excluded. Wrap in the same defensive
   `try/except` style as neighbouring read methods.
2. **Widget** (`app.py`): `BacklinksPanel(Vertical)` — a header `Label` and a
   `ListView` of backlink entries; `set_backlinks(paths, root)` renders
   vault-relative paths and toggles visibility (hidden when empty);
   `BacklinkSelected(Message)` posted on activation, following the
   `SearchResultsTree`/`TagCloud` message pattern.
3. **Layout** (`app.py`): `MarkdownViewer.compose` yields `ViewerLog` plus
   `BacklinksPanel(id="backlinks-panel")`; `DEFAULT_CSS` gives the panel a
   fixed max height (~8 lines), a top border, and `display: none` by default.
   Scrolling bindings stay on `ViewerLog`; the panel never scrolls away because
   it is a sibling of the log, not part of its content.
4. **Wiring** (`app.py`): `_update_backlinks_panel()` computes backlinks for
   the current file via `TagIndex.get_backlinks` and pushes them to the panel;
   called from the note-open path (`_navigate_to` / file-selected handlers) and
   after index rebuilds (`_rebuild_tag_cache`, which already runs on save and
   manual refresh). `on_backlinks_panel_backlink_selected` routes to the
   existing `_navigate_to`.
5. **i18n** (`i18n.py`): add ru/de entries for the panel header and related
   strings (canonical English keys).

## Complexity Tracking

No constitution violations.
