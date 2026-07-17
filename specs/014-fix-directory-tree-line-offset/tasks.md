# Tasks: Fix Directory Tree Line Offset

|**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/014-fix-directory-tree-line-offset/`

|**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tree-alignment.md, quickstart.md

|**Tests**: Headless smoke tests only; no new unit tests required.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Inspect Current Rendering

**Purpose**: Identify the exact emoji strings and rendering path that cause the misalignment.

- [x] T001 Locate `FileTree.populate_tree` and `FileTree._add_nodes` in `src/impactite/app.py` and list every emoji prefix used for tree nodes.
- [x] T002 Verify that `FileTree.render_label` and `FileTree._render_line` in `src/impactite/app.py` do not add or remove cells beyond the label text.
- [x] T003 Check how Textual/Rich reports the cell width of each emoji prefix in `src/impactite/app.py` (investigate `rich.cells.cell_len`).

---

## Phase 2: Foundational Decision

**Purpose**: Agree on a fixed-width replacement strategy.

- [x] T004 Confirm that all replacement prefixes are fixed-width (1 cell each) in any standard terminal.
- [x] T005 Decide the mapping of node types to single-cell prefixes in `src/impactite/app.py`:
  - Directory
  - Markdown file
  - Attachment/other file
  - Link graph pseudo-node
  - Favorites pseudo-node

**Decision for T005**: Use one single-width character plus one space for every node type so labels have a uniform `icon + name` layout.

---

## Phase 3: User Story 1 - Tree lines stay aligned at every row (Priority: P1) 🎯 MVP

**Goal**: Every visible row in the directory tree aligns horizontally; the fourth row (or any row) is not shifted by one character.

**Independent Test**: Start the app, open the directory tree, and visually confirm that all rows align.

### Implementation for User Story 1

- [x] T006 [US1] Replace the directory emoji prefix in `src/impactite/app.py` (`FileTree._add_nodes`) with a fixed-width prefix.
- [x] T007 [US1] Replace the Markdown-file emoji prefix in `src/impactite/app.py` with a fixed-width prefix.
- [x] T008 [US1] Replace the attachment emoji prefix in `src/impactite/app.py` with a fixed-width prefix.
- [x] T009 [US1] Replace the link-graph emoji prefix in `src/impactite/app.py` (`FileTree.populate_tree`) with a fixed-width prefix.
- [x] T010 [US1] Replace the favorites emoji prefix in `src/impactite/app.py` with a fixed-width prefix.
- [x] T011 [US1] Document the chosen icons in `specs/014-fix-directory-tree-line-offset/research.md` if any glyph changes during implementation.

**Checkpoint**: User Story 1 should be independently verifiable — all tree rows are aligned.

---

## Phase 4: User Story 2 - Rendering remains aligned when tree state changes (Priority: P2)

**Goal**: Alignment is preserved after expanding, collapsing, selecting, or styling rows.

**Independent Test**: Toggle expand/collapse, apply/reset directory colours, and confirm no row shifts.

### Implementation for User Story 2

- [x] T012 [US2] Verify in `src/impactite/app.py` that `render_label` only changes colour styling and does not inject any additional cells.
- [x] T013 [US2] Verify in `src/impactite/app.py` that `_render_line` only changes the background style and returns the same line length.
- [x] T014 [US2] Manually expand/collapse directories; visually confirm alignment holds.
- [x] T015 [US2] Apply a custom directory colour; visually confirm the coloured row aligns with its neighbours.

**Checkpoint**: User Stories 1 AND 2 should both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validation and cleanup.

- [x] T016 [P] Run `python -m compileall src` and fix any syntax errors in `src/impactite/app.py`.
- [x] T017 [P] Run the headless smoke test for `MarkdownEditorApp` to confirm the tree still populates without exceptions.
- [x] T018 Update `specs/014-fix-directory-tree-line-offset/quickstart.md` if the manual validation steps need to change.
- [x] T019 Check `git status --short` and ensure only intended changes in `src/impactite/app.py` and documentation are present.

---

## Dependencies & Execution Order

- **Phase 1** (inspect) → **Phase 2** (decision) → **Phase 3** (US1) → **Phase 4** (US2) → **Phase 5** (polish).
- Phase 3 and Phase 4 are sequential in the same file.

## Parallel Opportunities

- Phase 1 inspection tasks can run in parallel.
- Phase 5 validation tasks can run in parallel.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3: replace all emoji prefixes with fixed-width glyphs.
3. Stop and visually validate.

### Incremental Delivery

1. Phase 3 → all tree rows align.
2. Phase 4 → state changes do not break alignment.
3. Phase 5 → compile, smoke tests, docs.
