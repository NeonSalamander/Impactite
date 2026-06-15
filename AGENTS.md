<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read specs/001-current-note-search/plan.md
<!-- SPECKIT END -->

# Impactite Agent Guide

Impactite is a console (TUI) Markdown viewer and editor inspired by Obsidian,
written in Python 3.14+ using **Textual** and **Rich**.

## Project Context

- **Language / Runtime**: Python 3.14+
- **Package Manager**: `uv` — use `uv run`, `uv add`, and `uv sync` for all Python work
- **Build Backend**: `hatchling`
- **Primary Dependencies** (see `pyproject.toml`):
  `textual[syntax]`, `rich`, `markdown`, `pygments`, `pyyaml`, `ladybug`, `jinja2`
- **Entry Point**: `impactite = impactite.app:main`
- **Configuration**: `config.yaml` (language, hotkeys, display, notes paths, tags)
- **Notes Storage**: plain UTF-8 Markdown files in `notes_path`
- **Derived Indexes** (disposable, auto-rebuildable):
  - `.ladybug_index.lbug` — LadybugDB graph index (tags, links, favorites, form records)
  - `.impactite_fts.db` — SQLite FTS5 full-text search index

## Architecture

Source code lives in `src/impactite/` with a strict separation of concerns:

- `app.py` — Textual UI only: `App`, widgets, screens, `DEFAULT_CSS`, and message handlers.
- `core.py` — Business logic and data: `Config`, `FileSystem`, `MarkdownParser`,
  `TagIndex`, `QueryEngine`, `FullTextIndex`, and pure helpers.
- `i18n.py` — Localization for English, Russian, and German.
- `table_engine.py` — Isolated Org-mode TBLFM formula engine.
- `templater.py` — Isolated Jinja2 template rendering.

Rules:

- Keep UI code in `app.py` and testable core logic in `core.py` (or a new core module).
- Do **not** call widget methods from `core.py`.
- Widgets communicate via Textual `Message`, not direct `App` method calls.
- All user-facing strings go through `impactite.i18n.t` using canonical English keys.
- New data structures should be typed; prefer `@dataclass` and explicit annotations.

## SpecKit & Hermes Workflow

This repository uses **SpecKit** (`specify`) for specification-driven development
and is integrated with **hermes-agent**.

- **Constitution**: `.specify/memory/constitution.md` — highest-priority technical
  constraints; consult it before any architectural decision.
- **Current Feature Plan**: `specs/001-current-note-search/plan.md`.
- **Agent Context**: This file (`AGENTS.md`) is managed by the SpecKit
  `agent-context` extension. The block between `<!-- SPECKIT START -->` and
  `<!-- SPECKIT END -->` is refreshed automatically by SpecKit hooks.
- When implementing features, start from the active plan and the constitution.
- Follow the SpecKit flow: spec → plan → tasks → implementation.

## Development Commands

```bash
# Sync the local environment
uv sync

# Run the application
uv run impactite [path/to/config.yaml]

# Run as a module
uv run python -m impactite

# Add a runtime dependency
uv add <package>

# Add a development dependency
uv add --dev <package>

# Syntax check
python -m compileall src

# Run tests (when present)
uv run pytest
```

## Coding Conventions

- Follow the existing style in `app.py` and `core.py`.
- Keep business logic free of Textual `App` / widget imports so it can be unit-tested.
- Handle I/O, parsing, and user-input errors gracefully; surface them through
  Textual notifications or the status bar instead of raising unhandled exceptions.
- Use `pathlib.Path`, UTF-8 encoding, and `mkdir(parents=True, exist_ok=True)`
  for all file operations.
- Do not introduce web or desktop frameworks (Electron, Qt, React, etc.) without
  explicit stack-change approval per the constitution.
- Before committing, run `python -m compileall src`; for UI changes, also verify
  that the app launches to the first screen.
