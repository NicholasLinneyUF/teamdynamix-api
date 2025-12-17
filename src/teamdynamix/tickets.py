# =====================================================================
# FILE: src/teamdynamix/tickets.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .session import Session
from .transport import PatchPayload  # exported publicly via __init__.py per your plan


def _first_or_none(data: Any) -> Optional[Dict[str, Any]]:
    """
    TDX endpoints sometimes return either:
      - an object (dict)
      - a list of objects (list[dict])
      - an empty list []
    Normalize to "first dict or None".
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


def _patch_ops_json(
    ops: Union[Dict[str, Any], List[PatchPayload], List[Dict[str, Any]]]
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    We allow three shapes:
      1) dict[str, Any]  -> Transport will convert to JSON Patch (replace ops) for PATCH
      2) list[PatchPayload] -> we convert to list[dict]
      3) list[dict] -> passed through

    This keeps Tickets.update() endpoint-aligned (PATCH = JSON Patch),
    but still lets callers use the simple {"Field": "Value"} form.
    """
    if isinstance(ops, dict):
        return ops

    out: List[Dict[str, Any]] = []
    for item in ops:
        if isinstance(item, PatchPayload):
            out.append({"op": item.op, "path": item.path, "value": item.value})
        elif isinstance(item, dict):
            out.append(item)
    return out


# ---------------------------------------------------------------------
# DTOs (minimal: just enough to be useful without over-modeling)
# ---------------------------------------------------------------------
@dataclass(slots=True)
class Ticket:
    ID: Optional[int] = None
    Title: Optional[str] = None
    Description: Optional[str] = None
    StatusID: Optional[int] = None
    StatusName: Optional[str] = None
    TypeID: Optional[int] = None
    TypeName: Optional[str] = None
    PriorityID: Optional[int] = None
    PriorityName: Optional[str] = None
    RequestorUid: Optional[str] = None
    ResponsibleUid: Optional[str] = None
    ResponsibleGroupID: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Title=data.get("Title"),
            Description=data.get("Description"),
            StatusID=data.get("StatusID"),
            StatusName=data.get("StatusName"),
            TypeID=data.get("TypeID"),
            TypeName=data.get("TypeName"),
            PriorityID=data.get("PriorityID"),
            PriorityName=data.get("PriorityName"),
            RequestorUid=data.get("RequestorUid") or data.get("RequestorUID"),
            ResponsibleUid=data.get("ResponsibleUid") or data.get("ResponsibleUID"),
            ResponsibleGroupID=data.get("ResponsibleGroupID") or data.get("ResponsibleGroupId"),
        )


# ---------------------------------------------------------------------
# Meta endpoints (priorities/types/statuses/sources)
# ---------------------------------------------------------------------
class TicketPriorities:
    """
    Ticket priorities are per ticketing app.

    GET /api/{ticketingAppId}/tickets/priorities
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self) -> List[Dict[str, Any]]:
        self.session.log("TicketPriorities.list")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/priorities")
        return resp.json() or []


class TicketTypes:
    """
    Ticket types are per ticketing app.

    GET /api/{ticketingAppId}/tickets/types?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketTypes.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/types", params=params)
        return resp.json() or []


class TicketStatuses:
    """
    Ticket statuses are per ticketing app.

    GET /api/{ticketingAppId}/tickets/statuses?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketStatuses.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/statuses", params=params)
        return resp.json() or []


class TicketSources:
    """
    Ticket sources are per ticketing app.

    GET /api/{ticketingAppId}/tickets/sources?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketSources.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/sources", params=params)
        return resp.json() or []


# ---------------------------------------------------------------------
# Tickets client
# ---------------------------------------------------------------------
class Tickets:
    """
    Tickets client is per ticketing app.

    Common endpoints (per Postman):
      - GET    /api/{ticketingAppId}/tickets/{id}
      - POST   /api/{ticketingAppId}/tickets/search
      - POST   /api/{ticketingAppId}/tickets
      - PATCH  /api/{ticketingAppId}/tickets/{id}?notifyNewResponsible=
      - GET    /api/{ticketingAppId}/tickets/{id}/feed
      - POST   /api/{ticketingAppId}/tickets/{id}/feed
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)
        self._base = f"/api/{self.ticketing_app_id}/tickets"

    # --- Core CRUD-ish
    def get(self, ticket_id: int) -> Optional[Ticket]:
        self.session.log(f"Tickets.get: id={ticket_id}")
        resp = self.session.request("GET", f"{self._base}/{int(ticket_id)}")
        item = _first_or_none(resp.json())
        return Ticket.from_dict(item) if item is not None else None

    def create(self, ticket_payload: Dict[str, Any]) -> Ticket:
        """
        POST /api/{ticketingAppId}/tickets
        Returns created ticket object.
        """
        self.session.log("Tickets.create")
        resp = self.session.request("POST", self._base, json=ticket_payload)
        data = resp.json()
        if not isinstance(data, dict):
            # keep minimal: if API ever returns non-object here, just coerce to empty dict
            data = {}
        return Ticket.from_dict(data)

    def search(self, search_payload: Dict[str, Any]) -> List[Ticket]:
        """
        POST /api/{ticketingAppId}/tickets/search
        Returns list of tickets (possibly empty list []).
        """
        self.session.log("Tickets.search")
        resp = self.session.request("POST", f"{self._base}/search", json=search_payload)
        rows = resp.json() or []
        return [Ticket.from_dict(x) for x in rows if isinstance(x, dict)]

    def update(
        self,
        ticket_id: int,
        ops: Union[Dict[str, Any], List[PatchPayload], List[Dict[str, Any]]],
        *,
        notify_new_responsible: Optional[bool] = None,
    ) -> bool:
        """
        PATCH /api/{ticketingAppId}/tickets/{id}?notifyNewResponsible=
        Body is JSON Patch list. We also accept a simple dict of field->value,
        which Transport will convert into JSON Patch "replace" operations.

        Returns True on success.
        """
        params: Dict[str, Any] = {}
        if notify_new_responsible is not None:
            params["notifyNewResponsible"] = str(notify_new_responsible).lower()

        payload = _patch_ops_json(ops)
        self.session.log(f"Tickets.update: id={ticket_id}, params={params}")
        self.session.request("PATCH", f"{self._base}/{int(ticket_id)}", params=params, json=payload)
        return True

    # --- Feed
    def get_feed(self, ticket_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/{ticketingAppId}/tickets/{id}/feed
        """
        self.session.log(f"Tickets.get_feed: id={ticket_id}")
        resp = self.session.request("GET", f"{self._base}/{int(ticket_id)}/feed")
        return _as_list_of_dicts(resp.json())

    def add_feed_entry(self, ticket_id: int, feed_payload: Dict[str, Any]) -> bool:
        """
        POST /api/{ticketingAppId}/tickets/{id}/feed
        Returns True on success.
        """
        self.session.log(f"Tickets.add_feed_entry: id={ticket_id}")
        self.session.request("POST", f"{self._base}/{int(ticket_id)}/feed", json=feed_payload)
        return True
