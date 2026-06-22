# Quickstart: Add W311 Theme

## Validate the Theme

### Setup

1. Ensure Impactite launches with your notes directory:
   ```bash
   uv run impactite
   ```
2. If needed, set the active theme to "w311" by editing `config.yaml`:
   ```yaml
   display:
     app_theme: "w311"
   ```

### Run Scenarios

1. **Cold start with W311**
   - Launch the app.
   - Confirm the interface uses a light gray background, dark blue title bars, and black text.

2. **Switch to and from W311**
   - Start with another theme (e.g., `textual-dark` or `tv`).
   - Change `app_theme` to `w311` and restart.
   - Press `Ctrl+L` (or the configured light/dark toggle) and verify the theme switches cleanly.

3. **Editor readability**
   - Open a note containing a fenced code block.
   - The code block background and `github_light` syntax highlighting should be readable against the light gray chrome.

4. **Regression check**
   - Switch back to `textual-dark`, `textual-light`, and `tv`.
   - Confirm each theme still loads correctly and looks unchanged.

### Expected Outcomes

- `app.theme == "w311"` after startup when the config value is `"w311"`.
- "w311" appears in `_LIGHT_THEMES`.
- No exceptions during theme switches.
