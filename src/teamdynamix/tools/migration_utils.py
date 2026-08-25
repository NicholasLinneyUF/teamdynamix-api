"""Local migration tracker preparation with explicit restart semantics."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Literal, Protocol

from teamdynamix.exceptions import MigrationStateError

from .data_utils import assert_fingerprint_match, compute_fingerprint, resolve_data_path
from .sqlite_utils import (
    SqliteTracker,
    archive_db_file,
    create_db_file,
    read_fingerprint_from_db,
    write_fingerprint_to_db,
)

MigrationMode = Literal["new", "overwrite", "resume"]


class MigrationTable(Protocol):
    """Minimum read-only table surface accepted by tracker preparation."""

    def columns(self) -> Sequence[str]: ...

    def row_count(self) -> int: ...

    def get_row(self, index: int) -> Mapping[str, Any]: ...


def _log(logger: Callable[[str], Any] | None, message: str) -> None:
    if logger is not None:
        logger(message)


def _import_table(tracker: SqliteTracker, table: MigrationTable) -> int:
    columns = tuple(str(column) for column in table.columns())
    rows = (
        tuple(table.get_row(index).get(column) for column in columns)
        for index in range(table.row_count())
    )
    return tracker.import_rows(columns, rows, recreate=True)


def prepare_sqlite_tracker(
    mode: MigrationMode | str,
    db_path: str | Path,
    source_path: str | Path,
    table: MigrationTable,
    logger: Callable[[str], Any] | None = None,
) -> SqliteTracker:
    """Prepare a tracker for a new, overwritten, or safely resumed migration."""
    if mode not in {"new", "overwrite", "resume"}:
        raise MigrationStateError(
            f"Unsupported migration mode: {mode}",
            details={"mode": mode},
        )

    resolved_db = resolve_data_path(db_path)
    current_fingerprint = compute_fingerprint(source_path)

    if mode == "resume":
        if not resolved_db.exists():
            raise MigrationStateError(
                f"Cannot resume: tracker database does not exist: {resolved_db}",
                details={"db_path": str(resolved_db)},
            )
        stored_fingerprint = read_fingerprint_from_db(resolved_db)
        if stored_fingerprint is None:
            raise MigrationStateError(
                "Cannot resume: tracker database has no complete source fingerprint",
                details={"db_path": str(resolved_db)},
            )
        assert_fingerprint_match(stored_fingerprint, current_fingerprint)
        _log(logger, f"Resuming existing SQLite tracker: {resolved_db}")
        return SqliteTracker(resolved_db)

    if mode == "new" and resolved_db.exists():
        backup_path, _ = archive_db_file(resolved_db)
        _log(logger, f"Archived existing SQLite tracker to: {backup_path}")
    else:
        create_db_file(resolved_db, overwrite=True)

    tracker = SqliteTracker(resolved_db)
    inserted = _import_table(tracker, table)
    write_fingerprint_to_db(resolved_db, current_fingerprint)
    _log(logger, f"Prepared SQLite tracker with {inserted} rows: {resolved_db}")
    return tracker
