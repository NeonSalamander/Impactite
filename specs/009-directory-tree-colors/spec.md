# Feature Specification: Directory Tree Colors

|**Feature Branch**: `009-directory-tree-colors`|

**Created**: 2026-06-26

**Status**: Draft

**Input**: User description: "В дереве каталогов нужно добавить для каждого каталога задавать свой фон и цвет надписи которые будут сохраняться в настройках"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assign Colors to a Directory (Priority: P1) 🎯 MVP

As a user, I want to set a custom background color and label color for any directory in the directory tree so that I can visually emphasize folders that matter to me.

**Why this priority**: Without the ability to assign colors, the feature does not exist. This is the core user value.

**Independent Test**: Open the app, select a directory in the tree, choose a background and text color, and confirm the directory row immediately displays the selected colors.

**Acceptance Scenarios**:

1. **Given** a directory is visible in the directory tree, **When** the user sets its background and text color to custom values, **Then** the directory row in the tree uses those colors.
2. **Given** a directory has custom colors, **When** the user looks at the directory in the tree, **Then** both the background and the label text show the customized colors.

---

### User Story 2 - Visually Differentiate Multiple Directories (Priority: P2)

As a user, I want different directories to display different colors so that I can quickly recognize category, status, or importance at a glance without reading every label.

**Why this priority**: The value of the feature scales once a user can color-code several folders; otherwise it is just one-off decoration.

**Independent Test**: Assign unique colors to three or more directories and verify each one is visibly distinct in the tree.

**Acceptance Scenarios**:

1. **Given** multiple directories have different custom colors assigned, **When** the directory tree is displayed, **Then** each directory shows its own assigned colors and they do not affect each other.
2. **Given** a directory has no custom colors assigned, **When** it is displayed in the tree, **Then** it renders with the default application styling unchanged.

---

### User Story 3 - Persist Colors Across Sessions (Priority: P3)

As a user, I want the colors I chose for directories to survive an app restart so that I do not have to recolor folders every time I open the application.

**Why this priority**: Persistence is expected for personalization settings; without it, color assignments feel temporary and unreliable.

**Independent Test**: Assign colors to a directory, close the app, reopen it, and verify the same colors are still applied to the directory.

**Acceptance Scenarios**:

1. **Given** a directory has custom colors assigned, **When** the application restarts, **Then** the directory still renders with those colors.
2. **Given** the user opens the application settings after restart, **When** directory color preferences are inspected, **Then** the previously assigned colors are present.

---

### Edge Cases

- What happens if a directory is renamed or moved outside the application? The stored color association is tied to the original path and will not follow the directory.
- What happens if a directory with custom colors is deleted? The stale color entry should no longer affect any visible directory and may be safely ignored or cleaned up.
- What happens if the user picks colors with very low contrast? The application applies the chosen colors; guaranteeing readability is the user's responsibility in this version.
- What happens if a parent and child directory have different colors? Each directory keeps its own color; child directories do not inherit colors from their parents.
- What happens if the user resets a directory's colors? The directory immediately reverts to the default application styling and the custom entry is removed from settings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow the user to assign a custom background color to any directory shown in the directory tree.
- **FR-002**: System MUST allow the user to assign a custom text/label color to any directory shown in the directory tree.
- **FR-003**: System MUST persist each directory's background and text color in user settings so that they survive application restarts.
- **FR-004**: System MUST apply assigned colors to the corresponding directory row in the tree immediately after the user confirms the change.
- **FR-005**: System MUST provide a way to reset a directory's colors to the default application styling.
- **FR-006**: System MUST continue to render directories without custom colors using the existing default styling, without requiring any action from the user.
- **FR-007**: System MUST store color preferences keyed to the directory's path within the current vault/notes path.

### Key Entities *(include if feature involves data)*

- **Directory color preference**: A pair of colors (background and text/label) associated with one directory path within the current vault; stored as user settings.
- **Directory tree node**: The visual representation of a directory in the file explorer; it reads any saved color preference for that directory and applies it to its background and label.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can assign both a background color and a text color to a directory in under 15 seconds using the directory tree.
- **SC-002**: 100% of directories with saved custom colors display those colors every time the directory tree is rendered.
- **SC-003**: Directory color assignments persist on 100% of application restarts when the directory path has not changed.
- **SC-004**: Users can reset a directory to default colors in under 5 seconds.
- **SC-005**: At least 95% of users can visually distinguish customized directories from default-styled ones at a glance.

## Assumptions

- Color preferences are scoped to the active vault/notes path and stored in the application's existing settings file.
- Directory identity is based on its relative path from the vault root; renaming or moving a directory breaks the association.
- Custom colors affect only the directory row itself, not files, notes, or child directories inside it.
- The application already supports per-node styling control in the directory tree at a conceptual level.
- Any valid color value accepted by the application's style system can be used; automatic contrast correction is out of scope for this version.
- Default styling is unchanged for directories that the user has not customized.
