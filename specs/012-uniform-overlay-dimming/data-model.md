# Data Model: Uniform 25% Overlay Dimming

## Data Changes

This feature does not introduce any new data entities, files, or persistent configuration. It only changes the visual styling of modal backdrops and the context-menu overlay.

| Aspect | Current | After change |
|--------|---------|--------------|
| New files | none | none |
| Modified files | `src/impactite/app.py` (`DEFAULT_CSS`) | same |
| Configuration keys | none added | none added |

All dialogs and context menus will inherit a single shared CSS rule; no new runtime state is required.
