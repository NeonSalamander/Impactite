# Feature Specification: Remember User Theme

|**Feature Branch**: `017-remember-user-theme`

|**Created**: 2026-06-27

|**Status**: Draft

|**Input**: User description: "Не запоминается последняя использованная тема, по умолчанию при старте включается светлая тема оформления"

## Problem Statement

When the user changes the application theme during a session, the new selection is not restored on the next launch. The application starts with the light theme by default, forcing users who prefer a dark theme (or any other previously selected theme) to change it manually every time they open the application.

## User Scenarios & Testing

### User Story 1 - Theme choice persists between sessions (Priority: P1)

A user switches the application theme from the default to another theme (for example, a dark theme). They close the application and open it again later. The application starts with the same theme they last selected.

**Why this priority**: This directly addresses the reported bug — the chosen theme should be remembered across restarts.

**Independent Test**: Start the application, change the theme, restart the application, and verify the previously selected theme is active.

**Acceptance Scenarios**:

1. **Given** the application is running on the default theme, **When** the user selects a different theme, **Then** the application immediately applies that theme and remembers it.
2. **Given** the user has previously selected a non-default theme, **When** the application is launched again, **Then** it starts with the previously selected theme instead of the default light theme.

---

### User Story 2 - Light theme remains available (Priority: P2)

A user explicitly chooses the light theme. On the next launch the application starts in light mode, because that is the user's last deliberate choice.

**Why this priority**: Remembering the theme must apply to any theme choice, including light, not only to dark themes.

**Independent Test**: Set the theme to light, restart, and verify light theme is active.

**Acceptance Scenarios**:

1. **Given** the user selects the light theme, **When** the application restarts, **Then** it starts in light theme.

---

### Edge Cases

- The configuration file is missing or corrupted on startup; the application falls back to a safe default theme and does not crash.
- The previously saved theme name is no longer available (for example, after a theme was removed); the application falls back to the default theme and records the fallback.
- The user switches theme and immediately quits; the last selected theme is still the one restored next time.
- Multiple configuration files or command-line overrides are not affected; persisted theme applies to the same configuration used for the session.

## Requirements

### Functional Requirements

- **FR-001**: The application MUST save the user's selected theme when the theme changes.
- **FR-002**: On startup, the application MUST load and apply the last saved user theme before showing the main interface.
- **FR-003**: If no theme has ever been saved, the application MAY use the default light theme.
- **FR-004**: If the saved theme is invalid or unavailable, the application MUST fall back to the default theme and update the saved value to the fallback.
- **FR-005**: The theme toggle action (switching between light and dark variants of the same base theme) MUST continue to work without corrupting the saved base theme.

### Key Entities

- **Application theme**: The visual style applied to the Textual user interface.
- **Saved theme setting**: The theme name stored in the user's configuration file.

## Success Criteria

### Measurable Outcomes

- **SC-001**: After changing the theme and restarting the application, the active theme matches the last selected theme in 100% of valid configurations.
- **SC-002**: A user does not need to reselect their preferred theme more than once; subsequent launches restore it automatically.
- **SC-003**: If the configuration file is missing or contains an invalid theme name, the application starts successfully with the default theme and the outcome is observable to the user.

## Assumptions

- The application already has a configuration file path that is loaded on startup and writable while the application is running.
- Theme names are unique strings that can be stored and compared directly.
- The default fallback theme is the same light theme that currently appears on first launch.
