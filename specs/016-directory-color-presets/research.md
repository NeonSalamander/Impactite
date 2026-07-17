# Research: Directory Color Presets

## Unknown 1: Which 16 preset colours should be offered?

**Decision**: Use a standard basic palette of 16 named web/SVG colours that are guaranteed to parse with the existing `Color.parse` call.

**Palette** (hex values for reference):
1. Black   — `#000000`
2. White   — `#ffffff`
3. Gray    — `#808080`
4. Red     — `#ff0000`
5. Green   — `#00ff00`
6. Blue    — `#0000ff`
7. Yellow  — `#ffff00`
8. Magenta — `#ff00ff`
9. Cyan    — `#00ffff`
10. DarkRed    — `#8b0000`
11. DarkGreen  — `#006400`
12. DarkBlue   — `#00008b`
13. Orange     — `#ffa500`
14. Purple     — `#800080`
15. Teal       — `#008080`
16. Pink       — `#ffc0cb`

**Rationale**: These colours are widely recognised, distinct, and accepted by Textual/Rich `Color.parse`. They cover the basic set the user described.

## Unknown 2: How does a preset button know whether to fill the background or text input?

**Decision**: Track the most recently focused colour input. When a preset button is pressed, fill that input; if no input has been focused since the modal opened, fall back to the background-colour input.

**Rationale**:
- Simple to explain and consistent with the form flow (background is the first field).
- Avoids needing two separate palettes or mode-switching controls.
- Preserves the user's current context (focus).

## Unknown 3: Should the preset buttons replace manual input?

**Decision**: No. Presets populate the inputs, but the existing input fields remain visible and editable. The existing confirm logic still reads the inputs and validates both values.

**Rationale**: The user explicitly asked for presets as an additional option, not a replacement.

## Unknown 4: Keyboard accessibility

**Decision**: Preset buttons are regular Textual `Button` widgets, so they are reachable via `Tab` and activatable with `Space`/`Enter` without extra work.

**Rationale**: Minimises custom code and respects platform conventions.
