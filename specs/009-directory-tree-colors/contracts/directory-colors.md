# Contract: Directory Colors

## Interface: Config Persistence

**Location**: `src/impactite/core.py` (`Config` class)

`directory_colors` is a top-level key in `config.yaml` mapping relative directory paths to color pairs.

```yaml
directory_colors:
  projects/work:
    background: "#2d2d2d"
    text: "#ffd700"
```

### Methods

- `Config.load(config_path: str) -> Config`  
  Loads `directory_colors` from YAML and defaults it to `{}` if absent.

- `Config.get_directory_style(rel_path: str) -> DirectoryStyle | None`  
  Returns the stored style for the given relative path, or `None` if none exists.

- `Config.set_directory_style(rel_path: str, background: str, text: str) -> None`  
  Validates the two colors, updates `directory_colors`, and writes the config back to disk.

- `Config.remove_directory_style(rel_path: str) -> None`  
  Removes the entry for the given path and writes the config back to disk.

### Preconditions

- `rel_path` uses forward slashes and is relative to the vault root.
- `background` and `text` are non-empty color strings accepted by Textual/Rich `Color.parse`.
- `config_path` exists or a new config can be created.

### Postconditions

- The YAML file round-trips without losing unrelated config values.
- Removed paths are no longer present in `directory_colors`.
- Invalid color strings result in an error and no config change.

---

## Interface: FileTree Rendering

**Location**: `src/impactite/app.py` (`FileTree` class)

`FileTree` receives the current directory style map when it is populated and applies colors while rendering labels.

### Method

- `FileTree.populate_tree(file_system: FileSystem, directory_styles: Dict[str, DirectoryStyle] | None = None, favorites: List[str] | None = None)`  
  Builds the tree and stores `directory_styles` for use during rendering.

- `FileTree.render_label(node: TreeNode, base_style: Style, style: Style) -> Text`  
  Overridden to look up the node's path in `directory_styles`. When a style exists, it applies the stored `background` and `text` colors to the rendered label.

### Preconditions

- The node corresponds to a directory whose path is stored in `dir_nodes`.
- `directory_styles` keys are relative paths matching the path used during tree construction.

### Postconditions

- Directory nodes with a stored style render with the configured background and text colors.
- Directory nodes without a stored style render with the default theme styling.
- File nodes and special nodes (favorites, link graph) are unaffected.

---

## Interface: Color Selection Modal

**Location**: `src/impactite/app.py` (`DirectoryColorModal` class)

A modal screen that returns either a color pair or `None` (cancelled).

### Signature

```text
DirectoryColorModal(
    title: str,
    current_background: str = "",
    current_text: str = "",
) -> ModalScreen[tuple[str, str] | None]
```

### Preconditions

- The calling screen is on the app stack.

### Postconditions

- On submit: returns `(background, text)` after both values pass validation.
- On cancel or invalid values: returns `None`.

---

## Interface: User Actions

**Location**: `src/impactite/app.py` (`MarkdownEditorApp` actions)

- `action_set_directory_color()`  
  Reads the currently selected directory from the file tree, opens `DirectoryColorModal`, and on success calls `Config.set_directory_style` and refreshes the tree.

- `action_reset_directory_color()`  
  Reads the currently selected directory, removes its style via `Config.remove_directory_style`, and refreshes the tree.

### Preconditions

- The selected node in `#file-tree` is a directory (or the root).
- The app has a loaded `Config` instance.

### Postconditions

- The config file is updated.
- The file tree is refreshed so the change is visible immediately.
- A notification confirms the action.
