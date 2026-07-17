# Feature Specification: Directory Context Menu

|**Feature Branch**: `010-directory-context-menu`|

|**Created**: 2026-06-26

|**Status**: Draft

|**Input**: User description: "Нужно что бы при клике правой кнопкой мышки на каталоге открывалось контекстное меню в котором можно было выбрать настройки каталога и указать в том числе цвет фона и шрифта которые потом сохранятся в настройках"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open Directory Settings from the Context Menu (Priority: P1) 🎯 MVP

As a user, I want to right-click on a directory in the directory tree and open its settings so that I can customize how that directory looks without navigating through unrelated menus.

**Why this priority**: This is the core entry point of the feature. Without the context menu and a way to open settings, the user cannot reach any customization options for a directory.

**Independent Test**: Right-click a directory and verify that a context menu appears with an option to open directory settings.

**Acceptance Scenarios**:

1. **Given** a directory is visible in the directory tree, **When** the user right-clicks on it, **Then** a context menu appears near the pointer with an option labeled for directory settings.
2. **Given** the context menu is open for a directory, **When** the user selects the directory settings option, **Then** a settings dialog opens.

---

### User Story 2 - Set and Persist Directory Colors from the Settings Dialog (Priority: P2)

As a user, I want the directory settings dialog to let me choose a background color and a text/label color so that my chosen directory appearance is saved and applied.

**Why this priority**: Setting background and text colors is the specific customization requested. This story delivers the visible value after the menu entry point exists.

**Independent Test**: Open directory settings, enter a background color and a text color, confirm, and verify the directory row renders with the chosen colors and that the choices survive an application restart.

**Acceptance Scenarios**:

1. **Given** the directory settings dialog is open, **When** the user enters a background color and a text color and confirms, **Then** the directory row in the tree immediately uses those colors and the colors are saved in user settings.
2. **Given** a directory already has saved colors, **When** the user opens its settings dialog again, **Then** the current background and text colors are pre-filled.
3. **Given** the user enters an invalid color value in the dialog, **When** they attempt to confirm, **Then** the dialog rejects the value, shows feedback, and does not save or apply anything.

---

### User Story 3 - Reset Directory Colors from the Context Menu (Priority: P3)

As a user, I want to remove the custom colors from a directory so that it reverts to the default appearance and the stored setting is cleaned up.

**Why this priority**: Users make mistakes or change their minds. A reset path is a standard expectation for any personalization feature and keeps the settings list tidy.

**Independent Test**: Right-click a directory that has custom colors and choose the reset option; verify the directory reverts to default styling and the saved colors are removed from settings.

**Acceptance Scenarios**:

1. **Given** a directory has custom colors saved, **When** the user opens its context menu and chooses the reset option, **Then** the directory immediately reverts to default styling and its color entry is removed from settings.
2. **Given** a directory has no custom colors, **When** the reset option is invoked, **Then** the directory appearance does not change and settings remain unaffected.

---

### Edge Cases

- What happens if the user right-clicks on a file, the root of the tree, or an empty area? The context menu does not offer directory-specific settings because those items are not directories.
- What happens if a directory is renamed or moved outside the application? The stored color association remains tied to the original path and will not follow the directory.
- What happens if a directory with saved colors is deleted? The stale color entry should not affect any visible directory.
- What happens if the user cancels the settings dialog? No settings are changed and no colors are applied.
- What happens if a parent and child directory have different colors? Each directory keeps its own colors; child directories do not inherit colors from their parents.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a context menu when the user right-clicks a directory in the directory tree.
- **FR-002**: The context menu MUST include an option that opens the directory's settings.
- **FR-003**: The directory settings dialog MUST provide fields for the user to choose a background color and a text/label color.
- **FR-004**: System MUST pre-fill the settings dialog with any colors already saved for that directory.
- **FR-005**: System MUST save the chosen colors to user settings and apply them to the directory row when the user confirms the dialog.
- **FR-006**: System MUST reject invalid color entries in the settings dialog and provide feedback without saving or applying changes.
- **FR-007**: System MUST allow the user to reset a directory's colors to the default application styling from the context menu.
- **FR-008**: The context menu MUST NOT offer directory-specific settings for files, the tree root, or empty areas of the tree.

### Key Entities *(include if feature involves data)*

- **Directory settings dialog state**: The temporary state of a directory settings interaction, including the currently edited background and text colors.
- **Directory color preference**: A pair of colors (background and text/label) associated with one directory path within the current vault; stored as user settings.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open directory settings from the context menu in two interactions or fewer (right-click + select option).
- **SC-002**: After confirming a color change, the directory row reflects the new colors within 1 second.
- **SC-003**: Saved directory colors are still applied after the application is closed and reopened.
- **SC-004**: Users can reset a directory to default styling in two interactions or fewer from the context menu.
- **SC-005**: Invalid color values are rejected before any settings are changed.

## Assumptions

- The application already provides a directory tree where directories are visually distinct from files.
- A right-click is the primary interaction for opening the context menu; a keyboard alternative is out of scope for this feature.
- The directory settings dialog focuses on background and text/label colors only; other kinds of directory settings are out of scope.
- Color persistence follows the same user settings storage used for other application preferences.
- Changes made in the dialog apply to the selected directory only and do not affect child or parent directories.
