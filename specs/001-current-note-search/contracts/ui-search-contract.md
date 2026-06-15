# UI Contract: Current Note In-Editor Search

This document describes the user-facing interface contract for the in-note search feature. It covers activation, input behavior, navigation, and visual requirements.

## Activation

- **Default hotkey**: `F7`
- **Configuration key**: `search_in_note` under `hotkeys` in `config.yaml`
- **Availability**: Active whenever a Markdown note is open in view mode or edit mode.

## Search Dialog Contract

- The dialog appears as a compact overlay near the top of the note viewing area.
- The dialog does **not** dim the underlying note content.
- The dialog casts a shadow to visually separate it from the note text.
- The dialog contains:
  - A single-line input field for the query.
  - A status indicator showing `current / total` matches or a "no results" message.
- Focus is placed in the input field when the dialog opens.

## Input Behavior

- Typing immediately updates highlights in the current note.
- Search is case-insensitive by default.
- Search matches literal substrings.
- Clearing the input clears all highlights.

## Navigation Contract

- The same controls used for the global full-text search results navigate in-note matches when the in-note search dialog is active.
- `Next result`: moves selection to the next match and scrolls it into view.
- `Previous result`: moves selection to the previous match and scrolls it into view.
- At the last match, activating `Next result` wraps to the first match.
- At the first match, activating `Previous result` wraps to the last match.

## Dismissal

- Pressing the configured cancel/close key closes the dialog.
- Closing the dialog clears highlights and returns focus to the viewer or editor.

## Visual Highlight Contract

- All matches are highlighted with a secondary highlight style.
- The currently selected match is highlighted with a primary highlight style and scrolled into view.
- In edit mode the current match may be represented by the editor selection.
