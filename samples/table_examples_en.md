# Table Examples with Calculations (Org-mode TBLFM)

Impactite supports calculations in Markdown tables via formulas in Emacs Org-mode style.
Formulas are placed in an HTML comment immediately after the table:

```markdown
<!-- TBLFM: formula1::formula2::... -->
```

---

## 1. Basic Arithmetic Operations

All standard operators: `+`, `-`, `*`, `/`, `%` (modulo), `**` (power).

| A  | B | Sum | Difference | Product | Quotient | Remainder | Power |
|----|---|-----|------------|---------|----------|-----------|-------|
| 10 | 3 |     |            |         |          |           |       |
| 20 | 4 |     |            |         |          |           |       |
| 15 | 5 |     |            |         |          |           |       |
<!-- TBLFM: $3=$1+$2::$4=$1-$2::$5=$1*$2::$6=$1/$2::$7=$1%$2::$8=$1**$2 -->

---

## 2. Column Formulas (applied to all data rows)

A column formula `$N=expression` is automatically evaluated for each table row.

### 2.1. Orders: price × quantity

| Item       | Price | Qty | Discount % | Total with discount |
|------------|-------|-----|------------|---------------------|
| Laptop     | 1200  | 2   | 10         |                     |
| Mouse      | 25    | 5   | 0          |                     |
| Keyboard   | 80    | 3   | 5          |                     |
| Monitor    | 350   | 1   | 15         |                     |
| **Total**  |       |     |            |                     |
<!-- TBLFM: $5=$2*$3*(1-$4%)::@6$5=vsum(@2$5..@5$5) -->

### 2.2. Area and perimeter calculation

| Figure   | Length | Width | Area | Perimeter |
|----------|--------|-------|------|-----------|
| Room A   | 5.2    | 4.1   |      |           |
| Room B   | 3.8    | 3.5   |      |           |
| Room C   | 6.0    | 4.5   |      |           |
| Room D   | 2.5    | 2.2   |      |           |
| **Total**|        |       |      |           |
<!-- TBLFM: $4=$2*$3::$5=2*($2+$3)::@6$4=vsum(@2$4..@5$4)::@6$5=vsum(@2$5..@5$5) -->

---

## 3. Specific cells (@row$column)

The formula `@R$C=expression` computes a value only for the specified cell.

### 3.1. Total row manually

| Category    | January | February | March | Quarter |
|-------------|---------|----------|-------|---------|
| Groceries   | 450     | 520      | 480   |         |
| Transport   | 120     | 130      | 125   |         |
| Housing     | 800     | 800      | 850   |         |
| Entertainment| 200    | 150      | 300   |         |
| **Total**   |         |          |       |         |
<!-- TBLFM: @2$5=vsum(@2$2..@2$4)::@3$5=vsum(@3$2..@3$4)::@4$5=vsum(@4$2..@4$4)::@5$5=vsum(@5$2..@5$4)::@6$2=vsum(@2$2..@5$2)::@6$3=vsum(@2$3..@5$3)::@6$4=vsum(@2$4..@5$4)::@6$5=vsum(@2$5..@5$5) -->

### 3.2. Average per column

| Student  | Math | Physics | Chemistry | Average score |
|----------|------|---------|-----------|---------------|
| Ivanov   | 85   | 90      | 78        |               |
| Petrov   | 72   | 88      | 92        |               |
| Sidorov  | 91   | 76      | 85        |               |
| Kozlova  | 68   | 82      | 74        |               |
| **Mean** |      |         |           |               |
<!-- TBLFM: @2$5=vmean(@2$2..@2$4)::@3$5=vmean(@3$2..@3$4)::@4$5=vmean(@4$2..@4$4)::@5$5=vmean(@5$2..@5$4)::@6$2=vmean(@2$2..@5$2)::@6$3=vmean(@2$3..@5$3)::@6$4=vmean(@2$4..@5$4)::@6$5=vmean(@2$5..@5$5) -->

---

## 4. Aggregate Functions

- `vsum(range)` — sum
- `vmean(range)` — arithmetic mean
- `vmax(range)` — maximum
- `vmin(range)` — minimum
- `vprod(range)` — product
- `count(range)` — count of numeric cells

### 4.1. Sales statistics

| Month    | Sales | Profit | Clients |
|----------|-------|--------|---------|
| January  | 12000 | 2400   | 45      |
| February | 15000 | 3000   | 52      |
| March    | 11000 | 2200   | 38      |
| April    | 18000 | 3600   | 61      |
| May      | 16500 | 3300   | 55      |
| **Sum**  |       |        |         |
| **Average**|     |        |         |
| **Minimum**|     |        |         |
| **Maximum**|     |        |         |
| **Count**|       |        |         |
<!-- TBLFM: @7$2=vsum(@2$2..@6$2)::@7$3=vsum(@2$3..@6$3)::@7$4=vsum(@2$4..@6$4)::@8$2=vmean(@2$2..@6$2)::@8$3=vmean(@2$3..@6$3)::@8$4=vmean(@2$4..@6$4)::@9$2=vmin(@2$2..@6$2)::@9$3=vmin(@2$3..@6$3)::@9$4=vmin(@2$4..@6$4)::@10$2=vmax(@2$2..@6$2)::@10$3=vmax(@2$3..@6$3)::@10$4=vmax(@2$4..@6$4)::@11$2=count(@2$2..@6$2)::@11$3=count(@2$3..@6$3)::@11$4=count(@2$4..@6$4) -->

### 4.2. Product of all elements

| n | Value | Factorial (n!) |
|---|-------|----------------|
| 1 | 1     |                |
| 2 | 2     |                |
| 3 | 3     |                |
| 4 | 4     |                |
| 5 | 5     |                |
<!-- TBLFM: $3=vprod(@2$1..@$1) -->

> Note: in the formula `$3=vprod(@2$1..@$1)` column 3 computes the product of all values in column 1 from row 2 to the current row.

---

## 5. Percentages and Financial Calculations

Percentages like `10%`, `5.5%` are automatically converted to decimal fractions.

### 5.1. Taxes and net profit

| Company   | Revenue | Tax 20% | Net profit | Share per employee |
|-----------|---------|---------|------------|--------------------|
| AlphaTech | 500000  |         |            |                    |
| BetaSoft  | 320000  |         |            |                    |
| GammaData | 780000  |         |            |                    |
| DeltaNet  | 150000  |         |            |                    |
| **Total** |         |         |            |                    |
<!-- TBLFM: $3=$2*20%::$4=$2-$3::$5=$4/12::@6$2=vsum(@2$2..@5$2)::@6$3=vsum(@2$3..@5$3)::@6$4=vsum(@2$4..@5$4)::@6$5=vsum(@2$5..@5$5) -->

### 5.2. Deposit interest calculation

| Deposit amount | Rate | Annual income | After 3 years |
|----------------|------|---------------|---------------|
| 100000         | 8%   |               |               |
| 250000         | 7.5% |               |               |
| 500000         | 9%   |               |               |
<!-- TBLFM: $3=$1*$2::$4=$1+$3*3 -->

---

## 6. Combined Formulas

Multiple operations in one expression with parentheses.

### 6.1. Body Mass Index (BMI)

Formula: weight (kg) / height² (m)

| Name  | Weight kg | Height cm | Height m | BMI  | Category               |
|-------|-----------|-----------|----------|------|------------------------|
| Anna  | 58        | 165       |          |      |                        |
| Boris | 82        | 180       |          |      |                        |
| Vera  | 70        | 172       |          |      |                        |
| Gleb  | 95        | 175       |          |      |                        |
<!-- TBLFM: $4=$3/100::$5=$2/($4**2) -->

> The "Category" column is not computed automatically — it requires conditional logic.

### 6.2. Currency conversion

| Item    | Price USD | Rate | Price EUR | Rate EUR | Price RUB |
|---------|-----------|------|-----------|----------|-----------|
| iPhone  | 999       | 0.92 |           | 0.85     |           |
| iPad    | 799       | 0.92 |           | 0.85     |           |
| MacBook | 1299      | 0.92 |           | 0.85     |           |
<!-- TBLFM: $4=$2*$3::$6=$2*$5*$3*91 -->

---

## 7. Cell Ranges

### 7.1. Sum of part of a column

| Week | Sales | Cumulative |
|------|-------|------------|
| 1    | 100   |            |
| 2    | 150   |            |
| 3    | 120   |            |
| 4    | 200   |            |
| 5    | 180   |            |
| 6    | 90    |            |
| **Sum weeks 1–4** | | |
<!-- TBLFM: $3=vsum(@2$2..@$2)::@8$2=vsum(@2$2..@5$2)::@8$3=vsum(@2$3..@5$3) -->

### 7.2. Subtotals by group

| Category     | Item      | Sales |
|--------------|-----------|-------|
| Electronics  | Phone     | 5000  |
| Electronics  | Tablet    | 3000  |
| **Electronics total** | | |
| Clothing     | T-shirt   | 800   |
| Clothing     | Jeans     | 1200  |
| **Clothing total** | | |
| **Grand total** | | |
<!-- TBLFM: @4$3=vsum(@2$3..@3$3)::@7$3=vsum(@5$3..@6$3)::@8$3=vsum(@4$3,@7$3) -->

---

## 8. Row Formulas (@row = ...)

The formula `@N=expression` is applied to all columns of the specified row.

### 8.1. "Difference" row

| Metric    | Q1     | Q2     | Q3    | Q4     |
|-----------|--------|--------|-------|--------|
| Income    | 100000 | 120000 | 95000 | 135000 |
| Expense   | 70000  | 80000  | 65000 | 90000  |
| Profit    |        |        |       |        |
<!-- TBLFM: @4$2=@2$2-@3$2::@4$3=@2$3-@3$3::@4$4=@2$4-@3$4::@4$5=@2$5-@3$5 -->

---

## 9. Practical Scenarios

### 9.1. Timesheet

| Employee | Mon | Tue | Wed | Thu | Fri | Sat | Sun | Total hours | Overtime (>40) |
|----------|-----|-----|-----|-----|-----|-----|-----|-------------|----------------|
| Ivanov   | 8   | 8   | 8   | 8   | 8   | 4   | 0   |             |                |
| Petrov   | 8   | 7   | 8   | 9   | 8   | 0   | 0   |             |                |
| Sidorov  | 9   | 9   | 8   | 8   | 8   | 6   | 0   |             |                |
<!-- TBLFM: $9=vsum(@$2..@$8)::$10=@$9-40 -->

### 9.2. Warehouse inventory

| Item        | In stock | Reserved | Available | Min.stock | Shortage |
|-------------|----------|----------|-----------|-----------|----------|
| Paper A4    | 500      | 100      |           | 200       |          |
| Cartridge B | 45       | 15       |           | 30        |          |
| Staplers    | 12       | 5        |           | 20        |          |
| Folders     | 80       | 20       |           | 50        |          |
<!-- TBLFM: $4=$2-$3::$6=$5-$4 -->

### 9.3. Travel expense calculation

| Route          | Distance km | Consumption l/100km | Fuel l | Price/l | Cost |
|----------------|-------------|---------------------|--------|---------|------|
| Moscow–SPb     | 700         | 8.5                 |        | 55      |      |
| SPb–Kazan      | 1100        | 9.0                 |        | 52      |      |
| Kazan–Sochi    | 1800        | 10.5                |        | 58      |      |
| **Total**      |             |                     |        |         |      |
<!-- TBLFM: $4=$2*$3/100::$6=$4*$5::@5$2=vsum(@2$2..@4$2)::@5$4=vsum(@2$4..@4$4)::@5$6=vsum(@2$6..@4$6) -->

### 9.4. Project evaluation (weighted score)

| Project   | Criterion 1 (30%) | Criterion 2 (50%) | Criterion 3 (20%) | Final score |
|-----------|-------------------|-------------------|-------------------|-------------|
| Project A | 85                | 90                | 75                |             |
| Project B | 70                | 95                | 80                |             |
| Project C | 90                | 80                | 85                |             |
| Project D | 75                | 85                | 90                |             |
| **Average**|                  |                   |                   |             |
<!-- TBLFM: $5=$2*30%+$3*50%+$4*20%::@6$2=vmean(@2$2..@5$2)::@6$3=vmean(@2$3..@5$3)::@6$4=vmean(@2$4..@5$4)::@6$5=vmean(@2$5..@5$5) -->

### 9.5. Calorie calculation

| Ingredient | Weight g | Kcal/100g | Protein/100g | Fat/100g | Carbs/100g | Total kcal |
|------------|----------|-----------|--------------|----------|------------|------------|
| Chicken    | 200      | 165       | 31           | 3.6      | 0          |            |
| Rice       | 150      | 130       | 2.7          | 0.3      | 28         |            |
| Vegetables | 100      | 35        | 1.5          | 0.2      | 6          |            |
| Butter     | 10       | 884       | 0            | 100      | 0          |            |
| **Total**  |          |           |              |          |            |            |
<!-- TBLFM: $7=$2*$3/100::@6$2=vsum(@2$2..@5$2)::@6$7=vsum(@2$7..@5$7) -->

---

## 10. Comparative Tables

### 10.1. Budget vs actual

| Item      | Budget | Actual | Variance | Variance % |
|-----------|--------|--------|----------|------------|
| Marketing | 50000  | 54000  |          |            |
| IT        | 30000  | 28500  |          |            |
| Rent      | 20000  | 20000  |          |            |
| Salaries  | 150000 | 148000 |          |            |
<!-- TBLFM: $4=$3-$2::$5=$4/$2*100 -->

### 10.2. Unit conversion

| Value       | Mm    | Cm    | M     | Inches | Feet  |
|-------------|-------|-------|-------|--------|-------|
| 1 meter     |       |       |       |        |       |
| 50 cm       |       |       |       |        |       |
| 2 feet      |       |       |       |        |       |
| 12 inches   |       |       |       |        |       |
<!-- TBLFM: @2$2=1000::@2$3=100::@2$5=39.37::@2$6=3.281::@3$2=500::@3$3=50::@3$4=0.5::@3$5=19.685::@4$4=0.6096::@4$2=609.6::@4$3=60.96::@4$5=24::@5$2=304.8::@5$3=30.48::@5$4=0.3048::@5$6=1 -->

---

## Formula Syntax (cheatsheet)

| Element              | Description                         | Example                       |
|----------------------|-------------------------------------|-------------------------------|
| `$3`                 | Column 3 in the current row         | `$3=$1+$2`                    |
| `@2`                 | Row 2 in the current column         | `@2=vsum(@3..@5)`             |
| `@2$3`               | Specific cell (row 2, column 3)     | `@2$3=100`                    |
| `@2$1..@5$1`         | Cell range                          | `vsum(@2$1..@5$1)`            |
| `vsum(range)`        | Sum                                 | `vsum(@2$2..@5$2)`            |
| `vmean(range)`       | Average                             | `vmean(@2$2..@5$2)`           |
| `vmax(range)`        | Maximum                             | `vmax(@2$2..@5$2)`            |
| `vmin(range)`        | Minimum                             | `vmin(@2$2..@5$2)`            |
| `vprod(range)`       | Product                             | `vprod(@2$1..@$1)`            |
| `count(range)`       | Count of numbers                    | `count(@2$2..@5$2)`           |
| `::`                 | Formula separator                   | `formula1::formula2`          |
| `20%`                | Percentage (→ 0.2)                  | `$3=$2*20%`                   |
| `+ - * / % **`       | Arithmetic                          | `$3=$1*($2+5)`                |
