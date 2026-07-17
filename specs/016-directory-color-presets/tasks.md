# Tasks: Directory Color Presets

|**Input**: Design documents from `specs/016-directory-color-presets/`

|**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

## Phase 1: Core UI

|**Purpose**: Add the preset colour palette to the existing directory colour modal

|- [x] T001 [US1] Update `DirectoryColorModal` to include a 16-colour preset palette between the inputs and the existing hint label.
  - Palette layout: 4 rows × 4 columns.
  - Each button displays its colour as a filled block and sets the current/focused input.
|- [x] T002 [US1] Track the most-recently-focused colour input (`color-bg-input` or `color-fg-input`).
  - On modal mount the background input is focused, so the background input is the default target.
|- [x] T003 [US1] Implement `on_button_pressed` for preset buttons to populate the target input with the button's colour.
  - If the focused input cannot be determined, default to `color-bg-input`.
|- [x] T004 [US2] Ensure manual input fields remain visible and functional.
  - Existing `on_input_submitted` and `_confirm` logic must remain unchanged except for the button handler.
|- [x] T005 [US3] Add a user-facing label "Preset colors" with translations in `src/impactite/i18n.py`.
  - English: "Preset colors"
  - Russian: "Готовые цвета"
  - German: "Voreingestellte Farben"

**Checkpoint**: The modal shows 16 colour buttons and clicking them fills the current input.

---

## Phase 2: Validation

|**Purpose**: Confirm the palette works and existing behaviour is preserved

|- [x] T006 [P] [US1] Run syntax check: `python -m compileall src`
|- [x] T007 [P] [US1] Run existing smoke tests: `uv run python /tmp/test_backdrop_smoke.py`
|- [x] T008 [P] [US1] Run existing overlay tests: `uv run python /tmp/test_backdrop_overlays.py`
|- [x] T009 [US1] Write a focused headless test that opens `DirectoryColorModal` and asserts a preset button updates the background input.
|- [x] T010 [US2] In the same headless test, focus the text input and assert a different preset updates the text input.
|- [x] T011 [US3] Assert the original confirm/cancel flow still dismisses the modal correctly after selecting presets.

---

## Phase 3: Polish

|**Purpose**: Final cleanup and task completion

|- [x] T012 Mark all `tasks.md` items `[X]`
|- [x] T013 Run `git diff -- src/impactite/app.py src/impactite/i18n.py` to verify no scope creep
