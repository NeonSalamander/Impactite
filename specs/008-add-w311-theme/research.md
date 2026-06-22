# Research: Adding a Windows 3.11 "W311" Theme to Impactite

## Decision

Define a custom Textual `Theme` named "w311" and register it with the app at startup. The theme uses a classic Windows 3.11 palette:

- Light gray dominant chrome (`#c0c0c0`) for `background`, `surface`, and `panel`
- Black foreground (`#000000`) for standard text
- Dark blue (`#000080`) for `primary` (title bars / borders) and `accent` (focused highlights)
- Mid gray (`#808080`) for `secondary`
- Yellow warning (`#ffff00`), red error (`#ff0000`), green success (`#008000`)
- White (`#ffffff`) for `boost`
- Mark the theme as light (`dark=False`)

## Rationale

- Textual exposes a `Theme` class and `App.register_theme(name, theme)`, so a third-party framework is unnecessary.
- Windows 3.11 is a light UI; marking `dark=False` lets existing light/dark detection drive the editor code theme.
- The current `_apply_editor_syntax_theme` already switches pygments to `github_light` for any `self.theme in _LIGHT_THEMES`. Therefore "w311" must be added to `_LIGHT_THEMES`.
- The startup theme resolver already validates against registered themes via `self.get_theme(user_theme)`, so the new theme loads on startup once registered.
- The existing `Ctrl+L` toggle uses the persisted `user_theme` and resolves a light/dark counterpart. With "w311" saved as the user theme, toggling will switch to a dark variant (most likely `textual-dark`) and back.

## Alternatives Considered

- **Custom CSS override only**: Rejected because it would be fragile and not integrate with the app's theme switching/persistence.
- **Named pygments theme for application UI**: Rejected; pygments only highlights code blocks, not the TUI chrome.
- **Subclassing `App` theme handling**: Rejected; Textual's `register_theme`/reactive `theme` attribute already solves the problem.

## Implementation Notes

- Register the theme during `MarkdownEditorApp.__init__` immediately after `super().__init__()`.
- Add `"w311"` to `_LIGHT_THEMES`.
- Add `"w311"` to the config comment examples so users know it is available (optional documentation touch).
- No change to `core.py` unless exposing theme names; existing `get_user_theme`/`save_user_theme` strings suffice.
