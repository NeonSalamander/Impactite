# Quickstart: MCP Server Validation

This guide describes how to verify the MCP server integration end-to-end after implementation.

## Prerequisites

- Python 3.14+ environment managed by `uv`.
- `pyproject.toml` updated to include the `mcp` package dependency.
- A test vault directory with a few Markdown notes (e.g., `samples/`).
- A config file pointing at the test vault.

## Launch the server

Run Impactite in MCP mode:

```bash
cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
uv run impactite --mcp samples/config.yaml
```

The process should start reading JSON-RPC messages from stdin and writing responses to stdout. It must not open the TUI in this mode.

## Validate tool listing

Send a `tools/list` request:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

**Expected outcome**: Response contains all 14 tools defined in [contracts/mcp-tools.md](contracts/mcp-tools.md): `get_note`, `list_notes`, `search_notes`, `create_note`, `update_note`, `fill_form`, `get_note_types`, `get_type_schema`, `list_notes_by_type`, `fulltext_search`, `search_similar_notes`, `get_note_statistics`, `find_notes_by_date_range`, `get_notes_linked_to_project`.

## Validate reading a note

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_note",
    "arguments": {
      "note_id": "cheatsheet.md"
    }
  }
}
```

**Expected outcome**: JSON response with `note_id`, `title`, `type`, and `content` matching the file contents.

## Validate search

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "fulltext_search",
    "arguments": {
      "query": "markdown"
    }
  }
}
```

**Expected outcome**: A list of matching notes. Each result has `note_id`, `title`, `snippet`, and a non-negative `score`.

## Validate create + find

1. Call `create_note` with a supported type and content.
2. Confirm the file exists in the vault.
3. Call `list_notes_by_type` with the same type.

**Expected outcome**: The newly created note appears in the listing within 3 seconds.

## Validate optimistic concurrency

1. Call `get_note` and record `modified_at`.
2. Modify the file externally or through the TUI.
3. Call `update_note` with the original `last_modified_at`.

**Expected outcome**: Response has `success: false` and `error_code: "stale_note"`.

## Performance checks

Against a vault of ~10,000 notes:

- `get_note` returns in under 1 second.
- `fulltext_search` returns in under 2 seconds.
- `get_note_types` and `get_type_schema` return in under 500 milliseconds.

## Cleanup

Stop the server by closing stdin. Verify that no new long-lived background threads remain and that `.impactite_fts.db` and `.ladybug_index.lbug` remain disposable (can be deleted and rebuilt on next run).
