# UI Contract: Tree Icon Alignment

## Visual behaviour contract

| Condition | Requirement |
|-----------|-------------|
| Directory tree is visible | Every directory, file, favorite, link-graph, and favorite-entry row displays its original emoji prefix. |
| No tree interaction | All rows are horizontally aligned; no row is shifted by one character. |
| Directory expanded/collapsed | Child rows inherit the same icon/alignment rules. |
| Directory colour set/reset | Emoji remains, row alignment unchanged. |
| Theme switch | Emoji remains, row alignment unchanged. |

## Verifiable attributes

- A row label begins with one of the following exact prefixes:
  - `📁 ` — directory
  - `📄 ` — Markdown file
  - `📎 ` — other file
  - `🕸️ ` — link graph node
  - `⭐ ` — favorites root and favorite entries
- Each prefix is reported by `rich.cells.cell_len` as exactly 3 terminal cells (2 for emoji + 1 for space).
