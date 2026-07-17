# UI Contract: Directory Tree Row Alignment

## Visual behaviour contract

| Condition | Requirement |
|-----------|-------------|
| Tree is rendered in any supported terminal | Every visible row MUST start at the same horizontal cell boundary after the tree guides. No row may be shifted by one character. |
| A node has a custom background/foreground colour | The colour style MUST NOT introduce extra cells or change the alignment of the row. |
| Directory, markdown file, attachment, link graph, or favorite node is visible | The icon prefix MUST be a fixed-width glyph rendered in a known number of cells (no emoji width ambiguity). |
| Row is selected, expanded, collapsed, or scrolled | Alignment MUST remain identical to unselected/unexpanded rows in the same viewport. |

## Implementation notes (non-normative)

- The contract is realised by replacing emoji prefixes with single-cell ASCII or box-drawing symbols.
- No label styling logic is changed; `render_label` continues to apply node colours.
