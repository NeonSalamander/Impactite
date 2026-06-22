# Quickstart: Add TV Theme

## Validate the Theme

### Setup

1. Ensure Impactite launches with your notes directory:
   ```bash
   uv run impactite
   ```
2. If needed, set the active theme to "tv" by editing `config.yaml`:
   ```yaml
   display:
     app_theme: tv
   ```

### Expected Behavior

1. **Cold start with TV theme**:
   - Close and reopen the app.
   - The background is dark blue, borders/panels are cyan, and focused elements are highlighted in yellow/white.
2. **Switching into TV theme at runtime**:
   - Start with any other theme.
   - Change `display.app_theme` to `tv` and reload, or trigger the existing theme toggle until TV is selected.
   - The UI immediately updates to the TurboVision palette.
3. **Toggle out of TV theme**:
   - Press `Ctrl+L` while TV is active.
   - The app switches to the default light theme.
4. **Editor readability**:
   - Open a note containing a fenced code block.
   - The code block background and syntax highlighting remain readable against the dark-blue background.
5. **Persistence**:
   - Switch to TV, close the app, reopen it.
   - Confirm `config.yaml` still contains `display.app_theme: tv` and the UI loads in TV mode.

### Regression Checks

- Existing themes (textual-dark, textual-light, catppuccin, etc.) render unchanged.
- Code blocks in light themes still use a light pygments theme; in dark themes they use the configured dark syntax theme.
- `python -m compileall src` exits without errors.
