# Feature Specification: Open External Links

**Feature Branch**: `005-open-external-links`

**Created**: 2026-06-22

**Status**: Draft

**Input**: User description: "нужно реализовать обработку https/http ссылок в заметках в режиме просмотра, осуществлять переходы по ссылкам нужно которые указаны как явно в тексте например \"https://ya.ru\" так и по тем которые указаны средствами разметки markdown"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open a Raw URL in a Note (Priority: P1)

A user is reading a note in view mode and sees a plain URL such as `https://ya.ru` written directly in the text. The user wants to open that URL without manually selecting and copying it.

**Why this priority**: This is the most direct value from the feature — users frequently paste raw links into notes and expect to follow them quickly.

**Independent Test**: Can be fully tested by viewing a note containing a raw `http://` or `https://` URL and activating the link; the URL opens in the user's default handler.

**Acceptance Scenarios**:

1. **Given** a note in view mode contains the text `https://ya.ru`, **When** the user activates the rendered link, **Then** the URL opens in the system's default handler.
2. **Given** a note in view mode contains the text `http://example.com`, **When** the user activates the rendered link, **Then** the URL opens in the system's default handler.

---

### User Story 2 - Open a Markdown Inline Link (Priority: P2)

A user is reading a note in view mode and sees a Markdown link such as `[Yandex](https://ya.ru)` or `[Example](http://example.com)`. The user wants to follow the URL behind the visible text.

**Why this priority**: Markdown links are a common way to embed references in notes; supporting them makes the rendered note behave like a typical document reader.

**Independent Test**: Can be fully tested by viewing a note containing a Markdown inline link and activating the link; the URL from the markup opens in the user's default handler.

**Acceptance Scenarios**:

1. **Given** a note in view mode contains the Markdown link `[Search](https://ya.ru)`, **When** the user activates the rendered link, **Then** `https://ya.ru` opens in the system's default handler.
2. **Given** a note in view mode contains the Markdown link `[Example](http://example.com)`, **When** the user activates the rendered link, **Then** `http://example.com` opens in the system's default handler.

---

### User Story 3 - Distinguish and Select Among Multiple Links (Priority: P3)

A note in view mode contains several external links. The user wants to identify all available links and choose which one to open.

**Why this priority**: This improves navigation efficiency in longer notes with many references, but the core value is delivered by Stories 1 and 2.

**Independent Test**: Can be fully tested by viewing a note with multiple raw and Markdown links and confirming each one can be activated independently.

**Acceptance Scenarios**:

1. **Given** a note in view mode contains two different links, **When** the user activates the first link, **Then** only the first URL opens.
2. **Given** a note in view mode contains two different links, **When** the user activates the second link, **Then** only the second URL opens.

---

### Edge Cases

- A link is written inside an inline code span or a fenced code block. The application does not render it as an interactive link so that code remains copy-friendly and unchanged.
- A URL is malformed or contains only a host without a scheme (for example, `ya.ru` without `https://`). The application does not treat it as an external link.
- The system's default handler fails to open the URL. The application shows a clear message indicating that the link could not be opened.
- A Markdown link uses a title attribute, such as `[text](https://ya.ru "title")`. The application still treats the URL part as the target.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: In view mode, the application MUST render any raw `http://` or `https://` URL as an interactive link.
- **FR-002**: In view mode, the application MUST render any Markdown inline link whose target begins with `http://` or `https://` as an interactive link.
- **FR-003**: Activating an interactive link MUST open its target URL using the system's default handler for that URL.
- **FR-004**: Interactive links MUST be visually distinguishable from surrounding text.
- **FR-005**: URLs inside inline code spans or fenced code blocks MUST NOT be rendered as interactive links.
- **FR-006**: If the system's default handler fails to open a link, the application MUST display a clear, non-technical error message to the user.

### Key Entities *(include if feature involves data)*

- **External Link**: A reference found in a note consisting of a target URL (`http://` or `https://`) and optional displayed text. Two source forms matter for this feature: a raw URL appearing directly in the note text, and a URL provided through Markdown inline link markup.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can open a raw `http://` or `https://` URL from a note in view mode in fewer than three interactions.
- **SC-002**: A user can open a Markdown inline link from a note in view mode in fewer than three interactions.
- **SC-003**: Every valid `http://` or `https://` link rendered in the body of a note in view mode is interactive, except for links inside code blocks or inline code spans.
- **SC-004**: When a link cannot be opened, the user receives feedback within 1 second.
- **SC-005**: No link inside a code block or inline code span is interactive.

## Assumptions

- The user has a system default handler configured for web URLs (for example, a web browser).
- Only `http://` and `https://` schemes are in scope; other URI schemes such as `ftp://`, `mailto:`, or `file://` are not covered by this feature.
- The feature applies only to view mode; editing mode is not required to render clickable external links.
- URLs without an explicit scheme, such as `www.example.com`, are not treated as external links.
- Links open outside the application through the operating system's normal URL handling mechanism.
