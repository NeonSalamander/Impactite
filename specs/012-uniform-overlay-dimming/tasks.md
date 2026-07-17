# Tasks: Uniform 25% Overlay Dimming

|**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/012-uniform-overlay-dimming/`

|**Prerequisites**: plan.md, spec.md, research.md, contracts/backdrop-dimming.md, quickstart.md

|**Tests**: Smoke tests via `App.run_test()` plus `python -m compileall src`. No new unit tests required.

**Organization**: Tasks are grouped by user story. CSS changes affect a single file, so parallel tasks are modelled by conceptually independent edits that touch different CSS selectors.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different selectors/sections, no logical dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Inspect current overlay CSS)

**Purpose**: Check existing modal and context-menu CSS before changing it.

- [x] T001 In `src/impactite/app.py`, document all current modal CSS selectors and their `background` declarations in a checklist or annotation.
- [x] T002 In `src/impactite/app.py`, locate the `DirectoryContextMenu` CSS block and record its current full-screen `background` value.

---

## Phase 2: Foundational (Decide and verify a theme-independent dimming rule)

**Purpose**: Choose a single CSS rule that produces uniform 25% dimming regardless of theme.

**⚠️ CRITICAL**: No user story work relying on the shared rule can begin until this phase is complete.

- [x] T003 Confirm that Textual accepts a fixed translucent color rule such as `background: black 25%;` for a `ModalScreen` in `src/impactite/app.py` without runtime errors.
- [x] T004 Verify that the chosen rule renders correctly in headless `App.run_test()` (no crash) using a temporary test script.
- [x] T005 Update the project plan/research notes if the initial percentage needs adjustment based on the manual/quickstart checks.

**Checkpoint**: Foundation ready — a single shared dimming rule is known to compile and render.

---

## Phase 3: User Story 1 - Dialogs dim by 25% (Priority: P1) 🎯 MVP

**Goal**: Every modal dialog dims the workspace behind it instead of leaving it at full brightness.

**Independent Test**: Open any dialog (for example the directory-color dialog) and confirm the background looks darker.

### Tests for User Story 1

- [x] T006 [US1] Smoke test: create a temporary config and run `MarkdownEditorApp` via `App.run_test()` then push a `ModalScreen` subclass and confirm no exception occurs.
- [x] T007 [US1] Inspect the current virtual render output to verify the dialog backdrop is not fully transparent.

### Implementation for User Story 1

- [x] T008 [US1] Add a global `ModalScreen { background: black 25%; }` rule near the top of `MarkdownEditorApp.DEFAULT_CSS` in `src/impactite/app.py`.
- [x] T009 [P] [US1] Remove any per-modal `background` declarations that override the global rule from `InNoteSearch`, `UnsavedChangesModal`, `TagSearchModal`, and `TextPromptModal` blocks in `src/impactite/app.py`.
- [x] T010 [US1] Ensure modal inner containers (`#prompt-container`, `#tag-search-*`, `#unsaved-dialog`, etc.) keep opaque `background: $surface;` so dialogs remain readable.

**Checkpoint**: User Story 1 should be independently verifiable — dialogs dim the workspace.

---

## Phase 4: User Story 2 - Context menus dim by 25% (Priority: P1)

**Goal**: The directory context menu dims the area outside the menu box without hiding the underlying tree.

**Independent Test**: Right-click a directory and verify the tree behind the menu is still visible and darker.

### Tests for User Story 2

- [x] T011 [US2] Smoke test: run `MarkdownEditorApp` via `App.run_test()`, right-click a directory, and confirm `DirectoryContextMenu` opens without an exception.

### Implementation for User Story 2

- [x] T012 [US2] Change `DirectoryContextMenu` background in `src/impactite/app.py` from `transparent` (or theme-colored) to the same fixed translucent color used for `ModalScreen` (`black 25%`).
- [x] T013 [US2] Confirm that `#directory-context-menu-box` retains its opaque `background: $surface;` border in `src/impactite/app.py` so menu items remain readable.
- [x] T014 [US2] Verify that clicking outside `#directory-context-menu-box` still dismisses the menu in `src/impactite/app.py`.

**Checkpoint**: User Story 2 should be independently verifiable — context menu does not hide the tree.

---

## Phase 5: User Story 3 - Consistent dimming across themes (Priority: P2)

**Goal**: The same 25% dimming is visible in dark and light themes.

**Independent Test**: Toggle the theme while a dialog is open and compare perceived dimming strength.

### Tests for User Story 3

- [x] T015 [US3] Manual/quickstart check: open a dialog in dark theme, switch to light theme, and verify the background is still visibly dimmed (not full brightness).

### Implementation for User Story 3

- [x] T016 [US3] If `black 25%` is too weak in one theme or too strong in another, tune the global overlay value in `src/impactite/app.py` until both dark and light themes look similar.
- [x] T017 [US3] Ensure the `ModalScreen` and `DirectoryContextMenu` rules reference the same value or CSS variable to keep them synchronized.

**Checkpoint**: All user stories should be independently functional and visually consistent.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup.

- [x] T018 [P] Run `python -m compileall src` and fix any syntax errors in `src/impactite/app.py`.
- [x] T019 [P] Run headless smoke tests for all modal dialogs and the context menu from `quickstart.md`.
- [x] T020 Update `specs/012-uniform-overlay-dimming/quickstart.md` if any manual check steps changed during implementation.
- [x] T021 Inspect `git status --short` and ensure only the intended CSS changes appear.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; blocks user stories
- **User Stories (Phase 3–5)**: Depend on Foundational; can be built sequentially in priority order
- **Polish (Final Phase)**: Depends on all user stories

### User Story Dependencies

- **User Story 1**: Can start after Foundational
- **User Story 2**: Can start after Foundational; shares overlay color choice with US1
- **User Story 3**: Can start after US1 and US2 are functionally working

### Parallel Opportunities

- T001/T002 can run in parallel.
- T006/T011 can run in parallel once T005 is done.
- T009 covers multiple selectors; each removal can be done in parallel, but they all edit the same file.
- T018/T019/T020/T021 can run in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3: add global `ModalScreen { background: black 25%; }` and remove per-modal overrides.
3. Stop and visually validate: dialogs are dimmed.

### Incremental Delivery

1. Phase 3 → dialogs dimmed.
2. Phase 4 → context menu dimmed.
3. Phase 5 → consistent in both themes.
4. Phase 6 → compile, smoke tests, quickstart validation.

### Parallel Team Strategy

With multiple developers:

- Developer A: Phase 3 (dialogs) + compileall.
- Developer B: Phase 4 (context menu) + smoke test.
- Developer C: Phase 5 (theme consistency) + quickstart.

---

## Notes

- All CSS changes are localized to `src/impactite/app.py`.
- No new user-facing strings, core logic, or persistent state are introduced.
- The percentage may need one visual iteration in Phase 5; keep it in one global rule for easy tuning.
