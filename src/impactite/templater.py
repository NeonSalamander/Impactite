"""
Движок шаблонизации на основе Jinja2.

Шаблоны — обычные Markdown-файлы со вставками вида ``{{ variable }}``
и Jinja2-конструкциями (``{% if %}``, ``{% for %}`` и т.д.).

Поддерживаемые переменные:
  {{title}}               Название заметки (имя файла без расширения)
  {{date}}                Сегодняшняя дата (YYYY-MM-DD)
  {{time}}                Текущее время (HH:mm)
  {{creation-date}}       Дата создания файла (при первом рендере = сегодня)
  {{modification-date}}   Дата последнего изменения (при рендере = сегодня)
  {{author}}              Имя автора (из конфига, по умолчанию "")
  {{file-name}}           Имя файла без расширения
  {{file-path}}           Полный путь к файлу
  {{folder}}              Имя папки, в которой лежит файл
  {{random}}              Случайное число от 0 до 99999
  {{cursor}}              Пустая строка (маркер для позиции курсора)
  {{todo}}                Список задач (пока пустой список)
  {{task:pending}}        Список нерешённых задач (пока пустой)
  {{weekday}}             День недели (1-7, пн=1)
  {{week-number}}         Номер недели в году (1-53)
  {{month-name}}          Название месяца (на английском)
  {{year}}                Год (2026)
  {{month}}               Месяц (06)
  {{day}}                 День (10)
  {{uptime}}              Время с момента создания (пока None)

Поддерживаемые форматтеры Jinja2 (фильтры):
  {{date:YYYY-MM-DD}}     Дата с кастомным форматом
  {{time:HH:mm}}          Время с кастомным форматом

Шаблоны хранятся в папке ``templates/`` внутри каталога заметок.
Вложенные папки группируют шаблоны по категориям.
"""

import os
import random
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional


# ---- нативные функции для Jinja2 окружения (доступны из шаблонов) ----------

def _format_date(fmt: str = "%Y-%m-%d") -> str:
    """Вернуть сегодняшнюю дату в заданном формате strftime."""
    return date.today().strftime(fmt)


def _format_time(fmt: str = "%H:%M") -> str:
    """Вернуть текущее время в заданном формате strftime."""
    return datetime.now().strftime(fmt)


def _random_int() -> int:
    """Вернуть случайное число 0–99999."""
    return random.randint(0, 99999)


_CONVERTIBLE = {
    "YYYY": "%Y",
    "YY": "%y",
    "MM": "%m",
    "DD": "%d",
    "HH": "%H",
    "mm": "%M",
    "ss": "%S",
    "MMMM": "%B",
    "MMM": "%b",
    "Do": "%d",  # day ordinal
}


def _convert_readable_format(fmt: str) -> str:
    """Конвертировать читаемый формат (DD.MM.YYYY) в strftime (%d.%m.%Y).

    Заменяет по убыванию длины чтобы избежать частичных замен (YYYY → %Y
    раньше чем YY → %y, MMMM раньше MM и т.д.).
    """
    tokens = sorted(_CONVERTIBLE.keys(), key=len, reverse=True)
    result = fmt
    for token in tokens:
        result = result.replace(token, _CONVERTIBLE[token])
    return result


def _uptime(creation_str: Optional[str] = None) -> str:
    """Вернуть время с момента создания файла."""
    if not creation_str:
        return ""
    try:
        created = datetime.fromisoformat(creation_str)
        delta = datetime.now() - created
        parts = []
        if delta.days > 0:
            parts.append(f"{delta.days}d")
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        return " ".join(parts) if parts else "0m"
    except (ValueError, TypeError):
        return ""


# ---- сканирование шаблонов ------------------------------------------------

def collect_templates(templates_dir: Path) -> Dict[str, Path]:
    """Собрать все .md шаблоны из директории и вложенных папок.

    Возвращает {имя_шаблона: Path} — имена уникальные,
    при конфликте побеждает первый найденный (по алфавитному порядку папок).
    """
    templates: Dict[str, Path] = {}
    if not templates_dir.is_dir():
        return templates
    # Рекурсивный обход, сортировка путей для детерминизма
    for fp in sorted(templates_dir.rglob("*.md")):
        name = fp.stem
        if name not in templates:
            templates[name] = fp
    return templates


# ---- построение контекста -------------------------------------------------

def build_context(
    filepath: Optional[Path] = None,
    title: Optional[str] = None,
    author: str = "",
    created_at: Optional[str] = None,
    modified_at: Optional[str] = None,
    todo_list: Optional[list] = None,
    specials: Optional[Dict[str, str]] = None,
) -> dict:
    """Собрать словарь-контекст для рендера шаблона.

    Args:
        filepath: Полный путь к файлу (если известен).
        title: Название (имя файла без расширения).
        author: Имя автора.
        created_at: Дата создания в формате ISO (или любая strftime-совместимая).
        modified_at: Дата модификации в формате ISO.
        todo_list: Список задач.
        specials: Дополнительные пользовательские переменные {name: value}.

    Returns:
        Словарь, который можно передать в Template.render().
    """
    now = datetime.now()
    today_dt = date.today()

    # Имя файла без расширения
    if title is None and filepath is not None:
        title = filepath.stem

    # Папка
    folder = ""
    if filepath is not None:
        folder = filepath.parent.name

    # Дата создания (если не передана — сегодня)
    creation_date = created_at or today_dt.isoformat()

    return {
        "title": title or "",
        "date": today_dt.isoformat(),
        "time": now.strftime("%H:%M"),
        "creation_date": creation_date,
        "modification_date": modified_at or today_dt.isoformat(),
        "author": author,
        "file_name": title or "",
        "file_path": str(filepath) if filepath else "",
        "folder": folder,
        "random": _random_int(),
        "cursor": "",
        "todo": todo_list or [],
        "task_pending": [t for t in (todo_list or []) if not t.get("done", False)],
        "weekday": today_dt.isoweekday(),
        "week_number": today_dt.isocalendar()[1],
        "month_name": today_dt.strftime("%B"),
        "year": today_dt.strftime("%Y"),
        "month": today_dt.strftime("%m"),
        "day": today_dt.strftime("%d"),
        "uptime": _uptime(creation_date),
        # Псевдонимы для обратной совместимости
        "task:pending": [t for t in (todo_list or []) if not t.get("done", False)],
    }


# ---- рендер шаблона -------------------------------------------------------

def render_template(
    template_content: str,
    context: dict,
) -> str:
    """Отрендерить содержимое шаблона с подстановкой Jinja2-переменных.

    Args:
        template_content: Сырое содержимое .md-шаблона.
        context: Словарь переменных (из build_context).

    Returns:
        Отрендеренный текст.
    """
    from jinja2 import Environment, BaseLoader, TemplateNotFound, StrictUndefined

    # Кастомный загрузчик, который разрешает встроенные фильтры date/time
    class _FilterLoader(BaseLoader):
        def get_source(self, environment, template):
            raise TemplateNotFound(template)

    env = Environment(
        loader=_FilterLoader(),
        undefined=StrictUndefined,
        autoescape=False,
    )

    # Регистрируем фильтры для шаблонов вида {{date:YYYY-MM-DD}}
    # Jinja2-фильтр получает значение слева от `|` как первый аргумент.
    # Мы же хотим: `{{date:YYYY-MM-DD}}` → `{{date|fmt_date("YYYY-MM-DD")}}`
    # где фильтр игнорирует вход и возвращает отформатированную дату.
    def _fmt_filter(fmt_func, *args, **kwargs):
        # Игнорируем значение (оно пришло от переменной перед |)
        return fmt_func(str(list(args)[0]) if args else "%Y-%m-%d")

    def _fmt_date_filter(value, fmt="%Y-%m-%d"):
        # Поддержка читаемых форматов (DD → %d, MM → %m, YYYY → %Y, YY → %y)
        # Также HH → %H, mm → %M, ss → %S
        fmt = _convert_readable_format(fmt)
        return _format_date(fmt)

    def _fmt_time_filter(value, fmt="%H:%M"):
        fmt = _convert_readable_format(fmt)
        return _format_time(fmt)

    env.filters["fmt_date"] = _fmt_date_filter
    env.filters["fmt_time"] = _fmt_time_filter
    env.filters["fmt_random"] = lambda _: _random_int()
    env.filters["fmt_uptime"] = lambda _, creation: _uptime(creation)

    # Регистрируем глобальные функции
    env.globals["_date"] = _format_date
    env.globals["_time"] = _format_time
    env.globals["_random"] = _random_int

    # Пре-процессинг: заменяем имена с дефисами/двоеточиями на валидные
    # Jinja2 идентификаторы ({{week-number}} → {{week_number}},
    # {{task:pending}} → {{task_pending}}, {{date:YYYY-MM-DD}} обрабатывается ниже)
    content = re.sub(
        r"\{\{(task):(pending)([^}]*)\}\}",
        r"{{\1_\2\3}}",
        template_content,
    )
    content = re.sub(
        r"\{\{week-number\}\}",
        "{{week_number}}",
        content,
    )
    content = re.sub(
        r"\{\{month-name\}\}",
        "{{month_name}}",
        content,
    )
    content = re.sub(
        r"\{\{file-name\}\}",
        "{{file_name}}",
        content,
    )
    content = re.sub(
        r"\{\{file-path\}\}",
        "{{file_path}}",
        content,
    )

    # Разбираем псевдо-Jinja2 синтаксис вида {{ключ:формат}} → ключ|fmt_ключ("формат")
    # Это нужно, т.к. в шаблонах используется `{{date:YYYY-MM-DD}}`, а Jinja2
    # воспринимает часть после `:` как имя фильтра.
    # Переписываем: `{{date:YYYY-MM-DD}}` → `{{date|fmt_date("YYYY-MM-DD")}}`
    def _replace_fmt(m: re.Match) -> str:
        var_name = m.group(1)
        fmt = m.group(2).strip()
        return f"{{{{{var_name}|fmt_{var_name}('{fmt}')}}}}"

    content = re.sub(
        r"\{\{(\w+):([^}]*?)\}\}",
        _replace_fmt,
        content,
    )

    template = env.from_string(content)
    return template.render(**context)


# ---- создание файла из шаблона --------------------------------------------

def create_from_template(
    template_path: Path,
    target_path: Path,
    context: dict,
) -> str:
    """Прочитать шаблон, отрендерить и вернуть готовое содержимое.

    Аргументы:
        template_path: Путь к .md-файлу шаблона.
        target_path: Путь, куда будет записан результат (для контекста).
        context: Контекст для рендера.

    Возвращает:
        Отрендеренный текст.
    """
    content = template_path.read_text(encoding="utf-8")
    return render_template(content, context)
