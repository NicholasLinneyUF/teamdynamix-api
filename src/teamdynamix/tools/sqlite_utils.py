# =====================================================================
# FILE: src/teamdynamix/tools/sqlite_utils.py
#
# Intent:
# - Local-only SQLite helpers for one-time scripts.
# - Create short-term SQLite DB files to track row-by-row processing.
# - Provides a "data" table with a processed flag and an "errors" table to
#   capture failures (same columns + error_msg).
#
# Non-goals:
# - No HTTP calls
# - No dependency on TeamDynamix client modules (except optional Logger/Event)
# - No ORM
# - No schema inference beyond TEXT columns (predictable + script-friendly)
#
# Mutation policy:
# - Data access/search methods are read-only.
# - Tracking methods are allowed to mutate:
#     - mark_processed (sets processed=1)
#     - write_error (inserts into errors)
# =====================================================================

from __future__ import annotations

import os
import shutil
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union


# ---------------------------------------------------------------------
# Standard data path resolution (unopinionated)
# ---------------------------------------------------------------------
def resolve_data_path(
    relative_or_absolute: Union[str, Path],
    *,
    base_dir: Optional[Union[str, Path]] = None,
    env_var: str = "TDX_DATA_DIR",
) -> Path:
    """
    Resolve a data path in an unopinionated way.

    Rules:
      - If input is absolute -> return as Path
      - Else if base_dir provided -> base_dir / input
      - Else if env var set -> $TDX_DATA_DIR / input
      - Else -> current working directory / input
    """
    p = Path(relative_or_absolute)
    if p.is_absolute():
        return p

    if base_dir is not None:
        return Path(base_dir) / p

    env_base = os.getenv(env_var)
    if env_base:
        return Path(env_base) / p

    return Path.cwd() / p


def _maybe_log(logger: Any, message: str, *, level: int = 20, context: Optional[dict] = None) -> None:
    """
    Logger is optional; if provided, it must expose .log(message, level=?, context=?).
    Tools must not fail because logging failed.
    """
    if logger is None:
        return
    try:
        logger.log(message, level=level, context=context)
    except Exception:
        pass


# ---------------------------------------------------------------------
# Match object (mirrors csv_utils intent, but no cross-module dependency)
# ---------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class CellMatch:
    """
    Represents a single matching cell.

    - row: 0-based row index (ordered by rowid ascending)
    - column: column name
    - value: cell value

    Aliases:
    - x: column name
    - y: row index
    """
    row: int
    column: str
    value: Any

    @property
    def x(self) -> str:
        return self.column

    @property
    def y(self) -> int:
        return self.row


# ---------------------------------------------------------------------
# Filesystem operations: create / backup / archive
# ---------------------------------------------------------------------
DEFAULT_DB_PATH = "./data/sqlite.db"


def create_db_file(
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
    *,
    overwrite: bool = True,
    logger: Any = None,
) -> Path:
    """
    Create a new SQLite database file on disk.

    - If overwrite=True and file exists, it will be removed first.
    - Ensures parent directory exists.
    - Does not create tables; those are created when you initialize the tracker.
    """
    p = resolve_data_path(db_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if p.exists() and overwrite:
        _maybe_log(logger, "sqlite_utils.create_db_file: removing existing file", context={"db_path": str(p)})
        p.unlink()

    # Touch the DB by opening/closing a connection
    _maybe_log(logger, "sqlite_utils.create_db_file: creating db", context={"db_path": str(p)})
    conn = sqlite3.connect(str(p))
    conn.close()
    return p


def backup_db_file(
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
    *,
    backup_path: Optional[Union[str, Path]] = None,
    logger: Any = None,
) -> Path:
    """
    Backup an existing DB file.

    Default:
      - copies ./data/sqlite.db -> ./data/sqlite.db.bak

    Override:
      - pass backup_path for a custom destination.
    """
    src = resolve_data_path(db_path)
    if not src.exists():
        raise FileNotFoundError(f"Database file does not exist: {src}")

    dst = resolve_data_path(backup_path) if backup_path is not None else Path(str(src) + ".bak")
    dst.parent.mkdir(parents=True, exist_ok=True)

    _maybe_log(logger, "sqlite_utils.backup_db_file", context={"src": str(src), "dst": str(dst)})
    shutil.copy2(src, dst)
    return dst


def archive_db_file(
    db_path: Union[str, Path] = DEFAULT_DB_PATH,
    *,
    backup_path: Optional[Union[str, Path]] = None,
    logger: Any = None,
) -> Tuple[Path, Path]:
    """
    Archive an existing database:
      1) backup existing database (to .bak by default, or backup_path override)
      2) create a new database at the original db_path

    Returns:
      (backup_path, new_db_path)
    """
    src = resolve_data_path(db_path)
    bak = backup_db_file(src, backup_path=backup_path, logger=logger)
    new_db = create_db_file(src, overwrite=True, logger=logger)
    return (bak, new_db)


# ---------------------------------------------------------------------
# SQLite tracker object
# ---------------------------------------------------------------------
class SqliteTracker:
    """
    A lightweight wrapper around a SQLite file intended for script progress tracking.

    Tables created/maintained:
      - data   : imported columns + processed (INTEGER 0/1)
      - errors : imported columns + error_msg (TEXT)

    Notes:
    - All imported columns are stored as TEXT for predictability.
    - "processed" exists only on the data table and defaults to 0.
    - errors table does NOT have processed; it is an append-only log.
    """

    def __init__(
        self,
        db_path: Union[str, Path] = DEFAULT_DB_PATH,
        *,
        logger: Any = None,
    ):
        self.db_path = resolve_data_path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn: Optional[sqlite3.Connection] = None
        self._logger = logger

    # ---- Connection lifecycle ----
    def connect(self) -> None:
        if self._conn is not None:
            return
        _maybe_log(self._logger, "SqliteTracker.connect", context={"db_path": str(self.db_path)})
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.row_factory = sqlite3.Row

    def close(self) -> None:
        if self._conn is None:
            return
        _maybe_log(self._logger, "SqliteTracker.close", context={"db_path": str(self.db_path)})
        self._conn.close()
        self._conn = None

    def __enter__(self) -> "SqliteTracker":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def _ensure_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self.connect()
        assert self._conn is not None
        return self._conn

    # -----------------------------------------------------------------
    # Schema / initialization
    # -----------------------------------------------------------------
    def initialize(self, columns: Sequence[str], *, recreate: bool = True) -> None:
        """
        Create the required tables for a given set of columns.

        - data table: columns + processed INTEGER DEFAULT 0
        - errors table: columns + error_msg TEXT

        If recreate=True:
          - drops existing data/errors tables and recreates them.

        Use this once per imported dataset schema.
        """
        if not columns:
            raise ValueError("columns must be a non-empty sequence of column names.")

        cols = [str(c) for c in columns]
        self._validate_column_names(cols)

        conn = self._ensure_conn()
        cur = conn.cursor()

        if recreate:
            _maybe_log(self._logger, "SqliteTracker.initialize: dropping tables", context={"recreate": True})
            cur.execute('DROP TABLE IF EXISTS "data"')
            cur.execute('DROP TABLE IF EXISTS "errors"')

        # Build schema: all TEXT columns for predictability
        data_cols_sql = ", ".join([f'"{c}" TEXT' for c in cols] + ['"processed" INTEGER DEFAULT 0'])
        err_cols_sql = ", ".join([f'"{c}" TEXT' for c in cols] + ['"error_msg" TEXT'])

        _maybe_log(self._logger, "SqliteTracker.initialize: creating tables", context={"columns": cols})
        cur.execute(f'CREATE TABLE IF NOT EXISTS "data" ({data_cols_sql})')
        cur.execute(f'CREATE TABLE IF NOT EXISTS "errors" ({err_cols_sql})')

        conn.commit()

    @staticmethod
    def _validate_column_names(cols: Sequence[str]) -> None:
        bad = [c for c in cols if not c or not isinstance(c, str)]
        if bad:
            raise ValueError(f"Invalid column names: {bad}")
        if "processed" in cols:
            raise ValueError("Column name 'processed' is reserved (used by data table).")
        if "error_msg" in cols:
            raise ValueError("Column name 'error_msg' is reserved (used by errors table).")

    # -----------------------------------------------------------------
    # Import helpers (write once, then read/search many)
    # -----------------------------------------------------------------
    def import_rows(
        self,
        columns: Sequence[str],
        rows: Iterable[Sequence[Any]],
        *,
        recreate: bool = True,
        batch_size: int = 500,
    ) -> int:
        """
        Initialize schema and import rows into the data table.

        - columns: list of column names
        - rows: iterable of row sequences (list/tuple) matching columns length
        - recreate: drop/recreate tables before inserting

        Returns: number of rows inserted
        """
        cols = [str(c) for c in columns]
        self.initialize(cols, recreate=recreate)

        conn = self._ensure_conn()
        cur = conn.cursor()

        col_list_sql = ", ".join([f'"{c}"' for c in cols])
        placeholders = ", ".join(["?"] * len(cols))
        sql = f'INSERT INTO "data" ({col_list_sql}) VALUES ({placeholders})'

        inserted = 0
        batch: List[Tuple[Any, ...]] = []

        for r in rows:
            row_seq = list(r)
            if len(row_seq) != len(cols):
                raise ValueError(f"Row length {len(row_seq)} does not match column length {len(cols)}.")
            # Store everything as TEXT-ish (sqlite will coerce)
            batch.append(tuple("" if v is None else str(v) for v in row_seq))
            if len(batch) >= batch_size:
                cur.executemany(sql, batch)
                inserted += len(batch)
                batch.clear()

        if batch:
            cur.executemany(sql, batch)
            inserted += len(batch)

        conn.commit()
        return inserted

    def import_dicts(
        self,
        rows: Iterable[Mapping[str, Any]],
        *,
        recreate: bool = True,
        batch_size: int = 500,
    ) -> int:
        """
        Import from an iterable of dict-like rows.

        Column list is derived from the first row's keys, preserving order.

        Returns: number of rows inserted
        """
        iterator = iter(rows)
        first = next(iterator, None)
        if first is None:
            raise ValueError("rows is empty; cannot infer columns.")

        cols = list(first.keys())
        all_rows = [first]  # include first
        all_rows.extend(iterator)

        def row_to_seq(d: Mapping[str, Any]) -> List[Any]:
            return [d.get(c) for c in cols]

        return self.import_rows(cols, (row_to_seq(d) for d in all_rows), recreate=recreate, batch_size=batch_size)

    # -----------------------------------------------------------------
    # Read-only table shape helpers (data table)
    # -----------------------------------------------------------------
    def row_count(self) -> int:
        conn = self._ensure_conn()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) AS n FROM "data"')
        return int(cur.fetchone()[0])

    def column_count(self) -> int:
        return len(self.columns())

    def columns(self) -> List[str]:
        conn = self._ensure_conn()
        cur = conn.cursor()
        cur.execute("PRAGMA table_info('data')")
        # PRAGMA table_info: (cid, name, type, notnull, dflt_value, pk)
        cols = [str(r[1]) for r in cur.fetchall()]
        # hide processed from the public "imported columns" view?
        # You asked for column_count / columns: for a user script, it is usually
        # more helpful to see the imported columns only, but the spec includes
        # processed as part of data schema. We'll EXCLUDE it from "columns()"
        # and treat it as internal tracking.
        return [c for c in cols if c != "processed"]

    def get_column_index(self, name: str) -> int:
        cols = self.columns()
        if name not in cols:
            raise KeyError(f"Column not found: {name}")
        return int(cols.index(name))

    def get_column_name(self, index: int) -> str:
        cols = self.columns()
        if index < 0 or index >= len(cols):
            raise IndexError(f"Column index out of range: {index}")
        return cols[int(index)]

    # -----------------------------------------------------------------
    # Indexing model:
    # - Public "row index" is 0-based ordered by rowid ascending.
    # - Internal tracking uses rowid (stable within db file).
    # -----------------------------------------------------------------
    def _rowid_for_index(self, index: int) -> int:
        if index < 0:
            raise IndexError(f"Row index out of range: {index}")
        conn = self._ensure_conn()
        cur = conn.cursor()
        cur.execute('SELECT rowid FROM "data" ORDER BY rowid LIMIT 1 OFFSET ?', (int(index),))
        row = cur.fetchone()
        if row is None:
            raise IndexError(f"Row index out of range: {index}")
        return int(row[0])

    def _index_for_rowid(self, rowid: int) -> int:
        conn = self._ensure_conn()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "data" WHERE rowid < ?', (int(rowid),))
        return int(cur.fetchone()[0])

    # -----------------------------------------------------------------
    # Read-only row/cell access (data table)
    # -----------------------------------------------------------------
    def get_row(self, index: int) -> Dict[str, Any]:
        """
        Return a specific row (0-based, ordered by rowid).
        Returns only imported columns (excludes processed).
        """
        rowid = self._rowid_for_index(index)
        conn = self._ensure_conn()
        cur = conn.cursor()

        cols = self.columns()
        col_sql = ", ".join([f'"{c}"' for c in cols])
        cur.execute(f'SELECT {col_sql} FROM "data" WHERE rowid = ?', (rowid,))
        r = cur.fetchone()
        if r is None:
            raise IndexError(f"Row index out of range: {index}")

        return {cols[i]: r[i] for i in range(len(cols))}

    def get_cell(self, row_index: int, column: Union[int, str]) -> Any:
        """
        Return a specific cell value.
        column can be 0-based index or column name.
        """
        rowid = self._rowid_for_index(row_index)
        col_name = self.get_column_name(column) if isinstance(column, int) else str(column)

        if col_name not in self.columns():
            raise KeyError(f"Column not found: {col_name}")

        conn = self._ensure_conn()
        cur = conn.cursor()
        cur.execute(f'SELECT "{col_name}" FROM "data" WHERE rowid = ?', (rowid,))
        r = cur.fetchone()
        return None if r is None else r[0]

    def column_values(self, column: Union[int, str]) -> List[Any]:
        """
        Return all values for a given column (row order by rowid).
        """
        col_name = self.get_column_name(column) if isinstance(column, int) else str(column)
        if col_name not in self.columns():
            raise KeyError(f"Column not found: {col_name}")

        conn = self._ensure_conn()
        cur = conn.cursor()
        cur.execute(f'SELECT "{col_name}" FROM "data" ORDER BY rowid')
        return [r[0] for r in cur.fetchall()]

    # -----------------------------------------------------------------
    # Searching (read-only)
    # - We search only imported columns by default (exclude processed).
    # -----------------------------------------------------------------
    def search_contains(
        self,
        needle: str,
        *,
        case_sensitive: bool = False,
        columns: Optional[Sequence[Union[int, str]]] = None,
    ) -> List[CellMatch]:
        """
        Substring search across specified columns (or all imported columns).
        Returns CellMatch per matching cell.
        """
        if needle is None:
            raise ValueError("needle must be a string.")
        needle_s = str(needle)

        col_names = self._resolve_search_columns(columns)
        if not col_names:
            return []

        conn = self._ensure_conn()
        cur = conn.cursor()

        # Pull candidate rows and evaluate per-cell for accurate CellMatch emission
        col_sql = ", ".join([f'"{c}"' for c in col_names])
        cur.execute(f'SELECT rowid, {col_sql} FROM "data" ORDER BY rowid')
        rows = cur.fetchall()

        results: List[CellMatch] = []
        for row in rows:
            rowid = int(row[0])
            row_index = self._index_for_rowid(rowid)
            values = row[1:]

            for i, col in enumerate(col_names):
                v = values[i]
                if v is None:
                    continue
                hay = str(v)
                if case_sensitive:
                    ok = needle_s in hay
                else:
                    ok = needle_s.lower() in hay.lower()
                if ok:
                    results.append(CellMatch(row=row_index, column=str(col), value=v))

        return results

    def search_exact(
        self,
        value: str,
        *,
        case_sensitive: bool = False,
        columns: Optional[Sequence[Union[int, str]]] = None,
    ) -> List[CellMatch]:
        """
        Exact match search across specified columns (or all imported columns).
        Returns CellMatch per matching cell.
        """
        if value is None:
            raise ValueError("value must be a string.")
        value_s = str(value)

        col_names = self._resolve_search_columns(columns)
        if not col_names:
            return []

        conn = self._ensure_conn()
        cur = conn.cursor()

        col_sql = ", ".join([f'"{c}"' for c in col_names])
        cur.execute(f'SELECT rowid, {col_sql} FROM "data" ORDER BY rowid')
        rows = cur.fetchall()

        results: List[CellMatch] = []
        for row in rows:
            rowid = int(row[0])
            row_index = self._index_for_rowid(rowid)
            values = row[1:]

            for i, col in enumerate(col_names):
                v = values[i]
                if v is None:
                    continue
                hay = str(v)
                if case_sensitive:
                    ok = hay == value_s
                else:
                    ok = hay.lower() == value_s.lower()
                if ok:
                    results.append(CellMatch(row=row_index, column=str(col), value=v))

        return results

    def search_contains_rows(
        self,
        needle: str,
        *,
        case_sensitive: bool = False,
        columns: Optional[Sequence[Union[int, str]]] = None,
    ) -> List[int]:
        matches = self.search_contains(needle, case_sensitive=case_sensitive, columns=columns)
        return sorted({m.row for m in matches})

    def search_exact_rows(
        self,
        value: str,
        *,
        case_sensitive: bool = False,
        columns: Optional[Sequence[Union[int, str]]] = None,
    ) -> List[int]:
        matches = self.search_exact(value, case_sensitive=case_sensitive, columns=columns)
        return sorted({m.row for m in matches})

    def _resolve_search_columns(self, columns: Optional[Sequence[Union[int, str]]]) -> List[str]:
        all_cols = self.columns()
        if columns is None:
            return all_cols

        resolved: List[str] = []
        for c in columns:
            if isinstance(c, int):
                resolved.append(self.get_column_name(c))
            elif isinstance(c, str):
                if c not in all_cols:
                    raise KeyError(f"Column not found: {c}")
                resolved.append(c)
            else:
                raise TypeError("columns entries must be int indices or str column names.")
        return resolved

    # -----------------------------------------------------------------
    # Tracking operations (mutating by design)
    # -----------------------------------------------------------------
    def pop(self) -> Tuple[Optional[int], Optional[Dict[str, Any]]]:
        """
        Pop the next unprocessed row.

        Returns:
          (rowid, row_dict)  if found
          (None, None)       if no unprocessed rows remain

        row_dict includes only imported columns (excludes processed).
        rowid is required to mark_as_processed and write_error reliably.
        """
        conn = self._ensure_conn()
        cur = conn.cursor()

        cols = self.columns()
        col_sql = ", ".join([f'"{c}"' for c in cols])

        cur.execute(
            f'SELECT rowid, {col_sql} FROM "data" WHERE processed = 0 ORDER BY rowid LIMIT 1'
        )
        r = cur.fetchone()
        if r is None:
            return (None, None)

        rowid = int(r[0])
        values = r[1:]
        row_dict = {cols[i]: values[i] for i in range(len(cols))}
        return (rowid, row_dict)

    def mark_as_processed(self, rowid: int) -> bool:
        """
        Mark a row as processed by rowid.
        Returns True if an update occurred.
        """
        conn = self._ensure_conn()
        cur = conn.cursor()
        cur.execute('UPDATE "data" SET processed = 1 WHERE rowid = ?', (int(rowid),))
        conn.commit()
        return cur.rowcount > 0

    def write_error(
        self,
        row: Mapping[str, Any],
        error_msg: str,
        *,
        rowid: Optional[int] = None,
    ) -> None:
        """
        Write an error row into the errors table.

        - row: mapping of imported columns -> values (ideally the same dict returned by pop()).
        - error_msg: message to store in errors.error_msg
        - rowid: optional; used only for logging/context (not stored).

        The errors table schema is:
          imported columns + error_msg
        """
        if error_msg is None:
            error_msg = ""

        cols = self.columns()
        values = [row.get(c) for c in cols]
        values = [("" if v is None else str(v)) for v in values]
        values.append(str(error_msg))

        conn = self._ensure_conn()
        cur = conn.cursor()

        col_list_sql = ", ".join([f'"{c}"' for c in cols] + ['"error_msg"'])
        placeholders = ", ".join(["?"] * (len(cols) + 1))
        sql = f'INSERT INTO "errors" ({col_list_sql}) VALUES ({placeholders})'

        _maybe_log(
            self._logger,
            "SqliteTracker.write_error",
            level=30,
            context={"rowid": rowid, "error_msg": str(error_msg)[:200]},
        )

        cur.execute(sql, tuple(values))
        conn.commit()

    # -----------------------------------------------------------------
    # Convenience: unprocessed counts (useful in scripts)
    # -----------------------------------------------------------------
    def unprocessed_count(self) -> int:
        conn = self._ensure_conn()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM "data" WHERE processed = 0')
        return int(cur.fetchone()[0])
