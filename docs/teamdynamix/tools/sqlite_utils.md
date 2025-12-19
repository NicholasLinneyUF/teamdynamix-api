# `sqlite_utils` Module

**Module:** `teamdynamix.tools.sqlite_utils`
**Python Import Path:** `teamdynamix.tools.sqlite_utils`
**API Surface:** Local utility (non-HTTP)
**Primary Type:** `SqliteTracker`
**Requires:** Python stdlib (`sqlite3`, `pathlib`, `shutil`)

The `sqlite_utils` module provides **local SQLite database helpers** designed for one-time scripts that need to:

- import tabular data into a durable local store,
- iterate through rows reliably over multiple runs,
- mark rows as processed, and
- record failures into an `errors` table.

This is a **script utility** and is intentionally independent from the TeamDynamix API clients (`Session`, `Transport`, etc.).

------

## Design Intent

This module is designed for:

- One-time scripts that need durable progress tracking
- Batch imports (e.g., 500+ rows) where failures must be captured and reviewed
- Long-running script tasks that may be interrupted and resumed
- Storing intermediate “work queues” locally without bringing in a full database stack

It is intentionally **not optimized for**:

- multi-user concurrency
- high-throughput ingestion
- complex relational modeling
- long-lived service deployments

------

## Core Concept: Tracking Tables

Every database created/managed by this module uses two tables:

### `data` table

Holds the imported dataset + a processed flag.

- Contains exactly the imported columns **as TEXT**
- Adds one additional column:

| Column      | Type      | Default | Purpose                                        |
| ----------- | --------- | ------- | ---------------------------------------------- |
| `processed` | `INTEGER` | `0`     | Tracking flag (0 = unprocessed, 1 = processed) |

### `errors` table

Append-only log for failures.

- Contains exactly the same imported columns **as TEXT**
- Adds one additional column:

| Column      | Type   | Purpose                             |
| ----------- | ------ | ----------------------------------- |
| `error_msg` | `TEXT` | Stores error message for failed row |

This design lets scripts:

- mark progress safely (row-by-row)
- always capture errors in a structured way
- rerun safely without losing context

------

## Database Files and Paths

### Default DB Path

By default, the module uses:

```python
DEFAULT_DB_PATH = "./data/sqlite.db"
```

This is intentionally **unopinionated**:

- it does not assume your project layout,
- it works for typical scripts,
- it is always overrideable.

### `resolve_data_path(...)`

The module includes a helper that resolves relative paths without hard-coding directory assumptions.

Resolution order:

1. absolute path → used directly
2. `base_dir` argument (if provided)
3. environment variable (`TDX_DATA_DIR`)
4. current working directory

------

## Filesystem Operations

These functions manage DB files at the filesystem level. They do **not** create tables.

### `create_db_file(...)`

Creates a new SQLite DB file, defaulting to `./data/sqlite.db`.

```python
from teamdynamix.tools.sqlite_utils import create_db_file

db_path = create_db_file()
```

- Ensures parent directory exists
- Removes existing file if `overwrite=True`
- Touches database by opening/closing a connection

------

### `backup_db_file(...)`

Creates a backup copy of an existing DB.

```python
from teamdynamix.tools.sqlite_utils import backup_db_file

bak_path = backup_db_file("./data/sqlite.db")
```

Default behavior:

- `sqlite.db` → `sqlite.db.bak`

Override destination:

```python
bak_path = backup_db_file("./data/sqlite.db", backup_path="./archive/sqlite_backup.db")
```

------

### `archive_db_file(...)`

Archives a DB by:

1. backing up the current file
2. creating a new clean DB file at the original path

```python
from teamdynamix.tools.sqlite_utils import archive_db_file

bak, fresh = archive_db_file("./data/sqlite.db")
```

Returns:

```python
(backup_path, new_db_path)
```

------

## `SqliteTracker` Class

`SqliteTracker` is the main interface for:

- schema creation
- importing rows
- reading/searching data (read-only)
- tracking progress (`pop()`, `mark_as_processed()`)
- recording failures (`write_error()`)

### Construction

```python
from teamdynamix.tools.sqlite_utils import SqliteTracker

tracker = SqliteTracker("./data/sqlite.db")
```

Optional logging is supported using the library `Logger` shape:

```python
tracker = SqliteTracker("./data/sqlite.db", logger=my_logger)
```

------

## Connection Lifecycle

`SqliteTracker` supports explicit connect/close or context management.

### Manual

```python
tracker.connect()
# ... work ...
tracker.close()
```

### Context Manager (recommended)

```python
with SqliteTracker("./data/sqlite.db") as tracker:
    # ... work ...
    pass
```

------

## Initialization and Schema

### `initialize(columns, recreate=True)`

Creates the `data` and `errors` tables for a given schema.

```python
columns = ["Name", "Status", "ManagerUID"]
tracker.initialize(columns)
```

If `recreate=True`, existing tables are dropped and recreated.

Reserved column names:

- `processed` (reserved for tracking)
- `error_msg` (reserved for errors table)

------

## Importing Data

The tracker supports importing data into the `data` table.

All imported values are stored as **TEXT** for predictability.

### `import_rows(columns, rows, ...)`

Use this when your data is a 2D array / list-of-tuples.

```python
columns = ["ColA", "ColB", "ColC"]
rows = [
    ("a1", "b1", "c1"),
    ("a2", "b2", "c2"),
]

inserted = tracker.import_rows(columns, rows)
```

Returns number of inserted rows.

------

### `import_dicts(rows, ...)`

Use this when rows are dictionaries with keys matching column names.

```python
rows = [
    {"Name": "Alice", "Email": "a@example.com"},
    {"Name": "Bob", "Email": "b@example.com"},
]

inserted = tracker.import_dicts(rows)
```

Columns are derived from the first row’s key order.

------

## Read-Only Data Methods

These methods do not mutate the database.

### Table introspection

```python
tracker.row_count()
tracker.column_count()
tracker.columns()
```

Note: `columns()` returns only imported columns (excludes internal `processed`).

------

### Column helpers

```python
tracker.get_column_index("Email")
tracker.get_column_name(2)
```

------

### Accessors

#### Get row

```python
row = tracker.get_row(10)   # dict of imported columns
```

Rows are addressed by **0-based index**, ordered by internal `rowid`.

#### Get cell

```python
val = tracker.get_cell(10, "Email")
val = tracker.get_cell(10, 3)
```

#### Column values

```python
emails = tracker.column_values("Email")
```

------

## Searching

Search returns **locations** and matched values.

### `CellMatch`

Each match is represented as:

```python
CellMatch(row: int, column: str, value: Any)
```

Aliases:

- `.x` → column name
- `.y` → row index

------

### Substring search

```python
matches = tracker.search_contains("example.com", case_sensitive=False)
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

### Exact search

```python
matches = tracker.search_exact("ACTIVE", case_sensitive=True)
```

------

### Row-only convenience

```python
rows = tracker.search_contains_rows("admin")
rows = tracker.search_exact_rows("Y")
```

These return `List[int]`.

------

## Tracking Operations (Mutating by Design)

These are the only operations intended to mutate data.

### `pop()`

Fetches the next unprocessed row in the `data` table.

```python
rowid, row = tracker.pop()
if row is None:
    # no more work
    pass
```

Returns:

- `(rowid, row_dict)` if available
- `(None, None)` when no unprocessed rows remain

The returned `rowid` is used for reliable tracking.

------

### `mark_as_processed(rowid)`

Marks a row as processed:

```python
tracker.mark_as_processed(rowid)
```

Returns `True` if a row was updated.

------

### `write_error(row, error_msg, rowid=None)`

Appends an error row into the `errors` table.

```python
tracker.write_error(row, "ValueError: bad date", rowid=rowid)
```

The `row` mapping should match imported columns (the dict returned by `pop()` is ideal).

------

### Unprocessed count

```python
remaining = tracker.unprocessed_count()
```

Useful for progress reporting in scripts.

------

## Example Script Pattern

This is the intended end-to-end pattern:

```python
from teamdynamix.tools.sqlite_utils import SqliteTracker

with SqliteTracker("./data/sqlite.db") as db:
    while True:
        rowid, row = db.pop()
        if row is None:
            break

        try:
            # Do work using row dict
            # ...
            pass
        except Exception as exc:
            db.write_error(row, f"{type(exc).__name__}: {exc}", rowid=rowid)
        finally:
            db.mark_as_processed(rowid)
```

This pattern ensures:

- progress tracking always advances
- failures are recorded but do not break the run
- reruns safely skip already processed rows

------

## Error Handling

Errors are surfaced explicitly:

- missing DB file backups → `FileNotFoundError`
- invalid indices → `IndexError`
- missing columns → `KeyError`
- invalid schema (reserved names) → `ValueError`

------

## Thread Safety

This module is not designed for concurrent, multi-threaded writes.

- Intended for script-scoped usage
- A single process should own the DB during a script run

------

## Related Documentation

- `docs/teamdynamix/tools/README.md`
- `csv_utils.md`
- `DESIGN.md`
- `PATTERNS.md`

------