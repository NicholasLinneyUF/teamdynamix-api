# =====================================================================
# FILE: src/teamdynamix/attributes.py
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
class Attribute:
    """
    Minimal Attribute DTO. Attributes can vary widely by org and entity type,
    so we keep this intentionally small.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None
    IsRequired: Optional[bool] = None
    DataType: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attribute":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
            IsRequired=data.get("IsRequired"),
            DataType=data.get("DataType") or data.get("Type"),
        )


class Attributes:
    """
    Attributes client.

    TeamDynamix attributes are usually scoped to an application and an entity type.
    Endpoint shapes vary by tenant; this module stays endpoint-representative and minimal.

    Common patterns seen in TDX environments include:
      - GET /api/applications/{appId}/attributes/{component}
      - GET /api/attributes/{component}
      - GET /api/attributes

    This module supports a flexible but explicit set of methods:
      1) list_for_application_component(app_id, component)
      2) list_for_component(component)
      3) list_all()

    If your tenant only supports one of these, use the corresponding method.
    """
    def __init__(self, session: Session):
        self.session = session

    def list_for_application_component_raw(self, app_id: int, component: str) -> List[Dict[str, Any]]:
        """
        GET /api/applications/{appId}/attributes/{component}
        """
        component = component.strip().strip("/")
        path = f"/api/applications/{int(app_id)}/attributes/{component}"
        self.session.log(f"Attributes.list_for_application_component_raw: app_id={app_id}, component={component}")
        resp = self.session.request("GET", path)
        return _as_list_of_dicts(resp.json())

    def list_for_application_component(self, app_id: int, component: str) -> List[Attribute]:
        return [Attribute.from_dict(x) for x in self.list_for_application_component_raw(app_id, component)]

    def list_for_component_raw(self, component: str) -> List[Dict[str, Any]]:
        """
        GET /api/attributes/{component}
        """
        component = component.strip().strip("/")
        path = f"/api/attributes/{component}"
        self.session.log(f"Attributes.list_for_component_raw: component={component}")
        resp = self.session.request("GET", path)
        return _as_list_of_dicts(resp.json())

    def list_for_component(self, component: str) -> List[Attribute]:
        return [Attribute.from_dict(x) for x in self.list_for_component_raw(component)]

    def list_all_raw(self) -> List[Dict[str, Any]]:
        """
        GET /api/attributes
        """
        self.session.log("Attributes.list_all_raw")
        resp = self.session.request("GET", "/api/attributes")
        return _as_list_of_dicts(resp.json())

    def list_all(self) -> List[Attribute]:
        return [Attribute.from_dict(x) for x in self.list_all_raw()]
