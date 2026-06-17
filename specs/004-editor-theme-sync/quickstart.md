# Quickstart: Editor Theme Sync Validation

## Prerequisites

- Repository cloned and dependencies synced: `uv sync`
- A sample note exists (e.g., `samples/test_links.md` or any file under `notes/`)

## Syntax Check

```bash
uv run python -m compileall src
```

Expected outcome: no compilation errors.

## Manual Validation Steps

### Scenario 1: Light mode editor theme on open

1. Start the application:
   ```bash
   uv run impactite
   ```
2. If the app is not already in a light theme, press `Ctrl+L` to toggle to light mode.
3. Select a note and open it for editing (`e` or the configured edit-mode hotkey).
4. **Expected**: the code editor background is light and syntax highlighting uses a light theme.

### Scenario 2: Toggle back to dark while editing

1. With a note open in edit mode in light theme, press `Ctrl+L`.
2. **Expected**: the editor switches to the configured dark syntax theme immediately.
3. Press `Ctrl+L` again.
4. **Expected**: the editor returns to a light syntax theme immediately.

### Scenario 3: Switch between view and edit modes

1. Open a note in edit mode in light theme.
2. Press `v` (or the configured view-mode hotkey) to switch to view mode.
3. Press `e` to return to edit mode.
4. **Expected**: the editor remains in the light theme.

### Scenario 4: Dark mode unchanged

1. Start the application in dark mode.
2. Open a note for editing.
3. **Expected**: the editor uses the dark syntax theme configured in `config.yaml`.

## Automated Smoke Test (optional)

A minimal Textual pilot test can verify the theme value on the editor widget after toggling and entering edit mode. See `contracts/editor-theme.md` for the expected behavior contract.
