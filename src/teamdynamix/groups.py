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
