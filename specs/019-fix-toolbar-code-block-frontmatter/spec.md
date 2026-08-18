# Feature Specification: Fix toolbar code block insertion inside frontmatter

**Feature Branch**: `019-fix-toolbar-code-block-frontmatter`

**Created**: 2026-08-18

**Status**: Done

**Input**: User description: "при создании заметки при добавлении блока кода через кнопку пустой блок кода полявляется не в месте курсора а обрамляет заполненный фронтматтер"

## Problem Statement

When a new note is created (for example a daily note), the editor cursor starts at the beginning of the file, inside or directly before the YAML frontmatter. Pressing the editor toolbar "code block" button (` ``` `) with no text selected inserts an empty fenced code block at the cursor position. Because the cursor is inside the frontmatter, the inserted fence breaks the frontmatter: it either lands in front of it or turns it into a code block. The expected behaviour is to insert the empty code block after the frontmatter, preserving the note metadata.

## User Scenarios & Testing

### User Story 1 - Code block skips frontmatter on new notes (Priority: P1)

A user creates a new daily note or a note from a template. The note contains a YAML frontmatter block. Without moving the cursor, the user clicks the toolbar "code block" button. The empty code block is inserted after the frontmatter, not before or inside it.

**Why this priority**: This directly fixes the reported bug and preserves the integrity of note metadata on the most common trigger path.

**Independent Test**: Start the application, create a daily note, click the toolbar code-block button, and verify the frontmatter remains valid and the code block appears after it.

**Acceptance Scenarios**:

1. **Given** a newly created note with frontmatter, **When** the user clicks the toolbar code-block button with no selection, **Then** an empty fenced code block is inserted after the frontmatter.
2. **Given** the same scenario, **When** the note is saved and reopened, **Then** the frontmatter is still parsed correctly.

---

### User Story 2 - Existing selection is still wrapped (Priority: P2)

A user selects some text inside the editor (including text inside the frontmatter) and clicks the toolbar code-block button. The selected text is wrapped with code fences at the selection boundaries, exactly as before.

**Why this priority**: The bug fix must not remove the existing "wrap selection" behaviour that users rely on.

**Independent Test**: Open a note, select a paragraph, click the toolbar code-block button, and verify the selected text is wrapped.

**Acceptance Scenarios**:

1. **Given** a non-empty selection in the editor, **When** the toolbar code-block button is clicked, **Then** the selected text is replaced with the same text wrapped in ` ``` ` fences.

---

### User Story 3 - Notes without frontmatter are unaffected (Priority: P3)

A user opens a plain note without YAML frontmatter and clicks the toolbar code-block button. The empty code block is inserted at the current cursor position as it was before.

**Why this priority**: Frontmatter-aware behaviour should not change normal editing flow for notes that have no frontmatter.

**Independent Test**: Open a note that starts with a heading instead of `---`, place the cursor in the middle, click the toolbar code-block button, and verify insertion happens at the cursor.

**Acceptance Scenarios**:

1. **Given** a note without frontmatter and a cursor at a known position, **When** the toolbar code-block button is clicked, **Then** the empty code block is inserted at that position.

---

### Edge Cases

- The cursor is inside the frontmatter value area (for example on the `type:` line). The insertion must still move after the frontmatter.
- The frontmatter is not closed (only an opening `---`). The function must not move the cursor, because there is no safe boundary.
- The document consists only of frontmatter followed by blank lines. The code block is appended at the end of the document.
- The note has content after the frontmatter. The code block is inserted before that content, immediately after the frontmatter.
- Horizontal-rule and other toolbar buttons are out of scope for this fix; only the code-block button changes.

## Requirements

### Functional Requirements

- **FR-001**: The toolbar code-block button MUST NOT insert an empty fenced code block inside a YAML frontmatter block.
- **FR-002**: When the cursor is inside or before the frontmatter and no text is selected, the empty code block MUST be inserted after the frontmatter.
- **FR-003**: When a non-empty selection exists, the selected text MUST be wrapped with code fences at the selection boundaries, preserving existing behaviour.
- **FR-004**: Notes without a valid YAML frontmatter block MUST keep the original insertion-at-cursor behaviour.
- **FR-005**: The frontmatter-detection logic MUST be implemented as a pure, unit-testable helper in `core.py`.

### Key Entities

- **YAML frontmatter block**: A block that starts at the first line with `---` and ends at the next line that contains only `---`.
- **Safe insertion location**: The first non-blank line after the closing frontmatter fence, or the end of the document if only blank lines follow.
- **Editor toolbar action**: The `code` action emitted by `EditorToolbar` and handled in `MarkdownEditorApp.on_editor_toolbar_action`.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In a headless test, creating a daily note and clicking the toolbar code-block button produces a document whose first three lines are still `---`, `type: daily_note`, `date: ...`, followed by a fenced code block.
- **SC-002**: The frontmatter-detection helper passes unit tests for frontmatter-only notes, notes with content, notes without frontmatter, and unclosed frontmatter.
- **SC-003**: The existing "wrap selection" behaviour continues to work in the headless test suite.
- **SC-004**: `python -m compileall src` and `uv run pytest` pass after the change.

## Assumptions

- A YAML frontmatter block is recognised by the simple `---` fence convention used throughout the project.
- The fix applies only to the toolbar code-block button; inline code formatting and other toolbar actions keep their existing behaviour.
- The editor widget is a Textual `TextArea`; its coordinate system is `(row, column)`.
