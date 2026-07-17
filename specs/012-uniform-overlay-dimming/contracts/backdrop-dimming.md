# UI Contract: Uniform 25% Overlay Dimming

## Visual behavior contract

| Condition | Requirement |
|-----------|-------------|
| Any `ModalScreen` subclass is open | The full screen behind the dialog MUST be dimmed by a single shared rule; the workspace MUST remain visible and readable. |
| Context menu (`DirectoryContextMenu`) is open | The area outside the menu box (`#directory-context-menu-box`) MUST be dimmed to the same level as modal dialogs. |
| Theme change (dark / light) | The perceived dimming strength MUST remain approximately the same; it MUST NOT disappear in dark themes or become excessive in light themes. |
| Menu/dialog content | Inner dialog containers and the menu box MUST keep their opaque background (`$surface`), text, and borders unchanged. |

## Implementation notes (non-normative)

- The contract is realized through a global Textual CSS rule and one overlay widget CSS update.
- No code changes are required in modal classes, event handlers, or configuration.
