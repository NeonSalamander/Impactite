# Tasks: Suppress External Link Launch Warnings

**Input**: Design documents from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/006-suppress-link-launch-warning/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Manual validation only; no automated test suite is present in the project.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inspect the existing external link opening code and confirm project constraints.

- [x] T001 [P] Review current `open_url` implementation in `src/impactite/core.py`
- [x] T002 [P] Confirm `app.py` error handler still catches `OpenUrlError` and does not need changes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Validate that the planned fd-redirection approach is permitted and safe.

- [x] T003 Verify `webbrowser` and `os` are available in stdlib and no new dependency is required

**Checkpoint**: Foundation ready — single-function implementation can proceed.

---

## Phase 3: User Story 1 - Open External Link Without Console Noise (Priority: P1) 🎯 MVP

**Goal**: Clicking a raw or Markdown external link opens the browser and does not show the browser process's stdout/stderr in the TUI.

**Independent Test**: Create a note with `https://ya.ru` and `[Example](http://example.com)`. Click both links. The browser opens each URL and the TUI shows no line such as `kf.iconthemes: Icon theme "Breeze" not found.`.

### Implementation for User Story 1

- [x] T004 [US1] Implement stdout/stderr fd redirect to `os.devnull` around `webbrowser.open()` in `src/impactite/core.py`
- [x] T005 [US1] Add `try/finally` restoration of saved fds and safe close of `os.devnull` fd in `src/impactite/core.py`
- [x] T006 [US1] Ensure `OpenUrlError` is raised when `webbrowser.open` returns `False` or raises in `src/impactite/core.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Preserve Error Feedback on Browser Failure (Priority: P2)

**Goal**: When the browser cannot be opened, the user still sees a localized error notification instead of raw process output.

**Independent Test**: Click `[Bad](http://this-protocol-does-not-exist.invalid/)`. A localized error notification appears and the app does not crash.

### Implementation for User Story 2

- [x] T007 [US2] Verify `on_markdown_viewer_external_link_clicked` in `src/impactite/app.py` still catches `OpenUrlError` after fd redirection
- [x] T008 [US2] Confirm the localized notification key `Could not open link: {url}` displays correctly in `src/impactite/app.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Ensure no regressions and complete validation.

- [x] T009 [P] Run `python -m compileall src`
- [x] T010 [P] Launch the app with a temporary config and verify the first screen renders
- [x] T011 Verify internal Markdown links still open target notes in `src/impactite/app.py` (regression check)
- [x] T012 Verify external links inside fenced code blocks and inline code spans remain non-interactive in `src/impactite/app.py` (regression check)
- [x] T013 Run validation steps from `quickstart.md` for raw URL, Markdown external link, and failure path

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; single validation task
- **User Stories (Phase 3-4)**: All depend on Foundational phase completion
  - User stories proceed sequentially in priority order (P1 → P2)
- **Polish (Phase 5)**: Depends on both user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after User Story 1 is complete - ensures the primary fix works before validating its error path

### Within Each User Story

- Core implementation (fd redirection) before manual verification
- `OpenUrlError` contract verification before error-path validation
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run in parallel (different concerns, same file read-only)
- T009 and T010 can run in parallel (syntax check and launch are independent)

---

## Parallel Example: User Story 1

```bash
# Review and foundational checks
Task: "Review current open_url implementation in src/impactite/core.py"
Task: "Confirm app.py error handler still catches OpenUrlError"
Task: "Verify webbrowser and os are available in stdlib"

# Implementation
Task: "Implement stdout/stderr fd redirect around webbrowser.open() in src/impactite/core.py"
Task: "Add try/finally restoration of saved fds in src/impactite/core.py"
Task: "Ensure OpenUrlError contract is preserved in src/impactite/core.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test both raw URL and Markdown external link; confirm no console noise

### Incremental Delivery

1. Setup + Foundational → confirm single-function change is safe
2. User Story 1 → implement fd suppression → validate clean TUI
3. User Story 2 → validate error notification still works
4. Polish → regression checks and `python -m compileall src`

---

## Notes

- [P] tasks = different files or independent concerns, no dependencies
- [Story] label maps task to the specific user story for traceability
- Each user story should be independently completable and testable
- Stop at any checkpoint to validate the story independently
- Avoid: vague tasks, implementation details in task descriptions, cross-story dependencies that break independence
