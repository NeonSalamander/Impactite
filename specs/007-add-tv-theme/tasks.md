# Tasks: Add TV Theme

**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/007-add-tv-theme/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/theme-system.md, quickstart.md

**Tests**: No automated tests requested. Validation is manual per `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Understand the current theme mechanism and confirm the Textual API.

- [x] T001 [P] Review current theme imports and `_LIGHT_THEMES` usage in `src/impactite/app.py`
- [x] T002 [P] Review how `Config.get_user_theme()` and `validate_theme()` load the persisted theme in `src/impactite/core.py` and `src/impactite/app.py`
- [x] T003 [P] Confirm `textual.theme.Theme` and `App.register_theme` are available in the installed Textual version (`uv run python -c "from textual.theme import Theme; from textual.app import App"`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the TV theme definition before any UI path can use it.

**⚠️ CRITICAL**: User stories cannot begin until the theme object exists and is importable in `app.py`.

- [x] T004 Add `from textual.theme import Theme` to the imports in `src/impactite/app.py`
- [x] T005 Define the module-level `TV_THEME: Theme` constant in `src/impactite/app.py` using the TurboVision palette from `research.md`

**Checkpoint**: `TV_THEME` is defined and contains the expected color tokens (`#0000aa` background, `#00aaaa` primary, `#ffff55` accent, `dark=True`).

---

## Phase 3: User Story 1 - Select the TV Theme (Priority: P1) 🎯 MVP

**Goal**: Make "TV" a selectable, valid theme that can be activated at startup or runtime.

**Independent Test**: Start the app with `display.app_theme: tv` in `config.yaml` and confirm it loads the TurboVision palette. Alternatively, switch to TV via the existing theme toggle and confirm the UI changes.

### Implementation for User Story 1

- [x] T006 [US1] Register `TV_THEME` in `MarkdownEditorApp.__init__` in `src/impactite/app.py` after `super().__init__()`
- [x] T007 [US1] Update the startup theme assignment in `MarkdownEditorApp.__init__` in `src/impactite/app.py` to validate against registered themes via `self.get_theme(name)` (fallback to `textual-dark`)
- [x] T008 [US1] Verify `action_toggle_theme` in `src/impactite/app.py` treats "tv" as a dark theme and switches to a light counterpart

**Checkpoint**: User Story 1 is fully functional — the TV theme can be selected and the UI updates.

---

## Phase 4: User Story 2 - TV Theme Applies Consistently (Priority: P2)

**Goal**: Ensure the TV palette covers all common widgets and surfaces, including code blocks.

**Independent Test**: With TV active, open notes, dialogs, and menus; confirm every surface uses TV colors and code blocks remain readable.

### Implementation for User Story 2

- [x] T009 [US2] Verify `DEFAULT_CSS` and global CSS in `src/impactite/app.py` do not hardcode colors that override the TV theme tokens unintentionally
- [x] T010 [US2] Adjust `TV_THEME` token values in `src/impactite/app.py` if any widget surface shows poor contrast during manual inspection
- [x] T011 [US2] Verify `_apply_editor_syntax_theme` in `src/impactite/app.py` keeps a dark pygments theme when "tv" is active
- [x] T012 [US2] Verify Markdown rendering and code blocks in `src/impactite/app.py` use theme-aware backgrounds and remain readable on the dark-blue TV background

**Checkpoint**: User Stories 1 and 2 both work independently — TV theme is selectable and renders consistently.

---

## Phase 5: User Story 3 - TV Theme Persists Across Sessions (Priority: P3)

**Goal**: Ensure the TV theme choice survives an app restart.

**Independent Test**: Set theme to TV, close the app, reopen it, and verify the UI is still in TV mode; check `config.yaml` contains `display.app_theme: tv`.

### Implementation for User Story 3

- [x] T013 [US3] Verify `watch_theme` in `src/impactite/app.py` persists "tv" to `config.yaml` when the theme changes
- [x] T014 [US3] Verify cold start with a `config.yaml` value of `display.app_theme: tv` restores the TV theme in `src/impactite/app.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate completeness, prevent regressions, and update documentation.

- [x] T015 [P] Run `python -m compileall src`
- [x] T016 [P] Launch the app with `display.app_theme: tv` and visually inspect each `quickstart.md` scenario
- [x] T017 [P] Regression check: verify existing themes (`textual-dark`, `textual-light`, `catppuccin-mocha`, etc.) still render correctly in `src/impactite/app.py`
- [x] T018 [P] Verify `Ctrl+L` behavior when TV is active switches cleanly without artifacts
- [x] T019 Skipped: no user-facing theme menu was added, so no i18n label key is required

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — blocks all user stories.
- **User Stories (Phase 3–5)**: All depend on Foundational phase completion.
  - Proceed sequentially in priority order (P1 → P2 → P3).
  - Stories 2 and 3 can overlap with story 1 once the theme is registered.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational. No dependencies on other stories.
- **User Story 2 (P2)**: Can start after Foundational. Builds on US1 only in that the theme must be registered first.
- **User Story 3 (P3)**: Can start after Foundational. Builds on US1 in that the theme must be activatable.

### Parallel Opportunities

- T001, T002, T003 can run in parallel.
- T004 and T005 are sequential (imports precede constant definition).
- T011 and T012 can run in parallel after T010.
- All Phase 6 validation tasks can run in parallel once implementation is complete.

---

## Parallel Example: User Story 2

```bash
# After TV theme registration and selection work:
Task: "T009 Verify DEFAULT_CSS and global CSS do not hardcode colors"
Task: "T010 Adjust TV_THEME token values for contrast"
Task: "T011 Verify _apply_editor_syntax_theme keeps a dark pygments theme"
Task: "T012 Verify Markdown rendering and code blocks remain readable"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test that TV theme is selectable and loads.
5. Continue to User Stories 2 and 3.

### Incremental Delivery

1. Setup + Foundational → theme object ready.
2. User Story 1 → TV selectable and valid.
3. User Story 2 → TV renders consistently across widgets.
4. User Story 3 → TV persists across restarts.
5. Polish → compile checks, visual validation, regression checks.

---

## Notes

- `[P]` tasks can run in parallel when they touch different files or have no mutual dependencies.
- Each user story is independently completable and manually testable.
- Stop at any checkpoint to validate the story independently.
- Avoid vague tasks; each task names a concrete file and action.
