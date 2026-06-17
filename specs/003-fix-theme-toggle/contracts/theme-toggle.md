# Contract: Theme Toggle Behavior

## Overview

This document defines the runtime contract for the `Ctrl+L` theme toggle action.

## Trigger

- Keyboard shortcut: `Ctrl+L`
- Binding id: `toggle_theme`

## Preconditions

- The application has loaded a valid configuration.
- `config.display.app_theme` holds the user's selected theme preference.
- The reactive attribute `App.theme` holds the currently applied Textual theme.

## Behavior

1. The action determines whether the currently applied theme is light by checking membership in the known light themes set (`_LIGHT_THEMES`).
2. The action resolves the target theme using the user's preference (`config.display.app_theme`) and the target mode:
   - If currently light → target is the dark counterpart of `app_theme`.
   - If currently dark → target is the light counterpart of `app_theme`.
3. If `app_theme` has no known counterpart for the target mode, the target falls back to `textual-dark` or `textual-light` respectively.
4. The action sets `_suppress_theme_persist = True` before assigning `self.theme = target` and resets it to `False` immediately after.
5. The editor syntax theme is refreshed to match the new active theme (light themes use `github_light`; dark themes use the configured `syntax_theme`).

## Invariants

- `config.display.app_theme` is never modified as a side effect of pressing `Ctrl+L`.
- The fallback themes `textual-dark` and `textual-light` are always available.
- Rapid consecutive `Ctrl+L` presses cannot corrupt the saved user preference.

## State Diagram

```text
+----------------------------------+
| Startup                          |
| theme = app_theme (or fallback)  |
+----------------------------------+
          |
          v
+----------------------------------+
| User presses Ctrl+L              |
| suppress persist = True          |
| theme = counterpart(app_theme)   |
| (or fallback)                    |
| suppress persist = False         |
+----------------------------------+
          |
          v
+----------------------------------+
| watch_theme fires                |
| if not suppress persist:         |
|   save_user_theme(theme)         |
+----------------------------------+
```
