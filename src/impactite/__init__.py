"""
Markdown Viewer/Editor - консольный аналог Obsidian.
"""

from impactite.app import MarkdownEditorApp, main
from impactite.core import (
    Config,
    FileNode,
    FileSystem,
    MarkdownParser,
    QueryEngine,
    TagIndex,
)
from impactite.i18n import get_language, set_language, t
from impactite.todo_parser import (
    TodoItem,
    close_todo,
    collect_open_todos,
    find_note_files,
)

__all__ = [
    "Config",
    "FileNode",
    "FileSystem",
    "MarkdownEditorApp",
    "MarkdownParser",
    "QueryEngine",
    "TagIndex",
    "TodoItem",
    "close_todo",
    "collect_open_todos",
    "find_note_files",
    "get_language",
    "main",
    "set_language",
    "t",
]
