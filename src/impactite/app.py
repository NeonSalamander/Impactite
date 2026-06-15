"""
Основное приложение Markdown Viewer/Editor.
Консольный аналог Obsidian с использованием Textual и Rich.
"""

import re
from io import StringIO
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple

from rich.console import Console
from rich.markup import escape
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical, VerticalScroll
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
    Config, FileNode, FileSystem, FullTextIndex, MarkdownParser, Match, QueryEngine, SearchState, TagIndex,
    find_matches, parse_form_definition, parse_base_definition,
)
from impactite.i18n import _, retranslate_bindings, set_language
from impactite.templater import collect_templates, build_context, render_template
from impactite.table_engine import process_table_with_formulas

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


class EditorTextArea(TextArea):
    """Редактор с явной подсветкой текущего поискового совпадения."""

    DEFAULT_CSS = """
    EditorTextArea .text-area--selection {
        background: #ffcc00 !important;
        color: #000000 !important;
        text-style: bold !important;
    }

    EditorTextArea .text-area--cursor-line {
        background: $primary 30%;
    }
    """


class FileTree(Tree):
    """Дерево файлов."""

    class FileSelected(Message):
        """Сообщение о выборе файла."""

        def __init__(self, path: Path):
            self.path = path
            super().__init__()

    class GraphSelected(Message):
        """Сообщение о выборе графа связей."""

        pass

    def __init__(self, root_label: str, **kwargs):
        super().__init__(root_label, **kwargs)
        self.show_root = False
        self.file_nodes: Dict[int, Path] = {}
        self.dir_nodes: Dict[int, Path] = {}
        self.root_path: Optional[Path] = None
        # Текущий выбранный каталог (для создания заметок/папок)
        self.selected_dir: Optional[Path] = None
        self.graph_node_id: Optional[int] = None

    def populate_tree(self, file_system: FileSystem, favorites: Optional[List[str]] = None):
        """Заполнить дерево файлами."""
        self.clear()
        self.file_nodes.clear()
        self.dir_nodes.clear()
        self.graph_node_id = None
        self.root_path = file_system.root_path
        self.root.expand()

        # Граф связей — предопределённый узел
        graph_node = self.root.add(_("🕸️ Link graph"), expand=False)
        self.graph_node_id = id(graph_node)

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
        if node_id == self.graph_node_id:
            self.post_message(self.GraphSelected())
        elif node_id in self.file_nodes:
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

    can_focus = False
    FOCUS_ON_CLICK = False

    class Pressed(Message):
        def __init__(self, button_id: str) -> None:
            self.button_id = button_id
            super().__init__()

    def on_click(self, event) -> None:
        event.stop()
        self.post_message(self.Pressed(self.id or ""))


class EditorToolbar(Horizontal):
    """Панель инструментов форматирования над редактором."""

    can_focus = False
    can_focus_children = False

    class Action(Message):
        def __init__(self, action: str, selection=None) -> None:
            self.action = action
            self.selection = selection
            super().__init__()

    def compose(self) -> ComposeResult:
        buttons = [
            ("B", "bold"),
            ("I", "italic"),
            ("S", "strikethrough"),
            ("H1", "h1"),
            ("H2", "h2"),
            ("H3", "h3"),
            ("[L]", "link"),
            ("-", "bullet"),
            ("1.", "numbered"),
            ("[ ]", "checkbox"),
            (">", "quote"),
            ("```", "code"),
            ("—", "hr"),
        ]
        for label, action in buttons:
            btn = ToolButton(label, id=f"toolbar-{action}", classes="toolbar-btn")
            btn.tooltip = action
            yield btn

    def on_tool_button_pressed(self, event: ToolButton.Pressed) -> None:
        action = event.button_id.replace("toolbar-", "")
        saved_selection = None
        try:
            editor = self.screen.query_one("#editor", TextArea)
            saved_selection = editor.selection
        except Exception:
            pass
        self.post_message(self.Action(action, saved_selection))


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

    class CheckboxToggled(Message):
        def __init__(self, source_line: int) -> None:
            self.source_line = source_line
            super().__init__()

    class LinkClicked(Message):
        def __init__(self, target: str, text: str) -> None:
            self.target = target
            self.text = text
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._content = ""
        # Каждый элемент соответствует одной визуальной строке:
        # None — строка без тегов, (tags, plain_text) — строка с тегами
        self._tag_lines: list = []
        # Информация о чекбоксах: None или dict с позицией
        self._checkbox_lines: list = []
        # Информация о внутренних ссылках: None или список dict'ов
        self._link_lines: list = []

    def compose(self):
        yield ViewerLog(markup=True, highlight=False, wrap=True)

    def action_scroll_up(self)   -> None: self.query_one(ViewerLog).scroll_up()
    def action_scroll_down(self) -> None: self.query_one(ViewerLog).scroll_down()
    def action_page_up(self)     -> None: self.query_one(ViewerLog).scroll_page_up()
    def action_page_down(self)   -> None: self.query_one(ViewerLog).scroll_page_down()
    def action_scroll_home(self) -> None: self.query_one(ViewerLog).scroll_home()
    def action_scroll_end(self)  -> None: self.query_one(ViewerLog).scroll_end()

    def on_viewer_log_clicked(self, event: ViewerLog.Clicked) -> None:
        """Обработать клик по тексту заметки — ссылка, чекбокс или тег."""
        log = self.query_one(ViewerLog)
        cr = log.content_region          # абсолютные экранные координаты контента
        line_idx = event.screen_y - cr.y + int(log.scroll_y)
        if not (0 <= line_idx < len(self._tag_lines)):
            return
        col = event.screen_x - cr.x

        # Внутренняя ссылка?
        if line_idx < len(self._link_lines):
            link_data = self._link_lines[line_idx]
            if link_data:
                for link in link_data:
                    if link["start"] <= col <= link["end"]:
                        self.post_message(self.LinkClicked(link["target"], link["text"]))
                        return

        # Чекбокс?
        if line_idx < len(self._checkbox_lines):
            cb_info = self._checkbox_lines[line_idx]
            if cb_info:
                if cb_info["cb_start"] <= col <= cb_info["cb_end"]:
                    self.post_message(self.CheckboxToggled(cb_info["source_line"]))
                    return

        entry = self._tag_lines[line_idx]
        if not entry:
            return
        tags, plain = entry
        tag = self._tag_at_col(plain, tags, col) or tags[0]
        self.post_message(self.TagClicked(tag))

    @staticmethod
    def _tag_at_col(line: str, tags: list, col: int):
        """Определить тег по горизонтальной позиции клика."""
        for tag in tags:
            idx = line.find(f"#{tag}")
            if idx != -1 and idx <= col < idx + len(tag) + 1:
                return tag
        return None

    def update_content(
        self,
        content: str,
        search_terms: Optional[List[str]] = None,
        current_match_index: int = 0,
    ):
        """Обновить содержимое.

        Параметры поиска используются для подсветки найденных лексем.
        """
        self._content = content
        self._search_terms = search_terms or []
        self._current_match_index = current_match_index
        self._line_highlights: Dict[int, List[Tuple[int, int, bool]]] = {}
        self._tag_lines = []
        self._checkbox_lines = []
        self._link_lines = []
        log = self.query_one(ViewerLog)
        log.clear()

        if not content:
            log.write(f"[italic]{_('Select a file to view')}[/italic]")
            self._tag_lines.append(None)
            self._checkbox_lines.append(None)
            self._link_lines.append(None)
            return

        lines = content.split("\n")
        self._line_highlights = self._find_highlights(lines, self._search_terms, current_match_index)
        self._current_match_line: Optional[int] = None
        for lnum, hls in self._line_highlights.items():
            if any(is_current for _, _, is_current in hls):
                self._current_match_line = lnum
                break
        in_code_block = False
        code_lines = []
        code_language = ""
        skip_until = -1

        for line_idx, line in enumerate(lines):
            if line_idx <= skip_until:
                continue

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
                        self._checkbox_lines.append(None)
                        self._link_lines.append(None)
                    in_code_block = False
                continue

            if in_code_block:
                code_lines.append(line)
                continue

            # Таблицы Markdown с формулами
            if line.strip().startswith("|"):
                table, next_idx = process_table_with_formulas(lines, line_idx)
                if table:
                    self._render_table(log, table, lines, line_idx)
                    vis_height = len(table.rows) + 2
                    for _ in range(vis_height):
                        self._tag_lines.append(None)
                        self._checkbox_lines.append(None)
                        self._link_lines.append(None)
                    skip_until = next_idx - 1
                    continue

            # Чекбоксы
            cb_match = re.match(r'^(\s*)([-*])\s+\[([ xX])\]\s+(.*)', line)
            if cb_match:
                indent_str, _bullet, checked, text = cb_match.groups()
                is_checked = checked.lower() == 'x'
                prefix_spaces = " " * len(indent_str)
                checkbox_display = f"[bold green]{escape('[x]')}[/bold green]" if is_checked else f"[bold red]{escape('[ ]')}[/bold red]"
                pre_len = len(indent_str) + 3 + 1  # indent + [x]/[ ] + space
                formatted_text, links = self._process_formatting_inline(self._apply_highlights_range(text, line_idx, pre_len))
                log.write(f"{prefix_spaces}{checkbox_display} {formatted_text}")
                cb_start = len(prefix_spaces)
                cb_end = cb_start + 3
                offset = len(prefix_spaces) + 4
                link_data = [{"start": l["start"] + offset, "end": l["end"] + offset,
                              "target": l["target"], "text": l["text"]} for l in links] if links else None
                self._checkbox_lines.append({
                    "source_line": line_idx,
                    "cb_start": cb_start,
                    "cb_end": cb_end,
                })
                self._tag_lines.append(None)
                self._link_lines.append(link_data)
                continue

            # Заголовки
            if line.startswith("# "):
                log.write(f"[bold magenta]{self._apply_highlights_range(line[2:], line_idx, 2)}[/bold magenta]")
                self._tag_lines.append(None)
                self._checkbox_lines.append(None)
                self._link_lines.append(None)
            elif line.startswith("## "):
                log.write(f"[bold blue]{self._apply_highlights_range(line[3:], line_idx, 3)}[/bold blue]")
                self._tag_lines.append(None)
                self._checkbox_lines.append(None)
                self._link_lines.append(None)
            elif line.startswith("### "):
                log.write(f"[bold green]{self._apply_highlights_range(line[4:], line_idx, 4)}[/bold green]")
                self._tag_lines.append(None)
                self._checkbox_lines.append(None)
                self._link_lines.append(None)
            # Списки
            elif line.startswith("- ") or line.startswith("* "):
                text, links = self._process_formatting_inline(self._apply_highlights_range(line[2:], line_idx, 2))
                log.write(f"  • {text}")
                offset = 4
                link_data = [{"start": l["start"] + offset, "end": l["end"] + offset,
                              "target": l["target"], "text": l["text"]} for l in links] if links else None
                self._tag_lines.append(None)
                self._checkbox_lines.append(None)
                self._link_lines.append(link_data)
            elif re.match(r"^\d+\. ", line):
                match = re.match(r"^(\d+)\. (.*)", line)
                if match:
                    num = match.group(1)
                    prefix_len = len(num) + 2  # "N. "
                    text, links = self._process_formatting_inline(self._apply_highlights_range(match.group(2), line_idx, prefix_len))
                    log.write(f"  {num}. {text}")
                    offset = len(f"  {num}. ")
                    link_data = [{"start": l["start"] + offset, "end": l["end"] + offset,
                                  "target": l["target"], "text": l["text"]} for l in links] if links else None
                    self._tag_lines.append(None)
                    self._checkbox_lines.append(None)
                    self._link_lines.append(link_data)
            # Цитаты
            elif line.startswith("> "):
                text, links = self._process_formatting_inline(self._apply_highlights_range(line[2:], line_idx, 2))
                log.write(f"[italic yellow]  {text}[/italic yellow]")
                offset = 2
                link_data = [{"start": l["start"] + offset, "end": l["end"] + offset,
                              "target": l["target"], "text": l["text"]} for l in links] if links else None
                self._tag_lines.append(None)
                self._checkbox_lines.append(None)
                self._link_lines.append(link_data)
            # Теги
            elif re.search(r"#\w+", line):
                try:
                    tag_colors = self.app.tag_colors
                except Exception:
                    tag_colors = {}
                tags_in_line = re.findall(r"#(\w+)", line)
                parts = re.split(r"(#\w+)", line)
                formatted = ""
                offset = 0
                for part in parts:
                    if re.match(r"#\w+", part):
                        color = tag_colors.get(part[1:], "")
                        highlighted_part = self._apply_highlights_range(part, line_idx, offset)
                        if color:
                            formatted += f"[bold {color}]{highlighted_part}[/bold {color}]"
                        else:
                            formatted += f"[bold cyan]{highlighted_part}[/bold cyan]"
                    else:
                        formatted += self._apply_highlights_range(part, line_idx, offset)
                    offset += len(part)
                log.write(formatted)
                self._tag_lines.append((tags_in_line, line))
                self._checkbox_lines.append(None)
                self._link_lines.append(None)
            # Inline-форматирование
            elif any(m in line for m in ("**", "__", "~~", "*", "_[", "](")):
                formatted, links = self._process_formatting_inline(self._apply_highlights_range(line, line_idx, 0))
                log.write(formatted)
                link_data = [{"start": l["start"], "end": l["end"],
                              "target": l["target"], "text": l["text"]} for l in links] if links else None
                self._tag_lines.append(None)
                self._checkbox_lines.append(None)
                self._link_lines.append(link_data)
            # Пустые строки
            elif not line.strip():
                log.write("")
                self._tag_lines.append(None)
                self._checkbox_lines.append(None)
                self._link_lines.append(None)
            # Обычный текст
            else:
                log.write(self._apply_highlights_range(line, line_idx, 0))
                self._tag_lines.append(None)
                self._checkbox_lines.append(None)
                self._link_lines.append(None)

        if self._current_match_line is not None:
            try:
                log.scroll_to(0, max(0, self._current_match_line - 2))
            except Exception:
                pass

    def _render_table(self, log, table, lines, start_idx) -> None:
        """Отрендерить MarkdownTable в RichLog через rich.table.Table."""
        from rich.markup import escape as rich_escape
        from rich.text import Text

        def _cell_offset(line: str, cell_index: int, value: str) -> int:
            parts = line.split("|")
            if cell_index + 1 >= len(parts):
                return 0
            raw = parts[cell_index + 1]
            leading = len(raw) - len(raw.lstrip())
            pos = line.find(raw)
            return max(pos + leading, 0)

        def _source_indices() -> List[int]:
            indices: List[int] = []
            i = start_idx
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells_raw = [c.strip() for c in lines[i].strip()[1:].split("|")]
                while cells_raw and cells_raw[-1] == "":
                    cells_raw = cells_raw[:-1]
                if not (
                    all(re.match(r"^\s*:?-+:?\s*$", c) for c in cells_raw if c.strip() != "")
                    and any(c.strip() for c in cells_raw)
                ):
                    indices.append(i)
                i += 1
            return indices

        rich_table = Table(
            show_header=table.has_header,
            expand=False,
            border_style="dim",
            pad_edge=False,
        )
        num_cols = table.num_cols
        src_indices = _source_indices()

        # Заголовок
        header_row = table.rows[0] if table.has_header and table.rows else None
        for c in range(num_cols):
            header = header_row[c].value if header_row and c < len(header_row) else ""
            offset = 0
            if header_row is not None and src_indices:
                header_line = lines[src_indices[0]]
                offset = _cell_offset(header_line, c, header)
            highlighted_header = self._apply_highlights_range(rich_escape(header), src_indices[0] if src_indices else 0, offset)
            rich_table.add_column(Text.from_markup(highlighted_header))

        start = 1 if table.has_header else 0
        for r_idx in range(start, len(table.rows)):
            row = table.rows[r_idx]
            source_idx = src_indices[r_idx] if r_idx < len(src_indices) else 0
            cells = []
            for c_idx, cell in enumerate(row):
                offset = 0
                if source_idx < len(lines):
                    offset = _cell_offset(lines[source_idx], c_idx, cell.value)
                display_value = rich_escape(cell.value)
                highlighted = self._apply_highlights_range(display_value, source_idx, offset)
                if cell.computed:
                    cells.append(Text.from_markup(highlighted, style="italic cyan"))
                else:
                    cells.append(Text.from_markup(highlighted))
            while len(cells) < num_cols:
                cells.append("")
            rich_table.add_row(*cells)

        log.write(rich_table)

    def _process_formatting_inline(self, line: str) -> tuple[str, list]:
        """Обработать inline-форматирование markdown.

        Возвращает (отформатированная строка, список внутренних ссылок).
        Каждая ссылка: dict(start, end, target, text) — позиции в отформатированной строке.
        """
        links: list = []
        parts: list = []
        last_end = 0
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
            text = match.group(1)
            url = match.group(2)
            parts.append(line[last_end:match.start()])
            if re.match(r'^(https?://|mailto:)', url):
                link_markup = f'[link={url}]{text}[/link]'
            else:
                start_pos = sum(len(p) for p in parts)
                links.append({
                    "start": start_pos,
                    "end": start_pos + len(text) - 1,
                    "target": url,
                    "text": text,
                })
                link_markup = f'[underline blue]{text}[/underline blue]'
            parts.append(link_markup)
            last_end = match.end()
        parts.append(line[last_end:])
        line = ''.join(parts)

        # **жирный**
        line = re.sub(r"\*\*(.+?)\*\*", r"[bold]\1[/bold]", line)
        # __жирный__
        line = re.sub(r"__(.+?)__", r"[bold]\1[/bold]", line)
        # ~~зачёркнутый~~
        line = re.sub(r"~~(.+?)~~", r"[strike]\1[/strike]", line)
        # *курсив*
        line = re.sub(r"\*(.+?)\*", r"[italic]\1[/italic]", line)
        # _курсив_
        line = re.sub(r"_(.+?)_", r"[italic]\1[/italic]", line)
        return line, links

    def _find_highlights(
        self,
        lines: List[str],
        terms: List[str],
        current_idx: int,
    ) -> Dict[int, List[Tuple[int, int, bool]]]:
        """Найти позиции терминов для каждой строки и отметить текущее совпадение."""
        if not terms:
            return {}
        # Сначала длинные термины, чтобы частичные совпадения не блокировали длинные
        escaped = [re.escape(t) for t in sorted(terms, key=len, reverse=True)]
        pattern = re.compile("|".join(escaped), re.IGNORECASE)
        highlights: Dict[int, List[Tuple[int, int, bool]]] = {}
        idx = 0
        for lnum, line in enumerate(lines):
            hl = []
            for match in pattern.finditer(line):
                hl.append((match.start(), match.end(), idx == current_idx))
                idx += 1
            if hl:
                highlights[lnum] = hl
        return highlights

    def _apply_highlights_range(
        self, text: str, line_idx: int, offset: int
    ) -> str:
        """Подсветить только часть строки, начинающуюся с offset."""
        hl_all = sorted(self._line_highlights.get(line_idx, []))
        if not hl_all:
            return text
        parts = []
        pos = 0
        text_end = offset + len(text)
        for start, end, is_current in hl_all:
            if end <= offset:
                continue
            if start >= text_end:
                break
            s = max(start, offset) - offset
            e = min(end, text_end) - offset
            parts.append(text[pos:s])
            style = "bold #ffffff on #ff3333" if is_current else "bold #000000 on #ffcc00"
            parts.append(f"[{style}]{text[s:e]}[/{style}]")
            pos = e
        parts.append(text[pos:])
        return "".join(parts)

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


class BaseView(VerticalScroll):
    """Отображает заметку типа 'base' как компактные фильтры + таблица результатов query."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._query: str = ""
        self._filter_defs: list = []
        self._columns: list = []
        self._all_rows: list = []
        self._apply_generation: int = 0
        self._multi_select_values: dict[str, set] = {}
        self._multi_select_modes: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        yield Horizontal(id="base-filters")
        yield RichLog(id="base-results", markup=True, highlight=False, wrap=False)

    def load_base(self, query: str, filter_defs: list) -> None:
        """Загрузить query и определения фильтров."""
        self._query = query
        self._filter_defs = filter_defs
        self.run_worker(self._rebuild_filters(), exclusive=True)

    async def _rebuild_filters(self) -> None:
        """Пересобрать виджеты фильтров."""
        container = self.query_one("#base-filters", Horizontal)
        await container.remove_children()
        self._multi_select_values.clear()
        self._multi_select_modes.clear()
        widgets = self._build_filter_widgets()
        if widgets:
            await container.mount(*widgets)
        self._apply_filters()

    def _build_filter_widgets(self) -> list:
        """Построить компактные виджеты фильтров в ряд."""
        widgets: list = []
        app = self.app
        known_tags = sorted(getattr(app, "tag_cache", {}).keys()) if app else []

        for fd in self._filter_defs:
            if not isinstance(fd, dict):
                continue
            for name, info in fd.items():
                if not isinstance(info, list) or len(info) < 1:
                    continue
                ftype = str(info[0]).lower()
                widget = self._make_filter_widget(name, ftype, info, known_tags)
                reset_btn = Static(
                    "x",
                    id=f"base-filter-reset-{name}",
                    classes="base-filter-reset",
                )
                mode_btn = Static(
                    self._multi_select_modes.get(name, "OR"),
                    id=f"base-filter-mode-{name}",
                    classes="base-filter-mode",
                )
                if isinstance(widget, list):
                    if any(isinstance(w, Static) for w in widget):
                        non_static = [w for w in widget if not isinstance(w, Static)]
                        static_widgets = [w for w in widget if isinstance(w, Static)]
                        item = Vertical(
                            Horizontal(
                                Label(f"[bold]{name}:[/bold]", classes="base-filter-label"),
                                *non_static,
                                mode_btn,
                                reset_btn,
                                classes="base-filter-row",
                            ),
                            *static_widgets,
                            classes="base-filter-item base-filter-multiselect-item",
                        )
                    else:
                        item = Horizontal(
                            Label(f"[bold]{name}:[/bold]", classes="base-filter-label"),
                            *widget,
                            reset_btn,
                            classes="base-filter-item",
                        )
                else:
                    item = Horizontal(
                        Label(f"[bold]{name}:[/bold]", classes="base-filter-label"),
                        widget,
                        reset_btn,
                        classes="base-filter-item",
                    )
                widgets.append(item)
        return widgets

    def _make_filter_widget(self, name: str, ftype: str, info: list, known_tags: list):
        """Создать компактный виджет для одного фильтра."""
        wid = f"base-filter-{name}"
        if ftype == "string":
            return Input(placeholder=_("contains..."), id=wid,
                         classes="base-filter-widget base-filter-string")
        if ftype == "multi-select":
            options = info[1] if len(info) > 1 else []
            opts: list = []
            if options == "tags":
                opts = known_tags
            elif isinstance(options, list):
                opts = [str(o) for o in options]
            if opts:
                return [
                    Select(
                        [(o, o) for o in opts],
                        allow_blank=True,
                        prompt=name,
                        compact=True,
                        id=wid, classes="base-filter-widget base-filter-select",
                    ),
                    Static("", id=f"{wid}-display", classes="base-filter-display"),
                ]
            return Input(placeholder=_("contains..."), id=wid,
                         classes="base-filter-widget base-filter-string")
        if ftype == "integer":
            return [
                Input(placeholder=_("min"), type="integer",
                      id=f"{wid}-min", classes="base-filter-number"),
                Input(placeholder=_("max"), type="integer",
                      id=f"{wid}-max", classes="base-filter-number"),
            ]
        if ftype == "date":
            return [
                Input(placeholder=_("from"),
                      id=f"{wid}-from", classes="base-filter-date"),
                Input(placeholder=_("to"),
                      id=f"{wid}-to", classes="base-filter-date"),
            ]
        # fallback
        return Input(placeholder=_("contains..."), id=wid,
                     classes="base-filter-widget base-filter-string")

    def _collect_filter_values(self) -> dict:
        """Собрать текущие значения фильтров."""
        values: dict = {}
        for fd in self._filter_defs:
            if not isinstance(fd, dict):
                continue
            for name, info in fd.items():
                if not isinstance(info, list) or len(info) < 1:
                    continue
                ftype = str(info[0]).lower()
                try:
                    if ftype == "string":
                        v = self.query_one(f"#base-filter-{name}", Input).value.strip()
                        values[name] = v if v else None
                    elif ftype == "multi-select":
                        selected = sorted(self._multi_select_values.get(name, []))
                        values[name] = selected if selected else None
                        values[f"__mode_{name}"] = self._multi_select_modes.get(name, "OR")
                    elif ftype == "integer":
                        min_val = None
                        max_val = None
                        min_raw = self.query_one(f"#base-filter-{name}-min", Input).value.strip()
                        if min_raw:
                            min_val = int(min_raw)
                        max_raw = self.query_one(f"#base-filter-{name}-max", Input).value.strip()
                        if max_raw:
                            max_val = int(max_raw)
                        values[name] = (min_val, max_val) if (min_val is not None or max_val is not None) else None
                    elif ftype == "date":
                        from_val = None
                        to_val = None
                        from_raw = self.query_one(f"#base-filter-{name}-from", Input).value.strip()
                        if from_raw:
                            from_val = from_raw
                        to_raw = self.query_one(f"#base-filter-{name}-to", Input).value.strip()
                        if to_raw:
                            to_val = to_raw
                        values[name] = (from_val, to_val) if (from_val is not None or to_val is not None) else None
                    else:
                        values[name] = None
                except Exception:
                    values[name] = None
        return values

    def _apply_filters(self) -> None:
        """Выполнить query и применить фильтры."""
        engine = getattr(self.app, "query_engine", None)
        log = self.query_one("#base-results", RichLog)
        log.clear()

        if not self._query:
            log.write(f"[italic dim]{_('Query returned no data')}[/italic dim]")
            return

        if engine is None:
            log.write(f"[red]{_('Query engine unavailable')}[/red]")
            return

        try:
            columns, rows = engine.execute(self._query)
        except Exception as e:
            log.write(f"[red]{_('Query error: {error}', error=e)}[/red]")
            return

        self._columns = columns
        self._all_rows = rows
        filter_values = self._collect_filter_values()
        filtered = [r for r in rows if self._row_matches(r, filter_values)]
        self._render_results(filtered)

    def _row_matches(self, row: dict, filter_values: dict) -> bool:
        """Проверить, проходит ли строка через фильтры."""
        for name, val in filter_values.items():
            if val is None:
                continue
            if isinstance(name, str) and name.startswith("__mode_"):
                continue
            actual = row.get(name)
            if isinstance(val, str):
                if str(val).lower() not in str(actual).lower():
                    return False
            elif isinstance(val, list):
                if not val:
                    continue
                mode = filter_values.get(f"__mode_{name}", "OR")
                if mode == "AND":
                    for v in val:
                        v_matched = False
                        if isinstance(actual, (list, tuple, set)):
                            if v in actual or str(v) in [str(x) for x in actual]:
                                v_matched = True
                        else:
                            if str(v).lower() in str(actual).lower():
                                v_matched = True
                        if not v_matched:
                            return False
                else:
                    matched = False
                    for v in val:
                        if isinstance(actual, (list, tuple, set)):
                            if v in actual or str(v) in [str(x) for x in actual]:
                                matched = True
                                break
                        else:
                            if str(v).lower() in str(actual).lower():
                                matched = True
                                break
                    if not matched:
                        return False
            elif isinstance(val, tuple) and len(val) == 2:
                min_val, max_val = val
                try:
                    actual_cmp = float(actual) if actual is not None else None
                except (ValueError, TypeError):
                    actual_cmp = None
                if actual_cmp is None:
                    return False
                if min_val is not None and actual_cmp < min_val:
                    return False
                if max_val is not None and actual_cmp > max_val:
                    return False
        return True

    def _render_results(self, rows: list) -> None:
        """Отрисовать таблицу результатов."""
        log = self.query_one("#base-results", RichLog)
        log.clear()

        if not self._columns:
            log.write(f"[italic dim]{_('Query returned no data')}[/italic dim]")
            return

        table = Table(expand=False, header_style="bold magenta", border_style="dim")
        for col in self._columns:
            table.add_column(str(col))
        for row in rows:
            table.add_row(*[str(row.get(c, "")) for c in self._columns])
        log.write(table)
        if not rows:
            log.write(f"[italic dim]{_('0 records')}[/italic dim]")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id and event.input.id.startswith("base-filter-"):
            self._schedule_apply()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id and event.select.id.startswith("base-filter-"):
            name = event.select.id[len("base-filter-"):]
            for fd in self._filter_defs:
                if not isinstance(fd, dict):
                    continue
                if name not in fd:
                    continue
                info = fd[name]
                if isinstance(info, list) and len(info) >= 1 and str(info[0]).lower() == "multi-select":
                    self._add_multi_select(name, event.select.value)
                    event.select.value = Select.NULL
                    break
            self._schedule_apply()

    def _add_multi_select(self, name: str, value) -> None:
        """Добавить или убрать значение из набора multi-select фильтра."""
        if value is None or isinstance(value, NoSelection) or value == Select.NULL:
            return
        if name not in self._multi_select_values:
            self._multi_select_values[name] = set()
        str_val = str(value)
        if str_val in self._multi_select_values[name]:
            self._multi_select_values[name].remove(str_val)
        else:
            self._multi_select_values[name].add(str_val)
        self._update_multi_select_display(name)
        self._refresh_select_options(name)

    def _update_multi_select_display(self, name: str) -> None:
        """Обновить текстовое отображение выбранных значений."""
        try:
            display = self.query_one(f"#base-filter-{name}-display", Static)
            selected = sorted(self._multi_select_values.get(name, []))
            display.update(Text(", ".join(selected), style="yellow") if selected else "")
        except Exception:
            pass

    def _refresh_select_options(self, name: str) -> None:
        """Обновить цвета опций Select: выбранные — жёлтые."""
        try:
            sel = self.query_one(f"#base-filter-{name}", Select)
            selected = self._multi_select_values.get(name, set())
            new_options = []
            for opt in sel.options:
                label, val = opt
                if str(val) in selected:
                    new_options.append((Text(str(label), style="yellow"), val))
                else:
                    new_options.append((str(label), val))
            sel.set_options(new_options)
        except Exception:
            pass

    def _toggle_multi_select_mode(self, name: str) -> None:
        """Переключить режим фильтрации multi-select между OR и AND."""
        current = self._multi_select_modes.get(name, "OR")
        new_mode = "AND" if current == "OR" else "OR"
        self._multi_select_modes[name] = new_mode
        try:
            btn = self.query_one(f"#base-filter-mode-{name}", Static)
            btn.update(new_mode)
        except Exception:
            pass
        self._apply_filters()

    def _schedule_apply(self) -> None:
        """Отложить применение фильтров на 200 мс (debounce)."""
        self._apply_generation += 1
        gen = self._apply_generation

        def callback():
            if gen == self._apply_generation:
                self._apply_filters()

        self.set_timer(0.2, callback)

    def on_click(self, event: events.Click) -> None:
        widget = event.control
        if widget and widget.id:
            if widget.id.startswith("base-filter-reset-"):
                name = widget.id[len("base-filter-reset-"):]
                self._reset_filter(name)
            elif widget.id.startswith("base-filter-mode-"):
                name = widget.id[len("base-filter-mode-"):]
                self._toggle_multi_select_mode(name)

    def _reset_filter(self, name: str) -> None:
        for fd in self._filter_defs:
            if not isinstance(fd, dict):
                continue
            if name not in fd:
                continue
            info = fd[name]
            if not isinstance(info, list) or len(info) < 1:
                continue
            ftype = str(info[0]).lower()
            try:
                if ftype == "string":
                    self.query_one(f"#base-filter-{name}", Input).value = ""
                elif ftype == "multi-select":
                    self._multi_select_values.pop(name, None)
                    try:
                        display = self.query_one(f"#base-filter-{name}-display", Static)
                        display.update("")
                    except Exception:
                        pass
                    try:
                        sel = self.query_one(f"#base-filter-{name}", Select)
                        sel.value = Select.NULL
                        self._refresh_select_options(name)
                    except Exception:
                        pass
                elif ftype == "integer":
                    self.query_one(f"#base-filter-{name}-min", Input).value = ""
                    self.query_one(f"#base-filter-{name}-max", Input).value = ""
                elif ftype == "date":
                    self.query_one(f"#base-filter-{name}-from", Input).value = ""
                    self.query_one(f"#base-filter-{name}-to", Input).value = ""
                else:
                    self.query_one(f"#base-filter-{name}", Input).value = ""
            except Exception:
                pass
            break
        self._apply_filters()


class LinkGraphTree(Tree):
    """Дерево иерархических связей заметок и тегов."""

    class NoteSelected(Message):
        def __init__(self, path: Path) -> None:
            self.path = path
            super().__init__()

    class TagSelected(Message):
        def __init__(self, tag: str) -> None:
            self.tag = tag
            super().__init__()

    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self.show_root = False
        self._tag_cache: Dict[str, List[Path]] = {}
        self._tag_colors: Dict[str, str] = {}
        self._note_links: Dict[Path, Set[Path]] = {}
        self._all_md_files: Set[Path] = set()

    def build_graph(
        self,
        tag_cache: Dict[str, List[Path]],
        tag_colors: Dict[str, str],
        note_links: Dict[Path, Set[Path]],
        all_md_files: List[Path],
    ) -> None:
        """Построить иерархическое дерево связей."""
        self.clear()
        self._tag_cache = tag_cache
        self._tag_colors = tag_colors
        self._note_links = note_links
        self._all_md_files = set(all_md_files)

        if not tag_cache and not note_links:
            self.root.add(_("No data for graph"))
            return

        # Собираем обратные связи: кто ссылается на заметку
        back_links: Dict[Path, Set[Path]] = {}
        for src, targets in note_links.items():
            for t in targets:
                back_links.setdefault(t, set()).add(src)

        # Тег -> заметки
        tag_to_notes: Dict[str, Set[Path]] = {}
        for tag, files in tag_cache.items():
            tag_to_notes.setdefault(tag, set()).update(files)

        # Заметка -> теги
        note_to_tags: Dict[Path, Set[str]] = {}
        for tag, files in tag_cache.items():
            for f in files:
                note_to_tags.setdefault(f, set()).add(tag)

        visited_notes: Set[Path] = set()
        visited_tags: Set[str] = set()

        def add_note(parent, note: Path, depth: int = 0):
            if note in visited_notes or depth > 10:
                return
            visited_notes.add(note)
            label = f"📄 {note.name}"
            node = parent.add(label, expand=True, data={"type": "note", "value": note})
            # Теги заметки
            for tag in sorted(note_to_tags.get(note, [])):
                if tag not in visited_tags:
                    color = self._tag_colors.get(tag, "cyan")
                    tag_node = node.add(
                        f"[bold {color}]#{tag}[/bold {color}]",
                        expand=True,
                        data={"type": "tag", "value": tag},
                    )
                    visited_tags.add(tag)
                    # Другие заметки с этим тегом
                    for other in sorted(tag_to_notes.get(tag, set())):
                        if other != note and other not in visited_notes:
                            add_note(tag_node, other, depth + 1)
            # Прямые ссылки из заметки
            for target in sorted(self._note_links.get(note, set())):
                if target not in visited_notes:
                    add_note(node, target, depth + 1)
            # Обратные ссылки
            for src in sorted(back_links.get(note, set())):
                if src not in visited_notes:
                    add_note(node, src, depth + 1)

        # Начинаем с тегов верхнего уровня
        for tag in sorted(tag_cache.keys()):
            if tag not in visited_tags:
                color = self._tag_colors.get(tag, "cyan")
                tag_node = self.root.add(
                    f"[bold {color}]#{tag}[/bold {color}]",
                    expand=True,
                    data={"type": "tag", "value": tag},
                )
                visited_tags.add(tag)
                for note in sorted(tag_to_notes.get(tag, set())):
                    add_note(tag_node, note)

        # Заметки без тегов, но со ссылками
        for note in sorted(all_md_files):
            if note not in visited_notes:
                if note in self._note_links or note in back_links:
                    add_note(self.root, note)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if not data:
            return
        if data.get("type") == "note":
            self.post_message(self.NoteSelected(data["value"]))
        elif data.get("type") == "tag":
            self.post_message(self.TagSelected(data["value"]))


class LeftRibbon(Vertical):
    """Самая левая панель-ленточка с кнопками переключения режимов боковой панели."""

    class ModeChanged(Message):
        def __init__(self, mode: str) -> None:
            self.mode = mode
            super().__init__()

    def compose(self) -> ComposeResult:
        files_btn = ToolButton("📁", id="files-mode-btn", classes="ribbon-btn active")
        files_btn.tooltip = _("Files")
        search_btn = ToolButton("🔍", id="search-mode-btn", classes="ribbon-btn")
        search_btn.tooltip = _("Search")
        yield files_btn
        yield search_btn

    def set_active(self, mode: str) -> None:
        for btn_id, m in (("files-mode-btn", "files"), ("search-mode-btn", "search")):
            try:
                btn = self.query_one(f"#{btn_id}", ToolButton)
            except Exception:
                continue
            if m == mode:
                btn.add_class("active")
            else:
                btn.remove_class("active")

    def on_tool_button_pressed(self, event: ToolButton.Pressed) -> None:
        mode = "files" if event.button_id == "files-mode-btn" else "search"
        self.set_active(mode)
        self.post_message(self.ModeChanged(mode))


class SearchResultsTree(Tree):
    """Дерево результатов полнотекстового поиска."""

    class FileSelected(Message):
        def __init__(self, path: Path) -> None:
            self.path = path
            super().__init__()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        data = event.node.data
        if data and data.get("type") == "note":
            self.post_message(self.FileSelected(data["value"]))


class SearchView(Vertical):
    """Панель полнотекстового поиска (вместо дерева файлов)."""

    class FileSelected(Message):
        def __init__(self, path: Path, match_index: int = 0) -> None:
            self.path = path
            self.match_index = match_index
            super().__init__()

    class PrevMatch(Message):
        pass

    class NextMatch(Message):
        pass

    class Cleared(Message):
        pass

    def compose(self) -> ComposeResult:
        with Horizontal(id="search-input-row"):
            inp = Input(placeholder=_("Search notes"), id="search-input")
            inp.tooltip = _("Full-text search")
            yield inp
            clear_btn = ToolButton("✕", id="clear-search-btn", classes="search-clear-btn")
            clear_btn.tooltip = _("Clear")
            yield clear_btn
        yield Label("", id="search-status")
        yield SearchResultsTree(_("Search results"), id="search-results-tree")
        with Horizontal(id="search-nav"):
            prev_btn = ToolButton("▲", id="search-prev-btn", classes="search-nav-btn")
            prev_btn.tooltip = _("Previous result")
            yield prev_btn
            next_btn = ToolButton("▼", id="search-next-btn", classes="search-nav-btn")
            next_btn.tooltip = _("Next result")
            yield next_btn
            yield Label("", id="search-match-status")

    def set_results(self, results: List[Dict[str, Any]], total_found: int) -> None:
        """Заполнить дерево результатов."""
        tree = self.query_one("#search-results-tree", SearchResultsTree)
        tree.clear()
        tree.show_root = True
        tree.root.set_label(_("Search results"))
        tree.root.expand()
        if not results:
            tree.root.add(_("No results"))
        else:
            for r in results:
                node = tree.root.add(f"📄 {r['path'].name}", data={"type": "note", "value": r["path"]})
                if r.get("snippet"):
                    node.add_leaf(f"[dim]{escape(r['snippet'])}[/dim]")
        status = self.query_one("#search-status", Label)
        status.update(f"{total_found} results")

    def update_match_status(self, current: int, total: int) -> None:
        label = self.query_one("#search-match-status", Label)
        if total <= 0:
            label.update("")
        else:
            label.update(_("Result {current} / {total}", current=current + 1, total=total))

    def get_query(self) -> str:
        try:
            return self.query_one("#search-input", Input).value
        except Exception:
            return ""

    def set_query(self, value: str) -> None:
        try:
            self.query_one("#search-input", Input).value = value
        except Exception:
            pass

    def on_search_results_tree_file_selected(self, event: SearchResultsTree.FileSelected) -> None:
        self.post_message(self.FileSelected(event.path))

    def on_tool_button_pressed(self, event: ToolButton.Pressed) -> None:
        if event.button_id == "clear-search-btn":
            self.query_one("#search-input", Input).value = ""
            self.post_message(self.Cleared())
        elif event.button_id == "search-prev-btn":
            self.post_message(self.PrevMatch())
        elif event.button_id == "search-next-btn":
            self.post_message(self.NextMatch())


class InNoteSearch(ModalScreen):
    """Модальный диалог поиска по текущей заметке."""

    BINDINGS = [
        Binding("escape", "close", "Close", priority=True),
        Binding("f3", "next", "Next result", priority=True),
        Binding("shift+f3", "prev", "Prev result", priority=True),
        Binding("enter", "next", "Next result", show=False, priority=True),
    ]

    class QueryChanged(Message):
        """Пользователь изменил запрос."""

        def __init__(self, query: str) -> None:
            self.query = query
            super().__init__()

    class PrevMatch(Message):
        pass

    class NextMatch(Message):
        pass

    DEFAULT_CSS = """
    InNoteSearch {
        align: center top;
        background: transparent;
    }

    InNoteSearch #in-note-search-container {
        width: 60;
        height: auto;
        max-height: 20%;
        margin-top: 1;
        background: $surface;
        border: thick $primary;
    }

    InNoteSearch #in-note-search-title {
        height: 1;
        padding: 0 1;
        text-style: bold;
    }

    InNoteSearch #in-note-search-input {
        width: 1fr;
        margin: 0 1 1 1;
    }

    InNoteSearch #in-note-search-nav {
        height: auto;
        margin: 0 1 1 1;
    }

    InNoteSearch #in-note-search-status {
        width: 1fr;
        height: 1;
        content-align: right middle;
        color: $text;
        text-style: dim;
    }
    """

    def __init__(self, initial_query: str = "", **kwargs):
        super().__init__(**kwargs)
        self.initial_query = initial_query

    def compose(self) -> ComposeResult:
        with Container(id="in-note-search-container"):
            yield Label(_("Search in note"), id="in-note-search-title")
            yield Input(placeholder=_("Find in note..."), value=self.initial_query, id="in-note-search-input")
            with Horizontal(id="in-note-search-nav"):
                prev_btn = ToolButton("▲", id="in-note-search-prev", classes="search-nav-btn")
                prev_btn.tooltip = _("Previous result")
                yield prev_btn
                next_btn = ToolButton("▼", id="in-note-search-next", classes="search-nav-btn")
                next_btn.tooltip = _("Next result")
                yield next_btn
                yield Label("", id="in-note-search-status")

    def on_mount(self) -> None:
        input_widget = self.query_one("#in-note-search-input", Input)
        input_widget.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "in-note-search-input":
            self.post_message(self.QueryChanged(event.value))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "in-note-search-input":
            self.post_message(self.NextMatch())

    def on_tool_button_pressed(self, event: ToolButton.Pressed) -> None:
        if event.button_id == "in-note-search-prev":
            self.post_message(self.PrevMatch())
        elif event.button_id == "in-note-search-next":
            self.post_message(self.NextMatch())

    def action_close(self) -> None:
        self.dismiss(None)

    def action_next(self) -> None:
        self.post_message(self.NextMatch())

    def action_prev(self) -> None:
        self.post_message(self.PrevMatch())

    def update_status(self, current: int, total: int) -> None:
        label = self.query_one("#in-note-search-status", Label)
        if total <= 0:
            label.update(_("No matches"))
        else:
            label.update(_("Result {current} / {total}", current=current + 1, total=total))


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

    def __init__(self, title: str, placeholder: str = "", initial: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._placeholder = placeholder
        self._initial = initial

    def compose(self) -> ComposeResult:
        input_widget = Input(placeholder=self._placeholder, id="prompt-input")
        input_widget.value = self._initial
        yield Container(
            Label(f"[bold]{self._title}[/bold]"),
            input_widget,
            Label(f"[dim]{_('Enter — confirm, Escape — cancel')}[/dim]"),
            id="prompt-container",
        )

    def on_mount(self) -> None:
        self.query_one("#prompt-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip() or None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ConfirmModal(ModalScreen[bool]):
    """Модальное окно подтверждения да/нет."""

    BINDINGS = [
        Binding("enter", "confirm", "Confirm"),
        Binding("escape", "cancel", "Cancel"),
        Binding("y", "confirm", "Confirm", show=False),
        Binding("n", "cancel", "Cancel", show=False),
    ]

    def __init__(self, title: str, message: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._message = message

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"[bold]{self._title}[/bold]"),
            Label(self._message),
            Label(f"[dim]{_('Enter — confirm, Escape — cancel')}[/dim]"),
            id="confirm-container",
        )

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)


class TemplateSelectModal(ModalScreen[Optional[str]]):
    """Модальное окно выбора шаблона для создания заметки.

    Показывает список доступных шаблонов из ``templates_path``.
    Закрывается с именем шаблона (stem файла) или None при отмене.
    """

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, templates_dir: Path, **kwargs) -> None:
        super().__init__(**kwargs)
        self._templates = collect_templates(templates_dir)
        self._items: list[tuple[str, str, str]] = []
        for name, fp in self._templates.items():
            parent = fp.parent.name
            rel = fp.relative_to(templates_dir).parent
            category = str(rel).replace(".", "") if str(rel) != "." else ""
            self._items.append((name, str(fp.stem), category))

    def compose(self) -> ComposeResult:
        yield Container(
            Label(f"[bold]{_('Select template')}[/bold]"),
            ListView(
                *[
                    ListItem(Label(f"[bold]{name}[/bold]"
                                  f"  [dim]{' — ' + cat if cat else ''}[/dim]"),
                             name=name)
                    for name, _stem, cat in self._items
                ],
                id="template-list",
            ),
            Label(f"[dim]{_('Escape to close')}[/dim]"),
            id="template-modal-container",
        )

    def on_mount(self) -> None:
        lst = self.query_one("#template-list", ListView)
        lst.focus()
        if lst.children:
            lst.index = 0

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.name:
            self.dismiss(event.item.name)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class VerticalSplitter(Static):
    """Вертикальный разделитель, ширину которого можно менять перетаскиванием."""

    def __init__(self, **kwargs):
        super().__init__("", **kwargs)
        self._dragging = False
        self._drag_start_x = 0
        self._drag_start_width = 0

    def on_mouse_down(self, event) -> None:
        self._dragging = True
        self.capture_mouse()
        self._drag_start_x = event.screen_x
        sidebar = self.app.query_one("#sidebar")
        self._drag_start_width = sidebar.size.width

    def on_mouse_up(self, event) -> None:
        self._dragging = False
        self.release_mouse()
        main_container = self.app.query_one("#main-container")
        sidebar_width = int(main_container.styles.grid_columns[0].value)
        self.app.config.save_display_value("sidebar_width", sidebar_width)

    def on_mouse_move(self, event) -> None:
        if not self._dragging:
            return
        delta = event.screen_x - self._drag_start_x
        new_width = max(10, self._drag_start_width + delta)
        main_container = self.app.query_one("#main-container")
        main_container.styles.grid_columns = (new_width, 1, "1fr")


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
        Binding("ctrl+f", "toggle_search_mode", "Search"),
        Binding("f3", "search_next", "Next result"),
        Binding("shift+f3", "search_prev", "Prev result"),
        Binding("f7", "search_in_note", "Find in note", show=False, priority=True),
        Binding("ctrl+shift+f", "toggle_favorite", "Favorite"),
        Binding("ctrl+l", "toggle_theme", "Theme"),
        Binding("ctrl+question", "help", "Help"),
        Binding("d", "delete_selected", "Delete", show=False),
        Binding("r", "rename_selected", "Rename", show=False),
        Binding("backspace", "go_back", "Back", show=False),
    ]

    DEFAULT_CSS = """
    Screen {
        background: $background;
    }

    #main-container {
        layout: grid;
        grid-size: 4 1;
        grid-columns: 3 30 1 1fr;
        height: 1fr;
    }

    #left-ribbon {
        width: 3;
        height: 1fr;
        background: $surface-darken-1;
        border-right: solid $primary-darken-2;
        padding: 1 0;
    }

    .ribbon-btn {
        width: 3;
        height: 1;
        margin: 0 0 1 0;
        padding: 0;
        text-align: center;
        background: transparent;
        color: $text;
    }

    .ribbon-btn:hover {
        background: $primary-darken-2;
        color: $text;
    }

    .ribbon-btn.active {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #sidebar {
        border: solid $primary-darken-2;
        border-left: none;
        padding: 0;
        background: $surface;
    }

    VerticalSplitter {
        width: 1;
        background: transparent;
    }

    VerticalSplitter:hover {
        background: $primary-lighten-1;
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

    #search-view {
        height: 1fr;
        padding: 0;
        background: $surface;
        display: none;
    }

    #search-input-row {
        height: auto;
        padding: 1;
        background: $surface;
    }

    #search-input {
        width: 1fr;
        height: auto;
        min-height: 3;
    }

    .search-clear-btn {
        width: 3;
        height: auto;
        min-height: 3;
        margin-left: 1;
        padding: 0;
        text-align: center;
        background: $primary-darken-1;
        color: $text;
    }

    .search-clear-btn:hover {
        background: $error;
        color: $text;
    }

    #search-status {
        height: 1;
        padding: 0 1;
        color: $text;
        text-style: dim;
    }

    #search-results-tree {
        height: 1fr;
        background: $surface;
        padding: 0 0 0 1;
    }

    #search-results-tree Tree > .tree--directory {
        text-style: bold;
    }

    #search-nav {
        height: auto;
        padding: 0 1 1 1;
        background: $surface;
        border-top: solid $primary-darken-2;
    }

    .search-nav-btn {
        width: 5;
        height: 1;
        margin: 0 0 0 1;
        padding: 0 1;
        text-align: center;
        background: $primary-darken-1;
        color: $text;
    }

    .search-nav-btn:hover {
        background: $primary;
        color: $text;
    }

    #search-match-status {
        width: 1fr;
        height: 1;
        content-align: right middle;
        color: $text;
    }

    .search-highlight {
        background: #ffcc00;
        color: #000000;
        text-style: bold;
    }

    .search-current {
        background: #ff3333;
        color: #ffffff;
        text-style: bold reverse;
    }

    .search-current-warning {
        background: #ff5f1f;
        color: #000000;
        text-style: bold reverse;
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

    #editor-container {
        display: none;
        height: 1fr;
    }

    #editor-toolbar {
        height: auto;
        padding: 0 1;
        background: $surface-darken-1;
        border-bottom: solid $primary-darken-2;
    }

    .toolbar-btn {
        width: auto;
        min-width: 3;
        height: 1;
        margin: 0 0 0 1;
        padding: 0 1;
        text-align: center;
        background: $primary-darken-1;
        color: $text;
    }

    .toolbar-btn:hover {
        background: $primary;
        color: $text;
        text-style: bold;
    }

    #editor {
        height: 1fr;
    }

    #form-view {
        display: none;
        padding: 1 2;
    }

    #graph-view {
        display: none;
        height: 1fr;
        padding: 0;
        background: $background;
    }

    #graph-view Tree {
        padding: 0 1;
        height: 1fr;
    }

    #base-view {
        display: none;
        height: 1fr;
        padding: 0 1;
        background: $background;
    }

    #base-filters {
        width: auto;
        height: auto;
        padding: 0;
        layout: horizontal;
    }

    .base-filter-item {
        width: auto;
        height: 3;
        margin-right: 0;
        padding: 0;
        content-align: center middle;
    }

    .base-filter-multiselect-item {
        height: auto;
    }

    .base-filter-row {
        width: auto;
        height: 3;
        align: center middle;
    }

    .base-filter-label {
        height: 1;
        color: $text;
        text-style: bold;
        margin-right: 1;
        content-align-vertical: middle;
    }

    .base-filter-widget {
        width: auto;
        height: 1;
    }

    .base-filter-display {
        width: 100%;
        height: auto;
        color: $text;
        text-style: italic;
        padding: 0 1;
    }

    .base-filter-select {
        width: 26;
        height: 1;
    }

    .base-filter-string {
        width: 26;
        height: auto;
    }

    .base-filter-number {
        width: 14;
        height: auto;
    }

    .base-filter-date {
        width: 18;
        height: auto;
    }

    .base-filter-reset {
        width: 3;
        height: 1;
        min-width: 3;
        padding: 0;
        content-align: center middle;
        border: none;
        background: transparent;
        color: $text;
        text-style: dim;
    }

    .base-filter-mode {
        width: 4;
        height: 1;
        min-width: 4;
        padding: 0;
        content-align: center middle;
        border: none;
        background: transparent;
        color: $text-accent;
        text-style: bold;
    }

    #base-results {
        height: 1fr;
        padding: 1 0;
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

    #template-modal-container {
        width: 40;
        height: auto;
        margin: 2 4;
        border: thick $primary;
        padding: 1 2;
    }

    #template-modal-container > #template-list {
        height: auto;
        max-height: 15;
        margin: 1 0;
    }
    """

    def __init__(self, config: Config = None):
        super().__init__()
        self.config = config or Config.load()
        set_language(self.config.language)
        self.file_system = FileSystem(
            str(self.config.resolve_notes_path()),
            templates_subfolder=self.config.templates_path,
        )
        self.parser = MarkdownParser(
            syntax_theme=self.config.display.get("syntax_theme", "monokai")
        )
        self.theme = self.config.display.get("app_theme", "textual-dark")

        self.current_file: Optional[Path] = None
        self.is_edit_mode = False
        self.sidebar_visible = True
        self.sidebar_mode = "files"  # "files" | "search"
        self.tag_cache: Dict[str, List[Path]] = {}
        self.tag_colors: Dict[str, str] = {}
        self.note_links: Dict[Path, Set[Path]] = {}
        self._original_content: str = ""
        self._last_editor_selection = None
        self._file_history: List[Path] = []
        self._return_to_graph: bool = False
        self.tag_index = TagIndex(self.file_system.root_path)
        self.fts_index = FullTextIndex(self.file_system.root_path)
        self.query_engine = QueryEngine(self.file_system, self.parser, self.tag_index)
        self._rebuild_tag_cache()

        # Полнотекстовый поиск
        self._search_query: str = ""
        self._search_terms: List[str] = []
        self._search_matches: List[Tuple[int, int, int]] = []
        self._current_match_index: int = 0
        self._search_results: List[Dict[str, Any]] = []

        # Поиск по текущей заметке
        self._in_note_search: SearchState = SearchState()
        self._in_note_search_global_backup: Optional[Dict[str, Any]] = None

    def _rebuild_tag_cache(self):
        """Обновить SQLite-индекс и перезагрузить кэш тегов, цветов и связей."""
        md_files = self.file_system.get_md_files()
        # Связи перестраиваем ДО тегов, чтобы использовать старые mtime
        self.tag_index.rebuild_note_links(md_files, self.parser)
        self.tag_index.rebuild(md_files, self.parser)
        self.fts_index.rebuild(md_files)
        self.tag_cache = self.tag_index.get_tag_files()
        self.tag_colors = self.tag_index.get_tag_colors()
        self.note_links = self.tag_index.get_note_links()

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
            yield LeftRibbon(id="left-ribbon")

            with Vertical(id="sidebar"):
                with Horizontal(id="sidebar-header"):
                    yield Label(f"[bold]{self.file_system.root_path.name}[/bold]", id="sidebar-label")
                    new_folder = ToolButton("+📁", id="new-folder-btn", classes="sidebar-btn")
                    new_folder.tooltip = _("Create folder")
                    yield new_folder
                    new_note = ToolButton("+📄", id="new-note-btn", classes="sidebar-btn")
                    new_note.tooltip = _("Create note")
                    yield new_note
                    daily_btn = ToolButton("+📅", id="new-daily-btn", classes="sidebar-btn")
                    daily_btn.tooltip = _("Create daily note")
                    yield daily_btn
                    tmpl_btn = ToolButton("🧩", id="new-template-btn", classes="sidebar-btn")
                    tmpl_btn.tooltip = _("From template")
                    yield tmpl_btn
                    fav_btn = ToolButton("⭐", id="toggle-fav-btn", classes="sidebar-btn")
                    fav_btn.tooltip = _("Toggle favorite")
                    yield fav_btn
                yield FileTree("Файлы", id="file-tree")
                with Vertical(id="tag-cloud-container"):
                    yield Label(f"[bold]{_('Tags')}[/bold]")
                    yield TagCloud(id="tag-cloud")
                yield SearchView(id="search-view")

            yield VerticalSplitter(id="splitter")

            with Vertical(id="content-area"):
                yield MarkdownViewer(id="viewer")
                with Vertical(id="editor-container"):
                    yield EditorToolbar(id="editor-toolbar")
                    yield EditorTextArea(id="editor", language="markdown")
                yield FormView(id="form-view")
                yield BaseView(id="base-view")
                yield LinkGraphTree(id="graph-view")

        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self):
        """Инициализация после монтирования."""
        retranslate_bindings(self)
        hotkey = self.config.hotkeys.get("search_in_note", "f7")
        if hotkey and hotkey.lower() != "f7":
            self.bind(hotkey, "search_in_note", description=_("Find in note"), show=False)
        self.refresh_bindings()
        self._refresh_file_tree()
        self._update_tag_cloud()

        sidebar_width = self.config.display.get("sidebar_width", 30)
        main_container = self.query_one("#main-container")
        main_container.styles.grid_columns = (3, sidebar_width, 1, "1fr")

        editor = self.query_one("#editor", TextArea)
        self.query_one("#editor-container").display = False
        self.query_one("#form-view", FormView).display = False
        self.query_one("#base-view", BaseView).display = False
        self.query_one("#graph-view", LinkGraphTree).display = False
        self.query_one("#search-view", SearchView).display = False
        self._set_sidebar_mode("files")
        self._register_markdown_highlights(editor)
        self._apply_editor_syntax_theme(editor)
        self._update_status()

    def _set_sidebar_mode(self, mode: str) -> None:
        """Переключить боковую панель: дерево файлов или поиск."""
        self.sidebar_mode = mode
        ribbon = self.query_one("#left-ribbon", LeftRibbon)
        ribbon.set_active(mode)
        file_tree = self.query_one("#file-tree", FileTree)
        tag_cloud = self.query_one("#tag-cloud-container", Vertical)
        search_view = self.query_one("#search-view", SearchView)
        if mode == "files":
            file_tree.display = True
            tag_cloud.display = True
            search_view.display = False
        else:
            file_tree.display = False
            tag_cloud.display = False
            search_view.display = True
            def _focus_input() -> None:
                try:
                    inp = search_view.query_one("#search-input", Input)
                    self.set_focus(inp)
                except Exception:
                    pass
            self.call_after_refresh(_focus_input)

    def on_left_ribbon_mode_changed(self, event: LeftRibbon.ModeChanged) -> None:
        """Переключение режима левой панели."""
        self._set_sidebar_mode(event.mode)

    def action_toggle_search_mode(self) -> None:
        """Переключить режим боковой панели (файлы / поиск)."""
        if self._in_note_search.is_active:
            return
        new_mode = "search" if self.sidebar_mode == "files" else "files"
        self._set_sidebar_mode(new_mode)

    def action_search_in_note(self) -> None:
        """Открыть диалог поиска по текущей заметке."""
        if not self.current_file or self._in_note_search.is_active:
            return
        self._close_in_note_search_global_backup()
        self._in_note_search_global_backup = {
            "query": self._search_query,
            "terms": list(self._search_terms),
            "matches": list(self._search_matches),
            "index": self._current_match_index,
        }
        self._in_note_search = SearchState(is_active=True)
        self.push_screen(
            InNoteSearch(initial_query=self._in_note_search.query),
            callback=self._on_in_note_search_closed,
        )

    def _close_in_note_search_global_backup(self) -> None:
        """Восстановить состояние глобального поиска, если диалог уже открыт."""
        if self._in_note_search_global_backup is not None:
            backup = self._in_note_search_global_backup
            self._search_query = backup["query"]
            self._search_terms = backup["terms"]
            self._search_matches = backup["matches"]
            self._current_match_index = backup["index"]
            self._in_note_search_global_backup = None

    def _on_in_note_search_closed(self, _: Any) -> None:
        """Закрытие диалога поиска по заметке: снять подсветку и восстановить фокус."""
        self._in_note_search.is_active = False
        self._in_note_search = SearchState()
        self._close_in_note_search_global_backup()
        if self.current_file:
            self._load_file()
        self._focus_current_content()

    def _focus_current_content(self) -> None:
        """Вернуть фокус просмотрщику или редактору."""
        try:
            viewer = self.query_one("#viewer", MarkdownViewer)
            editor_container = self.query_one("#editor-container")
            if editor_container.display:
                self.query_one("#editor", TextArea).focus()
            elif viewer.display:
                viewer.focus()
        except Exception:
            pass

    def _close_in_note_search(self) -> None:
        """Закрыть модальный диалог поиска по заметке, если он активен."""
        if not self._in_note_search.is_active:
            return
        try:
            self.pop_screen()
        except Exception:
            self._on_in_note_search_closed(None)

    def _current_note_content_for_search(self) -> str:
        """Текущее содержимое заметки (из редактора или файла)."""
        if self.is_edit_mode:
            try:
                return self.query_one("#editor", TextArea).text
            except Exception:
                return ""
        if self.current_file:
            return self.file_system.read_file(self.current_file)
        return ""

    def _update_in_note_search(self, query: str) -> None:
        """Пересчитать совпадения для нового запроса и применить подсветку."""
        self._in_note_search.query = query
        self._in_note_search.current_index = 0
        self._in_note_search.matches = []
        if query.strip() and self.current_file:
            content = self._current_note_content_for_search()
            self._in_note_search.matches = find_matches(content, query)
            self._apply_in_note_match()
        elif self.current_file:
            self._load_file()
        self._update_in_note_status()

    def _apply_in_note_match(self) -> None:
        """Выделить текущее совпадение поиска по заметке."""
        if not self._in_note_search.matches or not self.current_file:
            return
        idx = self._in_note_search.current_index % len(self._in_note_search.matches)
        match = self._in_note_search.matches[idx]
        viewer = self.query_one("#viewer", MarkdownViewer)
        editor = self.query_one("#editor", TextArea)
        if viewer.display:
            content = self._current_note_content_for_search()
            viewer.update_content(content, [self._in_note_search.query], idx)
        elif editor.display:
            from textual.widgets.text_area import Selection
            query_len = len(self._in_note_search.query)
            editor.selection = Selection(
                (match.line, match.column), (match.line, match.column + query_len)
            )
            editor.scroll_cursor_visible()

    def _update_in_note_status(self) -> None:
        """Обновить счётчик совпадений в диалоге."""
        try:
            dialog = self.query_one(InNoteSearch)
        except Exception:
            return
        if self._in_note_search.matches:
            dialog.update_status(self._in_note_search.current_index, len(self._in_note_search.matches))
        else:
            dialog.update_status(0, 0)

    def on_in_note_search_query_changed(self, event: InNoteSearch.QueryChanged) -> None:
        """Пользователь изменил запрос в диалоге."""
        self._update_in_note_search(event.query)

    def on_in_note_search_next_match(self, _: InNoteSearch.NextMatch) -> None:
        """Следующее совпадение в текущей заметке."""
        self._in_note_search.select_next()
        self._apply_in_note_match()
        self._update_in_note_status()

    def on_in_note_search_prev_match(self, _: InNoteSearch.PrevMatch) -> None:
        """Предыдущее совпадение в текущей заметке."""
        self._in_note_search.select_prev()
        self._apply_in_note_match()
        self._update_in_note_status()

    def action_search_next(self) -> None:
        """Следующее совпадение (F3)."""
        if self._in_note_search.is_active:
            self.on_in_note_search_next_match(InNoteSearch.NextMatch())
            return
        self._search_next()

    def action_search_prev(self) -> None:
        """Предыдущее совпадение (Shift+F3)."""
        if self._in_note_search.is_active:
            self.on_in_note_search_prev_match(InNoteSearch.PrevMatch())
            return
        self._search_prev()

    def action_toggle_edit(self):
        """Переключить режим редактирования."""
        if self._in_note_search.is_active:
            self._close_in_note_search()
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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Запускаем поиск по Enter в строке поиска."""
        if event.input.id == "search-input":
            self._run_search(event.value)

    def _run_search(self, query: str) -> None:
        """Выполнить полнотекстовый поиск и обновить панель результатов."""
        self._search_query = query.strip()
        self._search_terms = self.fts_index.extract_terms(self._search_query) if self._search_query else []
        self._current_match_index = 0
        self._search_matches = []
        search_view = self.query_one("#search-view", SearchView)
        if not self._search_query:
            self._search_results = []
            search_view.set_results([], 0)
            search_view.update_match_status(0, 0)
            if self.current_file:
                self._load_file()
            return
        results = self.fts_index.search(self._search_query, limit=200)
        self._search_results = results
        search_view.set_results(results, len(results))
        if results:
            self._set_sidebar_mode("search")
        if self.current_file:
            self._load_file()
        else:
            search_view.update_match_status(0, 0)

    def _compute_search_matches(self, content: str) -> None:
        """Построить список совпадений для текущего содержимого."""
        self._search_matches = []
        if not self._search_terms or not content:
            return
        escaped = [re.escape(t) for t in sorted(self._search_terms, key=len, reverse=True)]
        pattern = re.compile("|".join(escaped), re.IGNORECASE)
        for lnum, line in enumerate(content.split("\n")):
            for match in pattern.finditer(line):
                self._search_matches.append((lnum, match.start(), match.end()))

    def _apply_current_match(self) -> None:
        """Подсветить/выделить текущее совпадение в просмотре или редакторе."""
        search_view = self.query_one("#search-view", SearchView)
        if not self._search_matches:
            search_view.update_match_status(0, 0)
            return
        idx = self._current_match_index % len(self._search_matches)
        line, start, end = self._search_matches[idx]
        search_view.update_match_status(idx, len(self._search_matches))

        viewer = self.query_one("#viewer", MarkdownViewer)
        if viewer.display and self.current_file:
            content = self.file_system.read_file(self.current_file)
            viewer.update_content(content, self._search_terms, idx)
            return

        editor = self.query_one("#editor", TextArea)
        if editor.display:
            from textual.widgets.text_area import Selection
            editor.selection = Selection((line, start), (line, end))
            editor.scroll_cursor_visible()
            editor.focus()

    def _search_next(self) -> None:
        if not self._search_matches:
            return
        self._current_match_index = (self._current_match_index + 1) % len(self._search_matches)
        self._apply_current_match()

    def _search_prev(self) -> None:
        if not self._search_matches:
            return
        self._current_match_index = (self._current_match_index - 1) % len(self._search_matches)
        self._apply_current_match()

    def action_search_next(self) -> None:
        """Следующее совпадение (F3)."""
        self._search_next()

    def action_search_prev(self) -> None:
        """Предыдущее совпадение (Shift+F3)."""
        self._search_prev()

    def on_search_view_file_selected(self, event: SearchView.FileSelected) -> None:
        """Открыть файл из результатов поиска."""
        self._return_to_graph = False
        self._current_match_index = event.match_index
        self._navigate_to(event.path)

    def on_search_view_cleared(self, _: SearchView.Cleared) -> None:
        """Очистить поиск."""
        self._search_query = ""
        self._search_terms = []
        self._search_matches = []
        self._current_match_index = 0
        self.query_one("#search-view", SearchView).set_results([], 0)
        self.query_one("#search-view", SearchView).update_match_status(0, 0)
        if self.current_file:
            self._load_file()

    def on_search_view_prev_match(self, _: SearchView.PrevMatch) -> None:
        self._search_prev()

    def on_search_view_next_match(self, _: SearchView.NextMatch) -> None:
        self._search_next()

    def _apply_editor_syntax_theme(self, editor: TextArea) -> None:
        """Установить синтаксическую тему редактора под текущую тему приложения."""
        if self.theme in _LIGHT_THEMES:
            editor.theme = "github_light"
        else:
            editor.theme = self.config.display.get("syntax_theme", "monokai")

    def watch_theme(self, theme: str) -> None:
        """Сохранить выбранную тему в конфиг при любом изменении."""
        if getattr(self, "config", None):
            self.config.save_theme(theme)

    def action_toggle_theme(self) -> None:
        """Переключить светлую / тёмную тему."""
        if self.theme in _LIGHT_THEMES:
            new_theme = self.config.display.get("app_theme", "textual-dark")
            if new_theme in _LIGHT_THEMES:
                new_theme = "textual-dark"
        else:
            new_theme = "textual-light"
        self.theme = new_theme
        editor = self.query_one("#editor", TextArea)
        self._apply_editor_syntax_theme(editor)
        # Перерисовать открытый файл с новой темой кода
        if self.current_file and not self.is_edit_mode:
            viewer = self.query_one("#viewer", MarkdownViewer)
            content = self.file_system.read_file(self.current_file)
            self._compute_search_matches(content)
            viewer.update_content(content, self._search_terms, self._current_match_index)
            self._update_search_match_status()

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

    def _navigate_to(self, path: Path) -> None:
        """Открыть файл, сохранив текущий в историю навигации."""
        if self.current_file and self.current_file != path:
            self._file_history.append(self.current_file)
        self.current_file = path
        self._load_file()

    def action_go_back(self) -> None:
        """Вернуться к предыдущему файлу из истории (Backspace в режиме просмотра).

        Если последний переход был из дерева связей — вернуться в граф."""
        if self.is_edit_mode:
            return
        if self._return_to_graph:
            self._return_to_graph = False
            self.show_graph()
            return
        if not self._file_history:
            return
        prev = self._file_history.pop()
        self.current_file = prev
        self._load_file()

    def on_file_tree_file_selected(self, event: FileTree.FileSelected):
        """Обработать выбор файла."""
        self._return_to_graph = False
        self._navigate_to(event.path)

    def on_file_tree_graph_selected(self, _: FileTree.GraphSelected) -> None:
        """Показать дерево связей."""
        self.show_graph()

    def show_graph(self) -> None:
        """Показать дерево связей и скрыть остальные панели."""
        viewer = self.query_one("#viewer", MarkdownViewer)
        editor_container = self.query_one("#editor-container")
        form = self.query_one("#form-view", FormView)
        base = self.query_one("#base-view", BaseView)
        graph = self.query_one("#graph-view", LinkGraphTree)

        viewer.display = False
        editor_container.display = False
        form.display = False
        base.display = False
        graph.display = True
        graph.build_graph(
            self.tag_cache,
            self.tag_colors,
            self.note_links,
            self.file_system.get_md_files(),
        )
        graph.focus()
        self.title = "Impactite — " + _("Link graph")
        self._update_status()

    def on_link_graph_tree_note_selected(self, event: LinkGraphTree.NoteSelected) -> None:
        """Открыть заметку из дерева связей."""
        if event.path.exists() and event.path.is_file():
            self._return_to_graph = True
            self._navigate_to(event.path)
        else:
            self.notify(_("File not found: {path}", path=str(event.path)), severity="error")

    def on_link_graph_tree_tag_selected(self, event: LinkGraphTree.TagSelected) -> None:
        """Открыть поиск по тегу из дерева связей."""
        self.push_screen(TagSearchModal(self.tag_cache, initial_query=event.tag, tag_colors=self.tag_colors))

    def _load_file(self):
        """Загрузить текущий файл."""
        if not self.current_file:
            return

        content = self.file_system.read_file(self.current_file)
        self._compute_search_matches(content)

        viewer = self.query_one("#viewer", MarkdownViewer)
        editor = self.query_one("#editor", TextArea)
        editor_container = self.query_one("#editor-container")
        form   = self.query_one("#form-view", FormView)
        base   = self.query_one("#base-view", BaseView)
        graph  = self.query_one("#graph-view", LinkGraphTree)

        graph.display = False
        if self.is_edit_mode:
            viewer.display = False
            editor_container.display = True
            form.display   = False
            base.display   = False
            self._original_content = content
            editor.load_text(content)
            self._apply_editor_search_match()
        else:
            form_def = parse_form_definition(content)
            base_def = parse_base_definition(content)
            if form_def is not None:
                viewer.display = False
                editor_container.display = False
                form.display   = True
                base.display   = False
                form.load_form(form_def["catalog"], form_def["fields"],
                               form_def["destination"])
                form.focus()
            elif base_def is not None:
                viewer.display = False
                editor_container.display = False
                form.display   = False
                base.display   = True
                base.load_base(base_def["query"], base_def["filters"])
                base.focus()
            else:
                viewer.display = True
                editor_container.display = False
                form.display   = False
                base.display   = False
                viewer.update_content(content, self._search_terms, self._current_match_index)
                viewer.focus()

        self.title = f"Impactite — {self.current_file.name}"
        self._update_status()
        self._update_search_match_status()

    def _apply_editor_search_match(self) -> None:
        """Выделить текущее совпадение в редакторе."""
        if not self._search_matches:
            return
        idx = self._current_match_index % len(self._search_matches)
        line, start, end = self._search_matches[idx]
        editor = self.query_one("#editor", TextArea)
        from textual.widgets.text_area import Selection
        editor.selection = Selection((line, start), (line, end))
        editor.scroll_cursor_visible()

    def _update_search_match_status(self) -> None:
        """Обновить счётчик совпадений в панели поиска."""
        search_view = self.query_one("#search-view", SearchView)
        if self._search_matches:
            search_view.update_match_status(
                self._current_match_index % len(self._search_matches),
                len(self._search_matches),
            )
        else:
            search_view.update_match_status(0, 0)

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
                self._compute_search_matches(content)
                viewer.update_content(content, self._search_terms, self._current_match_index)
                self._update_search_match_status()
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

    def on_markdown_viewer_link_clicked(self, event: MarkdownViewer.LinkClicked) -> None:
        """Клик по внутренней ссылке — открыть связанную заметку."""
        if not self.current_file:
            return
        target = Path(event.target)
        if not target.is_absolute():
            target = (self.current_file.parent / target).resolve()
        if target.exists() and target.is_file():
            self._return_to_graph = False
            self._navigate_to(target)
        else:
            self.notify(_("File not found: {path}", path=str(target)), severity="error")

    def on_markdown_viewer_checkbox_toggled(self, event: MarkdownViewer.CheckboxToggled) -> None:
        """Переключить чекбокс в markdown-файле и сохранить."""
        if not self.current_file or self.is_edit_mode:
            return
        content = self.file_system.read_file(self.current_file)
        lines = content.split("\n")
        if not (0 <= event.source_line < len(lines)):
            return
        old_line = lines[event.source_line]
        match = re.search(r'\[([ xX])\]', old_line)
        if not match:
            return
        current_checked = match.group(1).lower() == 'x'
        new_char = ' ' if current_checked else 'x'
        new_line = old_line[:match.start()] + f'[{new_char}]' + old_line[match.end():]
        lines[event.source_line] = new_line
        new_content = "\n".join(lines)
        if self.file_system.write_file(self.current_file, new_content):
            viewer = self.query_one("#viewer", MarkdownViewer)
            self._compute_search_matches(new_content)
            viewer.update_content(new_content, self._search_terms, self._current_match_index)
            self._update_search_match_status()
            self._rebuild_tag_cache()
            self._update_tag_cloud()
        else:
            self.notify(_("Save error"), severity="error")

    def on_text_area_selection_changed(self, event: TextArea.SelectionChanged) -> None:
        """Запомнить последний НЕПУСТОЙ selection редактора для toolbar."""
        try:
            editor = self.query_one("#editor", TextArea)
            sel = editor.selection
            if sel and not sel.is_empty:
                self._last_editor_selection = sel
        except Exception:
            pass

    def on_editor_toolbar_action(self, event: EditorToolbar.Action) -> None:
        """Обработать нажатие кнопки панели инструментов редактора."""
        try:
            editor = self.query_one("#editor", TextArea)
        except Exception:
            return
        # Восстановить selection: сначала из toolbar'а, затем из кэша App
        saved_sel = event.selection
        if saved_sel is None or saved_sel.is_empty:
            saved_sel = getattr(self, "_last_editor_selection", None)
        if saved_sel is not None and not saved_sel.is_empty:
            editor.selection = saved_sel
        sel = editor.selection
        start, end = sel.start, sel.end
        has_selection = not sel.is_empty
        selected = editor.document.get_text_range(start, end) if has_selection else ""

        if event.action in ("bold", "italic", "strikethrough"):
            self._wrap_selection(editor, start, end, selected, event.action)
        elif event.action in ("h1", "h2", "h3"):
            self._prefix_line(editor, start, "#" * int(event.action[1]) + " ")
        elif event.action == "link":
            new_text = f"[{selected}](url)" if has_selection else "[text](url)"
            editor.replace(new_text, start, end)
            offset = len(f"[{selected}](") if has_selection else len("[text](")
            editor.move_cursor((start[0], start[1] + offset))
        elif event.action == "bullet":
            self._prefix_line(editor, start, "- ")
        elif event.action == "numbered":
            self._prefix_line(editor, start, "1. ")
        elif event.action == "checkbox":
            self._prefix_line(editor, start, "- [ ] ")
        elif event.action == "quote":
            self._prefix_line(editor, start, "> ")
        elif event.action == "code":
            if has_selection:
                new_text = f"```\n{selected}\n```"
                editor.replace(new_text, start, end)
            else:
                editor.insert("```\n\n```", start)
                editor.move_cursor((start[0] + 1, 0))
        elif event.action == "hr":
            editor.insert("\n---\n", start)
            editor.move_cursor((start[0] + 2, 0))

    def _wrap_selection(self, editor: TextArea, start, end, selected: str, action: str) -> None:
        """Обернуть выделенный текст markdown-разметкой или вставить пустой шаблон."""
        wraps = {
            "bold": ("**", "**"),
            "italic": ("*", "*"),
            "strikethrough": ("~~", "~~"),
        }
        prefix, suffix = wraps[action]
        if selected:
            new_text = f"{prefix}{selected}{suffix}"
            cursor_col = start[1] + len(new_text)
        else:
            new_text = f"{prefix}{suffix}"
            cursor_col = start[1] + len(prefix)
        editor.replace(new_text, start, end)
        editor.move_cursor((start[0], cursor_col))

    def _prefix_line(self, editor: TextArea, location, prefix: str) -> None:
        """Добавить префикс к строкам редактора (заголовки, списки, цитаты).

        Если выделено несколько строк — префикс применяется ко всем выделенным строкам.
        """
        sel = editor.selection
        start_row = min(sel.start[0], sel.end[0])
        end_row = max(sel.start[0], sel.end[0])
        lines = editor.text.split("\n")
        modified = False

        for row in range(start_row, end_row + 1):
            if not (0 <= row < len(lines)):
                continue
            old_line = lines[row]
            if prefix.startswith("#"):
                new_line = re.sub(r'^#+\s*', prefix, old_line)
            else:
                if old_line.startswith(prefix):
                    continue
                new_line = prefix + old_line
            lines[row] = new_line
            modified = True

        if modified:
            editor.load_text("\n".join(lines))
            last_line = lines[end_row] if 0 <= end_row < len(lines) else ""
            editor.move_cursor((end_row, len(last_line)))

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
        elif event.button_id == "new-daily-btn":
            self._create_daily_note()
        elif event.button_id == "new-template-btn":
            self._prompt_template_note()
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
                self.fts_index.index_file(target)
                self._rebuild_tag_cache()
                self._update_tag_cloud()
            self._refresh_file_tree()
            # Сразу открыть новую заметку в режиме редактирования
            self._navigate_to(target)
            self.is_edit_mode = True
            self._load_file()
            self.query_one("#editor", TextArea).focus()
            if created:
                self.notify(_("Note created: {name}", name=target.name), severity="information")

        self.push_screen(TextPromptModal(_("New note name"), _("note name")), done)

    def _create_daily_note(self) -> None:
        """Создать ежедневную заметку с предзаполненным frontmatter."""
        from datetime import date

        today = date.today()
        filename = today.strftime("%d.%m.%Y") + ".md"

        # Каталог для ежедневных заметок — внутри корня заметок
        daily_folder_name = self.config.daily_notes_folder
        catalog = self.file_system.root_path / daily_folder_name
        catalog.mkdir(parents=True, exist_ok=True)

        target = catalog / filename
        if not target.exists():
            date_str = today.isoformat()  # 2026-06-10
            frontmatter = f"---\ntype: daily_note\ndate: {date_str}\n---\n\n"
            if not self.file_system.write_file(target, frontmatter):
                self.notify(_("Note creation error"), severity="error")
                return
            self.fts_index.index_file(target)
            self._rebuild_tag_cache()
            self._update_tag_cloud()

        self._refresh_file_tree()
        self._navigate_to(target)
        self.is_edit_mode = True
        self._load_file()
        self.query_one("#editor", TextArea).focus()
        self.notify(_("Daily note created: {name}", name=filename), severity="information")

    def _prompt_template_note(self) -> None:
        """Выбрать шаблон, запросить имя и создать заметку по шаблону."""
        templates_dir = self.config.resolve_templates_path()
        if not templates_dir.is_dir() or not list(templates_dir.rglob("*.md")):
            self.notify(_("No templates found"), severity="warning")
            return

        self.push_screen(TemplateSelectModal(templates_dir), self._on_template_selected)

    def _on_template_selected(self, template_name: Optional[str]) -> None:
        """Обработчик выбора шаблона — запрашивает имя файла и создаёт заметку."""
        if not template_name:
            return

        templates_dir = self.config.resolve_templates_path()
        all_templates = collect_templates(templates_dir)
        template_path = all_templates.get(template_name)
        if not template_path:
            self.notify(_("Template not found"), severity="error")
            return

        catalog = self._current_catalog()

        def done(name: Optional[str]) -> None:
            if not name:
                return
            if not name.endswith(".md"):
                name += ".md"
            target = catalog / name
            created = False
            if not target.exists():
                # Собираем контекст
                ctx = build_context(
                    filepath=target,
                    title=target.stem,
                    author=self.config.author,
                )
                try:
                    content = render_template(
                        template_path.read_text(encoding="utf-8"),
                        ctx,
                    )
                except Exception as e:
                    self.notify(
                        _("Template render error: {error}", error=str(e)),
                        severity="error",
                    )
                    return
                if not self.file_system.write_file(target, content):
                    self.notify(_("Note creation error"), severity="error")
                    return
                created = True
                self.fts_index.index_file(target)
                self._rebuild_tag_cache()
                self._update_tag_cloud()
            self._refresh_file_tree()
            self._navigate_to(target)
            self.is_edit_mode = True
            self._load_file()
            self.query_one("#editor", TextArea).focus()
            if created:
                self.notify(
                    _("Note created from template: {name}", name=target.name),
                    severity="information",
                )

        self.push_screen(TextPromptModal(_("New note name"), _("note name")), done)

    def action_refresh(self):
        """Обновить список файлов."""
        file_tree = self.query_one("#file-tree", FileTree)
        self._refresh_file_tree()
        self._rebuild_tag_cache()
        self._update_tag_cloud()
        self.notify(_("File list refreshed"), severity="information")

    def _selected_path(self) -> Optional[Path]:
        """Вернуть путь выбранного узла в дереве файлов (файл или каталог)."""
        tree = self.query_one("#file-tree", FileTree)
        node = tree.cursor_node
        if node is None:
            return None
        node_id = id(node)
        if node_id in tree.file_nodes:
            return tree.file_nodes[node_id]
        if node_id in tree.dir_nodes:
            return tree.dir_nodes[node_id]
        return None

    def action_delete_selected(self) -> None:
        """Удалить выбранный файл или каталог."""
        path = self._selected_path()
        if path is None:
            return
        if path == self.file_system.root_path:
            self.notify(_("Cannot delete root directory"), severity="warning")
            return

        def confirm(confirmed: Optional[bool]) -> None:
            if not confirmed:
                return
            try:
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
            except Exception as e:
                self.notify(_("File delete error: {error}", error=e), severity="error")
                return
            self.fts_index.remove_file(path)
            if self.current_file and (self.current_file == path or path in self.current_file.parents):
                self.current_file = None
                self._original_content = ""
                self._compute_search_matches("")
                self._clear_main_area()
            self._rebuild_tag_cache()
            self._update_tag_cloud()
            self._refresh_file_tree()
            self.notify(_("File deleted: {name}", name=path.name), severity="information")

        self.push_screen(
            ConfirmModal(
                title=_("Confirm deletion"),
                message=_("Delete {name}?", name=path.name),
            ),
            confirm,
        )

    def action_rename_selected(self) -> None:
        """Переименовать выбранный файл или каталог."""
        path = self._selected_path()
        if path is None:
            return
        if path == self.file_system.root_path:
            self.notify(_("Cannot rename root directory"), severity="warning")
            return

        def done(name: Optional[str]) -> None:
            if not name:
                return
            new_path = path.parent / name
            if new_path.exists():
                self.notify(_("Target already exists"), severity="error")
                return
            try:
                path.rename(new_path)
            except Exception as e:
                self.notify(_("Rename error: {error}", error=e), severity="error")
                return
            self.fts_index.remove_file(path)
            if new_path.is_file() and new_path.suffix.lower() == ".md":
                self.fts_index.index_file(new_path)
            if self.current_file == path:
                self.current_file = new_path
            self._rebuild_tag_cache()
            self._update_tag_cloud()
            self._refresh_file_tree()
            self.notify(_("File renamed to {name}", name=new_path.name), severity="information")

        self.push_screen(
            TextPromptModal(_("New name"), placeholder=path.name, initial=path.name),
            done,
        )

    def _clear_main_area(self) -> None:
        """Очистить основную область (просмотр / редактор / форма / база / граф)."""
        viewer = self.query_one("#viewer", MarkdownViewer)
        editor_container = self.query_one("#editor-container")
        form = self.query_one("#form-view", FormView)
        base = self.query_one("#base-view", BaseView)
        graph = self.query_one("#graph-view", LinkGraphTree)
        viewer.display = False
        editor_container.display = False
        form.display = False
        base.display = False
        graph.display = False
        self.title = "Impactite"
        self._update_status()

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
            self.fts_index.index_file(filepath)
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
        self._return_to_graph = False
        self._navigate_to(event.path)

    def on_unmount(self) -> None:
        self.tag_index.close()
        self.fts_index.close()


def main():
    """Точка входа приложения."""
    import sys

    args = sys.argv[1:]
    if args and args[0] == "--mcp":
        from impactite.mcp_server import run_mcp

        config_path = args[1] if len(args) > 1 else "config.yaml"
        run_mcp(Config.load(config_path))
        return

    config_path = args[0] if args else "config.yaml"
    config = Config.load(config_path)

    app = MarkdownEditorApp(config)
    app.run()


if __name__ == "__main__":
    main()
