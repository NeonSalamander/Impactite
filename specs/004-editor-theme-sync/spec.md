# Feature Specification: Editor Theme Sync

**Feature Branch**: `004-editor-theme-sync`

**Created**: 2026-06-17

**Status**: Draft

**Input**: User description: "при включеной через ctrl+l 'светлой теме' открытие на редактирование заметки все равно в 'темной' теме, надо фиксить"

## User Scenarios & Testing

### User Story 1 - Light Mode Editor Uses Light Syntax Theme (Priority: P1)

When the application is switched to a light theme via `Ctrl+L`, opening any note for editing must display the code editor with a light syntax theme instead of the dark one.

**Why this priority**: This is the core bug reported by the user; without this fix the editor remains visually inconsistent with the rest of the UI in light mode.

**Independent Test**: Toggle to a light theme, open a note in edit mode, and visually confirm that the editor background and code highlighting follow a light theme (e.g., `github_light`).

**Acceptance Scenarios**:

1. **Given** the user has pressed `Ctrl+L` and the app is using a light theme, **When** the user opens an existing note for editing, **Then** the text editor is rendered with a light syntax theme.
2. **Given** the user is already editing a note in dark mode, **When** the user presses `Ctrl+L` to switch to light mode, **Then** the editor immediately updates to a light syntax theme without closing or reopening the note.

---

### User Story 2 - Dark Mode Editor Returns to Dark Syntax Theme (Priority: P2)

When the user toggles back to a dark application theme, the editor must switch back to the configured dark syntax theme.

**Why this priority**: Restoring the original dark editor theme is required to keep the experience consistent when the user toggles between modes.

**Independent Test**: From light mode, press `Ctrl+L` to return to dark mode and verify the editor uses the configured dark syntax theme.

**Acceptance Scenarios**:

1. **Given** the app is currently in light mode with a light editor theme, **When** the user presses `Ctrl+L` to switch to dark mode, **Then** the editor is rendered with the configured dark syntax theme.
2. **Given** a dark syntax theme is configured in `config.yaml`, **When** the app starts in dark mode and a note is opened for editing, **Then** the editor uses that configured dark syntax theme.

---

### User Story 3 - Theme Persists When Switching Between View and Edit Modes (Priority: P3)

Switching between viewing and editing the same note must not reset or desynchronize the editor theme.

**Why this priority**: Prevents a regression where entering/leaving edit mode could leave the editor with the wrong theme.

**Independent Test**: In light mode, switch a note between view and edit modes multiple times and confirm the editor remains in the light theme.

**Acceptance Scenarios**:

1. **Given** a note is open in edit mode with a light editor theme, **When** the user switches to view mode and then back to edit mode, **Then** the editor still uses the light theme.
2. **Given** a note is open in edit mode with a dark editor theme, **When** the user switches to view mode and then back to edit mode, **Then** the editor still uses the dark theme.

---

### Edge Cases

- The editor widget is not yet mounted when the application theme changes.
- The configured dark syntax theme does not have a matching light counterpart.
- The user toggles theme rapidly multiple times while a note is open.
- A custom/user-defined theme is neither in the built-in light set nor the dark set.

## Requirements

### Functional Requirements

- **FR-001**: The application MUST detect whether the current application theme is light or dark after each `Ctrl+L` toggle.
- **FR-002**: When the application is in light mode, the code editor (`TextArea`) MUST use a light syntax theme.
- **FR-003**: When the application is in dark mode, the code editor MUST use the syntax theme configured in `config.yaml` (e.g., `monokai`, `dracula`).
- **FR-004**: The editor theme MUST update immediately after a theme toggle without requiring the user to reopen the note.
- **FR-005**: The editor theme MUST remain synchronized when switching between view mode and edit mode.
- **FR-006**: If the editor widget is not available at the moment of the theme change, the theme MUST be applied the next time the editor is mounted or focused.

### Key Entities

- **Application theme state**: represents whether the UI is currently light or dark.
- **Editor syntax theme**: the pygments-based theme applied to the `TextArea` editor.
- **Configuration (`display.syntax_theme`)**: the user's preferred dark syntax theme.

## Success Criteria

### Measurable Outcomes

- **SC-001**: After toggling to light mode with `Ctrl+L`, 100% of notes opened for editing display a light editor theme.
- **SC-002**: After toggling back to dark mode, the editor returns to the configured dark syntax theme within 1 second.
- **SC-003**: Users are not required to manually configure a light syntax theme; the application selects it automatically.
- **SC-004**: Switching between view and edit modes does not change the editor theme out of sync with the application mode.

## Assumptions

- The application already distinguishes light and dark application themes using a known set of light theme names.
- The editor is implemented as a Textual `TextArea` widget accessible via `#editor`.
- The configured `syntax_theme` value is a valid pygments theme name suitable for dark mode.
- The light editor fallback theme (e.g., `github_light`) is available through pygments/Textual.
