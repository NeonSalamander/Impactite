# Research: Modal and Context Menu Backdrop Dimming

## Unknown: How to control backdrop dimming in Textual

**Decision**: Override the default `ModalScreen` backdrop color/opacity in the application's `DEFAULT_CSS` using Textual's percentage transparency syntax (`$background <opacity>`).

**Rationale**:
- Textual's default `ModalScreen` CSS is:
  ```css
  ModalScreen {
      background: $background 60%;
  }
  ```
  On a dark background this looks nearly black, which is what the user wants to avoid.
- Lowering the opacity to roughly 20–30% keeps the underlying workspace visible while still signaling that the overlay is active.
- The `$background` variable automatically follows the active theme (dark/light), so no per-theme hard-coding is needed.
- Textual's `DirectoryContextMenu` (feature 010) is implemented as a full-screen `Container`; its backdrop can be styled the same way with a partially transparent background.

**Alternatives considered**:
- Add a global `Screen` background override: rejected because it would affect non-modal screens too.
- Use `background: transparent;` for all overlays: rejected because no dimming at all makes it hard to tell which element is active.
- Create a reusable custom `ModalScreen` subclass with lighter dimming: rejected because it adds an extra widget layer; a CSS rule on `ModalScreen` and the context-menu overlay is simpler and covers all existing modals.
- Make the dimming level user-configurable: rejected as over-engineering for the current request; a single sensible default satisfies the user's complaint.

## Unknown: How to keep the change consistent across existing dialogs

**Decision**: Apply one CSS rule to `ModalScreen` and a matching rule to `DirectoryContextMenu`. Any per-widget override (e.g., `TextPromptModal`) should be updated to the same opacity level.

**Rationale**:
- All existing modals inherit from `ModalScreen`; a single rule updates them all.
- The context menu from feature 010 is a `Container`, not a `ModalScreen`, so it needs its own matching rule.
- Some existing modals may set their own `background` on the screen class (e.g., `TextPromptModal` sets `background: $background 50%;`). These overrides must be aligned to the new value to keep consistency.

## Unknown: Light theme

**Decision**: Use the theme variable `$background` with a percentage. Textual resolves `$background` to the current theme's background color, so the same opacity works in both dark and light themes.

**Rationale**: 
- Hard-coding a black or white backdrop would look wrong in one theme. Theme variables automatically adapt.
- A 20–30% overlay on a light theme is a subtle gray; on a dark theme it is a subtle darkening. Both satisfy "slightly dim but not black."
