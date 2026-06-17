# Feature Specification: Fix Theme Toggle

**Feature Branch**: `003-fix-theme-toggle`

**Created**: 2026-06-17

**Status**: Draft

**Input**: User description: "при выбранной теме и дальнейшем переключении по ctrl+l на светлую и обратно теряется установленная тема и устанавливается дефолтная, надо исправить"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve Selected Theme After Light/Dark Toggle (Priority: P1)

A user has changed the application theme from the default to another theme (for example, through the theme selector or configuration). When they press `Ctrl+L` to temporarily switch to the light variant and then press `Ctrl+L` again to switch back, the previously selected theme is restored instead of being reset to the default theme.

**Why this priority**: This is the core bug being reported. Losing the selected theme forces the user to reconfigure the appearance every time they toggle light/dark mode, which is frustrating and breaks the expected behavior of a theme toggle.

**Independent Test**: Can be fully tested by selecting a non-default theme, pressing `Ctrl+L` twice, and verifying that the application returns to the originally selected theme.

**Acceptance Scenarios**:

1. **Given** the user has selected a non-default theme, **When** the user presses `Ctrl+L` to switch to the light variant, **Then** the application displays the light variant of the selected theme (or the closest available light equivalent), not the default theme.
2. **Given** the user has switched to the light variant with `Ctrl+L`, **When** the user presses `Ctrl+L` again, **Then** the application returns to the originally selected theme.

---

### User Story 2 - Persist Theme Choice Across Sessions (Priority: P2)

The user's theme choice survives an application restart. When the application starts again, it applies the last theme the user explicitly selected, rather than falling back to the default.

**Why this priority**: Persisting user preferences is a standard expectation for a desktop/TUI application and prevents repeated reconfiguration.

**Independent Test**: Can be tested by selecting a theme, closing the application, reopening it, and verifying the previously selected theme is active.

**Acceptance Scenarios**:

1. **Given** the user has selected a non-default theme, **When** the application is closed and reopened, **Then** the application starts with the previously selected theme.
2. **Given** the application is started for the first time (no prior user theme selection), **When** the application initializes, **Then** it uses the default theme as a fallback.

---

### User Story 3 - Handle Missing or Corrupted Configuration Gracefully (Priority: P3)

If the stored theme configuration is missing, corrupted, or points to a theme that is no longer available, the application falls back to the default theme without crashing or displaying an error state.

**Why this priority**: Defensive handling of configuration ensures the application remains usable even when the user's settings file is incomplete.

**Independent Test**: Can be tested by removing or corrupting the theme entry in the configuration file and verifying the application launches with the default theme.

**Acceptance Scenarios**:

1. **Given** the configuration file does not contain a theme entry, **When** the application starts, **Then** it uses the default theme.
2. **Given** the configuration file references a theme that is not installed/available, **When** the application starts or toggles modes, **Then** it falls back to the default theme.

---

### Edge Cases

- What happens when the currently selected theme has no matching light or dark counterpart?
- How does the system handle a configuration file with an invalid or empty theme value?
- What happens if the user toggles `Ctrl+L` rapidly multiple times in succession?
- How does the system behave when the theme setting is changed manually in the configuration file while the application is running?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The application MUST remember the theme explicitly selected by the user, distinct from any temporary light/dark mode toggle.
- **FR-002**: Pressing `Ctrl+L` MUST switch only between the light and dark variants of the current theme without discarding the user's theme choice.
- **FR-003**: The user's selected theme MUST be persisted so it is available after the application restarts.
- **FR-004**: When switching modes with `Ctrl+L`, the application SHOULD prefer the light/dark counterpart of the selected theme if one exists.
- **FR-005**: If the selected theme has no matching counterpart for the target mode, the application MUST fall back to a sensible default for that mode while keeping the user's original theme selection intact for subsequent toggles.
- **FR-006**: The application MUST handle missing, empty, or invalid theme configuration values by falling back to the default theme.

### Key Entities *(include if feature involves data)*

- **User Theme Preference**: The theme explicitly chosen by the user (e.g., via the theme selector or configuration file). This value should be stored and restored independently of temporary light/dark toggles.
- **Active Theme**: The theme currently applied to the UI, which may be a light or dark variant driven by `Ctrl+L`.
- **Theme Mode State**: The temporary light/dark toggle state triggered by `Ctrl+L`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After selecting a non-default theme and pressing `Ctrl+L` twice, the application returns to the originally selected theme in 100% of cases.
- **SC-002**: The last user-selected theme is restored after closing and reopening the application in 100% of cases when a valid theme was previously selected.
- **SC-003**: Users no longer need to reselect their preferred theme after using the light/dark toggle.
- **SC-004**: The application launches successfully and uses the default theme when the theme configuration is missing or invalid.

## Assumptions

- The application stores user preferences in a configuration file that is read at startup and can be updated at runtime.
- Themes are identified by names recognized by the TUI framework, and light themes can be distinguished from dark themes by the application.
- The `Ctrl+L` shortcut is the dedicated light/dark mode toggle and should not be overloaded with unrelated behavior.
- The fix does not require adding new third-party themes; it only ensures the existing theme selection is preserved.
