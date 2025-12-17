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