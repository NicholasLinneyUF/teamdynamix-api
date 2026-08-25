from __future__ import annotations

import sqlite3
from dataclasses import replace
from pathlib import Path

from teamdynamix.tools import (
    compute_fingerprint,
    read_fingerprint_from_db,
    write_fingerprint_to_db,
)


def _fingerprint(tmp_path: Path):
    source = tmp_path / "records.csv"
    source.write_text("id,name\n1,Ada\n", encoding="utf-8")
    return compute_fingerprint(
        source,
        fingerprint_fields=("columns", "file_sha256", "fingerprint_version"),
        fingerprint_version="1",
    )


def test_path_database_round_trip(tmp_path: Path) -> None:
    fingerprint = _fingerprint(tmp_path)
    db_path = tmp_path / "tracker.sqlite"

    write_fingerprint_to_db(db_path, fingerprint)

    assert read_fingerprint_from_db(db_path) == fingerprint
    with sqlite3.connect(db_path) as conn:
        schema = conn.execute("PRAGMA table_info('meta')").fetchall()
    assert [(row[1], row[2], row[5]) for row in schema] == [
        ("key", "TEXT", 1),
        ("value", "TEXT", 0),
    ]


def test_existing_connection_is_committed_and_left_open(tmp_path: Path) -> None:
    fingerprint = _fingerprint(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    conn = sqlite3.connect(db_path)
    try:
        write_fingerprint_to_db(conn, fingerprint)
        assert read_fingerprint_from_db(conn) == fingerprint

        with sqlite3.connect(db_path) as observer:
            assert observer.execute('SELECT COUNT(*) FROM "meta"').fetchone()[0] == 8

        assert conn.execute("SELECT 1").fetchone()[0] == 1
    finally:
        conn.close()


def test_missing_or_partial_metadata_returns_none(tmp_path: Path) -> None:
    db_path = tmp_path / "tracker.sqlite"

    assert read_fingerprint_from_db(db_path) is None
    with sqlite3.connect(db_path) as conn:
        conn.execute('INSERT INTO "meta" (key, value) VALUES (?, ?)', ("fingerprint_path", "x"))
        conn.commit()

    assert read_fingerprint_from_db(db_path) is None


def test_overwrite_removes_stale_optional_version(tmp_path: Path) -> None:
    fingerprint = _fingerprint(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    write_fingerprint_to_db(db_path, fingerprint)

    unversioned = replace(fingerprint, fingerprint_version=None)
    write_fingerprint_to_db(db_path, unversioned)

    assert read_fingerprint_from_db(db_path) == unversioned
    with sqlite3.connect(db_path) as conn:
        result = conn.execute(
            'SELECT value FROM "meta" WHERE key = ?', ("fingerprint_version",)
        ).fetchone()
    assert result is None


def test_rewrite_replaces_all_persisted_values(tmp_path: Path) -> None:
    fingerprint = _fingerprint(tmp_path)
    db_path = tmp_path / "tracker.sqlite"
    write_fingerprint_to_db(db_path, fingerprint)
    changed = replace(
        fingerprint,
        file_sha256="f" * 64,
        row_count=99,
        columns=("new", "shape"),
        fingerprint_fields=("row_count", "columns"),
        fingerprint_version="2",
    )

    write_fingerprint_to_db(db_path, changed)

    assert read_fingerprint_from_db(db_path) == changed
