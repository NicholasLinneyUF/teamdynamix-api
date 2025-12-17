This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
config/
  sample.config.ini
docs/
  Architectural_Decisions.md
src/
  teamdynamix/
    __init__.py
    accounts.py
    applications.py
    attributes.py
    auth.py
    config.py
    event.py
    exceptions.py
    functional_roles.py
    groups.py
    logger.py
    people.py
    projects.py
    service_catalog.py
    session.py
    tickets.py
    transport.py
  py.typed
tests/
  test_people_endpoints.py
  test_ticket_endpoints.py
.editorconfig
.gitignore
MANIFEST.in
pyproject.toml
pytest.ini
```

# Files

## File: config/sample.config.ini
```
# =====================================================================
# FILE: config.ini (TEMPLATE)
# =====================================================================
# TeamDynamix Python Client - vNext Config
#
# Rules:
# - Config validates structure/types/required fields.
# - Session/Transport implement behaviors (timeouts, requests, logging).
# - Timeout: one knob. 10 seconds by default. Set to 0 to disable.
#
# ---------------------------------------------------------------------

[tdx]
tenant = yourtenant.domain.com
environment = production
; Optional override (rare; normally computed from tenant/environment)
; base_url = https://yourtenant.domain.com/productionWebApi

[auth]
; admin or user
mode = admin

; admin mode creds
beid = 00000000-0000-0000-0000-000000000000
webserviceskey = your_webservices_key_here

; user mode creds (only if mode=user)
; username = you@example.com
; password = your_password_here

[logging]
; Optional. Defaults: level=ERROR, log_dir=./logs, console=true
log_dir = ./logs
level = ERROR
console = true

[http]
; One knob. Default 10 seconds. Set 0 to disable timeouts.
default_timeout_seconds = 10
```

## File: docs/Architectural_Decisions.md
```markdown
# Architectural_Decisions.md

## Introduction

This document records the architectural decisions made during the design and implementation of the **TeamDynamix API Python library**.  
The library is a clean-slate implementation informed by prior working code, but **not constrained by backward compatibility**. The primary goals are:

- Strong alignment with **SOLID principles**, especially *Separation of Concerns*
- A **clear, explicit architecture** that mirrors the vendor’s API surface
- Minimal abstraction and minimal “magic”
- Predictable behavior suitable for scripting, automation, and long-term maintenance
- A structure that can **scale naturally** as additional TeamDynamix endpoints are added

The design favors:
- Explicit object roles
- Centralized cross-cutting behavior
- Lazy execution of network-dependent operations
- Typed representations only where they provide clear value

The sections below document the major architectural decisions, including **what was decided, why it was decided, and how it is implemented**.

---

## Decision 1: Session as the Composition Root

### What
`Session` is the **composition root** of the library. All core objects (`Config`, `Logger`, `Transport`, `Auth`) are instantiated and owned by `Session`.

### Why
- Centralizes object creation
- Prevents duplicated initialization logic
- Makes dependency flow explicit and testable
- Avoids “utility object sprawl” across client modules

### How
- `Session.__init__()` loads and validates `Config`
- `Session` constructs `Logger`, `Transport`, and `Auth`
- Client modules (e.g., `People`) receive a `Session` instance and nothing else

---

## Decision 2: Lazy Authentication

### What
Authentication is **lazy**: no network calls are made during object construction.

### Why
- Improves ergonomics (`Session(...)` should always succeed if config is valid)
- Avoids unexpected side effects during import or initialization
- Enables deterministic testing
- Defers failure until an authenticated request is actually needed

### How
- `Auth` does not authenticate during construction
- `Session.request()` triggers authentication implicitly when required
- `Session.authenticate()` exists as an *explicit, optional* way to force authentication early

---

## Decision 3: Single Transport Boundary

### What
All HTTP traffic goes through a single class: `Transport`.

### Why
- Ensures consistent timeout behavior
- Ensures consistent error handling
- Provides a single place to adapt vendor quirks
- Minimizes the surface area that touches `requests`

### How
- `Transport.request()` is the only place that calls `requests.request`
- Client modules never import or reference `requests`
- `Session.request()` delegates directly to `Transport.request()`

---

## Decision 4: Centralized JSON Patch Handling

### What
**JSON Patch (RFC 6902)** logic is implemented in `Transport`, not in individual client modules.

### Why
- TeamDynamix uses JSON Patch across multiple PATCH endpoints
- PATCH semantics are cross-cutting, not endpoint-specific
- Prevents duplicated or inconsistent PATCH implementations
- Keeps client modules aligned with vendor semantics

### How
- If `method == PATCH` and `json` is a `dict`, `Transport` converts it into a JSON Patch list
- If `json` is already a list, it is passed through unchanged
- `Transport` ensures the correct `Content-Type` header is set
- Client modules simply pass `json={"Field": "Value"}`

---

## Decision 5: Minimal, Typed DTOs

### What
Typed dataclasses (e.g., `Person`) represent **only commonly used fields**, not full API payloads.

### Why
- TeamDynamix payloads are large, nested, and volatile
- Over-modeling increases maintenance cost
- Most scripts only need a small subset of fields
- Full payloads should still be accessible when needed

### How
- `Person` includes identity and commonly referenced fields
- `People.get_raw()` returns the full raw dictionary
- Typed DTOs are used for *reading*, not for enforcing schema completeness

---

## Decision 6: Endpoint-Representative Client Modules

### What
Client modules map **directly** to vendor API endpoints and avoid “helper” abstractions.

### Why
- Keeps the library aligned with the vendor API surface
- Avoids opinionated behavior that may not generalize
- Makes future API changes easier to track and implement
- Reduces cognitive load for users familiar with TeamDynamix

### How
- Each public method corresponds to a specific API endpoint
- Convenience methods are added only when architecturally justified
- No hidden side effects or implicit workflows inside client modules

---

## Decision 7: Validation Belongs in Config

### What
All configuration validation happens in `Config`, not in `Session` or client modules.

### Why
- Validation is a configuration concern, not a runtime concern
- Keeps `Session` lightweight and focused on orchestration
- Enables fail-fast behavior at application startup

### How
- `Config.__post_init__()` validates required fields and semantics
- `Session` trusts that `Config` is valid
- Runtime errors are reserved for runtime conditions (network, permissions, etc.)

---

## Decision 8: Simple, Optional Timeouts

### What
Timeout support is **minimal and optional**.

### Why
- Avoids over-engineering timeout policies
- Matches common scripting and automation needs
- Prevents crashes due to unhandled timeouts
- Keeps the configuration surface small

### How
- Timeout is configured once in `Config`
- `Transport` applies the timeout uniformly
- Timeout can be disabled by configuration (`0` or `None`)
- No retry or backoff logic is included by default

---

## Decision 9: Explicit Public API Surface

### What
The public API is explicitly defined via `__all__` in `teamdynamix/__init__.py`.

### Why
- Prevents accidental exposure of internal helpers
- Makes the intended usage surface obvious
- Improves long-term maintainability

### How
- All public classes and exceptions are imported and listed explicitly
- Internal helpers remain unexported unless intentionally exposed

---

## Summary

The architecture intentionally favors:

- **Clarity over cleverness**
- **Explicit boundaries over implicit behavior**
- **Vendor alignment over abstraction purity**

As a result, the library is:
- Easy to reason about
- Predictable in behavior
- Resistant to accidental complexity
- Well-positioned for incremental growth

This document should be updated as new architectural decisions are made.
```

## File: src/teamdynamix/__init__.py
```python
# src/teamdynamix/__init__.py
from __future__ import annotations

__version__ = "0.1.0"

# Core
from .config import Config
from .logger import Logger
from .event import Event
from .auth import Auth
from .session import Session
from .transport import Transport  # + PatchPayload once implemented

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
```

## File: src/teamdynamix/accounts.py
```python
# =====================================================================
# FILE: src/teamdynamix/accounts.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _first_or_none(data: Any) -> Optional[Dict[str, Any]]:
    """
    TDX endpoints sometimes return:
      - object (dict)
      - list[dict]
      - empty list []
    Normalize to first dict or None.
    """
    if data is None:
        return None
    if isinstance(data, list):
        if not data:
            return None
        first = data[0]
        return first if isinstance(first, dict) else None
    return data if isinstance(data, dict) else None


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Account:
    """
    Minimal Account DTO. Keep intentionally small; use Accounts.get_raw(...) for full dict.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    IsActive: Optional[bool] = None
    ParentID: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Account":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            IsActive=data.get("IsActive"),
            ParentID=data.get("ParentID") or data.get("ParentId"),
        )


class Accounts:
    """
    Accounts client.

    Endpoint-representative methods only (minimal helpers):
      - GET  /api/accounts/{id}
      - POST /api/accounts/search
      - GET  /api/accounts
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/accounts"

    def get_raw(self, account_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/accounts/{id}
        Returns raw dict or None (if API returns empty/None).
        """
        self.session.log(f"Accounts.get_raw: id={account_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(account_id)}")
        return _first_or_none(resp.json())

    def get(self, account_id: int) -> Optional[Account]:
        """
        GET /api/accounts/{id}
        Returns typed Account or None.
        """
        raw = self.get_raw(account_id)
        return Account.from_dict(raw) if raw is not None else None

    def search(self, search_payload: Dict[str, Any]) -> List[Account]:
        """
        POST /api/accounts/search
        Returns [] when no results (valid).
        """
        self.session.log("Accounts.search")
        resp = self.session.request("POST", f"{self._base_path}/search", json=search_payload)
        rows = resp.json() or []
        return [Account.from_dict(x) for x in rows if isinstance(x, dict)]

    def list_all(self, *, is_active: Optional[bool] = None) -> List[Account]:
        """
        GET /api/accounts
        Optional query param: isActive=true|false (if supported by tenant; harmless otherwise)

        Returns [] when no results (valid).
        """
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()

        self.session.log(f"Accounts.list_all: params={params}")
        resp = self.session.request("GET", self._base_path, params=params if params else None)
        rows = _as_list_of_dicts(resp.json())
        return [Account.from_dict(x) for x in rows]
```

## File: src/teamdynamix/applications.py
```python
# =====================================================================
# FILE: src/teamdynamix/applications.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Application:
    """
    Minimal Application DTO. Keep intentionally small; use Applications.list_raw() for full dicts.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    SystemClass: Optional[str] = None
    IsActive: Optional[bool] = None
    IsDefault: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Application":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            SystemClass=data.get("SystemClass"),
            IsActive=data.get("IsActive"),
            IsDefault=data.get("IsDefault"),
        )


class Applications:
    """
    Applications client.

    TeamDynamix commonly exposes application metadata endpoints under /api/applications.
    This module is intentionally minimal and endpoint-representative.

    Methods:
      - GET /api/applications
      - GET /api/applications/{id}   (if supported by tenant)
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/applications"

    def list_raw(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        GET /api/applications
        Returns raw list[dict]. [] is valid.
        """
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()

        self.session.log(f"Applications.list_raw: params={params}")
        resp = self.session.request("GET", self._base_path, params=params if params else None)
        return _as_list_of_dicts(resp.json())

    def list(self, *, is_active: Optional[bool] = None) -> List[Application]:
        """
        GET /api/applications
        Returns typed Application list.
        """
        return [Application.from_dict(x) for x in self.list_raw(is_active=is_active)]

    def get_raw(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/applications/{id}
        Some tenants may not support this. If unsupported, it will raise HttpError.
        """
        self.session.log(f"Applications.get_raw: id={app_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(app_id)}")
        data = resp.json()
        return data if isinstance(data, dict) else None

    def get(self, app_id: int) -> Optional[Application]:
        """
        GET /api/applications/{id}
        Returns typed Application or None if API returns non-dict/empty.
        """
        raw = self.get_raw(app_id)
        return Application.from_dict(raw) if raw is not None else None
```

## File: src/teamdynamix/attributes.py
```python
# =====================================================================
# FILE: src/teamdynamix/attributes.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Attribute:
    """
    Minimal Attribute DTO. Attributes can vary widely by org and entity type,
    so we keep this intentionally small.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None
    IsRequired: Optional[bool] = None
    DataType: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attribute":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
            IsRequired=data.get("IsRequired"),
            DataType=data.get("DataType") or data.get("Type"),
        )


class Attributes:
    """
    Attributes client.

    TeamDynamix attributes are usually scoped to an application and an entity type.
    Endpoint shapes vary by tenant; this module stays endpoint-representative and minimal.

    Common patterns seen in TDX environments include:
      - GET /api/applications/{appId}/attributes/{component}
      - GET /api/attributes/{component}
      - GET /api/attributes

    This module supports a flexible but explicit set of methods:
      1) list_for_application_component(app_id, component)
      2) list_for_component(component)
      3) list_all()

    If your tenant only supports one of these, use the corresponding method.
    """
    def __init__(self, session: Session):
        self.session = session

    def list_for_application_component_raw(self, app_id: int, component: str) -> List[Dict[str, Any]]:
        """
        GET /api/applications/{appId}/attributes/{component}
        """
        component = component.strip().strip("/")
        path = f"/api/applications/{int(app_id)}/attributes/{component}"
        self.session.log(f"Attributes.list_for_application_component_raw: app_id={app_id}, component={component}")
        resp = self.session.request("GET", path)
        return _as_list_of_dicts(resp.json())

    def list_for_application_component(self, app_id: int, component: str) -> List[Attribute]:
        return [Attribute.from_dict(x) for x in self.list_for_application_component_raw(app_id, component)]

    def list_for_component_raw(self, component: str) -> List[Dict[str, Any]]:
        """
        GET /api/attributes/{component}
        """
        component = component.strip().strip("/")
        path = f"/api/attributes/{component}"
        self.session.log(f"Attributes.list_for_component_raw: component={component}")
        resp = self.session.request("GET", path)
        return _as_list_of_dicts(resp.json())

    def list_for_component(self, component: str) -> List[Attribute]:
        return [Attribute.from_dict(x) for x in self.list_for_component_raw(component)]

    def list_all_raw(self) -> List[Dict[str, Any]]:
        """
        GET /api/attributes
        """
        self.session.log("Attributes.list_all_raw")
        resp = self.session.request("GET", "/api/attributes")
        return _as_list_of_dicts(resp.json())

    def list_all(self) -> List[Attribute]:
        return [Attribute.from_dict(x) for x in self.list_all_raw()]
```

## File: src/teamdynamix/auth.py
```python
# =====================================================================
# FILE: src/teamdynamix/auth.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import threading

from .config import Config
from .exceptions import AuthError
from .transport import Transport


@dataclass(slots=True)
class Auth:
    """
    Auth is responsible for:
    - determining auth mode (admin vs user) from validated Config
    - making the auth call (via Transport)
    - caching the token
    """
    config: Config
    logger: Any          # Logger-like
    transport: Transport

    _token: Optional[str] = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def _auth_url(self) -> str:
        if self.config.auth_mode == "admin":
            return f"{self.config.base_url}/api/auth/loginadmin"
        return f"{self.config.base_url}/api/auth/login"

    def _payload(self) -> Dict[str, str]:
        if self.config.auth_mode == "admin":
            # Config validation guarantees these exist
            return {"BEID": self.config.beid or "", "WebServicesKey": self.config.webserviceskey or ""}
        return {"username": self.config.username or "", "password": self.config.password or ""}

    def authenticate(self) -> str:
        """
        Forces a network authentication and returns a token (does not cache unless caller sets it).
        """
        url = self._auth_url()
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = self._payload()

        self.logger.log(f"Auth.authenticate: mode={self.config.auth_mode}\n")
        resp = self.transport.request("POST", url, headers=headers, json=payload)
        token = (resp.text or "").strip()
        if not token:
            raise AuthError("Empty token received from authentication endpoint.")
        return token

    def get_token(self, *, force_refresh: bool = False) -> str:
        """
        Returns cached token. If missing or force_refresh=True, authenticates.
        """
        with self._lock:
            if self._token is None or force_refresh:
                self._token = self.authenticate()
            return self._token
```

## File: src/teamdynamix/config.py
```python
# =====================================================================
# FILE: src/teamdynamix/config.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import configparser
from typing import Optional, Literal

from .exceptions import ConfigError

AuthMode = Literal["admin", "user"]


def _as_bool(value: str | None, default: bool) -> bool:
    v = (value or "").strip().lower()
    if v == "":
        return default
    if v in ("1", "true", "yes", "y", "on"):
        return True
    if v in ("0", "false", "no", "n", "off"):
        return False
    raise ConfigError(f"Invalid boolean value: {value!r}")


def _as_int(value: str | None, default: int) -> int:
    v = (value or "").strip()
    if v == "":
        return default
    try:
        return int(v)
    except ValueError as e:
        raise ConfigError(f"Invalid integer value: {value!r}") from e


@dataclass(frozen=True, slots=True)
class Config:
    # ---- Core TDX
    tenant: str
    environment: str
    base_url_override: Optional[str] = None

    # ---- Auth
    auth_mode: AuthMode = "admin"
    beid: Optional[str] = None
    webserviceskey: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    # ---- Logging (optional)
    log_dir: str = "./logs"
    log_level: str = "INFO"      # ← CHANGED DEFAULT
    log_console: bool = True

    # ---- HTTP (optional)
    default_timeout_seconds: int = 10   # 0 disables

    def __post_init__(self) -> None:
        # Validate core
        if not self.tenant or not self.tenant.strip():
            raise ConfigError("Missing required setting: [tdx].tenant")
        if not self.environment or not self.environment.strip():
            raise ConfigError("Missing required setting: [tdx].environment")

        mode = (self.auth_mode or "").strip().lower()
        if mode not in ("admin", "user"):
            raise ConfigError("Invalid [auth].mode. Expected 'admin' or 'user'.")

        # Validate creds based on mode
        if mode == "admin":
            if not (self.beid and self.beid.strip()) or not (self.webserviceskey and self.webserviceskey.strip()):
                raise ConfigError("Auth mode 'admin' requires [auth].beid and [auth].webserviceskey.")
        else:
            if not (self.username and self.username.strip()) or not (self.password and self.password.strip()):
                raise ConfigError("Auth mode 'user' requires [auth].username and [auth].password.")

        # Validate timeout semantics
        if self.default_timeout_seconds < 0:
            raise ConfigError("[http].default_timeout_seconds must be >= 0 (0 disables).")

        # Validate log_dir is at least non-empty
        if not self.log_dir or not self.log_dir.strip():
            raise ConfigError("[logging].log_dir must be a non-empty path.")

    @property
    def base_url(self) -> str:
        if self.base_url_override and self.base_url_override.strip():
            return self.base_url_override.strip().rstrip("/")
        return f"https://{self.tenant.strip().rstrip('/')}/{self.environment.strip()}WebApi"

    @property
    def timeout(self) -> Optional[int]:
        return None if self.default_timeout_seconds == 0 else self.default_timeout_seconds

    @classmethod
    def from_file(cls, config_path: str | Path = "./config/config.ini") -> "Config":
        """
        Required:
          [tdx]
          [auth]

        Optional:
          [logging]
          [http]
        """
        path = Path(config_path)
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")

        parser = configparser.ConfigParser()
        parser.read(path)

        # ---- Required sections
        missing_required = [sec for sec in ("tdx", "auth") if sec not in parser]
        if missing_required:
            raise ConfigError(f"Missing required INI sections: {', '.join(missing_required)}")

        tdx = parser["tdx"]
        auth = parser["auth"]

        logging_sec = parser["logging"] if "logging" in parser else None
        http = parser["http"] if "http" in parser else None

        # ---- [tdx]
        tenant = (tdx.get("tenant", "") or "").strip()
        environment = (tdx.get("environment", "") or "").strip()
        base_url_override = (tdx.get("base_url", "") or "").strip() or None

        # ---- [auth]
        auth_mode: AuthMode = (auth.get("mode", "admin") or "admin").strip().lower()  # type: ignore[assignment]
        beid = (auth.get("beid", "") or "").strip() or None
        webserviceskey = (auth.get("webserviceskey", "") or "").strip() or None
        username = (auth.get("username", "") or "").strip() or None
        password = (auth.get("password", "") or "").strip() or None

        # ---- [logging] (optional)
        log_dir = "./logs"
        log_level = "INFO"   # ← CHANGED DEFAULT
        log_console = True
        if logging_sec is not None:
            log_dir = (logging_sec.get("log_dir", "./logs") or "./logs").strip()
            log_level = (logging_sec.get("level", "INFO") or "INFO").strip().upper()
            log_console = _as_bool(logging_sec.get("console", "true"), default=True)

        # ---- [http] (optional)
        default_timeout_seconds = 10
        if http is not None:
            default_timeout_seconds = _as_int(http.get("default_timeout_seconds", "10"), default=10)

        return cls(
            tenant=tenant,
            environment=environment,
            base_url_override=base_url_override,
            auth_mode=auth_mode,  # type: ignore[arg-type]
            beid=beid,
            webserviceskey=webserviceskey,
            username=username,
            password=password,
            log_dir=log_dir,
            log_level=log_level,
            log_console=log_console,
            default_timeout_seconds=default_timeout_seconds,
        )
```

## File: src/teamdynamix/event.py
```python
# =====================================================================
# FILE: src/teamdynamix/event.py
# (kept close to refactor style; compatible with Logger above)
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any


@dataclass(slots=True)
class Event:
    message: str
    level: int = 20
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        ts = self.created_at.isoformat()
        ctx = f" | context={self.context}" if self.context else ""
        return f"{ts} [{self.level}] {self.message}{ctx}\n"
```

## File: src/teamdynamix/exceptions.py
```python
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
```

## File: src/teamdynamix/functional_roles.py
```python
# =====================================================================
# FILE: src/teamdynamix/functional_roles.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


@dataclass(slots=True)
class FunctionalRole:
    """
    Minimal Functional Role DTO based on the Postman export.

    Fields observed in the Postman body examples:
      ID, Name, CreatedDate, ModifiedDate, IsActive,
      NotifyOnAssignment, RequiresApproval, ManagerFullName, ManagerUID, ResourceCount
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    CreatedDate: Optional[str] = None
    ModifiedDate: Optional[str] = None
    IsActive: Optional[bool] = None
    NotifyOnAssignment: Optional[bool] = None
    RequiresApproval: Optional[bool] = None
    ManagerFullName: Optional[str] = None
    ManagerUID: Optional[str] = None  # Guid string
    ResourceCount: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionalRole":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            CreatedDate=data.get("CreatedDate"),
            ModifiedDate=data.get("ModifiedDate"),
            IsActive=data.get("IsActive"),
            NotifyOnAssignment=data.get("NotifyOnAssignment"),
            RequiresApproval=data.get("RequiresApproval"),
            ManagerFullName=data.get("ManagerFullName"),
            ManagerUID=data.get("ManagerUID"),
            ResourceCount=data.get("ResourceCount"),
        )


class FunctionalRoles:
    """
    Functional Roles API client (restricted to endpoints confirmed in your docs/Postman):

      POST /api/functionalroles              -> create()
      PUT  /api/functionalroles/{id}         -> edit()
      POST /api/functionalroles/search       -> search()

    Notes:
    - We intentionally keep this close to the vendor surface. No extra helper endpoints.
    - 200 OK with [] is treated as a valid “no results” outcome.
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/functionalroles"

    def create(self, payload: Dict[str, Any]) -> FunctionalRole:
        """
        POST /api/functionalroles

        Payload example fields (per Postman):
          Name, IsActive, NotifyOnAssignment, RequiresApproval, ManagerFullName, ManagerUID
        """
        self.session.log("FunctionalRoles.create")
        resp = self.session.request("POST", self._base_path, json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from FunctionalRoles.create (expected dict).")
        return FunctionalRole.from_dict(data)

    def edit(self, role_id: int, payload: Dict[str, Any]) -> FunctionalRole:
        """
        PUT /api/functionalroles/{id}

        Postman indicates the body includes the full role object (including ID).
        We do not force the ID into the payload here, but you can include it if required
        by your tenant’s validation rules.
        """
        self.session.log(f"FunctionalRoles.edit: id={role_id}")
        resp = self.session.request("PUT", f"{self._base_path}/{int(role_id)}", json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from FunctionalRoles.edit (expected dict).")
        return FunctionalRole.from_dict(data)

    def search(self, search_payload: Dict[str, Any]) -> List[FunctionalRole]:
        """
        POST /api/functionalroles/search

        Postman search body example fields:
          Name, ManagerUID, MaxResults, IsActive, ReturnItemCounts
        """
        self.session.log("FunctionalRoles.search")
        resp = self.session.request("POST", f"{self._base_path}/search", json=search_payload)
        data: Any = resp.json()

        if not data:
            return []
        if isinstance(data, list):
            return [FunctionalRole.from_dict(x) for x in data if isinstance(x, dict)]
        if isinstance(data, dict):
            return [FunctionalRole.from_dict(data)]
        return []
```

## File: src/teamdynamix/groups.py
```python
# =====================================================================
# FILE: src/teamdynamix/groups.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _first_or_none(data: Any) -> Optional[Dict[str, Any]]:
    """
    Normalize:
      - dict -> dict
      - list[dict] -> first dict
      - []/None -> None
    """
    if data is None:
        return None
    if isinstance(data, list):
        if not data:
            return None
        first = data[0]
        return first if isinstance(first, dict) else None
    return data if isinstance(data, dict) else None


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Group:
    """
    Minimal Group DTO. Keep small; use Groups.get_raw(...) if you need full dict fields.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Group":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
        )


class Groups:
    """
    Groups client (endpoint-representative, minimal helpers).

    Common TeamDynamix WebAPI endpoints:
      - GET  /api/groups/{id}
      - POST /api/groups/search
      - GET  /api/groups
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/groups"

    def get_raw(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/groups/{id}
        Returns raw dict or None when API returns empty/None.
        """
        self.session.log(f"Groups.get_raw: id={group_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(group_id)}")
        return _first_or_none(resp.json())

    def get(self, group_id: int) -> Optional[Group]:
        """
        GET /api/groups/{id}
        Returns typed Group or None.
        """
        raw = self.get_raw(group_id)
        return Group.from_dict(raw) if raw is not None else None

    def search_raw(self, search_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        POST /api/groups/search
        Returns [] when no matches (valid).
        """
        self.session.log("Groups.search_raw")
        resp = self.session.request("POST", f"{self._base_path}/search", json=search_payload)
        return _as_list_of_dicts(resp.json())

    def search(self, search_payload: Dict[str, Any]) -> List[Group]:
        """
        POST /api/groups/search
        Returns typed list (possibly empty []).
        """
        return [Group.from_dict(x) for x in self.search_raw(search_payload)]

    def list_all_raw(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        GET /api/groups
        Optional query param: isActive=true|false (if supported by tenant; harmless otherwise)
        """
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()

        self.session.log(f"Groups.list_all_raw: params={params}")
        resp = self.session.request("GET", self._base_path, params=params if params else None)
        return _as_list_of_dicts(resp.json())

    def list_all(self, *, is_active: Optional[bool] = None) -> List[Group]:
        """
        GET /api/groups
        Returns typed list (possibly empty []).
        """
        return [Group.from_dict(x) for x in self.list_all_raw(is_active=is_active)]
```

## File: src/teamdynamix/logger.py
```python
# =====================================================================
# FILE: src/teamdynamix/logger.py
# =====================================================================
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import threading
import time

from .event import Event


_LEVELS = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "WARN": 30,
    "INFO": 20,
    "DEBUG": 10,
}


class Logger:
    """
    Minimal logger:
    - Keeps an in-memory list of Event objects
    - Writes to a timestamped file under log_dir
    - Prints to console (optional)
    - Default level behavior: ERROR (catches errors/exceptions, ignores warnings)
    """
    def __init__(
        self,
        log_dir: str | Path = "./logs",
        level: str = "ERROR",
        console: bool = True,
        name_prefix: str = "log",
    ):
        self._lock = threading.RLock()
        self.events: List[Event] = []

        self.level_name = (level or "ERROR").strip().upper()
        self.level = _LEVELS.get(self.level_name, 40)

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        ts = time.strftime("%Y%m%d%H%M%S")
        self.log_file = self.log_dir / f"{name_prefix}-{ts}.txt"
        self.console = bool(console)

    def log(self, message: str, level: int | None = None, context: Optional[dict] = None) -> None:
        lvl = self.level if level is None else int(level)

        # Filter: only record if lvl >= configured level
        if lvl < self.level:
            return

        event = Event(message=message, level=lvl, context=context)
        with self._lock:
            self.events.append(event)

        # Console behavior requirement: print(event, end='')
        if self.console:
            print(event, end="")

        # File append
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(str(event))

    def clear_events(self) -> None:
        with self._lock:
            self.events.clear()
```

## File: src/teamdynamix/people.py
```python
# =====================================================================
# FILE: src/teamdynamix/people.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from .session import Session


@dataclass(slots=True)
class Person:
    """
    Minimal, commonly-used subset of a TeamDynamix Person record.

    We intentionally do NOT model the full People.get() payload (it is large and nested).
    Use People.get_raw(...) when you need the full dict.
    """
    UID: Optional[str] = None
    ReferenceID: Optional[int] = None
    BEID: Optional[str] = None

    IsActive: Optional[bool] = None
    IsEmployee: Optional[bool] = None

    UserName: Optional[str] = None
    FullName: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    PrimaryEmail: Optional[str] = None

    SecurityRoleName: Optional[str] = None
    DefaultAccountID: Optional[int] = None
    DefaultAccountName: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        # UID appears as UID/Id/id depending on endpoint shape
        uid = data.get("UID") or data.get("Id") or data.get("id")

        return cls(
            UID=uid,
            ReferenceID=data.get("ReferenceID"),
            BEID=data.get("BEID"),
            IsActive=data.get("IsActive"),
            IsEmployee=data.get("IsEmployee"),
            UserName=data.get("UserName"),
            FullName=data.get("FullName"),
            FirstName=data.get("FirstName"),
            LastName=data.get("LastName"),
            PrimaryEmail=data.get("PrimaryEmail"),
            SecurityRoleName=data.get("SecurityRoleName"),
            DefaultAccountID=data.get("DefaultAccountID"),
            DefaultAccountName=data.get("DefaultAccountName"),
        )


class People:
    """
    People API client.

    Design rules (per the new architecture):
    - No direct requests.* usage here. All calls go through Session.request().
    - No manual header/token handling here. Session injects auth headers.
    - 200 OK with [] is valid and should return []/None as appropriate.
    - Prefer endpoint-representative methods; avoid non-endpoint "helper" methods unless required.
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/people"

    # --- Core endpoints --------------------------------------------------

    def get_raw(self, uid: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        GET /api/people/{uid}

        Returns the raw dict payload (or None when API returns empty/None).
        This is the escape hatch for large/nested fields.
        """
        self.session.log(f"People.get_raw: uid={uid}")
        resp = self.session.request("GET", f"{self._base_path}/{uid}")
        data: Any = resp.json()

        if not data:
            return None
        if isinstance(data, list):
            item = data[0] if data else None
            return item if isinstance(item, dict) else None
        return data if isinstance(data, dict) else None

    def get(self, uid: Union[str, UUID]) -> Optional[Person]:
        """
        GET /api/people/{uid}

        Returns:
        - Person if found
        - None if API returns empty/None (valid behavior in some TDX responses)
        """
        raw = self.get_raw(uid)
        return Person.from_dict(raw) if raw is not None else None

    def search(
        self,
        search_text: str,
        *,
        max_results: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_employee: Optional[bool] = None,
        is_client: Optional[bool] = None,
        has_login: Optional[bool] = None,
    ) -> List[Person]:
        """
        POST /api/people/search

        Returns [] when no results (valid).
        """
        payload: Dict[str, Any] = {"SearchText": search_text}

        # Include optional filters only if explicitly provided
        if max_results is not None:
            payload["MaxResults"] = max_results
        if is_active is not None:
            payload["IsActive"] = is_active
        if is_employee is not None:
            payload["IsEmployee"] = is_employee
        if is_client is not None:
            payload["IsClient"] = is_client
        if has_login is not None:
            payload["HasLogin"] = has_login

        self.session.log(f"People.search: {payload}")
        resp = self.session.request("POST", f"{self._base_path}/search", json=payload)
        data: Any = resp.json()

        if not data:
            return []
        if isinstance(data, list):
            return [Person.from_dict(item) for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [Person.from_dict(data)]
        return []

    def user_list(self, is_active: bool = True) -> List[Person]:
        """
        GET /api/people/userlist?isActive=true|false

        Returns [] when no results (valid).
        """
        params = {"isActive": str(is_active).lower()}
        self.session.log(f"People.user_list: params={params}")
        resp = self.session.request("GET", f"{self._base_path}/userlist", params=params)
        data: Any = resp.json()

        if not data:
            return []
        if isinstance(data, list):
            return [Person.from_dict(item) for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [Person.from_dict(data)]
        return []

    def create(self, person_payload: Dict[str, Any]) -> Person:
        """
        POST /api/people

        Note: We intentionally accept dict payloads to avoid prematurely modeling
        the full TDX person schema.
        """
        self.session.log("People.create")
        resp = self.session.request("POST", self._base_path, json=person_payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from People.create (expected dict).")
        return Person.from_dict(data)

    def update(self, uid: Union[str, UUID], updates: Dict[str, Any]) -> bool:
        """
        PATCH /api/people/{uid}

        Returns True on success.
        """
        self.session.log(f"People.update: uid={uid}, updates={updates}")
        self.session.request("PATCH", f"{self._base_path}/{uid}", json=updates)
        return True

    # --- Functional roles -------------------------------------------------

    def list_functional_roles(self, uid: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        GET /api/people/{uid}/functionalroles

        Returns [] when none (valid).
        """
        self.session.log(f"People.list_functional_roles: uid={uid}")
        resp = self.session.request("GET", f"{self._base_path}/{uid}/functionalroles")
        data: Any = resp.json()

        if not data:
            return []
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [data]
        return []

    def add_functional_role(self, uid: Union[str, UUID], role_id: int, is_primary: bool = False) -> bool:
        """
        PUT /api/people/{uid}/functionalroles/{role_id}?isPrimary=true|false

        Returns True on success.
        """
        params = {"isPrimary": str(is_primary).lower()}
        self.session.log(f"People.add_functional_role: uid={uid}, role_id={role_id}, params={params}")
        self.session.request("PUT", f"{self._base_path}/{uid}/functionalroles/{role_id}", params=params)
        return True

    def remove_functional_role(self, uid: Union[str, UUID], role_id: int) -> bool:
        """
        DELETE /api/people/{uid}/functionalroles/{role_id}

        Returns True on success.
        """
        self.session.log(f"People.remove_functional_role: uid={uid}, role_id={role_id}")
        self.session.request("DELETE", f"{self._base_path}/{uid}/functionalroles/{role_id}")
        return True
```

## File: src/teamdynamix/service_catalog.py
```python
# =====================================================================
# FILE: src/teamdynamix/service_catalog.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Service:
    """
    Minimal Service Catalog DTO.

    The service catalog payload/response shape varies by tenant configuration, so we keep
    this intentionally small and rely on raw dicts for everything else.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Service":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
        )


class ServiceCatalog:
    """
    Service Catalog client, matching the Postman collection endpoints:

      GET    /api/{portalAppId}/services
      POST   /api/{portalAppId}/services
      GET    /api/{portalAppId}/services/{id}
      PUT    /api/{portalAppId}/services/{id}
      DELETE /api/{portalAppId}/services/{id}

    Notes:
    - We keep helper methods minimal and endpoint-representative.
    - 200 OK with [] is a valid “no results” outcome.
    """

    def __init__(self, session: Session, portal_app_id: int):
        self.session = session
        self.portal_app_id = int(portal_app_id)
        self._base_path = f"/api/{self.portal_app_id}/services"

    # ---- List
    def list_raw(self) -> List[Dict[str, Any]]:
        self.session.log(f"ServiceCatalog.list_raw: portal_app_id={self.portal_app_id}")
        resp = self.session.request("GET", self._base_path)
        return _as_list_of_dicts(resp.json())

    def list(self) -> List[Service]:
        return [Service.from_dict(x) for x in self.list_raw()]

    # ---- Get
    def get_raw(self, service_id: int) -> Dict[str, Any]:
        self.session.log(
            f"ServiceCatalog.get_raw: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        resp = self.session.request("GET", f"{self._base_path}/{int(service_id)}")
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.get (expected dict).")
        return data

    def get(self, service_id: int) -> Service:
        return Service.from_dict(self.get_raw(service_id))

    # ---- Create
    def create_raw(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.session.log(f"ServiceCatalog.create_raw: portal_app_id={self.portal_app_id}")
        resp = self.session.request("POST", self._base_path, json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.create (expected dict).")
        return data

    def create(self, payload: Dict[str, Any]) -> Service:
        return Service.from_dict(self.create_raw(payload))

    # ---- Update
    def update_raw(self, service_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.session.log(
            f"ServiceCatalog.update_raw: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        resp = self.session.request("PUT", f"{self._base_path}/{int(service_id)}", json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.update (expected dict).")
        return data

    def update(self, service_id: int, payload: Dict[str, Any]) -> Service:
        return Service.from_dict(self.update_raw(service_id, payload))

    # ---- Delete
    def delete(self, service_id: int) -> bool:
        self.session.log(
            f"ServiceCatalog.delete: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        self.session.request("DELETE", f"{self._base_path}/{int(service_id)}")
        return True
```

## File: src/teamdynamix/tickets.py
```python
# =====================================================================
# FILE: src/teamdynamix/tickets.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .session import Session
from .transport import PatchPayload  # exported publicly via __init__.py per your plan


def _first_or_none(data: Any) -> Optional[Dict[str, Any]]:
    """
    TDX endpoints sometimes return either:
      - an object (dict)
      - a list of objects (list[dict])
      - an empty list []
    Normalize to "first dict or None".
    """
    if data is None:
        return None
    if isinstance(data, list):
        if not data:
            return None
        first = data[0]
        return first if isinstance(first, dict) else None
    return data if isinstance(data, dict) else None


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _patch_ops_json(
    ops: Union[Dict[str, Any], List[PatchPayload], List[Dict[str, Any]]]
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    We allow three shapes:
      1) dict[str, Any]  -> Transport will convert to JSON Patch (replace ops) for PATCH
      2) list[PatchPayload] -> we convert to list[dict]
      3) list[dict] -> passed through

    This keeps Tickets.update() endpoint-aligned (PATCH = JSON Patch),
    but still lets callers use the simple {"Field": "Value"} form.
    """
    if isinstance(ops, dict):
        return ops

    out: List[Dict[str, Any]] = []
    for item in ops:
        if isinstance(item, PatchPayload):
            out.append({"op": item.op, "path": item.path, "value": item.value})
        elif isinstance(item, dict):
            out.append(item)
    return out


# ---------------------------------------------------------------------
# DTOs (minimal: just enough to be useful without over-modeling)
# ---------------------------------------------------------------------
@dataclass(slots=True)
class Ticket:
    ID: Optional[int] = None
    Title: Optional[str] = None
    Description: Optional[str] = None
    StatusID: Optional[int] = None
    StatusName: Optional[str] = None
    TypeID: Optional[int] = None
    TypeName: Optional[str] = None
    PriorityID: Optional[int] = None
    PriorityName: Optional[str] = None
    RequestorUid: Optional[str] = None
    ResponsibleUid: Optional[str] = None
    ResponsibleGroupID: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Title=data.get("Title"),
            Description=data.get("Description"),
            StatusID=data.get("StatusID"),
            StatusName=data.get("StatusName"),
            TypeID=data.get("TypeID"),
            TypeName=data.get("TypeName"),
            PriorityID=data.get("PriorityID"),
            PriorityName=data.get("PriorityName"),
            RequestorUid=data.get("RequestorUid") or data.get("RequestorUID"),
            ResponsibleUid=data.get("ResponsibleUid") or data.get("ResponsibleUID"),
            ResponsibleGroupID=data.get("ResponsibleGroupID") or data.get("ResponsibleGroupId"),
        )


# ---------------------------------------------------------------------
# Meta endpoints (priorities/types/statuses/sources)
# ---------------------------------------------------------------------
class TicketPriorities:
    """
    Ticket priorities are per ticketing app.

    GET /api/{ticketingAppId}/tickets/priorities
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self) -> List[Dict[str, Any]]:
        self.session.log("TicketPriorities.list")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/priorities")
        return resp.json() or []


class TicketTypes:
    """
    Ticket types are per ticketing app.

    GET /api/{ticketingAppId}/tickets/types?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketTypes.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/types", params=params)
        return resp.json() or []


class TicketStatuses:
    """
    Ticket statuses are per ticketing app.

    GET /api/{ticketingAppId}/tickets/statuses?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketStatuses.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/statuses", params=params)
        return resp.json() or []


class TicketSources:
    """
    Ticket sources are per ticketing app.

    GET /api/{ticketingAppId}/tickets/sources?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketSources.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/sources", params=params)
        return resp.json() or []


# ---------------------------------------------------------------------
# Tickets client
# ---------------------------------------------------------------------
class Tickets:
    """
    Tickets client is per ticketing app.

    Common endpoints (per Postman):
      - GET    /api/{ticketingAppId}/tickets/{id}
      - POST   /api/{ticketingAppId}/tickets/search
      - POST   /api/{ticketingAppId}/tickets
      - PATCH  /api/{ticketingAppId}/tickets/{id}?notifyNewResponsible=
      - GET    /api/{ticketingAppId}/tickets/{id}/feed
      - POST   /api/{ticketingAppId}/tickets/{id}/feed
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)
        self._base = f"/api/{self.ticketing_app_id}/tickets"

    # --- Core CRUD-ish
    def get(self, ticket_id: int) -> Optional[Ticket]:
        self.session.log(f"Tickets.get: id={ticket_id}")
        resp = self.session.request("GET", f"{self._base}/{int(ticket_id)}")
        item = _first_or_none(resp.json())
        return Ticket.from_dict(item) if item is not None else None

    def create(self, ticket_payload: Dict[str, Any]) -> Ticket:
        """
        POST /api/{ticketingAppId}/tickets
        Returns created ticket object.
        """
        self.session.log("Tickets.create")
        resp = self.session.request("POST", self._base, json=ticket_payload)
        data = resp.json()
        if not isinstance(data, dict):
            # keep minimal: if API ever returns non-object here, just coerce to empty dict
            data = {}
        return Ticket.from_dict(data)

    def search(self, search_payload: Dict[str, Any]) -> List[Ticket]:
        """
        POST /api/{ticketingAppId}/tickets/search
        Returns list of tickets (possibly empty list []).
        """
        self.session.log("Tickets.search")
        resp = self.session.request("POST", f"{self._base}/search", json=search_payload)
        rows = resp.json() or []
        return [Ticket.from_dict(x) for x in rows if isinstance(x, dict)]

    def update(
        self,
        ticket_id: int,
        ops: Union[Dict[str, Any], List[PatchPayload], List[Dict[str, Any]]],
        *,
        notify_new_responsible: Optional[bool] = None,
    ) -> bool:
        """
        PATCH /api/{ticketingAppId}/tickets/{id}?notifyNewResponsible=
        Body is JSON Patch list. We also accept a simple dict of field->value,
        which Transport will convert into JSON Patch "replace" operations.

        Returns True on success.
        """
        params: Dict[str, Any] = {}
        if notify_new_responsible is not None:
            params["notifyNewResponsible"] = str(notify_new_responsible).lower()

        payload = _patch_ops_json(ops)
        self.session.log(f"Tickets.update: id={ticket_id}, params={params}")
        self.session.request("PATCH", f"{self._base}/{int(ticket_id)}", params=params, json=payload)
        return True

    # --- Feed
    def get_feed(self, ticket_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/{ticketingAppId}/tickets/{id}/feed
        """
        self.session.log(f"Tickets.get_feed: id={ticket_id}")
        resp = self.session.request("GET", f"{self._base}/{int(ticket_id)}/feed")
        return _as_list_of_dicts(resp.json())

    def add_feed_entry(self, ticket_id: int, feed_payload: Dict[str, Any]) -> bool:
        """
        POST /api/{ticketingAppId}/tickets/{id}/feed
        Returns True on success.
        """
        self.session.log(f"Tickets.add_feed_entry: id={ticket_id}")
        self.session.request("POST", f"{self._base}/{int(ticket_id)}/feed", json=feed_payload)
        return True
```

## File: src/teamdynamix/transport.py
```python
# =====================================================================
# FILE: src/teamdynamix/transport.py
#
# Change summary (per your decision):
# - JSON Patch support lives in Transport because it is cross-cutting across client modules.
# - If method == PATCH and json is a dict, Transport converts it to RFC6902-style JSON Patch.
# - If method == PATCH and json is already a list, Transport passes it through unchanged.
# - Transport also ensures Content-Type is set for PATCH if caller didn't provide it.
#
# Notes:
# - This assumes TeamDynamix PATCH endpoints consistently use JSON Patch (common in TDX).
# - Client modules can now call session.request("PATCH", ..., json={"FirstName": "X"}) and it "just works".
# =====================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, Dict, List
import requests

from .exceptions import HttpError, TdxTimeoutError, TdxRequestError


@dataclass(frozen=True, slots=True)
class PatchPayload:
    """
    Represents a single JSON Patch operation (RFC 6902 style), as required by TeamDynamix PATCH endpoints.

    Example:
      {"op": "replace", "path": "/FirstName", "value": "NewFirstName"}
    """
    op: str
    path: str
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        return {"op": self.op, "path": self.path, "value": self.value}


def _build_replace_patch(updates: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Converts a dict of field updates into a JSON Patch list.

    Input:
      {"FirstName": "NewFirstName", "LastName": "NewLastName"}

    Output:
      [
        {"op": "replace", "path": "/FirstName", "value": "NewFirstName"},
        {"op": "replace", "path": "/LastName", "value": "NewLastName"}
      ]
    """
    ops: List[Dict[str, Any]] = []
    for key, value in updates.items():
        ops.append(PatchPayload(op="replace", path=f"/{key}", value=value).to_dict())
    return ops


@dataclass(slots=True)
class Transport:
    """
    Single transport boundary:
    - The only place that touches requests.*
    - Applies the default timeout (optional)
    - Translates timeouts / request exceptions into library exceptions
    - Normalizes TeamDynamix PATCH payloads (JSON Patch) centrally
    """
    logger: Any  # Logger-like: must have .log(str, ...)
    default_timeout: Optional[int] = None

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Any = None,
        data: Any = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        m = method.upper()
        effective_timeout = self.default_timeout if timeout is None else timeout

        # ---- PATCH normalization (TeamDynamix JSON Patch) ----
        # If caller passes a dict for PATCH, convert it to a JSON Patch list.
        # If caller passes a list, assume it's already a JSON Patch list and pass through.
        req_headers: Dict[str, str] = {}
        if headers:
            req_headers.update(headers)

        if m == "PATCH":
            if isinstance(json, dict):
                json = _build_replace_patch(json)
            # Ensure PATCH content-type if not specified
            if not any(k.lower() == "content-type" for k in req_headers.keys()):
                req_headers["Content-Type"] = "application/json; charset=utf-8"

        try:
            resp = requests.request(
                method=m,
                url=url,
                headers=req_headers if req_headers else None,
                params=params,
                json=json,
                data=data,
                timeout=effective_timeout,  # None means "no timeout"
            )
        except requests.exceptions.Timeout as e:
            self.logger.log(f"Timeout calling {m} {url} (timeout={effective_timeout})\n", level=40)
            raise TdxTimeoutError(f"Timeout calling {m} {url}") from e
        except requests.exceptions.RequestException as e:
            self.logger.log(f"Request error calling {m} {url}: {e}\n", level=40)
            raise TdxRequestError(f"Request error calling {m} {url}: {e}") from e

        if resp.status_code >= 400:
            text = ""
            try:
                text = (resp.text or "").strip()
            except Exception:
                text = ""
            raise HttpError(
                status_code=resp.status_code,
                method=m,
                url=url,
                message=f"HTTP {resp.status_code} for {m} {url}",
                response_text=text,
            )
        return resp
```

## File: src/py.typed
```
# (Leave this file empty)
```

## File: tests/test_people_endpoints.py
```python
# =====================================================================
# FILE: test_people_endpoints.py
#
# Minimal endpoint test script for People API client.
# - Assumes your config is valid at ./config/sandbox.config.ini (adjust as needed).
# - Uses the library as currently implemented: Session + People + Person.
# =====================================================================

from __future__ import annotations

from teamdynamix.session import Session
from teamdynamix.people import People


def main() -> None:
    # 0) Initialize session + client
    session = Session("./config/sandbox.config.ini")
    people = People(session)

    # Optional: prime authentication explicitly (useful for deterministic testing)
    session.authenticate()

    # 1) Search a person based on the string "000000"
    search_text = "000000"
    results = people.search(search_text, max_results=10)

    if not results:
        print(f"No people matched search text: {search_text}")
        return

    # Choose the first match for this test
    person = results[0]
    if not person.UID:
        print("Search result missing UID; cannot proceed.")
        return

    uid = person.UID
    print(f"[1] Search OK: UID={uid}, FullName={person.FullName}, Email={person.PrimaryEmail}")

    # 2) Get the full user object (raw dict) via People.get_raw + typed view via People.get
    typed_person = people.get(uid)
    raw_person = people.get_raw(uid)

    if typed_person is None or raw_person is None:
        print(f"[2] People.get/get_raw returned no data for UID={uid}")
        return

    print(f"[2] Get OK: FirstName={typed_person.FirstName!r}, LastName={typed_person.LastName!r}, UserName={typed_person.UserName!r}")

    # Capture original FirstName from raw payload (authoritative for patching)
    original_first_name = raw_person.get("FirstName") or ""
    if not isinstance(original_first_name, str):
        original_first_name = str(original_first_name)

    # 3) Update the User's FirstName by appending "TestPatch"
    suffix = "TestPatch"
    if original_first_name.endswith(suffix):
        patched_first_name = original_first_name
    else:
        patched_first_name = f"{original_first_name}{suffix}"

    print(f"[3] Patching FirstName -> {patched_first_name!r}")
    people.update(uid, {"FirstName": patched_first_name})

    # Confirm (re-fetch)
    verify_after_patch = people.get_raw(uid) or {}
    print(f"[3] Verify FirstName: {verify_after_patch.get('FirstName')!r}")

    # 4) Update the User's FirstName by removing "TestPatch" from the end
    current_first_name = verify_after_patch.get("FirstName") or ""
    if not isinstance(current_first_name, str):
        current_first_name = str(current_first_name)

    if current_first_name.endswith(suffix):
        reverted_first_name = current_first_name[: -len(suffix)]
    else:
        # If suffix is not present, revert to original to be safe
        reverted_first_name = original_first_name

    print(f"[4] Reverting FirstName -> {reverted_first_name!r}")
    people.update(uid, {"FirstName": reverted_first_name})

    # Confirm (re-fetch)
    verify_after_revert = people.get_raw(uid) or {}
    print(f"[4] Verify FirstName: {verify_after_revert.get('FirstName')!r}")

    # 5) List the user's functional roles
    roles_before = people.list_functional_roles(uid)
    print(f"[5] Functional roles before: {roles_before}")

    # 6) Add the user to Functional Role with ID 6
    role_id = 6
    print(f"[6] Adding functional role {role_id} (is_primary=False)")
    people.add_functional_role(uid, role_id, is_primary=False)

    roles_after_add = people.list_functional_roles(uid)
    print(f"[6] Functional roles after add: {roles_after_add}")

    # 7) Remove Functional Role with ID 6 from the User
    print(f"[7] Removing functional role {role_id}")
    people.remove_functional_role(uid, role_id)

    roles_after_remove = people.list_functional_roles(uid)
    print(f"[7] Functional roles after remove: {roles_after_remove}")

    print("Done.")


if __name__ == "__main__":
    main()
```

## File: tests/test_ticket_endpoints.py
```python
# =====================================================================
# FILE: tests/test_ticket_endpoints.py
#
# Minimal endpoint test script for Tickets API client.
# - Assumes your config is valid at ./config/sandbox.config.ini (adjust as needed).
# - Assumes you have implemented: Tickets, TicketPriorities, TicketStatuses, TicketSources, TicketTypes.
# - Assumes PATCH JSON Patch handling is centralized in Transport (dict -> JSON Patch list).
#
# Workflow:
# 0) Generate unique string for Description (used later for search)
# 1) List priorities
# 2) List statuses
# 3) List sources
# 4) List types
# 5) Create ticket with:
#    - TypeID: 1 if available else fallback
#    - StatusID: "New"
#    - SourceID: "API"
#    - PriorityID: middle priority (by sorted ID)
# 6) Search tickets by the random string
# 7) Get full ticket by ID
# 8) Add feed entry
# 9) Update ticket StatusID to "Cancelled"
# =====================================================================

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from teamdynamix.session import Session
from teamdynamix.tickets import (
    Tickets,
    TicketPriorities,
    TicketStatuses,
    TicketSources,
    TicketTypes,
)


def _pick_by_name(
    rows: List[Dict[str, Any]],
    desired: str,
    *,
    name_keys: Tuple[str, ...] = ("Name", "name", "StatusName", "SourceName", "TypeName"),
    id_keys: Tuple[str, ...] = ("ID", "Id", "id"),
) -> Optional[int]:
    """
    Find a row whose name matches desired (case-insensitive) and return its ID.
    """
    desired_norm = desired.strip().lower()
    for row in rows:
        if not isinstance(row, dict):
            continue
        name_val = None
        for k in name_keys:
            if k in row and row.get(k) is not None:
                name_val = str(row.get(k))
                break
        if name_val is None:
            continue
        if name_val.strip().lower() == desired_norm:
            for ik in id_keys:
                if ik in row and row.get(ik) is not None:
                    try:
                        return int(row.get(ik))
                    except Exception:
                        pass
    return None


def _pick_id_1_if_available(rows: List[Dict[str, Any]]) -> Optional[int]:
    """
    If any row has ID == 1, return 1, else return first available ID.
    """
    ids: List[int] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k in ("ID", "Id", "id"):
            if k in row and row.get(k) is not None:
                try:
                    ids.append(int(row.get(k)))
                except Exception:
                    pass
                break
    if not ids:
        return None
    if 1 in ids:
        return 1
    return ids[0]


def _pick_middle_id(rows: List[Dict[str, Any]]) -> Optional[int]:
    """
    Pick the "middle" ID (by sorted numeric ID).
    """
    ids: List[int] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k in ("ID", "Id", "id"):
            if k in row and row.get(k) is not None:
                try:
                    ids.append(int(row.get(k)))
                except Exception:
                    pass
                break
    ids = sorted(set(ids))
    if not ids:
        return None
    return ids[len(ids) // 2]


def main() -> None:
    # -----------------------------------------------------------------
    # USER PARAMETERS (edit these)
    # -----------------------------------------------------------------
    CONFIG_PATH = "./config/sandbox.config.ini"

    # You MUST set this to your Ticketing App ID in TeamDynamix
    TICKETING_APP_ID = 0  # <-- CHANGE ME

    # Ticket "base" parameters (IDs will be selected dynamically in the script)
    TEST_TICKET_PARAMS: Dict[str, Any] = {
        "Title": "API Test Ticket (teamdynamix-api)",
        # Description will be appended with a unique string below
        "Description": "Created by automated endpoint test.",
        # Depending on your TDX configuration, you may need additional fields.
        # Add them here if create() fails with validation errors.
        # Example possibilities (varies by org):
        # "RequestorUid": "<some-guid>",
        # "AccountID": 0,
        # "CategoryID": 0,
    }

    # -----------------------------------------------------------------
    # 0) Generate unique string for Description
    # -----------------------------------------------------------------
    unique = f"TDX_API_TEST_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    print(f"[0] Unique search token: {unique}")

    # -----------------------------------------------------------------
    # Init session + clients
    # -----------------------------------------------------------------
    session = Session(CONFIG_PATH)

    # Optional: deterministic testing (force auth early)
    session.authenticate()

    tickets = Tickets(session, ticketing_app_id=TICKETING_APP_ID)
    priorities_client = TicketPriorities(session, ticketing_app_id=TICKETING_APP_ID)
    statuses_client = TicketStatuses(session, ticketing_app_id=TICKETING_APP_ID)
    sources_client = TicketSources(session, ticketing_app_id=TICKETING_APP_ID)
    types_client = TicketTypes(session, ticketing_app_id=TICKETING_APP_ID)

    # -----------------------------------------------------------------
    # 1) Get TicketPriorities via list()
    # -----------------------------------------------------------------
    priorities = priorities_client.list()
    print(f"[1] Priorities count: {len(priorities)}")

    # -----------------------------------------------------------------
    # 2) Get TicketStatuses via list()
    # -----------------------------------------------------------------
    statuses = statuses_client.list(is_active=True)
    print(f"[2] Statuses (active) count: {len(statuses)}")

    # -----------------------------------------------------------------
    # 3) Get TicketSources via list()
    # -----------------------------------------------------------------
    sources = sources_client.list(is_active=True)
    print(f"[3] Sources (active) count: {len(sources)}")

    # -----------------------------------------------------------------
    # 4) Get TicketTypes via list()
    # -----------------------------------------------------------------
    types = types_client.list(is_active=True)
    print(f"[4] Types (active) count: {len(types)}")

    # -----------------------------------------------------------------
    # 5) Create ticket with selected IDs
    # -----------------------------------------------------------------
    type_id = _pick_id_1_if_available(types)
    status_new_id = _pick_by_name(statuses, "New")
    status_cancelled_id = _pick_by_name(statuses, "Cancelled")
    source_api_id = _pick_by_name(sources, "API")
    priority_middle_id = _pick_middle_id(priorities)

    missing = []
    if type_id is None:
        missing.append("TypeID (no types returned)")
    if status_new_id is None:
        missing.append("StatusID for 'New' (no match)")
    if status_cancelled_id is None:
        missing.append("StatusID for 'Cancelled' (no match)")
    if source_api_id is None:
        missing.append("SourceID for 'API' (no match)")
    if priority_middle_id is None:
        missing.append("PriorityID (no priorities returned)")

    if missing:
        print("[5] Cannot proceed; missing required IDs:")
        for m in missing:
            print(f"    - {m}")
        return

    ticket_payload = dict(TEST_TICKET_PARAMS)
    ticket_payload["Description"] = f"{ticket_payload.get('Description', '')}\n\n{unique}"
    ticket_payload["TypeID"] = type_id
    ticket_payload["StatusID"] = status_new_id
    ticket_payload["SourceID"] = source_api_id
    ticket_payload["PriorityID"] = priority_middle_id

    print(f"[5] Creating ticket with IDs: TypeID={type_id}, StatusID(New)={status_new_id}, "
          f"SourceID(API)={source_api_id}, PriorityID(mid)={priority_middle_id}")

    created = tickets.create(ticket_payload)

    if not created.ID:
        print("[5] Ticket create returned no ID; cannot proceed.")
        return

    ticket_id = int(created.ID)
    print(f"[5] Created ticket ID: {ticket_id}")

    # -----------------------------------------------------------------
    # 6) Search tickets by SearchText = unique token
    # -----------------------------------------------------------------
    search_payload = {"SearchText": unique}
    print(f"[6] Searching tickets with payload: {search_payload}")
    search_results = tickets.search(search_payload)
    print(f"[6] Search results count: {len(search_results)}")

    if not search_results:
        print("[6] No search results found; cannot proceed.")
        return

    # Prefer the created ticket if it appears in results; else use the first result
    found_id = None
    for t in search_results:
        if t.ID == ticket_id:
            found_id = ticket_id
            break
    if found_id is None:
        found_id = int(search_results[0].ID) if search_results[0].ID else None

    if found_id is None:
        print("[6] Search returned tickets but none had an ID; cannot proceed.")
        return

    print(f"[6] Using ticket ID from search: {found_id}")

    # -----------------------------------------------------------------
    # 7) Get full ticket using Tickets.get()
    # -----------------------------------------------------------------
    got = tickets.get(found_id)
    if got is None or not got.ID:
        print(f"[7] Tickets.get failed for ID={found_id}")
        return
    print(f"[7] Got ticket: ID={got.ID}, Title={got.Title!r}, StatusID={got.StatusID}, TypeID={got.TypeID}")

    # -----------------------------------------------------------------
    # 8) Add a feed entry
    # -----------------------------------------------------------------
    feed_payload = {"Body": "Ticket feed test via API."}
    print(f"[8] Adding feed entry: {feed_payload}")
    tickets.add_feed_entry(found_id, feed_payload)
    print("[8] Feed entry added.")

    # -----------------------------------------------------------------
    # 9) Update the ticket: set StatusID -> 'Cancelled'
    # -----------------------------------------------------------------
    print(f"[9] Updating ticket StatusID -> Cancelled ({status_cancelled_id})")
    tickets.update(found_id, {"StatusID": status_cancelled_id})
    print("[9] Ticket updated to Cancelled.")

    # Optional: verify status changed
    verify = tickets.get(found_id)
    if verify is not None:
        print(f"[9] Verify status: StatusID={verify.StatusID}, StatusName={verify.StatusName}")

    print("Done.")


if __name__ == "__main__":
    main()
```

## File: .editorconfig
```
# .editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 4
trim_trailing_whitespace = true
```

## File: MANIFEST.in
```
include LICENSE
include README.md
recursive-include src/teamdynamix *.py
include src/teamdynamix/py.typed
```

## File: pyproject.toml
```toml
# =====================================================================
# FILE: pyproject.toml
# =====================================================================
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "teamdynamix-api"
version = "0.1.0"
description = "A Python SDK for the TeamDynamix Web API."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "University of Florida" }]
keywords = ["teamdynamix", "api", "sdk", "requests", "tdx"]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  "Typing :: Typed",
]
dependencies = [
  "requests>=2.31",
]

[project.optional-dependencies]
dev = [
  "pytest>=7.0",
  "pytest-cov>=4.1",
  "ruff>=0.5",
  "mypy>=1.10",
  "build>=1.2",
  "twine>=5.0",
]

[project.urls]
Homepage = "https://gitlab.it.ufl.edu/nicholas.linney/teamdynamix-api"
Repository = "https://gitlab.it.ufl.edu/nicholas.linney/teamdynamix-api"
"Issue Tracker" = "https://gitlab.it.ufl.edu/nicholas.linney/teamdynamix-api/-/issues"

[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.packages.find]
where = ["src"]
include = ["teamdynamix*"]

[tool.setuptools.package-data]
teamdynamix = ["py.typed"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_unused_ignores = true
ignore_missing_imports = true
strict = false
```

## File: pytest.ini
```
[pytest]
pythonpath = ["src"]
addopts = -q --cov=src/teamdynamix --cov-report=term-missing --cov-fail-under=80
```

## File: src/teamdynamix/projects.py
```python
# =====================================================================
# FILE: src/teamdynamix/projects.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

from .session import Session
from .transport import PatchPayload


def _as_list(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize an API response into list[dict].

    Rules:
      - None / [] -> []
      - dict -> [dict]
      - list -> only dict entries (filters safely)
      - anything else -> []
    """
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _as_dict(data: Any) -> Optional[Dict[str, Any]]:
    """
    Normalize an API response into dict | None.

    Rules:
      - None / {} -> None
      - dict -> dict
      - anything else -> None
    """
    if not data:
        return None
    return data if isinstance(data, dict) else None


@dataclass(slots=True)
class Project:
    """
    Minimal Project model.

    Keep this intentionally lean: the SDK should stay close to the vendor API
    surface. If callers need additional fields, they can access raw dicts from
    response.json() or we can expand this dataclass later with proven needs.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    IsActive: Optional[bool] = None
    Description: Optional[str] = None
    ManagerUid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            IsActive=data.get("IsActive"),
            Description=data.get("Description"),
            ManagerUid=data.get("ManagerUid") or data.get("ManagerUID"),
        )


class Projects:
    """
    Projects client for TeamDynamix PPM endpoints.

    Pattern: thin endpoint wrapper (keeps vendor API surface recognizable),
    using Session as the facade and Transport as the sole HTTP boundary.
    """

    _base_path = "/api/projects"

    def __init__(self, session: Session):
        self.session = session

    # ---------------------------
    # Core endpoints
    # ---------------------------

    def search(self, criteria: Dict[str, Any]) -> List[Project]:
        """
        POST /api/projects/search
        Returns: list of projects (possibly empty, which is valid).
        """
        self.session.log(f"Projects.search: keys={list(criteria.keys())}")
        resp = self.session.request("POST", f"{self._base_path}/search", json=criteria)
        items = _as_list(resp.json())
        return [Project.from_dict(item) for item in items]

    def get(self, project_id: int) -> Project:
        """
        GET /api/projects/{id}
        """
        self.session.log(f"Projects.get: id={project_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(project_id)}")
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.get (expected dict).")
        return Project.from_dict(data)

    def create(
        self,
        project_data: Dict[str, Any],
        *,
        notify_new_manager: bool = False,
        notify_new_alt_managers: bool = False,
    ) -> Project:
        """
        POST /api/projects
        Query:
          notifyNewManager (bool)
          notifyNewAltManagers (bool)
        """
        params = {
            "notifyNewManager": str(bool(notify_new_manager)).lower(),
            "notifyNewAltManagers": str(bool(notify_new_alt_managers)).lower(),
        }
        self.session.log(f"Projects.create: params={params}, keys={list(project_data.keys())}")
        resp = self.session.request("POST", self._base_path, params=params, json=project_data)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.create (expected dict).")
        return Project.from_dict(data)

    def edit(self, project_id: int, updates: Dict[str, Any]) -> Project:
        """
        POST /api/projects/{id}
        (TDX uses POST for edit on this resource.)
        """
        self.session.log(f"Projects.edit: id={project_id}, keys={list(updates.keys())}")
        resp = self.session.request("POST", f"{self._base_path}/{int(project_id)}", json=updates)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.edit (expected dict).")
        return Project.from_dict(data)

    def patch(
        self,
        project_id: int,
        operations: Union[List[PatchPayload], List[Dict[str, Any]], Dict[str, Any]],
    ) -> Project:
        """
        PATCH /api/projects/{id}

        Accepts:
          - list[PatchPayload]       -> serialized via .to_dict()
          - list[dict[str, Any]]     -> passed through unchanged (assumed already RFC6902)
          - dict[str, Any]           -> passed through; Transport converts dict->JSON Patch list for PATCH
        """
        payload: Any
        if isinstance(operations, dict):
            payload = operations  # Transport converts dict -> patch list (replace ops)
        elif isinstance(operations, list):
            if all(isinstance(op, PatchPayload) for op in operations):
                payload = [op.to_dict() for op in operations]
            elif all(isinstance(op, dict) for op in operations):
                payload = operations
            else:
                raise TypeError("Projects.patch operations list must be all PatchPayload or all dict.")
        else:
            raise TypeError("Projects.patch operations must be a dict, list[PatchPayload], or list[dict].")

        self.session.log(f"Projects.patch: id={project_id}")
        resp = self.session.request("PATCH", f"{self._base_path}/{int(project_id)}", json=payload)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.patch (expected dict).")
        return Project.from_dict(data)

    # ---------------------------
    # Project Feed endpoints
    # ---------------------------

    def get_feed(self, project_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/projects/{id}/feed
        Returns [] when empty (valid).
        """
        self.session.log(f"Projects.get_feed: project_id={project_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(project_id)}/feed")
        return _as_list(resp.json())

    def add_feed(self, project_id: int, body: str) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/feed
        Body: { "Body": "<string>" }
        """
        payload = {"Body": body}
        self.session.log(f"Projects.add_feed: project_id={project_id}")
        resp = self.session.request("POST", f"{self._base_path}/{int(project_id)}/feed", json=payload)
        return _as_dict(resp.json()) or {}

    # ---------------------------
    # Plan / task endpoints
    # ---------------------------

    def get_plan(self, project_id: int, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/projects/{projectId}/plans/{planId}
        """
        self.session.log(f"Projects.get_plan: project_id={project_id}, plan_id={plan_id}")
        resp = self.session.request(
            "GET",
            f"{self._base_path}/{int(project_id)}/plans/{int(plan_id)}",
        )
        return _as_dict(resp.json())

    def edit_task(
        self,
        project_id: int,
        plan_id: int,
        task_id: int,
        updates: Dict[str, Any],
        *,
        notify_new_resources: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        POST /api/projects/{projectId}/plans/{planId}/tasks/{taskId}/edit
        Query:
          notifyNewResources (bool)
        """
        params = {"notifyNewResources": str(bool(notify_new_resources)).lower()}
        self.session.log(
            f"Projects.edit_task: project_id={project_id}, plan_id={plan_id}, task_id={task_id}, params={params}"
        )
        resp = self.session.request(
            "POST",
            f"{self._base_path}/{int(project_id)}/plans/{int(plan_id)}/tasks/{int(task_id)}/edit",
            params=params,
            json=updates,
        )
        return _as_dict(resp.json())

    # ---------------------------
    # Issue feed endpoints
    # ---------------------------

    def get_issue_feed(self, project_id: int, issue_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/projects/{projectId}/issues/{issueId}/feed
        Returns [] when empty (valid).
        """
        self.session.log(f"Projects.get_issue_feed: project_id={project_id}, issue_id={issue_id}")
        resp = self.session.request(
            "GET",
            f"{self._base_path}/{int(project_id)}/issues/{int(issue_id)}/feed",
        )
        return _as_list(resp.json())

    def add_issue_comment(self, project_id: int, issue_id: int, comment_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/issues/{issueId}/feed
        Body: (per Postman / TDX schema; typically includes "Body")
        """
        self.session.log(f"Projects.add_issue_comment: project_id={project_id}, issue_id={issue_id}")
        resp = self.session.request(
            "POST",
            f"{self._base_path}/{int(project_id)}/issues/{int(issue_id)}/feed",
            json=comment_payload,
        )
        return _as_dict(resp.json()) or {}
```

## File: src/teamdynamix/session.py
```python
# =====================================================================
# FILE: src/teamdynamix/session.py
# =====================================================================
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Union, Literal, Mapping

from .auth import Auth
from .config import Config, AuthMode
from .logger import Logger
from .transport import Transport
from .exceptions import ConfigError


TdxEnvironment = Literal["TD", "SBTD"]
ConfigSource = Union[str, Path, Config, Mapping[str, Any], None]


class Session:
    """
    Composition Root / Facade for the TeamDynamix client library.

    Enhanced constructor (pre-alpha.10):
      - config may be: path | Config | dict-like overlay | None
      - overrides may be: dict of key-value pairs applied after base config
      - auth_mode/environment can be overridden explicitly (validated literals)
    """

    def __init__(
        self,
        config: ConfigSource = "./config/config.ini",
        *,
        auth_mode: Optional[AuthMode] = None,
        environment: Optional[TdxEnvironment] = None,
        overrides: Optional[Mapping[str, Any]] = None,
    ):
        # 1) Resolve base config
        base_cfg: Optional[Config] = None
        overlay: Dict[str, Any] = {}

        if config is None:
            # default behavior: load from default ini path
            base_cfg = Config.from_file("./config/config.ini")
        elif isinstance(config, (str, Path)):
            base_cfg = Config.from_file(config)
        elif isinstance(config, Config):
            # Config is already validated and complete by design.
            base_cfg = config
        elif isinstance(config, Mapping):
            # Partial overlays are allowed here (validated only after merge/build).
            overlay.update(dict(config))
        else:
            raise ConfigError("Invalid config argument. Expected path, Config, mapping, or None.")

        # 2) Merge overlays in correct precedence order:
        #    base_cfg < config-mapping (if provided) < overrides < explicit keyword overrides
        merged: Dict[str, Any] = {}
        if base_cfg is not None:
            merged.update(asdict(base_cfg))

        merged.update(overlay)
        if overrides:
            merged.update(dict(overrides))

        if auth_mode is not None:
            mode = (auth_mode or "").strip().lower()
            if mode not in ("admin", "user"):
                raise ConfigError("Invalid auth_mode override. Expected 'admin' or 'user'.")
            merged["auth_mode"] = mode

        if environment is not None:
            env = (environment or "").strip().upper()
            if env not in ("TD", "SBTD"):
                raise ConfigError("Invalid environment override. Expected 'TD' or 'SBTD'.")
            merged["environment"] = env

        # 3) Build Config once (single validation point)
        #    ConfigError should only occur here if required fields remain missing/invalid.
        try:
            self.config = Config(**merged)  # type: ignore[arg-type]
        except TypeError as e:
            # Common cause: unknown key in overrides dict
            raise ConfigError(f"Invalid configuration keys provided: {e}") from e

        # 4) Wire dependencies (Composition Root)
        self.logger = Logger(
            log_dir=self.config.log_dir,
            level=self.config.log_level,
            console=self.config.log_console,
        )

        self.transport = Transport(
            logger=self.logger,
            default_timeout=self.config.timeout,
        )

        self.auth = Auth(
            config=self.config,
            logger=self.logger,
            transport=self.transport,
        )

    # ---- Facade properties/methods used by client modules ----

    @property
    def base_url(self) -> str:
        return self.config.base_url

    def log(self, message: str, *, level: int = 20) -> None:
        self.logger.log(message, level=level)

    def authenticate(self) -> str:
        """
        Optional explicit auth call for intentionality/testing.
        Otherwise token retrieval happens lazily when auth_header() is requested.
        """
        return self.auth.authenticate()

    def auth_header(self) -> Dict[str, str]:
        token = self.auth.get_token()
        return {"Authorization": f"Bearer {token}"}

    def request(self, method: str, path: str, **kwargs: Any):
        """
        Primary request entrypoint for all client modules.

        Returns: requests.Response
        """
        url = f"{self.base_url}{path}"
        return self.transport.request(
            method=method,
            url=url,
            headers=kwargs.pop("headers", None) or self.auth_header(),
            params=kwargs.pop("params", None),
            json=kwargs.pop("json", None),
            data=kwargs.pop("data", None),
            timeout=kwargs.pop("timeout", None),
        )
```

## File: .gitignore
```
# .gitignore
.DS_Store
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.cache/
.dist/
build/
dist/
.venv/
venv/
.env
.pytest_cache/
.mypy_cache/
coverage.xml
htmlcov/
logs/

# Ignore everything in config/
config/*

# But keep this specific file
!config/sample.config.ini
```
