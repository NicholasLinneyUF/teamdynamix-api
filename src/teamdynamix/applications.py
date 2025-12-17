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
