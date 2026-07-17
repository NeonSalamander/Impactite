# Tasks: Modal and Context Menu Backdrop Dimming

|**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/011-modal-contextmenu-backdrop/`

|**Prerequisites**: plan.md (required), spec.md (required)

## Phase 1 — Setup

Goal: Understand the current CSS for modal screens and the context-menu overlay.

- [x] T001 Read the current `MarkdownEditorApp.DEFAULT_CSS` block in `src/impactite/app.py` and locate all modal screen/backdrop rules.
- [x] T002 Identify every `ModalScreen` subclass (directory-color, text-prompt, tag-search, template-select, etc.) in `src/impactite/app.py` that might set its own `background`.
- [x] T003 Locate the `DirectoryContextMenu` CSS rule and re-read how the overlay is mounted in `src/impactite/app.py`.

## Phase 2 — Foundational

Goal: Choose the dimming approach and confirm Textual supports it.

- [x] T004 Decide a shared opacity value for overlay backdrops (e.g., 20–30%) based on the specification's "slightly dim" requirement; document the value in `src/impactite/app.py` as a comment near the CSS rule.
- [x] T005 [P] Verify that the chosen opacity value compiles and runs without a Textual CSS error using a minimal `App.run_test()` snippet against `src/impactite/app.py`.
- [x] T006 Confirm the opacity syntax works for both dark and light themes by temporarily toggling `app.theme` in a headless test and inspecting that no errors occur.

## Phase 3 — US1: Dialog backdrops remain visible

Goal: Ensure modal dialogs only slightly dim the workspace.

- [x] T007 [US1] Add a global `ModalScreen` CSS rule in `src/impactite/app.py` that sets the backdrop background to `$background` with the chosen low opacity.
- [x] T008 [US1] Remove or align any per-modal `background` override in `src/impactite/app.py` (e.g., `TextPromptModal`) to the same opacity value so all dialogs dim equally.
- [x] T009 [US1] Manual/visual check: open the directory-color dialog and confirm the note/tree behind it is still visible, not black.
- [x] T010 [US1] [P] Run `python -m compileall src` after CSS edits.

## Phase 4 — US2: Context menu backdrops remain visible

Goal: The directory context menu overlay uses the same gentle dimming.

- [x] T011 [US2] Update the `DirectoryContextMenu` CSS rule in `src/impactite/app.py` to apply the same low-opacity `$background` backdrop instead of `background: transparent`.
- [x] T012 [US2] Ensure the menu box (`#directory-context-menu-box`) remains opaque so menu items are readable while the surrounding overlay is dim.
- [x] T013 [US2] Manual/visual check: right-click a directory and confirm the tree behind the menu is still visible.

## Phase 5 — US3: Consistent dimming across overlays

Goal: All modal dialogs and the context menu use the same dimming level.

- [x] T014 [US3] Visually compare the directory-color dialog, text-prompt dialog, tag-search dialog, template-select dialog, and directory context menu in `src/impactite/app.py` to ensure their backdrops look equally dim.
- [x] T015 [US3] [P] Fix any dialog whose backdrop remains visibly darker or lighter than the chosen value by adjusting its CSS in `src/impactite/app.py`.
- [x] T016 [US3] Switch between dark and light theme and verify the relative dimming stays consistent in both.

## Phase 6 — Polish & cross-cutting concerns

Goal: Verify no regressions and update feature tasks.

- [x] T017 [P] Run the full quickstart validation steps in `specs/011-modal-contextmenu-backdrop/quickstart.md` and record results.
- [x] T018 [P] Run a headless smoke test that opens the directory-color dialog and the context menu and asserts neither crashes (`src/impactite/app.py`).
- [x] T019 [P] Run `python -m compileall src` as a final syntax check.
- [x] T020 [P] Mark remaining tasks in `specs/011-modal-contextmenu-backdrop/tasks.md` as `[x]` once all prior phases pass.

## Dependencies

```text
Phase 1 (Setup)
    |
    v
Phase 2 (Foundational) -> opacity value chosen and verified
    |
    +---> Phase 3 (US1) -> global ModalScreen rule
    |       |
    |       v
    +---> Phase 4 (US2) -> context menu overlay rule
            |
            v
    +---> Phase 5 (US3) -> consistency pass across all overlays
            |
            v
    +---> Phase 6 (Polish)
```

## Parallel execution opportunities

- T005, T006, T010, T019 are independent verification tasks.
- T009 (dialog visual check) and T013 (menu visual check) can be run in parallel once their CSS rules are in place.
- T015, T016, T017, T018, T020 can be executed in parallel after US1/US2/US3 are complete.

## Implementation strategy

MVP = Phase 1 + Phase 2 + Phase 3 (US1): add a single `ModalScreen` backdrop rule. This alone makes the most common complaint (dialogs going black) disappear. Phase 4 (US2) extends the same rule to the context menu. Phase 5 (US3) polishes consistency, and Phase 6 validates everything.
