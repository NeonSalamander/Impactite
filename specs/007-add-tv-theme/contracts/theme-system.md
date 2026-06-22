# Contract: Theme System

## Interface: Custom Theme Registration

**Location**: `src/impactite/app.py`

At application initialization, the "tv" theme is registered with the Textual app before the active theme is applied:

```python
self.register_theme(TV_THEME)
```

**Behavior**:

- After registration, `self.get_theme("tv")` returns the registered `Theme` instance.
- After registration, `self.theme = "tv"` is valid and applies the theme.
- If registration is omitted, setting `"tv"` raises a `ThemeError` (unknown theme).

## Interface: Theme Persistence

**Location**: `src/impactite/app.py` (`watch_theme`)

When `App.theme` is changed programmatically and theme persistence is not suppressed, the new theme name is saved to the user's configuration.

**Behavior**:

- Persisted theme name equals the active theme string (e.g., `"tv"`).
- On the next launch, the app reads the persisted name and restores it.

## Interface: Theme Toggle

**Location**: `src/impactite/app.py` (`action_toggle_theme`)

**Input**: current `App.theme` string.
**Output**: new `App.theme` string (light variant, dark variant, or default fallback).

**Behavior with TV**:

- If current theme is `"tv"` (dark), pressing `Ctrl+L` switches to the default light theme (`textual-light`).
- If the current theme is `"textual-light"`, pressing `Ctrl+L` switches to its dark counterpart (`textual-dark`).
- This matches the existing behavior: TV participates as a dark theme without a dedicated light counterpart.

## Error Handling

- Unknown persisted theme names fall back to `textual-dark` silently at startup.
- Theme registration failures are surfaced as a Textual notification without crashing the app.
