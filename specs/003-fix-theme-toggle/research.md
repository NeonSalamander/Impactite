# Research: Fix Theme Toggle

**Feature**: Fix Theme Toggle (`specs/003-fix-theme-toggle`)
**Date**: 2026-06-17

## Unknowns & Decisions

### 1. How to distinguish user-selected theme from temporary light/dark toggle

**Decision**: Treat `display.app_theme` in `config.yaml` as the user's explicit preference (set on startup and by any future theme selector). Do **not** persist temporary light/dark toggles. Introduce a transient flag in the app (`_suppress_theme_persist`) to skip saving while `Ctrl+L` is executing.

**Rationale**: The current bug occurs because `watch_theme` writes every runtime theme change back to `app_theme`. Once the toggle switches to `textual-light`, the saved preference is overwritten and the original theme is lost. Suppressing persistence during the toggle keeps the user's preference intact.

**Alternatives considered**:
- Add a separate config key (`app_theme_user`) — rejected because it duplicates state and requires migration of existing configs.
- Persist active mode and restore it on restart — rejected as out of scope; the specification only requires the *theme choice* to survive restarts, not the temporary mode.

### 2. How to determine the light/dark counterpart of an arbitrary theme

**Decision**: Use a small explicit mapping for known Textual theme pairs. If the current theme has no known counterpart, fall back to `textual-light` or `textual-dark`. The mapping lives in `core.py` as a pure helper so it is unit-testable.

**Rationale**: Textual does not expose a built-in "light/dark pair" API for every theme. A small mapping covers the themes available in the application today; unknown themes degrade gracefully to the default light/dark themes.

**Known pairs** (initial set):
- `textual-dark` ↔ `textual-light`
- `catppuccin-mocha` ↔ `catppuccin-latte`
- `rose-pine-moon` ↔ `rose-pine-dawn`
- `atom-one-dark` ↔ `atom-one-light`

**Light-only / dark-only themes** without known counterparts fall back to `textual-dark` (when switching to dark) or `textual-light` (when switching to light).

### 3. Where to place the theme-resolution logic

**Decision**: Put the pure resolution function in `core.py` and call it from `app.py`, passing `_LIGHT_THEMES` from `app.py`.

**Rationale**: Keeps `app.py` focused on UI reactions while making the counterpart/fallback logic testable without importing Textual widgets. `_LIGHT_THEMES` remains in `app.py` per the constitution.

### 4. How to handle invalid or missing `app_theme`

**Decision**: Fall back to `textual-dark` on startup and on every toggle resolution. This matches the existing default and keeps the application usable.

**Rationale**: Defensive handling is explicitly required by the specification and avoids crashes when the configuration file is edited manually or corrupted.
