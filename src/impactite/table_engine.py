"""
Движок вычислений для Markdown-таблиц, аналогичный Emacs Org-mode TBLFM.

Поддерживаемый синтаксис формул (в HTML-комментарии после таблицы):
    <!-- TBLFM: $4=$2*$3::@5$4=vsum(@2$4..@4$4) -->

Ссылка на ячейку:
    @2$3  — строка 2, столбец 3 (1-based, относительно всей таблицы)
    $3     — столбец 3 в текущей строке
    @2     — строка 2 в текущем столбце

Диапазон:
    @2$1..@4$1  — строки 2–4 столбца 1
    $1..$3      — столбцы 1–3 в текущей строке
    @2..@4      — строки 2–4 в текущем столбце

Встроенные функции:
    vsum(range)   — сумма
    vmean(range)  — среднее
    vmax(range)   — максимум
    vmin(range)   — минимум
    vprod(range)  — произведение
    count(range)  — количество непустых числовых ячеек

Арифметика: +, -, *, /, %, **, скобки.  Ячейки-ссылки внутри выражений
автоматически подменяются на их числовые значения (или 0).

Формулы в LHS:
    @2$4=expr       — конкретная ячейка
    $4=expr         — формула столбца: применяется ко всем строкам
    @2=expr         — формула строки: применяется ко всем столбцам
"""

import ast
import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union


@dataclass
class Cell:
    value: str
    computed: bool = False


@dataclass
class MarkdownTable:
    rows: List[List[Cell]]
    has_header: bool = True
    alignments: List[str] = field(default_factory=list)

    @property
    def num_rows(self) -> int:
        return len(self.rows)

    @property
    def num_cols(self) -> int:
        return max((len(r) for r in self.rows), default=0)


def parse_table_block(lines: List[str], start_idx: int) -> Tuple[Optional[MarkdownTable], int]:
    """Парсит блок таблицы, начинающийся со start_idx.

    Возвращает (MarkdownTable или None, индекс строки ПОСЛЕ таблицы).
    """
    if start_idx >= len(lines) or not lines[start_idx].strip().startswith("|"):
        return None, start_idx

    table_lines: List[str] = []
    i = start_idx
    while i < len(lines) and lines[i].strip().startswith("|"):
        table_lines.append(lines[i])
        i += 1

    rows: List[List[Cell]] = []
    alignments: List[str] = []
    has_header = False

    for line in table_lines:
        line = line.strip()
        cells_raw = [c.strip() for c in line[1:].split("|")]
        # Удаляем trailing empty от финального |
        while cells_raw and cells_raw[-1] == "":
            cells_raw = cells_raw[:-1]

        # Разделитель строки?
        if all(re.match(r"^\s*:?-+:?\s*$", c) for c in cells_raw if c.strip() != "") and any(c.strip() for c in cells_raw):
            has_header = True
            alignments = []
            for c in cells_raw:
                c_stripped = c.strip()
                if not c_stripped:
                    alignments.append("left")
                    continue
                left = c_stripped.startswith(":")
                right = c_stripped.endswith(":")
                if left and right:
                    alignments.append("center")
                elif right:
                    alignments.append("right")
                elif left:
                    alignments.append("left")
                else:
                    alignments.append("left")
            continue

        rows.append([Cell(value=c) for c in cells_raw])

    if not rows:
        return None, start_idx

    # Если разделитель не найден, первая строка считается заголовком по соглашению Markdown
    if not has_header and rows:
        has_header = True

    # Дополняем alignments до нужного количества столбцов
    num_cols = max(len(r) for r in rows) if rows else 0
    while len(alignments) < num_cols:
        alignments.append("left")

    return MarkdownTable(rows=rows, has_header=has_header, alignments=alignments[:num_cols]), i


def parse_formula_comment(line: str) -> List[str]:
    """Извлечь список формул из строки комментария.

    Поддерживает:
        <!-- TBLFM: $4=$2*$3::@2$4=vsum(@2$1..@4$1) -->
        # TBLFM: $4=$2*$3
    """
    m = re.match(r"<!--\s*TBLFM:\s*(.+?)\s*-->", line.strip())
    if m:
        raw = m.group(1)
    else:
        m = re.match(r"#\s*TBLFM:\s*(.+)", line.strip())
        if m:
            raw = m.group(1)
        else:
            return []
    return [f.strip() for f in raw.split("::") if f.strip()]


def _safe_eval(expr: str) -> float:
    """Безопасный eval арифметического выражения."""
    tree = ast.parse(expr, mode="eval")
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            raise ValueError(f"Disallowed node in expression: {type(node).__name__}")
    return eval(compile(tree, "<string>", "eval"), {"__builtins__": {}}, {})


def _to_number(value: str) -> Optional[float]:
    """Преобразовать строку в число или None."""
    s = value.strip()
    if not s:
        return None
    # Поддержка процентов
    if s.endswith("%"):
        try:
            return float(s[:-1]) / 100.0
        except ValueError:
            return None
    try:
        return float(s)
    except ValueError:
        return None


def _format_number(value: float) -> str:
    """Форматировать число для вывода в ячейку."""
    if value == int(value):
        return str(int(value))
    # Округляем до 4 значащих знаков, убираем trailing zeros
    s = f"{value:.4f}"
    s = s.rstrip("0").rstrip(".")
    return s


class FormulaEvaluator:
    def __init__(self, table: MarkdownTable):
        self.table = table

    # ------------------------------------------------------------------
    # Разбор ссылок
    # ------------------------------------------------------------------
    def _parse_cell_ref(self, ref: str, current_row: int, current_col: int) -> Tuple[int, int]:
        """Преобразовать текстовую ссылку в (row, col) 0-based."""
        ref = ref.strip()

        m = re.fullmatch(r"@(\d+)\$(\d+)", ref)
        if m:
            return int(m.group(1)) - 1, int(m.group(2)) - 1

        m = re.fullmatch(r"\$(\d+)", ref)
        if m:
            return current_row, int(m.group(1)) - 1

        m = re.fullmatch(r"@(\d+)", ref)
        if m:
            return int(m.group(1)) - 1, current_col

        # Орг-режим: @$N — текущая строка, столбец N
        m = re.fullmatch(r"@\$(\d+)", ref)
        if m:
            return current_row, int(m.group(1)) - 1

        raise ValueError(f"Invalid cell reference: {ref}")

    def _parse_range(self, ref: str, current_row: int, current_col: int) -> List[Tuple[int, int]]:
        """Разобрать список ячеек (через запятую) или диапазон (через ..)."""
        parts = [p.strip() for p in ref.split(",")]
        result = []
        for part in parts:
            if ".." in part:
                left, right = part.split("..", 1)
                r1, c1 = self._parse_cell_ref(left.strip(), current_row, current_col)
                r2, c2 = self._parse_cell_ref(right.strip(), current_row, current_col)
                for r in range(min(r1, r2), max(r1, r2) + 1):
                    for c in range(min(c1, c2), max(c1, c2) + 1):
                        result.append((r, c))
            else:
                result.append(self._parse_cell_ref(part, current_row, current_col))
        return result

    # ------------------------------------------------------------------
    # Чтение/запись ячеек
    # ------------------------------------------------------------------
    def _get(self, row: int, col: int) -> Optional[float]:
        if row < 0 or row >= self.table.num_rows:
            return None
        if col < 0 or col >= len(self.table.rows[row]):
            return None
        return _to_number(self.table.rows[row][col].value)

    def _set(self, row: int, col: int, value: Union[float, str]) -> None:
        if row < 0 or row >= self.table.num_rows:
            return
        # Дополняем строку при необходимости
        while col >= len(self.table.rows[row]):
            self.table.rows[row].append(Cell(value=""))
        text = _format_number(value) if isinstance(value, float) else str(value)
        self.table.rows[row][col] = Cell(value=text, computed=True)

    # ------------------------------------------------------------------
    # Вычисление выражений
    # ------------------------------------------------------------------
    def _eval_expr(self, expr: str, current_row: int, current_col: int) -> Optional[float]:
        expr = expr.strip()

        # 1. Числовой литерал (включая проценты вида 50%)
        num = _to_number(expr)
        if num is not None:
            return num

        # 2. Встроенная функция: vsum, vmean, vmax, vmin, vprod, count
        func_m = re.match(r"(vsum|vmean|vmax|vmin|vprod|count)\s*\(\s*(.+?)\s*\)\s*$", expr)
        if func_m:
            func_name = func_m.group(1)
            range_str = func_m.group(2)
            cells = self._parse_range(range_str, current_row, current_col)
            values = []
            for r, c in cells:
                v = self._get(r, c)
                if v is not None:
                    values.append(v)
            if not values:
                return None
            if func_name == "vsum":
                return sum(values)
            elif func_name == "vmean":
                return sum(values) / len(values)
            elif func_name == "vmax":
                return max(values)
            elif func_name == "vmin":
                return min(values)
            elif func_name == "vprod":
                p = 1.0
                for v in values:
                    p *= v
                return p
            elif func_name == "count":
                return float(len(values))

        # 3. Арифметическое выражение с ячейками-ссылками
        #    Заменяем ссылки на числовые значения, затем safe_eval
        safe = expr

        # @r$c — самый длинный, заменяем первым
        def repl_full(m):
            r, c = self._parse_cell_ref(m.group(0), current_row, current_col)
            v = self._get(r, c)
            return str(v) if v is not None else "0"

        safe = re.sub(r"@\d+\$\d+", repl_full, safe)

        # @$N — текущая строка, столбец N
        def repl_curr_col(m):
            col = int(m.group(1)) - 1
            v = self._get(current_row, col)
            return str(v) if v is not None else "0"

        safe = re.sub(r"@\$(\d+)", repl_curr_col, safe)

        # $c — столбец в текущей строке
        def repl_col(m):
            col = int(m.group(1)) - 1
            v = self._get(current_row, col)
            return str(v) if v is not None else "0"

        safe = re.sub(r"(?<![\w@])\$(\d+)", repl_col, safe)

        # @r — строка в текущем столбце
        def repl_row(m):
            row = int(m.group(1)) - 1
            v = self._get(row, current_col)
            return str(v) if v is not None else "0"

        safe = re.sub(r"@(\d+)(?!\$)", repl_row, safe)

        # Конвертируем проценты вида 50% → (50/100), но не ломаем оператор %
        safe = re.sub(r"(\d+(?:\.\d+)?)%(?!\d)", r"(\1/100)", safe)

        try:
            return float(_safe_eval(safe))
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Применение формулы
    # ------------------------------------------------------------------
    def apply_formula(self, formula: str) -> None:
        if "=" not in formula:
            return
        lhs, rhs = formula.split("=", 1)
        lhs = lhs.strip()
        rhs = rhs.strip()

        # Определяем тип формулы по LHS
        # 1. Столбцевая: $3=...
        col_m = re.fullmatch(r"\$(\d+)", lhs)
        if col_m:
            target_col = int(col_m.group(1)) - 1
            # Применяем ко всем строкам таблицы (включая заголовок? Org-mode исключает)
            start_row = 1 if self.table.has_header else 0
            for r in range(start_row, self.table.num_rows):
                val = self._eval_expr(rhs, r, target_col)
                if val is not None:
                    self._set(r, target_col, val)
            return

        # 2. Строчная: @2=...
        row_m = re.fullmatch(r"@(\d+)", lhs)
        if row_m:
            target_row = int(row_m.group(1)) - 1
            for c in range(self.table.num_cols):
                val = self._eval_expr(rhs, target_row, c)
                if val is not None:
                    self._set(target_row, c, val)
            return

        # 3. Диапазон: @2$1..@4$1=...
        if ".." in lhs:
            cells = self._parse_range(lhs, 0, 0)
            for r, c in cells:
                val = self._eval_expr(rhs, r, c)
                if val is not None:
                    self._set(r, c, val)
            return

        # 4. Конкретная ячейка: @2$3=...
        r, c = self._parse_cell_ref(lhs, 0, 0)
        val = self._eval_expr(rhs, r, c)
        if val is not None:
            self._set(r, c, val)


def apply_formulas(table: MarkdownTable, formulas: List[str]) -> None:
    """Применить список формул к таблице."""
    evaluator = FormulaEvaluator(table)
    for formula in formulas:
        evaluator.apply_formula(formula)


def process_table_with_formulas(lines: List[str], start_idx: int) -> Tuple[Optional[MarkdownTable], int]:
    """Парсит таблицу + формулы, применяет вычисления.

    Возвращает (MarkdownTable с computed ячейками, индекс строки ПОСЛЕ блока).
    """
    table, next_idx = parse_table_block(lines, start_idx)
    if table is None:
        return None, start_idx

    # Проверяем следующую строку на наличие TBLFM
    if next_idx < len(lines):
        formulas = parse_formula_comment(lines[next_idx])
        if formulas:
            apply_formulas(table, formulas)
            next_idx += 1

    return table, next_idx
