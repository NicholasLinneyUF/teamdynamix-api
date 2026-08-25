# `Functional Roles` Module

**Module:** `teamdynamix.functional_roles`
**Python Import Path:** `teamdynamix.functional_roles`
**API Surface:** `/api/functionalroles/*`
**Primary Client Class:** `FunctionalRoles`
**DTOs:** `FunctionalRole`

The `functional_roles` module provides a minimal client and DTO for interacting with **TeamDynamix Functional Roles** via the confirmed vendor endpoints implemented in the SDK.

This module is endpoint-representative and intentionally avoids adding convenience endpoints beyond what’s implemented.

------

## Architectural Notes

This module follows all core architectural guarantees of the `teamdynamix-api` library:

- All HTTP requests flow through `Session → Transport`
- Client modules do not manage authentication or headers
- Empty responses (including `[]`) are treated as valid outcomes where applicable
- Typed models are **selective views**, not complete schemas

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.functional_roles import FunctionalRoles

session = Session("./config/config.ini")
roles = FunctionalRoles(session)
```

No network calls occur during construction.

------

## Data Models (DTOs)

### `FunctionalRole`

A minimal typed representation of a TeamDynamix Functional Role, based on fields observed in the Postman body examples.

#### Fields

| Field                | Type          | Description                      |
| -------------------- | ------------- | -------------------------------- |
| `ID`                 | `int | None`  | Functional role identifier       |
| `Name`               | `str | None`  | Role name                        |
| `CreatedDate`        | `str | None`  | Created timestamp                |
| `ModifiedDate`       | `str | None`  | Last modified timestamp          |
| `IsActive`           | `bool | None` | Active status                    |
| `NotifyOnAssignment` | `bool | None` | Whether to notify on assignment  |
| `RequiresApproval`   | `bool | None` | Whether approval is required     |
| `ManagerFullName`    | `str | None`  | Manager display name             |
| `ManagerUID`         | `str | None`  | Manager GUID (string)            |
| `ResourceCount`      | `int | None`  | Count of resources (if returned) |

#### Notes

- This DTO is intentionally minimal and reflects only fields observed/used by the SDK.
- For full vendor payload fidelity, you may prefer using raw response dicts in your scripts (this client currently returns typed DTOs directly).

------

## Client Class

### `FunctionalRoles`

```python
class FunctionalRoles:
    ...
```

The `FunctionalRoles` client provides access to the following API endpoints (as implemented):

- `POST /api/functionalroles` → `create()`
- `PUT /api/functionalroles/{id}` → `edit()`
- `POST /api/functionalroles/search` → `search()`

------

## Methods

### `create(payload)`

**Endpoint:** `POST /api/functionalroles`
**Returns:** `FunctionalRole`

Create a new functional role.

```python
created = roles.create({
    "Name": "On-Call Approver",
    "IsActive": True,
    "NotifyOnAssignment": True,
    "RequiresApproval": False,
    "ManagerFullName": "Jane Manager",
    "ManagerUID": "00000000-0000-0000-0000-000000000000",
})

print(created.ID, created.Name)
```

**Parameters**

| Name      | Type   | Description                      |
| --------- | ------ | -------------------------------- |
| `payload` | `dict` | Raw request body sent to the API |

**Behavior notes**

- Expects the API response to be a JSON object (`dict`). If the response is not a dict, the method raises `ValueError` (unexpected response shape).

------

### `edit(role_id, payload)`

**Endpoint:** `PUT /api/functionalroles/{id}`
**Returns:** `FunctionalRole`

Edit an existing functional role.

```python
updated = roles.edit(
    role_id=123,
    payload={
        "ID": 123,
        "Name": "On-Call Approver (Updated)",
        "IsActive": True,
        "NotifyOnAssignment": True,
        "RequiresApproval": True,
    },
)

print(updated.ID, updated.RequiresApproval)
```

**Parameters**

| Name      | Type   | Description                      |
| --------- | ------ | -------------------------------- |
| `role_id` | `int`  | Functional role ID               |
| `payload` | `dict` | Raw request body sent to the API |

**Behavior notes**

- Some tenants may require that the `ID` field be included in the body; the SDK does not force this, but you may include it in `payload` if needed.
- Expects the API response to be a JSON object (`dict`). If the response is not a dict, the method raises `ValueError`.

------

### `search(search_payload)`

**Endpoint:** `POST /api/functionalroles/search`
**Returns:** `list[FunctionalRole]`

Search for functional roles using a TeamDynamix search payload.

```python
results = roles.search({
    "Name": "Approver",
    "IsActive": True,
    "MaxResults": 50,
    "ReturnItemCounts": True,
})

for r in results:
    print(r.ID, r.Name, r.ResourceCount)
```

**Parameters**

| Name             | Type   | Description                     |
| ---------------- | ------ | ------------------------------- |
| `search_payload` | `dict` | Raw search body sent to the API |

**Behavior notes**

- `[]` is treated as a valid “no results” response.
- If the API returns a single object (`dict`) instead of a list, the client wraps it into a one-item list.
- Non-dict items in lists are ignored.

------

## Raw vs Typed Methods

This client currently returns **typed DTOs only** (it does not expose `*_raw` methods).

If you need full payload fidelity, you can:

- Inspect the DTO fields available (`FunctionalRole`)
- Or add corresponding `create_raw`, `edit_raw`, and `search_raw` methods later following the project’s raw/typed pattern

------

## Error Handling

- HTTP and transport errors are raised by `Transport` (e.g., `HttpError`, `TdxTimeoutError`, `TdxRequestError`)
- Unexpected response shapes (non-JSON-object for `create`/`edit`) raise `ValueError`
- Empty results from `search` are valid and return `[]`

```python
from teamdynamix.exceptions import HttpError, TdxError

try:
    roles.search({"MaxResults": 5})
except HttpError as exc:
    print("Request failed:", exc.status_code, exc.url)
except TdxError as exc:
    print("SDK error:", exc)
```

------

## Design Intent

This module intentionally does **not**:

- Add endpoints beyond what is confirmed and implemented (`create`, `edit`, `search`)
- Provide caching or pagination helpers
- Validate payload fields (payload is passed through as provided)
- Abstract Functional Roles into higher-level workflows

It exists to provide predictable access to the implemented Functional Roles API surface.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`
- TeamDynamix API Documentation — Functional Roles