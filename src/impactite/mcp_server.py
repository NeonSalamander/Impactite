"""MCP server wiring for Impactite.

This module starts a stdio-based MCP server when ``impactite --mcp <config>`` is
invoked. It registers one tool per function in ``impactite.mcp_tools`` and maps
``McpError`` exceptions to structured error responses.
"""
from __future__ import annotations

import functools
import traceback
from typing import Any, Callable, Coroutine, Dict, Optional

from mcp.server.fastmcp import FastMCP

from impactite.core import Config, FileSystem, FullTextIndex, MarkdownParser, TagIndex
from impactite.mcp_tools import McpContext, McpError
from impactite.mcp_tools import (
    create_note as _create_note,
    fill_form as _fill_form,
    find_notes_by_date_range as _find_notes_by_date_range,
    fulltext_search as _fulltext_search,
    get_note as _get_note,
    get_note_statistics as _get_note_statistics,
    get_note_types as _get_note_types,
    get_notes_linked_to_project as _get_notes_linked_to_project,
    get_type_schema as _get_type_schema,
    list_notes as _list_notes,
    list_notes_by_type as _list_notes_by_type,
    search_notes as _search_notes,
    search_similar_notes as _search_similar_notes,
    update_note as _update_note,
)

mcp_app = FastMCP("impactite")

# Populated by run_mcp before the server starts serving requests.
_CTX: Optional[McpContext] = None


F = Callable[..., Coroutine[Any, Any, Dict[str, Any]]]


def _tool_handler(fn: F) -> F:
    """Wrap a tool handler so that errors are returned as JSON-compatible dicts."""

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            return await fn(*args, **kwargs)
        except McpError as exc:
            return {"success": False, "error_code": exc.code, "error_message": exc.message}
        except Exception as exc:
            traceback.print_exc()
            return {"success": False, "error_code": "internal_error", "error_message": str(exc)}

    return wrapper  # type: ignore[return-value]


def _require_ctx() -> McpContext:
    if _CTX is None:
        raise RuntimeError("MCP context is not initialized")
    return _CTX


@mcp_app.tool()
@_tool_handler
async def get_note(note_id: str) -> Dict[str, Any]:
    """Read a single note."""
    return await _get_note(_require_ctx(), note_id=note_id)


@mcp_app.tool()
@_tool_handler
async def list_notes(filter: Optional[str] = None, type: Optional[str] = None) -> Dict[str, Any]:
    """List notes with optional substring and type filters."""
    return await _list_notes(_require_ctx(), filter=filter, type=type)


@mcp_app.tool()
@_tool_handler
async def search_notes(query: str, type_filter: Optional[str] = None) -> Dict[str, Any]:
    """Search notes by query with an optional type filter."""
    return await _search_notes(_require_ctx(), query=query, type_filter=type_filter)


@mcp_app.tool()
@_tool_handler
async def create_note(type: str, content: str, note_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a new note of a supported type."""
    return await _create_note(_require_ctx(), type=type, content=content, note_id=note_id)


@mcp_app.tool()
@_tool_handler
async def update_note(note_id: str, content: str, last_modified_at: Optional[int] = None) -> Dict[str, Any]:
    """Update the content of an existing note."""
    return await _update_note(_require_ctx(), note_id=note_id, content=content, last_modified_at=last_modified_at)


@mcp_app.tool()
@_tool_handler
async def fill_form(note_id: str, form_data: Dict[str, Any], last_modified_at: Optional[int] = None) -> Dict[str, Any]:
    """Fill a form-type note with structured data."""
    return await _fill_form(_require_ctx(), note_id=note_id, form_data=form_data, last_modified_at=last_modified_at)


@mcp_app.tool()
@_tool_handler
async def get_note_types() -> Dict[str, Any]:
    """Return the list of configured note types."""
    return await _get_note_types(_require_ctx())


@mcp_app.tool()
@_tool_handler
async def get_type_schema(type_name: str) -> Dict[str, Any]:
    """Return the schema for a single note type."""
    return await _get_type_schema(_require_ctx(), type_name=type_name)


@mcp_app.tool()
@_tool_handler
async def list_notes_by_type(type: str) -> Dict[str, Any]:
    """Return all notes of a specific type."""
    return await _list_notes_by_type(_require_ctx(), type=type)


@mcp_app.tool()
@_tool_handler
async def fulltext_search(
    query: str,
    types: Optional[list[str]] = None,
    date_range: Optional[Dict[str, Optional[int]]] = None,
) -> Dict[str, Any]:
    """Full-text search with optional type and date filters."""
    return await _fulltext_search(_require_ctx(), query=query, types=types, date_range=date_range)


@mcp_app.tool()
@_tool_handler
async def search_similar_notes(note_id: str, similarity_threshold: float = 0.0) -> Dict[str, Any]:
    """Find notes similar to a given note."""
    return await _search_similar_notes(_require_ctx(), note_id=note_id, similarity_threshold=similarity_threshold)


@mcp_app.tool()
@_tool_handler
async def get_note_statistics() -> Dict[str, Any]:
    """Return aggregate vault statistics."""
    return await _get_note_statistics(_require_ctx())


@mcp_app.tool()
@_tool_handler
async def find_notes_by_date_range(start: int, end: int) -> Dict[str, Any]:
    """Return notes modified within a Unix timestamp range."""
    return await _find_notes_by_date_range(_require_ctx(), start=start, end=end)


@mcp_app.tool()
@_tool_handler
async def get_notes_linked_to_project(project_id: str) -> Dict[str, Any]:
    """Return notes referencing a project or relationship identifier."""
    return await _get_notes_linked_to_project(_require_ctx(), project_id=project_id)


def run_mcp(config: Config) -> None:
    """Start the MCP stdio server for the given configuration."""
    global _CTX
    notes_path = config.resolve_notes_path()
    fs = FileSystem(str(notes_path))
    parser = MarkdownParser()
    tag_index = TagIndex(notes_path)
    fts_index = FullTextIndex(notes_path)
    try:
        _CTX = McpContext(
            config=config,
            fs=fs,
            parser=parser,
            tag_index=tag_index,
            fts_index=fts_index,
        )
        mcp_app.run()
    finally:
        if _CTX is not None:
            _CTX.close()
            _CTX = None
