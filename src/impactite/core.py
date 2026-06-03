"""
Модуль для работы с файловой системой и парсинга Markdown.
"""
import colorsys
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import yaml
from markdown import Markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter
from pygments.styles import get_all_styles


@dataclass
class Config:
    """Конфигурация приложения."""
    notes_path: str = "./notes"
    language: str = "en"
    hotkeys: Dict[str, str] = field(default_factory=dict)
    display: Dict[str, any] = field(default_factory=dict)
    tags: Dict[str, any] = field(default_factory=dict)
    config_path: str = field(default="config.yaml", repr=False)

    def resolve_notes_path(self) -> Path:
        """Вернуть абсолютный путь к каталогу заметок.

        Поддерживаются: абсолютный путь, ``~`` (домашний каталог) и
        относительный путь. Относительный путь считается ОТНОСИТЕЛЬНО каталога
        конфиг-файла, а не текущей рабочей директории — чтобы запуск из любого
        места давал один и тот же каталог заметок.
        """
        p = Path(self.notes_path).expanduser()
        if not p.is_absolute():
            base = Path(self.config_path).expanduser().resolve().parent
            p = base / p
        return p.resolve()

    def save_theme(self, theme: str) -> None:
        """Обновить только app_theme в конфиг-файле, сохранив остальное без изменений."""
        self.display["app_theme"] = theme
        if not os.path.exists(self.config_path):
            return
        with open(self.config_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(
            r'(app_theme:\s*)["\']?[\w-]+["\']?',
            f'app_theme: "{theme}"',
            content,
        )
        with open(self.config_path, "w", encoding="utf-8") as f:
            f.write(content)

    @classmethod
    def load(cls, config_path: str = "config.yaml") -> "Config":
        """Загрузка конфигурации из YAML файла."""
        default_config = {
            "notes_path": "./notes",
            "language": "en",
            "hotkeys": {
                "open_file": "enter",
                "edit_mode": "e",
                "view_mode": "v",
                "save_file": "ctrl+s",
                "search_tags": "ctrl+t",
                "close_search": "escape",
                "quit": "ctrl+q",
                "refresh": "ctrl+r",
                "toggle_sidebar": "ctrl+b",
            },
            "display": {
                "show_line_numbers": True,
                "word_wrap": True,
                "syntax_theme": "monokai",
                "code_border": "round",
                "app_theme": "textual-dark",
            },
            "tags": {
                "show_cloud": True,
                "min_tag_size": 1,
                "max_tag_size": 3,
            }
        }

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                loaded = yaml.safe_load(f) or {}
                # Объединяем с дефолтными значениями
                for key in default_config:
                    if key not in loaded:
                        loaded[key] = default_config[key]
                    elif isinstance(default_config[key], dict):
                        for subkey in default_config[key]:
                            if subkey not in loaded[key]:
                                loaded[key][subkey] = default_config[key][subkey]
                return cls(
                    notes_path=loaded.get("notes_path", default_config["notes_path"]),
                    language=loaded.get("language", default_config["language"]),
                    hotkeys=loaded.get("hotkeys", default_config["hotkeys"]),
                    display=loaded.get("display", default_config["display"]),
                    tags=loaded.get("tags", default_config["tags"]),
                    config_path=config_path,
                )
        return cls(config_path=config_path)


@dataclass
class FileNode:
    """Узел файлового дерева."""
    name: str
    path: Path
    is_dir: bool
    children: List["FileNode"] = field(default_factory=list)
    level: int = 0

    def __lt__(self, other):
        # Директории всегда перед файлами
        if self.is_dir != other.is_dir:
            return self.is_dir
        return self.name.lower() < other.name.lower()


class FileSystem:
    """Управление файловой системой."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).expanduser().absolute()
        if not self.root_path.exists():
            self.root_path.mkdir(parents=True, exist_ok=True)

    def get_tree(self) -> FileNode:
        """Получить дерево файлов и директорий."""
        return self._build_tree(self.root_path, level=0)

    def _build_tree(self, path: Path, level: int) -> FileNode:
        """Рекурсивно построить дерево."""
        node = FileNode(
            name=path.name if path != self.root_path else self.root_path.name,
            path=path,
            is_dir=path.is_dir(),
            level=level
        )

        if path.is_dir():
            try:
                items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                for item in items:
                    if not item.name.startswith('.'):  # Игнорировать скрытые файлы
                        child = self._build_tree(item, level + 1)
                        node.children.append(child)
            except PermissionError:
                pass

        return node

    def read_file(self, path: Path) -> str:
        """Прочитать содержимое файла."""
        try:
            return path.read_text(encoding="utf-8")
        except Exception as e:
            return f"Ошибка чтения файла: {e}"

    def write_file(self, path: Path, content: str) -> bool:
        """Записать содержимое файла."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            return False

    def create_directory(self, path: Path) -> bool:
        """Создать каталог (вместе с родителями)."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def get_md_files(self) -> List[Path]:
        """Получить все .md файлы."""
        return list(self.root_path.rglob("*.md"))


class MarkdownParser:
    """Парсер Markdown с поддержкой подсветки кода."""

    def __init__(self, syntax_theme: str = "monokai"):
        self.syntax_theme = syntax_theme
        self.md = Markdown(extensions=['fenced_code', 'codehilite', 'tables', 'toc'])
        self._tag_pattern = re.compile(r'#(\w+)')

    def parse(self, content: str) -> str:
        """Преобразовать Markdown в HTML."""
        return self.md.convert(content)

    def extract_tags(self, content: str) -> Set[str]:
        """Извлечь все теги из содержимого."""
        return set(self._tag_pattern.findall(content))

    def _parse_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Вернуть (словарь frontmatter, тело документа без frontmatter)."""
        if not content.startswith("---"):
            return {}, content
        end = content.find("\n---", 3)
        if end == -1:
            return {}, content
        try:
            fm = yaml.safe_load(content[3:end]) or {}
            if not isinstance(fm, dict):
                fm = {}
        except Exception:
            fm = {}
        return fm, content[end + 4:]

    def extract_tags_with_source(self, path: Path) -> Tuple[Set[str], Set[str]]:
        """Вернуть (теги из frontmatter, теги из тела файла).

        Теги из frontmatter не включаются в body-набор.
        """
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return set(), set()

        fm, body = self._parse_frontmatter(content)

        fm_tags: Set[str] = set()
        raw = fm.get("tags", [])
        if isinstance(raw, str):
            raw = [t.strip() for t in raw.split(",")]
        elif not isinstance(raw, list):
            raw = []
        for t in raw:
            s = str(t).strip().lstrip("#")
            if s:
                fm_tags.add(s)

        body_tags = self.extract_tags(body) - fm_tags
        return fm_tags, body_tags

    def extract_tags_from_file(self, path: Path) -> Set[str]:
        """Извлечь теги из файла."""
        try:
            content = path.read_text(encoding="utf-8")
            return self.extract_tags(content)
        except Exception:
            return set()

    def find_files_by_tag(self, files: List[Path], tag: str) -> List[Tuple[Path, str]]:
        """Найти файлы, содержащие указанный тег."""
        results = []
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                if tag in self.extract_tags(content):
                    # Извлечь контекст вокруг тега
                    match = re.search(rf'#{tag}\b', content)
                    if match:
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        context = content[start:end].strip()
                        results.append((file_path, context))
            except Exception:
                continue
        return results

    def highlight_code_block(self, code: str, language: str = None) -> str:
        """Подсветить блок кода."""
        try:
            if language:
                lexer = get_lexer_by_name(language)
            else:
                lexer = guess_lexer(code)
        except Exception:
            lexer = get_lexer_by_name("text")

        formatter = TerminalFormatter(style=self.syntax_theme)
        return highlight(code, lexer, formatter)


class TagIndex:
    """SQLite-индекс тегов для быстрого поиска по заметкам.

    База данных хранится в том же каталоге, что и md-файлы.
    При первом запуске создаётся автоматически.
    Повторно индексируются только изменённые файлы.
    """

    _DB_NAME = ".tag_index.db"

    def __init__(self, notes_path: Path) -> None:
        self.db_path = notes_path / self._DB_NAME
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()

    @staticmethod
    def _color_for_tag(tag: str) -> str:
        """Детерминированно генерирует цвет тега по его имени (HSL → HEX).

        Lightness 55%, saturation 65% — хорошо читается на тёмном и светлом фоне.
        """
        hue = (hash(tag) & 0x7FFF_FFFF) % 360 / 360.0
        r, g, b = colorsys.hls_to_rgb(hue, 0.55, 0.65)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    def _init_schema(self) -> None:
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS file_tags (
                tag       TEXT NOT NULL,
                file_path TEXT NOT NULL,
                source    TEXT NOT NULL,
                PRIMARY KEY (tag, file_path, source)
            );
            CREATE TABLE IF NOT EXISTS file_mtimes (
                file_path TEXT PRIMARY KEY,
                mtime     REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tag_colors (
                tag   TEXT PRIMARY KEY,
                color TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS form_records (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                form_source TEXT NOT NULL,
                catalog     TEXT NOT NULL DEFAULT '',
                data        TEXT NOT NULL,
                created_at  TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_tag         ON file_tags(tag);
            CREATE INDEX IF NOT EXISTS idx_file        ON file_tags(file_path);
            CREATE INDEX IF NOT EXISTS idx_rec_source  ON form_records(form_source);
            CREATE INDEX IF NOT EXISTS idx_rec_catalog ON form_records(catalog);
            CREATE TABLE IF NOT EXISTS favorites (
                file_path TEXT PRIMARY KEY
            );
        """)
        self._conn.commit()

    def rebuild(self, files: List[Path], parser: MarkdownParser) -> None:
        """Инкрементально обновить индекс.

        Пропускает неизменённые файлы, удаляет записи для удалённых.
        """
        current = {str(f) for f in files}
        cached  = {row[0] for row in self._conn.execute("SELECT file_path FROM file_mtimes")}

        for stale in cached - current:
            self._conn.execute("DELETE FROM file_tags   WHERE file_path=?", (stale,))
            self._conn.execute("DELETE FROM file_mtimes WHERE file_path=?", (stale,))

        for fp in files:
            path_str = str(fp)
            try:
                mtime = fp.stat().st_mtime
            except OSError:
                continue

            row = self._conn.execute(
                "SELECT mtime FROM file_mtimes WHERE file_path=?", (path_str,)
            ).fetchone()
            if row and abs(row[0] - mtime) < 0.001:
                continue

            self._conn.execute("DELETE FROM file_tags WHERE file_path=?", (path_str,))
            fm_tags, body_tags = parser.extract_tags_with_source(fp)
            for tag in fm_tags:
                self._conn.execute(
                    "INSERT OR REPLACE INTO file_tags VALUES(?,?,'frontmatter')",
                    (tag, path_str),
                )
            for tag in body_tags:
                self._conn.execute(
                    "INSERT OR REPLACE INTO file_tags VALUES(?,?,'body')",
                    (tag, path_str),
                )
            self._conn.execute(
                "INSERT OR REPLACE INTO file_mtimes VALUES(?,?)", (path_str, mtime)
            )

        # Синхронизируем цвета: добавляем новые теги, удаляем исчезнувшие
        all_tags = {r[0] for r in self._conn.execute("SELECT DISTINCT tag FROM file_tags")}
        colored   = {r[0] for r in self._conn.execute("SELECT tag FROM tag_colors")}
        for tag in all_tags - colored:
            self._conn.execute(
                "INSERT INTO tag_colors VALUES(?,?)", (tag, self._color_for_tag(tag))
            )
        for tag in colored - all_tags:
            self._conn.execute("DELETE FROM tag_colors WHERE tag=?", (tag,))

        self._conn.commit()

    def get_tag_files(self) -> Dict[str, List[Path]]:
        """Вернуть {тег: [Path, ...]} по всем проиндексированным файлам."""
        result: Dict[str, List[Path]] = {}
        for tag, fp in self._conn.execute(
            "SELECT DISTINCT tag, file_path FROM file_tags ORDER BY tag"
        ):
            result.setdefault(tag, []).append(Path(fp))
        return result

    def get_tag_counts(self) -> Dict[str, int]:
        """Вернуть {тег: количество файлов}."""
        return dict(
            self._conn.execute(
                "SELECT tag, COUNT(DISTINCT file_path) FROM file_tags GROUP BY tag"
            )
        )

    def get_tag_colors(self) -> Dict[str, str]:
        """Вернуть {тег: цвет hex} для всех тегов."""
        return dict(self._conn.execute("SELECT tag, color FROM tag_colors"))

    def save_form_record(self, form_source: str, catalog: str, values: Dict) -> int:
        """Сохранить запись формы в БД. Значения сериализуются в JSON.

        Возвращает id вставленной записи.
        """
        cur = self._conn.execute(
            "INSERT INTO form_records(form_source, catalog, data, created_at) "
            "VALUES(?,?,?,?)",
            (
                form_source,
                catalog,
                json.dumps(values, ensure_ascii=False),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        self._conn.commit()
        return cur.lastrowid

    def get_form_records(
        self, form_source: Optional[str] = None, catalog: Optional[str] = None
    ) -> List[Dict]:
        """Вернуть записи форм (опционально фильтруя по источнику/каталогу).

        Каждая запись — dict {id, form_source, catalog, data, created_at},
        где data уже десериализована из JSON.
        """
        query = "SELECT id, form_source, catalog, data, created_at FROM form_records"
        conditions, params = [], []
        if form_source is not None:
            conditions.append("form_source = ?")
            params.append(form_source)
        if catalog is not None:
            conditions.append("catalog = ?")
            params.append(catalog)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY id"

        result = []
        for rid, src, cat, data, created in self._conn.execute(query, params):
            try:
                parsed = json.loads(data)
            except Exception:
                parsed = {}
            result.append({
                "id": rid, "form_source": src, "catalog": cat,
                "data": parsed, "created_at": created,
            })
        return result

    # ---- избранное -----------------------------------------------------------

    def add_favorite(self, file_path: str) -> None:
        self._conn.execute("INSERT OR IGNORE INTO favorites VALUES(?)", (file_path,))
        self._conn.commit()

    def remove_favorite(self, file_path: str) -> None:
        self._conn.execute("DELETE FROM favorites WHERE file_path=?", (file_path,))
        self._conn.commit()

    def toggle_favorite(self, file_path: str) -> bool:
        if self.is_favorite(file_path):
            self.remove_favorite(file_path)
            return False
        self.add_favorite(file_path)
        return True

    def is_favorite(self, file_path: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM favorites WHERE file_path=?", (file_path,)
        ).fetchone()
        return row is not None

    def get_favorites(self) -> List[str]:
        return [
            r[0] for r in self._conn.execute("SELECT file_path FROM favorites ORDER BY file_path")
        ]

    def close(self) -> None:
        self._conn.close()


def parse_form_definition(content: str) -> Optional[Dict]:
    """Проверить является ли заметка формой ввода.

    Возвращает dict {catalog, destination, fields} если первый ключ frontmatter —
    type: form, иначе None.

    destination: "note" — сохранять как md-файл (по умолчанию), "database" — в БД.
    """
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    try:
        fm = yaml.safe_load(content[3:end]) or {}
        if not isinstance(fm, dict):
            return None
        if next(iter(fm), None) != "type" or fm.get("type") != "form":
            return None
        destination = str(fm.get("destination", "note")).strip().lower()
        if destination not in ("note", "database"):
            destination = "note"
        return {
            "catalog": str(fm.get("catalog", "")).strip(),
            "destination": destination,
            "fields": fm.get("fields") or [],
        }
    except Exception:
        return None


class QueryEngine:
    """Движок псевдо-SQL запросов к заметкам (frontmatter) и записям форм в БД.

    Аналог Obsidian Dataview. Синтаксис:

        FROM notes|database[/<фильтр>]
        WHERE <field> <op> <value> [AND ...]
        GROUP BY <field1>, <field2>
        HAVING <агрегат|field> <op> <value> [AND ...]
        SELECT <field1>, COUNT(*), SUM(<field>) | *
        ORDER BY <field|агрегат> [ASC|DESC]
        LIMIT <n>

    Операторы: =, !=, >, <, >=, <=, CONTAINS, LIKE.
    Агрегатные функции: COUNT, SUM, MIN, MAX, AVG.
    При наличии GROUP BY (или агрегата в SELECT) строки группируются и
    для каждой группы вычисляются агрегаты; обычные поля в SELECT берутся
    из группирующих полей. ORDER BY в таком случае работает по подписи
    колонки (например, ORDER BY SUM(count) DESC).
    HAVING фильтрует уже сгруппированные строки по агрегатам или
    группирующим полям (например, HAVING COUNT(*) > 1).
    Для notes неявные поля: file (имя), path (относительный путь).
    Для database неявные поля: id, catalog, source, created_at.
    """

    _KEYWORDS = ["SELECT", "FROM", "WHERE", "GROUP BY", "HAVING",
                 "ORDER BY", "LIMIT"]
    _COND_RE = re.compile(
        r"^(.+?)\s*(>=|<=|!=|=|>|<|\bCONTAINS\b|\bLIKE\b)\s*(.+)$", re.IGNORECASE
    )
    _AGG_RE = re.compile(r"^(SUM|MIN|MAX|AVG|COUNT)\s*\(\s*(.+?)\s*\)$", re.IGNORECASE)

    def __init__(self, file_system: "FileSystem", parser: "MarkdownParser",
                 tag_index: "TagIndex") -> None:
        self.fs = file_system
        self.parser = parser
        self.tag_index = tag_index

    # ---- публичный API -----------------------------------------------------

    def execute(self, query_text: str) -> Tuple[List[str], List[Dict]]:
        """Выполнить запрос. Вернуть (колонки, строки)."""
        q = self._parse_query(query_text)
        if q["source"] == "database":
            rows = self._rows_from_db(q["filter"])
        else:
            rows = self._rows_from_notes(q["filter"])

        rows = [r for r in rows if self._match(r, q["where"])]

        select = q["select"]
        group_by = q["group_by"]
        having = q["having"]
        has_agg = bool(select) and any(self._AGG_RE.match(s) for s in select)
        if group_by or has_agg:
            columns, rows = self._aggregate(rows, select, group_by, having)
            if having:
                rows = [r for r in rows if self._match(r, having)]
        else:
            columns = select or self._infer_columns(rows)

        if q["order"]:
            field, desc = q["order"]
            rows.sort(key=lambda r: self._sort_key(r.get(field)), reverse=desc)
        if q["limit"] is not None:
            rows = rows[: q["limit"]]

        projected = [{c: self._fmt(r.get(c)) for c in columns} for r in rows]
        return columns, projected

    # ---- группировка и агрегаты -------------------------------------------

    def _aggregate(self, rows: List[Dict], select: Optional[List[str]],
                   group_by: Optional[List[str]],
                   having: Optional[List[Tuple]] = None
                   ) -> Tuple[List[str], List[Dict]]:
        """Сгруппировать строки и вычислить агрегаты. Вернуть (колонки, строки).

        Агрегаты, упомянутые только в HAVING, тоже вычисляются (как скрытые
        колонки) — чтобы фильтрация работала, даже если их нет в SELECT.
        """
        keys = group_by or []
        # SELECT по умолчанию: группирующие поля + COUNT(*)
        if not select:
            select = list(keys) + ["COUNT(*)"]

        # Разобрать SELECT в спецификации колонок
        specs: List[Tuple] = []  # (label, kind, func, arg)
        for item in select:
            m = self._AGG_RE.match(item)
            if m:
                specs.append((item, "agg", m.group(1).upper(), m.group(2).strip()))
            else:
                specs.append((item, "field", None, item))

        # Дополнительные агрегаты, нужные только для HAVING
        spec_labels = {s[0] for s in specs}
        extra: List[Tuple] = []
        for field, _op, _val in (having or []):
            m = self._AGG_RE.match(field)
            if m and field not in spec_labels and field not in {e[0] for e in extra}:
                extra.append((field, "agg", m.group(1).upper(), m.group(2).strip()))

        # Сгруппировать строки, сохраняя порядок появления групп
        groups: Dict[Tuple, List[Dict]] = {}
        order_of_keys: List[Tuple] = []
        for r in rows:
            key = tuple(self._hashable(r.get(f)) for f in keys)
            if key not in groups:
                groups[key] = []
                order_of_keys.append(key)
            groups[key].append(r)
        # Без GROUP BY с агрегатами — одна группа из всех строк
        if not keys:
            order_of_keys = [()]
            groups = {(): rows}

        result: List[Dict] = []
        for key in order_of_keys:
            grp = groups[key]
            out: Dict = {}
            # Группирующие поля доступны для HAVING по их именам
            for f in keys:
                out[f] = grp[0].get(f) if grp else None
            for label, kind, func, arg in specs + extra:
                if kind == "agg":
                    out[label] = self._compute_agg(func, arg, grp)
                else:
                    out[label] = grp[0].get(arg) if grp else None
            result.append(out)
        return [s[0] for s in specs], result

    def _compute_agg(self, func: str, arg: str, group: List[Dict]):
        if func == "COUNT":
            if arg == "*":
                return len(group)
            return sum(1 for r in group if r.get(arg) is not None)
        values = [r.get(arg) for r in group]
        if func in ("SUM", "AVG"):
            nums = self._numeric(values)
            if func == "SUM":
                return sum(nums)
            return round(sum(nums) / len(nums), 2) if nums else None
        # MIN / MAX — числа, либо лексикографически (даты/строки)
        non_null = [v for v in values if v is not None]
        if not non_null:
            return None
        nums = self._numeric(non_null)
        if len(nums) == len(non_null):
            return min(nums) if func == "MIN" else max(nums)
        chooser = min if func == "MIN" else max
        return chooser(non_null, key=self._sort_key)

    @staticmethod
    def _numeric(values) -> List[float]:
        nums: List[float] = []
        for v in values:
            if isinstance(v, bool) or v is None:
                continue
            if isinstance(v, (int, float)):
                nums.append(v)
            else:
                try:
                    nums.append(float(v))
                except (ValueError, TypeError):
                    pass
        return nums

    @staticmethod
    def _hashable(v):
        if isinstance(v, list):
            return tuple(v)
        if isinstance(v, dict):
            return str(sorted(v.items()))
        return v

    # ---- парсинг запроса ---------------------------------------------------

    def _parse_query(self, text: str) -> Dict:
        clauses = self._split_clauses(text)
        # FROM
        source, filt = "notes", None
        if "FROM" in clauses:
            raw = clauses["FROM"].strip()
            if "/" in raw:
                source, filt = raw.split("/", 1)
                source, filt = source.strip().lower(), filt.strip()
            else:
                source = raw.lower()
            if source not in ("notes", "database"):
                source = "notes"
        # SELECT
        select = None
        if "SELECT" in clauses:
            sc = clauses["SELECT"].strip()
            if sc and sc != "*":
                select = [c.strip() for c in sc.split(",") if c.strip()]
        # WHERE
        where = self._parse_conditions(clauses.get("WHERE"))
        # GROUP BY
        group_by = None
        if "GROUP BY" in clauses:
            gb = [c.strip() for c in clauses["GROUP BY"].split(",") if c.strip()]
            group_by = gb or None
        # HAVING
        having = self._parse_conditions(clauses.get("HAVING"))
        # ORDER BY
        order = None
        if "ORDER BY" in clauses:
            ob = clauses["ORDER BY"].split()
            if ob:
                desc = len(ob) > 1 and ob[1].upper() == "DESC"
                order = (ob[0], desc)
        # LIMIT
        limit = None
        if "LIMIT" in clauses:
            try:
                limit = int(clauses["LIMIT"].strip())
            except ValueError:
                limit = None
        return {"source": source, "filter": filt, "select": select,
                "where": where, "group_by": group_by, "having": having,
                "order": order, "limit": limit}

    def _parse_conditions(self, text: Optional[str]) -> List[Tuple]:
        """Разобрать условия WHERE/HAVING в список (field, op, value)."""
        conds: List[Tuple] = []
        if not text:
            return conds
        for part in re.split(r"\s+AND\s+", text, flags=re.IGNORECASE):
            m = self._COND_RE.match(part.strip())
            if m:
                conds.append((m.group(1).strip(),
                              m.group(2).upper().strip(),
                              self._coerce(m.group(3).strip())))
        return conds

    def _split_clauses(self, text: str) -> Dict[str, str]:
        """Разбить текст запроса на части по ключевым словам."""
        positions = []
        for kw in self._KEYWORDS:
            for m in re.finditer(rf"\b{kw}\b", text, re.IGNORECASE):
                positions.append((m.start(), m.end(), kw))
        positions.sort()
        clauses: Dict[str, str] = {}
        for i, (start, end, kw) in enumerate(positions):
            nxt = positions[i + 1][0] if i + 1 < len(positions) else len(text)
            clauses[kw] = text[end:nxt].strip()
        return clauses

    # ---- источники данных --------------------------------------------------

    def _rows_from_notes(self, subfolder: Optional[str]) -> List[Dict]:
        rows: List[Dict] = []
        root = self.fs.root_path
        base = (root / subfolder) if subfolder else root
        for path in self.fs.get_md_files():
            if subfolder and base not in path.parents and path.parent != base:
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue
            fm, _ = self.parser._parse_frontmatter(content)
            if not isinstance(fm, dict):
                fm = {}
            row = dict(fm)
            row.setdefault("file", path.stem)
            row.setdefault("path", str(path.relative_to(root)))
            rows.append(row)
        return rows

    def _rows_from_db(self, catalog: Optional[str]) -> List[Dict]:
        rows: List[Dict] = []
        for rec in self.tag_index.get_form_records(catalog=catalog or None):
            row = dict(rec["data"]) if isinstance(rec["data"], dict) else {}
            row["id"] = rec["id"]
            row["catalog"] = rec["catalog"]
            row["created_at"] = rec["created_at"]
            try:
                row["source"] = Path(rec["form_source"]).stem
            except Exception:
                row["source"] = rec["form_source"]
            rows.append(row)
        return rows

    # ---- фильтрация и сортировка -------------------------------------------

    def _match(self, row: Dict, conditions: List[Tuple]) -> bool:
        for field, op, expected in conditions:
            actual = row.get(field)
            if not self._compare(actual, op, expected):
                return False
        return True

    @staticmethod
    def _compare(actual, op: str, expected) -> bool:
        try:
            if op == "=":
                return actual == expected
            if op == "!=":
                return actual != expected
            if op in (">", "<", ">=", "<="):
                if actual is None:
                    return False
                a, e = float(actual), float(expected)
                return {">": a > e, "<": a < e, ">=": a >= e, "<=": a <= e}[op]
            if op == "CONTAINS":
                if isinstance(actual, (list, tuple, set)):
                    return expected in actual or str(expected) in [str(x) for x in actual]
                return str(expected).lower() in str(actual).lower()
            if op == "LIKE":
                return str(expected).lower() in str(actual).lower()
        except (ValueError, TypeError):
            return False
        return False

    @staticmethod
    def _sort_key(value):
        if value is None:
            return (2, "")
        if isinstance(value, bool):
            return (1, value)
        if isinstance(value, (int, float)):
            return (0, value)
        return (1, str(value).lower())

    # ---- утилиты -----------------------------------------------------------

    @staticmethod
    def _coerce(token: str):
        """Преобразовать строковый литерал в значение нужного типа."""
        t = token.strip()
        if len(t) >= 2 and t[0] in "\"'" and t[-1] == t[0]:
            return t[1:-1]
        low = t.lower()
        if low in ("true", "yes"):
            return True
        if low in ("false", "no"):
            return False
        try:
            return int(t)
        except ValueError:
            pass
        try:
            return float(t)
        except ValueError:
            pass
        return t

    @staticmethod
    def _infer_columns(rows: List[Dict]) -> List[str]:
        cols: List[str] = []
        for r in rows:
            for k in r:
                if k not in cols:
                    cols.append(k)
        return cols

    @staticmethod
    def _fmt(value) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "✓" if value else "✗"
        if isinstance(value, (list, tuple)):
            return ", ".join(str(x) for x in value)
        return str(value)


def get_available_syntax_themes() -> List[str]:
    """Получить список доступных тем подсветки."""
    return list(get_all_styles())


if __name__ == "__main__":
    # Тестирование
    config = Config.load()
    print(f"Notes path: {config.notes_path} -> {config.resolve_notes_path()}")
    print(f"Hotkeys: {config.hotkeys}")

    fs = FileSystem(str(config.resolve_notes_path()))
    tree = fs.get_tree()
    print(f"Root: {tree.name}, children: {len(tree.children)}")

    parser = MarkdownParser()
    test_md = """
# Тест

Это **жирный** и *курсивный* текст.

```python
def hello():
    print("Hello, World!")
```

#тег1 #тег2
"""
    print(parser.extract_tags(test_md))
