from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from teamdynamix.exceptions import FingerprintMismatchError
from teamdynamix.tools import (
    DEFAULT_FINGERPRINT_FIELDS,
    assert_fingerprint_match,
    compare_fingerprint,
    compute_fingerprint,
    fingerprints_match,
)


def _write_csv(path: Path, contents: str) -> None:
    path.write_text(contents, encoding="utf-8")


def test_compute_fingerprint_records_identity_and_csv_shape(tmp_path: Path) -> None:
    source = tmp_path / "records.csv"
    _write_csv(source, "id,name\n1,Ada\n2,Grace\n")

    fingerprint = compute_fingerprint(source)

    assert fingerprint.path == str(source.resolve())
    assert fingerprint.algorithm == "sha256"
    assert len(fingerprint.file_sha256) == 64
    assert fingerprint.mtime_ns == source.stat().st_mtime_ns
    assert fingerprint.row_count == 2
    assert fingerprint.columns == ("id", "name")
    assert fingerprint.fingerprint_fields == DEFAULT_FINGERPRINT_FIELDS
    assert fingerprint.fingerprint_version is None


def test_empty_csv_has_no_columns_or_data_rows(tmp_path: Path) -> None:
    source = tmp_path / "empty.csv"
    _write_csv(source, "")

    fingerprint = compute_fingerprint(source)

    assert fingerprint.columns == ()
    assert fingerprint.row_count == 0


def test_identical_fingerprints_match(tmp_path: Path) -> None:
    source = tmp_path / "records.csv"
    _write_csv(source, "id\n1\n")
    left = compute_fingerprint(source)
    right = compute_fingerprint(source)

    assert fingerprints_match(left, right)
    assert compare_fingerprint(left, right).is_empty()
    assert compare_fingerprint(left, right).brief() == ""
    assert_fingerprint_match(left, right)


def test_compare_reports_content_shape_and_policy_changes(tmp_path: Path) -> None:
    source = tmp_path / "records.csv"
    _write_csv(source, "id,name\n1,Ada\n")
    left = compute_fingerprint(source)
    right = replace(
        left,
        file_sha256="0" * 64,
        columns=("id", "display_name"),
        row_count=2,
        fingerprint_fields=("columns", "row_count", "file_sha256"),
    )

    diff = compare_fingerprint(left, right)

    assert set(diff.mismatches) == {
        "fingerprint_fields",
        "file_sha256",
        "columns",
        "row_count",
    }
    assert not diff.is_empty()
    assert not fingerprints_match(left, right)
    assert len(diff.brief(max_len=30)) <= 30


def test_assert_match_raises_tools_exception_with_structured_details(tmp_path: Path) -> None:
    source = tmp_path / "records.csv"
    _write_csv(source, "id\n1\n")
    left = compute_fingerprint(source)
    right = replace(left, mtime_ns=left.mtime_ns + 1)

    with pytest.raises(FingerprintMismatchError) as caught:
        assert_fingerprint_match(left, right)

    assert caught.value.details == {
        "mismatches": {"mtime_ns": (left.mtime_ns, right.mtime_ns)}
    }


def test_comparison_uses_union_of_declared_fields(tmp_path: Path) -> None:
    source = tmp_path / "records.csv"
    _write_csv(source, "id\n1\n")
    left = compute_fingerprint(source, fingerprint_fields=("file_sha256",))
    right = replace(
        left,
        mtime_ns=left.mtime_ns + 1,
        fingerprint_fields=("file_sha256", "mtime_ns"),
    )

    diff = compare_fingerprint(left, right)

    assert "fingerprint_fields" in diff.mismatches
    assert diff.mismatches["mtime_ns"] == (left.mtime_ns, right.mtime_ns)


def test_unknown_hash_algorithm_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "records.csv"
    _write_csv(source, "id\n1\n")

    with pytest.raises(ValueError, match="Unsupported fingerprint algorithm"):
        compute_fingerprint(source, algorithm="not-a-real-algorithm")
