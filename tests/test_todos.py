"""Tests for the open todo parser and save action."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from impactite.todo_parser import (
    TodoItem,
    close_todo,
    collect_open_todos,
    find_note_files,
)


@pytest.fixture
def sample_vault(tmp_path: Path) -> Path:
    """Create a temporary vault with a few Markdown notes."""
    (tmp_path / ".hidden").mkdir()
    (tmp_path / ".hidden" / "secret.md").write_text(
        "- [ ] hidden todo\n", encoding="utf-8"
    )

    (tmp_path / "project.md").write_text(
        "---\ntags: [work]\n---\n\n"
        "# Project\n\n"
        "- [ ] top level open\n"
        "* [x] completed task\n"
        "  - [ ] nested open\n"
        "  + [ ] another nested\n"
        "Plain paragraph with - [ ] inline fake todo.\n"
        "```\n"
        "# not a real todo\n"
        "- [ ] code block todo\n"
        "```\n"
        "- [ ] after code block\n",
        encoding="utf-8",
    )

    (tmp_path / "inbox.md").write_text(
        "- [ ] first inbox todo\n- [ ] second inbox todo\n- [x] done inbox todo\n",
        encoding="utf-8",
    )

    return tmp_path


def test_find_note_files_ignores_hidden(sample_vault: Path) -> None:
    files = find_note_files(sample_vault)
    assert len(files) == 2
    assert all(p.name in ("project.md", "inbox.md") for p in files)


def test_collect_open_todos_finds_open_and_ignores_closed(sample_vault: Path) -> None:
    files = find_note_files(sample_vault)
    todos = collect_open_todos(files)

    texts = {t.line_text.strip() for t in todos}
    assert "- [ ] top level open" in texts
    assert "- [ ] nested open" in texts
    assert "+ [ ] another nested" in texts
    assert "- [ ] after code block" in texts
    assert "- [ ] first inbox todo" in texts
    assert "- [ ] second inbox todo" in texts

    assert "* [x] completed task" not in texts
    assert "- [x] done inbox todo" not in texts


def test_collect_open_todos_ignores_frontmatter_and_code_blocks(
    sample_vault: Path,
) -> None:
    files = find_note_files(sample_vault)
    todos = collect_open_todos(files)

    texts = {t.line_text.strip() for t in todos}
    assert "- [ ] code block todo" not in texts
    assert "Plain paragraph with - [ ] inline fake todo." not in texts


def test_horizontal_rule_in_body_does_not_suppress_todos(tmp_path: Path) -> None:
    path = tmp_path / "hr.md"
    path.write_text(
        "---\ntitle: note\n---\n\nbody\n\n---\n\n- [ ] after horizontal rule\n",
        encoding="utf-8",
    )

    todos = collect_open_todos([path])

    assert any("after horizontal rule" in t.line_text for t in todos)


def test_tilde_code_fences_exclude_todos(tmp_path: Path) -> None:
    path = tmp_path / "tilde.md"
    path.write_text(
        "- [ ] before fence\n~~~\n- [ ] inside tilde fence\n~~~\n- [ ] after fence\n",
        encoding="utf-8",
    )

    todos = collect_open_todos([path])
    texts = {t.line_text.strip() for t in todos}

    assert "- [ ] before fence" in texts
    assert "- [ ] inside tilde fence" not in texts
    assert "- [ ] after fence" in texts


def test_indented_and_nested_backtick_fences_behave(tmp_path: Path) -> None:
    path = tmp_path / "nested.md"
    path.write_text(
        "- [ ] before\n"
        "~~~\n"
        "```\n"
        "- [ ] nested backticks inside tilde\n"
        "```\n"
        "~~~\n"
        "  ```\n"
        "- [ ] indented fence todo\n"
        "  ```\n"
        "- [ ] after\n",
        encoding="utf-8",
    )

    todos = collect_open_todos([path])
    texts = {t.line_text.strip() for t in todos}

    assert "- [ ] nested backticks inside tilde" not in texts
    assert "- [ ] indented fence todo" not in texts
    assert "- [ ] before" in texts
    assert "- [ ] after" in texts


def test_fence_with_info_string_is_not_recognized(tmp_path: Path) -> None:
    path = tmp_path / "info_fence.md"
    path.write_text(
        "```python\n- [ ] inside info string fence\nplain line\n- [ ] another inside\n",
        encoding="utf-8",
    )

    todos = collect_open_todos([path])
    texts = {t.line_text.strip() for t in todos}

    # ```python is not a valid fence line, so its content is scanned.
    assert "- [ ] inside info string fence" in texts
    assert "- [ ] another inside" in texts


def test_collect_open_todos_returns_structured_fields(sample_vault: Path) -> None:
    files = find_note_files(sample_vault)
    todos = collect_open_todos(files)

    first = todos[0]
    assert isinstance(first, TodoItem)
    assert first.file_path == sample_vault / "inbox.md"
    assert first.line_number == 0
    assert first.line_text == "- [ ] first inbox todo"
    assert first.char_offset == 2
    assert first.id
    assert len(first.id) == 16


def test_collect_open_todos_sorts_by_path_then_line_number(sample_vault: Path) -> None:
    files = find_note_files(sample_vault)
    todos = collect_open_todos(files)

    keys = [(str(t.file_path), t.line_number) for t in todos]
    assert keys == sorted(keys)


def test_collect_open_todos_handles_empty_list() -> None:
    assert collect_open_todos([]) == []


def test_todo_ids_are_stable(sample_vault: Path) -> None:
    files = find_note_files(sample_vault)
    first_run = {t.id for t in collect_open_todos(files)}
    second_run = {t.id for t in collect_open_todos(files)}
    assert first_run == second_run


def test_close_todo_flips_dash_marker_and_preserves_indentation(
    sample_vault: Path,
) -> None:
    files = find_note_files(sample_vault)
    todos = collect_open_todos(files)
    target = next(t for t in todos if t.line_text.strip() == "- [ ] nested open")

    assert close_todo(target) is True

    new_text = target.file_path.read_text(encoding="utf-8")
    assert "  - [x] nested open" in new_text
    assert "- [ ] nested open" not in new_text
    assert "  + [ ] another nested" in new_text


def test_close_todo_flips_asterisk_marker(sample_vault: Path) -> None:
    files = find_note_files(sample_vault)
    todos = collect_open_todos(files)
    target = next(t for t in todos if "after code block" in t.line_text)

    assert close_todo(target) is True

    new_text = target.file_path.read_text(encoding="utf-8")
    assert "- [x] after code block" in new_text


def test_close_todo_preserves_crlf(tmp_path: Path) -> None:
    path = tmp_path / "crlf.md"
    path.write_bytes(b"- [ ] one\r\n- [ ] two\r\n")
    todo = TodoItem(
        file_path=path,
        line_text="- [ ] two",
        line_number=1,
        char_offset=0,
        id="id",
    )

    assert close_todo(todo) is True
    assert path.read_bytes() == b"- [ ] one\r\n- [x] two\r\n"


def test_close_todo_preserves_bom(tmp_path: Path) -> None:
    path = tmp_path / "bom.md"
    path.write_bytes(b"\xef\xbb\xbf- [ ] one\n- [ ] two\n")
    todo = TodoItem(
        file_path=path,
        line_text="- [ ] two",
        line_number=1,
        char_offset=0,
        id="id",
    )

    assert close_todo(todo) is True
    assert path.read_bytes() == b"\xef\xbb\xbf- [ ] one\n- [x] two\n"


def test_close_todo_does_not_add_bom(tmp_path: Path) -> None:
    path = tmp_path / "nobom.md"
    path.write_bytes(b"- [ ] one\n- [ ] two\n")
    todo = TodoItem(
        file_path=path,
        line_text="- [ ] two",
        line_number=1,
        char_offset=0,
        id="id",
    )

    assert close_todo(todo) is True
    assert path.read_bytes() == b"- [ ] one\n- [x] two\n"


def test_close_todo_atomic_replace_failure_leaves_original_intact(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "atomic.md"
    original = b"- [ ] one\n- [ ] two\n"
    path.write_bytes(original)
    todo = TodoItem(
        file_path=path,
        line_text="- [ ] two",
        line_number=1,
        char_offset=0,
        id="id",
    )

    def failing_replace(*_args, **_kwargs):
        raise OSError("injected replace failure")

    monkeypatch.setattr(os, "replace", failing_replace)

    assert close_todo(todo) is False
    assert path.read_bytes() == original


def test_close_todo_preserves_inline_content(sample_vault: Path) -> None:
    files = find_note_files(sample_vault)
    todos = collect_open_todos(files)
    target = next(t for t in todos if t.line_text.strip() == "- [ ] top level open")

    assert close_todo(target) is True

    new_text = target.file_path.read_text(encoding="utf-8")
    assert "- [x] top level open" in new_text


def test_close_todo_detects_mismatch_between_item_and_file(sample_vault: Path) -> None:
    files = find_note_files(sample_vault)
    todos = collect_open_todos(files)
    target = next(t for t in todos if "first inbox" in t.line_text)

    # Mutate target line so it no longer matches the file contents.
    wrong = TodoItem(
        file_path=target.file_path,
        line_text="- [ ] does not match",
        line_number=target.line_number,
        char_offset=target.char_offset,
        id=target.id,
    )

    assert close_todo(wrong) is False

    new_text = target.file_path.read_text(encoding="utf-8")
    assert "- [x] first inbox todo" not in new_text
    assert "- [ ] first inbox todo" in new_text
