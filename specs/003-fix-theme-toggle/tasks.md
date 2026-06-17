# Tasks: Fix Theme Toggle

**Input**: Design documents from `/specs/003-fix-theme-toggle/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/theme-toggle.md, quickstart.md

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

**Purpose**: Understand existing theme handling and project conventions

- [x] T001 Inspect current theme handling in `src/impactite/app.py` (`watch_theme`, `action_toggle_theme`, `_LIGHT_THEMES`)
- [x] T002 Inspect current config persistence in `src/impactite/core.py` (`Config.save_theme`, `Config.display` defaults)
- [x] T003 Review theme-toggle contract in `specs/003-fix-theme-toggle/contracts/theme-toggle.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core helpers that MUST be complete before any user story can be implemented

⚠️ **CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Add pure theme variant resolver `resolve_theme_variant` to `src/impactite/core.py`
- [x] T005 [P] Add Config user-theme accessors (`get_user_theme`, `save_user_theme`) to `src/impactite/core.py`

**Checkpoint**: Foundation ready — `core.py` exposes a testable resolver and user-preference accessors

---

## Phase 3: User Story 1 - Preserve Selected Theme After Light/Dark Toggle (Priority: P1) 🎯 MVP

**Goal**: Pressing `Ctrl+L` switches between light and dark variants of the user's selected theme without overwriting the saved user preference.

**Independent Test**: Select a non-default theme, press `Ctrl+L` twice, and verify the UI returns to the originally selected theme. Check that `config.yaml` still contains the original theme after toggling.

### Implementation for User Story 1

- [x] T006 [US1] Add `_suppress_theme_persist` guard attribute to application state in `src/impactite/app.py`
- [x] T007 [US1] Rewrite `action_toggle_theme` to use the user theme and resolver in `src/impactite/app.py` (depends on T004, T005, T006)
- [x] T008 [US1] Update `watch_theme` to skip persistence when `_suppress_theme_persist` is set in `src/impactite/app.py` (depends on T006)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Persist Theme Choice Across Sessions (Priority: P2)

**Goal**: The user's theme choice survives an application restart.

**Independent Test**: Select a non-default theme, close the application, reopen it, and verify the previously selected theme is active.

### Implementation for User Story 2

- [x] T009 [P] [US2] Ensure startup theme is loaded from the user's preference in `src/impactite/app.py` (depends on T005)
- [x] T010 [P] [US2] Verify `Config.save_user_theme` writes `app_theme` to `config.yaml` correctly in `src/impactite/core.py` (depends on T005)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Handle Missing or Corrupted Configuration Gracefully (Priority: P3)

**Goal**: Invalid or missing theme configuration falls back to the default theme without errors.

**Independent Test**: Set `app_theme` to a non-existent value in `config.yaml`, restart the application, and verify it launches with the default `textual-dark` theme.

### Implementation for User Story 3

- [x] T011 [P] [US3] Add fallback logic for invalid theme names in `resolve_theme_variant` in `src/impactite/core.py` (depends on T004)
- [x] T012 [P] [US3] Validate startup theme and fall back to `textual-dark` when invalid in `src/impactite/app.py` (depends on T011)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and cross-cutting updates

- [x] T013 [P] Run syntax validation with `uv run python -m compileall src`
- [x] T014 [P] Run quickstart validation per `specs/003-fix-theme-toggle/quickstart.md`
- [x] T015 Update i18n keys in `src/impactite/i18n.py` if any new user-facing message is introduced (no new strings added)
- [x] T016 Final review of `src/impactite/app.py` and `src/impactite/core.py` for code style and constitution compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
  - T004 and T005 can run in parallel
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
  - T006 blocks T007 and T008
  - T007 blocks the end-to-end test of US1
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — No dependencies on US1 implementation
  - T009 and T010 can run in parallel
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — No dependencies on US1/US2 implementation
  - T011 and T012 can run in parallel

### Within Each User Story

- Core helpers before UI wiring
- UI state guard before action/watch updates
- Implementation before manual validation

### Parallel Opportunities

- T004 and T005 (Foundational) can run in parallel
- T009 and T010 (US2) can run in parallel
- T011 and T012 (US3) can run in parallel
- T013, T014, and T015 (Polish) can run in parallel after stories are complete
- Different user stories can be worked on in parallel by different team members once Foundational phase is done

---

## Parallel Example: User Story 1 + Foundational

```bash
# Foundational helpers can be added in parallel:
Task: "Add pure theme variant resolver resolve_theme_variant to src/impactite/core.py"
Task: "Add Config user-theme accessors to src/impactite/core.py"

# Once foundational is ready, US1 wiring can proceed:
Task: "Add _suppress_theme_persist guard attribute to app state in src/impactite/app.py"
Task: "Rewrite action_toggle_theme to use the user theme and resolver in src/impactite/app.py"
Task: "Update watch_theme to skip persistence when _suppress_theme_persist is set in src/impactite/app.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Toggle `Ctrl+L` twice and confirm the original theme returns
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently (restart app)
4. Add User Story 3 → Test independently (invalid config fallback)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify `python -m compileall src` passes after each substantial change
- Commit after each task or logical group
- Stop at any checkpoint to validate the story independently
- Avoid vague tasks; every task references an exact file path

## Validation log

- `uv run python -m compileall src` — passed
- E2E toggle test (`rose-pine-dawn` → `rose-pine-moon` → `rose-pine-dawn`) — passed
- Invalid theme fallback (`not-a-real-theme` → `textual-dark`) — passed
