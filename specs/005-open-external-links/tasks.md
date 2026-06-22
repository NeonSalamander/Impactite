# Tasks: Open External Links

**Input**: Design documents from `/specs/005-open-external-links/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Understand current implementation and prepare shared changes

- [x] T001 Review current MarkdownViewer link rendering and click handling in `src/impactite/app.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core helpers and UI contract that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 [P] Add raw URL and external Markdown link detection helper in `src/impactite/core.py`
- [x] T003 [P] Add `open_url` helper and `OpenUrlError` exception in `src/impactite/core.py`
- [x] T004 [P] Add external-link error i18n keys to `src/impactite/i18n.py`
- [x] T005 [P] Add `MarkdownViewer.ExternalLinkClicked` message in `src/impactite/app.py`
- [x] T006 Add App handler for `ExternalLinkClicked` in `src/impactite/app.py` (depends on T003, T004, T005)

**Checkpoint**: Foundation ready — external links can be detected, rendered, and opened by the App

---

## Phase 3: User Story 1 - Open a Raw URL in a Note (Priority: P1) 🎯 MVP

**Goal**: When a note in view mode contains a raw `http://` or `https://` URL, the URL is styled as a clickable link and opens in the default browser when activated.

**Independent Test**: View a note containing `https://ya.ru` in plain text and click the URL; the browser opens `https://ya.ru`.

### Implementation for User Story 1

- [x] T007 Update `MarkdownViewer.update_content` in `src/impactite/app.py` to detect raw URLs in plain-text lines
- [x] T008 [US1] Style raw URL links and append them to `_link_lines` for click handling in `src/impactite/app.py`
- [x] T009 [US1] Validate raw URL click opens the browser (follow `quickstart.md` validation steps)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Open a Markdown Inline Link (Priority: P2)

**Goal**: When a note in view mode contains a Markdown inline link with an `http://` or `https://` target, the visible text is clickable and opens the target in the default browser.

**Independent Test**: View a note containing `[Example](http://example.com)` and click the link text; the browser opens `http://example.com`.

### Implementation for User Story 2

- [x] T010 [US2] Update `_process_formatting_inline` in `src/impactite/app.py` to classify `http://`/`https://` Markdown links as external and return them for tracking
- [x] T011 [US2] Render tracked external Markdown links with the same clickable style as raw URLs in `src/impactite/app.py`
- [x] T012 [US2] Validate Markdown inline link click opens the browser (follow `quickstart.md` validation steps)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Distinguish and Select Among Multiple Links (Priority: P3)

**Goal**: A note with several external links (raw URLs and/or Markdown links) allows the user to activate any one of them independently.

**Independent Test**: View a note with two or more different external links and confirm each one opens its own unique URL.

### Implementation for User Story 3

- [x] T013 [US3] Verify that multiple links per rendered line are tracked with independent hit regions in `src/impactite/app.py`
- [x] T014 [US3] Validate clicking different links opens the correct URL (follow `quickstart.md` validation steps)

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality checks, error paths, and integration validation

- [x] T015 [P] Confirm links inside code blocks remain inactive (follow `quickstart.md` validation steps)
- [x] T016 [P] Verify failed browser opens display a localized error notification (follow `quickstart.md` error-path validation)
- [x] T017 [P] Run `python -m compileall src` and fix any syntax errors
- [x] T018 [P] Launch the application and verify the first screen renders without errors
- [x] T019 [P] Verify link styling is visible in both light and dark themes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — may share styling with US1 but can be implemented independently
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — validates US1 and US2 together; should be independently testable once both are done

### Within Each User Story

- Implementation tasks are sequential within a story
- Each story ends with a manual validation task
- Story complete before moving to next priority

### Parallel Opportunities

- T002, T003, T004, and T005 can run in parallel during the Foundational phase
- T016, T017, T018, and T019 can run in parallel during the Polish phase
- User Stories 1, 2, and 3 can be worked on in parallel once Phase 2 is complete (US3 validation needs US1 and US2 complete)

---

## Parallel Example: User Story 1

```bash
# These tasks can be picked up together after Phase 2 is done:
Task: "Update MarkdownViewer.update_content in src/impactite/app.py to detect raw URLs in plain-text lines"
Task: "Style raw URL links and append them to _link_lines for click handling in src/impactite/app.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test raw URL opening independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test raw URL opening independently
3. Add User Story 2 → Test Markdown inline link opening independently
4. Add User Story 3 → Test multiple-link selection independently
5. Complete Polish phase → syntax check, launch check, theme check

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
3. Developer C picks up User Story 3 once US1 and US2 are complete
4. Polish tasks are distributed in parallel

---

## Notes

- [P] tasks = different files or independent logic, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No automated tests are requested; validation is manual per `quickstart.md`
- Commit after each task or logical group
- Stop at any checkpoint to validate a story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
