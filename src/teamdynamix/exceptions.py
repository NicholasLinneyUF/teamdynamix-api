# =====================================================================
# FILE: src/teamdynamix/exceptions.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class TdxError(Exception):
    """Base exception for the TeamDynamix client."""


class ConfigError(TdxError):
    """Raised when configuration is missing or invalid."""


class AuthError(TdxError):
    """Raised when authentication fails or credentials are missing."""


@dataclass(slots=True)
class HttpError(TdxError):
    """Raised for HTTP responses with non-success status codes."""
    status_code: int
    method: str
    url: str
    message: str = ""
    response_text: str = ""


class TdxTimeoutError(TdxError):
    """Raised when a request times out."""


class TdxRequestError(TdxError):
    """Raised for non-timeout transport errors (connection errors, etc.)."""
