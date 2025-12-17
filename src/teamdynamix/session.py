# =====================================================================
# FILE: src/teamdynamix/session.py
# =====================================================================
from __future__ import annotations

from typing import Optional, Any, Dict

from .config import Config
from .logger import Logger
from .transport import Transport
from .auth import Auth


class Session:
    """
    Composition root / facade:
    - builds Config, Logger, Transport, Auth
    - provides a small request surface and auth helpers
    - no network calls during __init__
    """
    def __init__(
        self,
        config_path: str = "./config/config.ini",
        *,
        config: Optional[Config] = None,
        logger: Optional[Logger] = None,
        transport: Optional[Transport] = None,
        auth: Optional[Auth] = None,
        default_timeout_seconds: Optional[int] = None,  # optional script override
    ):
        self.config = config or Config.from_file(config_path)

        # Logger defaults: ERROR level, ignore warnings by default
        self.logger = logger or Logger(
            log_dir=self.config.log_dir,
            level=self.config.log_level,
            console=self.config.log_console,
        )

        # Effective timeout: script override wins; else config.timeout (None if disabled)
        effective_timeout = self.config.timeout if default_timeout_seconds is None else (
            None if default_timeout_seconds == 0 else default_timeout_seconds
        )

        self.transport = transport or Transport(logger=self.logger, default_timeout=effective_timeout)

        # Auth uses Transport (single transport boundary); Session does NOT authenticate here
        self.auth = auth or Auth(config=self.config, logger=self.logger, transport=self.transport)

    @property
    def base_url(self) -> str:
        return self.config.base_url

    def authenticate(self, *, force_refresh: bool = False) -> str:
        """
        Optional explicit call for intentionality/testing.
        - If force_refresh=False, returns cached token if present.
        - If force_refresh=True, forces a network auth.
        """
        return self.auth.get_token(force_refresh=force_refresh)

    def auth_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.auth.get_token()}"}

    def log(self, message: str, level: int = 20, context: Optional[dict] = None) -> None:
        self.logger.log(message, level=level, context=context)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict] = None,
        json: Any = None,
        data: Any = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,     # per-call override (None uses Transport default)
        auth: bool = True,                 # disable for auth endpoints if needed
    ):
        """
        Central request entry point for API clients.
        - Builds URL from base_url + path
        - Injects Authorization header by default
        - Uses Transport for actual HTTP + error translation
        """
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        merged_headers: Dict[str, str] = {}
        if headers:
            merged_headers.update(headers)
        if auth:
            merged_headers.update(self.auth_header())

        return self.transport.request(
            method=method,
            url=url,
            headers=merged_headers,
            params=params,
            json=json,
            data=data,
            timeout=timeout,
        )
