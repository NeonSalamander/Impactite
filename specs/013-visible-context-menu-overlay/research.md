# Research: Visible Context-Menu Overlay

## Unknown 1: Why is the context-menu overlay solid?

**Decision**: The current CSS defines `DirectoryContextMenu { width: 100%; height: 100%; background: black 25%; }`. Some terminals do not render semi-transparent background colors as blends with lower-layer content; instead they approximate the translucent color against the terminal background, producing a near-opaque dark fill (as seen in `screen.png`).

**Rationale**:
- The screenshot histogram shows `#0D0D0D` across most of the image, matching an opaque dark overlay, not a 25% translucent one.
- The same `black 25%` rule applied to `ModalScreen` behaves differently because `ModalScreen` is rendered on its own screen and Textual may handle its background through a different path.
- A widget that fills the whole screen with any non-transparent color will hide the widgets below unless the terminal supports true alpha blending.

## Unknown 2: Should we make the context menu non-full-screen instead?

**Decision**: Yes. The simplest robust fix is to size the context menu container to fit its content and position it near the cursor. Remove the full-screen overlay entirely for `DirectoryContextMenu`; only the menu box itself is rendered.

**Rationale**:
- A small floating menu does not need a full-screen overlay to look correct.
- Keeping the rest of the workspace fully unobscured directly satisfies the screenshot complaint.
- Dismissal still works by clicking anywhere outside the menu box.

## Unknown 3: What happens to modal dialogs?

**Decision**: Keep the shared `ModalScreen` dimming rule but switch from `black 25%` to a theme-aware translucent background that Textual renders consistently. If screenshots show dialogs are still too dark, further reduce the opacity or use `$background 30%`.

**Rationale**: Dialogs legitimately dim the workspace, but the color must not become a solid wall on low-color terminals.

## Unknown 4: Where do clicks outside the menu go?

**Decision**: The existing `DirectoryContextMenu._on_click` dismisses the menu when the click is outside the menu box. Removing the full-screen overlay background does not change this because the container still covers the screen; only its *background* is transparent.

**Rationale**: The container still receives mouse events over the whole screen; the user can click outside to close.
