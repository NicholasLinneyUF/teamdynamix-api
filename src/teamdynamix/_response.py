"""Internal, stateless normalization for variable TeamDynamix JSON shapes.

Pure module functions were selected instead of a mixin: normalization has no
instance state, explicit imports make client dependencies visible, and avoiding
inheritance prevents MRO/API-surface concerns as clients evolve.
"""

from __future__ import annotations

from typing import Any


def as_list_of_dicts(data: Any) -> list[dict[str, Any]]:
    """Return dict payloads as a list and discard non-dict list entries."""
    if not data:
        return []
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def as_dict(data: Any) -> dict[str, Any] | None:
    """Return a non-empty dict payload, otherwise ``None``."""
    if not data:
        return None
    return data if isinstance(data, dict) else None


def first_dict_or_none(data: Any) -> dict[str, Any] | None:
    """Return a dict payload or the first list entry when that entry is a dict."""
    if data is None:
        return None
    if isinstance(data, list):
        if not data:
            return None
        first = data[0]
        return first if isinstance(first, dict) else None
    return data if isinstance(data, dict) else None
