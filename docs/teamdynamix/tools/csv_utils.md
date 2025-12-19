# `csv_utils` Module

**Module:** `teamdynamix.tools.csv_utils`
**Python Import Path:** `teamdynamix.tools.csv_utils`
**API Surface:** Local utility (non-HTTP)
**Primary Types:** `CsvTable`, `CellMatch`
**Requires:** `pandas`

The `csv_utils` module provides **read-only CSV loading, querying, and searching utilities** designed for one-time scripts, migrations, and batch processing workflows.

It is intentionally **independent of the TeamDynamix API**, `Session`, and HTTP transport layers.

------

## Design Intent

This module is designed for:

- One-time scripts
- Data migrations
- Batch processing
- Local data inspection and preparation
- Spreadsheet-driven automation

It is intentionally **not optimized for**:

- Long-running services
- Concurrent mutation
- Streaming or real-time ingestion
- Large distributed datasets

All operations are **read-only** with respect to loaded data.

------

## Architectural Notes

Key design principles:

- **No endpoint awareness** (pure local utility)
- **No dependency on Session/Auth/Transport**
- **Predictable behavior**
- **Script-friendly APIs**
- **Minimal internal state**
- **Explicit separator control**

Internally, CSV data is stored using a `pandas.DataFrame`, but the API is designed so callers do **not need to work with pandas directly**.

------

## Separator Handling (Important)

CSV delimiter handling is controlled via a **module-global separator character**.

### Defaults

- Default separator: **comma**
- Default stored as **character code (`ord`)** for maximum flexibility

```python
DEFAULT_SEPARATOR_ORD = 44  # comma
```

### Global separator controls

These affect all subsequent loads and writes unless overridden per call:

```python
from teamdynamix.tools.csv_utils import (
    set_separator_ord,
    set_separator,
    reset_separator_default,
)

set_separator_ord(9)     # tab-delimited
set_separator("|")      # pipe-delimited
reset_separator_default()
```

### Per-call override

Every relevant function also supports **explicit overrides**, which take precedence over the global setting.

------

## Loading CSV Files

### `load_csv(...)`

```python
from teamdynamix.tools.csv_utils import load_csv

table = load_csv("./data/input.csv")
```

#### Signature

```python
load_csv(
    path: str | Path,
    *,
    separator_ord: int | None = None,
    separator: str | None = None,
    encoding: str = "utf-8",
    keep_default_na: bool = False,
    logger: Any = None,
) -> CsvTable
```

#### Behavior

- Loads the entire CSV into memory
- All values are loaded as **strings** (`dtype=str`)
- Empty strings are preserved by default
- Separator resolution order:
  1. `separator` argument
  2. `separator_ord` argument
  3. module-global separator

------

## `CsvTable` Class

`CsvTable` is an immutable, read-focused wrapper around a CSV dataset.

```python
from teamdynamix.tools.csv_utils import CsvTable
```

### Introspection Methods

```python
table.row_count()
table.column_count()
table.columns()
```

| Method           | Description             |
| ---------------- | ----------------------- |
| `row_count()`    | Total number of rows    |
| `column_count()` | Total number of columns |
| `columns()`      | List of column names    |

------

### Column Helpers

```python
table.get_column_index("Email")
table.get_column_name(3)
```

| Method                   | Description                  |
| ------------------------ | ---------------------------- |
| `get_column_index(name)` | Returns 0-based column index |
| `get_column_name(index)` | Returns column name          |

------

### Accessors

#### Get a full row

```python
row = table.get_row(10)
```

Returns a `dict[str, Any]` keyed by column name.

#### Get a specific cell

```python
value = table.get_cell(10, "Email")
value = table.get_cell(10, 3)
```

#### Get all values for a column

```python
emails = table.column_values("Email")
```

------

## Searching

Searching always returns **locations**, not copies of rows.

### `CellMatch`

Each match is represented by a `CellMatch` object:

```python
CellMatch(
    row: int,
    column: str,
    value: Any
)
```

Aliases:

- `.x` → column name
- `.y` → row index

------

### Substring search

```python
matches = table.search_contains(
    "example.com",
    case_sensitive=False,
)
```

#### Signature

```python
search_contains(
    needle: str,
    *,
    case_sensitive: bool = False,
    columns: Sequence[int | str] | None = None,
) -> list[CellMatch]
```

------

### Exact match search

```python
matches = table.search_exact(
    "ACTIVE",
    case_sensitive=True,
)
```

------

### Row-only convenience helpers

If you only need row indices:

```python
rows = table.search_contains_rows("admin")
rows = table.search_exact_rows("Y")
```

These return `List[int]`.

------

## Writing CSV Output

### `CsvTable.to_csv(...)`

```python
table.to_csv("./data/output.csv")
```

#### Signature

```python
to_csv(
    path: str | Path,
    *,
    separator_ord: int | None = None,
    separator: str | None = None,
    index: bool = False,
    encoding: str = "utf-8",
) -> Path
```

- Does **not** modify the table
- Uses global separator unless overridden
- Returns the resolved output path

------

## Standard Data Path Resolution

### `resolve_data_path(...)`

```python
from teamdynamix.tools.csv_utils import resolve_data_path

path = resolve_data_path("input.csv")
```

Resolution order:

1. Absolute path → used directly
2. `base_dir` argument
3. Environment variable (`TDX_DATA_DIR`)
4. Current working directory

This avoids hard-coding assumptions into scripts.

------

## Error Handling

Errors are surfaced immediately and explicitly:

- Invalid row/column indices → `IndexError`
- Missing columns → `KeyError`
- Invalid parameters → `TypeError` / `ValueError`

No silent coercion is performed.

------

## Thread Safety

This module is **not thread-safe** by design.

- Intended for script-scoped usage
- Module-global separator state is mutable

------

## Example Workflow

```python
from teamdynamix.tools.csv_utils import load_csv, set_separator_ord

set_separator_ord(44)  # comma

table = load_csv("users.csv")

inactive = table.search_exact_rows("Inactive", columns=["Status"])

for row_index in inactive:
    email = table.get_cell(row_index, "Email")
    print(email)
```

------

## Related Documentation

- `docs/teamdynamix/tools/README.md`
- `PATTERNS.md`
- `DESIGN.md`