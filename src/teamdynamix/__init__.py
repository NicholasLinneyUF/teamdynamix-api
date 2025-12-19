# src/teamdynamix/__init__.py
from __future__ import annotations

__version__ = "0.0.0-pre-alpha.11"

# Exceptions (public)
from .exceptions import (
    TdxError,
    ConfigError,
    AuthError,
    HttpError,
    TdxTimeoutError,
    TdxRequestError,
)

# Core
from .config import Config
from .logger import Logger
from .event import Event
from .auth import Auth
from .session import Session
from .transport import Transport, PatchPayload

# Clients
from .accounts import Accounts, Account
from .applications import Applications, Application
from .attributes import Attributes, Attribute, AttributeChoice
from .functional_roles import FunctionalRoles, FunctionalRole
from .groups import Groups, Group
from .people import People, Person
from .projects import Projects, Project
from .service_catalog import ServiceCatalog, Service
from .tickets import (
    Tickets,
    Ticket,
    TicketPriorities,
    TicketTypes,
    TicketStatuses,
    TicketSources,
)

__all__ = [
    "__version__",
    # Exceptions
    "TdxError",
    "ConfigError",
    "AuthError",
    "HttpError",
    "TdxTimeoutError",
    "TdxRequestError",
    # Core
    "Config",
    "Logger",
    "Event",
    "Auth",
    "Session",
    "Transport",
    "PatchPayload",
    # Clients
    "Accounts",
    "Account",
    "Applications",
    "Application",
    "Attributes",
    "Attribute",
    "AttributeChoice",
    "FunctionalRoles",
    "FunctionalRole",
    "Groups",
    "Group",
    "People",
    "Person",
    "Projects",
    "Project",
    "ServiceCatalog",
    "Service",
    "Tickets",
    "Ticket",
    "TicketPriorities",
    "TicketTypes",
    "TicketStatuses",
    "TicketSources",
]
