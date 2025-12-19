# `Tickets` Module

**Module:** `teamdynamix.tickets`
**Python Import Path:** `teamdynamix.tickets`
**API Surface:** `/api/{ticketingAppId}/tickets/*`
**Primary Client Class:** `Tickets`
**DTOs:** `Ticket`

The `tickets` module provides a thin, endpoint-representative client for working with **TeamDynamix Tickets** within a specific ticketing application.

It intentionally models only a **minimal, commonly useful subset** of ticket fields while preserving access to raw payloads for feeds, metadata, and tenant-specific extensions.

------

## Architectural Notes

This module follows the core architectural guarantees of `teamdynamix-api`:

- All HTTP requests flow through `Session → Transport`
- Clients are scoped to a specific **ticketing app**
- Empty responses are valid and expected in multiple endpoints
- Typed DTOs are intentionally minimal
- JSON Patch is supported for updates without over-modeling

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.tickets import Tickets

session = Session("./config/config.ini")

# ticketing_app_id is required
tickets = Tickets(session, ticketing_app_id=123)
```

No network calls occur during construction.

------

## Data Models (DTOs)

### `Ticket`

A minimal typed representation of a TeamDynamix Ticket.

#### Fields

| Field                | Type         | Description            |
| -------------------- | ------------ | ---------------------- |
| `ID`                 | `int | None` | Ticket identifier      |
| `Title`              | `str | None` | Ticket title           |
| `Description`        | `str | None` | Ticket description     |
| `StatusID`           | `int | None` | Status identifier      |
| `StatusName`         | `str | None` | Status name            |
| `TypeID`             | `int | None` | Ticket type identifier |
| `TypeName`           | `str | None` | Ticket type name       |
| `PriorityID`         | `int | None` | Priority identifier    |
| `PriorityName`       | `str | None` | Priority name          |
| `RequestorUid`       | `str | None` | Requestor UID          |
| `ResponsibleUid`     | `str | None` | Responsible user UID   |
| `ResponsibleGroupID` | `int | None` | Responsible group ID   |

#### Notes

- ID normalization accepts `ID`, `Id`, or `id`
- UID normalization accepts both `Uid` and `UID` variants
- This DTO intentionally does **not** model the full ticket schema

------

## Metadata Clients

These helper clients expose **ticket metadata** scoped to a ticketing app.

### `TicketPriorities`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/priorities`

```python
from teamdynamix.tickets import TicketPriorities

priorities = TicketPriorities(session, 123).list()
```

Returns a list of raw dictionaries.

------

### `TicketTypes`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/types?isActive=`

```python
from teamdynamix.tickets import TicketTypes

types = TicketTypes(session, 123).list(is_active=True)
```

------

### `TicketStatuses`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/statuses?isActive=`

```python
from teamdynamix.tickets import TicketStatuses

statuses = TicketStatuses(session, 123).list(is_active=True)
```

------

### `TicketSources`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/sources?isActive=`

```python
from teamdynamix.tickets import TicketSources

sources = TicketSources(session, 123).list()
```

------

## Client Class

### `Tickets`

```python
class Tickets:
    ...
```

The `Tickets` client maps directly to the common TeamDynamix ticket endpoints for a specific ticketing application.

------

## Methods

### Core Ticket Operations

#### `get(ticket_id)`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/{id}`
**Returns:** `Ticket \| None`

```python
ticket = tickets.get(456)
if ticket:
    print(ticket.Title, ticket.StatusName)
```

**Behavior notes**

- Returns `None` when the API response is empty
- If the API returns a list, the first item is used

------

#### `create(ticket_payload)`

**Endpoint:** `POST /api/{ticketingAppId}/tickets`
**Returns:** `Ticket`

```python
created = tickets.create({
    "Title": "Printer not working",
    "Description": "The printer on floor 2 is jammed.",
})
```

**Behavior notes**

- Payload is passed through unchanged
- If response shape is unexpected, an empty dict is coerced before DTO creation

------

#### `search(search_payload)`

**Endpoint:** `POST /api/{ticketingAppId}/tickets/search`
**Returns:** `list[Ticket]`

```python
results = tickets.search({
    "SearchText": "printer",
    "MaxResults": 10,
})
```

**Behavior notes**

- Returns `[]` when no results are found (valid)
- Filters non-dict list entries defensively

------

#### `update(ticket_id, ops, *, notify_new_responsible=None)`

**Endpoint:**
`PATCH /api/{ticketingAppId}/tickets/{id}?notifyNewResponsible=`

**Returns:** `bool`

```python
from teamdynamix.transport import PatchPayload

tickets.update(
    456,
    {"StatusID": 3},
    notify_new_responsible=True,
)

tickets.update(
    456,
    [
        PatchPayload.replace("/Title", "Updated title"),
    ],
)
```

**Accepted update forms**

- `dict[str, Any]`
  → converted by `Transport` into JSON Patch `"replace"` operations
- `list[PatchPayload]`
- `list[dict]` (assumed RFC-6902 compliant)

**Behavior notes**

- Mixed operation lists are normalized defensively
- Returns `True` on success
- Invalid payload shapes may raise `TypeError`

------

### Ticket Feed Operations

#### `get_feed(ticket_id)`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/{id}/feed`
**Returns:** `list[dict]`

```python
feed = tickets.get_feed(456)
```

Returns `[]` when empty (valid).

------

#### `add_feed_entry(ticket_id, feed_payload)`

**Endpoint:** `POST /api/{ticketingAppId}/tickets/{id}/feed`
**Returns:** `bool`

```python
tickets.add_feed_entry(
    456,
    {"Body": "Investigating the issue."},
)
```

Returns `True` on success.

------

## Raw vs Typed Methods

This module uses a **mixed approach**:

- Core ticket operations return typed `Ticket` DTOs
- Metadata endpoints return raw dictionaries
- Feed endpoints return raw dictionaries
- Updates accept both typed patch payloads and simple dicts

This balances usability with tenant-specific flexibility.

------

## Error Handling

- HTTP and transport errors are raised by `Transport`
- Empty responses are treated as valid outcomes
- Invalid patch payloads may raise `TypeError`

```python
from teamdynamix.exceptions import HttpError

try:
    tickets.get(999999)
except HttpError as exc:
    print("HTTP error:", exc.status_code)
```

------

## Design Intent

This module intentionally does **not**:

- Model the full ticket schema
- Enforce validation on ticket payloads
- Provide workflow abstractions
- Automatically resolve metadata IDs

It exists to provide **predictable, endpoint-aligned access** to TeamDynamix ticket operations while remaining flexible for scripting and automation.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`
- TeamDynamix API Documentation — Tickets