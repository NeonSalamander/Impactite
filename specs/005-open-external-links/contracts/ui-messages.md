# UI Contract: External Link Activation

## Message interface

### `MarkdownViewer.LinkClicked` (existing)

Used for internal wiki-style links (`[[note]]` or `[text](note.md)`).

- `target: str` — relative or absolute path to another note.
- `text: str` — displayed link text.

Behaviour: the App resolves `target` as a `Path` and navigates to that note.

### `MarkdownViewer.ExternalLinkClicked` (new)

Used for `http://` and `https://` links, both raw URLs and Markdown inline links.

- `url: str` — full external URL.
- `text: str` — displayed link text.

Behaviour: the App calls `core.open_url(url)` and shows a notification if the URL cannot be opened.

## Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `core.py` | Detect external links in a note line; provide `open_url(url)` helper. |
| `MarkdownViewer` (app.py) | Render external links as styled, clickable text; build `_link_lines` hit-test data; post `ExternalLinkClicked` on click. |
| `App` (app.py) | Handle `ExternalLinkClicked` by opening the URL and surfacing errors via `self.notify`. |

## Error handling contract

- `core.open_url` must never raise a generic exception. It raises a single domain exception (`OpenUrlError`) with a human-readable message.
- `App` handler catches `OpenUrlError` and calls `self.notify(message, severity="error")` using a localized key.
