# Quickstart: Directory Tree Colors

## Validate the Feature

### Setup

1. Ensure Impactite launches with your notes directory:
   ```bash
   uv run impactite
   ```
2. Create a few directories through the UI if your vault is empty.

### Run Scenarios

1. **Assign colors to a directory**
   - Select a directory in the file tree.
   - Trigger the "Set directory color" action (e.g., a hotkey or context action configured for this feature).
   - Enter a background color (e.g., `#2d2d2d`) and a text color (e.g., `#ffd700`), then confirm.
   - The directory row immediately renders with the chosen colors.

2. **Color multiple directories differently**
   - Repeat the steps above for at least two different directories.
   - Verify that each directory shows its own colors and that files/notes inside remain unchanged.

3. **Persist across restarts**
   - Set colors for a directory, then close the app.
   - Reopen the app and confirm the same colors are applied.
   - Check `config.yaml`: the `directory_colors` key should contain the relative path and color pair.

4. **Reset to default**
   - Select a customized directory and trigger the "Reset directory color" action.
   - The directory reverts to the default theme styling and its entry is removed from `directory_colors`.

### Expected Outcomes

- `directory_colors` appears in `config.yaml` only after at least one directory is customized.
- Customized directories render with the user-defined background and text color in every tree refresh.
- Non-customized directories look identical to the behavior before this feature.
- Invalid color strings are rejected without modifying the config.
