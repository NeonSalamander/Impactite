# Quickstart: Directory Context Menu

## Validate the Feature

### Setup

1. Ensure Impactite launches with your notes directory:
   ```bash
   cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
   uv run impactite
   ```
2. Create a few directories through the UI if your vault is empty.

### Run Scenarios

1. **Open context menu on a directory**
   - Right-click a directory in the file tree.
   - Verify a small menu appears near the pointer with options "Directory settings" and "Reset color".

2. **Set colors via the context menu**
   - Select "Directory settings".
   - Enter a background color (e.g., `#2d2d2d`) and a text color (e.g., `#ffd700`), then confirm.
   - The directory row immediately renders with the chosen colors.

3. **Reset colors via the context menu**
   - Right-click the customized directory again.
   - Select "Reset color".
   - The directory row reverts to the default application styling and the entry is removed from `config.yaml`.

4. **Right-click on files or empty tree area**
   - Right-click a file or an empty area of the tree.
   - Verify that the directory-specific menu does **not** appear.

### Expected Outcomes

- Right-clicking only directories opens the context menu.
- The "Directory settings" option opens the existing color dialog.
- The "Reset color" option removes stored colors for that directory.
- `config.yaml` is updated only when the user confirms a color change.
