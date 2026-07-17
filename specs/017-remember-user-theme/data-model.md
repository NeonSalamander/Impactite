# Data Model: Remember User Theme

## Data Changes

No new data structures or files are introduced. The existing `display.app_theme` key in `config.yaml` is reused.

| Aspect | Current | After change |
|--------|---------|--------------|
| New entities | None | None |
| New persistent keys | None | None (uses existing `display.app_theme`) |
| Modified fields | `display.app_theme` already exists | Value now stores the last effective theme, not only the "base" theme |
| Validation | None on startup | Saved theme validated against registered themes; invalid values fall back and overwrite the key |
| Default value | `textual-dark` per code defaults, or whatever is in `config.yaml` | Falls back to `textual-dark` if saved theme is missing/invalid |

## State Transitions

```
[App launch] -> read display.app_theme
   |
   +-- valid registered theme -> apply it and save it back (idempotent)
   |
   +-- invalid/missing theme -> apply textual-dark and update display.app_theme

[User toggles theme with Ctrl+L] -> resolve counterpart theme
   |
   +-- apply counterpart and save it to display.app_theme
```
