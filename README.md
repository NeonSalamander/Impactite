# Impactite

🌐 **English** · [Русский](README.ru.md) · [Deutsch](README.de.md)

A console (TUI) Markdown viewer and editor in the spirit of Obsidian, written in
Python with the **Rich** and **Textual** libraries.

## Features

- 📁 **File tree** — navigate files and folders in the left panel
- 👁️ **View mode** — rendered Markdown with formatting and scrolling
- ✅ **Interactive checkboxes** — click task list checkboxes (`- [ ]` / `- [x]`) in view mode to toggle and save them instantly
- ✏️ **Edit mode** — Markdown syntax highlighting and code highlighting in fenced blocks, with a formatting toolbar
- 🏷️ **Tag cloud** — all tags with individual colors, clickable
- 🔍 **Tag search** — modal window with clickable results
- 🕸️ **Link graph** — hierarchical tree of note-tag relationships; all nodes clickable (notes open, tags search)
- 🎨 **Light/dark theme** — toggle on the fly or via the command palette; your choice is saved automatically
- 🌐 **Interface localization** — English, Russian, German
- 📝 **Input forms** — form notes with fields, saved to a file or a database
- 🧮 **Pseudo-SQL queries** — embeddable queries over notes and the database (Dataview-style)
- ⭐ **Favorites** — bookmark notes and access them quickly via a virtual folder
- 🗂️ **Any notes folder** — the directory is set in the config (absolute / `~` / relative)
- ⌨️ **Customizable hotkeys**

## Requirements

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (package and environment manager)

## Installation

```bash
uv sync
```

## Running

```bash
# Via the CLI (after uv sync)
uv run impactite

# Or as a module
uv run python -m impactite

# With an explicit config path
uv run impactite path/to/config.yaml
```

## Installing as an executable command

So you don't have to launch the app through `uv run` every time, you can install
it as a regular `impactite` command on your system. The project already declares
an entry point (`[project.scripts]` in `pyproject.toml`), so a single command is
enough:

```bash
# Install the project as a global command (from the project root)
uv tool install .
```

After that the `impactite` command is available from any directory:

```bash
impactite                      # run
impactite path/to/config.yaml  # with a config path
```

> **PATH.** `uv` places the executable in its own directory (usually
> `~/.local/bin`). If the command isn't found, add that directory to your `PATH`:
> ```bash
> uv tool update-shell   # adds the required directory to PATH
> ```
> (then restart your terminal). You can find the path with `uv tool dir`.

Useful commands for managing the installed command:

```bash
uv tool install --editable .   # "editable" install: code edits take effect
                               # immediately, no reinstall needed (handy in dev)
uv tool upgrade impactite      # update after changes (if not editable)
uv tool list                   # list installed tools
uv tool uninstall impactite    # remove the command
```

> **Note about `config.yaml`.** After installation `impactite` runs from any
> directory, and the config is looked up in the **current** directory by default.
> Pass the config path explicitly (`impactite ~/notes/config.yaml`) or run from
> the folder where `config.yaml` lives. Recall that a relative `notes_path` is
> resolved relative to the config file itself, so the notes folder won't "drift".

### Alternative: building a distribution (wheel)

If you need an installable package (for example, to install it into another
environment via `pip`):

```bash
uv build            # creates dist/impactite-0.1.0-py3-none-any.whl and .tar.gz
# then in any environment:
pip install dist/impactite-0.1.0-py3-none-any.whl
```

## Project structure

```
impactite/
├── pyproject.toml          # Project configuration and dependencies
├── config.yaml             # Application settings
├── README.md               # Documentation (English)
├── README.ru.md            # Documentation (Русский)
├── README.de.md            # Documentation (Deutsch)
├── src/impactite/
│   ├── __init__.py         # Package entry point
│   ├── core.py             # Core: Config, FileSystem, MarkdownParser,
│   │                       #       TagIndex, QueryEngine, parse_form_definition
│   ├── app.py              # Textual UI (App + widgets, styles in DEFAULT_CSS)
│   ├── i18n.py             # Localization (en/ru/de)
│   └── editor.tcss         # (unused — kept for compatibility)
└── notes/                  # Notes folder (default)
    └── .tag_index.db       # SQLite: tag index, colors, form records, favorites, note links
```

---

## Configuration

All settings live in `config.yaml`. By default the app looks for it in the
current directory, but you can pass a path explicitly:
`uv run impactite my-config.yaml`.

```yaml
# Path to the folder with markdown files.
# Any directory works:
#   - absolute path:        "/home/user/Documents/MyNotes"
#   - with the home dir:    "~/Notes"
#   - relative path:        "./notes" (resolved RELATIVE TO this config file)
notes_path: "./notes"

# Interface language: en (English), ru (Русский), de (Deutsch)
language: "en"

# Hotkeys
hotkeys:
  open_file: "enter"          # Open the selected file
  edit_mode: "e"              # Toggle edit mode
  view_mode: "v"              # Toggle view mode
  save_file: "ctrl+s"         # Save the file
  search_tags: "ctrl+t"       # Tag search
  close_search: "escape"      # Close search/dialog
  quit: "ctrl+q"              # Quit
  refresh: "ctrl+r"           # Refresh the file list
  toggle_sidebar: "ctrl+b"    # Show/hide the sidebar

# Display settings
display:
  show_line_numbers: true     # Line numbers in the editor
  word_wrap: true             # Word wrap in the editor
  syntax_theme: "monokai"     # Code highlighting theme (monokai, dracula, github_light, ...)
  code_border: "round"        # Code block border style (round, box, double)
  app_theme: "textual-dark"   # Application theme (see below)

# Tag cloud settings
tags:
  show_cloud: true            # Show the tag cloud
  min_tag_size: 1             # Min tag size
  max_tag_size: 3             # Max tag size
```

### Parameters

| Parameter | Purpose |
|-----------|---------|
| `notes_path` | Notes directory. A relative path is resolved **relative to the config file**, not the current working directory — launching from anywhere opens the same folder. `~` is supported. |
| `language` | Interface language: `en`, `ru`, `de`. An unknown value → `en`. |
| `hotkeys.*` | Hotkeys for actions. |
| `display.show_line_numbers` | Line numbers in the editor. |
| `display.word_wrap` | Wrap long lines in the editor. |
| `display.syntax_theme` | Code highlighting theme (Pygments styles: `monokai`, `dracula`, `github_light`, …). |
| `display.code_border` | Border style around code blocks. |
| `display.app_theme` | Application theme. Saved automatically when toggled (`Ctrl+L`). |
| `tags.show_cloud` | Whether to show the tag cloud. |
| `tags.min_tag_size` / `max_tag_size` | The "weight" range of tags in the cloud. |

### Application themes (`app_theme`)

Dark: `textual-dark`, `dracula`, `monokai`, `nord`, `gruvbox`, `tokyo-night`, …
Light: `textual-light`, `solarized-light`, `catppuccin-latte`, `rose-pine-dawn`, `atom-one-light`.

`Ctrl+L` toggles the light/dark theme, and the choice is automatically saved
to `config.yaml` (the `app_theme` field) — no matter whether you toggle via the
hotkey or the command palette.

---

## Tags

Tags are detected in two ways (in priority order):

1. **In the note's frontmatter** — the `tags:` list:
   ```yaml
   ---
   tags:
     - python
     - tutorial
   ---
   ```
2. **In the note's body** — in the `#tag` format:
   ```markdown
   This note is about #python and #textual.
   ```

On startup all notes are scanned and the tag index is stored in the SQLite
database `.tag_index.db` inside the notes folder. Each tag is deterministically
assigned a unique color (saved in the DB). The tag cloud in the bottom-left and
the tags within the text are clickable — a click opens search for that tag.

---

## Link graph

The **🕸️ Link graph** is a predefined node in the sidebar (alongside ⭐ Favorites).
It opens a hierarchical tree that visualizes the relationships between your notes
and tags:

- **Tags** are the top-level branches (colored, clickable → opens tag search)
- **Notes** are nested under the tags they contain (clickable → opens the note)
- **Internal links** between notes (`[text](other.md)`) are followed and shown as
  nested connections
- **Back-links** (notes that link to the current one) are also displayed
- All nodes are **expanded by default** so the full structure is visible at a glance

When you open a note from the graph, press `Backspace` to return to the graph.

---

## Input forms

Any note whose **first frontmatter key** is `type: form` is shown in **view mode**
as an interactive data-entry form (with "Save" / "Cancel" buttons). In **edit mode**
you see the regular form markup.

### Form definition structure

```yaml
---
type: form                 # required, must be the FIRST key
destination: note          # where to save: note (md file) or database (DB)
catalog: ./projects/       # subfolder (for note) or catalog label (for database)
fields:
  - <key>: [<label>, <type>, <param3>, <param4>]
  - ...
---
```

- **`type: form`** — the form marker (must be first).
- **`destination`** — `note` (default) saves the result as a separate md file with
  frontmatter; `database` saves a record into SQLite (the same DB as the tag
  index, the `form_records` table).
- **`catalog`** — for `note` this is a subfolder inside the notes directory where
  the created file is placed; for `database` it's a text catalog label of the record.
- **`fields`** — a list of fields. Each item is a single-key mapping:
  `field_name: [label, type, param3, param4]`.
  - `field_name` — the key under which the value lands in the frontmatter/DB (and
    by which you can later query it).
  - `label` — the label text shown above the field.
  - `type` — the field type (see the table below).
  - `param3`, `param4` — depend on the type.

### Field types

| Type | Widget | Param 3 | Param 4 | Stored value |
|------|--------|---------|---------|--------------|
| `string` | single-line input | max length (number, `0` = no limit) | — | string |
| `text` | multi-line input | — | — | string (multi-line) |
| `integer` | numeric input | — | — | integer |
| `date` | date input (placeholder `YYYY-MM-DD`) | — | — | date string |
| `boolean` | toggle switch | — | — | `true` / `false` |
| `list` | list (see below) | mode: `select` / `multi-select` | array of options | string or list |

For `list`, the third parameter sets the behavior:

- **`select`** — a dropdown, **one** option is chosen → a single string is saved.
- **`multi-select`** — a multi-select list → an array of strings is saved.
- anything else/absent — free comma-separated input (`value1, value2 ...`), the
  value is split into an array of strings.

The fourth parameter (`[option1, option2, ...]`) defines the available options for
`select` / `multi-select`.

### Example 1. A form saved to md files

```yaml
---
type: form
destination: note
catalog: ./tasks/
fields:
  - name: ["Task name", string, 60]
  - date: ["Start date", date, 0]
  - enable: ["Active", boolean, 0]
  - priority: ["Priority", list, select, [low, medium, high]]
  - tags: ["Tags", list, multi-select, [python, backend, ui, docs]]
  - count: ["Estimate (hours)", integer, 0]
  - description: ["Description", text, 0]
---
```

When filled in and saved, a file like `notes/tasks/Task_name.md` is created:

```yaml
---
name: Write the parser
date: '2026-06-02'
enable: true
priority: high
tags:
  - python
  - backend
count: 8
description: Parse the input data and write it to the DB
---
```

> The file name comes from the first non-empty string field (sanitized and
> substituted), otherwise from a timestamp.

### Example 2. A form saved to the database

```yaml
---
type: form
destination: database
catalog: crm
fields:
  - title: ["Client", string, 80]
  - status: ["Status", list, select, [new, active, closed]]
  - amount: ["Amount", integer, 0]
  - notes: ["Notes", text, 0]
---
```

Each save appends a row to the `form_records` table (columns `id`, `form_source`,
`catalog`, `data` as JSON, `created_at`). These records are then available to
pseudo-SQL queries through the `database` source.

---

## Pseudo-SQL queries (Dataview-style)

In **view mode**, a code block with the language `query` (or `dataview`) is
executed as a query and displayed as a table.

````markdown
```query
FROM notes
WHERE enable = true
SELECT name, count, category
ORDER BY count DESC
LIMIT 10
```
````

### Full syntax

```
FROM notes|database[/<filter>]
WHERE <field> <operator> <value> [AND ...]
GROUP BY <field1>, <field2>
HAVING <aggregate|field> <operator> <value> [AND ...]
SELECT <field1>, <field2>, <aggregate> | *
ORDER BY <field|aggregate> [ASC|DESC]
LIMIT <n>
```

Every clause except `FROM` is optional. Keyword case doesn't matter.

### Data sources (`FROM`)

- **`notes`** — rows from the frontmatter of md files. Extra implicit fields:
  `file` (file name without extension) and `path` (path relative to the notes
  directory). You can restrict to a subfolder: `FROM notes/tasks`.
- **`database`** — form records from the `form_records` table. Implicit fields:
  `id`, `catalog`, `source` (the form file name), `created_at`. You can restrict
  to a catalog: `FROM database/crm`.

### Operators (`WHERE` / `HAVING`)

| Operator | Meaning |
|----------|---------|
| `=` | equal |
| `!=` | not equal |
| `>` `<` `>=` `<=` | numeric comparison |
| `CONTAINS` | membership (for lists — is the element present; for strings — substring) |
| `LIKE` | case-insensitive substring |

Multiple conditions are joined with `AND`.

**Values** are recognized automatically: `true`/`false` (or `yes`/`no`) → boolean,
an integer/float → number, quoted text → string, otherwise — the string as-is.
Examples: `enable = true`, `count >= 10`, `category = backend`, `tags CONTAINS python`.

### Aggregate functions and grouping

Available: `COUNT`, `SUM`, `MIN`, `MAX`, `AVG`.

- `COUNT(*)` — the number of rows in a group; `COUNT(field)` — the number of non-empty values.
- `SUM` / `AVG` — computed over numeric values only (`AVG` is rounded to 2 decimals).
- `MIN` / `MAX` — over numbers, or lexicographically if the values are non-numeric (dates/strings).

Aggregation kicks in when there's a `GROUP BY` **or** an aggregate in `SELECT`.
Without `GROUP BY`, an aggregate is computed over all rows (overall totals). If
`SELECT` is omitted alongside `GROUP BY`, the grouping fields and `COUNT(*)` are
shown by default.

`HAVING` filters the already-grouped rows. You can filter by an aggregate that is
**not** in `SELECT` — it will be computed behind the scenes.

### Query examples

**A simple selection with filtering and sorting:**

````markdown
```query
FROM notes/tasks
WHERE enable = true
SELECT name, count, category
ORDER BY count DESC
```
````

**Filter by a tag (membership in a list):**

````markdown
```query
FROM notes/tasks
WHERE tags CONTAINS python
SELECT name, count, tags
```
````

**A summary by category with aggregates:**

````markdown
```query
FROM notes/tasks
GROUP BY category
SELECT category, COUNT(*), SUM(count), AVG(count), MIN(count), MAX(count)
ORDER BY SUM(count) DESC
```
````

**Overall totals without grouping:**

````markdown
```query
FROM notes/tasks
WHERE enable = true
SELECT COUNT(*), SUM(count)
```
````

**Grouping + filtering by an aggregate (`HAVING`):**

````markdown
```query
FROM notes/tasks
GROUP BY category
SELECT category, COUNT(*), SUM(count)
HAVING COUNT(*) > 1
ORDER BY SUM(count) DESC
```
````

**`HAVING` on an aggregate that isn't in `SELECT`:**

````markdown
```query
FROM notes/tasks
GROUP BY category
SELECT category, COUNT(*)
HAVING SUM(count) >= 20
```
````

**A query against form records in the database:**

````markdown
```query
FROM database/crm
WHERE status = active
SELECT title, amount, created_at
ORDER BY amount DESC
```
````

---

## Hotkeys (default)

| Key | Action |
|-----|--------|
| `Enter` | Open the selected file |
| `E` | Edit mode |
| `Ctrl+S` | Save the file |
| `Ctrl+T` | Tag search |
| `Ctrl+F` | Toggle favorite |
| `Ctrl+L` | Toggle light/dark theme |
| `Ctrl+R` | Refresh the file list |
| `Ctrl+B` | Show/hide the sidebar |
| `Ctrl+Q` | Quit |
| `Backspace` | Go back to the previous note (or back to the link graph) |
| `Escape` | Close search/dialog; exit the editor (with a save prompt) |

In view mode scrolling is available: arrows `↑`/`↓`, `PgUp`/`PgDown`, `Home`/`End`.
In modal windows the button focus is moved with arrows `←`/`→` and `Tab`, and
confirmed with `Enter`. The note text can be selected with the mouse for copying
(in both view and edit modes).

---

## Edit mode toolbar

In edit mode, a toolbar appears above the editor with quick formatting buttons:

| Button | Action |
|--------|--------|
| **B** | Bold (`**text**`) |
| *I* | Italic (`*text*`) |
| S | Strikethrough (`~~text~~`) |
| H1 / H2 / H3 | Heading levels |
| [L] | Link (`[text](url)`) |
| - | Bullet list (`- item`) |
| 1. | Numbered list (`1. item`) |
| [ ] | Task list (`- [ ] item`) |
| > | Blockquote (`> quote`) |
| ``` | Code block (` ``` ... ``` `) |
| — | Horizontal rule (`---`) |

If text is selected, the button wraps the selection. Otherwise, it inserts a template and places the cursor inside.

---

## Markdown: examples

### Code with highlighting

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Interactive checkboxes

Task list items are clickable in view mode — a click toggles the checkbox and saves the file immediately.

```markdown
- [x] Write the parser
- [ ] Add tests
- [ ] Update documentation
```

### Tags

Add tags anywhere in the file: `#tag1`, `#python`, `#tutorial`.

---

## Development

```bash
# Add a dependency
uv add <package>

# Add a dev dependency
uv add --dev <package>

# Run the tests (if any)
uv run pytest
```

## License

MIT
