# Implementation Plan: MCP Server Integration

**Branch**: `002-mcp-server` | **Date**: 2026-06-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-mcp-server/spec.md`

## Summary

Add an MCP-compatible server layer to Impactite so that external AI assistants can read notes, create and update notes, discover note types/schemas, run full-text/similarity searches, and perform analytics queries. The server uses stdio transport, treats note identifiers as relative vault paths, and delegates data operations to the existing `FileSystem`, `TagIndex`, and `FullTextIndex` subsystems.

## Technical Context

| Item | Value |
|------|-------|
| Language / Version | Python 3.14+ |
| Primary Dependencies | `textual[syntax]`, `rich`, `markdown`, `pygments`, `pyyaml`, `jinja2`, `ladybug`, plus the official `mcp` Python SDK for protocol handling |
| Storage | Plain UTF-8 Markdown files in `notes_path`; disposable indexes `.ladybug_index.lbug` and `.impactite_fts.db` |
| Testing | `pytest` for core MCP tool handlers; manual validation via an MCP client over stdio |
| Target Platform | Local Linux/Unix desktop environment where Impactite already runs |
| Project Type | Console TUI application extended with an MCP stdio server mode |
| Performance Goals | Read note <1s, full-text search <2s, schema requests <500ms for up to 10k notes; writes searchable within 3s |
| Constraints | No web frameworks; keep core MCP tool logic free of Textual/App imports; UTF-8 + pathlib for I/O; indexes must remain disposable/rebuildable |
| Scale / Scope | Personal/local vaults up to ~10,000 notes; single-user local access |

## Constitution Check

| Gate | Status | Notes |
|------|--------|-------|
| No web/native UI frameworks introduced | PASS | MCP server uses stdio and the official `mcp` SDK, not HTTP/REST/Electron/Qt/React |
| New dependency declared in `pyproject.toml` | PASS | `mcp` package to be added with rationale in commit message |
| UI code remains in `app.py`, core logic separate | PASS | MCP tool handlers go in a new core module (`mcp_tools.py`); server runner in `mcp_server.py`; no widget calls from core |
| File I/O uses `pathlib.Path`, UTF-8, robust error handling | PASS | Reuses existing `FileSystem`; new code follows same conventions |
| Indexes remain disposable/rebuildable | PASS | Writes trigger asynchronous rebuild of existing FTS/Ladybug indexes |
| Core logic stays unit-testable without Textual | PASS | Tool handlers accept `FileSystem`/`TagIndex`/`FullTextIndex` and return plain data structures |
| User-facing strings use i18n keys | PASS | New TUI/error strings use `impactite.i18n.t`; MCP protocol messages are API-facing and use fixed English keys |
| No unjustified architectural violations | PASS | — |

## Project Structure

### Documentation (this feature)

```text
specs/002-mcp-server/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (speckit-tasks)
```

### Source Code (repository root)

```text
src/impactite/
├── __init__.py
├── app.py               # Textual UI; receives --mcp flag handling only at entrypoint level
├── core.py              # Config, FileSystem, TagIndex, FullTextIndex, QueryEngine
├── mcp_tools.py         # Pure tool handler functions (core/business logic)
├── mcp_server.py        # MCP Server lifecycle, tool registration, stdio transport
├── i18n.py              # Existing localization
├── table_engine.py      # Existing formula engine
└── templater.py         # Existing template renderer

tests/
└── test_mcp_tools.py    # Unit tests for tool handlers
```

**Structure Decision**: Add two small modules (`mcp_tools.py` for business logic, `mcp_server.py` for protocol wiring) and a `--mcp` entrypoint path. The TUI code in `app.py` is not modified for normal usage; only the `main()` entry path branches to server mode.

## Complexity Tracking

No constitution violations requiring justification.
