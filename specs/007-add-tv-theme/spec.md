# Feature Specification: Add TV Theme

**Feature Branch**: `007-add-tv-theme`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "Добавить тему оформления 'TV', максимально полно копирующую внешний вид UI тулкита TurboVision"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select the TV Theme (Priority: P1) 🎯 MVP

As a user, I want to select a theme named "TV" from the application's theme list so that the entire interface is styled after the classic TurboVision toolkit.

**Why this priority**: Without the ability to choose the theme, the rest of the feature is unreachable. This is the core user value.

**Independent Test**: Open the app, choose the "TV" theme through the existing theme selector (hotkey or settings), and confirm the interface immediately updates to a TurboVision-inspired palette.

**Acceptance Scenarios**:

1. **Given** the application is running with any other theme, **When** the user selects the "TV" theme, **Then** all visible UI chrome uses the TurboVision color palette (dark blue background, cyan panels, yellow/white accents).
2. **Given** the user opens the theme list, **When** they look for available themes, **Then** a theme named "TV" is present and selectable.

---

### User Story 2 - TV Theme Applies Consistently (Priority: P2)

As a user, I want the TV theme to cover every common widget and surface so that the retro look is coherent and readable.

**Why this priority**: A partial theme feels broken; full coverage is required for the nostalgic TurboVision effect.

**Independent Test**: With the TV theme active, navigate through the note tree, editor, preview pane, status bar, modals, and menus. Each screen element should use TV-appropriate colors and remain readable.

**Acceptance Scenarios**:

1. **Given** the TV theme is active, **When** the user opens a note in view mode, **Then** the rendered Markdown, borders, and background all follow the TV palette.
2. **Given** the TV theme is active, **When** the user opens a dialog or modal, **Then** the dialog background, borders, and focused element highlight use the TV palette.
3. **Given** the TV theme is active, **When** a code block is shown, **Then** the block background and syntax highlighting remain readable against the dark-blue TV background.

---

### User Story 3 - TV Theme Persists Across Sessions (Priority: P3)

As a user, I want my TV theme choice to survive an app restart so that I don't have to reselect it every time.

**Why this priority**: Persistence is expected behavior for all existing themes; the new theme must match that convention.

**Independent Test**: Set the theme to TV, close the app, reopen it, and verify the UI still uses the TV theme.

**Acceptance Scenarios**:

1. **Given** the user has selected the "TV" theme, **When** the app restarts, **Then** the UI loads in the "TV" theme by default.
2. **Given** the app loads with the persisted "TV" theme, **When** the user checks the settings file, **Then** the saved theme value is "TV".

---

### Edge Cases

- What happens when the TV theme is active and the user toggles to a previously saved custom CSS file? The custom CSS should override or coexist without crashing the app.
- What happens when the terminal does not support the exact TurboVision colors? The theme should fall back to the closest available standard colors.
- What happens when the editor/code theme is synced automatically? The chosen editor theme should remain readable against the dark-blue TV application background.
- What happens when the user rapidly cycles themes? Each switch should complete cleanly without leftover artifacts from the previous theme.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a theme named "TV" in the theme selection list.
- **FR-002**: The "TV" theme MUST visually evoke the TurboVision toolkit using a dark blue dominant background, cyan panels/borders, and yellow or white highlights for focused/active elements.
- **FR-003**: The "TV" theme MUST apply to all core UI surfaces: sidebar/tree, editor/preview panes, status bar, dialogs, modals, menus, and scrollbars.
- **FR-004**: The "TV" theme MUST persist after the application is closed and reopened, using the same configuration mechanism as existing themes.
- **FR-005**: The existing theme-switching shortcut or command MUST cycle through the "TV" theme along with other available themes.
- **FR-006**: The "TV" theme MUST maintain readable contrast for text, code blocks, and highlighted elements.

### Key Entities

- **Theme "TV"**: A selectable application color theme inspired by TurboVision.
- **Config theme value**: The stored string that records the user's active theme; "TV" must be a valid value.
- **Editor/code theme pairing**: The associated code-highlighting theme used when "TV" is active; must remain readable on the TV application background.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can switch to the "TV" theme in under 2 seconds using the existing theme selector.
- **SC-002**: 100% of core UI surfaces described in FR-003 render with TV palette colors after activation.
- **SC-003**: The "TV" theme is restored on 100% of cold starts when it was the last selected theme.
- **SC-004**: Text and code blocks in the TV theme achieve a contrast ratio that users report as readable in a manual check.
- **SC-005**: No existing themes are broken or visually regressed by the addition of the TV theme.

## Assumptions

- The application already has a theme mechanism that can host a new theme entry without changing the architecture.
- TurboVision styling can be expressed within the Textual/Rich color system (no new UI framework is introduced).
- The TV theme is treated as a dark theme; if the implementation instead makes it a light theme, the existing light-theme tracking must be updated.
- Custom user CSS, if present, takes precedence over theme defaults in its specific scope.
- No new icons, fonts, or bitmaps are required; the theme is purely color and style.
