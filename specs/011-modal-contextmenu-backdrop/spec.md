# Feature Specification: Modal and Context Menu Backdrop Dimming

|**Feature Branch**: `011-modal-contextmenu-backdrop`|

|**Created**: 2026-06-27

|**Status**: Draft

|**Input**: User description: "Когда открывается диалоговое окно или контекстное меню то вся область которая под ним становится черной, так не нужно, нужно ее немного затемнить но не более"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dialogs do not hide the workspace (Priority: P1)

When I open any dialog box (for example, to enter a color or set a folder option), the rest of the application window should not turn completely black. I still want to see the note or tree that was behind the dialog.

**Why this priority**: This is the main usability problem the user reported. A black screen hides context and makes the interface feel heavy.

**Independent Test**: Open a color dialog while a note is visible in the background and verify that the note is still partially visible.

**Acceptance Scenarios**:

1. **Given** a note is displayed in the viewer, **When** I open the directory-color dialog, **Then** the note behind the dialog remains partially visible (not fully blacked out).
2. **Given** the tree is visible, **When** I trigger the directory settings dialog, **Then** the tree rows behind the dialog are still distinguishable.

---

### User Story 2 - Context menu does not hide the workspace (Priority: P1)

When I open a context menu by right-clicking a folder, the area outside the menu should not turn black. It should be slightly dimmed so I know the menu is active, but I can still see the folder tree.

**Why this priority**: The context menu was introduced in feature 010 and currently behaves as a full-screen overlay. It should follow the same visual rule as dialogs.

**Independent Test**: Right-click a directory to open the context menu and verify that the tree behind it is still visible.

**Acceptance Scenarios**:

1. **Given** the directory tree is visible, **When** I open the directory context menu, **Then** the tree behind the menu remains partially visible.
2. **Given** the context menu is open, **When** I dismiss it, **Then** the workspace returns to its normal appearance immediately.

---

### User Story 3 - Consistent dimming across all overlays (Priority: P2)

All modal dialogs and context menus should use the same gentle dimming level. I do not want one dialog to dim a lot and another one to dim a little.

**Why this priority**: Consistency reduces visual distraction and makes the application feel polished.

**Independent Test**: Open every available dialog/context menu in sequence and visually compare the backdrop darkness.

**Acceptance Scenarios**:

1. **Given** I open the tag-search dialog, **When** I compare it to the directory-color dialog, **Then** both backdrops have a similar visible-lightness level.
2. **Given** the context menu is open, **When** I compare its backdrop to a modal dialog backdrop, **Then** they appear equally dim.

---

### Edge Cases

- A very short dialog (e.g., a prompt with one input) still leaves most of the workspace visible.
- Multiple overlays can never appear at once for the same area; if one opens while another is visible, the underlying workspace remains dimmed only once.
- The dimming must not reduce color contrast so much that existing colored directories become unreadable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When a modal dialog opens, the area behind it MUST remain partially visible; it MUST NOT become completely black or opaque.
- **FR-002**: Modal dialog backdrops MUST apply a slight darkening effect to focus attention on the dialog.
- **FR-003**: When the directory context menu opens, the area behind the menu MUST remain partially visible and MUST NOT become completely black or opaque.
- **FR-004**: The context menu area outside the menu itself MUST apply a slight darkening effect consistent with modal dialogs.
- **FR-005**: All modal dialogs and context menus MUST use the same dimming intensity.
- **FR-006**: The dimming MUST NOT prevent users from recognizing content behind the overlay (text and colors remain distinguishable).

### Key Entities

- **Overlay backdrop**: The visual region between the active overlay and the underlying workspace. Attributes: dim intensity, transparency level, coverage area.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With any modal dialog open, a user can correctly identify the currently visible note or tree section behind the dialog in at least 90% of cases.
- **SC-002**: With the context menu open, a user can correctly identify the right-clicked directory in the tree behind the menu in at least 90% of cases.
- **SC-003**: When shown two different overlays side-by-side, users rate their backdrop darkness as "the same" or "very similar" in at least 9 out of 10 comparisons.
- **SC-004**: No overlay backdrop is completely opaque (0% visible) after opening.

## Assumptions

- The term "dialog" covers all modal confirmation, input, selection, and settings windows used in the application, including the directory-color dialog.
- The term "context menu" refers to the directory right-click menu introduced alongside this feature request.
- Notifications, toasts, and small tooltips are out of scope.
- Dimming intensity is applied uniformly behind each overlay; no per-overlay configuration is required.
