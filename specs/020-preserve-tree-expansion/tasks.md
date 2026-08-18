# Tasks: Preserve file tree expansion when creating notes

**Input**: Design documents from `specs/020-preserve-tree-expansion/`

**Prerequisites**: plan.md, spec.md, research.md

## Phase 0 — Reproduce & lock behaviour

- [x] T001 Read `FileTree` and `_refresh_file_tree` in `src/impactite/app.py`.
- [x] T002 Write a failing headless test that expands a directory, refreshes the tree, and asserts the directory is still expanded.

## Phase 1 — Implement preservation

- [x] T003 Add helper methods to `FileTree` in `src/impactite/app.py`:
  - `_collect_expanded_dir_paths()` — return a set of directory paths that are currently expanded.
  - `_ancestor_paths(path)` — return all directory paths from the vault root down to and including `path`.
  - `_restore_expansion(expanded_paths, selected_path)` — expand all directories that were expanded or are selected, and re-select the selected directory node.
- [x] T004 Update `FileTree.populate_tree()` to capture expansion/selection state before `self.clear()` and restore it after rebuilding the tree.
- [x] T005 Set `FileTree.auto_expand = False` so selecting a directory node does not toggle its expansion state.

## Phase 2 — Validation

- [x] T006 Run the failing regression test and verify it passes.
- [x] T007 Add tests for multiple expanded directories and for a collapsed sibling directory.
- [x] T008 Run `python -m compileall src`.
- [x] T009 Run `uv run python test_tree_expansion.py`.
- [x] T010 Revert any unintended changes to workspace `config.yaml`.
