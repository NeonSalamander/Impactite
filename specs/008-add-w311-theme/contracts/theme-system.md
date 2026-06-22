# Contract: Theme System

## Interface: Custom Theme Registration

**Location**: `src/impactite/app.py`

At application initialization, the "w311" theme is registered with the Textual app before the active theme is resolved.

```text
register_theme("w311", W311_THEME)
```

**Preconditions**:
- `W311_THEME` is a valid Textual `Theme` instance.
- `MarkdownEditorApp.__init__` has completed `super().__init__()`.

**Postconditions**:
- `App.get_theme("w311")` returns the registered theme.
- The theme is available for assignment to `self.theme`.

## Interface: Light Theme Set

**Location**: `src/impactite/app.py`

The `_LIGHT_THEMES` frozenset includes `"w311"`.

**Behavior**:
- `_apply_editor_syntax_theme` switches the editor to `github_light` when `self.theme in _LIGHT_THEMES`.
- `action_toggle_theme` treats "w311" as the light base and switches to a dark counterpart.

## Interface: Theme Persistence

**Location**: `src/impactite/core.py` (existing `Config` methods)

No changes to the persistence contract. `Config.save_user_theme(theme)` and `Config.get_user_theme()` accept `"w311"` transparently.

**Behavior**:
- Selecting "w311" calls `watch_theme`, which persists `"w311"` to `config.yaml`.
- Startup loads `"w311"`, validates it against registered themes, and applies it.

## Interface: Fallback Theme

**Location**: `src/impactite/app.py`

If `Config.get_user_theme()` returns an unregistered theme name, the app falls back to `"textual-dark"`.

**Behavior**:
- `user_theme = config.get_user_theme()`
- `self.theme = user_theme if self.get_theme(user_theme) else "textual-dark"`
