# Research Notes: MCP Server Integration

## Decision: MCP Transport

- **Decision**: stdio transport.
- **Rationale**: The feature specification and project constitution both require local, single-user operation without exposing network ports or web frameworks. stdio is the simplest MCP transport for a local TUI tool launched by a desktop LLM client.
- **Alternatives considered**: SSE over HTTP (would require a local server), HTTP endpoints (same issue). Both conflict with the constitution’s prohibition on web frameworks and add operational complexity.

## Decision: MCP Protocol Library

- **Decision**: Use the official `mcp` Python SDK (`pip install mcp`).
- **Rationale**: It provides `Server`, `@server.call_tool()`, `@server.list_tools()`, and `stdio_server`, handling JSON-RPC framing, lifecycle, and schema validation so we can focus on tool logic.
- **Alternatives considered**: Implementing the protocol manually. Rejected because parsing JSON-RPC over stdio, request IDs, and lifecycle messages is error-prone and would duplicate a stable reference implementation.
- **Implication**: Add `mcp` as a runtime dependency in `pyproject.toml`.

## Decision: Note Identifier Format

- **Decision**: `note_id` is the relative path from `notes_path`.
- **Rationale**: Files in the vault already have unique paths; using the relative path removes the need for a separate ID registry and keeps identifiers human-readable and portable.
- **Validation**: Existing `FileSystem` methods already work with relative paths; the core layer can resolve them absolutely.

## Decision: Concurrent Write Strategy

- **Decision**: Optimistic concurrency using file modification time.
- **Rationale**: Prevents silent overwrites when both the TUI editor and an MCP client modify a note. The client must re-read and retry on conflict.
- **Implementation idea**: Tool handlers accept an optional `last_modified_at` (mtime) argument; `update_note`/`fill_form` reject if on-disk mtime differs.

## Decision: Similarity Search Algorithm

- **Decision**: Combine existing full-text overlap (FTS5) with tag/link graph proximity (LadybugDB).
- **Rationale**: Keeps the feature self-contained and offline; no external embedding model or service is required.
- **Scoring idea**: Rank candidates by a weighted mix of FTS match score, shared tags, and wiki-link distance to the source note. The client supplies a threshold to filter low-scoring results.

## Decision: Asynchronous Index Refresh

- **Decision**: After each successful write, mark indexes as dirty and refresh them in a background task within 3 seconds.
- **Rationale**: Meets SC-003 without blocking the MCP response; matches current application behavior where indexes can be rebuilt on demand.

## Decision: Entrypoint for Server Mode

- **Decision**: Add `--mcp` flag to the existing `impactite` CLI entrypoint; when present, start the MCP server instead of the TUI.
- **Rationale**: External clients already launch the process; a flag avoids adding a separate entry point and keeps packaging simple.
- **Implication**: Minimal change to `app.py` main function; server mode does not mount the Textual UI.

## Decision: Error Handling Strategy

- **Decision**: Tool handlers return structured MCP errors (e.g., `note_not_found`, `type_not_found`, `stale_note`, `validation_error`) with plain-English messages. Unexpected exceptions are logged and mapped to an `internal_error` response without leaking stack traces.
- **Rationale**: Provides actionable feedback to the LLM client while protecting internal details and respecting the constitution’s graceful error-handling requirement.
