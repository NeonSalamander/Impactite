# Quickstart: Modal and Context Menu Backdrop Dimming

## Validate the Feature

### Setup

1. Ensure Impactite launches with your notes directory:
   ```bash
   cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
   uv run impactite [path/to/config.yaml]
   ```

### Manual validation scenarios

1. **Dialog backdrop is not black**
   - Select a directory in the tree and press the `c` hotkey to open the directory-color dialog.
   - Expected: the note/tree behind the dialog is still visible, only slightly darker.

2. **Context menu backdrop is not black**
   - Right-click a directory in the tree to open the context menu.
   - Expected: the folder tree behind the menu remains visible, only slightly darker.

3. **Consistency between overlays**
   - Open the tag-search dialog (`Ctrl+T`) and the directory-color dialog (`c`).
   - Expected: both dialogs dim the background by the same amount.

4. **Light theme check**
   - Switch to a light theme (`Ctrl+L`) and reopen a dialog/context menu.
   - Expected: the backdrop is a subtle gray, not white or black.

5. **Syntax check**
   ```bash
   cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
   python -m compileall src
   ```
   Expected: no errors.

6. **Smoke test**
   ```bash
   cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
   uv run impactite [path/to/config.yaml]
   ```
   Expected: app launches to the first screen without errors.
