# Data Model: Directory Color Presets

## Data Changes

No new data structures or persistent files are introduced.

| Aspect | Current | After change |
|--------|---------|--------------|
| New entities | None | None |
| Modified fields | None | None |
| Files changed | `src/impactite/app.py`, `src/impactite/i18n.py` | same |

The directory colour is still stored as a `DirectoryStyle` in `config.yaml`. The preset palette only changes how the user selects the colour values; it does not change how those values are stored or validated.
