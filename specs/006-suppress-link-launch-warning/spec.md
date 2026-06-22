# Feature Specification: Suppress External Link Launch Warnings

**Feature Branch**: `006-suppress-link-launch-warning`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "При клике на ссылку вверху экрана появляется текстовая строка 'kf.iconthemes: Icon theme "Breeze" not found.'"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open External Link Without Console Noise (Priority: P1)

When a user activates an external `http://` or `https://` link in a note, the default browser should open and the application UI must remain clean — no stray stderr/stdout text from the launched browser process should appear on the screen.

**Why this priority**: The visible warning breaks the reading experience and looks like an application error, reducing trust in the link-opening feature.

**Independent Test**: Open a note containing an external link, click the link, and confirm the browser opens while the TUI shows no unexpected console text.

**Acceptance Scenarios**:

1. **Given** a note in view mode contains the raw URL `https://ya.ru`, **When** the user clicks the URL, **Then** the system browser opens and the application does not display any text from the browser process (e.g., `kf.iconthemes: Icon theme "Breeze" not found.`).
2. **Given** a note in view mode contains the Markdown link `[Example](http://example.com)`, **When** the user clicks the link text, **Then** the system browser opens and no stderr/stdout from the browser appears inside the TUI.

---

### User Story 2 - Preserve Error Feedback on Browser Failure (Priority: P2)

When the browser cannot be opened, the application must still tell the user that something went wrong, distinct from suppressed background warnings.

**Why this priority**: Silencing all output must not hide real failures that the user needs to act upon.

**Independent Test**: Trigger a browser-open failure (e.g., via an invalid URL or missing handler) and confirm a user-facing error notification is shown.

**Acceptance Scenarios**:

1. **Given** the browser cannot open the requested URL, **When** the user clicks the external link, **Then** the application displays a localized error notification and does not crash.

---

### Edge Cases

- What happens when the browser prints warnings but returns success? The warning text must not appear in the application UI.
- What happens when the browser prints fatal errors and fails? The user sees a normal application error notification; the raw process output is not dumped on screen.
- What happens if the user clicks several links quickly? Each click is isolated; output from one launch must not leak into another activation.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST open external `http://`/`https://` links in the default browser without displaying the browser process's stdout/stderr inside the application.
- **FR-002**: System MUST continue to show a localized, user-friendly error notification when the browser cannot be opened.
- **FR-003**: System MUST keep output suppression scoped to the browser-launch operation and not affect other application logging.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of external link activations on a system that emits browser warnings produce no visible console text in the TUI.
- **SC-002**: Failed browser opens continue to display an application notification within 1 second of the click.
- **SC-003**: No regression in existing internal link navigation or other console output behavior.

## Assumptions

- The stray text originates from the spawned browser or desktop-integration process, not from the application itself.
- Suppressing the child process's output while opening a link is acceptable because the application already provides its own success/failure feedback.
- The fix belongs to the same helper responsible for opening external URLs, keeping the UI layer unaware of the suppression detail.
