# MCP Tools Contract

This document defines the tools exposed by the Impactite MCP server.
All tool names, parameters, and result shapes are part of the public contract with external clients.

## Tool: `get_note`

Read a single note.

**Parameters**:
```json
{
  "note_id": "string, relative path from notes_path"
}
```

**Result on success**:
```json
{
  "note_id": "string",
  "title": "string",
  "type": "string | null",
  "content": "string (Markdown)",
  "frontmatter": "object",
  "created_at": "number | null",
  "modified_at": "number"
}
```

**Error codes**: `note_not_found`, `internal_error`

---

## Tool: `list_notes`

List notes with optional filters.

**Parameters**:
```json
{
  "filter": "string | null, substring matched against path or title",
  "type": "string | null"
}
```

**Result on success**:
```json
{
  "notes": [
    {
      "note_id": "string",
      "title": "string",
      "type": "string | null",
      "modified_at": "number"
    }
  ]
}
```

---

## Tool: `search_notes`

Search notes by query with optional type filter.

**Parameters**:
```json
{
  "query": "string",
  "type_filter": "string | null"
}
```

**Result on success**:
```json
{
  "results": [
    {
      "note_id": "string",
      "title": "string",
      "type": "string | null",
      "snippet": "string",
      "score": "number"
    }
  ]
}
```

---

## Tool: `create_note`

Create a new note.

**Parameters**:
```json
{
  "type": "string",
  "content": "string (Markdown)",
  "note_id": "string | null, relative path; if omitted, derived from title/type"
}
```

**Result on success**:
```json
{
  "note_id": "string",
  "success": true,
  "error_code": null,
  "error_message": null
}
```

**Error codes**: `type_not_found`, `internal_error`

---

## Tool: `update_note`

Replace the content of an existing note.

**Parameters**:
```json
{
  "note_id": "string",
  "content": "string",
  "last_modified_at": "number | null"
}
```

**Result on success**:
```json
{
  "note_id": "string",
  "success": true,
  "error_code": null,
  "error_message": null
}
```

**Error codes**: `note_not_found`, `stale_note`, `internal_error`

---

## Tool: `fill_form`

Fill fields of a form-type note.

**Parameters**:
```json
{
  "note_id": "string",
  "form_data": "object",
  "last_modified_at": "number | null"
}
```

**Result on success**:
```json
{
  "note_id": "string",
  "success": true,
  "error_code": null,
  "error_message": null
}
```

**Error codes**: `note_not_found`, `stale_note`, `validation_error`, `internal_error`

---

## Tool: `get_note_types`

List all configured note types.

**Parameters**: none

**Result on success**:
```json
{
  "types": [
    {
      "name": "string",
      "label": "string"
    }
  ]
}
```

---

## Tool: `get_type_schema`

Return the schema of a single note type.

**Parameters**:
```json
{
  "type_name": "string"
}
```

**Result on success**:
```json
{
  "name": "string",
  "label": "string",
  "fields": [
    {
      "name": "string",
      "required": true,
      "type": "string",
      "description": "string | null"
    }
  ],
  "default_template": "string | null"
}
```

**Error codes**: `type_not_found`

---

## Tool: `list_notes_by_type`

Return all notes of a specific type.

**Parameters**:
```json
{
  "type": "string"
}
```

**Result on success**: same shape as `list_notes`.

**Error codes**: `type_not_found`

---

## Tool: `fulltext_search`

Full-text search with optional type and date filters.

**Parameters**:
```json
{
  "query": "string",
  "types": ["string"],
  "date_range": {
    "start": "number | null",
    "end": "number | null"
  }
}
```

**Result on success**: same shape as `search_notes`.

**Error codes**: `invalid_date_range`

---

## Tool: `search_similar_notes`

Find notes similar to a given note.

**Parameters**:
```json
{
  "note_id": "string",
  "similarity_threshold": "number, 0.0–1.0"
}
```

**Result on success**: same shape as `search_notes`.

**Error codes**: `note_not_found`

---

## Tool: `get_note_statistics`

Vault-level statistics.

**Parameters**: none

**Result on success**:
```json
{
  "total_notes": "number",
  "by_type": {
    "type_name": "number"
  }
}
```

---

## Tool: `find_notes_by_date_range`

Return notes created or modified within a date range.

**Parameters**:
```json
{
  "start": "number",
  "end": "number"
}
```

**Result on success**: same shape as `list_notes`.

**Error codes**: `invalid_date_range`

---

## Tool: `get_notes_linked_to_project`

Return notes that reference a project or relationship identifier.

**Parameters**:
```json
{
  "project_id": "string"
}
```

**Result on success**: same shape as `list_notes`.
