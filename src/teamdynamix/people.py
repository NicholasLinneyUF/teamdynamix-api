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
