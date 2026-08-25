# =====================================================================
# FILE: src/teamdynamix/exceptions.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass


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

    def __str__(self) -> str:
        """Return a concise, response-body-free description of the failure."""
        return self.message or f"HTTP {self.status_code} {self.method.upper()} {self.url}"


class TdxTimeoutError(TdxError):
    """Raised when a request times out."""


class TdxRequestError(TdxError):
    """Raised for non-timeout transport errors (connection errors, etc.)."""
