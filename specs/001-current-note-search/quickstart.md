# Quickstart: Current Note In-Editor Search

Use this guide to validate the in-note search feature end-to-end after implementation.

## Prerequisites

- Python 3.14+ environment with project dependencies installed (`uv sync`).
- A working `config.yaml` pointing to a notes directory that contains at least one Markdown file.

## Run the application

```bash
uv run impactite
```

Or, with an explicit config:

```bash
uv run impactite path/to/config.yaml
```

## Validation Steps

### 1. Open a note

- Select any `.md` file from the file tree and open it.
- Confirm the note content is visible in view mode.

### 2. Activate in-note search

- Press `F7`.
- **Expected result**: a compact search dialog appears near the top of the viewing area. The note text behind it remains readable and only the dialog casts a shadow.

### 3. Search for a phrase

- Type a word that appears multiple times in the note.
- **Expected result**: every occurrence is highlighted in the note; the status indicator shows the total number of matches and the first match is selected/scrolled into view.

### 4. Navigate results

- Press the same "next result" control used for global full-text search.
- **Expected result**: the selection moves to the next match and the note scrolls to keep it visible.
- Press the "previous result" control.
- **Expected result**: the selection moves to the previous match and scrolls into view.

### 5. Empty query handling

- Clear the search input.
- **Expected result**: all highlights disappear and the status shows no matches.

### 6. No-results handling

- Type a string that does not occur in the note.
- **Expected result**: a "no results"/empty-state message is shown in the dialog and no highlights remain in the note.

### 7. Edit mode search

- Open a note in edit mode (`e`).
- Press `F7` and type a phrase.
- **Expected result**: matches are highlighted in the editor, and next/previous controls move the selection.

### 8. Close the dialog

- Press `Escape` or the configured close key.
- **Expected result**: the dialog closes, all highlights are removed, and focus returns to the viewer or editor.

## Success Criteria Reference

- Dialog opens within 1 second of pressing `F7`.
- Highlights appear within 500 ms of typing.
- Navigation to next/previous match scrolls within 500 ms.
- Dialog covers no more than ~20% of the vertical viewing area.
