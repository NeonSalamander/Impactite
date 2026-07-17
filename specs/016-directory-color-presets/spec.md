# Feature Specification: Directory Color Presets

|**Feature Branch**: `016-directory-color-presets`

|**Created**: 2026-06-27

|**Status**: Draft

|**Input**: User description: "В форме настроек каталога нужно добавить кнопки для указания одного из 16 базовых цветов для цвета фона или цвета шрифта, что бы была возможность не только вводить код цвета а дополнительно использовать предустановленные"

## User Scenarios & Testing

### User Story 1 - Pick a preset color for the directory background (Priority: P1)

A user opens the directory colour settings form for a directory. They do not remember the hex code they want. They click one of the preset colour buttons and the selected colour is applied as the directory background colour.

**Why this priority**: This directly satisfies the request — provide preset colours so the user does not have to type a colour code.

**Independent Test**: Open the directory colour form, press a preset colour button, and confirm the form uses that value.

**Acceptance Scenarios**:

1. **Given** the directory colour form is open with the background input active, **When** the user presses a preset colour button, **Then** the background colour input is filled with the selected preset value.
2. **Given** the user has selected a preset for the background colour, **When** they confirm the form, **Then** the directory receives that background colour.

---

### User Story 2 - Pick a preset color for the directory text colour (Priority: P1)

A user opens the directory colour settings form. They want to change the text colour to something standard without typing a colour code. They focus the text-colour input, press a preset colour button, and the text colour is set.

**Why this priority**: The request explicitly mentions both background and text colour presets.

**Independent Test**: Open the directory colour form, switch focus to the text-colour input, press a preset colour button, and confirm the form uses that value.

**Acceptance Scenarios**:

1. **Given** the directory colour form is open with the text-colour input active, **When** the user presses a preset colour button, **Then** the text-colour input is filled with the selected preset value.
2. **Given** the user has selected a preset for the text colour, **When** they confirm the form, **Then** the directory receives that text colour.

---

### User Story 3 - Switch between preset and manual entry (Priority: P2)

A user can still type a colour code manually if the preset palette does not contain the exact colour they need.

**Why this priority**: The request says presets should be an additional option, not a replacement for manual input.

**Independent Test**: Open the form, type a custom colour code in either input, and confirm the form still accepts it.

**Acceptance Scenarios**:

1. **Given** the preset palette is visible, **When** the user types a valid colour code into an input field, **Then** the form uses the typed value instead of any preset.
2. **Given** the user has typed a custom colour code, **When** they press a preset button, **Then** the input is replaced by the preset value.

---

### Edge Cases

- The user presses a preset button when no colour input was ever focused; the background input receives the value by default.
- The user presses a preset for one input, then focuses the other input and presses a different preset; the second input receives the new value.
- The user can still focus a preset button with the keyboard or mouse to click it, and the value goes to the previously selected input.
- The user confirms the form without changing either input; previous values (if any) are preserved.
- The user types an invalid colour code; existing validation still rejects it.

## Requirements

### Functional Requirements

- **FR-001**: The directory colour form MUST display a compact palette of 16 clearly identifiable preset colours that does not dominate the form.
- **FR-002**: Each preset colour button MUST set the colour input that the user has selected (background or text). The form MUST keep track of the user's last selected input, even when the preset button itself receives focus for clicking.
- **FR-003**: Pressing a preset button MUST NOT require the user to type the colour code manually.
- **FR-004**: The existing manual colour-code inputs MUST remain available and functional.
- **FR-005**: The form MUST continue to validate both selected colours before confirmation.
- **FR-006**: The preset palette MUST be usable with keyboard or mouse.
- **FR-007**: Existing directory colour data MUST be preserved when the feature is added.

### Key Entities

- **Directory Colour Form**: The modal used to edit background and text colours for a directory.
- **Preset Colour Palette**: A set of 16 basic colours shown as selectable buttons inside the form.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A user can set either the background or text colour for a directory using only the preset palette, without typing a colour code, in under 10 seconds.
- **SC-002**: At least 16 distinct preset colours are available.
- **SC-003**: Manual colour-code entry continues to work for valid values (and invalid values are still rejected).
- **SC-004**: No existing saved directory colours are lost or changed after the update.
- **SC-005**: The preset palette fits compactly inside the directory colour form and does not push important controls off-screen.

## Assumptions

- The 16 preset colours are the standard basic set (black, white, grey, red, green, blue, yellow, magenta, cyan, dark red, dark green, dark blue, orange, purple, olive/teal, and a second light/dark neutral).
- Presets set values using the same format that the manual inputs accept (e.g., hex codes or named colours parseable by the existing colour parser).
- The palette is part of the directory settings form only; other colour pickers are out of scope.
