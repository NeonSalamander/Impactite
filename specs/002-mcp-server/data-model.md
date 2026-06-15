# Data Model: MCP Server Integration

## Entities

### NoteRef

Represents a lightweight pointer to a note returned by list/search operations.

| Field | Type | Description |
|-------|------|-------------|
| `note_id` | `str` | Relative path from `notes_path` (canonical identifier) |
| `title` | `str` | Note title derived from the first heading or filename |
| `type` | `str \| None` | Note type name, if declared |
| `modified_at` | `int` | Last modification timestamp (Unix seconds) |

### Note

Full note representation used by `get_note` and write operations.

| Field | Type | Description |
|-------|------|-------------|
| `note_id` | `str` | Relative path from `notes_path` |
| `title` | `str` | Note title |
| `type` | `str \| None` | Note type |
| `content` | `str` | Raw Markdown content |
| `frontmatter` | `dict[str, Any]` | Parsed YAML frontmatter |
| `created_at` | `int \| None` | Creation timestamp when available |
| `modified_at` | `int` | Last modification timestamp |

### NoteTypeSchema

Schema description returned by `get_note_types` and `get_type_schema`.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Type identifier |
| `label` | `str` | Human-readable label |
| `fields` | `list[FieldSchema]` | Required and optional fields |
| `default_template` | `str \| None` | Markdown template used when creating a note of this type |

### FieldSchema

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Field key |
| `required` | `bool` | Whether the field must be present |
| `type` | `str` | Expected value type (`string`, `number`, `date`, `boolean`, `list`) |
| `description` | `str \| None` | Short human-readable description |

### SearchQuery

Internal representation of a search request.

| Field | Type | Description |
|-------|------|-------------|
| `query` | `str` | Search string or note_id |
| `type_filter` | `str \| None` | Optional note type filter |
| `date_range` | `tuple[int, int] \| None` | Optional (start, end) Unix timestamps |
| `similarity_threshold` | `float \| None` | Threshold for similarity search, 0.0–1.0 |

### SearchResult

| Field | Type | Description |
|-------|------|-------------|
| `note_id` | `str` | Matching note identifier |
| `title` | `str` | Note title |
| `type` | `str \| None` | Note type |
| `snippet` | `str` | Relevant excerpt or context |
| `score` | `float` | Relevance/similarity score |

### WriteResult

Result of `create_note`, `update_note`, or `fill_form`.

| Field | Type | Description |
|-------|------|-------------|
| `note_id` | `str` | Identifier of the affected note |
| `success` | `bool` | Whether the operation succeeded |
| `error_code` | `str \| None` | Stable error code when `success` is false |
| `error_message` | `str \| None` | Human-readable error description |

## State Transitions

```text
MCP request
    |
    v
Validation (note_id exists, type exists, form data matches schema)
    |
    +--> Invalid ----> WriteResult(success=False, error_code=..., error_message=...)
    |
    v
Operation (read / list / search / create / update / fill)
    |
    +--> Failure ----> WriteResult or error response
    |
    v
Success response (Note, list[NoteRef], list[SearchResult], WriteResult, or statistics)
```

## Validation Rules

- `note_id` must resolve to a path inside `notes_path`; paths attempting traversal (`..`) are rejected.
- `create_note` requires a `type` that exists in configured note types.
- `update_note`/`fill_form` reject with `stale_note` if the on-disk mtime is newer than the client’s `last_modified_at`.
- `fill_form` field values must match the declared field types in the schema; missing required fields are rejected.

## Error Codes

| Code | Meaning |
|------|---------|
| `note_not_found` | The requested `note_id` does not exist |
| `type_not_found` | The note type is not configured |
| `stale_note` | Optimistic concurrency conflict |
| `validation_error` | Form data does not match schema |
| `invalid_date_range` | Start timestamp is after end timestamp |
| `internal_error` | Unexpected server failure |
