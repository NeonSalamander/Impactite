# Research: Editor Theme Sync

**Feature**: Editor Theme Sync (`specs/004-editor-theme-sync`)
**Date**: 2026-06-17

## Unknowns & Decisions

### 1. Where should the editor theme be (re-)applied?

**Finding**: The existing helper `_apply_editor_syntax_theme(editor)` in `src/impactite/app.py` already implements the correct light/dark selection (`github_light` vs. configured `syntax_theme`). It is called in `on_mount` and in `action_toggle_theme`, but it is skipped when the editor is shown in `_load_file`.

**Decision**: Call `_apply_editor_syntax_theme(editor)` inside `_load_file` whenever `is_edit_mode` becomes `True`, immediately after `editor.load_text(content)`.

**Rationale**: This is the only path where a hidden editor is made visible with content. Applying the theme here guarantees fresh state when the user enters edit mode.

### 2. Should the theme also update during an active theme toggle while editing?

**Finding**: `action_toggle_theme` currently applies the editor theme only after a theme switch and only when a file is open in view mode (`if self.current_file and not self.is_edit_mode`). If the user is editing, the editor theme is not refreshed.

**Decision**: Change `action_toggle_theme` to update the editor theme whenever the editor container (`#editor-container`) is visible, covering both view and edit modes.

**Rationale**: Meets User Story 2 (toggle back to dark while editing) and keeps the logic widget-state driven rather than mode dependent.

### 3. Are any new dependencies or config fields required?

**Finding**: `_LIGHT_THEMES` and `Config.display["syntax_theme"]` already exist.

**Decision**: No new dependencies, no new configuration fields.

## Summary

No [NEEDS CLARIFICATION] remains. The fix is a localized change in `app.py`:
- Re-apply editor syntax theme when entering edit mode.
- Update editor syntax theme on theme toggle whenever the editor is visible.
