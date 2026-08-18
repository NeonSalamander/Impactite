# Research: Toolbar code block insertion and frontmatter

**Feature**: `019-fix-toolbar-code-block-frontmatter`

## Reproduction

A temporary headless Textual test was run against the current `src/impactite/app.py`.

### Steps

1. Create a temporary vault and `Config`.
2. Launch `MarkdownEditorApp` with `App.run_test()`.
3. Call `_create_daily_note()` to create a note with frontmatter:
   ```markdown
   ---
   type: daily_note
   date: 2026-08-18
   ---

   ```
4. Move the cursor to the end of the document.
5. Click the toolbar code-block button (`#toolbar-code`).

### Observed behaviour

With the cursor at the end of the document, the code block is inserted correctly after the frontmatter.

However, when the cursor is left at the default position `(0, 0)` — which is the case immediately after creating a new note — the same handler inserts the empty fenced block before the frontmatter:

```markdown
```

```---
type: daily_note
date: 2026-08-18
---

```

Because the closing fence of the inserted block is immediately followed by `---`, the original frontmatter fences are interpreted as a new code block. The metadata is visually "inside a code block" and no longer parsed as frontmatter.

### Root cause

The toolbar `code` action handler in `MarkdownEditorApp.on_editor_toolbar_action` (around line 3842) inserts the empty block at the current cursor location without checking whether that location is inside YAML frontmatter:

```python
elif event.action == "code":
    if has_selection:
        new_text = f"```\n{selected}\n```"
        editor.replace(new_text, start, end)
    else:
        editor.insert("```\n\n```", start)
        editor.move_cursor((start[0] + 1, 0))
```

After `_load_file()`, Textual's `TextArea.load_text()` moves the cursor to `(0, 0)`. For a daily note this is inside/before the frontmatter, so the insertion corrupts it.

### Fix direction

Introduce a pure helper that, given the document text and a cursor location, returns a location that is after the frontmatter if the cursor is inside or before it. Use this helper only for the empty-insertion branch, preserving the existing wrap-selection behaviour.
