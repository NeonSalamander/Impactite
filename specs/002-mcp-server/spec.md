# Feature Specification: MCP Server Integration

**Feature Branch**: `002-mcp-server`

**Created**: 2026-06-15

**Status**: Draft

**Input**: User description: "Implement MCP server in the application with functions for reading notes, creating/updating notes, working with note types, full-text search, and analytics"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve note context (Priority: P1)

An external AI assistant needs to read existing notes and find the right content before answering a user question.

**Why this priority**: Without reliable read access, the assistant cannot ground its answers in the user's actual notes.

**Independent Test**: Give the assistant a note identifier and verify it receives the note content and metadata through the MCP interface.

**Acceptance Scenarios**:

1. **Given** a note exists in the vault, **when** the assistant requests it by identifier, **then** the system returns the note content and its type.
2. **Given** the assistant searches for a keyword, **when** results are returned, **then** each result contains enough context (title, snippet, identifier) to choose the right note.
3. **Given** the assistant filters by note type, **when** listing notes, **then** only notes of that type are returned.

---

### User Story 2 - Create and update notes (Priority: P2)

An external AI assistant needs to capture information without opening the editor — for example, after a conversation or as the result of analysis.

**Why this priority**: Programmatic creation removes friction and lets the assistant persist structured outputs directly.

**Independent Test**: Ask the assistant to create a note, then open the note in Impactite and confirm it exists with the correct type and content.

**Acceptance Scenarios**:

1. **Given** a supported note type, **when** the assistant creates a note with valid content, **then** a new note file appears in the vault.
2. **Given** an existing note, **when** the assistant updates its content, **then** the file is overwritten and changes are reflected in the UI after refresh.
3. **Given** a form-type note, **when** the assistant provides field values matching the schema, **then** the form fields are filled and saved.

---

### User Story 3 - Discover note types and schemas (Priority: P3)

An external AI assistant needs to know which note types exist and what fields each form expects before it can create notes correctly.

**Why this priority**: Type discovery prevents invalid creations and helps the assistant use the user's own organizational conventions.

**Independent Test**: Query available note types and a schema; verify the returned data matches the definitions configured in Impactite.

**Acceptance Scenarios**:

1. **Given** the vault contains several note types, **when** the assistant asks for the type list, **then** all types are returned.
2. **Given** a type name, **when** the assistant asks for its schema, **then** the schema lists required and optional fields.
3. **Given** a type name, **when** listing notes by type, **then** only matching notes are returned.

---

### User Story 4 - Search by content and similarity (Priority: P4)

An external AI assistant needs to find notes that are semantically or textually related to a question or to another note.

**Why this priority**: Full-text and similarity search turn the vault into a retrievable knowledge base for the assistant.

**Independent Test**: Run a keyword search and a similarity search against an existing note; both return a ranked list of related notes.

**Acceptance Scenarios**:

1. **Given** a query string, **when** the assistant performs full-text search, **then** matching notes are returned ranked by relevance.
2. **Given** an existing note identifier, **when** the assistant asks for similar notes, **then** it receives notes related by content or links above a configurable threshold.
3. **Given** optional type and date filters, **when** the assistant applies them, **then** results respect both criteria.

---

### User Story 5 - Analytics and relationship queries (Priority: P5)

An external AI assistant needs to answer questions about the vault as a whole — counts, recent activity, and project relationships.

**Why this priority**: Aggregate queries let the assistant summarize the user's knowledge base and track activity over time.

**Independent Test**: Request statistics, a date-range query, and project-linked notes; verify the counts and identifiers are accurate.

**Acceptance Scenarios**:

1. **Given** notes exist in the vault, **when** the assistant requests statistics, **then** it receives counts by type and totals.
2. **Given** a date range, **when** the assistant searches within it, **then** all notes created or modified in that range are returned.
3. **Given** a project identifier, **when** the assistant asks for linked notes, **then** all notes referencing that project are returned.

---

### Edge Cases

- What happens when the requested `note_id` does not exist?
- How does the system handle creation of a note with a type that is not defined?
- How does the system respond when `fill_form` receives field values that violate the type schema?
- What is returned when a full-text or similarity query yields no results?
- **Concurrent writes are resolved with optimistic concurrency**: an MCP `update_note` or `fill_form` operation is rejected if the target file was modified after the note was last read by the client.
- What happens when a date range is invalid (e.g., start after end)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a way for an external client to retrieve a single note by `note_id` (`get_note`).
- **FR-002**: The system MUST allow listing notes with optional filtering by type and other criteria (`list_notes`).
- **FR-003**: The system MUST support searching notes by query with an optional type filter (`search_notes`).
- **FR-004**: The system MUST allow creating a new note of a supported type with initial content (`create_note`).
- **FR-005**: The system MUST allow updating the content of an existing note (`update_note`).
- **FR-006**: The system MUST support filling a form-type note with structured data that conforms to the type schema (`fill_form`).
- **FR-007**: The system MUST expose the list of configured note types (`get_note_types`).
- **FR-008**: The system MUST expose the schema for any supported note type, including required and optional fields (`get_type_schema`).
- **FR-009**: The system MUST allow listing all notes of a specific type (`list_notes_by_type`).
- **FR-010**: The system MUST provide full-text search across note contents with optional type and date range filters (`fulltext_search`).
- **FR-011**: The system MUST support finding notes similar to a given note using a configurable similarity threshold. Similarity is computed from local full-text overlap and link/tag graph proximity (`search_similar_notes`).
- **FR-012**: The system MUST provide aggregate statistics about the vault (`get_note_statistics`).
- **FR-013**: The system MUST allow finding notes within a date range (`find_notes_by_date_range`).
- **FR-014**: The system MUST allow retrieving all notes linked to a given project or relationship identifier (`get_notes_linked_to_project`).
- **FR-015**: The system MUST reject an `update_note` or `fill_form` request when the target note was modified after it was last read by the requesting client (optimistic concurrency).

### Key Entities *(include if feature involves data)*

- **Note**: A Markdown file in the vault, identified by a stable `note_id` that equals the note's path relative to the notes root. Attributes include content, type, creation date, and modification date.
- **Note Type**: A template/schema definition that determines note structure. Attributes include type name, optional/required fields, and default content.
- **Form Data**: A mapping of field names to values used to populate a form-type note.
- **Project/Relationship Link**: A reference from a note to a project or another note, typically encoded through tags, frontmatter, or wiki-links.
- **Search Query**: A string or note identifier used to drive full-text or similarity search.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An external client retrieves any existing note in under 1 second when the vault contains up to 10,000 notes.
- **SC-002**: Full-text search returns ranked results in under 2 seconds for a vault of up to 10,000 notes.
- **SC-003**: Newly created or updated notes are persisted and discoverable by search within 3 seconds; index refresh happens asynchronously after the write returns.
- **SC-004**: At least 99% of syntactically valid MCP requests complete without an internal server error.
- **SC-005**: All configured note types and their schemas are discoverable, and schema requests resolve in under 500 milliseconds.
- **SC-006**: Similarity search returns results ranked by relevance threshold, with controls exposed to the external client.

## Assumptions

- The MCP server uses **stdio transport**: external clients launch Impactite as a subprocess and communicate over stdin/stdout.
- The MCP server operates on the same local notes directory as the Impactite application.
- No external network authentication is required; the integration is intended for local or trusted client access.
- Note identifiers are stable and equal the note's path relative to the notes root; clients reference notes by this relative path.
- Type definitions and templates are read from the same configuration and template directories as the UI.
- Write operations follow existing vault conventions: UTF-8 Markdown files, valid frontmatter, and index rebuild triggers.
- Similarity search uses local full-text overlap and link/tag graph proximity; it does not require external embedding services.
- Changes made through the MCP interface become visible to subsequent MCP searches within 3 seconds, after an asynchronous index refresh; UI visibility follows the existing refresh/index rebuild cycle.

## Clarifications

### Session 2026-06-15

- Q: Which MCP transport should the server expose? → A: stdio (Option A).
- Q: What should the canonical `note_id` format be? → A: relative file path from the notes root (Option A).
- Q: How should concurrent MCP/UI writes be resolved? → A: optimistic concurrency — reject writes when the file changed after the client's last read (Option B).
- Q: What should "similarity" mean for `search_similar_notes`? → A: local full-text overlap + link/tag graph proximity (Option A).
- Q: When should MCP writes become searchable? → A: asynchronously within 3 seconds (Option B).
