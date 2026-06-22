# Implementation Plan: Open External Links

**Branch**: `005-open-external-links` | **Date**: 2026-06-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-open-external-links/spec.md`

## Summary

Add external-link handling to Impactite's Markdown viewer. Detect raw `http://`/`https://` URLs and Markdown inline links whose targets use those schemes, render them as interactive elements in view mode, and open the target in the system's default browser when activated. Internal wiki-style links continue to navigate to other notes as before.

## Technical Context

**Language/Version**: Python 3.14+

**Primary Dependencies**: Textual, Rich, `markdown` (existing); Python stdlib `re`, `urllib.parse`, and `webbrowser`. No new external dependencies are required.

**Storage**: N/A — notes remain plain Markdown files; no new indexes or databases.

**Testing**: No automated test suite exists yet. All parsing/detection helpers must remain importable and testable without importing Textual widgets or the App class. Manual validation is documented in `quickstart.md`.

**Target Platform**: Linux/Unix terminal primarily; URL opening works cross-platform through Python's `webbrowser` module.

**Project Type**: Console TUI application (Obsidian-like Markdown viewer/editor).

**Performance Goals**:
- Render a note with link detection in under 100 ms for typical notes (up to ~10 000 lines).
- Respond to a link activation (click) in under 200 ms.

**Constraints**:
- Keep link-detection/parser logic in `core.py` and UI/activation logic in `app.py`.
- Widgets communicate through Textual `Message` classes; do not call widget/App methods from `core.py`.
- Do not add web frameworks, Electron, Qt, or other non-console UI stacks.
- Any new dependency must be added to `pyproject.toml` and justified; prefer stdlib.
- Surface I/O and browser-launch errors through Textual notifications, not unhandled exceptions.
- Links inside code blocks/inline code must remain inactive.
- All new user-facing strings must go through `impactite.i18n.t` with English keys.

**Scale/Scope**: Local single-user note vault. Only `http://` and `https://` schemes are in scope. Edit mode is out of scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|-----------|---------|-------|
| I. Technology stack | PASS | Stays within Python/Textual/Rich; uses stdlib `webbrowser` for URL opening. No prohibited frameworks. |
| II. Architecture & structure | PASS | Link scanning/parsing belongs in `core.py`; activation and rendering stay in `app.py`. Messaging is already used for internal links. |
| III. UI styling | PASS | Link appearance controlled through Rich markup / widget CSS; light/dark theme behaviour must be verified. |
| IV. Data management | PASS | Notes remain UTF-8 Markdown files; indexes unchanged. |
| V. Development practices | PASS | New i18n keys required; typed helpers preferred; core logic testable without Textual; errors surfaced via notifications; compileall + launch check required. |

## Project Structure

### Documentation (this feature)

```text
specs/005-open-external-links/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit-tasks)
```

### Source Code (repository root)

```text
src/impactite/
├── core.py              # Link scanner / URL classifier (testable)
├── app.py               # MarkdownViewer external-link rendering + click handler
└── i18n.py              # New keys for external link errors
```

**Structure Decision**: The feature touches three existing modules. No new modules are required; however, if the link scanner grows, it may be extracted to a dedicated `links.py` core module in the future.

## Complexity Tracking

No constitution violations required.
