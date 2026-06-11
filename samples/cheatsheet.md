---
title: "Шпаргалка: Markdown + Pseudo-SQL"
tags:
  - cheatsheet
  - markdown
  - sql
---

# Шпаргалка по оформлению и запросам

Эта заметка демонстрирует все возможности оформления Markdown и псевдо-SQL (Dataview), доступные в **Impactite**.

---

## Текстовое оформление

- *Курсив* — оберните текст в одну звёздочку: `*курсив*`
- **Жирный** — оберните в две звёздочки: `**жирный**`
- ~~Зачёркнутый~~ — оберните в две тильды: `~~зачёркнутый~~`
- Можно комбинировать: ***жирный курсив***, **~~жирный зачёркнутый~~**

---

## Заголовки

```markdown
# Заголовок 1
## Заголовок 2
### Заголовок 3
```

---

## Ссылки

- Внутренняя ссылка на другую заметку: [О проекте](about.md)
- Внешняя ссылка: [Impactite на GitHub](https://github.com)
- Ссылка в списке: [Форматирование](test_formatting.md)

---

## Списки

### Маркированный список

- Первый пункт
- Второй пункт
  - Вложенный пункт
  - Ещё один вложенный
- Третий пункт

### Нумерованный список

1. Первый шаг
2. Второй шаг
3. Третий шаг

### Интерактивные чекбоксы

В режиме просмотра можно кликать по чекбоксам — они переключаются и сохраняются автоматически.

- [x] Прочитать документацию
- [ ] Написать заметку
- [x] Протестировать запросы
- [ ] Добавить #tags в заметки

---

## Цитаты

> Это цитата. Внутри неё могут быть **жирные** и *курсивные* фрагменты,
> а также [ссылки](test_links.md).

---

## Блоки кода

### Python

```python
def hello(name: str) -> None:
    print(f"Hello, {name}!")

hello("Impactite")
```

### SQL

```sql
SELECT title, author, rating
FROM books
WHERE rating >= 4
ORDER BY rating DESC;
```

### Без указания языка

```
Просто текстовый блок.
Вторая строка.
```

---

## Таблицы

| Язык      | Год  | Парадигма     |
|-----------|------|---------------|
| Python    | 1991 | Мультипарадигма|
| Rust      | 2010 | Системный     |
| Haskell   | 1990 | Функциональный|

---

## Теги

Теги распознаются автоматически в тексте: #cheatsheet, #markdown, #sql.

Также их можно задавать в frontmatter (см. самое начало этой заметки).

---

## Frontmatter

В начале любой заметки можно указать метаданные между тройными черточками:

```yaml
---
title: "Название заметки"
date: 2026-06-11
tags:
  - project
  - idea
---
```

---

# Псевдо-SQL запросы (Dataview)

Блоки кода с языком `query` (или `dataview`) в режиме просмотра выполняются как запросы и отображаются в виде таблиц.

````markdown
```query
FROM notes/samples/books
SELECT title, author, genre, year
ORDER BY year
```
````

### Результат

```query
FROM samples/books
SELECT title, author, genre, year
ORDER BY year
```

---

## Синтаксис запросов

```
FROM notes|database[/<фильтр>]
WHERE <поле> <оператор> <значение> [AND ...]
GROUP BY <поле1>, <поле2>
HAVING <агрегат|поле> <оператор> <значение> [AND ...]
SELECT <поле1>, <поле2>, <агрегат> | *
ORDER BY <поле|агрегат> [ASC|DESC]
LIMIT <n>
```

Все секции кроме `FROM` необязательны. Регистр ключевых слов не важен.

---

## Источники данных

| Источник | Описание | Неявные поля |
|----------|----------|--------------|
| `notes` | Frontmatter всех `.md` файлов | `file` (имя), `path` (путь) |
| `notes/подпапка` | Только файлы из подпапки | `file`, `path` |
| `database` | Записи форм из БД | `id`, `catalog`, `source`, `created_at` |
| `database/каталог` | Записи конкретного каталога | `id`, `catalog`, `source`, `created_at` |

---

## Операторы WHERE

| Оператор | Значение | Пример |
|----------|----------|--------|
| `=` | Равно | `genre = sci-fi` |
| `!=` | Не равно | `read != true` |
| `>` `<` `>=` `<=` | Числовое сравнение | `rating >= 4` |
| `CONTAINS` | Входит в список / подстрока | `tags CONTAINS classic` |
| `LIKE` | Подстрока (без учёта регистра) | `author LIKE tolkien` |

---

## Примеры запросов

### Простая выборка с фильтром и сортировкой

```query
FROM samples/books
WHERE read = true
SELECT title, author, rating
ORDER BY rating DESC
```

### Фильтрация по тегу (CONTAINS)

```query
FROM samples/books
WHERE tags CONTAINS fantasy
SELECT title, author, tags
```

### Поиск по подстроке в авторе (LIKE)

```query
FROM samples/books
WHERE author LIKE frank
SELECT title, author, year
```

### Толстые книги, топ-5

```query
FROM samples/books
WHERE pages > 400
SELECT title, pages, genre
ORDER BY pages DESC
LIMIT 5
```

---

## Агрегатные функции

Доступные функции: `COUNT`, `SUM`, `MIN`, `MAX`, `AVG`.

### Сколько книг в каждом жанре

```query
FROM samples/books
GROUP BY genre
SELECT genre, COUNT(*)
ORDER BY COUNT(*) DESC
```

### Полная сводка по жанрам

```query
FROM samples/books
GROUP BY genre
SELECT genre, COUNT(*), SUM(pages), AVG(pages), MIN(year), MAX(year)
ORDER BY COUNT(*) DESC
```

### Общие итоги (без GROUP BY)

```query
FROM samples/books
WHERE read = true
SELECT COUNT(*), SUM(pages), AVG(rating)
```

---

## HAVING — фильтрация групп

### Жанры с более чем одной книгой

```query
FROM samples/books
GROUP BY genre
SELECT genre, COUNT(*)
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
```

### Жанры с суммарным объёмом > 1000 страниц

```query
FROM samples/books
GROUP BY genre
SELECT genre, COUNT(*)
HAVING SUM(pages) > 1000
```

---

## Запросы к базе данных

> Чтобы получить данные, сначала откройте `form_review_db.md` в режиме просмотра,
> заполните форму и нажмите «Save». Запись попадёт в каталог `reviews`.

### Все отзывы

```query
FROM database/reviews
SELECT book, reviewer, rating, recommend
ORDER BY rating DESC
```

### Средний рейтинг по книгам

```query
FROM database/reviews
GROUP BY book
SELECT book, COUNT(*), AVG(rating)
ORDER BY AVG(rating) DESC
```

---

## Полезные подсказки

- Кликайте на теги в тексте — откроется поиск по тегу.
- Кликайте на чекбоксы в списках задач — состояние сохраняется автоматически.
- Кликайте на внутренние ссылки — откроется связанная заметка.
- В режиме редактирования (`E`) доступна панель инструментов для быстрого форматирования.
- Запросы `query` можно использовать в любой заметке — они всегда показывают актуальные данные.
