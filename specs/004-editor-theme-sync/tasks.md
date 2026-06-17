# Tasks: Editor Theme Sync

**Input**: Design documents from `/specs/004-editor-theme-sync/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/editor-theme.md, quickstart.md

**Tests**: Not requested for this feature; validation is via manual quickstart scenarios and syntax checks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/impactite/` at repository root
- Tests: manual validation via `uv run impactite` and `python -m compileall src`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Understand existing editor theme handling and project conventions

- [x] T001 Inspect current editor theme handling in `src/impactite/app.py` (`_apply_editor_syntax_theme`, `_load_file`, `action_toggle_theme`)
- [x] T002 Review editor-theme contract in `specs/004-editor-theme-sync/contracts/editor-theme.md`

---

## Phase 2: User Story 1 - Light Mode Editor Uses Light Syntax Theme (Priority: P1) 🎯 MVP

**Goal**: When the application is switched to a light theme via `Ctrl+L`, opening a note for editing displays the editor with a light syntax theme.

**Independent Test**: Toggle to a light theme, open a note in edit mode, and verify the editor uses a light syntax theme.

### Implementation for User Story 1

- [x] T003 [US1] Apply `_apply_editor_syntax_theme(editor)` when entering edit mode in `_load_file` in `src/impactite/app.py`
- [x] T004 [US1] Confirm `_apply_editor_syntax_theme` selects `github_light` for light application themes in `src/impactite/app.py`

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 3: User Story 2 - Dark Mode Editor Returns to Dark Syntax Theme (Priority: P2)

**Goal**: When the user toggles back to a dark application theme while editing, the editor switches back to the configured dark syntax theme.

**Independent Test**: Open a note in edit mode in light theme, press `Ctrl+L` to toggle to dark mode, and verify the editor uses the configured dark syntax theme.

### Implementation for User Story 2

- [x] T005 [US2] Update `action_toggle_theme` to refresh the editor syntax theme whenever the editor container is visible in `src/impactite/app.py` (depends on T003)

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 4: User Story 3 - Theme Persists When Switching Between View and Edit Modes (Priority: P3)

**Goal**: Switching a note between view and edit modes does not desynchronize the editor theme.

**Independent Test**: In light mode, switch a note between view and edit modes multiple times and confirm the editor remains in the light theme.

### Implementation for User Story 3

- [x] T006 [US3] Verify `_load_file` applies editor theme on every transition into edit mode in `src/impactite/app.py` (depends on T003)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T007 [P] Run syntax validation with `uv run python -m compileall src` — passed
- [x] T008 [P] Run quickstart validation per `specs/004-editor-theme-sync/quickstart.md` — automated Textual pilot test passed (rose-pine-dawn → rose-pine-moon → rose-pine-dawn; view/edit switch preserved light theme)
- [x] T009 Final review of `src/impactite/app.py` for code style and constitution compliance — no new deps, UI logic stays in `app.py`, consistent with project conventions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **User Story 1 (Phase 2)**: Can start after Setup completion
- **User Story 2 (Phase 3)**: Depends on User Story 1 implementation
  - T005 depends on T003
- **User Story 3 (Phase 4)**: Depends on User Story 1 implementation
  - T006 depends on T003
- **Polish (Phase 5)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP; no dependencies on other stories
- **User Story 2 (P2)**: Builds on edit-mode theme application from US1
- **User Story 3 (P3)**: Verified by the same edit-mode theme application from US1

### Parallel Opportunities

- T001 and T002 (Setup) can run in parallel
- T007 and T008 (Polish) can run in parallel

### Sequential Requirements

- T003 must complete before T005 and T006

---

## Parallel Example: User Story 1 + Setup

```bash
# Setup tasks can run in parallel:
Task: "Inspect current editor theme handling in src/impactite/app.py"
Task: "Review editor-theme contract in specs/004-editor-theme-sync/contracts/editor-theme.md"

# Once setup is complete, implement US1:
Task: "Apply _apply_editor_syntax_theme(editor) when entering edit mode in _load_file in src/impactite/app.py"
Task: "Confirm _apply_editor_syntax_theme selects github_light for light application themes in src/impactite/app.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: User Story 1
3. **STOP and VALIDATE**: Toggle to light theme and open a note for editing; confirm light editor theme
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup
2. Add User Story 1 → test independently
3. Add User Story 2 → test theme toggle while editing
4. Add User Story 3 → test view/edit switching
5. Each story adds value without breaking previous stories

---

## Validation Log

- `uv run python -m compileall src` — passed
- Automated headless Textual pilot test:
  - Started in `rose-pine-dawn` light theme
  - Opened note, entered edit mode → editor theme `github_light`
  - Pressed `Ctrl+L` → app theme `rose-pine-moon`, editor theme `monokai`
  - Pressed `Ctrl+L` again → app theme `rose-pine-dawn`, editor theme `github_light`
  - Switched view → edit → editor theme remained `github_light`

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify `python -m compileall src` passes after each substantial change
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
- Avoid vague tasks; every task references an exact file path
