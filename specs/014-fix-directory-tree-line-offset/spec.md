# Feature Specification: Fix Directory Tree Line Offset

|**Feature Branch**: `014-fix-directory-tree-line-offset`

|**Created**: 2026-06-27

|**Status**: Draft

|**Input**: User description: "в файле \"screen2.png\" посмотри как на четвертой строке экрана сбивается верстка на один символ"

## Problem Statement

In the directory-tree view, one of the rendered lines (specifically around the fourth visible line) is shifted horizontally by one character, breaking the vertical alignment of guide characters, icons, or directory names. The rest of the tree appears aligned correctly, indicating a localised rendering issue rather than a global layout problem.

## User Scenarios & Testing

### User Story 1 - Tree lines stay aligned at every row (Priority: P1)

A user is browsing the directory tree. Every row, including the fourth visible row, lines up vertically with its neighbours so guide characters and icons do not appear shifted.

**Why this priority**: A one-character offset makes the tree look broken and can mislead the user about the hierarchy depth of the item.

**Independent Test**: Open the directory tree and visually confirm that guide/tree lines are aligned on every row, especially around the fourth visible line.

**Acceptance Scenarios**:

1. **Given** the directory tree shows several directories, **When** the user looks at the fourth visible line, **Then** its leading guides, icons, and label are horizontally aligned with the rows above and below it.
2. **Given** a directory has custom colours or style applied, **When** it is rendered, **Then** the styling does not shift its row by one character.

---

### User Story 2 - Rendering remains aligned when tree state changes (Priority: P2)

The alignment is preserved when rows are expanded, collapsed, selected, or coloured.

**Why this priority**: If the offset only appears in a specific state (selected, expanded, coloured), the root cause must be located and fixed so the fix is reliable.

**Independent Test**: Toggle expand/collapse, select different rows, and apply/reset directory colours; confirm alignment holds.

**Acceptance Scenarios**:

1. **Given** a directory with custom colour is expanded or collapsed, **When** its row is re-rendered, **Then** it stays aligned with sibling rows.
2. **Given** the selected row changes, **When** the highlight moves, **Then** no row shifts by one character.

---

### Edge Cases

- The tree is scrolled so that the "fourth visible line" might be different rows at different scroll positions; the fix must apply to all rows in the tree, not just a specific absolute index.
- A directory name contains non-ASCII or wide characters; the row must still align correctly.
- The user applies both foreground and background colours to a directory; the row must not shift.
- The tree is rendered with a light or a dark theme; alignment is preserved.

## Requirements

### Functional Requirements

- **FR-001**: Every row in the directory tree MUST render with consistent horizontal alignment of leading guides, expand/collapse icons, and labels.
- **FR-002**: Custom directory styling (foreground/background colours) MUST NOT introduce a one-character shift in any row.
- **FR-003**: Row alignment MUST remain correct after expand/collapse, selection change, scroll, or theme switch.
- **FR-004**: The fix MUST NOT visibly regress other rows or other widgets on the screen.
- **FR-005**: Headless smoke tests MUST continue to pass.

### Key Entities

- None. This is a rendering fix in the tree widget; no data or persistence is involved.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In a screenshot or manual check, all directory-tree rows appear aligned; no row is visibly shifted by one character.
- **SC-002**: Alignment is preserved after applying/removing directory colours, expanding/collapsing directories, and switching themes.
- **SC-003**: Application smoke tests and tree-related headless checks continue to pass.

## Assumptions

- The offset is caused by custom rendering code in the directory tree widget rather than a Textual core bug.
- The screenshot refers to a row that appears fourth from the top in the current viewport; the fix will be made row-agnostic, not hard-coded to index 4.
- The terminal exposes standard cell-based rendering; no special handling is needed for graphical terminal quirks.
