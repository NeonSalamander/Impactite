# Research: File tree collapse after note creation

**Feature**: `020-preserve-tree-expansion`

## Code under investigation

`src/impactite/app.py`:

- `FileTree.populate_tree()` calls `self.clear()` and rebuilds every directory node with `expand=False`.
- `MarkdownEditorApp._refresh_file_tree()` calls `populate_tree()` after note creation, deletion, renaming, color changes, etc.
- `FileTree.selected_dir` stores the directory chosen for creating notes, but the visual tree node is not kept expanded.

## Reproduction

A headless test scenario:

1. Create a vault with a subdirectory, e.g. `notes/projects/`.
2. Launch `MarkdownEditorApp` with `App.run_test()`.
3. Expand the `projects` directory node.
4. Set `FileTree.selected_dir = projects_path`.
5. Call `_refresh_file_tree()`.

### Observed behaviour

After the refresh, the `projects` node is collapsed (`is_expanded == False`) even though `selected_dir` still points to it.

### Root cause

`populate_tree()` discards all existing nodes and creates new ones with default `expand=False`. There is no capture/restore of expansion state or selected directory.

### Fix direction

Before clearing the tree:

1. Walk existing directory nodes and collect paths where `node.is_expanded`.
2. Remember `selected_dir`.

After rebuilding:

1. Compute the set of directories that must be expanded, including all ancestors of any expanded or selected directory.
2. Expand the corresponding new nodes and re-select the selected directory node.

This keeps the fix self-contained inside `FileTree` and avoids special-casing note creation.
