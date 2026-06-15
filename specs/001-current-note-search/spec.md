# Feature Specification: Current Note In-Editor Search

|**Feature Branch**: `001-current-note-search`

|**Created**: 2026-06-15

|**Status**: Draft

|**Input**: User description: "Нужно добавить поиск по тексту текущей открытой заметки в режиме просмотра или редактирования, по свободному сочетанию клавишь например f7, диалоговое окно для ввода искомой строки не должно зачернять всю область под ним а только создавать эффект тени, кнопки для навигации по результатам поиска должны работать, можно использовать существующие так как сейчас они работают только для режима полнотекстового поиска"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open in-note search (Priority: P1)

As a user viewing or editing a note, I want to open a search dialog for the currently open note using a configurable hotkey so I can quickly locate a phrase without leaving the current document.

**Why this priority**: This is the core entry point for the feature; without it the remaining scenarios cannot be triggered.

**Independent Test**: Open any note, press the configured hotkey, and verify that a search input dialog appears.

**Acceptance Scenarios**:

1. **Given** the user has a note open in view or edit mode, **When** the user presses the configured hotkey, **Then** a search input dialog opens and focus moves to the search field.
2. **Given** the user has the search dialog open, **When** the user presses the close/cancel key, **Then** the dialog closes, search highlights are removed, and focus returns to the viewer or editor.

---

### User Story 2 - Find and highlight matches (Priority: P1)

As a user searching within a note, I want the current document to highlight all occurrences of my query so I can see where the phrase appears.

**Why this priority**: Highlights provide immediate visual feedback and are required before navigation can be validated.

**Independent Test**: Type a query in the search dialog and confirm that every matching substring in the current note is visually highlighted.

**Acceptance Scenarios**:

1. **Given** the search dialog is open and the current note contains the query text, **When** the user types the query, **Then** all matching occurrences in the current note are highlighted and the first match is automatically selected/scrolled into view.
2. **Given** the query has no matches in the current note, **When** the user finishes typing, **Then** an empty-state indication is shown and no previous highlights remain.

---

### User Story 3 - Navigate between matches (Priority: P2)

As a user reviewing search results, I want to step through matches using existing navigation controls so I can move between occurrences without learning new interactions.

**Why this priority**: Reusing existing navigation controls keeps the interaction consistent with the full-text search experience.

**Independent Test**: After a query returns multiple matches, use the previous/next result controls to move the selection through each occurrence.

**Acceptance Scenarios**:

1. **Given** multiple matches exist in the current note, **When** the user activates the next-result control, **Then** the highlight selection advances to the next match and the document scrolls so the match is visible.
2. **Given** the selection is on the last match, **When** the user activates the next-result control, **Then** the selection wraps to the first match (or a boundary message is shown, depending on product convention).

---

### User Story 4 - Non-obstructive dialog appearance (Priority: P2)

As a user searching while reading, I want the search dialog to appear as a compact overlay with a shadow effect rather than dimming the entire document, so I can still see the underlying note content.

**Why this priority**: The user explicitly requested this visual behavior to preserve context while searching.

**Independent Test**: Open the search dialog and visually confirm that the note text behind it remains readable and only the dialog area casts a shadow.

**Acceptance Scenarios**:

1. **Given** the search dialog is open over a note, **Then** the dialog background does not fully obscure the note text beneath it.
2. **Given** the dialog is displayed, **Then** a shadow effect visually separates the dialog from the note content.

---

### Edge Cases

- The current note is empty or has no text.
- The query is empty (cleared field).
- The query contains only whitespace.
- The user switches to another note while the search dialog is still open.
- The current match scrolls out of view and then the user navigates to the next/previous result.
- The user toggles between view and edit modes while a search is active.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: While a note is open in view mode or edit mode, the system MUST allow the user to open a dedicated search dialog for that note.
- **FR-002**: The search dialog MUST be activatable by a configurable hotkey; the default hotkey MUST be `F7`.
- **FR-003**: The search dialog MUST appear as a compact overlay and MUST NOT dim or fully obscure the note content behind it.
- **FR-004**: The search dialog MUST visually separate itself from the note content with a shadow effect.
- **FR-005**: As the user types a query, the system MUST highlight all matching substrings in the current note.
- **FR-006**: The search MUST be case-insensitive by default and match literal substrings.
- **FR-007**: The system MUST support stepping forward and backward through matches using the existing result-navigation controls.
- **FR-008**: When navigating matches, the system MUST scroll the selected match into view in both view and edit modes.
- **FR-009**: If the query yields no results, the system MUST display a clear empty-state indication.
- **FR-010**: Closing the search dialog MUST remove all highlights and return focus to the viewer or editor.

### Key Entities *(include if feature involves data)*

- **Current note content**: The text being viewed or edited; the target surface for search highlighting and navigation.
- **Search query**: The substring entered by the user to locate within the current note.
- **Match list**: The ordered set of occurrences of the query within the current note, used for navigation.
- **Selected match index**: The currently focused occurrence within the match list.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open the in-note search dialog within 1 second of pressing the configured hotkey.
- **SC-002**: Typing a query highlights matching occurrences in the current note within 500 milliseconds.
- **SC-003**: Navigating to the next or previous match scrolls the target occurrence into view within 500 milliseconds.
- **SC-004**: The search dialog covers no more than 20% of the vertical height of the note viewing area.
- **SC-005**: 95% of users can locate a desired phrase in a note of up to 10,000 words on the first attempt.

## Assumptions

- The default hotkey is `F7`, but it can be overridden through user configuration.
- Search is case-insensitive and literal (no regular expressions in the first version).
- Existing previous/next result controls are reused; their labels and positions remain unchanged.
- The feature applies to both view mode and edit mode for the currently active note.
- Notes are expected to be plain Markdown text loaded into memory when searched; performance targets apply to notes up to 10,000 words.
