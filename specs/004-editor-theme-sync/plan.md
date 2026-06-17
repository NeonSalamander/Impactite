# Implementation Plan: Editor Theme Sync

**Branch**: `004-editor-theme-sync` | **Date**: 2026-06-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-editor-theme-sync/spec.md`

**Summary**
Fix a visual inconsistency: when the application is switched to a light theme via `Ctrl+L`, the code editor (`TextArea`) still opens with a dark syntax theme. The editor syntax theme must always match the current application light/dark mode when entering edit mode and when toggling themes.

## Technical Context

**Language/Version**: Python 3.14+

**Primary Dependencies**: Textual, Rich (both already used)

**Storage**: N/A — no configuration schema changes

**Testing**: Manual validation via `uv run impactite` and `python -m compileall src`

**Target Platform**: Linux terminal / console

**Project Type**: desktop TUI app

**Performance Goals**: Instant theme application, no perceivable delay when opening a note or toggling theme

**Constraints**: No new dependencies; UI logic stays in `app.py`; reuse existing `_LIGHT_THEMES` set and `_apply_editor_syntax_theme` helper

**Scale/Scope**: Single widget behavior change, localized to the editor view

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Technology Stack**: Python 3.14+ with Textual/Rich; no new frameworks. ✓ OK
- **II. Architecture**: UI changes in `app.py`; no business-logic dependencies needed. ✓ OK
- **III. Styling**: Existing `_LIGHT_THEMES` and `_apply_editor_syntax_theme` reused; no inline CSS. ✓ OK
- **IV. Data Management**: No persistent data changes; disposable indexes unaffected. ✓ OK
- **V. Development Practices**: No new user-facing strings; logic is testable in isolation through Textual's pilot mode. ✓ OK

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/004-editor-theme-sync/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
└── tasks.md             # Phase 2 output (created by /speckit-tasks)
```

### Source Code (repository root)

```text
src/
└── impactite/
    ├── app.py   # Editor theme application logic updated
    ├── core.py  # Unaffected
    └── ...
```

**Structure Decision**: Single-project layout; change is localized to `app.py` UI logic.

## Phase 0: Research

### Findings

- The application already distinguishes light/dark mode via `_LIGHT_THEMES` in `app.py`.
- `_apply_editor_syntax_theme(editor)` already chooses `github_light` for light mode and the configured `syntax_theme` for dark mode.
- `on_mount` calls `_apply_editor_syntax_theme`, but the editor starts hidden (`#editor-container.display = False`).
- `_load_file` shows the editor when `is_edit_mode=True` but does **not** re-apply the syntax theme.
- `action_toggle_theme` updates the editor theme only when a file is open in view mode, missing the edit-mode case.

### Decisions

- **Decision**: Apply the editor syntax theme inside `_load_file` whenever edit mode is activated.
- **Decision**: Update `action_toggle_theme` to apply the editor theme whenever the editor container is visible (regardless of view/edit mode).
- **Alternatives considered**: Watch `self.theme` and re-apply automatically. Rejected because Textual's reactive watcher already exists but does not target the editor; explicit application at mode-transition points is simpler and avoids widget calls in the watcher.

**Output**: research.md

## Phase 1: Design & Contracts

### Data Model

Editor theme state is derived from two existing values:

- `App.theme` → mapped to light/dark via `_LIGHT_THEMES`
- `Config.display["syntax_theme"]` → dark editor theme preference

No new entities are required.

### Interface Contract

See `contracts/editor-theme.md` for the UI behavior contract.

### Quickstart

See `quickstart.md` for syntax-check and manual validation steps.

### Agent Context Update

`AGENTS.md` should be updated to reference `specs/004-editor-theme-sync/plan.md` before implementation.

## Key Rules

- Use absolute paths for filesystem operations; project-relative paths in documentation and agent context.
- ERROR on gate failures or unresolved clarifications.

## Done When

- [ ] Plan workflow executed and design artifacts generated
- [ ] Extension hooks dispatched or skipped
- [ ] Completion reported with branch, plan path, and generated artifacts
