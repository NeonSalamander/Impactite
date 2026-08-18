# Feature Specification: Preserve file tree expansion when creating notes

**Feature Branch**: `020-preserve-tree-expansion`

**Created**: 2026-08-18

**Status**: Done

**Input**: User description: "при создании заметки после открытия поля для редактирования заметки схлопывается каталоги в левой части которые были выбраны для сохранения заметки"

## Problem Statement

When the user creates a new note inside a previously selected directory, the left sidebar file tree is rebuilt after the operation. The rebuild discards the expansion state of directory nodes, so the directory that was selected as the save location (and any other directories the user had expanded) collapses. The user has to re-expand the tree to see the newly created note or to continue working with the same folder.

## User Scenarios & Testing

### User Story 1 - Selected directory stays expanded after creating a note (Priority: P1)

A user selects a directory in the file tree, clicks the "Create note" button, enters a name, and confirms. After the new note opens in the editor, the selected directory in the file tree remains expanded and the new note is visible inside it.

**Why this priority**: This is the exact scenario reported by the user.

**Independent Test**: Expand a directory, create a note in it via the UI, and verify the directory is still expanded after the tree refreshes.

**Acceptance Scenarios**:

1. **Given** a directory is expanded and selected in the file tree, **When** the user creates a note in that directory, **Then** the directory stays expanded after creation.
2. **Given** the same scenario, **When** the new note is created, **Then** the directory node remains selected.

---

### User Story 2 - Other expanded directories stay expanded (Priority: P2)

A user has expanded several directories in the file tree. They create a note in one of them. After the tree refreshes, all previously expanded directories remain expanded.

**Why this priority**: Rebuilding the tree should not punish the user for having explored the folder structure.

**Independent Test**: Expand multiple directories, create a note in one, and verify all expanded directories are still expanded.

**Acceptance Scenarios**:

1. **Given** several directories are expanded, **When** a note is created, **Then** every previously expanded directory is still expanded.

---

### User Story 3 - Collapsed directories stay collapsed (Priority: P3)

Directories that were collapsed before the refresh remain collapsed after the refresh.

**Why this priority**: Preserving expansion state is a two-way contract; we should not auto-expand folders the user intentionally collapsed.

**Independent Test**: Ensure that a collapsed sibling directory is still collapsed after creating a note in another directory.

**Acceptance Scenarios**:

1. **Given** a sibling directory is collapsed, **When** a note is created elsewhere, **Then** that sibling directory remains collapsed.

---

### Edge Cases

- The selected directory is the vault root. The root is always expanded.
- A directory is deleted or renamed between refreshes. Its saved expansion state is silently ignored.
- The tree is refreshed for reasons other than note creation (for example, after setting a directory color). Expansion state is still preserved.
- The selected directory is deeply nested. All of its ancestor directories are expanded so that it remains visible.

## Requirements

### Functional Requirements

- **FR-001**: `FileTree.populate_tree` MUST preserve the expansion state of directory nodes across tree rebuilds.
- **FR-002**: The directory currently selected as the save location (`selected_dir`) MUST remain expanded after a refresh.
- **FR-003**: The selected directory node SHOULD remain selected after a refresh when it still exists.
- **FR-004**: Collapsed directories MUST NOT be auto-expanded by the preservation logic.
- **FR-005**: Preservation MUST apply to any tree refresh, not only to note creation.

### Key Entities

- **FileTree**: The Textual `Tree` subclass that renders the left sidebar.
- **Directory node**: A node in `FileTree` that represents a directory and carries a `Path` in its `data`.
- **selected_dir**: The `Path` stored in `FileTree` that determines where new notes/folders are created.
- **Expansion state**: The set of directory paths whose tree nodes are currently `is_expanded == True`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A headless test that expands a directory, creates a note inside it, and refreshes the tree passes; the directory node is expanded after the refresh.
- **SC-002**: A headless test with multiple expanded directories passes; all remain expanded after refresh.
- **SC-003**: A headless test with a collapsed sibling directory passes; it remains collapsed after refresh.
- **SC-004**: `python -m compileall src` and the relevant UI tests pass after the change.

## Assumptions

- The file tree is small enough that walking all directory nodes on refresh is cheap.
- Directory paths are unique within a single vault.
- The root node of the tree is always expanded and is not represented by a directory node.
