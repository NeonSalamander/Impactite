"""
Основное приложение Markdown Viewer/Editor.
Консольный аналог Obsidian с использованием Textual и Rich.
"""

import re
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Set

from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    OptionList,
    RichLog,
    Select,
    SelectionList,
    Static,
    Switch,
    TextArea,
    Tree,
)
from textual.widgets.option_list import Option
from textual.widgets.selection_list import Selection
from textual.widgets._select import NoSelection

from impactite.core import (
    Config, FileNode, FileSystem, MarkdownParser, QueryEngine, TagIndex,
    parse_form_definition,
)
from impactite.i18n import _, retranslate_bindings, set_language

_LIGHT_THEMES: frozenset[str] = frozenset({
    "textual-light", "solarized-light", "catppuccin-latte",
    "rose-pine-dawn", "atom-one-light",
})

# ============================================================================
# Виджеты
# ============================================================================


class TagCloud(ListView):
    """Кликабельный список тегов."""

    class TagClicked(Message):
        def __init__(self, tag: str) -> None:
            self.tag = tag
            super().__init__()

    def update_tags(self, tags: Dict[str, int], colors: Dict[str, str] = None) -> None:
        self.clear()
        if not tags:
            self.append(ListItem(Label(f"[dim]{_('No tags')}[/dim]"), name=""))
            return
        colors = colors or {}
        for tag, count in sorted(tags.items(), key=lambda x: x[1], reverse=True):
            color = colors.get(tag, "")
            label = f"[{color}]#{tag}[/{color}] [dim]{count}[/dim]" if color else f"#{tag} [dim]{count}[/dim]"
            self.append(ListItem(Label(label), name=tag))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        event.stop()
        if event.item.name:
            self.post_message(self.TagClicked(event.item.name))


class FileTree(Tree):
    """Дерево файлов."""

    class FileSelected(Message):
        """Сообщение о выборе файла."""

        def __init__(self, path: Path):
            self.path = path
            super().__init__()

    def __init__(self, root_label: str, **kwargs):
        super().__init__(root_label, **kwargs)
        self.show_root = False
        self.file_nodes: Dict[int, Path] = {}
        self.dir_nodes: Dict[int, Path] = {}
        self.root_path: Optional[Path] = None
        # Текущий выбранный каталог (для создания заметок/папок)
        self.selected_dir: Optional[Path] = None

    def populate_tree(self, file_system: FileSystem, favorites: Optional[List[str]] = None):
        """Заполнить дерево файлами."""
        self.clear()
        self.file_nodes.clear()
        self.dir_nodes.clear()
        self.root_path = file_system.root_path
        self.root.expand()

        if favorites:
            existing: List[Path] = []
            for f in favorites:
                fp = Path(f).resolve()
                if fp.exists():
                    existing.append(fp)
            if existing:
                fav_node = self.root.add(_("⭐ Favorites"), expand=False)
                for fp in existing:
                    node = fav_node.add(f"⭐ {fp.name}")
                    self.file_nodes[id(node)] = fp

        tree = file_system.get_tree()
        self._add_nodes(self.root, tree)

    def current_dir(self) -> Optional[Path]:
        """Каталог, в котором создавать новые заметки/папки."""
        return self.selected_dir or self.root_path

    def _add_nodes(self, parent_node, file_node: FileNode):
        """Рекурсивно добавить узлы."""
        for child in sorted(file_node.children):
            if child.is_dir:
                dir_node = parent_node.add(f"📁 {child.name}", expand=False)
                self.dir_nodes[id(dir_node)] = child.path
                self._add_nodes(dir_node, child)
            else:
                icon = "📄" if child.name.endswith(".md") else "📎"
                node = parent_node.add(f"{icon} {child.name}")
                self.file_nodes[id(node)] = child.path

    def on_tree_node_selected(self, event: Tree.NodeSelected):
        """Обработать выбор узла."""
        node_id = id(event.node)
        if node_id in self.file_nodes:
            # Каталог для создания — папка, в которой лежит выбранный файл
            self.selected_dir = self.file_nodes[node_id].parent
            self.post_message(self.FileSelected(self.file_nodes[node_id]))
        elif node_id in self.dir_nodes:
            self.selected_dir = self.dir_nodes[node_id]


class ToolButton(Static):
    """Однострочная кликабельная кнопка-иконка для тулбара.

    Обычный textual Button по сути трёхстрочный, и при height: 1 его подпись
    обрезается. Здесь — однострочный Static, поэтому иконка всегда видна.
    """

    class Pressed(Message):
        def __init__(self, button_id: str) -> None:
            self.button_id = button_id
            super().__init__()

    def on_click(self, event) -> None:
        event.stop()
        self.post_message(self.Pressed(self.id or ""))


class ViewerLog(RichLog):
    """RichLog с перехватом кликов — фиксирует абсолютные экранные координаты."""

    class Clicked(Message):
        def __init__(self, screen_y: int, screen_x: int) -> None:
            self.screen_y = screen_y
            self.screen_x = screen_x
            super().__init__()

    def on_click(self, event) -> None:
        self.post_message(self.Clicked(event.screen_y, event.screen_x))


class MarkdownViewer(Static):
    """Виджет для просмотра Markdown с прокруткой."""

    can_focus = True

    BINDINGS = [
        Binding("up",       "scroll_up",   show=False),
        Binding("down",     "scroll_down", show=False),
        Binding("pageup",   "page_up",     show=False),
        Binding("pagedown", "page_down",   show=False),
        Binding("home",     "scroll_home", show=False),
        Binding("end",      "scroll_end",  show=False),
    ]

    class TagClicked(Message):
        def __init__(self, tag: str) -> None:
            self.tag = tag
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._content = ""
        # Каждый элемент соответствует одной визуальной строке:
        # None — строка без тегов, (tags, plain_text) — строка с тегами
        self._tag_lines: list = []

    def compose(self):
        yield ViewerLog(markup=True, highlight=False, wrap=True)

    def action_scroll_up(self)   -> None: self.query_one(ViewerLog).scroll_up()
    def action_scroll_down(self) -> None: self.query_one(ViewerLog).scroll_down()
    def action_page_up(self)     -> None: self.query_one(ViewerLog).scroll_page_up()
    def action_page_down(self)   -> None: self.query_one(ViewerLog).scroll_page_down()
    def action_scroll_home(self) -> None: self.query_one(ViewerLog).scroll_home()
    def action_scroll_end(self)  -> None: self.query_one(ViewerLog).scroll_end()

    def on_viewer_log_clicked(self, event: ViewerLog.Clicked) -> None:
        """Обработать клик по тексту заметки — найти тег под курсором."""
        log = self.query_one(ViewerLog)
        cr = log.content_region          # абсолютные экранные координаты контента
        line_idx = event.screen_y - cr.y + int(log.scroll_y)
        if not (0 <= line_idx < len(self._tag_lines)):
            return
        entry = self._tag_lines[line_idx]
        if not entry:
            return
        tags, plain = entry
        tag = self._tag_at_col(plain, tags, event.screen_x - cr.x) or tags[0]
        self.post_message(self.TagClicked(tag))

    @staticmethod
    def _tag_at_col(line: str, tags: list, col: int):
        """Определить тег по горизонтальной позиции клика."""
        for tag in tags:
            idx = line.find(f"#{tag}")
            if idx != -1 and idx <= col < idx + len(tag) + 1:
                return tag
        return None

    def update_content(self, content: str):
        """Обновить содержимое."""
        self._content = content
        self._tag_lines = []
        log = self.query_one(ViewerLog)
        log.clear()

        if not content:
            log.write(f"[italic]{_('Select a file to view')}[/italic]")
            self._tag_lines.append(None)
            return

        lines = content.split("\n")
        in_code_block = False
        code_lines = []
        code_language = ""

        for line in lines:
            code_match = re.match(r"^```(\w*)", line)
            if code_match:
                if not in_code_block:
                    in_code_block = True
                    code_language = code_match.group(1) or "text"
                    code_lines = []
                else:
                    if code_language in ("query", "dataview"):
                        height = self._render_query_block(log, "\n".join(code_lines))
                    else:
                        try:
                            is_light = self.app.theme in _LIGHT_THEMES
                        except Exception:
                            is_light = False
                        syntax = Syntax(
                            "\n".join(code_lines),
                            code_language,
                            theme="friendly" if is_light else "monokai",
                            padding=(0, 1),
                        )
                        log.write(syntax)
                        height = max(1, len(code_lines))
                    # блок занимает примерно height визуальных строк
                    for _ in range(height):
                        self._tag_lines.append(None)
                    in_code_block = False
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # Заголовки
            if line.startswith("# "):
                log.write(f"[bold magenta]{line[2:]}[/bold magenta]")
                self._tag_lines.append(None)
            elif line.startswith("## "):
                log.write(f"[bold blue]{line[3:]}[/bold blue]")
                self._tag_lines.append(None)
            elif line.startswith("### "):
                log.write(f"[bold green]{line[4:]}[/bold green]")
                self._tag_lines.append(None)
            # Списки
            elif line.startswith("- ") or line.startswith("* "):
                log.write(f"  • {line[2:]}")
                self._tag_lines.append(None)
            elif re.match(r"^\d+\. ", line):
                match = re.match(r"^(\d+)\. (.*)", line)
                if match:
                    log.write(f"  {match.group(1)}. {match.group(2)}")
                    self._tag_lines.append(None)
            # Цитаты
            elif line.startswith("> "):
                log.write(f"[italic yellow]  {line[2:]}[/italic yellow]")
                self._tag_lines.append(None)
            # Теги
            elif re.search(r"#\w+", line):
                try:
                    tag_colors = self.app.tag_colors
                except Exception:
                    tag_colors = {}
                tags_in_line = re.findall(r"#(\w+)", line)
                parts = re.split(r"(#\w+)", line)
                formatted = ""
                for part in parts:
                    if re.match(r"#\w+", part):
                        color = tag_colors.get(part[1:], "")
                        if color:
                            formatted += f"[bold {color}]{part}[/bold {color}]"
                        else:
                            formatted += f"[bold cyan]{part}[/bold cyan]"
                    else:
                        formatted += part
                log.write(formatted)
                self._tag_lines.append((tags_in_line, line))
            # Жирный/курсив
            elif "**" in line or "__" in line:
                formatted = self._process_formatting_inline(line)
                log.write(formatted)
                self._tag_lines.append(None)
            # Пустые строки
            elif not line.strip():
                log.write("")
                self._tag_lines.append(None)
            # Обычный текст
            else:
                log.write(line)
                self._tag_lines.append(None)

    def _process_formatting_inline(self, line: str) -> str:
        """Обработать жирный и курсивный текст."""
        # **жирный**
        line = re.sub(r"\*\*(.+?)\*\*", r"[bold]\1[/bold]", line)
        # __жирный__
        line = re.sub(r"__(.+?)__", r"[bold]\1[/bold]", line)
        # *курсив*
        line = re.sub(r"\*(.+?)\*", r"[italic]\1[/italic]", line)
        return line

    def _render_query_block(self, log: "ViewerLog", query_text: str) -> int:
        """Выполнить псевдо-SQL запрос и отрендерить результат таблицей.

        Возвращает примерную высоту отрисованного блока (в строках).
        """
        engine = getattr(self.app, "query_engine", None)
        if engine is None:
            log.write(f"[red]{_('Query engine unavailable')}[/red]")
            return 1
        try:
            columns, rows = engine.execute(query_text)
        except Exception as e:
            log.write(f"[red]{_('Query error: {error}', error=e)}[/red]")
            return 1

        if not columns:
            log.write(f"[italic dim]{_('Query returned no data')}[/italic dim]")
            return 1

        table = Table(expand=False, header_style="bold magenta", border_style="dim")
        for col in columns:
            table.add_column(str(col))
        for row in rows:
            table.add_row(*[str(row.get(c, "")) for c in columns])
        log.write(table)
        if not rows:
            log.write(f"[italic dim]{_('0 records')}[/italic dim]")
        # высота: рамки сверху/снизу + заголовок + разделитель + строки
        return len(rows) + 4


class FormView(VerticalScroll):
    """Отображает заметку типа 'form' как интерактивную форму ввода данных."""

    BINDINGS = [Binding("ctrl+s", "save_form", "Save", show=False)]

    class Saved(Message):
        def __init__(self, catalog: str, destination: str, values: dict) -> None:
            self.catalog = catalog
            self.destination = destination
            self.values = values
            super().__init__()

    class Cancelled(Message):
        pass

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._catalog: str = ""
        self._destination: str = "note"
        self._field_defs: list = []

    def compose(self) -> ComposeResult:
        yield Vertical(id="form-fields")
        with Horizontal(id="form-buttons"):
            yield Button(_("Save"), id="form-save", variant="primary")
            yield Button(_("Cancel"), id="form-cancel", variant="error")

    def load_form(self, catalog: str, field_defs: list, destination: str = "note") -> None:
        """Заполнить форму по переданным field_defs."""
        self._catalog = catalog
        self._destination = destination
        self._field_defs = field_defs
        widgets: list = []
        for fd in field_defs:
            if not isinstance(fd, dict):
                continue
            for name, info in fd.items():
                if not isinstance(info, list) or len(info) < 2:
                    continue
                alias = str(info[0])
                widgets.append(Label(f"[bold]{alias}[/bold]", classes="field-label"))
                widgets.append(self._make_input(name, info))
        # Пересборка через worker: дождаться удаления старых полей перед монтированием
        self.run_worker(self._rebuild_fields(widgets), exclusive=True)

    async def _rebuild_fields(self, widgets: list) -> None:
        container = self.query_one("#form-fields", Vertical)
        await container.remove_children()
        if widgets:
            await container.mount(*widgets)
        self.scroll_home(animate=False)

    def _make_input(self, name: str, info: list) -> "Widget":
        wid = f"field-{name}"
        ftype = str(info[1]).lower()
        if ftype == "boolean":
            return Switch(id=wid, classes="field-widget")
        if ftype == "text":
            return TextArea(id=wid, classes="field-widget field-text")
        if ftype == "integer":
            return Input(placeholder="0", type="integer", id=wid, classes="field-widget")
        if ftype == "date":
            return Input(placeholder=_("YYYY-MM-DD"), restrict=r"[\d\-]*",
                         id=wid, classes="field-widget")
        if ftype == "list":
            mode = str(info[2]).lower() if len(info) > 2 else ""
            options = info[3] if len(info) > 3 and isinstance(info[3], list) else []
            opts = [str(o) for o in options]
            if mode == "multi-select":
                return SelectionList(
                    *[Selection(o, o) for o in opts],
                    id=wid, classes="field-widget field-multiselect",
                )
            if mode == "select":
                return Select(
                    [(o, o) for o in opts], allow_blank=True,
                    id=wid, classes="field-widget",
                )
            # обычный список через свободный ввод
            return Input(placeholder=_("value1, value2 ..."),
                         id=wid, classes="field-widget")
        # string
        length = int(info[2]) if len(info) > 2 and str(info[2]).isdigit() else 0
        kw = {"max_length": length} if length > 0 else {}
        return Input(placeholder="...", id=wid, classes="field-widget", **kw)

    def _collect_values(self) -> dict:
        values: dict = {}
        for fd in self._field_defs:
            if not isinstance(fd, dict):
                continue
            for name, info in fd.items():
                ftype = str(info[1]).lower() if len(info) > 1 else "string"
                wid = f"#field-{name}"
                try:
                    if ftype == "boolean":
                        values[name] = self.query_one(wid, Switch).value
                    elif ftype == "text":
                        values[name] = self.query_one(wid, TextArea).text
                    elif ftype == "integer":
                        v = self.query_one(wid, Input).value.strip()
                        values[name] = int(v) if v else 0
                    elif ftype == "list":
                        mode = str(info[2]).lower() if len(info) > 2 else ""
                        if mode == "multi-select":
                            values[name] = list(self.query_one(wid, SelectionList).selected)
                        elif mode == "select":
                            sel = self.query_one(wid, Select).value
                            values[name] = None if isinstance(sel, NoSelection) else sel
                        else:
                            raw = self.query_one(wid, Input).value
                            values[name] = [
                                i.strip() for i in re.split(r"[,\s]+", raw) if i.strip()
                            ]
                    else:
                        values[name] = self.query_one(wid, Input).value
                except Exception:
                    values[name] = None
        return values

    def action_save_form(self) -> None:
        self.post_message(self.Saved(self._catalog, self._destination, self._collect_values()))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "form-save":
            self.post_message(self.Saved(self._catalog, self._destination, self._collect_values()))
        elif event.button.id == "form-cancel":
            self.post_message(self.Cancelled())


class TagSearchModal(ModalScreen):
    """Модальное окно поиска по тегам."""

    BINDINGS = [Binding("escape", "close", "Close")]

    class FileSelected(Message):
        def __init__(self, path: Path):
            self.path = path
            super().__init__()

    def __init__(self, all_tags: Dict[str, List[Path]], initial_query: str = "",
                 tag_colors: Dict[str, str] = None, **kwargs):
        super().__init__(**kwargs)
        self.all_tags = all_tags
        self.initial_query = initial_query
        self.tag_colors = tag_colors or {}
        self.current_results: List[tuple] = []

    def on_mount(self) -> None:
        if self.initial_query:
            self.query_one("#search-input", Input).value = self.initial_query

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"[bold]{_('Tag search')}[/bold]"),
            Input(placeholder=_("Enter tag (without #)"), id="search-input"),
            OptionList(id="results"),
            Label(f"[dim]{_('Escape to close')}[/dim]"),
            id="search-container",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip().lstrip("#")
        results_widget = self.query_one("#results", OptionList)
        results_widget.clear_options()
        self.current_results = []

        if not query:
            return

        seen_paths: set = set()
        for tag, files in self.all_tags.items():
            if query.lower() in tag.lower():
                for file_path in files:
                    if file_path not in seen_paths:
                        seen_paths.add(file_path)
                        self.current_results.append((tag, file_path))

        if not self.current_results:
            results_widget.add_option(Option(_("No files found"), id="empty"))
        else:
            for i, (tag, path) in enumerate(self.current_results):
                color = self.tag_colors.get(tag, "")
                tag_text = f"[{color}]#{tag}[/{color}]" if color else f"#{tag}"
                results_widget.add_option(
                    Option(f"{tag_text}  —  {path.name}", id=f"f{i}")
                )

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_id and event.option_id.startswith("f"):
            idx = int(event.option_id[1:])
            _, path = self.current_results[idx]
            self.post_message(self.FileSelected(path))
            self.dismiss()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if self.current_results:
            _, path = self.current_results[0]
            self.post_message(self.FileSelected(path))
            self.dismiss()

    def action_close(self) -> None:
        self.dismiss()


class UnsavedChangesModal(ModalScreen):
    """Диалог несохранённых изменений."""

    BINDINGS = [
        Binding("escape", "discard",      "Don't save"),
        Binding("left",   "prev_button",  show=False),
        Binding("right",  "next_button",  show=False),
    ]

    class Save(Message):
        pass

    class Discard(Message):
        pass

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"[bold]{_('Unsaved changes')}[/bold]"),
            Label(_("Save changes before leaving the editor?")),
            Horizontal(
                Button(_("Save"), id="save-btn", variant="primary"),
                Button(_("Don't save"), id="discard-btn", variant="error"),
                id="dialog-buttons",
            ),
            id="unsaved-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#save-btn", Button).focus()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save-btn":
            self.post_message(self.Save())
        else:
            self.post_message(self.Discard())
        self.dismiss()

    def action_prev_button(self) -> None:
        self.focus_previous()

    def action_next_button(self) -> None:
        self.focus_next()

    def action_discard(self):
        self.post_message(self.Discard())
        self.dismiss()


class TextPromptModal(ModalScreen[Optional[str]]):
    """Модальное окно ввода одной строки (имя каталога / заметки).

    Закрывается через ``dismiss`` с введённой строкой (или ``None`` при отмене).
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, placeholder: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"[bold]{self._title}[/bold]"),
            Input(placeholder=self._placeholder, id="prompt-input"),
            Label(f"[dim]{_('Enter — confirm, Escape — cancel')}[/dim]"),
            id="prompt-container",
        )

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip() or None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ============================================================================
# Главное приложение
# ============================================================================


class MarkdownEditorApp(App):
    """Основное приложение."""

    TITLE = "Impactite"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save", "Save"),
        Binding("e", "toggle_edit", "Edit"),
        Binding("escape", "exit_edit", "Exit editor", show=False),
        Binding("ctrl+t", "search_tags", "Tags"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+b", "toggle_sidebar", "Sidebar"),
        Binding("ctrl+l", "toggle_theme", "Theme"),
        Binding("ctrl+f", "toggle_favorite", "Favorite"),
    ]

    DEFAULT_CSS = """
    Screen {
        background: $background;
    }

    #main-container {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 30 1fr;
        height: 1fr;
    }

    #sidebar {
        border: solid $primary-darken-2;
        padding: 0;
        background: $surface;
    }

    #sidebar-header {
        height: 1;
        background: $panel;
    }

    #sidebar-label {
        padding: 0 1;
        width: 1fr;
        height: 1;
        content-align: left middle;
        background: $panel;
    }

    .sidebar-btn {
        width: 5;
        height: 1;
        margin: 0 0 0 1;
        padding: 0 1;
        text-align: center;
        background: $primary-darken-1;
        color: $text;
    }

    .sidebar-btn:hover {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #tag-cloud Label {
        color: $primary;
    }

    #file-tree {
        height: 1fr;
    }

    #tag-cloud-container {
        height: auto;
        max-height: 12;
        border-top: solid $primary-darken-2;
        padding: 0 1 1 1;
        background: $surface-darken-1;
    }

    #tag-cloud {
        background: $surface-darken-1;
        border: none;
        height: auto;
        max-height: 9;
        padding: 0;
    }

    #content-area {
        padding: 0;
        background: $background;
    }

    #viewer {
        padding: 0;
        height: 1fr;
    }

    #viewer ViewerLog {
        padding: 1 2;
        height: 1fr;
    }

    #editor {
        display: none;
    }

    #form-view {
        display: none;
        padding: 1 2;
    }

    #form-fields {
        height: auto;
    }

    .field-label {
        margin-top: 1;
        color: $text;
    }

    .field-widget {
        width: 100%;
        margin-bottom: 0;
    }

    .field-text {
        height: 6;
    }

    .field-multiselect {
        height: auto;
        max-height: 8;
    }

    .field-multiselect > .selection-list--button-selected {
        color: $panel;
        background: $success;
        text-style: bold;
    }

    .field-multiselect > .selection-list--button-selected-highlighted {
        color: $panel;
        background: $success-lighten-1;
        text-style: bold;
    }

    #form-buttons {
        margin-top: 2;
        height: auto;
    }

    #form-buttons Button {
        margin-right: 1;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $primary-darken-3;
        padding: 0 1;
    }

    .hidden {
        display: none;
    }

    UnsavedChangesModal {
        align: center middle;
        background: $background 50%;
    }

    #unsaved-dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #dialog-buttons {
        margin-top: 1;
        height: auto;
    }

    #dialog-buttons Button {
        margin-right: 1;
    }

    TagSearchModal {
        align: center middle;
        background: $background 50%;
    }

    TagSearchModal Container {
        width: 90%;
        height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    TagSearchModal #search-input {
        width: 100%;
        margin: 1 0;
    }

    TagSearchModal #results {
        width: 100%;
        height: 1fr;
        background: $background;
    }

    TextPromptModal {
        align: center middle;
        background: $background 50%;
    }

    #prompt-container {
        width: 60;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
    }

    #prompt-input {
        width: 100%;
        margin: 1 0;
    }
    """

    def __init__(self, config: Config = None):
        super().__init__()
        self.config = config or Config.load()
        set_language(self.config.language)
        self.file_system = FileSystem(str(self.config.resolve_notes_path()))
        self.parser = MarkdownParser(
            syntax_theme=self.config.display.get("syntax_theme", "monokai")
        )
        self.theme = self.config.display.get("app_theme", "textual-dark")

        self.current_file: Optional[Path] = None
        self.is_edit_mode = False
        self.sidebar_visible = True
        self.tag_cache: Dict[str, List[Path]] = {}
        self.tag_colors: Dict[str, str] = {}
        self._original_content: str = ""
        self.tag_index = TagIndex(self.file_system.root_path)
        self.query_engine = QueryEngine(self.file_system, self.parser, self.tag_index)
        self._rebuild_tag_cache()

    def _rebuild_tag_cache(self):
        """Обновить SQLite-индекс и перезагрузить кэш тегов и цветов."""
        self.tag_index.rebuild(self.file_system.get_md_files(), self.parser)
        self.tag_cache = self.tag_index.get_tag_files()
        self.tag_colors = self.tag_index.get_tag_colors()

    def _refresh_file_tree(self) -> None:
        """Перестроить дерево файлов с учётом избранного."""
        self.query_one("#file-tree", FileTree).populate_tree(
            self.file_system, self.tag_index.get_favorites()
        )

    def action_toggle_favorite(self) -> None:
        """Добавить / убрать текущую заметку из избранного."""
        if not self.current_file:
            return
        path_str = str(self.current_file)
        is_fav = self.tag_index.toggle_favorite(path_str)
        self.notify(
            _("Added to favorites") if is_fav else _("Removed from favorites"),
            severity="information",
        )
        self._refresh_file_tree()
        self._update_status()

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main-container"):
            with Vertical(id="sidebar"):
                with Horizontal(id="sidebar-header"):
                    yield Label(f"[bold]{self.file_system.root_path.name}[/bold]", id="sidebar-label")
                    new_folder = ToolButton("+📁", id="new-folder-btn", classes="sidebar-btn")
                    new_folder.tooltip = _("Create folder")
                    yield new_folder
                    new_note = ToolButton("+📄", id="new-note-btn", classes="sidebar-btn")
                    new_note.tooltip = _("Create note")
                    yield new_note
                    fav_btn = ToolButton("⭐", id="toggle-fav-btn", classes="sidebar-btn")
                    fav_btn.tooltip = _("Toggle favorite")
                    yield fav_btn
                yield FileTree("Файлы", id="file-tree")
                with Vertical(id="tag-cloud-container"):
                    yield Label(f"[bold]{_('Tags')}[/bold]")
                    yield TagCloud(id="tag-cloud")

            with Vertical(id="content-area"):
                yield MarkdownViewer(id="viewer")
                yield TextArea(id="editor", language="markdown")
                yield FormView(id="form-view")

        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self):
        """Инициализация после монтирования."""
        retranslate_bindings(self)
        self.refresh_bindings()
        self._refresh_file_tree()
        self._update_tag_cloud()

        editor = self.query_one("#editor", TextArea)
        editor.display = False
        self.query_one("#form-view", FormView).display = False
        self._register_markdown_highlights(editor)
        self._apply_editor_syntax_theme(editor)
        self._update_status()

    def _apply_editor_syntax_theme(self, editor: TextArea) -> None:
        """Установить синтаксическую тему редактора под текущую тему приложения."""
        if self.theme in _LIGHT_THEMES:
            editor.theme = "github_light"
        else:
            editor.theme = self.config.display.get("syntax_theme", "monokai")

    def action_toggle_theme(self) -> None:
        """Переключить светлую / тёмную тему и сохранить выбор."""
        if self.theme in _LIGHT_THEMES:
            new_theme = self.config.display.get("app_theme", "textual-dark")
            if new_theme in _LIGHT_THEMES:
                new_theme = "textual-dark"
        else:
            new_theme = "textual-light"
        self.theme = new_theme
        self.config.save_theme(new_theme)
        editor = self.query_one("#editor", TextArea)
        self._apply_editor_syntax_theme(editor)
        # Перерисовать открытый файл с новой темой кода
        if self.current_file and not self.is_edit_mode:
            viewer = self.query_one("#viewer", MarkdownViewer)
            viewer.update_content(self.file_system.read_file(self.current_file))

    def _register_markdown_highlights(self, editor: TextArea) -> None:
        """Кастомный highlight-запрос: код в блоках окрашивается как строки."""
        try:
            import textual as _tx
            from pathlib import Path
            from textual._tree_sitter import get_language

            query_path = (
                Path(_tx.__file__).parent / "tree-sitter" / "highlights" / "markdown.scm"
            )
            query = query_path.read_text(encoding="utf-8")
            query = query.replace(
                "(code_fence_content) @none",
                "(code_fence_content) @string",
            )
            # имя языка после ``` подсвечиваем как keyword
            query += "\n(fenced_code_block (info_string (language) @keyword))\n"
            editor.register_language("markdown", get_language("markdown"), query)
        except Exception:
            pass  # дефолтная подсветка останется

    def _update_tag_cloud(self):
        """Обновить облако тегов."""
        tag_cloud = self.query_one("#tag-cloud", TagCloud)
        tag_counts = {tag: len(files) for tag, files in self.tag_cache.items()}
        tag_cloud.update_tags(tag_counts, self.tag_colors)

    def _update_status(self):
        """Обновить статус бар."""
        status = self.query_one("#status-bar", Static)
        mode = _("EDIT") if self.is_edit_mode else _("VIEW")
        if self.current_file:
            if self.tag_index.is_favorite(str(self.current_file)):
                file_info = _("⭐ {name}", name=self.current_file.name)
            else:
                file_info = _("File: {name}", name=self.current_file.name)
        else:
            file_info = _("No file")
        status.update(_("{file} | Mode: {mode}", file=file_info, mode=mode))

    def on_file_tree_file_selected(self, event: FileTree.FileSelected):
        """Обработать выбор файла."""
        self.current_file = event.path
        self._load_file()

    def _load_file(self):
        """Загрузить текущий файл."""
        if not self.current_file:
            return

        content = self.file_system.read_file(self.current_file)
        viewer = self.query_one("#viewer", MarkdownViewer)
        editor = self.query_one("#editor", TextArea)
        form   = self.query_one("#form-view", FormView)

        if self.is_edit_mode:
            viewer.display = False
            editor.display = True
            form.display   = False
            self._original_content = content
            editor.load_text(content)
        else:
            form_def = parse_form_definition(content)
            if form_def is not None:
                viewer.display = False
                editor.display = False
                form.display   = True
                form.load_form(form_def["catalog"], form_def["fields"],
                               form_def["destination"])
                form.focus()
            else:
                viewer.display = True
                editor.display = False
                form.display   = False
                viewer.update_content(content)
                viewer.focus()

        self.title = f"Impactite — {self.current_file.name}"
        self._update_status()

    def action_toggle_edit(self):
        """Переключить режим редактирования."""
        if not self.current_file:
            return

        # При выходе из редактора — сохранить изменения
        if self.is_edit_mode:
            editor = self.query_one("#editor", TextArea)
            if editor.text != self._original_content:
                self.file_system.write_file(self.current_file, editor.text)
                self._rebuild_tag_cache()
                self._update_tag_cloud()

        self.is_edit_mode = not self.is_edit_mode
        # _load_file сам выберет режим: форма / просмотр / редактор
        self._load_file()
        if self.is_edit_mode:
            self.query_one("#editor", TextArea).focus()

    def action_save(self):
        """Сохранить файл."""
        if not self.current_file:
            return

        editor = self.query_one("#editor", TextArea)
        content = editor.text

        if self.file_system.write_file(self.current_file, content):
            self._original_content = content
            self.notify(_("File saved"), severity="information")
            self._rebuild_tag_cache()
            self._update_tag_cloud()
            if not self.is_edit_mode:
                viewer = self.query_one("#viewer", MarkdownViewer)
                viewer.update_content(content)
        else:
            self.notify(_("Save error"), severity="error")

    def action_exit_edit(self):
        """Выйти из режима редактирования по Escape."""
        if not self.is_edit_mode:
            return
        editor = self.query_one("#editor", TextArea)
        if editor.text != self._original_content:
            self.push_screen(UnsavedChangesModal())
        else:
            self._switch_to_view()

    def _switch_to_view(self):
        """Переключиться в режим просмотра (с учётом форм)."""
        self.is_edit_mode = False
        self._load_file()

    def on_unsaved_changes_modal_save(self, event: UnsavedChangesModal.Save):
        """Сохранить и выйти из редактора."""
        editor = self.query_one("#editor", TextArea)
        if self.current_file:
            if self.file_system.write_file(self.current_file, editor.text):
                self._original_content = editor.text
                self._rebuild_tag_cache()
                self._update_tag_cloud()
                self.notify(_("File saved"), severity="information")
            else:
                self.notify(_("Save error"), severity="error")
        self._switch_to_view()

    def on_unsaved_changes_modal_discard(self, _: UnsavedChangesModal.Discard):
        """Выйти без сохранения."""
        self._switch_to_view()

    def on_markdown_viewer_tag_clicked(self, event: MarkdownViewer.TagClicked) -> None:
        """Клик по тегу в тексте заметки — открыть поиск."""
        self.push_screen(TagSearchModal(self.tag_cache, initial_query=event.tag, tag_colors=self.tag_colors))

    def on_tag_cloud_tag_clicked(self, event: TagCloud.TagClicked) -> None:
        """Открыть поиск с предзаполненным тегом по клику в облаке тегов."""
        self.push_screen(TagSearchModal(self.tag_cache, initial_query=event.tag, tag_colors=self.tag_colors))

    def action_search_tags(self):
        """Открыть поиск по тегам."""
        self.push_screen(TagSearchModal(self.tag_cache, tag_colors=self.tag_colors))

    def on_tool_button_pressed(self, event: ToolButton.Pressed) -> None:
        """Кнопки в шапке боковой панели: создать каталог / заметку."""
        if event.button_id == "new-folder-btn":
            self._prompt_new_folder()
        elif event.button_id == "new-note-btn":
            self._prompt_new_note()
        elif event.button_id == "toggle-fav-btn":
            self.action_toggle_favorite()

    def _current_catalog(self) -> Path:
        """Каталог для создания (выбранный в дереве, иначе корень заметок)."""
        tree = self.query_one("#file-tree", FileTree)
        return tree.current_dir() or self.file_system.root_path

    def _prompt_new_folder(self) -> None:
        """Запросить имя и создать каталог в выбранной папке."""
        catalog = self._current_catalog()

        def done(name: Optional[str]) -> None:
            if not name:
                return
            target = catalog / name
            if self.file_system.create_directory(target):
                self._refresh_file_tree()
                self.notify(_("Folder created: {name}", name=name), severity="information")
            else:
                self.notify(_("Folder creation error"), severity="error")

        self.push_screen(TextPromptModal(_("New folder name"), _("folder name")), done)

    def _prompt_new_note(self) -> None:
        """Запросить имя, создать заметку в выбранной папке и открыть в редакторе."""
        catalog = self._current_catalog()

        def done(name: Optional[str]) -> None:
            if not name:
                return
            if not name.endswith(".md"):
                name += ".md"
            target = catalog / name
            created = False
            if not target.exists():
                if not self.file_system.write_file(target, f"# {target.stem}\n\n"):
                    self.notify(_("Note creation error"), severity="error")
                    return
                created = True
                self._rebuild_tag_cache()
                self._update_tag_cloud()
            self._refresh_file_tree()
            # Сразу открыть новую заметку в режиме редактирования
            self.current_file = target
            self.is_edit_mode = True
            self._load_file()
            self.query_one("#editor", TextArea).focus()
            if created:
                self.notify(_("Note created: {name}", name=target.name), severity="information")

        self.push_screen(TextPromptModal(_("New note name"), _("note name")), done)

    def action_refresh(self):
        """Обновить список файлов."""
        file_tree = self.query_one("#file-tree", FileTree)
        self._refresh_file_tree()
        self._rebuild_tag_cache()
        self._update_tag_cloud()
        self.notify(_("File list refreshed"), severity="information")

    def action_toggle_sidebar(self):
        """Показать/скрыть боковую панель."""
        sidebar = self.query_one("#sidebar")
        self.sidebar_visible = not self.sidebar_visible
        sidebar.display = self.sidebar_visible

    def on_form_view_saved(self, event: FormView.Saved) -> None:
        """Сохранить данные формы — в md-файл или в БД (по destination)."""
        if event.destination == "database":
            self._save_form_to_db(event)
        else:
            self._save_form_to_note(event)
        self._switch_to_view()

    def _save_form_to_db(self, event: FormView.Saved) -> None:
        """Сохранить запись формы в SQLite (та же БД, что и индекс тегов)."""
        values = {k: v for k, v in event.values.items() if v is not None}
        form_source = str(self.current_file) if self.current_file else ""
        try:
            rid = self.tag_index.save_form_record(form_source, event.catalog, values)
            self.notify(_("Record #{id} saved to database", id=rid), severity="information")
        except Exception as e:
            self.notify(_("Database write error: {error}", error=e), severity="error")

    def _save_form_to_note(self, event: FormView.Saved) -> None:
        """Сохранить данные формы как md-заметку с frontmatter."""
        from datetime import datetime
        import yaml as _yaml

        root = self.file_system.root_path
        catalog_path = (root / event.catalog) if event.catalog else root
        catalog_path.mkdir(parents=True, exist_ok=True)

        values = event.values

        # Имя файла — из первого непустого строкового поля или метка времени
        filename: str | None = None
        for v in values.values():
            if isinstance(v, str) and v.strip():
                clean = re.sub(r"[^\wЀ-ӿ\-_ ]", "", v)[:50].strip().replace(" ", "_")
                if clean:
                    filename = clean + ".md"
                    break
        if not filename:
            filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".md"

        filepath = catalog_path / filename
        fm_str = _yaml.dump(
            {k: v for k, v in values.items() if v is not None},
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
        file_content = f"---\n{fm_str}---\n"

        if self.file_system.write_file(filepath, file_content):
            self._rebuild_tag_cache()
            self._update_tag_cloud()
            self._refresh_file_tree()
            self.notify(_("Saved: {name}", name=filepath.name), severity="information")
        else:
            self.notify(_("Save error"), severity="error")

    def on_form_view_cancelled(self, _: FormView.Cancelled) -> None:
        """Отмена ввода — вернуться в режим просмотра."""
        self._switch_to_view()

    def on_tag_search_modal_file_selected(self, event: TagSearchModal.FileSelected):
        """Обработать выбор файла из поиска."""
        self.current_file = event.path
        self._load_file()

    def on_unmount(self) -> None:
        self.tag_index.close()


def main():
    """Точка входа приложения."""
    import sys

    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    config = Config.load(config_path)

    app = MarkdownEditorApp(config)
    app.run()


if __name__ == "__main__":
    main()
