"""Shared, local-only data normalization and path helpers.

This module has no dependency on TeamDynamix API clients, sessions, transport,
or authentication. It centralizes small helpers used by script-oriented tools.
"""

from __future__ import annotations

import csv
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from teamdynamix.exceptions import FingerprintMismatchError


DEFAULT_FINGERPRINT_FIELDS = ("file_sha256", "columns", "row_count", "mtime_ns")


@dataclass(frozen=True, slots=True)
class FileFingerprint:
    """Immutable identity metadata for a local delimited data file."""

    path: str
    algorithm: str
    file_sha256: str
    mtime_ns: int
    row_count: int
    columns: tuple[str, ...]
    fingerprint_fields: tuple[str, ...] = DEFAULT_FINGERPRINT_FIELDS
    fingerprint_version: str | None = None


@dataclass(frozen=True, slots=True)
class FingerprintDiff:
    """Field-level differences between two file fingerprints."""

    mismatches: dict[str, tuple[Any, Any]]

    def is_empty(self) -> bool:
        """Return whether the compared fingerprints match."""
        return not self.mismatches

    def brief(self, max_len: int = 200) -> str:
        """Render a compact, optionally truncated mismatch summary."""
        if max_len < 0:
            raise ValueError("max_len must be non-negative")
        summary = "; ".join(
            f"{field}: {left!r} != {right!r}"
            for field, (left, right) in self.mismatches.items()
        )
        if len(summary) <= max_len:
            return summary
        if max_len <= 3:
            return "." * max_len
        return f"{summary[: max_len - 3]}..."


def resolve_data_path(
    path: str | Path,
    base_dir: str | Path | None = None,
    env_var: str = "TDX_DATA_DIR",
) -> Path:
    """Resolve a data path using absolute, existing base/env, then cwd precedence.

    Intermediate candidates under ``base_dir`` or ``env_var`` are selected only
    when they already exist. The current-working-directory fallback is returned
    whether or not it exists so callers retain control over validation.
    """
    candidate_path = Path(path)
    if candidate_path.is_absolute():
        return candidate_path

    if base_dir is not None:
        base_candidate = Path(base_dir) / candidate_path
        if base_candidate.exists():
            return base_candidate

    env_base = os.environ.get(env_var)
    if env_base:
        env_candidate = Path(env_base) / candidate_path
        if env_candidate.exists():
            return env_candidate

    return Path.cwd() / candidate_path


def clean_key(value: str) -> str:
    """Trim whitespace and one matching pair of surrounding quotes."""
    cleaned = value.strip()
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        cleaned = cleaned[1:-1].strip()
    return cleaned


def clean_str(value: Any) -> str:
    """Normalize strings with :func:`clean_key`, map ``None`` to an empty string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return clean_key(value)
    return str(value)


def compute_fingerprint(
    path: str | Path,
    *,
    algorithm: str = "sha256",
    fingerprint_fields: tuple[str, ...] = DEFAULT_FINGERPRINT_FIELDS,
    fingerprint_version: str | None = None,
) -> FileFingerprint:
    """Compute file identity and CSV-shape metadata without loading all rows."""
    resolved = Path(path).expanduser().resolve()
    normalized_algorithm = algorithm.lower()
    try:
        digest = hashlib.new(normalized_algorithm)
    except ValueError as exc:
        raise ValueError(f"Unsupported fingerprint algorithm: {algorithm}") from exc

    with resolved.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)

    with resolved.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        columns = tuple(next(reader, ()))
        row_count = sum(1 for _ in reader)

    return FileFingerprint(
        path=str(resolved),
        algorithm=normalized_algorithm,
        file_sha256=digest.hexdigest(),
        mtime_ns=resolved.stat().st_mtime_ns,
        row_count=row_count,
        columns=columns,
        fingerprint_fields=tuple(fingerprint_fields),
        fingerprint_version=fingerprint_version,
    )


def compare_fingerprint(left: FileFingerprint, right: FileFingerprint) -> FingerprintDiff:
    """Compare algorithms, field policies, and every field declared by either side."""
    mismatches: dict[str, tuple[Any, Any]] = {}
    if left.algorithm != right.algorithm:
        mismatches["algorithm"] = (left.algorithm, right.algorithm)
    if left.fingerprint_fields != right.fingerprint_fields:
        mismatches["fingerprint_fields"] = (
            left.fingerprint_fields,
            right.fingerprint_fields,
        )

    fields = tuple(dict.fromkeys((*left.fingerprint_fields, *right.fingerprint_fields)))
    for field in fields:
        if not hasattr(left, field) or not hasattr(right, field):
            mismatches[field] = (getattr(left, field, None), getattr(right, field, None))
            continue
        left_value = getattr(left, field)
        right_value = getattr(right, field)
        if left_value != right_value:
            mismatches[field] = (left_value, right_value)
    return FingerprintDiff(mismatches=mismatches)


def fingerprints_match(left: FileFingerprint, right: FileFingerprint) -> bool:
    """Return whether two fingerprints match under their declared policies."""
    return compare_fingerprint(left, right).is_empty()


def assert_fingerprint_match(left: FileFingerprint, right: FileFingerprint) -> None:
    """Raise when two fingerprints do not match under their declared policies."""
    diff = compare_fingerprint(left, right)
    if not diff.is_empty():
        raise FingerprintMismatchError(
            f"File fingerprints do not match: {diff.brief()}",
            details={"mismatches": diff.mismatches},
        )
