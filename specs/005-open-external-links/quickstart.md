# Quickstart: Validate Open External Links

## Prerequisites

- Python 3.14+
- `uv sync` completed in the project root
- A default web browser configured on the system
- A test note vault with at least one Markdown file

## Setup

1. Create or edit a note in your vault with the following content:

```markdown
# External link test

Visit https://ya.ru directly.
Or use a [Markdown link](https://example.com).

```text
This code block contains https://hidden.example.com and must NOT be clickable.
```
```

2. Launch Impactite:

```bash
uv run impactite /path/to/config.yaml
```

## Validation steps

1. Select the test note and make sure you are in **view mode** (not edit mode).
2. Hover over or look at the line with `https://ya.ru`. It should be styled as a link.
3. Click `https://ya.ru`. The system browser should open `https://ya.ru`.
4. Click the `Markdown link` text. The system browser should open `https://example.com`.
5. Scroll to the code block. The URL `https://hidden.example.com` must appear as plain text and must not respond to clicks.

## Error-path validation

1. Create a note with an obviously invalid URL such as `https://this-domain-does-not-exist-12345.invalid`.
2. Click the link.
3. Expect a non-technical error notification (for example, "Could not open link") instead of a traceback.

## Expected outcome

- Raw `http://`/`https://` URLs are interactive in view mode.
- Markdown inline links with `http://`/`https://` targets are interactive.
- Links inside code blocks are inactive.
- Failed opens show a friendly notification.
