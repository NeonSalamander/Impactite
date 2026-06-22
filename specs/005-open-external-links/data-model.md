# Data Model: Open External Links

## Entities

### `ExternalLink`

A clickable external reference discovered in a rendered note line.

| Field        | Type   | Description |
|--------------|--------|-------------|
| `url`        | `str`  | Full `http://` or `https://` target URL. |
| `text`       | `str`  | Text displayed to the user. For raw URLs this is the URL itself; for Markdown links this is the link text. |
| `start`      | `int`  | Column index (in the rendered Rich text) where the clickable region starts. |
| `end`        | `int`  | Column index (in the rendered Rich text) where the clickable region ends. |
| `source_kind`| `str`  | Either `"raw"` for an explicit URL or `"markdown"` for a Markdown inline link. |

## Core helpers

### `LinkScanner`

A small, stateless helper (functions or class) in `core.py` responsible for:
1. Finding raw `http://`/`https://` URLs in a plain text line.
2. Finding Markdown inline links and classifying their targets as internal or external.
3. Returning a list of `ExternalLink` data (or simple dicts) that `MarkdownViewer` can use for hit-testing and rendering.

It does not import Textual, Rich, or the App class.

### `open_url(url: str)`

A `core.py` helper that opens the given URL through the system's default handler.

- Uses the Python stdlib `webbrowser` module.
- Raises a domain-specific exception (`OpenUrlError`) on failure so the UI can show a localized notification.

## State transitions

No persistent state. Runtime state per rendered note:

```
MarkdownViewer._link_lines: list[Optional[list[ExternalLink]]]
```

On every `update_content` call this list is rebuilt together with the existing internal-link and tag lines.
