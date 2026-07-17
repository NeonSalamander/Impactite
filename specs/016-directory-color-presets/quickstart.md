# Quickstart: Directory Color Presets

## Validate the Feature

### Setup

Create a temporary notes directory and config:

```bash
mkdir -p /tmp/impactite-test/notes/Subdir
touch /tmp/impactite-test/notes/Subdir/note.md
cat > /tmp/impactite-test/config.yaml <<EOF
notes_path: /tmp/impactite-test/notes
language: en
display:
  app_theme: dark
EOF
```

### Run

```bash
cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
uv run impactite /tmp/impactite-test/config.yaml
```

### Manual checks

1. Right-click a directory in the file tree (or press the configured shortcut).
2. Select **Directory settings**.
3. Confirm the modal shows:
   - Background colour input
   - Text colour input
   - A grid of 16 coloured preset buttons
4. Click a preset button while the background input is focused.
5. Confirm the background input is updated to the chosen preset value.
6. Click into the text-colour input, click a different preset button.
7. Confirm the text-colour input is updated.
8. Press `Enter` or the confirm action.
9. Confirm the directory is rendered with the selected colours and the modal closes.
10. Re-open the form and type a custom hex value manually; confirm it is accepted.

### Headless checks

```bash
python -m compileall src
uv run python /tmp/test_backdrop_smoke.py
uv run python /tmp/test_backdrop_overlays.py
```

Expected: all commands exit successfully.
