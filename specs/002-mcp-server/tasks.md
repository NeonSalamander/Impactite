# Tasks: MCP Server Integration

**Input**: Design documents from `/specs/002-mcp-server/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [data-model.md](data-model.md), [contracts/](contracts/), [research.md](research.md), [quickstart.md](quickstart.md)

**Tests**: Not explicitly requested; core tool handlers remain unit-testable per the project constitution, but no test files are required for completion.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., [US1], [US2])
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the new dependency and create the two new source modules defined in the implementation plan.

- [X] T001 Add the `mcp` package dependency to `pyproject.toml` with a comment explaining it is the official MCP Python SDK
- [X] T002 Create `src/impactite/mcp_tools.py` with module docstring and response datatypes (Note, NoteRef, WriteResult)
- [X] T003 Create `src/impactite/mcp_server.py` with module docstring and an empty `Server` instance placeholder

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the shared primitives that every MCP tool depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Add `--mcp` CLI branch to `src/impactite/app.py:main()` that launches the server instead of the TUI when the flag is present
- [X] T005 Implement `resolve_note_id(note_id)` helper in `src/impactite/mcp_tools.py` that validates the path stays inside `notes_path`
- [X] T006 Implement `mcp_error(code, message)` helper in `src/impactite/mcp_tools.py` for uniform error responses
- [X] T007 Implement `load_note(note_id)` helper in `src/impactite/mcp_tools.py` that reads Markdown, parses frontmatter, and returns a `Note` object
- [X] T008 Implement `schedule_index_refresh()` helper in `src/impactite/mcp_tools.py` that marks indexes dirty and schedules a background rebuild within 3 seconds

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 — Retrieve note context (Priority: P1) 🎯 MVP

**Goal**: External clients can read individual notes, list notes, and run keyword searches.

**Independent Test**: Launch `impactite --mcp`, call `get_note`, `list_notes`, and `search_notes`; each returns the expected schema.

### Implementation for User Story 1

- [X] T009 [US1] Implement the `get_note` tool handler in `src/impactite/mcp_tools.py`
- [X] T010 [P] [US1] Implement the `list_notes` tool handler with optional `filter` and `type` parameters in `src/impactite/mcp_tools.py`
- [X] T011 [US1] Implement the `search_notes` tool handler with optional `type_filter` in `src/impactite/mcp_tools.py`
- [X] T012 [US1] Register `get_note`, `list_notes`, and `search_notes` with the MCP server in `src/impactite/mcp_server.py`
- [X] T013 [US1] Validate US1 tools against the scenarios in `specs/002-mcp-server/quickstart.md`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 — Create and update notes (Priority: P2)

**Goal**: External clients can create notes, update existing notes, and fill form-type notes.

**Independent Test**: Call `create_note`, verify the file appears; call `update_note` and `fill_form`, verify content and schema changes; verify optimistic concurrency rejects stale writes.

### Implementation for User Story 2

- [X] T014 [US2] Implement the `create_note` tool handler in `src/impactite/mcp_tools.py` (derives path from type/content if `note_id` is omitted)
- [X] T015 [P] [US2] Implement the `update_note` tool handler with optimistic concurrency (`last_modified_at` check) in `src/impactite/mcp_tools.py`
- [X] T016 [P] [US2] Implement the `fill_form` tool handler with schema validation and optimistic concurrency in `src/impactite/mcp_tools.py`
- [X] T017 [US2] Register `create_note`, `update_note`, and `fill_form` with the MCP server in `src/impactite/mcp_server.py`
- [X] T018 [US2] Validate US2 tools against the create/update/form scenarios in `specs/002-mcp-server/quickstart.md`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 — Discover note types and schemas (Priority: P3)

**Goal**: External clients can list available note types, read type schemas, and list notes by type.

**Independent Test**: Call `get_note_types`, `get_type_schema`, and `list_notes_by_type`; results match the configured type definitions.

### Implementation for User Story 3

- [X] T019 [US3] Implement the `get_note_types` tool handler in `src/impactite/mcp_tools.py`
- [X] T020 [P] [US3] Implement the `get_type_schema` tool handler in `src/impactite/mcp_tools.py`
- [X] T021 [P] [US3] Implement the `list_notes_by_type` tool handler in `src/impactite/mcp_tools.py`
- [X] T022 [US3] Register type-discovery tools with the MCP server in `src/impactite/mcp_server.py`
- [X] T023 [US3] Validate US3 tools against the quickstart type-discovery scenario

**Checkpoint**: User Stories 1, 2, and 3 all work independently.

---

## Phase 6: User Story 4 — Search by content and similarity (Priority: P4)

**Goal**: External clients can run filtered full-text searches and find notes similar to a given note.

**Independent Test**: Call `fulltext_search` with filters and `search_similar_notes` with a threshold; both return ranked results.

### Implementation for User Story 4

- [X] T024 [US4] Implement the `fulltext_search` tool handler with `types` and `date_range` filters in `src/impactite/mcp_tools.py`
- [X] T025 [US4] Implement the `search_similar_notes` tool handler using FTS overlap and Ladybug link/tag proximity in `src/impactite/mcp_tools.py`
- [X] T026 [US4] Register `fulltext_search` and `search_similar_notes` with the MCP server in `src/impactite/mcp_server.py`
- [X] T027 [US4] Validate US4 tools against the search and similarity scenarios in `specs/002-mcp-server/quickstart.md`

**Checkpoint**: User Stories 1–4 all work independently.

---

## Phase 7: User Story 5 — Analytics and relationship queries (Priority: P5)

**Goal**: External clients can request vault statistics, filter notes by date range, and retrieve notes linked to a project.

**Independent Test**: Call `get_note_statistics`, `find_notes_by_date_range`, and `get_notes_linked_to_project`; counts and identifiers are correct.

### Implementation for User Story 5

- [X] T028 [US5] Implement the `get_note_statistics` tool handler in `src/impactite/mcp_tools.py`
- [X] T029 [P] [US5] Implement the `find_notes_by_date_range` tool handler in `src/impactite/mcp_tools.py`
- [X] T030 [P] [US5] Implement the `get_notes_linked_to_project` tool handler using tag/link graph in `src/impactite/mcp_tools.py`
- [X] T031 [US5] Register analytics tools with the MCP server in `src/impactite/mcp_server.py`
- [X] T032 [US5] Validate US5 tools against the analytics scenarios in `specs/002-mcp-server/quickstart.md`

**Checkpoint**: All five user stories are independently functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Finalize code quality, validation, and documentation.

- [X] T033 [P] Add type annotations and docstrings to all public functions in `src/impactite/mcp_tools.py` and `src/impactite/mcp_server.py`
- [X] T034 [P] Run `uv run python -m compileall src` and fix any syntax errors introduced in `src/impactite/mcp_tools.py` or `src/impactite/mcp_server.py`
- [X] T035 Run the full validation checklist from `specs/002-mcp-server/quickstart.md` against the implemented MCP server
- [X] T036 [P] Update `README.md` with a short MCP usage section (`impactite --mcp <config>`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 completion. BLOCKS all user stories.
- **Phases 3–7 (User Stories)**: All depend on Phase 2 completion.
  - Stories can proceed in parallel if capacity allows.
  - Sequential order is P1 → P2 → P3 → P4 → P5.
- **Phase 8 (Polish)**: Depends on all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2. No dependencies on other stories.
- **US2 (P2)**: Can start after Phase 2. Optionally reuses `load_note` from foundational phase.
- **US3 (P3)**: Can start after Phase 2. Reuses note reading/filtering helpers from US1.
- **US4 (P4)**: Can start after Phase 2. Reuses index helpers; can be done in parallel with US3.
- **US5 (P5)**: Can start after Phase 2. Reuses note listing and graph-index helpers.

### Within Each User Story

- Foundational helpers before story-specific handlers.
- Tool handlers before registration in `mcp_server.py`.
- Registration before quickstart validation.

### Parallel Opportunities

- T002 and T003 (module creation) can run in parallel.
- T005–T008 (foundational helpers) can run in parallel once T004 is done.
- Within each user story, tool handlers marked [P] can run in parallel.
- Different user stories can be worked on in parallel after Phase 2 is complete.
- T033, T034, and T036 in Phase 8 can run in parallel.

---

## Parallel Example: User Story 1

```text
# Launch in parallel after Phase 2:
Task T010 [P] [US1] Implement list_notes in src/impactite/mcp_tools.py
Task T011 [US1] Implement search_notes in src/impactite/mcp_tools.py

# Then register and validate:
Task T012 [US1] Register read/search tools in src/impactite/mcp_server.py
Task T013 [US1] Validate US1 tools against quickstart.md
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: Test `get_note`, `list_notes`, and `search_notes` independently.
5. Continue to remaining stories only after US1 is solid.

### Incremental Delivery

1. Setup + Foundational → foundation ready.
2. US1 → test independently → MVP demo.
3. US2 → test independently.
4. US3 → test independently.
5. US4 → test independently.
6. US5 → test independently.
7. Phase 8 polish and documentation.

### Parallel Team Strategy

With multiple developers:

- Team completes Phase 1 and Phase 2 together.
- Once foundational helpers exist:
  - Developer A: US1 + US2
  - Developer B: US3 + US4
  - Developer C: US5 + documentation/polish
- Each story is validated independently before integration.

---

## Notes

- [P] tasks are parallelizable only when they touch different files and have no runtime dependency on incomplete tasks.
- All tasks reference explicit files in `src/impactite/`.
- No TUI code in `src/impactite/app.py` is changed except the `--mcp` entrypoint branch.
- Stop at any user-story checkpoint to validate independently against `specs/002-mcp-server/quickstart.md`.
