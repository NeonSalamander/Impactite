# Feature Specification: Visible Context-Menu Overlay

|**Feature Branch**: `013-visible-context-menu-overlay` |

|**Created**: 2026-06-27

|**Status**: Draft

|**Input**: User description: "в файле \"screen.png\" посмотри как отображается, при активно контекстном меню все что под ним не видно"

## Problem Statement

When a directory context menu is open, the entire workspace behind the menu becomes effectively invisible. The screenshot (`screen.png`) shows a near-solid dark overlay covering the tree and the rest of the interface. The expected behaviour is that the user can still see the note tree, current file, and other elements while the menu is active; they need only be visually de-emphasized, not hidden.

## User Scenarios & Testing

### User Story 1 - Context menu does not hide the workspace (Priority: P1)

A user right-clicks a directory in the note tree to open options. The menu appears, but the underlying tree, editor, and other panes remain visible and only slightly subdued, so the user keeps their spatial context.

**Why this priority**: This is the core bug reported by the user. A modal overlay that hides the workspace defeats the purpose of a context menu and makes the interface feel heavy and fragile.

**Independent Test**: Open the directory context menu on any directory and visually confirm that the note tree and other panes behind it are still readable.

**Acceptance Scenarios**:

1. **Given** the application is showing notes with the directory tree visible, **When** the user right-clicks a directory, **Then** the context menu opens and the workspace behind it is still visible (dimmed or subdued, not solid).

---

### User Story 2 - Overlay behaviour is consistent for all overlay types (Priority: P2)

The same approach used to keep the workspace visible under a context menu also applies to modal dialogs, pop-ups, and any other transient overlay, so the user gets a predictable experience.

**Why this priority**: Consistency reduces surprise. Once the context-menu overlay is fixed, the same pattern should prevent any overlay from becoming a solid wall.

**Independent Test**: Open a dialog (for example the directory color dialog) and confirm the background workspace remains visible and subdued rather than hidden.

**Acceptance Scenarios**:

1. **Given** a dialog or overlay is active, **When** the user looks at the area outside the dialog or menu box, **Then** the background content is visible and only visually de-emphasized.

---

### Edge Cases

- The user opens the context menu near the edge of the terminal window; the menu must not extend beyond visible area and the overlay must still cover only the available workspace.
- A user opens a dialog while a context menu is already visible; both overlays should behave consistently.
- The user switches theme while an overlay is open; the workspace remains visible under both dark and light themes.

## Requirements

### Functional Requirements

- **FR-001**: When the directory context menu is open, the full-screen overlay behind it MUST NOT be drawn as a solid color that hides the workspace.
- **FR-002**: The workspace behind an active context menu MUST remain at least partially visible (e.g. dimmed, translucent, or partially see-through).
- **FR-003**: The context-menu box itself (the list of actions) MUST remain clearly readable with an opaque or strongly contrasting background.
- **FR-004**: The solution MUST apply uniformly to all full-screen overlays, including modal dialogs.
- **FR-005**: Headless smoke tests MUST continue to pass — opening the context menu and a modal dialog must not raise exceptions.

### Key Entities

- None. This is a visual/CSS overlay change; no data or persistence is involved.

## Success Criteria

### Measurable Outcomes

- **SC-001**: In a screenshot or manual check, background text and UI elements are still distinguishable when the context menu is open.
- **SC-002**: The same recognisable background is visible in both dark and light themes when a context menu or dialog is open.
- **SC-003**: Opening the context menu or a dialog does not break headless application launch tests.

## Assumptions

- The underlying terminal or terminal emulator supports either true transparency, ANSI dimming, or a CSS-level workaround that lets lower-layer widgets show through.
- A small, visually consistent dimming level (approximately 25% darker or less) is acceptable to the user.
- The "solid" appearance in `screen.png` is caused by the current overlay background rule, not by unrelated rendering issues in the note tree.
