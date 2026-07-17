# UI Contract: Visible Context-Menu Overlay

## Visual behaviour contract

| Condition | Requirement |
|-----------|-------------|
| Context menu (`DirectoryContextMenu`) is open | The area outside the menu box MUST NOT be filled with an opaque color. The workspace (tree, editor, etc.) MUST remain fully readable. |
| Modal dialogs open | The screen behind the dialog MAY be dimmed, but it MUST remain visible and not become a solid wall. |
| Menu box itself | The context-menu box (`#directory-context-menu-box`) MUST keep an opaque background so its items are readable. |
| Click outside the menu | The full-screen container still receives mouse events; clicking outside the menu box MUST close the menu. |

## Implementation notes (non-normative)

- The contract is realized by making `DirectoryContextMenu` transparent and sizing it to its menu box content.
- No code changes are needed in handlers, config, or core logic.
