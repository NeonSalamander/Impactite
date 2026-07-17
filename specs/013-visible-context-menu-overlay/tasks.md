# Tasks: Visible Context-Menu Overlay

|**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/013-visible-context-menu-overlay/`

|**Prerequisites**: plan.md, spec.md, research.md, contracts/visible-overlay.md, quickstart.md

|**Tests**: Headless smoke tests (`App.run_test()`) and `python -m compileall src`. No new unit tests required.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Inspect Current Code

**Purpose**: Locate the CSS and rendering code responsible for the solid overlay.

- [x] T001 Locate `DirectoryContextMenu` CSS and Python class in `src/impactite/app.py`.
- [x] T002 Locate the shared `ModalScreen` overlay rule in `src/impactite/app.py`.
- [x] T003 Verify that `screen.png` histogram shows a near-solid dark overlay covering the workspace.

---

## Phase 2: Foundational Decision

**Purpose**: Decide how to keep the workspace visible.

- [x] T004 Confirm that removing/transparentizing the full-screen background in `src/impactite/app.py` still allows the container to capture click events for dismissal.
- [x] T005 Decide whether `DirectoryContextMenu` should be sized to its content or keep full-screen with transparent background.

**Decision for T005**: Size to content and remove the dark full-screen overlay.

---

## Phase 3: User Story 1 - Make context-menu workspace visible (Priority: P1) 🎯 MVP

**Goal**: Opening the directory context menu no longer hides the workspace behind it.

**Independent Test**: Right-click a directory; the tree and other panes behind the menu box remain visible.

### Tests for User Story 1

- [x] T006 [US1] Run headless smoke test: `MarkdownEditorApp` starts and a context menu can be opened without exception.

### Implementation for User Story 1

- [x] T007 [US1] In `src/impactite/app.py`, change `DirectoryContextMenu` CSS: set `background: transparent;` (or remove `width: 100%; height: 100%;`) so it does not paint a full-screen dark overlay.
- [x] T008 [US1] Ensure `#directory-context-menu-box` keeps its opaque background (`background: $surface;`) and border in `src/impactite/app.py`.
- [x] T009 [US1] Verify the menu still dismisses on click outside the box by inspecting existing `_on_click` handler in `src/impactite/app.py`.

**Checkpoint**: User Story 1 should be independently verifiable — context menu does not hide the workspace.

---

## Phase 4: User Story 2 - Keep dialogs visually consistent (Priority: P2)

**Goal**: Dialogs dim the workspace but never hide it completely.

**Independent Test**: Open any modal dialog; the background is still distinguishable.

### Tests for User Story 2

- [x] T010 [US2] Run headless smoke test: push a sample `ModalScreen` from `MarkdownEditorApp` and ensure no exception.

### Implementation for User Story 2

- [x] T011 [US2] If a shared `ModalScreen` overlay rule exists in `src/impactite/app.py`, tune it so it dims without hiding content (e.g., keep a low-opacity translucent color, not a solid theme color).
- [x] T012 [US2] Ensure modal inner containers retain opaque `background: $surface;` in `src/impactite/app.py` so dialog content remains readable.

**Checkpoint**: User Story 2 should be independently verifiable — dialogs dim but do not obscure.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validate and clean up.

- [x] T013 [P] Run `python -m compileall src` and fix any syntax errors in `src/impactite/app.py`.
- [x] T014 [P] Run headless smoke tests for both context menu and modal dialogs.
- [x] T015 Update `specs/013-visible-context-menu-overlay/quickstart.md` if manual steps changed during implementation.
- [x] T016 Check `git status --short` and ensure only intended CSS changes in `src/impactite/app.py` are present.

---

## Dependencies & Execution Order

- **Phase 1** (inspect) → **Phase 2** (decision) → **Phase 3** (US1) → **Phase 4** (US2) → **Phase 5** (polish).
- Phase 3 and Phase 4 can be done sequentially in the same file; US2 is only a CSS value adjustment.

## Parallel Opportunities

- Phase 1 tasks can run in parallel.
- Phase 5 validation tasks can run in parallel.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3: make `DirectoryContextMenu` transparent and ensure the menu box itself is opaque.
3. Stop and visually validate.

### Incremental Delivery

1. Phase 3 → context menu no longer hides workspace.
2. Phase 4 → dialogs dim subtly.
3. Phase 5 → compile, smoke tests, docs.
