# Data Model: Fix Directory Tree Line Offset

## Data Changes

No new data structures or persistent files are introduced.

| Aspect | Current | After change |
|--------|---------|--------------|
| New files | none | none |
| Modified files | `src/impactite/app.py` (icon strings) | same |
| Configuration keys | none | none |

The change replaces variable-width emoji prefixes with fixed-width glyphs in the node labels created by `FileTree`.
