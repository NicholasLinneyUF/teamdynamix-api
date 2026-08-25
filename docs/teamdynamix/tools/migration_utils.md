# `migration_utils` Module

**Module:** `teamdynamix.tools.migration_utils`  
**Purpose:** Prepare a fingerprint-bound SQLite tracker for local migration scripts

`prepare_sqlite_tracker(mode, db_path, source_path, table, logger=None)` joins
the lower-level CSV fingerprint and SQLite tracker primitives behind three
explicit lifecycle modes:

- `new` archives an existing database to its normal `.bak` path, creates a
  fresh tracker, imports the supplied table, and stores the source fingerprint.
- `overwrite` recreates the tracker without archiving, imports the supplied
  table, and stores the source fingerprint.
- `resume` requires an existing database and a complete stored fingerprint. It
  verifies an exact fingerprint match and returns the existing tracker without
  importing rows or changing progress.

The table may be a `CsvTable` or any object implementing `columns()`,
`row_count()`, and `get_row(index)`. Logging is optional and uses a simple
callable accepting one message; the workflow has no Session, transport, or API
client dependency.

```python
from teamdynamix.tools import load_csv, prepare_sqlite_tracker

source = "people.csv"
table = load_csv(source)
tracker = prepare_sqlite_tracker("new", "people.sqlite", source, table)
```

Unsafe resume states fail closed: a missing database or fingerprint raises
`MigrationStateError`, while changed source identity raises
`FingerprintMismatchError` with field-level details.
