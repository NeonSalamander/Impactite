# Research: Keep Tree Icons Aligned

## Unknown 1: Why did the original emoji labels shift by one cell?

**Decision**: The shift was caused by switching some icon prefixes to ASCII while the tree still contained other rows (e.g., root, pseudo-nodes) with emoji. Restoring a uniform set of original emoji prefixes of identical cell width removes the inconsistency.

**Rationale**:
- Rich's `cell_len` reports each original emoji (`📁`, `📄`, `📎`, `🕸️` with VS16, `⭐`) as two terminal cells.
- In the original implementation every node label used the same format: `emoji + " " + name`.
- The temporary fix replaced emoji with ASCII prefixes. The user now wants the original pictograms back.
- Because all original emoji prefixes share the same Rich-calculated width, Textual's `Tree` should render them uniformly as long as the terminal honours the same widths.

**Alternatives considered**:
- Replace emoji with single-width Unicode symbols — rejected by user constraint "Важно оставить оригинальные эмодзи".
- Add/remove spacing around emoji depending on terminal — too fragile and terminal-dependent.

## Unknown 2: Which rows need the icons restored?

**Decision**: Restore emoji on every place where the temporary ASCII fix removed them:
- Link graph root node: `🕸️ Link graph`
- Favorites root node: `⭐ Favorites`
- Favorite entries: `⭐ {name}`
- Directory nodes: `📁 {name}`
- File nodes: `📄 {name}` for `.md`, `📎 {name}` for other files

**Rationale**: This covers all visible nodes in `FileTree.populate_tree` and `FileTree._add_nodes`.

## Unknown 3: Is there a code-level cause of the one-character shift?

**Decision**: No code-level width bug found. `render_label` only colours the text; it does not change length. The `_render_line` override only changes background style. The label format `icon + " " + name` is consistent.

**Rationale**:
- Verified `render_label` returns `text.copy()` with a global style overlay.
- Verified `_render_line` applies `base_style + Style(bgcolor=...)` and does not mutate segment lengths.
- Verified with `rich.cells.cell_len` that all selected emojis are width 2.

## Risk

If the terminal where `screen2.png` was captured renders one of these emoji differently from Rich (e.g., as 1 cell instead of 2), alignment cannot be enforced without changing the character. In that case the fix would be terminal-dependent, which conflicts with the requirement. We accept this risk because the user explicitly requires the original emoji.
