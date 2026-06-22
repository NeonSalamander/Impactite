# Research: Adding a TurboVision "TV" Theme to Impactite

## Decision

Define a custom Textual `Theme` named "tv" and register it with the app at startup. The theme uses a TurboVision palette: dark blue background (`#0000aa`), cyan panels/borders (`#00aaaa`), light gray/cyan foreground (`#aaaaaa`), and yellow/white accents (`#ffff55`, `#ffffff`). Because it is a dark theme, no `_LIGHT_THEMES` update is required.

## Rationale

- Textual exposes a `Theme` dataclass and `App.register_theme(Theme)` API, so a new theme can be added without patching Textual internals.
- Textual stores theme values as CSS variables; once registered, the theme applies to all built-in widgets automatically.
- The existing `watch_theme` handler already persists the active theme name to `config.yaml`, so persistence is free once `App.theme` is set to `"tv"`.
- Keeping the theme definition in `app.py` follows the constitution: UI/styling code belongs to the UI layer.

## TurboVision Color Mapping to Textual Tokens

| TurboVision element | Suggested Textual token | Color |
|---------------------|------------------------|-------|
| Background          | `background`           | `#0000aa` (dark blue) |
| Panel/dialog bg     | `panel` / `surface`    | `#00aaaa` (cyan) or `#0000aa` |
| Border              | `primary`              | `#00aaaa` (cyan) |
| Focused/accent      | `accent`               | `#ffff55` (yellow) |
| Text                | `foreground`           | `#aaaaaa` (light gray) |
| Error               | `error`                | `#ff5555` (red) |
| Warning             | `warning`              | `#ffff00` (bright yellow) |
| Success             | `success`              | `#55ff55` (bright green) |
| Secondary           | `secondary`            | `#5555ff` (blue) |
| Boost               | `boost`                | `#00005f` (darker blue) |

## Theme Toggle Behavior

The existing `action_toggle_theme` toggles between light and dark variants of the current base theme using `_THEME_PAIRS` and `_LIGHT_THEMES`.

- If the active theme is "tv" (dark) and the user presses `Ctrl+L`, the toggle will switch to the default light theme (`textual-light`) because "tv" has no registered light counterpart.
- This is acceptable for the MVP: it keeps the existing toggle logic unchanged and allows users to leave TV via the same shortcut.
- A future enhancement could replace the binary toggle with a full cycle through all registered themes.

## Editor/Code Theme Pairing

- The TV background is dark blue, so a dark pygments theme is required.
- Default editor theme `monokai` works; no change needed.
- `_apply_editor_syntax_theme` decides editor theme based on `self.theme in _LIGHT_THEMES`. Since TV is not in `_LIGHT_THEMES`, the editor keeps `syntax_theme` (default `monokai`) — good contrast.

## Validation of Config Theme

- `core.validate_theme()` currently checks only `textual.theme.BUILTIN_THEMES`.
- At app startup we register the "tv" theme before assigning `self.theme`, then validate the persisted theme name against the union of builtin and registered themes (using `App.get_theme`).
- If the persisted theme is unknown, fall back to `textual-dark`.

## Alternatives Considered

| Approach | Why Rejected |
|----------|--------------|
| Patch `_LIGHT_THEMES` and pretend TV is a builtin theme | Impossible; builtin themes are sealed in Textual |
| Override CSS globally instead of using `Theme` | Bypasses Textual's theme system; harder to make selectable and persistent |
| Add a light variant "tv-light" | Out of scope; user only asked for one TurboVision theme |
| Store theme in a new config key | Unnecessary; existing `display/theme` (or equivalent) already persists the active theme |

## Implementation Notes

- Define a module-level constant `TV_THEME: Theme = Theme(name="tv", primary="#00aaaa", ..., dark=True)` in `app.py`.
- In `MarkdownEditorApp.__init__`, after `super().__init__()`, call `self.register_theme(TV_THEME)`.
- Replace `self.theme = validate_theme(self.config.get_user_theme())` with a check against registered themes via `self.get_theme(name)`.
- Add "tv" to any theme-enumeration used for pickers if one is added later (not needed for MVP).
