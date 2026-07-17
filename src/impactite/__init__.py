"""
Markdown Viewer/Editor - консольный аналог Obsidian.
"""

from impactite.app import MarkdownEditorApp, main
from impactite.core import (
    Config, FileNode, FileSystem, MarkdownParser, QueryEngine, TagIndex,
)
from impactite.i18n import get_language, set_language, t
from impactite import templater

__all__ = [
    "Config",
    "FileSystem",
    "MarkdownParser",
    "FileNode",
    "TagIndex",
    "QueryEngine",
    "MarkdownEditorApp",
    "main",
    "t",
    "set_language",
    "get_language",
]
