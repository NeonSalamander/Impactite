# Quickstart: Fix Directory Tree Line Offset

## Validate the Fix

### Setup

Use an isolated temp config:

```bash
mkdir -p /tmp/impactite-test/notes
mkdir -p /tmp/impactite-test/notes/Subdir
touch /tmp/impactite-test/notes/note.md
touch /tmp/impactite-test/notes/Subdir/another.md
cat > /tmp/impactite-test/config.yaml <<YAML
notes_path: /tmp/impactite-test/notes
language: en
YAML
cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
uv run impactite /tmp/impactite-test/config.yaml
```

### Manual Checks

1. **Default tree view**
   - Look at the first several rows of the directory tree.
   - Confirm that every row's left edge aligns after the tree guides; no row is shifted by one character.

2. **Styled directory**
   - Select a directory and press `c` to set foreground or background colour.
   - Confirm the coloured row still aligns with neighbour rows.

3. **Expand/collapse**
   - Expand and collapse directories.
   - Confirm alignment is preserved during state changes.

4. **Both themes**
   - If a light theme is available, switch to it and repeat the checks.

### Automated Checks

```bash
cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
python -m compileall src
```

Run the headless smoke test from `tasks.md` to confirm the app still starts and the tree is populated.
