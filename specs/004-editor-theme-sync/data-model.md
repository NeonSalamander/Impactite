# Data Model: Editor Theme Sync

## Derived State: Editor Syntax Theme

The editor syntax theme is not persisted; it is derived from existing application state.

| Source | Field | Type | Description |
|--------|-------|------|-------------|
| `app.py` | `App.theme` | `str` | Current application theme name |
| `app.py` | `_LIGHT_THEMES` | `frozenset[str]` | Known light application themes |
| `config.yaml` | `display.syntax_theme` | `str` | User-preferred dark syntax theme |

## Rules

1. If `App.theme ∈ _LIGHT_THEMES`, the editor syntax theme is `github_light`.
2. Otherwise, the editor syntax theme is `config.display["syntax_theme"]` with a default of `monokai`.
3. The derived theme is applied every time the editor becomes visible or the application theme changes while the editor is visible.

## State Transitions

- `view_mode → edit_mode`: editor loads note content, then editor theme is reapplied.
- `theme_toggle` while editor visible: application theme changes, then editor theme is reapplied.
- `theme_toggle` while editor hidden (e.g., in graph view): no immediate editor update; theme will be applied next time the editor becomes visible.
