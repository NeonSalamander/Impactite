# Tasks: Backlinks Panel

|**Input**: Design documents from `specs/018-backlinks-panel/`

|**Prerequisites**: plan.md (required), spec.md (required for user stories)

## Phase 0 — Baseline

|- [x] T001 Add a failing core check for `TagIndex.get_backlinks` against the sample vault (`samples/`): pick a note known to be linked (e.g. a book linked from a review) and assert the source path is returned, sorted, without self-links.

## Phase 1 — Core query

|- [x] T002 Implement `TagIndex.get_backlinks(path: Path) -> List[Path]` in `src/impactite/core.py` using `run_read_cypher` (`MATCH (f:File)-[:LINKS_TO]->(t:File {path: $p}) RETURN f.path`), sorted, self-links excluded, defensive `try/except` like neighbouring readers.
|- [x] T003 Run the T001 check and verify it passes.

## Phase 2 — UI widget & layout

|- [x] T004 Add `BacklinksPanel(Vertical)` to `src/impactite/app.py`: header label, `ListView` of entries, `set_backlinks(paths, root)` with vault-relative rendering and hide-when-empty, `BacklinkSelected(Message)` on activation.
|- [x] T005 Update `MarkdownViewer.compose` to yield the panel below `ViewerLog`; add `DEFAULT_CSS` rules (fixed max height ~8, top border, hidden by default), legible in light and dark themes.
|- [x] T006 Wire `_update_backlinks_panel()` in the app: refresh on note open (`_navigate_to` path) and after index rebuild (`_rebuild_tag_cache`); handle `BacklinkSelected` via existing `_navigate_to`.
|- [x] T007 Add ru/de translations for new strings in `src/impactite/i18n.py`.

## Phase 3 — Validation

|- [x] T008 Write/run a headless smoke check (`test_backlinks_panel.py` at repo root): open a linked note in the sample vault, assert the panel is visible and lists the source; activate the entry and assert navigation; open an unlinked note and assert the panel is hidden.
|- [x] T009 Run `python -m compileall src`.
|- [x] T010 Launch the app to the first screen; manually verify panel behaviour in both light and dark themes, in view vs edit mode, and after editing+saving a link.
