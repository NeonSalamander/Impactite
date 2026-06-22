# Feature Specification: Add W311 Theme

**Feature Branch**: `008-add-w311-theme`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "Добавить тему оформления 'W311', максимально полно копирующую внешний вид Windows 3.11"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select the W311 Theme (Priority: P1) 🎯 MVP

As a user, I want to select a theme named "W311" from the application's theme list so that the entire interface adopts the classic Windows 3.11 look.

**Why this priority**: Without the ability to choose the theme, the rest of the feature is unreachable. This is the core user value.

**Independent Test**: Open the app, choose the "W311" theme through the existing theme selector or settings, and confirm the interface immediately updates to a Windows 3.11-inspired palette.

**Acceptance Scenarios**:

1. **Given** the application is running with any other theme, **When** the user selects the "W311" theme, **Then** all visible UI chrome uses the Windows 3.11 color palette (light gray background, dark blue title bars, black text, raised/lowered appearing borders).
2. **Given** the user opens the theme list or inspects the active theme, **When** they look for available themes, **Then** a theme named "W311" is present and selectable.

---

### User Story 2 - W311 Theme Applies Consistently (Priority: P2)

As a user, I want the W311 theme to cover every common widget and surface so that the retro look is coherent and readable.

**Why this priority**: A partial theme feels broken; full coverage is required for the nostalgic Windows 3.11 effect.

**Independent Test**: With the W311 theme active, navigate through the note tree, editor, preview pane, status bar, modals, and menus. Each screen element should use W311-appropriate colors and remain readable.

**Acceptance Scenarios**:

1. **Given** the W311 theme is active, **When** the user opens a note in view mode, **Then** the rendered Markdown, borders, and background all follow the W311 palette.
2. **Given** the W311 theme is active, **When** the user opens a dialog or modal, **Then** the dialog background, title bar, borders, and focused element highlight use the W311 palette.
3. **Given** the W311 theme is active, **When** a code block is shown, **Then** the block background and syntax highlighting remain readable against the light gray W311 background.

---

### User Story 3 - W311 Theme Persists Across Sessions (Priority: P3)

As a user, I want my W311 theme choice to survive an app restart so that I don't have to reselect it every time.

**Why this priority**: Persistence is expected behavior for all existing themes; the new theme must match that convention.

**Independent Test**: Set the theme to W311, close the app, reopen it, and verify the UI still uses the W311 theme.

**Acceptance Scenarios**:

1. **Given** the user has selected the "W311" theme, **When** the app restarts, **Then** the UI loads in the "W311" theme by default.
2. **Given** the app loads with the persisted "W311" theme, **When** the user checks the settings file, **Then** the saved theme value is "W311".

---

### Edge Cases

- What happens when the W311 theme is active and the user toggles to a previously saved custom CSS file? The custom CSS should override or coexist without crashing the app.
- What happens when the terminal does not support the exact Windows 3.11 colors? The theme should fall back to the closest available standard colors.
- What happens when the editor/code theme is synced automatically? The chosen editor theme should remain readable against the light gray W311 application background.
- What happens when the user rapidly cycles themes? Each switch should complete cleanly without leftover artifacts from the previous theme.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a theme named "W311" in the theme selection list.
- **FR-002**: The "W311" theme MUST visually evoke Windows 3.11 using a light gray dominant background, dark blue title bars, black text, and highlighted/focused elements in blue or white.
- **FR-003**: The "W311" theme MUST apply to all core UI surfaces: sidebar/tree, editor/preview panes, status bar, dialogs, modals, menus, and scrollbars.
- **FR-004**: The "W311" theme MUST persist after the application is closed and reopened, using the same configuration mechanism as existing themes.
- **FR-005**: The existing theme-switching shortcut or command MUST cycle through the "W311" theme along with other available themes.
- **FR-006**: The "W311" theme MUST maintain readable contrast for text, code blocks, and highlighted elements.

### Key Entities

- **Theme "W311"**: A selectable application color theme inspired by Windows 3.11.
- **Config theme value**: The stored string that records the user's active theme; "W311" must be a valid value.
- **Editor/code theme pairing**: The associated code-highlighting theme used when "W311" is active; must remain readable on the W311 application background.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can switch to the "W311" theme in under 2 seconds using the existing theme selector.
- **SC-002**: 100% of core UI surfaces described in FR-003 render with W311 palette colors after activation.
- **SC-003**: The "W311" theme is restored on 100% of cold starts when it was the last selected theme.
- **SC-004**: Text and code blocks in the W311 theme achieve a contrast ratio that users report as readable in a manual check.
- **SC-005**: No existing themes are broken or visually regressed by the addition of the W311 theme.

## Assumptions

- The application already has a theme mechanism that can host a new theme entry without changing the architecture.
- Windows 3.11 styling can be expressed within the Textual/Rich color system (no new UI framework is introduced).
- The W311 theme is treated as a light theme; the existing light-theme tracking in the application is updated accordingly.
- Custom user CSS, if present, takes precedence over theme defaults in its specific scope.
- No new icons, fonts, or bitmaps are required; the theme is purely color and style.
