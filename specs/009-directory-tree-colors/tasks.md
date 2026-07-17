# Tasks: Directory Tree Colors

|**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/009-directory-tree-colors/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not explicitly requested. Validation tasks use headless `App.run_test()` and manual checks from `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project layout: `src/impactite/app.py`, `src/impactite/core.py`, `src/impactite/i18n.py`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Understand the current tree, config, and i18n mechanisms before making changes.

- [x] T001 [P] Review `FileTree` node population and `dir_nodes`/`file_nodes` handling in `src/impactite/app.py`
- [x] T002 [P] Review `Tree.render_label` signature and how `FileNode.path` maps to tree nodes in `src/impactite/app.py`
- [x] T003 [P] Review `Config.load`, default config merging, and YAML save helpers in `src/impactite/core.py`
- [x] T004 [P] Review i18n key conventions and identify new keys for the color modal in `src/impactite/i18n.py`
- [x] T005 [P] Verify `Color.parse` and `Style(bgcolor=..., color=...)` behavior in the installed Textual/Rich version

**Checkpoint**: Current code paths are understood; no ambiguous dependencies remain.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the data model and config persistence before any user story can be functional.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T006 Add `DirectoryStyle` dataclass in `src/impactite/core.py`
- [x] T007 Load `directory_colors` with default `{}` in `Config.load` and store it on `Config` in `src/impactite/core.py`
- [x] T008 Implement `Config.get_directory_style(rel_path)` in `src/impactite/core.py`
- [x] T009 Implement `Config.set_directory_style(rel_path, background, text)` with validation in `src/impactite/core.py`
- [x] T010 Implement `Config.remove_directory_style(rel_path)` in `src/impactite/core.py`
- [x] T011 Implement `Config.save_directory_colors()` to rewrite the `directory_colors` section in `config.yaml` in `src/impactite/core.py`
- [x] T012 Add unit-style validation helper for color strings using `Color.parse` in `src/impactite/core.py`

**Checkpoint**: Foundation ready — directory color preferences can be loaded, set, removed, and persisted.

---

## Phase 3: User Story 1 - Assign Colors to a Directory (Priority: P1) 🎯 MVP

**Goal**: Users can set a custom background and text color for any directory in the tree and see the change immediately.

**Independent Test**: Open the color modal for a directory, submit two colors, and verify the `FileTree` label reflects them.

### Implementation for User Story 1

- [x] T013 [US1] Extend `FileTree.populate_tree` to accept `directory_styles: Dict[str, DirectoryStyle]` in `src/impactite/app.py`
- [x] T014 [US1] Compute relative directory paths when adding directory nodes in `FileTree._add_nodes` in `src/impactite/app.py`
- [x] T015 [US1] Override `FileTree.render_label` to apply stored background and text colors in `src/impactite/app.py`
- [x] T016 [US1] Create `DirectoryColorModal` class with background and text inputs in `src/impactite/app.py`
- [x] T017 [US1] Add color validation inside `DirectoryColorModal` using `Color.parse` in `src/impactite/app.py`
- [x] T018 [US1] Add `action_set_directory_color` to `MarkdownEditorApp` in `src/impactite/app.py`
- [x] T019 [US1] Wire `DirectoryColorModal` result to `Config.set_directory_style` and `_refresh_file_tree` in `src/impactite/app.py`
- [x] T020 [US1] Headless test: open `DirectoryColorModal`, submit colors, and assert the directory node label carries the new style

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Visually Differentiate Multiple Directories (Priority: P2)

**Goal**: Different directories can have different colors, and default directories remain unchanged.

**Independent Test**: Color two directories differently; confirm each is distinct and neighboring nodes use default styling.

### Implementation for User Story 2

- [x] T021 [US2] Verify multiple directory nodes each render with their own `DirectoryStyle` in `src/impactite/app.py`
- [x] T022 [US2] Verify directories without a stored `DirectoryStyle` render with the default theme styling in `src/impactite/app.py`
- [x] T023 [US2] Ensure file nodes and special nodes (favorites, link graph) are never affected by directory color logic in `src/impactite/app.py`
- [x] T024 [US2] Manual check: color two sibling directories differently and confirm visual distinction

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Persist Colors Across Sessions (Priority: P3)

**Goal**: Directory colors survive app restart and can be reset to default.

**Independent Test**: Set colors, restart the app, verify colors are restored; reset colors and verify they disappear.

### Implementation for User Story 3

- [x] T025 [US3] Pass loaded directory styles from `Config` to `FileTree.populate_tree` during tree refresh in `src/impactite/app.py`
- [x] T026 [US3] Add `action_reset_directory_color` to `MarkdownEditorApp` in `src/impactite/app.py`
- [x] T027 [US3] Wire reset action to `Config.remove_directory_style` and `_refresh_file_tree` in `src/impactite/app.py`
- [x] T028 [US3] Headless/manual test: set directory colors, inspect `config.yaml`, restart app, and verify colors are reapplied in `src/impactite/app.py`
- [x] T029 [US3] Headless/manual test: reset directory colors and verify the config entry is removed in `src/impactite/app.py`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate completeness, prevent regressions, and localize new strings.

- [x] T030 [P] Add English/Russian/German translations for new color-modal keys in `src/impactite/i18n.py`
- [x] T031 [P] Run `python -m compileall src`
- [x] T032 [P] Run the manual validation scenarios from `quickstart.md`
- [x] T033 [P] Regression check: existing file tree navigation, theme toggling, and note creation still work in `src/impactite/app.py`
- [x] T034 [P] Verify invalid color values are rejected by the modal without writing to `config.yaml`

---

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Builds on US1 but should be independently testable.
- **User Story 3 (P3)**: Can start after US1 (requires color render path) — Independently testable once the render path exists.

### Within Each User Story

- Core `FileTree` rendering path is required before modal/user actions.
- Save/persist helpers from Foundational must exist before UI actions call them.
- Story complete before moving to next priority.

### Parallel Opportunities

- T001, T002, T003, T004, T005 can run in parallel.
- T006, T007, T008, T009, T010, T011, T012 can run in parallel (different methods in `src/impactite/core.py`).
- T016, T017, T018, T019 can run in parallel with T020 if interfaces are agreed.
- T030, T031, T032, T033, T034 can run in parallel.

### Parallel Example: Foundational Phase

```text
Task: "Add DirectoryStyle dataclass in src/impactite/core.py"
Task: "Load directory_colors default in Config.load in src/impactite/core.py"
Task: "Implement Config.get_directory_style in src/impactite/core.py"
Task: "Implement Config.set_directory_style with validation in src/impactite/core.py"
Task: "Implement Config.remove_directory_style in src/impactite/core.py"
Task: "Implement Config.save_directory_colors in src/impactite/core.py"
Task: "Add color string validation using Color.parse in src/impactite/core.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational — `DirectoryStyle`, load/save/persist in `Config`.
3. Complete Phase 3: User Story 1 — render path and modal to set a directory's colors.
4. **STOP and VALIDATE**: Test User Story 1 independently.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready.
2. Add User Story 1 → Test independently (MVP!).
3. Add User Story 2 → Test multiple directories and default styling.
4. Add User Story 3 → Test persistence and reset.
5. Run Phase 6 polish/regression checks.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together.
2. Once Foundational is done:
   - Developer A: User Story 1 (render path + modal)
   - Developer B: User Story 2 (multiple directory verification, default styling)
   - Developer C: User Story 3 (persistence wiring + reset)
3. Stories integrate through the shared `Config.directory_colors` contract.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Each user story should be independently completable and testable.
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently.
- Avoid: vague tasks, same-file conflicts during parallel work, and cross-story dependencies that break independence.
