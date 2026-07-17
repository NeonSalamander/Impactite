# Feature Specification: Backlinks Panel

|**Feature Branch**: `018-backlinks-panel`

|**Created**: 2026-07-17

|**Status**: Draft

|**Input**: User description: "Панель обратных ссылок (backlinks) для текущей заметки в стиле Logseq/Obsidian: закреплена под viewer'ом, только прямые ссылки, простой список файлов, без unlinked mentions и без отслеживания unresolved-ссылок"

## Problem Statement

Impactite indexes `[[internal links]]` between notes in the LadybugDB graph
(`LINKS_TO` relations) and uses them in the global link-graph tree, but a user
reading a note has no way to see **which notes link to it**. Incoming links are
the primary discovery mechanism in Obsidian (Backlinks core plugin) and Logseq
(Linked references); without them, connections in the vault are invisible from
the target note's side.

## User Scenarios & Testing

### User Story 1 - See incoming links while reading a note (Priority: P1)

A user opens a note that other notes link to. Below the rendered note content,
a fixed panel lists the source files that link to the currently open note.

**Why this priority**: This is the core value of the feature — making incoming
connections visible from the note being read.

**Independent Test**: In the sample vault, open a note that is the target of a
`[[...]]` link from another note (e.g. a book note linked from a review) and
verify the panel lists the source file.

**Acceptance Scenarios**:

1. **Given** note A contains `[[B]]` and the link index is built, **When** the
   user opens note B, **Then** a panel anchored at the bottom of the viewer
   lists note A.
2. **Given** several notes link to note B, **When** the user opens note B,
   **Then** all of them are listed, sorted alphabetically by path, each shown
   as a vault-relative path.
3. **Given** note B is open, **When** the user scrolls the note content,
   **Then** the backlinks panel stays fixed at the bottom of the viewer area
   and does not scroll away with the text.

---

### User Story 2 - Navigate to a linking note (Priority: P1)

A user clicks (or selects via keyboard) an entry in the backlinks panel and
jumps to the source note.

**Why this priority**: Backlinks without navigation are only half the feature;
jumping to the source is what makes connections traversable.

**Independent Test**: Open a note with backlinks, activate an entry, verify the
source note opens and the back-navigation history still works.

**Acceptance Scenarios**:

1. **Given** the backlinks panel lists note A for open note B, **When** the
   user activates the entry for A, **Then** note A opens via the standard
   navigation path (so "go back" returns to B).

---

### User Story 3 - Panel stays out of the way when irrelevant (Priority: P2)

A user opens a note that no other note links to. The panel does not occupy
screen space.

**Why this priority**: Terminal screen space is scarce; an always-visible empty
panel would waste several lines on most notes.

**Independent Test**: Open a note with no incoming links and verify the panel
is not visible and the viewer occupies the full content area.

**Acceptance Scenarios**:

1. **Given** no note links to the open note, **When** the note is displayed,
   **Then** the backlinks panel is hidden.
2. **Given** the panel is visible for note B, **When** the user opens a note
   with no backlinks, **Then** the panel hides again.

---

### Edge Cases

- A note links to itself; the self-link is excluded from the panel.
- A source file is renamed or deleted outside the app; after the next index
  rebuild the stale entry no longer appears.
- The user edits and saves a note, changing its outgoing links; panels shown
  for subsequently opened notes reflect the updated index.
- More backlinks exist than fit the panel height; the list scrolls inside the
  fixed-height panel.
- The current "note" is a form, base, or the link-graph view; the panel is not
  shown (it belongs to the rendered-note viewer only).
- The link index is empty or missing (fresh vault); the panel simply stays
  hidden, no errors are raised.

## Requirements

### Functional Requirements

- **FR-001**: The core MUST expose a way to obtain the list of files that link
  to a given note, derived from the existing `LINKS_TO` graph index.
- **FR-002**: While a note is displayed in view mode, a panel anchored at the
  bottom of the viewer MUST list every note that links to it, each entry
  rendered as a vault-relative path.
- **FR-003**: Entries MUST be sorted alphabetically by path and MUST exclude
  self-links.
- **FR-004**: Activating an entry MUST open that note through the existing
  navigation mechanism, preserving back-navigation history.
- **FR-005**: The panel MUST be hidden when the open note has no incoming
  links, and shown again when it has at least one.
- **FR-006**: The panel MUST refresh when a note is opened and after the link
  index is rebuilt (file save, manual refresh).
- **FR-007**: The panel MUST NOT appear in edit mode or in form/base/graph
  views; it is part of the rendered-note viewer only.
- **FR-008**: All user-facing strings MUST go through `impactite.i18n` with
  English keys and ru/de translations.
- **FR-009**: The feature MUST NOT introduce new dependencies or new persistent
  storage; the existing graph index is the only data source.

### Out of Scope (explicitly excluded)

- Unlinked mentions (plain-text occurrences of the note name without a link).
- Tracking or displaying links to not-yet-existing notes (unresolved links).
- Per-link context lines/snippets from the source note.
- Backlinks for tags (tags already have their own search UI).

### Key Entities

- **Backlink**: an inverted `LINKS_TO` relation — for note B, every note A such
  that `A -[:LINKS_TO]-> B` exists in the graph index.
- **Backlinks panel**: a fixed-height widget at the bottom of the note viewer
  listing backlinks and emitting navigation messages.

## Success Criteria

### Measurable Outcomes

- **SC-001**: For any note with incoming links, 100% of indexed source notes
  appear in the panel when the note is opened.
- **SC-002**: Activating any listed entry opens the corresponding note in one
  action, with working back-navigation.
- **SC-003**: After editing links in a note and saving, opening a linked target
  shows the updated source list without restarting the application.
- **SC-004**: Notes without incoming links render exactly as before the feature
  (no panel, no layout shift).

## Assumptions

- The LadybugDB `LINKS_TO` index is already maintained incrementally
  (`TagIndex.rebuild_note_links`) and is refreshed on save/refresh.
- Only links to existing files are indexed today; this matches the decision to
  skip unresolved-link tracking.
- A fixed panel that appears and disappears depending on backlink presence is
  acceptable UX (chosen over an always-visible panel).
