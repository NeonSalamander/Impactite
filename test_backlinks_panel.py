"""Headless-проверка панели обратных ссылок (spec 018-backlinks-panel).

Запуск: uv run python test_backlinks_panel.py
"""
import asyncio
import tempfile
from pathlib import Path

from impactite.app import MarkdownEditorApp, BacklinksPanel
from impactite.core import Config, TagIndex, MarkdownParser
from textual.widgets import ListView


def test_core():
    """get_backlinks: инверсия LINKS_TO, сортировка, исключение самоссылок."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "a.md").write_text("# A\n[self](a.md) [to b](b.md)\n", encoding="utf-8")
        (root / "b.md").write_text("# B\n[to a](a.md)\n", encoding="utf-8")
        (root / "c.md").write_text("# C\nno links here\n", encoding="utf-8")
        ti = TagIndex(root)
        parser = MarkdownParser()
        files = list(root.rglob("*.md"))
        ti.rebuild_note_links(files, parser)
        ti.rebuild(files, parser)

        bl_a = [p.name for p in ti.get_backlinks(root / "a.md")]
        assert bl_a == ["b.md"], f"backlinks(a) = {bl_a}, ожидалось ['b.md'] без самоссылки"
        assert ti.get_backlinks(root / "b.md") == [root / "a.md"], "backlinks(b) должен быть [a.md]"
        assert ti.get_backlinks(root / "c.md") == [], "backlinks(c) должен быть пустым"
        ti.close()
    print("core: OK")


async def test_ui():
    """Панель: видимость, содержимое, навигация, скрытие на заметке без ссылок."""
    config = Config.load("config.yaml")
    app = MarkdownEditorApp(config)
    async with app.run_test() as pilot:
        await pilot.pause()
        root = app.file_system.root_path
        panel = app.query_one("#backlinks-panel", BacklinksPanel)
        lst = panel.query_one("#backlinks-list", ListView)

        # До открытия файла панель скрыта
        assert not panel.display, "панель должна быть скрыта до открытия файла"

        # Заметка с обратными ссылками: панель видна, источники отсортированы
        app.current_file = root / "test_formatting.md"
        app._load_file()
        await pilot.pause()
        assert panel.display, "панель должна быть видна для test_formatting.md"
        names = sorted(Path(i.name).name for i in lst.children)
        assert names == ["cheatsheet.md", "test_links.md"], f"неожиданный список: {names}"

        # Навигация по обратной ссылке + история для "назад"
        app.on_backlinks_panel_backlink_selected(
            BacklinksPanel.BacklinkSelected(root / "test_links.md")
        )
        await pilot.pause()
        assert app.current_file.name == "test_links.md", "навигация не сработала"
        assert app._file_history and app._file_history[-1].name == "test_formatting.md", \
            "история навигации не сохранена"
        names = sorted(Path(i.name).name for i in lst.children)
        assert names == ["cheatsheet.md"], f"backlinks(test_links) = {names}"

        # Заметка без обратных ссылок: панель скрыта
        app.current_file = root / "books" / "Dune.md"
        app._load_file()
        await pilot.pause()
        assert not panel.display, "панель должна скрываться на заметке без обратных ссылок"
    print("ui: OK")


if __name__ == "__main__":
    test_core()
    asyncio.run(test_ui())
    print("Все проверки прошли")
