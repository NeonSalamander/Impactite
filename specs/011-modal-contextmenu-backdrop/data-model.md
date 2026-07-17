# Data Model: Modal and Context Menu Backdrop Dimming

## Data Changes

This feature does not introduce any new data entities, files, or persistent configuration. It only changes the visual styling of overlay backdrops.

## Existing Overlay Concepts Used

- **ModalScreen**: Textual screen type used for confirmation prompts, input dialogs, selection dialogs, and settings dialogs. Its built-in `background` CSS property controls the dimming of the workspace behind it.
- **DirectoryContextMenu**: A full-screen `Container` widget from feature 010 whose background covers the workspace when the context menu is open. Its `background` CSS property controls dimming.

## Notes

Because there is no persistent state, input validation, or relationships, no new entity definitions are necessary.
