"""
Модуль для работы с файловой системой и парсинга Markdown.
"""
import colorsys
import json
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime

import yaml
from markdown import Markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter
from pygments.styles import get_all_styles

# LadybugDB import
try:
    import ladybug
    from ladybug import Connection
except ImportError:
    # Fallback for development - in production, ladybug should be installed
    ladybug = None
    Connection = None


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
        конг-файла, а не текущей рабочей директории — чтобы запуск из любого
        места давал один и тот же каталог заметок.
        """
        p = Path(self.notes_path).expanduser()
        if not p.is_absolute():
            base = Path(self.config_path).expanduser().resolve().parent
            p = base / p
        return p.resolve()

    def save_theme(self, theme: str) -> None:
        """Обновить только app_theme в конг-файле, сохранив остальное без изменений."""
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

    def save_display_value(self, key: str, value) -> None:
        """Обновить значение в display-секции конфига, сохранив остальное без изменений."""
        self.display[key] = value
        if not os.path.exists(self.config_path):
            return
        with open(self.config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        display_idx = None
        for i, line in enumerate(lines):
            if line.strip().startswith("display:"):
                display_idx = i
                break
        if display_idx is None:
            return

        display_indent = len(lines[display_idx]) - len(lines[display_idx].lstrip())
        item_indent = display_indent + 2

        key_line = None
        last_item_idx = display_idx
        for i in range(display_idx + 1, len(lines)):
            line = lines[i]
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= display_indent:
                break
            last_item_idx = i
            if stripped.startswith(f"{key}:"):
                key_line = i
                break

        if key_line is not None:
            lines[key_line] = re.sub(
                rf'^(\s*{key}:\s*).+$', f'\\g<1>{value}', lines[key_line]
            )
        else:
            lines.insert(last_item_idx + 1, " " * item_indent + f'{key}: {value}\n')

        with open(self.config_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

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
                "sidebar_width": 30,
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

    def extract_internal_links(self, content: str) -> Set[str]:
        """Извлечь внутренние ссылки на другие заметки (не URL/почта)."""
        links: Set[str] = set()
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', content):
            url = match.group(2)
            if not re.match(r'^(https?://|mailto:)', url):
                links.add(url)
        return links

    def extract_internal_links_from_file(self, path: Path) -> Set[str]:
        """Извлечь внутренние ссылки из файла."""
        try:
            content = path.read_text(encoding="utf-8")
            return self.extract_internal_links(content)
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
    """LadybugDB-индекс тегов для быстрого поиска по заметкам.

    База данных хранится в том же каталоге, что и md-файлы.
    При первом запуске создаётся автоматически.
    Повторно индексируются только изменённые файлы.
    """

    _DB_NAME = ".ladybug_index.lbug"

    def __init__(self, notes_path: Path) -> None:
        self.notes_dir = notes_path
        # Initialize LadybugDB connection instead of sqlite3
        self.db_path = self.notes_dir / self._DB_NAME
        if ladybug is None:
            raise ImportError("LadybugDB is not installed. Please install ladybug>=0.1.0")
        # Create database and connection
        self.database = ladybug.Database(str(self.db_path))
        self.connection = ladybug.Connection(self.database)
        self._initialize_schema()

    def close(self) -> None:
        """Закрыть соединение с LadybugDB."""
        if hasattr(self, "connection") and self.connection:
            self.connection.close()
        if hasattr(self, "database") and self.database:
            self.database.close()

    def _initialize_schema(self):
        """Create node and relationship tables if they don't exist"""
        # Node tables
        self.connection.execute("""
            CREATE NODE TABLE IF NOT EXISTS Tag (
                name STRING PRIMARY KEY,
                color STRING
            )
        """)
        
        self.connection.execute("""
            CREATE NODE TABLE IF NOT EXISTS File (
                path STRING PRIMARY KEY,
                mtime DOUBLE
            )
        """)
        
        self.connection.execute("""
            CREATE NODE TABLE IF NOT EXISTS FormRecord (
                id INT64 PRIMARY KEY,
                source STRING,
                catalog STRING,
                created_at STRING,
                data JSON
            )
        """)
        
        self.connection.execute("""
            CREATE NODE TABLE IF NOT EXISTS Favorite (
                file_path STRING PRIMARY KEY
            )
        """)
        
        # Relationship tables
        self.connection.execute("""
            CREATE REL TABLE IF NOT EXISTS HAS_TAG_FRONTMatter (
                FROM File TO Tag
            )
        """)
        
        self.connection.execute("""
            CREATE REL TABLE IF NOT EXISTS HAS_TAG_BODY (
                FROM File TO Tag
            )
        """)
        
        self.connection.execute("""
            CREATE REL TABLE IF NOT EXISTS RECORD_FROM_FILE (
                FROM FormRecord TO File
            )
        """)
        
        self.connection.execute("""
            CREATE REL TABLE IF NOT EXISTS LINKS_TO (
                FROM File TO File
            )
        """)

    @staticmethod
    def _color_for_tag(tag: str) -> str:
        """Детерминированно генерирует цвет тега по его имени (HSL → HEX).

        Lightness 55%, saturation 65% — хорошо читается на тёмном и светлом фоне.
        """
        hue = (hash(tag) & 0x7FFF_FFFF) % 360 / 360.0
        r, g, b = colorsys.hls_to_rgb(hue, 0.55, 0.65)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

    def rebuild(self, files: List[Path], parser: MarkdownParser) -> None:
        """Инкрементально обновить индекс.

        Пропускает неизменённые файлы, удаляет записи для удалённые.
        """
        # Convert files to set of strings for easier comparison
        markdown_files = set(str(f) for f in files)
        
        # Get currently indexed files from LadybugDB
        indexed_files = {}
        try:
            result = self.connection.execute("MATCH (f:File) RETURN f.path AS path, f.mtime AS mtime")
            # Process the QueryResult
            while result.has_next():
                row = result.get_next()
                indexed_files[row[0]] = row[1]
        except Exception:
            # If no File table exists yet, treat all as new
            indexed_files = {}
        
        # Determine files to process
        files_to_add = markdown_files - set(indexed_files.keys())
        files_to_delete = set(indexed_files.keys()) - markdown_files
        files_to_update = set()
        
        # Check for modified files
        for file_path in markdown_files & set(indexed_files.keys()):
            current_mtime = Path(file_path).stat().st_mtime
            if current_mtime > indexed_files[file_path]:
                files_to_update.add(file_path)
        
        # Process deletions
        for file_path in files_to_delete:
            self._remove_file_from_index(file_path)
        
        # Process additions and updates
        for file_path in files_to_add | files_to_update:
            self._add_or_update_file_in_index(file_path, Path(file_path).stat().st_mtime, parser)
        
        # Cleanup orphaned tags
        self._cleanup_orphaned_tags()
    
    def _remove_file_from_index(self, file_path: str) -> None:
        """Remove a file and its associated data from the index"""
        # Delete file node and all its relationships
        self.connection.execute("""
            MATCH (f:File {path: $path})
            DETACH DELETE f
        """, {"path": file_path})
        
        # Note: We do NOT delete associated form records or favorites here to match original behavior
        # Form records and favorites are preserved when a file is deleted from the index
    
    def _add_or_update_file_in_index(self, file_path: str, mtime: float, parser: MarkdownParser) -> None:
        """Add or update a file in the index and process its tags"""
        # Upsert file node
        self.connection.execute("""
            MERGE (f:File {path: $path})
            SET f.mtime = $mtime
        """, {"path": file_path, "mtime": mtime})
        
        # Remove existing tag and form record relationships for this file
        self.connection.execute("""
            MATCH (f:File {path: $file_path})-[r:HAS_TAG_FRONTMatter]->()
            DELETE r
        """, {"file_path": file_path})
        self.connection.execute("""
            MATCH (f:File {path: $file_path})-[r:HAS_TAG_BODY]->()
            DELETE r
        """, {"file_path": file_path})
        self.connection.execute("""
            MATCH (f:File {path: $file_path})-[r:RECORD_FROM_FILE]->()
            DELETE r
        """, {"file_path": file_path})
        
        # Parse file to extract tags and form data
        tags_frontmatter, tags_body, form_data = self._parse_file_for_indexing(file_path, parser)
        
        # Process frontmatter tags
        for tag_name in tags_frontmatter:
            color = self._generate_deterministic_color(tag_name)
            # Ensure tag node exists
            self.connection.execute("""
                MERGE (t:Tag {name: $tag_name})
                ON CREATE SET t.color = $color
            """, {
                "tag_name": tag_name,
                "color": color,
            })
            # Ensure relationship exists
            self.connection.execute("""
                MATCH (f:File {path: $file_path})
                MATCH (t:Tag {name: $tag_name})
                MERGE (f)-[r:HAS_TAG_FRONTMatter]->(t)
            """, {
                "file_path": file_path,
                "tag_name": tag_name,
            })
        
        # Process body tags
        for tag_name in tags_body:
            color = self._generate_deterministic_color(tag_name)
            # Ensure tag node exists
            self.connection.execute("""
                MERGE (t:Tag {name: $tag_name})
                ON CREATE SET t.color = $color
            """, {
                "tag_name": tag_name,
                "color": color,
            })
            # Ensure relationship exists
            self.connection.execute("""
                MATCH (f:File {path: $file_path})
                MATCH (t:Tag {name: $tag_name})
                MERGE (f)-[r:HAS_TAG_BODY]->(t)
            """, {
                "file_path": file_path,
                "tag_name": tag_name,
            })
        
        # Process form record if present
        if form_data:
            self._upsert_form_record(file_path, form_data)
    
    def _cleanup_orphaned_tags(self) -> None:
        """Remove tags that are no longer associated with any files"""
        self.connection.execute("""
            MATCH (t:Tag)
            WHERE NOT ((t)<-[:HAS_TAG_FRONTMatter]-() OR (t)<-[:HAS_TAG_BODY]-())
            DETACH DELETE t
        """)
    
    def _parse_file_for_indexing(self, file_path: str, parser: MarkdownParser) -> Tuple[Set[str], Set[str], Optional[Dict]]:
        """Parse a markdown file to extract frontmatter tags, body tags, and form data"""
        path_obj = Path(file_path)
        
        # Extract tags with source (frontmatter vs body) using the provided parser
        fm_tags, body_tags = parser.extract_tags_with_source(path_obj)
        
        # Check if this is a form record
        try:
            content = path_obj.read_text(encoding="utf-8")
            form_def = parse_form_definition(content)
            form_data = None
            if form_def and form_def.get("destination") == "database":
                # Extract form values from the content
                # This is simplified - in practice we'd need to parse the actual form values
                # For now, we'll create a basic form record
                form_data = {
                    "catalog": form_def.get("catalog", ""),
                    "data": {}  # Would be populated from actual form fields
                }
        except Exception:
            form_data = None
            
        return fm_tags, body_tags, form_data
    
    def _generate_deterministic_color(self, tag_name: str) -> str:
        """Generate deterministic HSL->HEX color for a tag"""
        # Use the same implementation as the original TagIndex
        hue = (hash(tag_name) & 0x7FFF_FFFF) % 360 / 360.0
        r, g, b = colorsys.hls_to_rgb(hue, 0.55, 0.65)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    
    def _upsert_form_record(self, file_path: str, form_data: Dict) -> None:
        """Insert or update a form record in the database"""
        # Generate deterministic ID based on file path and form data
        form_id = hash((file_path, json.dumps(form_data, sort_keys=True))) & ((1 << 63) - 1)
        
        self.connection.execute("""
            MERGE (fr:FormRecord {id: $form_id})
            ON CREATE SET 
                fr.source = $source,
                fr.catalog = $catalog,
                fr.created_at = $created_at,
                fr.data = $data
            ON MATCH SET
                fr.source = $source,
                fr.catalog = $catalog,
                fr.created_at = $created_at,
                fr.data = $data
        """, {
            "form_id": form_id,
            "source": file_path,
            "catalog": form_data.get("catalog", ""),
            "created_at": form_data.get("created_at", ""),
            "data": json.dumps(form_data.get("data", {}))
        })
        
        # Create relationship to file
        self.connection.execute("""
            MATCH (fr:FormRecord {id: $form_id})
            MATCH (f:File {path: $file_path})
            MERGE (fr)-[r:RECORD_FROM_FILE]->(f)
        """, {
            "form_id": form_id,
            "file_path": file_path
        })

    def rebuild_note_links(self, files: List[Path], parser: MarkdownParser) -> None:
        """Инкрементально обновить связи между заметками.

        Использует те же file_mtimes для определения изменённых файлов.
        Удаляет связи для удалённых файлов.
        """
        current = {str(f) for f in files}
        cached = {}
        try:
            result = self.connection.execute(
                "MATCH (f:File) RETURN f.path AS path, f.mtime AS mtime"
            )
            while result.has_next():
                row = result.get_next()
                cached[row[0]] = row[1]
        except Exception:
            cached = {}

        cached_paths = set(cached.keys())

        # Удалить связи для удалённых файлов (как source, так и target)
        for stale in cached_paths - current:
            self.connection.execute("""
                MATCH (f:File {path: $path})-[r:LINKS_TO]->()
                DELETE r
            """, {"path": stale})
            self.connection.execute("""
                MATCH ()-[r:LINKS_TO]->(f:File {path: $path})
                DELETE r
            """, {"path": stale})

        for fp in files:
            path_str = str(fp)
            try:
                mtime = fp.stat().st_mtime
            except OSError:
                continue

            cached_mtime = cached.get(path_str)
            if cached_mtime and abs(cached_mtime - mtime) < 0.001:
                continue

            # Файл изменился — перестраиваем его связи
            self.connection.execute("""
                MATCH (f:File {path: $path})-[r:LINKS_TO]->()
                DELETE r
            """, {"path": path_str})

            raw_links = parser.extract_internal_links_from_file(fp)
            for link in raw_links:
                target = Path(link)
                if not target.is_absolute():
                    target = (fp.parent / target).resolve()
                else:
                    target = target.resolve()
                if target.exists() and target.is_file():
                    self.connection.execute("""
                        MATCH (f:File {path: $src})
                        MATCH (t:File {path: $tgt})
                        MERGE (f)-[r:LINKS_TO]->(t)
                    """, {"src": path_str, "tgt": str(target)})

    def get_note_links(self) -> Dict[Path, Set[Path]]:
        """Вернуть {source: {target, ...}} по всем связям."""
        result: Dict[Path, Set[Path]] = {}
        try:
            query_result = self.connection.execute("""
                MATCH (f:File)-[:LINKS_TO]->(t:File)
                RETURN f.path AS src, t.path AS tgt
            """)
            while query_result.has_next():
                row = query_result.get_next()
                result.setdefault(Path(row[0]), set()).add(Path(row[1]))
        except Exception:
            pass
        return result

    def get_tag_files(self) -> Dict[str, List[Path]]:
        """Вернуть {тег: [Path, ...]} по всем проиндексированным файлам."""
        try:
            # Query for all tag-file relationships
            result = self.connection.execute("""
                MATCH (t:Tag)<-[:HAS_TAG_FRONTMatter|:HAS_TAG_BODY]-(f:File)
                RETURN t.name AS tag, f.path AS path
            """)
            
            # Group by tag
            tag_files: Dict[str, List[Path]] = {}
            while result.has_next():
                row = result.get_next()
                tag = row[0]
                path = Path(row[1])
                if tag not in tag_files:
                    tag_files[tag] = []
                tag_files[tag].append(path)
            
            return tag_files
        except Exception:
            return {}
    
    def get_tag_counts(self) -> Dict[str, int]:
        """Вернуть {тег: количество файлов}."""
        try:
            result = self.connection.execute("""
                MATCH (t:Tag)<-[:HAS_TAG_FRONTMatter|:HAS_TAG_BODY]-(f:File)
                RETURN t.name AS tag, COUNT(DISTINCT f) AS count
            """)
            
            # Process the QueryResult
            counts = {}
            while result.has_next():
                row = result.get_next()
                counts[row[0]] = row[1]
            return counts
        except Exception:
            return {}
    
    def get_tag_colors(self) -> Dict[str, str]:
        """Вернуть {тег: цвет hex} для всех тегов."""
        try:
            result = self.connection.execute("""
                MATCH (t:Tag)
                RETURN t.name AS tag, t.color AS color
            """)
            
            # Process the QueryResult
            colors = {}
            while result.has_next():
                row = result.get_next()
                colors[row[0]] = row[1]
            return colors
        except Exception:
            return {}
    
    def save_form_record(self, form_source: str, catalog: str, values: Dict) -> int:
        """Сохранить запись формы в БД. Значения сериализуются в JSON.

        Возвращает id вставленной записи.
        """
        # Generate deterministic ID based on form source and values
        form_id = hash((form_source, json.dumps(values, sort_keys=True))) & ((1 << 63) - 1)
        
        self.connection.execute("""
            MERGE (fr:FormRecord {id: $form_id})
            ON CREATE SET 
                fr.source = $source,
                fr.catalog = $catalog,
                fr.created_at = $created_at,
                fr.data = $data
            ON MATCH SET
                fr.source = $source,
                fr.catalog = $catalog,
                fr.created_at = $created_at,
                fr.data = $data
        """, {
            "form_id": form_id,
            "source": form_source,
            "catalog": catalog,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "data": json.dumps(values, ensure_ascii=False)
        })
        
        return form_id

    def get_form_records(
        self, form_source: Optional[str] = None, catalog: Optional[str] = None
    ) -> List[Dict]:
        """Вернуть записи форм (опционально фильтруя по источнику/каталогу).

        Каждая запись — dict {id, form_source, catalog, data, created_at},
        где data уже десериализована из JSON.
        """
        try:
            query = "MATCH (fr:FormRecord)"
            params = {}
            
            conditions = []
            if form_source is not None:
                conditions.append("fr.source = $form_source")
                params["form_source"] = form_source
            if catalog is not None:
                conditions.append("fr.catalog = $catalog")
                params["catalog"] = catalog
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " RETURN fr.id AS id, fr.source AS source, fr.catalog AS catalog, fr.created_at AS created_at, fr.data AS data"
            
            result = self.connection.execute(query, params)
            
            # Process the QueryResult
            records = []
            while result.has_next():
                row = result.get_next()
                records.append({
                    "id": row[0],
                    "source": row[1],
                    "catalog": row[2],
                    "created_at": row[3],
                    "data": json.loads(row[4]) if row[4] else {}
                })
            
            return records
        except Exception:
            return []

    # ---- избранное -----------------------------------------------------------

    def add_favorite(self, file_path: Union[str, Path]) -> None:
        """Добавить файл в избранное"""
        try:
            self.connection.execute("""
                MERGE (fav:Favorite {file_path: $file_path})
            """, {"file_path": str(file_path)})
        except Exception:
            pass  # Fail silently to match existing behavior

    def remove_favorite(self, file_path: Union[str, Path]) -> None:
        """Удалить файл из избранного"""
        try:
            self.connection.execute("""
                MATCH (fav:Favorite {file_path: $file_path})
                DELETE fav
            """, {"file_path": str(file_path)})
        except Exception:
            pass  # Fail silently to match existing behavior

    def toggle_favorite(self, file_path: Union[str, Path]) -> bool:
        """Переключить статус избранного для файла"""
        if self.is_favorite(file_path):
            self.remove_favorite(file_path)
            return False
        self.add_favorite(file_path)
        return True

    def is_favorite(self, file_path: Union[str, Path]) -> bool:
        """Проверить, отмечен ли файл как избранный"""
        try:
            result = self.connection.execute("""
                MATCH (fav:Favorite {file_path: $file_path})
                RETURN count(fav) > 0 AS is_fav
            """, {"file_path": str(file_path)})
            
            # Process the QueryResult
            if result.has_next():
                row = result.get_next()
                return row[0]
            return False
        except Exception:
            return False

    def get_favorites(self) -> List[str]:
        """Получить все избранные файлы"""
        try:
            result = self.connection.execute("""
                MATCH (fav:Favorite)
                RETURN fav.file_path AS path
            """)
            
            # Process the QueryResult
            favorites = []
            while result.has_next():
                row = result.get_next()
                favorites.append(row[0])
            return favorites
        except Exception:
            return []

    def run_read_cypher(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a read-only Cypher query and return the results as a list of dictionaries.
        Each dictionary represents a row, with keys being the column names (or variable names in the RETURN clause).

        Warning: This method does not validate that the query is read-only. It is the caller's responsibility
        to ensure that the query does not modify the database. Write queries may lead to undefined behavior
        and are not supported.

        Args:
            query: The Cypher query to execute.
            parameters: Optional dictionary of parameters to pass to the query.

        Returns:
            A list of dictionaries, each representing a row in the result.
        """
        if parameters is None:
            parameters = {}
        result = self.connection.execute(query, parameters)
        columns = result.keys()
        rows = []
        while result.has_next():
            row = result.get_next()
            rows.append(dict(zip(columns, row)))
        return rows


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


def parse_base_definition(content: str) -> Optional[Dict]:
    """Проверить является ли заметка базовой выборкой.

    Возвращает dict {query, filters} если type == base, иначе None.

    filters — список dict'ов вида {name: [type, ...options]}.
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
        if fm.get("type") != "base":
            return None
        raw_filters = fm.get("filters") or []
        filters = []
        for item in raw_filters:
            if isinstance(item, dict):
                filters.append(item)
        return {
            "query": str(fm.get("query", "")).strip(),
            "filters": filters,
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