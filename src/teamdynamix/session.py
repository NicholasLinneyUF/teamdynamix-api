# =====================================================================
# FILE: src/teamdynamix/session.py
# =====================================================================
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from .auth import Auth
from .config import AuthMode, Config
from .exceptions import ConfigError
from .logger import Logger
from .transport import Transport

TdxEnvironment = Literal["TD", "SBTD"]
ConfigSource = str | Path | Config | Mapping[str, Any] | None


class Session:
    """
    Composition Root / Facade for the TeamDynamix client library.

    Enhanced constructor (pre-alpha.10):
      - config may be: path | Config | dict-like overlay | None
      - overrides may be: dict of key-value pairs applied after base config
      - auth_mode/environment can be overridden explicitly (validated literals)
      - name_prefix customizes the session log filename prefix
    """

    def __init__(
        self,
        config: ConfigSource = "./config/config.ini",
        *,
        auth_mode: AuthMode | None = None,
        environment: TdxEnvironment | None = None,
        overrides: Mapping[str, Any] | None = None,
        name_prefix: str | None = None,
    ) -> None:
        # 1) Resolve base config
        base_cfg: Config | None = None
        overlay: dict[str, Any] = {}

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
        merged: dict[str, Any] = {}
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
            self.config = Config(**merged)
        except TypeError as e:
            # Common cause: unknown key in overrides dict
            raise ConfigError(f"Invalid configuration keys provided: {e}") from e

        # 4) Wire dependencies (Composition Root)
        self.logger = Logger(
            log_dir=self.config.log_dir,
            level=self.config.log_level,
            console=self.config.log_console,
            name_prefix=name_prefix or "log",
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

    def auth_header(self) -> dict[str, str]:
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
