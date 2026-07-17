# UI Contract: Directory Color Presets

## Visual behaviour contract

| Condition | Requirement |
|-----------|-------------|
| Directory colour modal is open | Background input, text input, and 16 preset buttons are visible. |
| User clicks a preset button while background input is focused | The background input is set to the preset value. |
| User clicks a preset button while text input is focused | The text input is set to the preset value. |
| User clicks a preset button when neither input is focused | The background input is set to the preset value. |
| User types a valid colour manually | The typed value is used; the input is not overwritten unless a preset is pressed. |
| User confirms the modal | Both current input values are validated and, if valid, saved as the directory style. |

## Preset values

The 16 preset colours are documented in [research.md](research.md). Each value is a string parseable by the existing colour parser.

## Accessibility

- Each preset button is focusable via keyboard.
- Activating a focused preset button has the same effect as clicking it.
