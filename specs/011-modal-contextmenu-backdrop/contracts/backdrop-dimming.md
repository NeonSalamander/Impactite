# UI Contract: Modal and Context Menu Backdrop Dimming

## Visual behavior contract

| Condition | Requirement |
|-----------|-------------|
| Any modal dialog (`ModalScreen`) is open | The area behind the dialog MUST remain partially visible and MUST NOT be completely black/opaque. |
| The directory context menu is open | The full-screen overlay behind the menu box MUST remain partially visible and MUST NOT be completely black/opaque. |
| Dialogs and context menus are compared side-by-side | Their backdrops MUST have the same visible darkness level. |

## CSS contract

- The `ModalScreen` base class has a backdrop background using the theme's `$background` color with a low opacity percentage (20–30%).
- The `DirectoryContextMenu` overlay has a backdrop background using the same `$background` color and the same opacity percentage as `ModalScreen`.
- Any existing per-modal `background` override is aligned to the same opacity level.

## Non-goals

- No per-overlay or per-user dimming configuration.
- No changes to modal content styling (only the backdrop).
- No effect on notifications, toasts, or tooltips.
