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
