# Tasks: Remember User Theme

|**Input**: Design documents from `specs/017-remember-user-theme/`

|**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md

## Phase 0 — Reproduce & lock behaviour

|- [x] T001 Read `src/impactite/app.py` and `src/impactite/core.py` to locate theme lifecycle (`__init__`, `watch_theme`, `action_toggle_theme`, `save_theme`, `get_user_theme`).
|- [x] T002 Write and run a headless test that toggles the theme, restarts app with the same config, and asserts the last theme is restored (expected to fail before fix).

## Phase 1 — Core fix

|- [x] T003 Update `action_toggle_theme` so the effective theme after toggling is persisted.
|- [x] T004 Keep fallback and validation on startup: invalid/missing saved themes are replaced with the default theme and persisted.
|- [x] T005 Ensure theme writes preserve all other config keys and YAML comments/formatting.

## Phase 2 — Validation

|- [x] T006 Run the headless persistence test and verify it passes.
|- [x] T007 Run `python -m compileall src`.
|- [x] T008 Run existing smoke/overlay/tree tests for regression.
|- [x] T009 Revert any unintended changes to workspace `config.yaml`.
