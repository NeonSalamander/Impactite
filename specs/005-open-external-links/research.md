# Research: Open External Links

## Unknown 1: How should the application detect external links in note text?

**Decision**: Detect two forms consistently inside `core.py`:
- Markdown inline links: `\[([^\]]+)\]\(([^)]+)\)` — already partially parsed by the viewer.
- Raw URLs: a regex that matches `http://` or `https://` followed by a valid domain/path fragment.

**Rationale**: The feature explicitly asks for both explicit text URLs and Markdown markup links. Centralising detection in `core.py` keeps `app.py` focused on rendering and allows unit testing. Code blocks/inline code are excluded by the caller (`MarkdownViewer`) before detection runs, matching existing behaviour.

**Alternatives considered**:
- Use Rich's automatic URL highlighter. Rejected because it does not give the application control over click handling or error feedback.
- Rely only on the existing Markdown parser (`markdown` library) to emit `<a>` tags. Rejected because the viewer does not render HTML; it uses a custom line-by-line renderer.

## Unknown 2: How should links be activated and opened in the browser?

**Decision**: Track clickable external links in the viewer the same way internal links are already tracked (`_link_lines`), then handle click coordinates in `on_viewer_log_clicked`. For activation, use Python's `webbrowser.open(url)` via a small helper in `core.py`.

**Rationale**: This reuses the existing click-infrastructure and keeps the UI in control of the user flow. `webbrowser.open` is cross-platform and part of the stdlib, avoiding new dependencies.

**Alternatives considered**:
- Use Rich `[link=url]...[/link]` markup and rely on terminal OSC 8 hyperlinks. Rejected because support varies across terminals and the application cannot provide consistent error handling or keyboard activation.
- Shell out to `xdg-open`/`open` directly. Rejected because `webbrowser` already abstracts these commands and falls back gracefully.

## Unknown 3: How should external links be visually styled?

**Decision**: Render external links with Rich markup (e.g., underlined and coloured) similar to internal links, but with a distinct colour or the same link style. The exact class/style is left to the implementation phase; it must be visible in both light and dark themes.

**Rationale**: Visual distinction is a stated requirement. Using Rich markup keeps it consistent with the existing inline formatting and does not require extra CSS classes for the first iteration.

**Alternatives considered**:
- Use Textual `DEFAULT_CSS` classes. Possible, but inline Rich markup is simpler for text inside a `RichLog` and matches current internal-link rendering.
