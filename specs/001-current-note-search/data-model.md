# Data Model: Current Note In-Editor Search

## Entities

### SearchState

Represents the transient state of an active in-note search while a note is open.

| Field | Type | Description |
|-------|------|-------------|
| `query` | `str` | The current query string entered by the user. |
| `matches` | `List[Match]` | Ordered list of all found occurrences in the current note. |
| `current_index` | `int` | Zero-based index of the currently selected match; `-1` when no matches exist. |
| `is_active` | `bool` | Whether a search session is currently open. |

### Match

Represents a single occurrence of the query in the note.

| Field | Type | Description |
|-------|------|-------------|
| `start` | `int` | Absolute character offset of the match start in the document. |
| `end` | `int` | Absolute character offset immediately after the match end. |
| `line` | `int` | Line number (0-based) where the match begins. |
| `column` | `int` | Column number (0-based) where the match begins on the line. |

## Validation Rules

- `query` may be empty; when empty, `matches` is empty and `current_index` is `-1`.
- `current_index` is valid only when `0 <= current_index < len(matches)`.
- `start` < `end` for every match.
- Matches do not overlap for literal substring search.

## State Transitions

```
Idle
  │ hotkey
  ▼
Searching ──query changed──► Searching (matches recomputed)
  │
  │ next / prev
  ▼
Searching (current_index updated, view/editor scrolled)
  │
  │ close
  ▼
Idle (SearchState cleared)
```

## Relationships

- `SearchState` has a many-to-one relationship with the current note content (the plain Markdown text being viewed or edited).
- `MarkdownEditorApp` owns zero or one `SearchState` instances per open note session.
- `MarkdownViewer` and `EditorTextArea` consume the current `SearchState` to render highlights and scroll positions.
