"""Локализация приложения.

Поддерживаемые языки: английский (en), русский (ru), немецкий (de).

Каноническим ключом перевода служит сам английский текст — поэтому для
языка ``en`` отдельный каталог не нужен, а при отсутствии перевода строка
показывается по-английски (мягкий fallback).

Использование::

    from impactite.i18n import set_language, t
    set_language("ru")
    t("Save")                      # -> "Сохранить"
    t("File: {name}", name="a.md") # -> "Файл: a.md"
"""

from dataclasses import replace
from typing import Dict

SUPPORTED = ("en", "ru", "de")
DEFAULT = "en"

# Каталоги переводов: ключ — канонический английский текст.
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "ru": {
        # Виджеты / просмотр
        "No tags": "Нет тегов",
        "Tags": "Теги",
        "Select a file to view": "Выберите файл для просмотра",
        "Query engine unavailable": "Движок запросов недоступен",
        "Query error: {error}": "Ошибка запроса: {error}",
        "Query returned no data": "Запрос не вернул данных",
        "0 records": "0 записей",
        # Базовые выборки (base)
        "Filters": "Фильтры",
        "contains...": "содержит...",
        "min": "мин",
        "max": "макс",
        "from": "от",
        "to": "до",
        # Формы
        "Save": "Сохранить",
        "Cancel": "Отмена",
        "YYYY-MM-DD": "ГГГГ-ММ-ДД",
        "value1, value2 ...": "значение1, значение2 ...",
        # Поиск по тегам
        "Close": "Закрыть",
        "Tag search": "Поиск по тегам",
        "Enter tag (without #)": "Введите тег (без #)",
        "Escape to close": "Escape для закрытия",
        "No files found": "Файлы не найдены",
        # Несохранённые изменения
        "Don't save": "Не сохранять",
        "Unsaved changes": "Несохранённые изменения",
        "Save changes before leaving the editor?":
            "Сохранить изменения перед выходом из редактора?",
        # Создание каталога / заметки
        "Create folder": "Создать каталог",
        "Create note": "Создать заметку",
        "Create daily note": "Ежедневная заметка",
        "Daily note created: {name}": "Ежедневная заметка создана: {name}",
        "From template": "По шаблону",
        "Select template": "Выберите шаблон",
        "No templates found": "Шаблоны не найдены",
        "Template not found": "Шаблон не найден",
        "Template render error: {error}": "Ошибка рендера шаблона: {error}",
        "Note created from template: {name}": "Заметка по шаблону создана: {name}",
        "New folder name": "Имя нового каталога",
        "New note name": "Имя новой заметки",
        "folder name": "имя каталога",
        "note name": "имя заметки",
        "Enter — confirm, Escape — cancel": "Enter — подтвердить, Escape — отмена",
        "Folder created: {name}": "Каталог создан: {name}",
        "Folder creation error": "Ошибка создания каталога",
        "Note created: {name}": "Заметка создана: {name}",
        "Note creation error": "Ошибка создания заметки",
        # Горячие клавиши (Footer)
        "Quit": "Выход",
        "Edit": "Редактировать",
        "Exit editor": "Выход из редактора",
        "Refresh": "Обновить",
        "Sidebar": "Панель",
        "Theme": "Тема",
        # Статус-бар
        "EDIT": "РЕДАКТИРОВАНИЕ",
        "VIEW": "ПРОСМОТР",
        "File: {name}": "Файл: {name}",
        "No file": "Нет файла",
        "{file} | Mode: {mode}": "{file} | Режим: {mode}",
        # Уведомления
        "File saved": "Файл сохранён",
        "Save error": "Ошибка сохранения",
        "File list refreshed": "Список файлов обновлён",
        "Record #{id} saved to database": "Запись #{id} сохранена в БД",
        "Database write error: {error}": "Ошибка записи в БД: {error}",
        "Saved: {name}": "Сохранено: {name}",
        # Избранное
        "⭐ Favorites": "⭐ Избранное",
        "Toggle favorite": "В избранное",
        "Added to favorites": "Добавлено в избранное",
        "Removed from favorites": "Удалено из избранного",
        "Favorite": "Избранное",
        "Link graph": "Граф связей",
        "No data for graph": "Нет данных для графа",
        "File not found: {path}": "Файл не найден: {path}",
    },
    "de": {
        # Виджеты / просмотр
        "No tags": "Keine Tags",
        "Tags": "Tags",
        "Select a file to view": "Wählen Sie eine Datei zur Ansicht",
        "Query engine unavailable": "Abfrage-Engine nicht verfügbar",
        "Query error: {error}": "Abfragefehler: {error}",
        "Query returned no data": "Abfrage lieferte keine Daten",
        "0 records": "0 Datensätze",
        # Базовые выборки (base)
        "Filters": "Filter",
        "contains...": "enthält...",
        "min": "min",
        "max": "max",
        "from": "von",
        "to": "bis",
        # Формы
        "Save": "Speichern",
        "Cancel": "Abbrechen",
        "YYYY-MM-DD": "JJJJ-MM-TT",
        "value1, value2 ...": "Wert1, Wert2 ...",
        # Поиск по тегам
        "Close": "Schließen",
        "Tag search": "Tag-Suche",
        "Enter tag (without #)": "Tag eingeben (ohne #)",
        "Escape to close": "Escape zum Schließen",
        "No files found": "Keine Dateien gefunden",
        # Несохранённые изменения
        "Don't save": "Nicht speichern",
        "Unsaved changes": "Ungespeicherte Änderungen",
        "Save changes before leaving the editor?":
            "Änderungen vor dem Verlassen des Editors speichern?",
        # Создание каталога / заметки
        "Create folder": "Ordner erstellen",
        "Create note": "Notiz erstellen",
        "Create daily note": "Tägliche Notiz",
        "Daily note created: {name}": "Tägliche Notiz erstellt: {name}",
        "From template": "Aus Vorlage",
        "Select template": "Vorlage auswählen",
        "No templates found": "Keine Vorlagen gefunden",
        "Template not found": "Vorlage nicht gefunden",
        "Template render error: {error}": "Vorlagenfehler: {error}",
        "Note created from template: {name}": "Notiz aus Vorlage erstellt: {name}",
        "New folder name": "Name des neuen Ordners",
        "New note name": "Name der neuen Notiz",
        "folder name": "Ordnername",
        "note name": "Notizname",
        "Enter — confirm, Escape — cancel": "Enter — bestätigen, Escape — abbrechen",
        "Folder created: {name}": "Ordner erstellt: {name}",
        "Folder creation error": "Fehler beim Erstellen des Ordners",
        "Note created: {name}": "Notiz erstellt: {name}",
        "Note creation error": "Fehler beim Erstellen der Notiz",
        # Горячие клавиши (Footer)
        "Quit": "Beenden",
        "Edit": "Bearbeiten",
        "Exit editor": "Editor verlassen",
        "Refresh": "Aktualisieren",
        "Sidebar": "Seitenleiste",
        "Theme": "Thema",
        # Статус-бар
        "EDIT": "BEARBEITEN",
        "VIEW": "ANSICHT",
        "File: {name}": "Datei: {name}",
        "No file": "Keine Datei",
        "{file} | Mode: {mode}": "{file} | Modus: {mode}",
        # Уведомления
        "File saved": "Datei gespeichert",
        "Save error": "Fehler beim Speichern",
        "File list refreshed": "Dateiliste aktualisiert",
        "Record #{id} saved to database": "Datensatz #{id} in DB gespeichert",
        "Database write error: {error}": "DB-Schreibfehler: {error}",
        "Saved: {name}": "Gespeichert: {name}",
        # Избранное
        "⭐ Favorites": "⭐ Favoriten",
        "Toggle favorite": "Favorit umschalten",
        "Added to favorites": "Zu Favoriten hinzugefügt",
        "Removed from favorites": "Aus Favoriten entfernt",
        "Favorite": "Favorit",
        "Link graph": "Verknüpfungsgraph",
        "No data for graph": "Keine Daten für Graph",
        "File not found: {path}": "Datei nicht gefunden: {path}",
    },
}

_current = DEFAULT


def set_language(lang: str) -> None:
    """Установить активный язык приложения. Неизвестный язык -> ``en``."""
    global _current
    lang = (lang or DEFAULT).lower()
    _current = lang if lang in SUPPORTED else DEFAULT


def get_language() -> str:
    """Текущий активный язык."""
    return _current


def t(key: str, **kwargs) -> str:
    """Перевести ``key`` на текущий язык и подставить параметры формата."""
    text = key if _current == DEFAULT else TRANSLATIONS.get(_current, {}).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text
    return text


# Короткий алиас в стиле gettext.
_ = t


def retranslate_bindings(obj) -> None:
    """Перевести описания горячих клавиш у объекта Textual (App/Screen).

    Описания в ``BINDINGS`` заданы каноническим английским текстом; здесь они
    заменяются на перевод для текущего языка. Вызывать после ``set_language``
    (обычно в ``on_mount``), затем обновить Footer через ``refresh_bindings``.
    """
    bindings_map = getattr(obj, "_bindings", None)
    if bindings_map is None:
        return
    key_to_bindings = getattr(bindings_map, "key_to_bindings", None)
    if not key_to_bindings:
        return
    for key, blist in key_to_bindings.items():
        key_to_bindings[key] = [
            replace(b, description=t(b.description)) if b.description else b
            for b in blist
        ]
