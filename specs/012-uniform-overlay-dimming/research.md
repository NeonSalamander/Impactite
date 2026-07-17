# Research: Uniform 25% Overlay Dimming

## Unknown 1: Why did `$background 25%` fail to dim in dark themes?

**Decision**: A theme-aware overlay color (`$background 25%`) is blended with the underlying workspace. When the app background is already the same base color as the overlay, the delta is too small, so dark themes perceive no dimming and light themes may also see little change if the colors are close. A fixed neutral dark overlay (e.g., `black 25%`) gives a more consistent visual reduction in every theme because it always darkens the background, not merely tints it with the theme color.

**Rationale**:
- 25% dimming means the perceived brightness of the workspace should drop, not just receive a theme-colored tint.
- Using the application background as the overlay color makes the effect depend on how similar the rendered background already is to `$background`.
- Textual supports `background: <color> <percentage>;` syntax for alpha blending. A fixed dark color with 25% opacity produces the desired ``see-through but darker'' effect across both dark and light themes.

**Alternatives considered**:
- Keep `$background 25%`: simple but theme-dependent; rejected because it failed the user's dark-theme report.
- Use `#000000 25%` / `black 25%`: better theme independence and provides actual darkening.
- Use a fully transparent overlay (`transparent`): gives no dimming at all; rejected by the requirement.

## Unknown 2: Do all existing modals need per-class rules?

**Decision**: Define a single global rule for `ModalScreen` and let every subclass inherit it. Remove any per-class `background` declarations that override it. This also fixes the previous inconsistency where some dialogs had no dimming.

**Rationale**: One rule guarantees uniformity and avoids having to touch each modal class individually whenever the dimming level changes.

## Unknown 3: How should context-menu dimming behave?

**Decision**: Apply the same fixed 25% dark overlay to the full-screen `DirectoryContextMenu` container. Keep the inner menu box (`#directory-context-menu-box`) opaque so the menu itself stays readable. Clicking outside the box already closes the menu.

**Rationale**: The full-screen context-menu overlay is structurally the same as a modal backdrop: an area around a focused surface that should remain visible but subdued.
