from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from teamdynamix.exceptions import FingerprintMismatchError, MigrationStateError
from teamdynamix.tools import prepare_sqlite_tracker


@dataclass
class FakeTable:
    headers: tuple[str, ...]
    rows: tuple[dict[str, Any], ...]

    def columns(self) -> tuple[str, ...]:
        return self.headers

    def row_count(self) -> int:
        return len(self.rows)

    def get_row(self, index: int) -> dict[str, Any]:
        return self.rows[index]


def _source_and_table(tmp_path: Path) -> tuple[Path, FakeTable]:
    source = tmp_path / "people.csv"
    source.write_text("id,name\n1,Ada\n2,Grace\n", encoding="utf-8")
    return source, FakeTable(
        headers=("id", "name"),
        rows=({"id": "1", "name": "Ada"}, {"id": "2", "name": "Grace"}),
    )


def test_new_creates_imported_fingerprinted_tracker(tmp_path: Path) -> None:
    source, table = _source_and_table(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    messages: list[str] = []

    tracker = prepare_sqlite_tracker("new", db_path, source, table, messages.append)
    try:
        assert tracker.row_count() == 2
        assert tracker.columns() == ["id", "name"]
        assert tracker.get_row(1) == {"id": "2", "name": "Grace"}
    finally:
        tracker.close()
    assert any("Prepared SQLite tracker with 2 rows" in message for message in messages)


def test_new_archives_an_existing_database(tmp_path: Path) -> None:
    source, table = _source_and_table(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE legacy (value TEXT)")
        conn.execute("INSERT INTO legacy VALUES ('preserved')")

    tracker = prepare_sqlite_tracker("new", db_path, source, table)
    tracker.close()

    backup_path = Path(f"{db_path}.bak")
    assert backup_path.exists()
    with sqlite3.connect(backup_path) as conn:
        assert conn.execute("SELECT value FROM legacy").fetchone()[0] == "preserved"


def test_overwrite_recreates_without_archiving(tmp_path: Path) -> None:
    source, table = _source_and_table(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE legacy (value TEXT)")

    tracker = prepare_sqlite_tracker("overwrite", db_path, source, table)
    try:
        assert tracker.row_count() == 2
    finally:
        tracker.close()
    assert not Path(f"{db_path}.bak").exists()
    with sqlite3.connect(db_path) as conn:
        assert conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='legacy'"
        ).fetchone()[0] == 0


def test_resume_preserves_existing_progress_without_reimport(tmp_path: Path) -> None:
    source, table = _source_and_table(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    initial = prepare_sqlite_tracker("new", db_path, source, table)
    rowid, _ = initial.pop()
    assert rowid is not None
    initial.mark_as_processed(rowid)
    initial.close()

    resumed = prepare_sqlite_tracker("resume", db_path, source, table)
    try:
        assert resumed.row_count() == 2
        assert resumed.unprocessed_count() == 1
    finally:
        resumed.close()


def test_resume_rejects_missing_database(tmp_path: Path) -> None:
    source, table = _source_and_table(tmp_path)

    with pytest.raises(MigrationStateError, match="database does not exist"):
        prepare_sqlite_tracker("resume", tmp_path / "missing.sqlite", source, table)


def test_resume_rejects_missing_fingerprint(tmp_path: Path) -> None:
    source, table = _source_and_table(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE placeholder (value TEXT)")

    with pytest.raises(MigrationStateError, match="no complete source fingerprint"):
        prepare_sqlite_tracker("resume", db_path, source, table)


def test_resume_rejects_changed_source(tmp_path: Path) -> None:
    source, table = _source_and_table(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    tracker = prepare_sqlite_tracker("new", db_path, source, table)
    tracker.close()
    source.write_text("id,name\n1,Ada\n2,Grace Hopper\n", encoding="utf-8")

    with pytest.raises(FingerprintMismatchError) as caught:
        prepare_sqlite_tracker("resume", db_path, source, table)

    assert caught.value.details is not None
    assert "file_sha256" in caught.value.details["mismatches"]


def test_invalid_mode_is_rejected(tmp_path: Path) -> None:
    source, table = _source_and_table(tmp_path)

    with pytest.raises(MigrationStateError, match="Unsupported migration mode"):
        prepare_sqlite_tracker("continue", tmp_path / "tracker.sqlite", source, table)
