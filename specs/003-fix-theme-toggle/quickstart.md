# Quickstart: Fix Theme Toggle Validation

## Prerequisites

- Repository cloned and dependencies synced: `uv sync`
- Working configuration file `config.yaml` with a non-default light theme, e.g.:
  ```yaml
  display:
    app_theme: "rose-pine-dawn"
  ```

## Validation Steps

### 1. Syntax check

```bash
uv run python -m compileall src
```

**Expected outcome**: no compile errors.

### 2. Launch the application

```bash
uv run impactite config.yaml
```

**Expected outcome**: the application opens using the theme configured in `config.yaml` (`rose-pine-dawn` in the example).

### 3. Toggle to dark mode

Press `Ctrl+L`.

**Expected outcome**: the UI switches to a dark theme. If a dark counterpart is known (e.g., `rose-pine-moon`), that theme is used; otherwise it falls back to `textual-dark`.

### 4. Toggle back to the original theme

Press `Ctrl+L` again.

**Expected outcome**: the UI returns to the originally configured theme (`rose-pine-dawn`).

### 5. Verify persistence was not corrupted

Close the application (`Ctrl+Q`) and check `config.yaml`:

```bash
grep "app_theme" config.yaml
```

**Expected outcome**: `app_theme` still equals `rose-pine-dawn` (or whatever theme you started with). It must **not** be `textual-light` or `textual-dark`.

### 6. Restart and confirm theme is restored

```bash
uv run impactite config.yaml
```

**Expected outcome**: the application opens with the original configured theme (`rose-pine-dawn`).

### 7. Edge case: missing theme

1. Stop the application.
2. Edit `config.yaml` and set `app_theme` to a non-existent theme name.
3. Restart the application.

**Expected outcome**: the application launches with the default `textual-dark` theme and remains usable.

## Definition of Done

- Steps 1–6 pass without manual reconfiguration.
- Step 7 degrades gracefully without an error dialog.
- `config.yaml` is modified only when the user explicitly changes the theme, never by `Ctrl+L`.
