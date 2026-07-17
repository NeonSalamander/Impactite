# Quickstart: Keep Tree Icons Aligned

## Validate the Fix

### Setup

Use an isolated temp config so the repo config is not modified:

```bash
mkdir -p /tmp/impactite-test/notes/Subdir
touch /tmp/impactite-test/notes/note.md
touch /tmp/impactite-test/notes/Subdir/other.txt
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

1. Inspect the file tree sidebar.
2. Confirm each row has an emoji prefix:
   - `📁 Subdir`
   - `📄 note.md`
   - `📎 other.txt`
3. Confirm the fourth visible row is aligned with rows above and below it.
4. Expand/collapse `Subdir`; confirm children remain aligned.
5. Press `c` on a directory, set a colour; confirm the coloured row stays aligned and keeps its icon.
6. Switch theme (default shortcut) and confirm icons and alignment persist.

### Headless smoke validation

```bash
python -m compileall src
uv run python /tmp/test_backdrop_smoke.py
uv run python /tmp/test_backdrop_overlays.py
```

Expected result: all commands pass without exceptions.
