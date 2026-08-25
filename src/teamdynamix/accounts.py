# =====================================================================
# FILE: src/teamdynamix/accounts.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ._response import as_list_of_dicts as _as_list_of_dicts
from ._response import first_dict_or_none as _first_or_none
from .session import Session


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
