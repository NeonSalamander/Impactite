"""Open todo parser for Markdown note files."""

from __future__ import annotations

import hashlib
import logging
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class TodoItem:
    """One open (unchecked) Markdown todo item.

    Line numbers are zero-based, matching the in-memory representation used by
    the viewer. ``char_offset`` points to the opening bracket ``[`` of the
    marker.
    """

    file_path: Path
    line_text: str
    line_number: int
    char_offset: int
    id: str


def find_note_files(root_path: str | Path) -> list[Path]:
    """Return every ``.md`` file under ``root_path`` recursively.

    Hidden files and directories are ignored.
    """
    root = Path(root_path).expanduser().resolve()
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.md") if not any(part.startswith(".") for part in p.relative_to(root).parts))


def collect_open_todos(files: list[Path]) -> list[TodoItem]:
    """Scan note files and return all unchecked todo markers.

    Only Markdown list-item markers ``- [ ]`` / ``* [ ]`` / ``+ [ ]`` at the
    start of a line (after indentation) are considered. Markers inside YAML
    frontmatter and fenced code blocks are ignored to avoid false positives.

    Args:
        files: Markdown note files to scan.

    Returns:
        TodoItem list sorted by file path, then line number.
    """
    todos: list[TodoItem] = []
    marker_re: re.Pattern[str] = re.compile(r"^\s*[-*+]\s+\[( )\]\s+")
    fence_re: re.Pattern[str] = re.compile(r"^( {0,3})(```|~~~)\s*$")

    for path in files:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as _exc:
            _log.debug("Unable to read %s", path, exc_info=_exc)
            continue

        lines = content.split("\n")
        in_frontmatter = False
        in_code_fence = False
        fence_char: str = ""
        file_offset = 0

        for line_number, line in enumerate(lines):
            if line_number == 0 and line == "---":
                in_frontmatter = True
                file_offset += len(line) + 1
                continue
            if in_frontmatter:
                if line == "---":
                    in_frontmatter = False
                file_offset += len(line) + 1
                continue

            fence_match = fence_re.match(line)
            if fence_match:
                char = fence_match.group(2)[0]
                if in_code_fence:
                    if char == fence_char:
                        in_code_fence = False
                        fence_char = ""
                else:
                    in_code_fence = True
                    fence_char = char
                file_offset += len(line) + 1
                continue
            if in_code_fence:
                file_offset += len(line) + 1
                continue

            match = marker_re.match(line)
            if match:
                # Character offset of the opening '[' within the file.
                char_offset = file_offset + line.find("[")
                item_id = hashlib.sha256(
                    f"{path.resolve().as_posix()}:{line_number}:{char_offset}".encode()
                ).hexdigest()[:16]
                todos.append(
                    TodoItem(
                        file_path=path,
                        line_text=line,
                        line_number=line_number,
                        char_offset=char_offset,
                        id=item_id,
                    )
                )

            file_offset += len(line) + 1

    return sorted(todos, key=lambda item: (str(item.file_path), item.line_number))


class TodoStateError(Exception):
    """The targeted todo line does not match the expected marker."""


OPEN_MARKER_RE: re.Pattern[str] = re.compile(r"^(\s*[-*+])\s+\[( )\]\s+(.*)$")


def close_todo(item: TodoItem) -> bool:
    """Mark a single todo as completed in its source file.

    The function reads the file from ``item.file_path``, verifies that the
    line at ``item.line_number`` still matches ``item.line_text``, then flips
    the open marker to a closed one and persists the change.

    Indentation, inline content, byte order mark and line endings are
    preserved. Only the targeted marker is changed; other todos in the file
    are untouched. The write is performed atomically by writing to a sibling
    temporary file and replacing the original with ``os.replace``.

    Args:
        item: The todo to close.

    Returns:
        ``True`` if the file was written successfully, ``False`` if the target
        line could not be matched.

    Raises:
        OSError: propagated when file I/O fails after the marker check passes.
    """
    path = item.file_path
    try:
        raw_bytes = path.read_bytes()
    except Exception as _exc:
        _log.error("Unable to read %s", path, exc_info=_exc)
        return False

    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        bom = b"\xef\xbb\xbf"
        encoding = "utf-8-sig"
    else:
        bom = b""
        encoding = "utf-8"

    newline = _detect_newline(raw_bytes)
    text = raw_bytes[len(bom) :].decode(encoding)
    lines = text.split(newline)

    if not (0 <= item.line_number < len(lines)):
        _log.warning("Todo line number %d out of range in %s", item.line_number, path)
        return False

    file_line = lines[item.line_number]
    if file_line != item.line_text:
        _log.warning(
            "Todo line does not match expected text in %s (line %d)",
            path,
            item.line_number,
        )
        return False

    open_match = OPEN_MARKER_RE.match(file_line)
    if open_match:
        prefix = open_match.group(1)
        rest = open_match.group(3)
        lines[item.line_number] = f"{prefix} [x] {rest}"
    else:
        _log.warning("No open todo marker found on line %d of %s", item.line_number, path)
        return False

    new_body = newline.join(lines)
    new_bytes = bom + new_body.encode("utf-8")

    try:
        fd, tmp_name = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "wb") as tmp_file:
                tmp_file.write(new_bytes)
        except Exception:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise
        os.replace(tmp_name, path)
    except Exception as _exc:
        _log.error("Unable to write %s", path, exc_info=_exc)
        return False
    return True


def _detect_newline(data: bytes) -> str:
    """Return the dominant newline sequence in ``data``."""
    crlf_count = data.count(b"\r\n")
    lf_count = data.count(b"\n") - crlf_count
    return "\r\n" if crlf_count >= lf_count else "\n"
