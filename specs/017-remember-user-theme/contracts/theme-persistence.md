# UI Contract: Remember User Theme

## Theme persistence contract

| Condition | Requirement |
|-----------|-------------|
| Application starts with a valid saved theme | The main window appears using that theme |
| Application starts with an invalid/missing saved theme | The main window appears using the default dark theme and the config is updated to the default |
| User presses the theme toggle action | The theme switches to the light/dark counterpart and the change is saved |
| Application restarts after a toggle | The theme active before shutdown is restored |

## Configuration contract

- The theme is read from `display.app_theme`.
- The theme is written back to `display.app_theme` whenever it changes.
- Writes preserve the YAML structure and all other configuration keys.
