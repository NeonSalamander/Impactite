"""Pure MCP tool handlers for Impactite.

This module contains no Textual or MCP-server imports so that the business logic
remains unit-testable. All functions operate on an ``McpContext`` instance that
holds the vault configuration, file system, parser, tag index, and full-text
index.
"""
from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

from impactite.core import Config, FileSystem, FullTextIndex, MarkdownParser, TagIndex, parse_form_definition
from impactite.templater import build_context, collect_templates, create_from_template, render_template


class McpError(Exception):
    """Error that should be reported to the MCP client as a structured error."""

    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


@dataclass
class McpContext:
    """Runtime context shared by all MCP tool handlers."""

    config: Config
    fs: FileSystem
    parser: MarkdownParser
    tag_index: TagIndex
    fts_index: FullTextIndex
    _refresh_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _pending_refresh: Optional[asyncio.TimerHandle] = None
    _dirty: bool = False

    def refresh_indexes(self) -> None:
        """Synchronously rebuild both derived indexes."""
        files = self.fs.get_md_files()
        self.fts_index.rebuild(files)
        self.tag_index.rebuild(files, self.parser)
        self.tag_index.rebuild_note_links(files, self.parser)

    def schedule_refresh(self) -> None:
        """Mark indexes dirty and schedule an asynchronous rebuild.

        Multiple writes in quick succession collapse into a single refresh that
        runs within the 3-second visibility window defined by the spec.
        """
        self._dirty = True
        if self._pending_refresh is not None:
            self._pending_refresh.cancel()
        loop = asyncio.get_event_loop()
        self._pending_refresh = loop.call_later(1.0, self._run_refresh)

    def _run_refresh(self) -> None:
        """Background callback: run the refresh in the default executor."""
        if not self._dirty:
            return
        self._dirty = False
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.refresh_indexes)

    def close(self) -> None:
        """Close indexes and cancel pending refreshes."""
        if self._pending_refresh is not None:
            self._pending_refresh.cancel()
            self._pending_refresh = None
        self.fts_index.close()
        self.tag_index.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_RE_TITLE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_RE_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def _slugify(text: str) -> str:
    """Convert an arbitrary string into a safe filename component."""
    text = re.sub(r"[^\w\s-]", "", text).strip()
    text = re.sub(r"[-\s]+", "-", text)
    return text[:80].lower() or "untitled"


def _mtime(path: Path) -> int:
    """Return the file modification time as Unix seconds."""
    try:
        return int(path.stat().st_mtime)
    except OSError as exc:
        raise McpError("internal_error", f"Failed to stat {path}: {exc}") from exc


def _title(content: str, path: Path) -> str:
    """Derive a human-readable title from content or filename."""
    match = _RE_TITLE.search(content)
    if match:
        return match.group(1).strip()
    return path.stem


def _note_type(content: str) -> Optional[str]:
    """Return the declared note type from frontmatter, if any."""
    fm, _ = MarkdownParser()._parse_frontmatter(content)
    value = fm.get("type")
    if value and isinstance(value, str):
        return value.strip()
    return None


def _frontmatter(content: str) -> Dict[str, Any]:
    """Return parsed frontmatter as a dict."""
    fm, _ = MarkdownParser()._parse_frontmatter(content)
    return fm if isinstance(fm, dict) else {}


def _read_text(path: Path) -> str:
    """Read file contents as UTF-8, raising McpError on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise McpError("note_not_found", f"Note not found: {path.name}") from exc
    except OSError as exc:
        raise McpError("internal_error", f"Failed to read {path}: {exc}") from exc


def _resolve_note_id(ctx: McpContext, note_id: str) -> Path:
    """Resolve a relative note_id to an absolute path inside notes_path."""
    if not note_id or note_id.strip() == "":
        raise McpError("validation_error", "note_id is required")
    note_id = note_id.strip()
    if note_id.startswith("/") or ".." in Path(note_id).parts:
        raise McpError("validation_error", f"Invalid note_id: {note_id}")
    abs_path = ctx.fs.root_path / note_id
    try:
        abs_path.relative_to(ctx.fs.root_path)
    except ValueError as exc:
        raise McpError("validation_error", f"note_id escapes vault: {note_id}") from exc
    return abs_path


def _note_ref(ctx: McpContext, abs_path: Path) -> Dict[str, Any]:
    """Build a lightweight NoteRef dict for a vault file."""
    content = _read_text(abs_path)
    rel = abs_path.relative_to(ctx.fs.root_path).as_posix()
    return {
        "note_id": rel,
        "title": _title(content, abs_path),
        "type": _note_type(content),
        "modified_at": _mtime(abs_path),
    }


def _note_dict(ctx: McpContext, abs_path: Path) -> Dict[str, Any]:
    """Build a full Note dict for a vault file."""
    content = _read_text(abs_path)
    rel = abs_path.relative_to(ctx.fs.root_path).as_posix()
    stat = abs_path.stat()
    fm = _frontmatter(content)
    return {
        "note_id": rel,
        "title": _title(content, abs_path),
        "type": _note_type(content),
        "content": content,
        "frontmatter": fm,
        "created_at": int(stat.st_ctime),
        "modified_at": int(stat.st_mtime),
    }


def _write_note(ctx: McpContext, abs_path: Path, content: str) -> None:
    """Write content to a vault file, creating parent directories if needed."""
    try:
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise McpError("internal_error", f"Failed to write {abs_path}: {exc}") from exc


def _check_stale(abs_path: Path, last_modified_at: Optional[int]) -> None:
    """Optimistic concurrency check using file mtime."""
    if last_modified_at is None:
        return
    current = _mtime(abs_path)
    if current != last_modified_at:
        raise McpError(
            "stale_note",
            f"Note was modified after the client's last read "
            f"(expected {last_modified_at}, got {current})",
        )


def _list_md_files(ctx: McpContext) -> List[Path]:
    """Return all Markdown files in the vault, sorted for determinism."""
    return sorted(ctx.fs.get_md_files())


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------


async def get_note(ctx: McpContext, note_id: str) -> Dict[str, Any]:
    """Return a single note by identifier."""
    abs_path = _resolve_note_id(ctx, note_id)
    if not abs_path.exists():
        raise McpError("note_not_found", f"Note not found: {note_id}")
    return _note_dict(ctx, abs_path)


async def list_notes(
    ctx: McpContext,
    filter: Optional[str] = None,
    type: Optional[str] = None,
) -> Dict[str, Any]:
    """List notes with optional substring and type filters."""
    results: List[Dict[str, Any]] = []
    filter_lower = (filter or "").lower()
    for path in _list_md_files(ctx):
        try:
            ref = _note_ref(ctx, path)
        except McpError:
            continue
        if filter_lower and filter_lower not in ref["note_id"].lower() and filter_lower not in ref["title"].lower():
            continue
        if type and ref["type"] != type:
            continue
        results.append(ref)
    return {"notes": results}


async def search_notes(
    ctx: McpContext,
    query: str,
    type_filter: Optional[str] = None,
) -> Dict[str, Any]:
    """Search notes by query using the full-text index."""
    query = (query or "").strip()
    if not query:
        return {"results": []}
    ctx.fts_index.rebuild(_list_md_files(ctx))
    raw = ctx.fts_index.search(query, limit=100)
    results: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for item in raw:
        path = item["path"]
        rel = path.relative_to(ctx.fs.root_path).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        ref = _note_ref(ctx, path)
        if type_filter and ref["type"] != type_filter:
            continue
        results.append({
            "note_id": rel,
            "title": ref["title"],
            "type": ref["type"],
            "snippet": item.get("snippet", ""),
            "score": 0.0,
        })
    return {"results": results}


async def create_note(
    ctx: McpContext,
    type: str,
    content: str,
    note_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new note, optionally rendering a template."""
    templates = collect_templates(ctx.config.resolve_templates_path())
    template_path = templates.get(type)
    if template_path is None:
        raise McpError("type_not_found", f"Note type/template not found: {type}")

    if note_id:
        abs_path = _resolve_note_id(ctx, note_id)
    else:
        title = _title(content, Path("note.md"))
        rel = f"{type}/{_slugify(title)}.md" if type != "note" else f"{_slugify(title)}.md"
        abs_path = ctx.fs.root_path / rel

    if abs_path.exists():
        raise McpError("validation_error", f"Note already exists: {abs_path.relative_to(ctx.fs.root_path).as_posix()}")

    context = build_context(
        filepath=abs_path,
        title=_title(content, abs_path),
        author=ctx.config.author,
    )
    rendered = create_from_template(template_path, abs_path, context)
    final_content = rendered
    if content.strip():
        # If the caller supplied content, append it after the rendered template
        # unless the template already contains it.
        if content.strip() not in rendered:
            final_content = rendered.rstrip() + "\n\n" + content.strip() + "\n"

    _write_note(ctx, abs_path, final_content)
    ctx.schedule_refresh()
    rel = abs_path.relative_to(ctx.fs.root_path).as_posix()
    return {"note_id": rel, "success": True, "error_code": None, "error_message": None}


async def update_note(
    ctx: McpContext,
    note_id: str,
    content: str,
    last_modified_at: Optional[int] = None,
) -> Dict[str, Any]:
    """Replace the content of an existing note."""
    abs_path = _resolve_note_id(ctx, note_id)
    if not abs_path.exists():
        raise McpError("note_not_found", f"Note not found: {note_id}")
    _check_stale(abs_path, last_modified_at)
    _write_note(ctx, abs_path, content)
    ctx.schedule_refresh()
    return {"note_id": note_id, "success": True, "error_code": None, "error_message": None}


async def fill_form(
    ctx: McpContext,
    note_id: str,
    form_data: Dict[str, Any],
    last_modified_at: Optional[int] = None,
) -> Dict[str, Any]:
    """Fill a form-type note with structured data."""
    abs_path = _resolve_note_id(ctx, note_id)
    if not abs_path.exists():
        raise McpError("note_not_found", f"Note not found: {note_id}")
    content = _read_text(abs_path)
    form_def = parse_form_definition(content)
    if not form_def:
        raise McpError("validation_error", f"Note is not a form: {note_id}")

    fields = form_def.get("fields") or []
    required = {f["name"] for f in fields if isinstance(f, dict) and f.get("required")}
    missing = required - set(form_data.keys())
    if missing:
        raise McpError("validation_error", f"Missing required fields: {', '.join(sorted(missing))}")

    _check_stale(abs_path, last_modified_at)

    fm, body = ctx.parser._parse_frontmatter(content)
    rendered_body = render_template(body, {**form_data, "form": form_data})

    if fm:
        fm_lines = ["---", yaml.safe_dump(fm, default_flow_style=False, allow_unicode=True).strip(), "---"]
        new_content = "\n".join(fm_lines) + "\n" + rendered_body
    else:
        new_content = rendered_body

    _write_note(ctx, abs_path, new_content)
    ctx.schedule_refresh()
    return {"note_id": note_id, "success": True, "error_code": None, "error_message": None}


async def get_note_types(ctx: McpContext) -> Dict[str, Any]:
    """Return all configured note types (template names)."""
    templates = collect_templates(ctx.config.resolve_templates_path())
    types = [{"name": name, "label": name.replace("_", " ").title()} for name in sorted(templates)]
    return {"types": types}


async def get_type_schema(ctx: McpContext, type_name: str) -> Dict[str, Any]:
    """Return the schema for a note type."""
    templates = collect_templates(ctx.config.resolve_templates_path())
    template_path = templates.get(type_name)
    if template_path is None:
        raise McpError("type_not_found", f"Note type not found: {type_name}")
    content = _read_text(template_path)
    placeholders = sorted(set(_RE_PLACEHOLDER.findall(content)))
    fields: List[Dict[str, Any]] = [
        {"name": name, "required": False, "type": "string", "description": None}
        for name in placeholders
    ]
    fields.insert(0, {"name": "content", "required": False, "type": "string", "description": "Free-form Markdown content"})
    return {
        "name": type_name,
        "label": type_name.replace("_", " ").title(),
        "fields": fields,
        "default_template": template_path.relative_to(ctx.config.resolve_templates_path()).as_posix(),
    }


async def list_notes_by_type(ctx: McpContext, type: str) -> Dict[str, Any]:
    """Return all notes of a specific type."""
    templates = collect_templates(ctx.config.resolve_templates_path())
    if type not in templates:
        raise McpError("type_not_found", f"Note type not found: {type}")
    return await list_notes(ctx, type=type)


async def fulltext_search(
    ctx: McpContext,
    query: str,
    types: Optional[List[str]] = None,
    date_range: Optional[Dict[str, Optional[int]]] = None,
) -> Dict[str, Any]:
    """Execute a full-text search with optional type and date filters."""
    query = (query or "").strip()
    if not query:
        return {"results": []}
    start = (date_range or {}).get("start")
    end = (date_range or {}).get("end")
    if start is not None and end is not None and start > end:
        raise McpError("invalid_date_range", "Start date must be before end date")

    ctx.fts_index.rebuild(_list_md_files(ctx))
    raw = ctx.fts_index.search(query, limit=200)
    results = []
    seen: Set[str] = set()
    for item in raw:
        path = item["path"]
        rel = path.relative_to(ctx.fs.root_path).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        ref = _note_ref(ctx, path)
        if types and ref["type"] not in types:
            continue
        mtime = ref["modified_at"]
        if start is not None and mtime < start:
            continue
        if end is not None and mtime > end:
            continue
        results.append({
            "note_id": rel,
            "title": ref["title"],
            "type": ref["type"],
            "snippet": item.get("snippet", ""),
            "score": 0.0,
        })
    return {"results": results}


async def search_similar_notes(
    ctx: McpContext,
    note_id: str,
    similarity_threshold: float = 0.0,
) -> Dict[str, Any]:
    """Find notes similar to a given note using FTS overlap plus tag/link proximity."""
    source_path = _resolve_note_id(ctx, note_id)
    if not source_path.exists():
        raise McpError("note_not_found", f"Note not found: {note_id}")
    source_content = _read_text(source_path)
    source_tags = ctx.parser.extract_tags(source_content)
    source_links = ctx.parser.extract_internal_links(source_content)

    ctx.fts_index.rebuild(_list_md_files(ctx))

    candidates: Dict[str, Dict[str, Any]] = {}

    # Use the first heading as a small query to surface content-overlap candidates.
    title = _title(source_content, source_path)
    if title:
        for item in ctx.fts_index.search(title, limit=50):
            path = item["path"]
            rel = path.relative_to(ctx.fs.root_path).as_posix()
            if rel == note_id:
                continue
            candidates[rel] = {"path": path, "score": 0.5, "snippet": item.get("snippet", "")}

    # Score by shared tags and internal links.
    for path in _list_md_files(ctx):
        rel = path.relative_to(ctx.fs.root_path).as_posix()
        if rel == note_id:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        tags = ctx.parser.extract_tags(content)
        links = ctx.parser.extract_internal_links(content)
        score = 0.0
        shared_tags = source_tags & tags
        shared_links = source_links & links
        if source_links:
            score += len(shared_links) / len(source_links) * 3.0
        if source_tags:
            score += len(shared_tags) / len(source_tags) * 2.0
        if not score:
            continue
        if rel not in candidates:
            snippet = ""
            if shared_tags:
                snippet = "Tags: " + ", ".join(sorted(shared_tags))
            candidates[rel] = {"path": path, "score": score, "snippet": snippet}
        else:
            candidates[rel]["score"] += score

    results = []
    for rel, data in candidates.items():
        if data["score"] < similarity_threshold:
            continue
        ref = _note_ref(ctx, data["path"])
        results.append({
            "note_id": rel,
            "title": ref["title"],
            "type": ref["type"],
            "snippet": data["snippet"],
            "score": round(data["score"], 2),
        })
    results.sort(key=lambda r: r["score"], reverse=True)
    return {"results": results}


async def get_note_statistics(ctx: McpContext) -> Dict[str, Any]:
    """Return vault-level statistics."""
    total = 0
    by_type: Dict[str, int] = {}
    for path in _list_md_files(ctx):
        total += 1
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        nt = _note_type(content)
        by_type.setdefault(nt or "note", 0)
        by_type[nt or "note"] += 1
    return {"total_notes": total, "by_type": by_type}


async def find_notes_by_date_range(
    ctx: McpContext,
    start: int,
    end: int,
) -> Dict[str, Any]:
    """Return notes created or modified within a Unix timestamp range."""
    if start > end:
        raise McpError("invalid_date_range", "Start date must be before end date")
    results = []
    for path in _list_md_files(ctx):
        mtime = _mtime(path)
        if start <= mtime <= end:
            results.append(_note_ref(ctx, path))
    return {"notes": results}


async def get_notes_linked_to_project(
    ctx: McpContext,
    project_id: str,
) -> Dict[str, Any]:
    """Return notes referencing a project or relationship identifier."""
    if not project_id:
        raise McpError("validation_error", "project_id is required")
    query = project_id.strip()
    ctx.fts_index.rebuild(_list_md_files(ctx))
    raw = ctx.fts_index.search(query, limit=200)
    results = []
    seen: Set[str] = set()
    for item in raw:
        path = item["path"]
        rel = path.relative_to(ctx.fs.root_path).as_posix()
        if rel in seen:
            continue
        seen.add(rel)
        results.append(_note_ref(ctx, path))
    return {"notes": results}


# ---------------------------------------------------------------------------
# Refresh helper
# ---------------------------------------------------------------------------

async def refresh_now(ctx: McpContext) -> Dict[str, Any]:
    """Force an immediate index refresh (helper tool, not part of the public contract)."""
    ctx.refresh_indexes()
    return {"success": True}
