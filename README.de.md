# Impactite

🌐 [English](README.md) · [Русский](README.ru.md) · **Deutsch**

Ein Konsolen-(TUI-)Betrachter und -Editor für Markdown-Dateien im Stil von
Obsidian, geschrieben in Python mit den Bibliotheken **Rich** und **Textual**.

## Funktionen

- 📁 **Dateibaum** — Navigation durch Dateien und Ordner im linken Bereich
- 👁️ **Ansichtsmodus** — gerendertes Markdown mit Formatierung und Scrollen
- ✅ **Interaktive Checkboxen** — klicken Sie auf Aufgabenlisten-Checkboxen (`- [ ]` / `- [x]`) im Ansichtsmodus, um sie umzuschalten und sofort zu speichern
- ✏️ **Bearbeitungsmodus** — Markdown-Syntaxhervorhebung und Code-Hervorhebung in Codeblöcken, mit einer Formatierungs-Symbolleiste
- 🏷️ **Tag-Wolke** — alle Tags mit individuellen Farben, anklickbar
- 🔍 **Tag-Suche** — modales Fenster mit anklickbaren Ergebnissen
- 🕸️ **Verknüpfungsgraph** — hierarchischer Baum der Beziehungen zwischen Notizen und Tags; alle Knoten anklickbar (Notizen öffnen, Tags suchen)
- 🎨 **Helles/dunkles Thema** — Umschalten im laufenden Betrieb oder über die Befehlspalette; die Auswahl wird automatisch gespeichert
- 🌐 **Oberflächenlokalisierung** — Englisch, Russisch, Deutsch
- 📝 **Eingabeformulare** — Formularnotizen mit Feldern, gespeichert in eine Datei oder eine Datenbank
- 🧮 **Pseudo-SQL-Abfragen** — einbettbare Abfragen über Notizen und die Datenbank (im Dataview-Stil)
- ⭐ **Favoriten** — Notizen als Favoriten markieren und über einen virtuellen Ordner aufrufen
- 🗂️ **Beliebiger Notizordner** — das Verzeichnis wird in der Konfiguration festgelegt (absolut / `~` / relativ)
- ⌨️ **Anpassbare Tastenkürzel**

## Voraussetzungen

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (Paket- und Umgebungsmanager)

## Installation

```bash
uv sync
```

## Ausführen

```bash
# Über die CLI (nach uv sync)
uv run impactite

# Oder als Modul
uv run python -m impactite

# Mit explizitem Konfigurationspfad
uv run impactite path/to/config.yaml
```

## Als ausführbarer Befehl installieren

Damit Sie die App nicht jedes Mal über `uv run` starten müssen, können Sie sie als
normalen Befehl `impactite` auf Ihrem System installieren. Das Projekt deklariert
bereits einen Einstiegspunkt (`[project.scripts]` in `pyproject.toml`), daher
genügt ein einziger Befehl:

```bash
# Das Projekt als globalen Befehl installieren (aus dem Projektstamm)
uv tool install .
```

Danach ist der Befehl `impactite` aus jedem Verzeichnis verfügbar:

```bash
impactite                      # starten
impactite path/to/config.yaml  # mit einem Konfigurationspfad
```

> **PATH.** `uv` legt die ausführbare Datei in seinem eigenen Verzeichnis ab (in
> der Regel `~/.local/bin`). Wird der Befehl nicht gefunden, fügen Sie dieses
> Verzeichnis zu Ihrem `PATH` hinzu:
> ```bash
> uv tool update-shell   # trägt das benötigte Verzeichnis in PATH ein
> ```
> (danach das Terminal neu starten). Den Pfad finden Sie mit `uv tool dir`.

Nützliche Befehle zum Verwalten des installierten Befehls:

```bash
uv tool install --editable .   # "editable"-Installation: Codeänderungen wirken
                               # sofort, keine Neuinstallation nötig (praktisch beim Entwickeln)
uv tool upgrade impactite      # nach Änderungen aktualisieren (falls nicht editable)
uv tool list                   # installierte Werkzeuge auflisten
uv tool uninstall impactite    # den Befehl entfernen
```

> **Hinweis zu `config.yaml`.** Nach der Installation läuft `impactite` aus jedem
> Verzeichnis, und die Konfiguration wird standardmäßig im **aktuellen**
> Verzeichnis gesucht. Geben Sie den Konfigurationspfad explizit an
> (`impactite ~/notes/config.yaml`) oder starten Sie aus dem Ordner, in dem
> `config.yaml` liegt. Denken Sie daran: Ein relativer `notes_path` wird relativ
> zur Konfigurationsdatei selbst aufgelöst, sodass der Notizordner nicht „verrutscht“.

### Alternative: ein Distributionspaket bauen (Wheel)

Wenn Sie ein installierbares Paket benötigen (zum Beispiel, um es in eine andere
Umgebung per `pip` zu installieren):

```bash
uv build            # erzeugt dist/impactite-0.1.0-py3-none-any.whl und .tar.gz
# dann in einer beliebigen Umgebung:
pip install dist/impactite-0.1.0-py3-none-any.whl
```

## Projektstruktur

```
impactite/
├── pyproject.toml          # Projektkonfiguration und Abhängigkeiten
├── config.yaml             # Anwendungseinstellungen
├── README.md               # Dokumentation (English)
├── README.ru.md            # Dokumentation (Русский)
├── README.de.md            # Dokumentation (Deutsch)
├── src/impactite/
│   ├── __init__.py         # Paket-Einstiegspunkt
│   ├── core.py             # Kern: Config, FileSystem, MarkdownParser,
│   │                       #       TagIndex, QueryEngine, parse_form_definition
│   ├── app.py              # Textual-UI (App + Widgets, Stile in DEFAULT_CSS)
│   ├── i18n.py             # Lokalisierung (en/ru/de)
│   └── editor.tcss         # (ungenutzt — aus Kompatibilitätsgründen behalten)
└── notes/                  # Notizordner (Standard)
    └── .tag_index.db       # SQLite: Tag-Index, Farben, Formulardatensätze, Favoriten, Notiz-Verknüpfungen
```

---

## Konfiguration

Alle Einstellungen stehen in `config.yaml`. Standardmäßig sucht die App sie im
aktuellen Verzeichnis, aber Sie können einen Pfad explizit angeben:
`uv run impactite my-config.yaml`.

```yaml
# Pfad zum Ordner mit Markdown-Dateien.
# Jedes Verzeichnis funktioniert:
#   - absoluter Pfad:       "/home/user/Documents/MyNotes"
#   - mit dem Home-Ordner:  "~/Notes"
#   - relativer Pfad:       "./notes" (RELATIV zu dieser Konfigurationsdatei aufgelöst)
notes_path: "./notes"

# Oberflächensprache: en (English), ru (Русский), de (Deutsch)
language: "de"

# Tastenkürzel
hotkeys:
  open_file: "enter"          # Ausgewählte Datei öffnen
  edit_mode: "e"              # Bearbeitungsmodus umschalten
  view_mode: "v"              # Ansichtsmodus umschalten
  save_file: "ctrl+s"         # Datei speichern
  search_tags: "ctrl+t"       # Tag-Suche
  close_search: "escape"      # Suche/Dialog schließen
  quit: "ctrl+q"              # Beenden
  refresh: "ctrl+r"           # Dateiliste aktualisieren
  toggle_sidebar: "ctrl+b"    # Seitenleiste ein-/ausblenden

# Anzeigeeinstellungen
display:
  show_line_numbers: true     # Zeilennummern im Editor
  word_wrap: true             # Zeilenumbruch im Editor
  syntax_theme: "monokai"     # Code-Hervorhebungsthema (monokai, dracula, github_light, ...)
  code_border: "round"        # Rahmenstil der Codeblöcke (round, box, double)
  app_theme: "textual-dark"   # Anwendungsthema (siehe unten)

# Tag-Wolken-Einstellungen
tags:
  show_cloud: true            # Tag-Wolke anzeigen
  min_tag_size: 1             # Min. Tag-Größe
  max_tag_size: 3             # Max. Tag-Größe
```

### Parameter

| Parameter | Zweck |
|-----------|-------|
| `notes_path` | Notizverzeichnis. Ein relativer Pfad wird **relativ zur Konfigurationsdatei** aufgelöst, nicht zum aktuellen Arbeitsverzeichnis — der Start von überall öffnet denselben Ordner. `~` wird unterstützt. |
| `language` | Oberflächensprache: `en`, `ru`, `de`. Ein unbekannter Wert → `en`. |
| `hotkeys.*` | Tastenkürzel für Aktionen. |
| `display.show_line_numbers` | Zeilennummern im Editor. |
| `display.word_wrap` | Lange Zeilen im Editor umbrechen. |
| `display.syntax_theme` | Code-Hervorhebungsthema (Pygments-Stile: `monokai`, `dracula`, `github_light`, …). |
| `display.code_border` | Rahmenstil um Codeblöcke. |
| `display.app_theme` | Anwendungsthema. Wird beim Umschalten automatisch gespeichert (`Ctrl+L`). |
| `tags.show_cloud` | Ob die Tag-Wolke angezeigt wird. |
| `tags.min_tag_size` / `max_tag_size` | Der „Gewichts“-Bereich der Tags in der Wolke. |

### Anwendungsthemen (`app_theme`)

Dunkel: `textual-dark`, `dracula`, `monokai`, `nord`, `gruvbox`, `tokyo-night`, …
Hell: `textual-light`, `solarized-light`, `catppuccin-latte`, `rose-pine-dawn`, `atom-one-light`.

`Ctrl+L` schaltet das helle/dunkle Thema um, und die Auswahl wird automatisch
in `config.yaml` gespeichert (Feld `app_theme`) — unabhängig davon, ob Sie das
Thema über die Tastenkombination oder die Befehlspalette wechseln.

---

## Tags

Tags werden auf zwei Arten erkannt (in der Reihenfolge der Priorität):

1. **Im Frontmatter** der Notiz — die `tags:`-Liste:
   ```yaml
   ---
   tags:
     - python
     - tutorial
   ---
   ```
2. **Im Text** der Notiz — im Format `#tag`:
   ```markdown
   Diese Notiz handelt von #python und #textual.
   ```

Beim Start werden alle Notizen gescannt und der Tag-Index in der SQLite-Datenbank
`.tag_index.db` im Notizordner gespeichert. Jedem Tag wird deterministisch eine
eindeutige Farbe zugewiesen (in der DB gespeichert). Die Tag-Wolke unten links und
die Tags direkt im Text sind anklickbar — ein Klick öffnet die Suche nach diesem Tag.

---

## Verknüpfungsgraph

Der **🕸️ Verknüpfungsgraph** ist ein vordefinierter Knoten in der Seitenleiste
(neben ⭐ Favoriten). Er öffnet einen hierarchischen Baum, der die Beziehungen
zwischen Ihren Notizen und Tags visualisiert:

- **Tags** sind die obersten Äste (farbig, anklickbar → öffnet die Tag-Suche)
- **Notizen** sind unter den Tags verschachtelt, die sie enthalten (anklickbar → öffnet die Notiz)
- **Interne Links** zwischen Notizen (`[Text](andere.md)`) werden verfolgt und als
  verschachtelte Verbindungen angezeigt
- **Rückverweise** (Notizen, die auf die aktuelle verlinken) werden ebenfalls angezeigt
- Alle Knoten sind **standardmäßig ausgeklappt**, sodass die gesamte Struktur auf einen Blick sichtbar ist

Wenn Sie eine Notiz aus dem Graphen öffnen, drücken Sie `Backspace`, um zum Graphen zurückzukehren.

---

## Eingabeformulare

Jede Notiz, deren **erster Frontmatter-Schlüssel** `type: form` ist, wird im
**Ansichtsmodus** als interaktives Dateneingabeformular angezeigt (mit den
Schaltflächen „Speichern“ / „Abbrechen“). Im **Bearbeitungsmodus** sehen Sie die
gewöhnliche Formular-Auszeichnung.

### Struktur der Formulardefinition

```yaml
---
type: form                 # erforderlich, muss der ERSTE Schlüssel sein
destination: note          # wohin speichern: note (md-Datei) oder database (DB)
catalog: ./projects/       # Unterordner (für note) oder Katalog-Label (für database)
fields:
  - <schlüssel>: [<beschriftung>, <typ>, <param3>, <param4>]
  - ...
---
```

- **`type: form`** — die Formularmarkierung (muss zuerst stehen).
- **`destination`** — `note` (Standard) speichert das Ergebnis als separate
  md-Datei mit Frontmatter; `database` speichert einen Datensatz in SQLite
  (dieselbe DB wie der Tag-Index, die Tabelle `form_records`).
- **`catalog`** — für `note` ein Unterordner im Notizverzeichnis, in dem die
  erstellte Datei abgelegt wird; für `database` ein Text-Katalog-Label des Datensatzes.
- **`fields`** — eine Liste von Feldern. Jeder Eintrag ist ein Mapping mit einem
  einzigen Schlüssel: `feldname: [beschriftung, typ, param3, param4]`.
  - `feldname` — der Schlüssel, unter dem der Wert im Frontmatter/in der DB landet
    (und nach dem Sie später abfragen können).
  - `beschriftung` — der über dem Feld angezeigte Beschriftungstext.
  - `typ` — der Feldtyp (siehe Tabelle unten).
  - `param3`, `param4` — hängen vom Typ ab.

### Feldtypen

| Typ | Widget | Param 3 | Param 4 | Gespeicherter Wert |
|-----|--------|---------|---------|--------------------|
| `string` | einzeilige Eingabe | max. Länge (Zahl, `0` = kein Limit) | — | Zeichenkette |
| `text` | mehrzeilige Eingabe | — | — | Zeichenkette (mehrzeilig) |
| `integer` | numerische Eingabe | — | — | Ganzzahl |
| `date` | Datumseingabe (Platzhalter `YYYY-MM-DD`) | — | — | Datums-Zeichenkette |
| `boolean` | Umschalter | — | — | `true` / `false` |
| `list` | Liste (siehe unten) | Modus: `select` / `multi-select` | Array von Optionen | Zeichenkette oder Liste |

Bei `list` legt der dritte Parameter das Verhalten fest:

- **`select`** — eine Dropdown-Liste, **eine** Option wird gewählt → eine einzelne Zeichenkette wird gespeichert.
- **`multi-select`** — eine Mehrfachauswahlliste → ein Array von Zeichenketten wird gespeichert.
- alles andere/fehlend — freie kommagetrennte Eingabe (`wert1, wert2 ...`), der Wert
  wird in ein Array von Zeichenketten aufgeteilt.

Der vierte Parameter (`[option1, option2, ...]`) definiert die verfügbaren Optionen
für `select` / `multi-select`.

### Beispiel 1. Ein in md-Dateien gespeichertes Formular

```yaml
---
type: form
destination: note
catalog: ./tasks/
fields:
  - name: ["Aufgabenname", string, 60]
  - date: ["Startdatum", date, 0]
  - enable: ["Aktiv", boolean, 0]
  - priority: ["Priorität", list, select, [low, medium, high]]
  - tags: ["Tags", list, multi-select, [python, backend, ui, docs]]
  - count: ["Schätzung (Stunden)", integer, 0]
  - description: ["Beschreibung", text, 0]
---
```

Beim Ausfüllen und Speichern wird eine Datei wie `notes/tasks/Aufgabenname.md` erstellt:

```yaml
---
name: Den Parser schreiben
date: '2026-06-02'
enable: true
priority: high
tags:
  - python
  - backend
count: 8
description: Die Eingabedaten parsen und in die DB schreiben
---
```

> Der Dateiname stammt aus dem ersten nicht leeren Zeichenketten-Feld (bereinigt
> und eingesetzt), andernfalls aus einem Zeitstempel.

### Beispiel 2. Ein in der Datenbank gespeichertes Formular

```yaml
---
type: form
destination: database
catalog: crm
fields:
  - title: ["Kunde", string, 80]
  - status: ["Status", list, select, [new, active, closed]]
  - amount: ["Betrag", integer, 0]
  - notes: ["Notizen", text, 0]
---
```

Jedes Speichern hängt eine Zeile an die Tabelle `form_records` an (Spalten `id`,
`form_source`, `catalog`, `data` als JSON, `created_at`). Diese Datensätze stehen
dann Pseudo-SQL-Abfragen über die Quelle `database` zur Verfügung.

---

## Pseudo-SQL-Abfragen (im Dataview-Stil)

Im **Ansichtsmodus** wird ein Codeblock mit der Sprache `query` (oder `dataview`)
als Abfrage ausgeführt und als Tabelle angezeigt.

````markdown
```query
FROM notes
WHERE enable = true
SELECT name, count, category
ORDER BY count DESC
LIMIT 10
```
````

### Vollständige Syntax

```
FROM notes|database[/<filter>]
WHERE <feld> <operator> <wert> [AND ...]
GROUP BY <feld1>, <feld2>
HAVING <aggregat|feld> <operator> <wert> [AND ...]
SELECT <feld1>, <feld2>, <aggregat> | *
ORDER BY <feld|aggregat> [ASC|DESC]
LIMIT <n>
```

Alle Klauseln außer `FROM` sind optional. Die Groß-/Kleinschreibung der
Schlüsselwörter spielt keine Rolle.

### Datenquellen (`FROM`)

- **`notes`** — Zeilen aus dem Frontmatter von md-Dateien. Zusätzliche implizite
  Felder: `file` (Dateiname ohne Erweiterung) und `path` (Pfad relativ zum
  Notizverzeichnis). Sie können auf einen Unterordner einschränken: `FROM notes/tasks`.
- **`database`** — Formulardatensätze aus der Tabelle `form_records`. Implizite
  Felder: `id`, `catalog`, `source` (Dateiname des Formulars), `created_at`. Sie
  können auf einen Katalog einschränken: `FROM database/crm`.

### Operatoren (`WHERE` / `HAVING`)

| Operator | Bedeutung |
|----------|-----------|
| `=` | gleich |
| `!=` | ungleich |
| `>` `<` `>=` `<=` | numerischer Vergleich |
| `CONTAINS` | Enthaltensein (für Listen — ist das Element vorhanden; für Zeichenketten — Teilzeichenkette) |
| `LIKE` | Teilzeichenkette ohne Beachtung der Groß-/Kleinschreibung |

Mehrere Bedingungen werden mit `AND` verknüpft.

**Werte** werden automatisch erkannt: `true`/`false` (oder `yes`/`no`) → boolesch,
eine Ganzzahl/Gleitkommazahl → Zahl, Text in Anführungszeichen → Zeichenkette,
andernfalls — die Zeichenkette wie sie ist. Beispiele: `enable = true`,
`count >= 10`, `category = backend`, `tags CONTAINS python`.

### Aggregatfunktionen und Gruppierung

Verfügbar: `COUNT`, `SUM`, `MIN`, `MAX`, `AVG`.

- `COUNT(*)` — die Anzahl der Zeilen in einer Gruppe; `COUNT(feld)` — die Anzahl der nicht leeren Werte.
- `SUM` / `AVG` — werden nur über numerische Werte berechnet (`AVG` wird auf 2 Nachkommastellen gerundet).
- `MIN` / `MAX` — über Zahlen, oder lexikografisch, wenn die Werte nicht numerisch sind (Daten/Zeichenketten).

Die Aggregation greift, wenn es ein `GROUP BY` **oder** ein Aggregat im `SELECT`
gibt. Ohne `GROUP BY` wird ein Aggregat über alle Zeilen berechnet (Gesamtsummen).
Wird `SELECT` zusammen mit `GROUP BY` weggelassen, werden standardmäßig die
Gruppierungsfelder und `COUNT(*)` angezeigt.

`HAVING` filtert die bereits gruppierten Zeilen. Sie können nach einem Aggregat
filtern, das **nicht** in `SELECT` steht — es wird im Hintergrund berechnet.

### Abfragebeispiele

**Eine einfache Auswahl mit Filterung und Sortierung:**

````markdown
```query
FROM notes/tasks
WHERE enable = true
SELECT name, count, category
ORDER BY count DESC
```
````

**Filtern nach einem Tag (Enthaltensein in einer Liste):**

````markdown
```query
FROM notes/tasks
WHERE tags CONTAINS python
SELECT name, count, tags
```
````

**Eine Zusammenfassung nach Kategorie mit Aggregaten:**

````markdown
```query
FROM notes/tasks
GROUP BY category
SELECT category, COUNT(*), SUM(count), AVG(count), MIN(count), MAX(count)
ORDER BY SUM(count) DESC
```
````

**Gesamtsummen ohne Gruppierung:**

````markdown
```query
FROM notes/tasks
WHERE enable = true
SELECT COUNT(*), SUM(count)
```
````

**Gruppierung + Filterung nach einem Aggregat (`HAVING`):**

````markdown
```query
FROM notes/tasks
GROUP BY category
SELECT category, COUNT(*), SUM(count)
HAVING COUNT(*) > 1
ORDER BY SUM(count) DESC
```
````

**`HAVING` auf einem Aggregat, das nicht in `SELECT` steht:**

````markdown
```query
FROM notes/tasks
GROUP BY category
SELECT category, COUNT(*)
HAVING SUM(count) >= 20
```
````

**Eine Abfrage gegen Formulardatensätze in der Datenbank:**

````markdown
```query
FROM database/crm
WHERE status = active
SELECT title, amount, created_at
ORDER BY amount DESC
```
````

---

## Tastenkürzel (Standard)

| Taste | Aktion |
|-------|--------|
| `Enter` | Ausgewählte Datei öffnen |
| `E` | Bearbeitungsmodus |
| `Ctrl+S` | Datei speichern |
| `Ctrl+T` | Tag-Suche |
| `Ctrl+F` | Zu Favoriten hinzufügen/entfernen |
| `Ctrl+L` | Helles/dunkles Thema umschalten |
| `Ctrl+R` | Dateiliste aktualisieren |
| `Ctrl+B` | Seitenleiste ein-/ausblenden |
| `Ctrl+Q` | Beenden |
| `Backspace` | Zurück zur vorherigen Notiz (oder zurück zum Verknüpfungsgraph) |
| `Escape` | Suche/Dialog schließen; Editor verlassen (mit Speicheraufforderung) |

Im Ansichtsmodus ist Scrollen verfügbar: Pfeile `↑`/`↓`, `PgUp`/`PgDown`,
`Home`/`End`. In modalen Fenstern wird der Schaltflächenfokus mit den Pfeilen
`←`/`→` und `Tab` bewegt und mit `Enter` bestätigt. Der Notiztext kann mit der
Maus zum Kopieren markiert werden (sowohl im Ansichts- als auch im Bearbeitungsmodus).

---

## Symbolleiste im Bearbeitungsmodus

Im Bearbeitungsmodus erscheint über dem Editor eine Symbolleiste mit Knöpfen für schnelle Formatierung:

| Knopf | Aktion |
|-------|--------|
| **B** | Fett (`**Text**`) |
| *I* | Kursiv (`*Text*`) |
| S | Durchgestrichen (`~~Text~~`) |
| H1 / H2 / H3 | Überschriftenebenen |
| [L] | Link (`[Text](url)`) |
| - | Aufzählungsliste (`- Punkt`) |
| 1. | Nummerierte Liste (`1. Punkt`) |
| [ ] | Aufgabenliste (`- [ ] Punkt`) |
| > | Zitat (`> Zitat`) |
| ``` | Codeblock (` ``` ... ``` `) |
| — | Horizontale Linie (`---`) |

Wenn Text markiert ist, wird die Markierung umschlossen. Andernfalls wird eine Vorlage eingefügt und der Cursor hineingesetzt.

---

## Markdown: Beispiele

### Code mit Hervorhebung

````markdown
```python
def hello():
    print("Hello, World!")
```
````

### Interaktive Checkboxen

Aufgabenlisteneinträge sind im Ansichtsmodus anklickbar — ein Klick schaltet die Checkbox um und speichert die Datei sofort.

```markdown
- [x] Den Parser schreiben
- [ ] Tests hinzufügen
- [ ] Dokumentation aktualisieren
```

### Tags

Fügen Sie Tags an beliebiger Stelle in der Datei ein: `#tag1`, `#python`, `#tutorial`.

---

## Entwicklung

```bash
# Eine Abhängigkeit hinzufügen
uv add <package>

# Eine Dev-Abhängigkeit hinzufügen
uv add --dev <package>

# Die Tests ausführen (falls vorhanden)
uv run pytest
```

## Lizenz

MIT
