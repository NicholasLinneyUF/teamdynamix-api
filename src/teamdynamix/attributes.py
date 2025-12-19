# =====================================================================
# FILE: src/teamdynamix/attributes.py
# =====================================================================
"""
Client for the TeamDynamix *Attributes* API surface.

This module preserves the legacy listing endpoints and adds parity with the
Postman Attributes folder for:

- Attribute Choices sub-resource:
    GET    /api/attributes/{id}/choices
    POST   /api/attributes/{id}/choices?copyFromChoiceId=
    PUT    /api/attributes/{id}/choices/{choiceId}
    DELETE /api/attributes/{id}/choices/{choiceId}

- Custom Attributes lookup:
    GET /api/attributes/custom?componentId=&associatedTypeId=&appId=

Patterns:
- Client modules receive a Session and call session.request(...)
- Response-first: resp = session.request(...); data = resp.json()
- Raw methods return dict/list[dict]; typed wrappers return DTOs
- Empty responses are valid and must not throw
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


# -------------------------------------------------------------------
# Response normalization helpers (consistent with pre-alpha10 style)
# -------------------------------------------------------------------
def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize an API response into list[dict].

    Rules:
      - None / [] / {} -> []
      - dict -> [dict]
      - list -> dict entries only
      - anything else -> []
    """
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _as_dict(data: Any) -> Optional[Dict[str, Any]]:
    """
    Normalize an API response into dict | None.

    Rules:
      - None / {} -> None
      - dict -> dict
      - anything else -> None
    """
    if not data:
        return None
    return data if isinstance(data, dict) else None


# -------------------------------------------------------------------
# DTOs (selective / lightweight)
# -------------------------------------------------------------------
@dataclass(slots=True)
class Attribute:
    """
    Minimal Attribute DTO – intentionally lean.

    Keep fields small and stable; callers can use raw methods for full payloads.
    """

    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None
    IsDefault: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attribute":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
            IsDefault=data.get("IsDefault"),
        )


@dataclass(slots=True)
class AttributeChoice:
    """
    DTO representing an Attribute Choice (selectable options for an Attribute).

    Fields align with the Postman/OpenAPI schema:
      ID, Name, IsActive, DateCreated, DateModified, Order
    """

    ID: Optional[int] = None
    Name: Optional[str] = None
    IsActive: Optional[bool] = None
    DateCreated: Optional[str] = None
    DateModified: Optional[str] = None
    Order: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttributeChoice":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            IsActive=data.get("IsActive"),
            DateCreated=data.get("DateCreated"),
            DateModified=data.get("DateModified"),
            Order=data.get("Order"),
        )


# -------------------------------------------------------------------
# Client
# -------------------------------------------------------------------
class Attributes:
    """
    Attributes client.

    Legacy list endpoints preserved:
      - GET /api/applications/{appId}/attributes/{component}
      - GET /api/attributes/{component}
      - GET /api/attributes

    Added endpoints (Postman parity):
      - GET    /api/attributes/{id}/choices
      - POST   /api/attributes/{id}/choices?copyFromChoiceId=
      - PUT    /api/attributes/{id}/choices/{choiceId}
      - DELETE /api/attributes/{id}/choices/{choiceId}
      - GET    /api/attributes/custom?componentId=&associatedTypeId=&appId=
    """

    _base_path = "/api/attributes"

    def __init__(self, session: Session):
        self.session = session

    # -----------------------------------------------------------------
    # Legacy “Attributes” listing helpers (preserve names/behavior)
    # -----------------------------------------------------------------
    def list_for_application_component_raw(self, app_id: int, component: str) -> List[Dict[str, Any]]:
        """
        GET /api/applications/{appId}/attributes/{component}
        Returns raw list[dict] (possibly empty, valid).
        """
        component = component.strip().strip("/")
        path = f"/api/applications/{int(app_id)}/attributes/{component}"
        self.session.log(f"Attributes.list_for_application_component_raw: app_id={app_id}, component={component}")
        resp = self.session.request("GET", path)
        return _as_list_of_dicts(resp.json())

    def list_for_application_component(self, app_id: int, component: str) -> List[Attribute]:
        """
        GET /api/applications/{appId}/attributes/{component}
        Returns typed Attribute list (possibly empty, valid).
        """
        return [Attribute.from_dict(x) for x in self.list_for_application_component_raw(app_id, component)]

    def list_for_component_raw(self, component: str) -> List[Dict[str, Any]]:
        """
        GET /api/attributes/{component}
        Returns raw list[dict] (possibly empty, valid).
        """
        component = component.strip().strip("/")
        path = f"{self._base_path}/{component}"
        self.session.log(f"Attributes.list_for_component_raw: component={component}")
        resp = self.session.request("GET", path)
        return _as_list_of_dicts(resp.json())

    def list_for_component(self, component: str) -> List[Attribute]:
        """
        GET /api/attributes/{component}
        Returns typed Attribute list (possibly empty, valid).
        """
        return [Attribute.from_dict(x) for x in self.list_for_component_raw(component)]

    def list_all_raw(self) -> List[Dict[str, Any]]:
        """
        GET /api/attributes
        Returns raw list[dict] (possibly empty, valid).
        """
        self.session.log("Attributes.list_all_raw")
        resp = self.session.request("GET", self._base_path)
        return _as_list_of_dicts(resp.json())

    def list_all(self) -> List[Attribute]:
        """
        GET /api/attributes
        Returns typed Attribute list (possibly empty, valid).
        """
        return [Attribute.from_dict(x) for x in self.list_all_raw()]

    # -----------------------------------------------------------------
    # Attribute Choices (Postman parity)
    # -----------------------------------------------------------------
    def list_choices_raw(self, attribute_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/attributes/{id}/choices
        Returns raw list[dict] (possibly empty, valid).
        """
        self.session.log(f"Attributes.list_choices_raw: attribute_id={attribute_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(attribute_id)}/choices")
        return _as_list_of_dicts(resp.json())

    def list_choices(self, attribute_id: int) -> List[AttributeChoice]:
        """
        GET /api/attributes/{id}/choices
        Returns typed AttributeChoice list (possibly empty, valid).
        """
        return [AttributeChoice.from_dict(x) for x in self.list_choices_raw(attribute_id)]

    def add_choice_raw(
        self,
        attribute_id: int,
        choice_payload: Dict[str, Any],
        *,
        copy_from_choice_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        POST /api/attributes/{id}/choices?copyFromChoiceId=

        Parameters
        ----------
        choice_payload:
            Raw payload dict per TDX schema (typically includes Name, IsActive, Order; ID may be blank).
        copy_from_choice_id:
            Optional query param to clone from an existing choice.

        Returns
        -------
        Dict[str, Any]
            Raw created choice dict (or {} if API returns non-dict/empty).
        """
        params: Dict[str, Any] = {}
        if copy_from_choice_id is not None:
            params["copyFromChoiceId"] = str(int(copy_from_choice_id))

        self.session.log(f"Attributes.add_choice_raw: attribute_id={attribute_id}, params={params}")
        resp = self.session.request(
            "POST",
            f"{self._base_path}/{int(attribute_id)}/choices",
            params=params if params else None,
            json=choice_payload,
        )
        return _as_dict(resp.json()) or {}

    def add_choice(
        self,
        attribute_id: int,
        choice_payload: Dict[str, Any],
        *,
        copy_from_choice_id: Optional[int] = None,
    ) -> AttributeChoice:
        """
        POST /api/attributes/{id}/choices?copyFromChoiceId=
        Returns typed AttributeChoice.
        """
        raw = self.add_choice_raw(attribute_id, choice_payload, copy_from_choice_id=copy_from_choice_id)
        return AttributeChoice.from_dict(raw)

    def edit_choice_raw(self, attribute_id: int, choice_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        PUT /api/attributes/{id}/choices/{choiceId}
        Returns raw updated choice dict (or {} if API returns non-dict/empty).
        """
        self.session.log(f"Attributes.edit_choice_raw: attribute_id={attribute_id}, choice_id={choice_id}")
        resp = self.session.request(
            "PUT",
            f"{self._base_path}/{int(attribute_id)}/choices/{int(choice_id)}",
            json=payload,
        )
        return _as_dict(resp.json()) or {}

    def edit_choice(self, attribute_id: int, choice_id: int, payload: Dict[str, Any]) -> AttributeChoice:
        """
        PUT /api/attributes/{id}/choices/{choiceId}
        Returns typed AttributeChoice.
        """
        raw = self.edit_choice_raw(attribute_id, choice_id, payload)
        return AttributeChoice.from_dict(raw)

    def delete_choice_raw(self, attribute_id: int, choice_id: int) -> bool:
        """
        DELETE /api/attributes/{id}/choices/{choiceId}
        Returns True on success.
        """
        self.session.log(f"Attributes.delete_choice_raw: attribute_id={attribute_id}, choice_id={choice_id}")
        self.session.request("DELETE", f"{self._base_path}/{int(attribute_id)}/choices/{int(choice_id)}")
        return True

    def delete_choice(self, attribute_id: int, choice_id: int) -> bool:
        """
        DELETE /api/attributes/{id}/choices/{choiceId}
        Returns True on success.
        """
        return self.delete_choice_raw(attribute_id, choice_id)

    # -----------------------------------------------------------------
    # Custom Attributes (Postman parity)
    # -----------------------------------------------------------------
    def list_custom_raw(
        self,
        *,
        component_id: Optional[int] = None,
        associated_type_id: Optional[int] = None,
        app_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        GET /api/attributes/custom?componentId=&associatedTypeId=&appId=

        All query params are optional; omitted params are not sent.
        Returns raw list[dict] (possibly empty, valid).
        """
        params: Dict[str, Any] = {}
        if component_id is not None:
            params["componentId"] = str(int(component_id))
        if associated_type_id is not None:
            params["associatedTypeId"] = str(int(associated_type_id))
        if app_id is not None:
            params["appId"] = str(int(app_id))

        self.session.log(f"Attributes.list_custom_raw: params={params}")
        resp = self.session.request("GET", f"{self._base_path}/custom", params=params if params else None)
        return _as_list_of_dicts(resp.json())

    def list_custom(
        self,
        *,
        component_id: Optional[int] = None,
        associated_type_id: Optional[int] = None,
        app_id: Optional[int] = None,
    ) -> List[Attribute]:
        """
        GET /api/attributes/custom?componentId=&associatedTypeId=&appId=
        Returns typed Attribute list (possibly empty, valid).
        """
        return [
            Attribute.from_dict(x)
            for x in self.list_custom_raw(
                component_id=component_id,
                associated_type_id=associated_type_id,
                app_id=app_id,
            )
        ]

    # Back-compat / symmetry aliases (optional but harmless)
    get_custom_by_component_raw = list_custom_raw
    get_custom_by_component = list_custom
    list_custom_by_component_raw = list_custom_raw
    list_custom_by_component = list_custom
