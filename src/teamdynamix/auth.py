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
