# src/teamdynamix/__init__.py
from __future__ import annotations

__version__ = "0.0.0-pre-alpha.10"

# Core
from .config import Config
from .logger import Logger
from .event import Event
from .auth import Auth
from .session import Session
from .transport import Transport, PatchPayload

# Clients
from .people import People, Person

__all__ = [
    "__version__",
    # Core
    "Config",
    "Logger",
    "Event",
    "Auth",
    "Session",
    "Transport",
    "PatchPayload",
    # Clients
    "People",
    "Person",
]
