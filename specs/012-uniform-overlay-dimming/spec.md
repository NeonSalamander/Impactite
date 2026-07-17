# Feature Specification: Uniform 25% Overlay Dimming

|**Feature Branch**: `012-uniform-overlay-dimming`|

|**Created**: 2026-06-27

|**Status**: Draft

|**Input**: User description: "при вызове контекстных меню по прежнему все что находится под меню не отображается, диалоговые окна отображаются вообще без затемнения того что было под ними, нужно исправлять так что бы при открытии окна или контекстного меню все что под ним просто затемнялось на 25% от обычного"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dialogs dim the workspace by 25% (Priority: P1)

When I open any dialog window, the note, tree, and panels behind it should not stay at full brightness. They should look slightly darker — about one quarter darker than usual — so the dialog clearly stands out, but I can still read what is behind it.

**Why this priority**: This is the core issue the user reported: dialogs currently open with no dimming at all, making them hard to distinguish from the workspace.

**Independent Test**: Open a dialog while a note is visible and compare the note's apparent brightness before and after the dialog opens.

**Acceptance Scenarios**:

1. **Given** a note is visible in the viewer, **When** I open the directory-color dialog, **Then** the note behind the dialog appears noticeably darker than before the dialog opened.
2. **Given** the tree is visible, **When** I open the tag-search dialog, **Then** the tree behind the dialog remains readable but clearly dimmed.

---

### User Story 2 - Context menus dim the workspace by 25% (Priority: P1)

When I open a context menu by right-clicking, the folder tree and notes behind the menu must not be hidden. They must be dimmed by the same 25% as dialogs so I can still see what I clicked on.

**Why this priority**: The user explicitly reported that context menus currently obscure everything underneath them, which hides important context.

**Independent Test**: Right-click a directory to open the context menu and verify the underlying tree is still visible and only slightly darker.

**Acceptance Scenarios**:

1. **Given** the directory tree is visible, **When** I open the directory context menu, **Then** the tree behind the menu is still fully visible, only dimmed by about 25%.
2. **Given** the context menu is open, **When** I move the cursor away and click outside the menu, **Then** the menu closes and the workspace returns to normal brightness immediately.

---

### User Story 3 - Consistent dimming across themes (Priority: P2)

Whether I use a dark theme or a light theme, the dimming level must look the same: about 25% darker. I do not want the overlay to disappear in one theme and become too dark in another.

**Why this priority**: Inconsistent dimming leads to the same problem reappearing when the user switches themes.

**Independent Test**: Switch between dark and light themes and open the same dialog or menu in each; compare the apparent dimming level.

**Acceptance Scenarios**:

1. **Given** the application is in dark theme, **When** I open a dialog, **Then** the workspace behind it is visibly dimmed.
2. **Given** the application is in light theme, **When** I open the same dialog, **Then** the dimming looks equally strong as in dark theme.

---

### Edge Cases

- A dialog with very little content still dims the same large area behind it.
- Opening a context menu over a brightly colored directory must keep that directory visible and only tone it down by the same 25%.
- If two overlays were ever stacked, the dimming should remain at 25% total, not compounded to a much darker result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When any modal dialog is open, the workspace behind it MUST be dimmed by approximately 25% compared to its normal brightness.
- **FR-002**: When a context menu is open, the area outside the menu box MUST be dimmed by approximately 25%; the underlying workspace MUST remain visible and readable.
- **FR-003**: The dimming MUST be uniform across all modal dialogs and all context menus.
- **FR-004**: The dimming MUST be independent of the current application theme: it MUST look like 25% dimming in both dark and light themes.
- **FR-005**: The content of dialogs and menus (text, buttons, inputs) MUST remain fully readable and not be affected by the backdrop dimming.

### Key Entities

- **Overlay backdrop**: The full-screen visual layer behind an active dialog or context menu. Attributes: dimming intensity (target 25% brightness reduction), visibility of underlying content, theme independence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a side-by-side comparison, a user can correctly identify when a dialog is open by spotting the 25% dimming in at least 95% of trials.
- **SC-002**: With a context menu open, a user can correctly identify the right-clicked directory underneath the menu in at least 95% of trials.
- **SC-003**: When switching between dark and light themes, at least 8 out of 10 users rate the dimming strength as "the same" in both themes.
- **SC-004**: No overlay backdrop completely hides the workspace or leaves it at full brightness after opening.

## Assumptions

- "25% dimming" means the underlying workspace is rendered at roughly 75% of its original perceived brightness, not a 25% opaque black layer.
- The fix applies to all current modal dialogs and the directory context menu; future overlays should reuse the same mechanism.
- Terminal or emulator used by the user supports the rendering mode required for blended/partially-transparent overlay colors.
- Notifications, toasts, and inline tooltips are out of scope.
