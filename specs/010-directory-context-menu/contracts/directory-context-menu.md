# UI Contract: Directory Context Menu

## User interaction contract

| Event | Source | Condition | Action |
|-------|--------|-----------|--------|
| Right-click (`MouseDown` button 3) | `FileTree` | Pointer is over a directory node (`node.data` is a `Path` and `is_dir()`) | Move cursor/selection to that node, set `selected_dir`, and open the context menu near the pointer. |
| Right-click (`MouseDown` button 3) | `FileTree` | Pointer is over a file, root, or empty area | Ignore; no menu is shown. |
| Left-click or click outside menu | `DirectoryContextMenu` overlay | Menu is visible and click is outside menu bounds | Dismiss the menu. |
| `Escape` key | `DirectoryContextMenu` | Menu is focused | Dismiss the menu. |
| Select "Directory settings" | `DirectoryContextMenu` | Target directory is a directory | Dismiss the menu and push `DirectoryColorModal` for the target directory. |
| Select "Reset color" | `DirectoryContextMenu` | Target directory is a directory | Call `Config.remove_directory_style(...)`, refresh the file tree, and dismiss the menu. |

## Tooltip/menu labels contract

All labels shown in the context menu are canonical English keys passed through `impactite.i18n.t`:

- `"Directory settings"` — opens the color settings dialog.
- `"Reset color"` — removes the custom colors for the directory.

## Dialog contract

The color dialog contract is unchanged from feature 009-directory-tree-colors:

- Input fields for background and text color.
- Current colors pre-filled when available.
- Confirmation validates both values and persist them via `Config.set_directory_style(...)`.
- Cancel leaves settings unchanged.
