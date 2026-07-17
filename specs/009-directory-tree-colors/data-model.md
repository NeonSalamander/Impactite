# Data Model: Directory Tree Colors

## Entities

### `DirectoryStyle`

A pure data object representing the colors assigned to one directory.

| Field | Type | Description |
|-------|------|-------------|
| `path` | `str` | Directory path relative to the vault root, using forward slashes (e.g., `"projects/work"`) |
| `background` | `str` | Background color string validated by `Color.parse` (e.g., `"#ff0000"`, `"red"`) |
| `text` | `str` | Text/label color string validated by `Color.parse` (e.g., `"#ffffff"`, `"white"`) |

### `Config.directory_colors`

A dict stored under the top-level `directory_colors` key in `config.yaml`.

| Field | Type | Description |
|-------|------|-------------|
| `directory_colors` | `Dict[str, Dict[str, str]]` | Mapping of relative directory path → `{ "background": str, "text": str }` |

Default value is `{}`. The dict is loaded alongside other `Config` defaults and persisted back to YAML when changed.

### `FileTree.directory_styles`

Runtime mapping held by the `FileTree` widget while it is populated.

| Field | Type | Description |
|-------|------|-------------|
| `directory_styles` | `Dict[str, DirectoryStyle]` | Relative path → `DirectoryStyle`, passed from `Config` during tree refresh |

This mapping is consulted by `FileTree.render_label` and/or `_render_line` to apply the stored colors.

## Invariants

- The relative path key is computed from `child.path.relative_to(file_system.root_path)` using forward-slash separators.
- If `directory_colors` contains a path that no longer exists, the entry is ignored at render time and may be pruned on a subsequent save.
- Color strings must be valid according to Textual/Rich `Color.parse`; invalid values cannot be persisted.
- No directory inherits colors from its parent unless a separate entry exists for that child path.
- Resetting a directory removes its key from `Config.directory_colors` entirely, restoring default tree styling.
