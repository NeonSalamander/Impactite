# Tasks: Keep Tree Icons Aligned

|**Input**: Design documents from `specs/015-keep-tree-icons-aligned/`

|**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- Include exact file paths in descriptions

---

## Phase 1: Implementation

|**Purpose**: Restore original emoji prefixes and ensure consistent label format

|- [x] T001 [US1] Revert tree node prefixes to original emoji in `src/impactite/app.py`
  - Link graph: `🕸️ Link graph`
  - Favorites: `⭐ Favorites`
  - Favorite entries: `⭐ {name}`
  - Directories: `📁 {name}`
  - Markdown files: `📄 {name}`
  - Other files: `📎 {name}`
|- [x] T002 [US1] Verify every label follows `icon + single space + name` format
|- [x] T003 [US1] Ensure `_render_line` and `render_label` width/alignment behaviour is unchanged

**Checkpoint**: All tree rows display original emojis with uniform prefix format

---

## Phase 2: Validation

|**Purpose**: Confirm icons and alignment are correct

|- [x] T004 [P] [US1] Run syntax check: `python -m compileall src`
|- [x] T005 [P] [US1] Run headless smoke test: `uv run python /tmp/test_backdrop_smoke.py`
|- [x] T006 [P] [US1] Run headless overlay test: `uv run python /tmp/test_backdrop_overlays.py`
|- [x] T007 [US1] Write/run a focused headless test that asserts each visible node label starts with the expected emoji prefix
|- [x] T008 [US1] Manual/quickstart check with temp config to verify no row is shifted by one character

---

## Phase 3: Polish

|**Purpose**: Final cleanup and task list completion

|- [x] T009 Mark all `tasks.md` items `[X]`
|- [x] T010 Update AGENTS.md/context if needed
