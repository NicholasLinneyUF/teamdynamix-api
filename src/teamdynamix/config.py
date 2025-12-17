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
