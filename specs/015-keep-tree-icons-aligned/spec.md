# Feature Specification: Keep Tree Icons Aligned

|**Feature Branch**: `015-keep-tree-icons-aligned`

|**Created**: 2026-06-27

|**Status**: Draft

|**Input**: User description: "Нужно оставить пиктограммы для каталогов и избранного и всего остального как было, и убрать смещение которое было озвучено ранее"

|**Input**: User description: "в файле \"screen2.png\" посмотри как на четвертой строке экрана сбивается верстка на один символ". The file `screen2.png` is located in the project root and shows the reported one-character offset on the fourth visible row.

## Problem Statement

The directory tree uses small emoji pictograms (📁 folder, 📄 file, 📎 attachment, 🕸️ link graph, ⭐ favorites) so users can tell node types at a glance. A recent change replaced these pictograms with plain ASCII characters, which makes the tree harder to scan. The original emoji pictograms caused a one-character horizontal shift on some rows. The goal is to keep the exact original emoji pictograms while ensuring every row remains aligned in the terminal.

**Constraint**: The original emoji characters must not be replaced with different symbols.

## User Scenarios & Testing

### User Story 1 - Tree keeps pictograms and stays aligned (Priority: P1)

A user opens the directory tree. Directories, files, favorites, and the link graph still have recognizable small icons next to their names, and every row is horizontally aligned with the rows above and below it.

**Why this priority**: This directly addresses the user's request — keep icons as before and remove the shift.

**Independent Test**: Open the directory tree and visually confirm that all node icons are present and no row is shifted by one character.

**Acceptance Scenarios**:

1. **Given** the directory tree is visible, **When** the user looks at any row, **Then** a recognizable pictogram appears to the left of the label and the row is aligned with neighbouring rows.
2. **Given** a directory has custom foreground or background colour, **When** it is rendered, **Then** its row remains aligned and keeps its icon.

---

### User Story 2 - Pictogram alignment survives tree interactions (Priority: P2)

The user expands directories, collapses them, selects rows, or applies colours. Throughout all interactions, icons remain visible and rows stay aligned.

**Why this priority**: A fix that only works in the initial view would be unreliable.

**Independent Test**: Expand/collapse directories, select different rows, apply and reset directory colours, and confirm icons and alignment persist.

**Acceptance Scenarios**:

1. **Given** a directory with an icon is expanded, **When** its children appear, **Then** child rows (files and subdirectories) are also aligned and icon-prefixed.
2. **Given** a directory colour is set and then reset, **When** the tree re-renders, **Then** the icon and alignment are unchanged.

---

### Edge Cases

- The tree is scrolled; the "fourth visible row" may change, but every row in the viewport must be aligned.
- A node name contains non-ASCII or wide characters; the icon prefix must not introduce extra misalignment.
- The user switches between dark and light themes; icons and alignment remain consistent.

## Requirements

### Functional Requirements

- **FR-001**: The directory tree MUST use the exact original emoji pictograms as before: 📁 for directories, 📄 for Markdown files, 📎 for other files, 🕸️ for the link graph, and ⭐ for favorites.
- **FR-002**: Emoji pictograms MUST NOT cause any visible row to be shifted horizontally by one character.
- **FR-003**: Emoji pictograms MUST occupy a consistent number of terminal cells in any standard terminal.
- **FR-004**: Custom directory colours MUST continue to work and MUST NOT affect row alignment.
- **FR-005**: Expand, collapse, selection, scroll, and theme switch MUST preserve alignment and icons.
- **FR-006**: Headless smoke tests MUST continue to pass.

### Key Entities

- None. This is a rendering-only change; no data or persistence is involved.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In a screenshot or manual check, every visible tree row has an icon and is horizontally aligned with its neighbours.
- **SC-002**: No visible row is shifted by one character after expanding, collapsing, applying colour, selecting, or switching theme.
- **SC-003**: Headless application launch and tree-population tests continue to pass.

## Assumptions

- The original emoji characters are the only symbols allowed; no fallback or replacement glyphs may be introduced.
- In a standard terminal, the original emoji characters occupy two terminal cells each, and the rendering library is aware of this width.
- Any remaining shift is caused by how the label is assembled around the emoji, not by the emoji itself, and can be corrected without changing the emoji character.
