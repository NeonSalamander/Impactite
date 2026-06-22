# Data Model: Add TV Theme

## Entities

### `Theme "tv"`

A custom Textual theme object registered at runtime.

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Theme identifier: `"tv"` |
| `primary` | `str` | Color used for primary accents/borders |
| `secondary` | `str` | Secondary color |
| `warning` | `str` | Warning color |
| `error` | `str` | Error color |
| `success` | `str` | Success color |
| `accent` | `str` | Focused/active element color |
| `foreground` | `str` | Main text color |
| `background` | `str` | Application background color |
| `surface` | `str` | Surface/panel background |
| `panel` | `str` | Panel background |
| `boost` | `str` | Boost color for subtle emphasis |
| `dark` | `bool` | Whether the theme is dark (`True` for TV) |
| `variables` | `dict[str, str]` | Optional extra CSS variables |

### `Config theme value`

The user's selected theme name stored in `config.yaml`.

| Field | Type | Description |
|-------|------|-------------|
| `display.app_theme` or equivalent | `str` | Active theme name, e.g. `"tv"`, `"textual-dark"` |

## State Transitions

- **Startup**: `config.yaml` → `App.register_theme(tv)` → `App.theme = "tv"` if registered.
- **Theme switch**: User presses `Ctrl+L` → `action_toggle_theme` resolves light/dark variant → `App.theme` changes → `watch_theme` persists new name to `config.yaml`.
- **Cold start**: `config.yaml` value is restored as active theme on next launch.

## Invariants

- The "tv" theme name must be registered before `App.theme` is assigned.
- Unknown persisted theme names fall back to `textual-dark`.
- `_LIGHT_THEMES` contains only light themes; "tv" must not be added to it.
- The editor syntax theme must remain readable when "tv" is active.
