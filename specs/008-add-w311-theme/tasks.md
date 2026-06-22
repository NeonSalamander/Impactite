# Tasks: Add W311 Theme

**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/008-add-w311-theme/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not explicitly requested. Validation tasks are included as manual checks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single project layout: `src/impactite/app.py`, `src/impactite/core.py`, `src/impactite/i18n.py`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Understand the current theme mechanism before making changes.

- [x] T001 [P] Review existing theme imports and `_LIGHT_THEMES` usage in `src/impactite/app.py`
- [x] T002 [P] Confirm `textual.theme.Theme` and `App.register_theme` are available in the project's Textual version
- [x] T003 [P] Review how `Config.get_user_theme()` and `Config.save_user_theme()` persist the active theme in `src/impactite/core.py`

**Checkpoint**: Current theme code is understood; no ambiguous dependencies remain.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the theme definition and mark it as light before any user story can be functional.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Add `from textual.theme import Theme` to the imports in `src/impactite/app.py` (verify it is already present if another custom theme exists)
- [x] T005 Define the module-level `W311_THEME: Theme` constant in `src/impactite/app.py` using the Windows 3.11 palette from `research.md`
- [x] T006 Add `"w311"` to the `_LIGHT_THEMES` frozenset in `src/impactite/app.py`

**Checkpoint**: Foundation ready — a light Windows 3.11 theme object exists and is known to the light-theme logic.

---

## Phase 3: User Story 1 - Select the W311 Theme (Priority: P1) 🎯 MVP

**Goal**: Users can switch to the "W311" theme and immediately see the Windows 3.11 look.

**Independent Test**: Headless launch with `display.app_theme: w311` sets `app.theme == "w311"`.

### Implementation for User Story 1

- [x] T007 [US1] Register `W311_THEME` in `MarkdownEditorApp.__init__` in `src/impactite/app.py` after `super().__init__()`
- [x] T008 [US1] Verify the startup theme assignment in `MarkdownEditorApp.__init__` in `src/impactite/app.py` accepts the registered "w311" theme and falls back to "textual-dark" for unknown values
- [x] T009 [US1] Headless launch test: create a temporary `config.yaml` with `display.app_theme: w311` and assert `app.theme == "w311"` after `App.run_test()`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - W311 Theme Applies Consistently (Priority: P2)

**Goal**: The W311 theme covers all core surfaces and keeps code blocks readable.

**Independent Test**: With `w311` active, open a note with a fenced code block; no exceptions and editor code theme uses a light pygments theme.

### Implementation for User Story 2

- [x] T010 [US2] Verify `DEFAULT_CSS` and global CSS in `src/impactite/app.py` do not hardcode colors that override the W311 theme tokens unintentionally
- [x] T011 [US2] Adjust `W311_THEME` token values in `src/impactite/app.py` if any widget surface shows poor contrast during manual inspection
- [x] T012 [US2] Verify `_apply_editor_syntax_theme` in `src/impactite/app.py` switches to `github_light` when "w311" is active
- [x] T013 [US2] Verify Markdown rendering and code blocks in `src/impactite/app.py` use theme-aware backgrounds and remain readable on the light gray W311 background

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - W311 Theme Persists Across Sessions (Priority: P3)

**Goal**: The user's W311 choice survives an app restart.

**Independent Test**: Set theme to "w311" in `App.run_test()`, close the test, and read `"w311"` from the config file.

### Implementation for User Story 3

- [x] T014 [US3] Verify `watch_theme` in `src/impactite/app.py` persists "w311" to `config.yaml` when the theme changes
- [x] T015 [US3] Verify cold start with a `config.yaml` value of `display.app_theme: w311` restores the W311 theme in `src/impactite/app.py`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate completeness, prevent regressions, and update documentation.

- [x] T016 [P] Run `python -m compileall src`
- [x] T017 [P] Launch the app with `display.app_theme: w311` and visually inspect each `quickstart.md` scenario
- [x] T018 [P] Regression check: verify existing themes (`textual-dark`, `textual-light`, `tv`, `catppuccin-mocha`, etc.) still render correctly in `src/impactite/app.py`
- [x] T019 [P] Verify `Ctrl+L` behavior when W311 is active switches cleanly without artifacts
- [x] T020 Skipped: no user-facing theme menu was added, so no i18n label key is required

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
- **User Story 3 (P3)**: Can start after User Story 1 (requires persistence) — Independently testable once US1 works.

### Within Each User Story

- Core implementation before integration.
- Story complete before moving to next priority.

### Parallel Opportunities

- T001, T002, T003 can run in parallel.
- T004, T005, T006 can run in parallel (different regions of `src/impactite/app.py`).
- T016, T017, T018, T019 can run in parallel.

### Parallel Example: Foundational Phase

```text
Task: "Add Textual Theme import to src/impactite/app.py"
Task: "Define W311_THEME constant in src/impactite/app.py using the Windows 3.11 palette"
Task: "Add 'w311' to _LIGHT_THEMES in src/impactite/app.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational — define and register W311 theme.
3. Complete Phase 3: User Story 1 — make W311 selectable.
4. **STOP and VALIDATE**: Test User Story 1 independently.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready.
2. Add User Story 1 → Test independently (MVP!).
3. Add User Story 2 → Test consistency and readability.
4. Add User Story 3 → Test persistence.
5. Run Phase 6 polish/regression checks.

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Each user story should be independently completable and testable.
- Commit after each task or logical group.
- Stop at any checkpoint to validate a story independently.
