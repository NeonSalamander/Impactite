# Quickstart: Visible Context-Menu Overlay

## Validate the Fix

### Setup

Use an isolated temp config to avoid touching the repo config:

```bash
mkdir -p /tmp/impactite-test/notes
cat > /tmp/impactite-test/config.yaml <<YAML
notes_path: /tmp/impactite-test/notes
language: en
YAML
cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
uv run impactite /tmp/impactite-test/config.yaml
```

### Manual Checks

1. **Context menu**
   - Right-click any directory in the tree.
   - Confirm the note tree behind the menu is fully visible; only the small menu box should stand out.
   - Click outside the menu — it should close.

2. **Dialog**
   - Focus a directory and press `c`.
   - Confirm the directory color dialog is readable and the workspace behind it is somewhat dimmed but still visible.

3. **Both themes**
   - If a light theme is available, switch to it and repeat steps 1 and 2.
   - The context menu should never hide the workspace; dialogs should dim but not obscure.

### Automated Checks

```bash
cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
python -m compileall src
```

Run the headless smoke tests from `tasks.md` to confirm no exceptions are raised when opening the menu or a dialog.
