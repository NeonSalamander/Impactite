# Contract: Editor Theme Sync

## Overview

This contract defines how the code editor (`TextArea`) theme must follow the application's light/dark mode.

## Stakeholders

- User interacting with the TUI editor
- `app.py` — owner of the editor widget and theme application logic

## Behavior

### When entering edit mode

Given the user has opened a note for editing:

1. The application MUST determine whether the current `App.theme` is a light theme by checking membership in the known light theme set.
2. If the application is in light mode, the editor (`TextArea.theme`) MUST be set to `github_light`.
3. If the application is in dark mode, the editor MUST be set to the value of `Config.display["syntax_theme"]` (default `monokai`).

### When toggling application theme

Given the user pressed `Ctrl+L` while a note is open in edit mode:

1. The application MUST update `App.theme` according to the existing toggle logic.
2. If the editor container (`#editor-container`) is visible, the editor theme MUST be refreshed using the same light/dark selection rules.
3. The refresh MUST happen without requiring the user to close and reopen the note.

### When switching between view and edit modes

Given the user toggles between view and edit mode on the same note:

1. Entering edit mode MUST apply the editor theme before focus is given to the editor.
2. Returning to view mode MUST not affect editor theme state.

### Error Handling

- If the editor widget is not yet mounted, the theme application MUST fail silently; the theme will be applied when the widget becomes available.
- If `syntax_theme` is missing or invalid, the dark-mode editor MUST fall back to `monokai`.
