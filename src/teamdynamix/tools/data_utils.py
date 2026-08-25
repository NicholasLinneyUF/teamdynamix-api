"""Shared, local-only data normalization and path helpers.

This module has no dependency on TeamDynamix API clients, sessions, transport,
or authentication. It centralizes small helpers used by script-oriented tools.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


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
