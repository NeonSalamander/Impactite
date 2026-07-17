# Research: Remember User Theme

## Unknown 1: Why is the last theme not restored?

**Decision**: `action_toggle_theme` in `app.py` deliberately suppresses saving the theme when switching between the light and dark variant of the user's selected "base" theme. It sets `_suppress_theme_persist = True`, changes `self.theme`, and leaves the config untouched.

Because the startup code loads `config.get_user_theme()` (the base theme), a user who toggles to the dark variant does not have that variant saved. The next launch reads the base theme again, which is still light.

**Rationale**: The intent of the suppression was to avoid corrupting the saved "base" theme name every time the user presses Ctrl+L. However, the practical effect is that the last active theme is lost.

**Alternatives considered**:
- Save a separate "base theme" plus "last variant" flag — more complex and not required by the spec; the spec asks to remember the last selected theme.
- Save only on explicit theme selection elsewhere — there is currently no separate theme chooser; the toggle is the only path.
- Save the effective theme on every toggle — keeps the model simple and matches user expectation.

## Unknown 2: What should happen when the saved theme is invalid or missing?

**Decision**: On startup, validate the saved theme against `App.get_theme`. If it is invalid or unavailable, fall back to `"textual-dark"` and persist the fallback so the config is not left in a broken state over multiple launches.

**Rationale**: Textual's `register_theme` only knows about built-in themes and themes explicitly registered by the app (e.g., custom `TV_THEME`, `W311_THEME`). A theme name that does not pass `App.get_theme` would fail if applied.

**Alternatives considered**:
- Keep the invalid value and silently use the default — rejected because the user would keep relaunching into a broken state.
- Raise an error — rejected because a missing config is a normal first-launch scenario.

## Unknown 3: How do we avoid repeatedly overwriting the config at start-up?

**Decision**: The startup code already sets `self.theme = user_theme`, which triggers `watch_theme` and calls `config.save_user_theme`. Writing the same value back is harmless. The fix does not need to suppress this write; it only needs to ensure the value being written is the effective theme (including after a toggle) and valid.

**Rationale**: Avoiding the startup write would require a separate guard and complicate the reactive flow. Re-writing the same valid theme is idempotent and keeps the code path uniform.

**Alternatives considered**:
- Add `_suppress_theme_persist = True` around the startup assignment — rejected because it would also suppress the first legitimate save when a user explicitly changes the theme later unless the guard is reset carefully.
