# Research: Fix Directory Tree Line Offset

## Unknown 1: What causes the one-character shift on certain rows?

**Decision**: Variable-width emoji/grapheme clusters used as node prefixes render as either one or two cells depending on the terminal font and Unicode version. When Textual expects a 2-cell emoji but the terminal renders it as 1 cell (or vice-versa), the guide characters, label text, and fill to the right edge of the tree widget slip by one cell for that row.

**Rationale**:
- `FileTree._add_nodes` prefixes directory nodes with `📁 `, Markdown files with `📄 `, attachments with `📎 `, the link graph with `🕸️ `, and favorites with `⭐ `.
- These emoji strings rely on terminal-specific Unicode width tables. On the screenshot, one of those rows is the only visible row shifted — consistent with a single glyph width disagreement.
- Textual/Rich generally reports emoji as width 2, but some terminals (or fonts) render certain emoji sequences (especially those with `U+FE0F` variation selectors like 🕸️) as 1 cell, creating the observed offset.

## Unknown 2: Should we keep emojis at all?

**Decision**: No. Replace the emoji prefixes with fixed-width terminal-safe glyphs that every terminal renders in exactly one cell.

**Rationale**:
- Any solution that requires user-specific terminal configuration is fragile.
- Single-width glyphs such as `[D]`, `+`, `▸`, `◦`, or basic box-drawing characters have stable cell width and still distinguish directory, file, and attachment nodes.
- This removes ambiguity and fixes the alignment in all terminals without disabling emoji system-wide.

## Unknown 3: Which replacement glyphs should be used?

**Decision**: Use single-width character prefixes plus a space:

| Node type | Proposed prefix | Notes |
|-----------|-----------------|-------|
| Directory | `📁` → `[D]` | ASCII brackets are 3 cells total (`[D] `) — further discussion in contracts. |
| Markdown file | `📄` → `•` or `-` | Single cell bullet/dash. |
| Attachment | `📎` → `◦` | Hollow bullet to distinguish from Markdown files. |
| Link graph | `🕸️` → `~` or `∞` | Avoid combined emoji. |
| Favorite | `⭐` → `*` | Single cell star. |

**Rationale**:
- The exact glyphs will be chosen during implementation; the critical part is that each prefix is a known single-cell width.
- If a glyph is selected that has ambiguous width (e.g., some East-Asian characters), it must be rejected.

## Alternatives considered

1. **Width detection at runtime** — call `rich.cells.cell_len(icon)` and pad accordingly. Rejected because the terminal, not the library, decides actual display width; padding may still misalign.
2. **Disable icons for selected nodes only** — overly specific to the screenshot row.
3. **Use standard Textual `Tree` expand/collapse icons without prefixes** — loses visual node-type distinction.

## Implementation notes

- Only the strings passed to `TreeNode.add(...)` in `FileTree._add_nodes` and `FileTree.populate_tree` are affected.
- `render_label` and `_render_line` need no width-aware changes once the prefixes are fixed-width.
- No core/config changes are needed.
