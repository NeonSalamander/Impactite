---

description: "Task list for current note in-editor search"

---

# Tasks: Current Note In-Editor Search

**Input**: Design documents from `/specs/001-current-note-search/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-search-contract.md, quickstart.md

**Tests**: Not requested in the specification. No automated test tasks are generated; validation is performed manually via `quickstart.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Single project: `src/impactite/`, configuration in `config.yaml`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add configuration and translation keys required by all user stories.

- [X] T001 Add default `search_in_note: "f7"` hotkey to `Config.load()` defaults in `src/impactite/core.py`
- [X] T002 [P] Add canonical English keys and `ru`/`de` translations for the in-note search dialog in `src/impactite/i18n.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the pure search-state model and helper used by both the viewer and the editor.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Create `Match` and `SearchState` dataclasses in `src/impactite/core.py`
- [X] T004 Implement `find_matches(text: str, query: str) -> List[Match]` helper in `src/impactite/core.py`
- [X] T005 [P] Add a reusable translucent overlay + shadow CSS class for the search dialog in `src/impactite/app.py`

**Checkpoint**: Foundation ready — `core.py` provides match computation and the app has a styled overlay primitive.

---

## Phase 3: User Story 1 - Open in-note search (Priority: P1) 🎯 MVP

**Goal**: Users can open and close a dedicated in-note search dialog with a hotkey in both view and edit modes.

**Independent Test**: Open any note, press `F7`; confirm the search dialog appears and focus moves to the input field. Press `Escape`; confirm the dialog closes, highlights are removed, and focus returns to the viewer/editor.

### Implementation for User Story 1

- [X] T006 [US1] Create `InNoteSearch` modal screen class in `src/impactite/app.py`
- [X] T007 [US1] Wire the `search_in_note` hotkey binding to push `InNoteSearch` in `MarkdownEditorApp` in `src/impactite/app.py`
- [X] T008 [US1] Apply non-dimming translucent background + shadow CSS to `InNoteSearch` in `src/impactite/app.py`
- [X] T009 [US1] Implement close-on-escape and focus return to the viewer/editor in `src/impactite/app.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Find and highlight matches (Priority: P1)

**Goal**: Typing a query highlights all occurrences in the current note and shows a clear empty state when there are no matches.

**Independent Test**: Open a note, press `F7`, type a word that appears multiple times; confirm all occurrences are highlighted and the first match is selected/scrolled into view. Type a non-existent word and confirm a "no results" indication appears.

### Implementation for User Story 2

- [X] T010 [US2] Pass current note text into `InNoteSearch` when it opens in `src/impactite/app.py`
- [X] T011 [US2] Extend `MarkdownViewer.update_content()` to accept and render in-note match highlights in `src/impactite/app.py`
- [X] T012 [US2] Recompute `SearchState.matches` on every input change and refresh highlights in `src/impactite/app.py`
- [X] T013 [US2] Add a status label showing `current / total` matches in `InNoteSearch` in `src/impactite/app.py`
- [X] T014 [US2] Handle empty and whitespace-only queries by clearing highlights and updating status in `src/impactite/app.py`
- [X] T015 [US2] Handle no-results state with a clear empty-state message in `src/impactite/app.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 - Navigate between matches (Priority: P2)

**Goal**: Users can step through matches using the existing previous/next result controls already used for global full-text search.

**Independent Test**: Search for a word with multiple matches, press the existing "next result" control repeatedly; confirm the selection advances and each match scrolls into view, wrapping from last to first. Do the same for "previous result".

### Implementation for User Story 3

- [X] T016 [US3] Track whether in-note search is active and reuse existing next/previous result actions in `MarkdownEditorApp` in `src/impactite/app.py`
- [X] T017 [US3] Scroll the selected in-note match into view in `MarkdownViewer` in `src/impactite/app.py`
- [X] T018 [US3] Update `EditorTextArea` selection to the current in-note match when in edit mode in `src/impactite/app.py`
- [X] T019 [US3] Implement wrap-around navigation at first/last match in `src/impactite/app.py`

**Checkpoint**: User Stories 1, 2, and 3 should now be independently functional.

---

## Phase 6: User Story 4 - Non-obstructive dialog appearance (Priority: P2)

**Goal**: The search dialog visually separates itself from the note with a shadow and does not obscure note content.

**Independent Test**: Open the search dialog over a note and visually confirm that the text behind the dialog remains readable and only the dialog casts a shadow.

### Implementation for User Story 4

- [X] T020 [US4] Restrict `InNoteSearch` dialog to a compact height near the top of the screen in `src/impactite/app.py`
- [X] T021 [US4] Verify and tune CSS so the overlay background is fully transparent/translucent and only the dialog region casts a shadow in `src/impactite/app.py`

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, manual validation, and minor configuration updates.

- [X] T022 [P] Handle edge cases: empty note, user switches note while dialog is open, mode toggle while search is active in `src/impactite/app.py`
- [X] T023 [P] Update sample `config.yaml` with the new `search_in_note: "f7"` entry
- [X] T024 [P] Walk through the validation steps in `specs/001-current-note-search/quickstart.md` and fix any deviations
- [X] T025 [P] Run `python -m compileall src` and a smoke run of the app to first screen

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — blocks all user stories.
- **User Stories (Phase 3–6)**: All depend on Foundational phase completion.
  - Execute in priority order (P1 → P2) or in parallel if team capacity allows.
- **Polish (Phase 7)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational. No dependencies on other stories.
- **User Story 2 (P1)**: Starts after User Story 1 because it reuses the dialog and requires highlight plumbing.
- **User Story 3 (P2)**: Starts after User Story 2 because it depends on existing match highlights.
- **User Story 4 (P2)**: Can be done in parallel with User Story 2/3 once the dialog exists.

### Within Each User Story

- Models/helpers before UI wiring.
- Core widget action before integration with global navigation.
- Story complete before moving to the next priority.

### Parallel Opportunities

- T001 and T002 can run in parallel.
- T003, T004, T005 can run in parallel.
- Once the `InNoteSearch` skeleton exists, T011 (viewer highlights) and T018 (editor selection) can be worked on in parallel.
- Polish tasks T022–T025 can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Wire modal + hotkey:
Task: "T006 Create InNoteSearch modal screen class in src/impactite/app.py"
Task: "T007 Wire search_in_note hotkey binding in src/impactite/app.py"

# Apply styling and dismissal independently:
Task: "T008 Apply non-dimming translucent background + shadow CSS in src/impactite/app.py"
Task: "T009 Implement close-on-escape and focus return in src/impactite/app.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 and 2)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1 (open/close dialog).
4. Complete Phase 4: User Story 2 (highlight on input).
5. **STOP and VALIDATE**: Run the first four quickstart scenarios.
6. Deploy/demo if ready.

### Incremental Delivery

1. Setup + Foundational → Foundation ready.
2. Add User Story 1 → Test independently.
3. Add User Story 2 → Test independently (MVP complete here).
4. Add User Story 3 → Test independently.
5. Add User Story 4 → Test independently.
6. Run Polish phase and final quickstart validation.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together.
2. Once the `InNoteSearch` dialog skeleton exists:
   - Developer A: User Story 2 viewer highlights.
   - Developer B: User Story 3 navigation and editor selection.
   - Developer C: User Story 4 visual polish.
3. Integrate all changes and run quickstart validation.

---

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps a task to a specific user story for traceability.
- Each user story should be independently completable.
- Commit after each task or logical group.
- Avoid vague tasks or cross-story dependencies that break independence.
