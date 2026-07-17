# Quickstart: Remember User Theme

## Validate the Feature

### Setup

Use a temporary configuration file to avoid dirtying the workspace config:

```bash
mkdir -p /tmp/impactite-theme-test/notes
(\
echo "notes_path: /tmp/impactite-theme-test/notes"; \
echo "language: en"; \
echo "display:"; \
echo "  app_theme: w311" \
) > /tmp/impactite-theme-test/config.yaml
```

### Scenario 1: Theme survives restart

1. Start the application:

```bash
cd /home/kandellak/__MAIN_SCRAP__/work/Impactite
uv run impactite /tmp/impactite-theme-test/config.yaml
```

2. Press `Ctrl+L` to switch to the dark variant.
3. Quit with `Ctrl+Q`.
4. Check the config file:

```bash
grep app_theme /tmp/impactite-theme-test/config.yaml
```

**Expected outcome**: `app_theme` now equals the dark theme name (for example, `"textual-dark"`), not `"w311"`.

5. Start the application again with the same config.

**Expected outcome**: The application starts in the dark theme.

### Scenario 2: Invalid saved theme falls back

1. Overwrite the config with an invalid theme:

```bash
sed -i 's/app_theme:.*/app_theme: "not-a-theme"/' /tmp/impactite-theme-test/config.yaml
```

2. Start the application.

**Expected outcome**: It starts with the default dark theme and `app_theme` is rewritten to the fallback value.

### Automated contract test

Run the headless test added for this feature:

```bash
uv run python /tmp/test_theme_persistence.py
```

**Expected outcome**: `THEME PERSISTENCE TEST PASSED`
