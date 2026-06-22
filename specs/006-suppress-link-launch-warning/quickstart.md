# Quickstart: Suppress External Link Launch Warnings

## Validate the Fix

### Setup

1. Start Impactite with your normal notes directory:
   ```bash
   uv run impactite
   ```
2. Open a note that contains both a raw URL and a Markdown external link:
   ```markdown
   # Link test

   Raw URL: https://ya.ru

   Markdown link: [Example](http://example.com)
   ```

### Expected Behavior

1. Click the raw URL `https://ya.ru`.
   - The browser opens `https://ya.ru`.
   - The TUI does **not** show any extra line at the top (no `kf.iconthemes: Icon theme "Breeze" not found.` or similar).
2. Click the Markdown link `Example`.
   - The browser opens `http://example.com`.
   - The TUI remains clean; no console output from the browser appears.

### Failure-Path Validation

1. Create or open a note containing `[Bad](http://this-protocol-does-not-exist.invalid/)`.
2. Click the link.
3. A localized error notification appears at the bottom of the screen; the application does not crash.

### Regression Checks

- Internal Markdown links still open the target note inside Impactite.
- External links inside fenced code blocks and inline code spans remain non-interactive.
- `python -m compileall src` exits without errors.
