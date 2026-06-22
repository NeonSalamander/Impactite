# Data Model: Add W311 Theme

## Entities

### `Theme "w311"`

A custom Textual theme object registered at runtime.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Canonical theme name `"w311"` |
| `primary` | `str` | Dark blue `#000080` (title bars, borders) |
| `secondary` | `str` | Mid gray `#808080` |
| `warning` | `str` | Yellow `#ffff00` |
| `error` | `str` | Red `#ff0000` |
| `success` | `str` | Green `#008000` |
| `accent` | `str` | Dark blue `#000080` (focused elements) |
| `foreground` | `str` | Black `#000000` |
| `background` | `str` | Light gray `#c0c0c0` |
| `surface` | `str` | Light gray `#c0c0c0` |
| `panel` | `str` | Light gray `#c0c0c0` |
| `boost` | `str` | White `#ffffff` |
| `dark` | `bool` | `False` because this is a light theme |

### `_LIGHT_THEMES`

A frozenset in `src/impactite/app.py` that names all light themes. Adding `"w311"` here activates automatic light-mode behaviors (editor syntax theme, toggle logic).

### `Config.display.app_theme`

A string stored in `config.yaml`. It may now equal `"w311"` and must round-trip through `Config.get_user_theme()` / `Config.save_user_theme()`.

## Invariants

- The `w311` theme is registered before `self.theme` is assigned in `MarkdownEditorApp.__init__`.
- `"w311"` is present in `_LIGHT_THEMES`.
- If `app_theme` is not registered, the app falls back to `"textual-dark"`.
