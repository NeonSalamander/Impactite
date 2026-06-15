# Research: Current Note In-Editor Search

## Unknowns Resolved

No `[NEEDS CLARIFICATION]` markers were present in the specification. The following design decisions were made based on the existing project context.

## Decisions

### Search interaction model

- **Decision**: Use a dedicated Textual `ModalScreen` for the search input.
- **Rationale**: Textual already uses modal screens for tag search, confirmation dialogs, and template selection. Reusing the same primitive keeps the codebase consistent.
- **Alternatives considered**: Inline input in the status bar (rejected because it would compete with status information and obscure the requested overlay-with-shadow UX).

### Dialog appearance

- **Decision**: Render the modal with a transparent or very lightly tinted background and a CSS `layer: notification`-style shadow.
- **Rationale**: The requirement explicitly states the dialog must not darken the whole area. A translucent overlay with a drop shadow preserves context and matches the requested visual behavior.
- **Alternatives considered**: Full-screen dim (rejected per requirement); no background at all (rejected because the dialog would visually merge with note text).

### Search algorithm

- **Decision**: Case-insensitive literal substring matching using Python `str.lower()` plus `str.find` / `re.finditer` for non-overlapping occurrences.
- **Rationale**: Matches the specification's assumption of literal search and is sufficient for notes up to 10,000 words while staying within performance targets.
- **Alternatives considered**: Regular-expression search (deferred to a future version; would add ambiguity around case-insensitive regex semantics).

### Highlighting in view mode

- **Decision**: Reuse the existing `MarkdownViewer` highlight infrastructure (`_line_highlights` / `_apply_highlights_range`) and add a second highlight style for the "current match".
- **Rationale**: `MarkdownViewer` already computes per-line highlights for full-text search terms. Extending it for a second tier of highlights avoids duplicate rendering logic.
- **Alternatives considered**: Re-render the whole viewer on every keystroke (rejected as it would break existing link/checkbox click tracking).

### Highlighting in edit mode

- **Decision**: Use the `EditorTextArea` selection styling already used for current full-text-search matches (`text-area--selection`).
- **Rationale**: `TextArea` has built-in selection support; showing the current match as a selection and highlighting other occurrences as secondary selections is idiomatic and requires no custom painting.
- **Alternatives considered**: Custom content overlay in the editor (rejected because `TextArea` does not support arbitrary overlays).

### Result navigation

- **Decision**: Reuse the existing previous/next result controls already bound in `MarkdownEditorApp` for full-text search.
- **Rationale**: The user explicitly requested reuse. The controls can switch behavior depending on whether the in-note search dialog or the global search view is active.
- **Alternatives considered**: New dedicated keys for in-note navigation (rejected to satisfy the reuse requirement and keep the learning curve flat).

## Open Questions (for future iterations)

- Whether to support regex or whole-word search in later versions.
- Whether to remember the last query per note or globally.
