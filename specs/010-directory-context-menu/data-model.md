# Data Model: Directory Context Menu

## Entities

### DirectoryColorPreference (managed by feature 009)

A pair of colors associated with a single directory path within the current vault.

| Field | Type | Description |
|-------|------|-------------|
| path | string | Directory path relative to `notes_path`, used as the storage key. |
| background | string | Color value for the directory row background. |
| text | string | Color value for the directory row label text. |

**Storage**: serialized under the `directory_colors` key in `config.yaml`.

### DirectoryContextMenuState

Transient UI state for the context menu currently on screen.

| Field | Type | Description |
|-------|------|-------------|
| target_path | Path | The directory path associated with the menu; used by actions. |
| menu_options | list[str] | Labels shown in the menu (e.g., "Directory settings", "Reset color"). |
| dismissed | bool | Becomes true once the menu closes. |

## Validation Rules

- A node is eligible for the context menu only when `node.data` is a `Path` and `path.is_dir()` is true.
- The "Reset" menu option is available for any directory; if no custom colors are stored, it is a no-op.
- Color validation inside the settings dialog follows the same rules as feature 009: both values must be present and must parse as valid colors.

## State Transitions

```text
Directory selected via right-click
        ↓
Context menu displayed near pointer
        ↓
┌──────────────┬─────────────────┐
▼              ▼                 ▼
"Settings"   "Reset"           Dismiss
        ↓              ↓              ↓
DirectoryColorModal   Config.remove...   Menu removed,
        ↓              refresh tree       no change
Confirm:
Config.set_directory_style
refresh tree
dismiss menu
```

## Relationships

- `DirectoryContextMenuState` references exactly one `DirectoryColorPreference` by path.
- `DirectoryColorPreference` entities continue to be owned and persisted by `Config` in `core.py`.
