# =====================================================================
# FILE: src/teamdynamix/service_catalog.py
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
class Service:
    """
    Minimal Service Catalog DTO.

    The service catalog payload/response shape varies by tenant configuration, so we keep
    this intentionally small and rely on raw dicts for everything else.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Service":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
        )


class ServiceCatalog:
    """
    Service Catalog client, matching the Postman collection endpoints:

      GET    /api/{portalAppId}/services
      POST   /api/{portalAppId}/services
      GET    /api/{portalAppId}/services/{id}
      PUT    /api/{portalAppId}/services/{id}
      DELETE /api/{portalAppId}/services/{id}

    Notes:
    - We keep helper methods minimal and endpoint-representative.
    - 200 OK with [] is a valid “no results” outcome.
    """

    def __init__(self, session: Session, portal_app_id: int):
        self.session = session
        self.portal_app_id = int(portal_app_id)
        self._base_path = f"/api/{self.portal_app_id}/services"

    # ---- List
    def list_raw(self) -> List[Dict[str, Any]]:
        self.session.log(f"ServiceCatalog.list_raw: portal_app_id={self.portal_app_id}")
        resp = self.session.request("GET", self._base_path)
        return _as_list_of_dicts(resp.json())

    def list(self) -> List[Service]:
        return [Service.from_dict(x) for x in self.list_raw()]

    # ---- Get
    def get_raw(self, service_id: int) -> Dict[str, Any]:
        self.session.log(
            f"ServiceCatalog.get_raw: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        resp = self.session.request("GET", f"{self._base_path}/{int(service_id)}")
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.get (expected dict).")
        return data

    def get(self, service_id: int) -> Service:
        return Service.from_dict(self.get_raw(service_id))

    # ---- Create
    def create_raw(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.session.log(f"ServiceCatalog.create_raw: portal_app_id={self.portal_app_id}")
        resp = self.session.request("POST", self._base_path, json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.create (expected dict).")
        return data

    def create(self, payload: Dict[str, Any]) -> Service:
        return Service.from_dict(self.create_raw(payload))

    # ---- Update
    def update_raw(self, service_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.session.log(
            f"ServiceCatalog.update_raw: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        resp = self.session.request("PUT", f"{self._base_path}/{int(service_id)}", json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.update (expected dict).")
        return data

    def update(self, service_id: int, payload: Dict[str, Any]) -> Service:
        return Service.from_dict(self.update_raw(service_id, payload))

    # ---- Delete
    def delete(self, service_id: int) -> bool:
        self.session.log(
            f"ServiceCatalog.delete: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        self.session.request("DELETE", f"{self._base_path}/{int(service_id)}")
        return True
