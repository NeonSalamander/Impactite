"""Regression tests for preserving file tree expansion state on refresh.

Run: uv run python test_tree_expansion.py
"""

import asyncio
import tempfile
from pathlib import Path

from impactite.app import FileTree, MarkdownEditorApp
from impactite.core import Config


def make_config(root: Path) -> Config:
    config_path = root / "config.yaml"
    notes_path = root / "notes"
    config_path.write_text(
        f'''notes_path: "{notes_path.as_posix()}"
daily_notes_folder: "Daily notes"
language: "en"
hotkeys:
  open_file: "enter"
  edit_mode: "e"
  view_mode: "v"
  save_file: "ctrl+s"
  search_tags: "ctrl+t"
  close_search: "escape"
  quit: "ctrl+q"
  refresh: "ctrl+r"
  toggle_sidebar: "ctrl+b"
display:
  show_line_numbers: true
  word_wrap: true
  syntax_theme: "monokai"
  code_border: "round"
  app_theme: "textual-dark"
tags:
  show_cloud: true
  min_tag_size: 1
  max_tag_size: 3
''',
        encoding="utf-8",
    )
    return Config.load(str(config_path))


def find_node_by_path(tree: FileTree, path: Path):
    """Найти узел дерева по пути каталога или файла."""
    for node in tree._walk_tree_nodes(tree.root):
        if isinstance(node.data, Path) and node.data == path:
            return node
    return None


async def test_selected_directory_stays_expanded():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        notes_path = root / "notes"
        notes_path.mkdir()
        projects = notes_path / "projects"
        projects.mkdir()
        (projects / "existing.md").write_text("# Existing\n", encoding="utf-8")

        config = make_config(root)
        app = MarkdownEditorApp(config=config)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            tree = app.query_one("#file-tree", FileTree)

            projects_node = find_node_by_path(tree, projects)
            assert projects_node is not None, "projects node must exist"
            projects_node.expand()
            tree.selected_dir = projects

            app._refresh_file_tree()
            await pilot.pause()

            projects_node_after = find_node_by_path(tree, projects)
            assert projects_node_after is not None, "projects node must exist after refresh"
            assert projects_node_after.is_expanded, "selected directory must stay expanded"
            assert tree.cursor_node is projects_node_after, "selected directory must remain selected"


async def test_multiple_expanded_directories_preserved():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        notes_path = root / "notes"
        notes_path.mkdir()
        projects = notes_path / "projects"
        archive = notes_path / "archive"
        projects.mkdir()
        archive.mkdir()

        config = make_config(root)
        app = MarkdownEditorApp(config=config)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            tree = app.query_one("#file-tree", FileTree)

            projects_node = find_node_by_path(tree, projects)
            archive_node = find_node_by_path(tree, archive)
            assert projects_node and archive_node
            projects_node.expand()
            archive_node.expand()

            app._refresh_file_tree()
            await pilot.pause()

            assert find_node_by_path(tree, projects).is_expanded
            assert find_node_by_path(tree, archive).is_expanded


async def test_collapsed_sibling_stays_collapsed():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        notes_path = root / "notes"
        notes_path.mkdir()
        projects = notes_path / "projects"
        drafts = notes_path / "drafts"
        projects.mkdir()
        drafts.mkdir()

        config = make_config(root)
        app = MarkdownEditorApp(config=config)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            tree = app.query_one("#file-tree", FileTree)

            projects_node = find_node_by_path(tree, projects)
            drafts_node = find_node_by_path(tree, drafts)
            assert projects_node and drafts_node
            projects_node.expand()
            # drafts intentionally left collapsed

            app._refresh_file_tree()
            await pilot.pause()

            assert find_node_by_path(tree, projects).is_expanded
            assert not find_node_by_path(tree, drafts).is_expanded


def run_sync(coro):
    return asyncio.run(coro)


if __name__ == "__main__":
    run_sync(test_selected_directory_stays_expanded())
    run_sync(test_multiple_expanded_directories_preserved())
    run_sync(test_collapsed_sibling_stays_collapsed())
    print("All tests passed.")
