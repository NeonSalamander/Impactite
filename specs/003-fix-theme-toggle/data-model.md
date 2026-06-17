# Data Model: Fix Theme Toggle

## Configuration Entity: `display.app_theme`

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `app_theme` | `str` | `config.yaml` → `display.app_theme` | The user's explicitly selected application theme. This value is preserved across restarts and is never overwritten by temporary light/dark toggles. |

### Validation rules

- If missing, blank, or references an unknown theme, the application falls back to `textual-dark`.
- The value is updated only when the user explicitly changes the theme (current behavior on startup, and any future theme selector). It is **not** updated when the user presses `Ctrl+L`.

## Runtime Entity: Application Theme State

| Attribute | Type | Owner | Description |
|-----------|------|-------|-------------|
| `theme` | `str` | `textual.app.App` | The currently active Textual theme. May be a light or dark variant of the user's selected theme. |
| `_suppress_theme_persist` | `bool` | `ImpactiteApp` | Internal guard set to `True` while `action_toggle_theme` runs, so `watch_theme` does not persist the temporary active theme to `config.yaml`. |

### State transitions

```text
[Startup]
  theme = config.display.app_theme (fallback textual-dark)

[Ctrl+L pressed while theme is light]
  _suppress_theme_persist = True
  theme = resolve_dark_variant(config.display.app_theme)
  _suppress_theme_persist = False

[Ctrl+L pressed while theme is dark]
  _suppress_theme_persist = True
  theme = resolve_light_variant(config.display.app_theme)
  _suppress_theme_persist = False

[watch_theme triggered]
  if not _suppress_theme_persist:
      config.save_user_theme(theme)
```

## Helper Entity: Theme Variant Resolver

| Function | Inputs | Output | Description |
|----------|--------|--------|-------------|
| `resolve_theme_variant(user_theme: str, target_light: bool, light_themes: frozenset[str]) -> str` | User's selected theme, desired mode, set of known light themes | Theme name to apply | Returns the counterpart theme for the requested mode, or a sensible fallback if no counterpart exists. |

### Counterpart mapping (initial)

| Dark theme | Light counterpart |
|------------|-------------------|
| `textual-dark` | `textual-light` |
| `catppuccin-mocha` | `catppuccin-latte` |
| `rose-pine-moon` | `rose-pine-dawn` |
| `atom-one-dark` | `atom-one-light` |

Unmapped themes fall back to `textual-dark` (when switching to dark) or `textual-light` (when switching to light).
