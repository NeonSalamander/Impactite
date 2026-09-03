"""Smoke tests for the Impactite package."""

from __future__ import annotations

from impactite import Config, FileSystem, MarkdownParser, TagIndex, main, t
from impactite.app import MarkdownEditorApp
from impactite.core import QueryEngine
from impactite.i18n import get_language, set_language


def test_package_imports() -> None:
    """Everything required to run the app can be imported."""
    assert callable(main)
    assert callable(t)
    assert callable(get_language)
    assert callable(set_language)


def test_core_types_can_instantiate(tmp_path) -> None:
    """Core data classes build without crashing."""
    config = Config(notes_path=str(tmp_path))
    fs = FileSystem(tmp_path)
    parser = MarkdownParser()
    index = TagIndex(tmp_path)
    engine = QueryEngine(fs, parser, index)
    assert config.resolve_notes_path() == tmp_path.resolve()
    assert index is not None
    assert engine is not None


def test_app_class_exists() -> None:
    """The Textual app class is importable."""
    assert issubclass(MarkdownEditorApp, object)
