# =====================================================================
# FILE: tests/test_ticket_endpoints.py
#
# Minimal endpoint test script for Tickets API client.
# - Assumes your config is valid at ./config/sandbox.config.ini (adjust as needed).
# - Assumes you have implemented: Tickets, TicketPriorities, TicketStatuses, TicketSources, TicketTypes.
# - Assumes PATCH JSON Patch handling is centralized in Transport (dict -> JSON Patch list).
#
# Workflow:
# 0) Generate unique string for Description (used later for search)
# 1) List priorities
# 2) List statuses
# 3) List sources
# 4) List types
# 5) Create ticket with:
#    - TypeID: 1 if available else fallback
#    - StatusID: "New"
#    - SourceID: "API"
#    - PriorityID: middle priority (by sorted ID)
# 6) Search tickets by the random string
# 7) Get full ticket by ID
# 8) Add feed entry
# 9) Update ticket StatusID to "Cancelled"
# =====================================================================

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from teamdynamix.session import Session
from teamdynamix.tickets import (
    Tickets,
    TicketPriorities,
    TicketStatuses,
    TicketSources,
    TicketTypes,
)


def _pick_by_name(
    rows: List[Dict[str, Any]],
    desired: str,
    *,
    name_keys: Tuple[str, ...] = ("Name", "name", "StatusName", "SourceName", "TypeName"),
    id_keys: Tuple[str, ...] = ("ID", "Id", "id"),
) -> Optional[int]:
    """
    Find a row whose name matches desired (case-insensitive) and return its ID.
    """
    desired_norm = desired.strip().lower()
    for row in rows:
        if not isinstance(row, dict):
            continue
        name_val = None
        for k in name_keys:
            if k in row and row.get(k) is not None:
                name_val = str(row.get(k))
                break
        if name_val is None:
            continue
        if name_val.strip().lower() == desired_norm:
            for ik in id_keys:
                if ik in row and row.get(ik) is not None:
                    try:
                        return int(row.get(ik))
                    except Exception:
                        pass
    return None


def _pick_id_1_if_available(rows: List[Dict[str, Any]]) -> Optional[int]:
    """
    If any row has ID == 1, return 1, else return first available ID.
    """
    ids: List[int] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k in ("ID", "Id", "id"):
            if k in row and row.get(k) is not None:
                try:
                    ids.append(int(row.get(k)))
                except Exception:
                    pass
                break
    if not ids:
        return None
    if 1 in ids:
        return 1
    return ids[0]


def _pick_middle_id(rows: List[Dict[str, Any]]) -> Optional[int]:
    """
    Pick the "middle" ID (by sorted numeric ID).
    """
    ids: List[int] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k in ("ID", "Id", "id"):
            if k in row and row.get(k) is not None:
                try:
                    ids.append(int(row.get(k)))
                except Exception:
                    pass
                break
    ids = sorted(set(ids))
    if not ids:
        return None
    return ids[len(ids) // 2]


def main() -> None:
    # -----------------------------------------------------------------
    # USER PARAMETERS (edit these)
    # -----------------------------------------------------------------
    CONFIG_PATH = "./config/sandbox.config.ini"

    # You MUST set this to your Ticketing App ID in TeamDynamix
    TICKETING_APP_ID = 0  # <-- CHANGE ME

    # Ticket "base" parameters (IDs will be selected dynamically in the script)
    TEST_TICKET_PARAMS: Dict[str, Any] = {
        "Title": "API Test Ticket (teamdynamix-api)",
        # Description will be appended with a unique string below
        "Description": "Created by automated endpoint test.",
        # Depending on your TDX configuration, you may need additional fields.
        # Add them here if create() fails with validation errors.
        # Example possibilities (varies by org):
        # "RequestorUid": "<some-guid>",
        # "AccountID": 0,
        # "CategoryID": 0,
    }

    # -----------------------------------------------------------------
    # 0) Generate unique string for Description
    # -----------------------------------------------------------------
    unique = f"TDX_API_TEST_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    print(f"[0] Unique search token: {unique}")

    # -----------------------------------------------------------------
    # Init session + clients
    # -----------------------------------------------------------------
    session = Session(CONFIG_PATH)

    # Optional: deterministic testing (force auth early)
    session.authenticate()

    tickets = Tickets(session, ticketing_app_id=TICKETING_APP_ID)
    priorities_client = TicketPriorities(session, ticketing_app_id=TICKETING_APP_ID)
    statuses_client = TicketStatuses(session, ticketing_app_id=TICKETING_APP_ID)
    sources_client = TicketSources(session, ticketing_app_id=TICKETING_APP_ID)
    types_client = TicketTypes(session, ticketing_app_id=TICKETING_APP_ID)

    # -----------------------------------------------------------------
    # 1) Get TicketPriorities via list()
    # -----------------------------------------------------------------
    priorities = priorities_client.list()
    print(f"[1] Priorities count: {len(priorities)}")

    # -----------------------------------------------------------------
    # 2) Get TicketStatuses via list()
    # -----------------------------------------------------------------
    statuses = statuses_client.list(is_active=True)
    print(f"[2] Statuses (active) count: {len(statuses)}")

    # -----------------------------------------------------------------
    # 3) Get TicketSources via list()
    # -----------------------------------------------------------------
    sources = sources_client.list(is_active=True)
    print(f"[3] Sources (active) count: {len(sources)}")

    # -----------------------------------------------------------------
    # 4) Get TicketTypes via list()
    # -----------------------------------------------------------------
    types = types_client.list(is_active=True)
    print(f"[4] Types (active) count: {len(types)}")

    # -----------------------------------------------------------------
    # 5) Create ticket with selected IDs
    # -----------------------------------------------------------------
    type_id = _pick_id_1_if_available(types)
    status_new_id = _pick_by_name(statuses, "New")
    status_cancelled_id = _pick_by_name(statuses, "Cancelled")
    source_api_id = _pick_by_name(sources, "API")
    priority_middle_id = _pick_middle_id(priorities)

    missing = []
    if type_id is None:
        missing.append("TypeID (no types returned)")
    if status_new_id is None:
        missing.append("StatusID for 'New' (no match)")
    if status_cancelled_id is None:
        missing.append("StatusID for 'Cancelled' (no match)")
    if source_api_id is None:
        missing.append("SourceID for 'API' (no match)")
    if priority_middle_id is None:
        missing.append("PriorityID (no priorities returned)")

    if missing:
        print("[5] Cannot proceed; missing required IDs:")
        for m in missing:
            print(f"    - {m}")
        return

    ticket_payload = dict(TEST_TICKET_PARAMS)
    ticket_payload["Description"] = f"{ticket_payload.get('Description', '')}\n\n{unique}"
    ticket_payload["TypeID"] = type_id
    ticket_payload["StatusID"] = status_new_id
    ticket_payload["SourceID"] = source_api_id
    ticket_payload["PriorityID"] = priority_middle_id

    print(f"[5] Creating ticket with IDs: TypeID={type_id}, StatusID(New)={status_new_id}, "
          f"SourceID(API)={source_api_id}, PriorityID(mid)={priority_middle_id}")

    created = tickets.create(ticket_payload)

    if not created.ID:
        print("[5] Ticket create returned no ID; cannot proceed.")
        return

    ticket_id = int(created.ID)
    print(f"[5] Created ticket ID: {ticket_id}")

    # -----------------------------------------------------------------
    # 6) Search tickets by SearchText = unique token
    # -----------------------------------------------------------------
    search_payload = {"SearchText": unique}
    print(f"[6] Searching tickets with payload: {search_payload}")
    search_results = tickets.search(search_payload)
    print(f"[6] Search results count: {len(search_results)}")

    if not search_results:
        print("[6] No search results found; cannot proceed.")
        return

    # Prefer the created ticket if it appears in results; else use the first result
    found_id = None
    for t in search_results:
        if t.ID == ticket_id:
            found_id = ticket_id
            break
    if found_id is None:
        found_id = int(search_results[0].ID) if search_results[0].ID else None

    if found_id is None:
        print("[6] Search returned tickets but none had an ID; cannot proceed.")
        return

    print(f"[6] Using ticket ID from search: {found_id}")

    # -----------------------------------------------------------------
    # 7) Get full ticket using Tickets.get()
    # -----------------------------------------------------------------
    got = tickets.get(found_id)
    if got is None or not got.ID:
        print(f"[7] Tickets.get failed for ID={found_id}")
        return
    print(f"[7] Got ticket: ID={got.ID}, Title={got.Title!r}, StatusID={got.StatusID}, TypeID={got.TypeID}")

    # -----------------------------------------------------------------
    # 8) Add a feed entry
    # -----------------------------------------------------------------
    feed_payload = {"Body": "Ticket feed test via API."}
    print(f"[8] Adding feed entry: {feed_payload}")
    tickets.add_feed_entry(found_id, feed_payload)
    print("[8] Feed entry added.")

    # -----------------------------------------------------------------
    # 9) Update the ticket: set StatusID -> 'Cancelled'
    # -----------------------------------------------------------------
    print(f"[9] Updating ticket StatusID -> Cancelled ({status_cancelled_id})")
    tickets.update(found_id, {"StatusID": status_cancelled_id})
    print("[9] Ticket updated to Cancelled.")

    # Optional: verify status changed
    verify = tickets.get(found_id)
    if verify is not None:
        print(f"[9] Verify status: StatusID={verify.StatusID}, StatusName={verify.StatusName}")

    print("Done.")


if __name__ == "__main__":
    main()
