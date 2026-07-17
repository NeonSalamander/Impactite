# Tasks: Directory Context Menu

|**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/010-directory-context-menu/`

|**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

|**Tests**: Not explicitly requested. Validation tasks use headless `App.run_test()` and manual checks from `quickstart.md`.

|**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project layout: `src/impactite/app.py`, `src/impactite/core.py`, `src/impactite/i18n.py`.

## Phase 1: Setup (Shared Infrastructure)

|**Purpose**: Understand the existing tree widget, color modal, and i18n mechanisms before adding the context menu.

- [x] T001 [P] Review `FileTree` node population and how directory nodes carry `node.data = Path` in `src/impactite/app.py`
- [x] T002 [P] Review `DirectoryColorModal` composition, validation, and dismissal flow in `src/impactite/app.py`
- [x] T003 [P] Review `Config.get_directory_style`, `set_directory_style`, and `remove_directory_style` in `src/impactite/core.py`
- [x] T004 [P] Review i18n key conventions and identify new keys for the context menu in `src/impactite/i18n.py`
- [x] T005 [P] Verify `Tree.hover_line` and `Tree.get_node_at_line()` behavior for mouse-aware node lookup in Textual 8.2.4

|**Checkpoint**: Current code paths are understood; implementation dependencies are clear.

|---

## Phase 2: Foundational (Blocking Prerequisites)

|**Purpose**: Add the right-click detection and context-menu widget before any user story can be functional.

|**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Implement `_on_mouse_down` handler in `FileTree` to detect `event.button == 3` in `src/impactite/app.py`
- [x] T007 Implement directory eligibility check in `FileTree` using `node.data` as a `Path` pointing to a directory in `src/impactite/app.py`
- [x] T008 Move the tree cursor/selection to the right-clicked directory before opening the menu in `src/impactite/app.py`
- [x] T009 Create `DirectoryContextMenu` widget class with "Directory settings" and "Reset color" action buttons in `src/impactite/app.py`
- [x] T010 Add pointer positioning for `DirectoryContextMenu` using `styles.offset` in `src/impactite/app.py`
- [x] T011 Implement dismiss behavior for `DirectoryContextMenu` on `Escape` and outside-click in `src/impactite/app.py`
- [x] T012 [P] Add CSS for the context menu overlay and menu box in `src/impactite/app.py` DEFAULT_CSS

|**Checkpoint**: Foundation ready — right-clicks on directories can open and dismiss a context menu.

|---

## Phase 3: User Story 1 - Open Directory Settings from the Context Menu (Priority: P1) 🎯 MVP

|**Goal**: Users can right-click a directory to open a context menu near the pointer.

|**Independent Test**: Simulate a right-click on a directory node and verify the context menu appears with the expected options.

### Implementation for User Story 1

- [x] T013 [US1] Wire `FileTree._on_mouse_down` to mount `DirectoryContextMenu` for directory nodes in `src/impactite/app.py`
- [x] T014 [US1] Ensure right-clicking files, root, or empty tree areas does not open a context menu in `src/impactite/app.py`
- [x] T015 [US1] Add i18n keys for "Directory settings" and "Reset color" and include them in `src/impactite/i18n.py`
- [x] T016 [US1] Headless test: simulate a right-click `MouseDown` event on a directory node and assert that `DirectoryContextMenu` is mounted
- [x] T017 [US1] Headless test: simulate a right-click on a file node and assert that no `DirectoryContextMenu` is mounted

|**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

|---

## Phase 4: User Story 2 - Set and Persist Directory Colors from the Settings Dialog (Priority: P2)

|**Goal**: The "Directory settings" menu option opens the color dialog and persists the chosen colors.

|**Independent Test**: Open the context menu, choose "Directory settings", submit colors, and verify the directory row and `config.yaml` reflect the change.

### Implementation for User Story 2

- [x] T018 [US2] Implement "Directory settings" button handler to dismiss the menu and push `DirectoryColorModal` in `src/impactite/app.py`
- [x] T019 [US2] Pre-fill `DirectoryColorModal` with existing colors for the right-clicked directory in `src/impactite/app.py`
- [x] T020 [US2] Handle `DirectoryColorModal` confirmation: call `Config.set_directory_style(...)` and refresh the file tree in `src/impactite/app.py`
- [x] T021 [US2] Headless test: open context menu for a directory, choose settings, submit colors, and assert the directory row style changes and `config.yaml` is updated

|**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

|---

## Phase 5: User Story 3 - Reset Directory Colors from the Context Menu (Priority: P3)

|**Goal**: Users can remove custom colors from a directory via the context menu.

|**Independent Test**: Open the context menu for a customized directory, choose "Reset color", and verify the directory reverts to default styling and config is cleaned.

### Implementation for User Story 3

- [x] T022 [US3] Implement "Reset color" button handler to remove stored colors and refresh the file tree in `src/impactite/app.py`
- [x] T023 [US3] Make "Reset color" a safe no-op when no colors are stored for the directory in `src/impactite/app.py`
- [x] T024 [US3] Headless test: set directory colors, open the context menu, choose reset, and assert the directory uses default styling and the config entry is removed

|**Checkpoint**: All user stories should now be independently functional.

|---

## Phase 6: Polish & Cross-Cutting Concerns

|**Purpose**: Validate completeness, prevent regressions, and ensure localization.

- [x] T025 [P] Add English/Russian/German translations for context menu and related status messages in `src/impactite/i18n.py`
- [x] T026 [P] Run `python -m compileall src`
- [x] T027 [P] Run the manual validation scenarios from `quickstart.md`
- [x] T028 [P] Regression check: existing file tree navigation, theme toggling, note creation, and color-modal flows still work in `src/impactite/app.py`
- [x] T029 [P] Verify the context menu closes on `Escape`, outside click, and after selecting an action

|---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User stories can then proceed in parallel (if staffed).
  - Or sequentially in priority order (P1 → P2 → P3).
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories.
- **User Story 2 (P2)**: Can start after US1 (requires the menu to exist) and after existing color-persistence helpers are available.
- **User Story 3 (P3)**: Can start after US2 (uses the same menu and color-persistence helpers).

### Within Each User Story

- Right-click detection and menu rendering is required before menu actions can be wired.
- Save/persist helpers from `core.py` must exist before UI actions call them.
- Story complete before moving to the next priority.

### Parallel Opportunities

- T001, T002, T003, T004, T005 can run in parallel.
- T006, T007, T008, T009, T010, T011, T012 can run in parallel (different parts of `src/impactite/app.py`).
- T025, T026, T027, T028, T029 can run in parallel.

### Parallel Example: Foundational Phase

```text
Task: "Implement _on_mouse_down handler in FileTree to detect right-clicks in src/impactite/app.py"
Task: "Implement directory eligibility check in src/impactite/app.py"
Task: "Move the tree cursor/selection to the right-clicked directory in src/impactite/app.py"
Task: "Create DirectoryContextMenu widget class in src/impactite/app.py"
Task: "Add pointer positioning for DirectoryContextMenu in src/impactite/app.py"
Task: "Implement dismiss behavior for DirectoryContextMenu in src/impactite/app.py"
Task: "Add CSS for the context menu overlay in src/impactite/app.py"
```

|---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational — right-click detection and a dismissible context menu.
3. Complete Phase 3: User Story 1 — right-click on directories opens the menu; right-click elsewhere does nothing.
4. **STOP and VALIDATE**: Test User Story 1 independently.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready.
2. Add User Story 1 → Menu opens for directories only (MVP!).
3. Add User Story 2 → "Directory settings" opens the color dialog and persists colors.
4. Add User Story 3 → "Reset color" removes stored colors.
5. Run Phase 6 polish/regression checks.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together.
2. Once Foundational is done:
   - Developer A: User Story 1 (right-click detection + menu rendering)
   - Developer B: User Story 2 (settings option + color modal wiring)
   - Developer C: User Story 3 (reset option + config cleanup)
3. Stories integrate through the shared `FileTree` context-menu state and existing `Config.directory_colors` contract.

|---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Each user story should be independently completable and testable.
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently.
- Avoid: vague tasks, same-file conflicts during parallel work, and cross-story dependencies that break independence.
