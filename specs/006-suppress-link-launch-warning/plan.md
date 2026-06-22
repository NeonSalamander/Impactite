# Implementation Plan: Suppress External Link Launch Warnings

**Branch**: `006-suppress-link-launch-warning` | **Date**: 2026-06-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/home/kandellak/__MAIN_SCRAP__/work/Impactite/specs/006-suppress-link-launch-warning/spec.md`

**Summary**: Redirect the standard output/error file descriptors to `/dev/null` around `webbrowser.open()` in `core.py`, then restore them. Failure handling and the `OpenUrlError` contract stay unchanged.

## Technical Context

- **Language/Version**: Python 3.14+
- **Primary Dependencies**: `webbrowser` (stdlib), Textual/Rich for UI
- **Storage**: N/A
- **Testing**: Manual / `Uv run` verification; no automated test suite yet
- **Target Platform**: Linux (CachyOS), multi-platform where `webbrowser` is available
- **Project Type**: Console TUI application
- **Performance Goals**: <100 ms per link activation (opening the browser dominates this budget)
- **Constraints**: No new dependencies; fix must remain in `core.py`; UI layer remains unaware of suppression
- **Scale/Scope**: Single helper function change; affects every external link click

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Technology Stack | ✓ PASS | Stays within Python stdlib (`webbrowser`, `os`), no new packages |
| II. Architecture | ✓ PASS | Change is isolated to `core.py` (`open_url`); UI layer unchanged |
| III. Styling | N/A | No UI changes |
| IV. Data Management | N/A | No I/O or persistence changes |
| V. Development Practices | ✓ PASS | `open_url` remains unit-testable; error notifications already localized |

**Re-check after Phase 1**: Still passes with fd-redirection approach.

## Project Structure

### Documentation (this feature)

```text
specs/006-suppress-link-launch-warning/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code

```text
src/impactite/
├── core.py              # open_url helper to be updated
├── app.py               # unchanged
└── i18n.py              # unchanged
```

**Structure Decision**: A one-function change in `src/impactite/core.py`. No new files or modules.

## Complexity Tracking

No complexity justifications needed.
