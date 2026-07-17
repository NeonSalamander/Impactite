# Quickstart: Uniform 25% Overlay Dimming

## Validate the Feature

### Setup

1. Ensure Impactite launches with your notes directory:
   ```bash
   cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
   uv run impactite</path/to/config.yaml>
   ```

2. Use an isolated temp config if you do not want to touch the repo config:
   ```bash
   mkdir -p /tmp/impactite-test/notes
   echo -e "notes_path: /tmp/impactite-test/notes\nlanguage: en" > /tmp/impactite-test/config.yaml
   uv run impactite /tmp/impactite-test/config.yaml
   ```

### Run the Checks

1. **Dialog dimming**
   - Focus the directory tree, press `c` to open the directory color dialog.
   - Confirm the note viewer and tree behind the dialog are still visible but clearly darker than before the dialog opened.
   - Close the dialog and press `Ctrl+Shift+F` to open tag search; check the same.

2. **Context-menu dimming**
   - Right-click any directory in the tree.
   - Confirm the underlying tree remains visible through the overlay and is only slightly darker, not black.
   - Click outside the menu — it should close and the tree should return to normal brightness.

3. **Both themes**
   - If the app supports a light theme, toggle to it and repeat steps 1 and 2.
   - The dimming level should look similar, not disappear in dark theme or become too strong in light theme.

### Automated Smoke Tests

```bash
python -m compileall src
```

Use headless tests from `tasks.md` to confirm dialogs and context menus still open without crashing.
