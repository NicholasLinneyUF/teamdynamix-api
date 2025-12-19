# `People` Module

**Module:** `teamdynamix.people`
**Python Import Path:** `teamdynamix.people`
**API Surface:** `/api/people/*`
**Primary Client Class:** `People`
**DTOs:** `Person`

The `people` module provides a minimal client and DTO for working with **TeamDynamix People** records.

It intentionally models only a **commonly-used subset** of the full People payload. The People record returned by TeamDynamix can be large and nested; this module provides `get_raw(...)` as the escape hatch when full fidelity is required.

------

## Architectural Notes

This module follows all core architectural guarantees of the `teamdynamix-api` library:

- All HTTP requests flow through `Session → Transport`
- Client modules do not manage authentication or headers
- Empty responses (`[]`, `{}`, `null`) are valid and expected where applicable
- Prefer endpoint-representative methods; avoid non-endpoint “helper” methods
- Typed models are **selective views**, not complete schemas

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.people import People

session = Session("./config/config.ini")
people = People(session)
```

No network calls occur during construction.

------

## Data Models (DTOs)

### `Person`

A minimal, commonly-used subset of a TeamDynamix Person record.

This DTO intentionally does **not** model the full `GET /api/people/{uid}` payload (which may be large and nested). Use `People.get_raw(...)` when you need the full dict payload.

#### Fields

| Field                | Type          | Description                                                  |
| -------------------- | ------------- | ------------------------------------------------------------ |
| `UID`                | `str | None`  | Person UID (may appear as `UID` / `Id` / `id` depending on endpoint shape) |
| `ReferenceID`        | `int | None`  | Reference ID (if returned)                                   |
| `BEID`               | `str | None`  | BEID identifier (if returned)                                |
| `IsActive`           | `bool | None` | Active status                                                |
| `IsEmployee`         | `bool | None` | Employee status                                              |
| `UserName`           | `str | None`  | Username/login name                                          |
| `FullName`           | `str | None`  | Full name                                                    |
| `FirstName`          | `str | None`  | First name                                                   |
| `LastName`           | `str | None`  | Last name                                                    |
| `PrimaryEmail`       | `str | None`  | Primary email address                                        |
| `SecurityRoleName`   | `str | None`  | Security role name (if returned)                             |
| `DefaultAccountID`   | `int | None`  | Default account ID (if returned)                             |
| `DefaultAccountName` | `str | None`  | Default account name (if returned)                           |

#### Notes

- This DTO is intended to be stable and useful across multiple People endpoints.
- Field values are taken directly from response payloads; no normalization is performed beyond UID key selection.

------

## Client Class

### `People`

```python
class People:
    ...
```

The `People` client maps directly to the implemented TeamDynamix People endpoints, including:

- Core person endpoints (`get`, `search`, `user_list`, `create`, `update`)
- Functional role membership endpoints scoped under a person

------

## Methods

### `get_raw(uid)`

**Endpoint:** `GET /api/people/{uid}`
**Returns:** `dict \| None`

Retrieve a person record by UID, returning the **raw dict payload**.

This method is the escape hatch for large or nested person payloads.

```python
raw = people.get_raw("00000000-0000-0000-0000-000000000000")

if raw is None:
    print("Not found")
else:
    print(raw.get("FullName"))
```

**Parameters**

| Name  | Type         | Description |
| ----- | ------------ | ----------- |
| `uid` | `str | UUID` | Person UID  |

**Behavior notes**

- Returns `None` when the API response is empty/`null`
- If the API returns a list, the first item is used (if it is a dict)

------

### `get(uid)`

**Endpoint:** `GET /api/people/{uid}`
**Returns:** `Person \| None`

Typed wrapper around `get_raw(...)`.

```python
p = people.get("00000000-0000-0000-0000-000000000000")
if p:
    print(p.FullName, p.PrimaryEmail)
```

------

### `search(search_text, *, max_results=None, is_active=None, is_employee=None, is_client=None, has_login=None)`

**Endpoint:** `POST /api/people/search`
**Returns:** `list[Person]`

Search for people using a search text string and optional filters.

```python
results = people.search(
    "linney",
    max_results=25,
    is_active=True,
    has_login=True,
)

for p in results:
    print(p.UID, p.FullName)
```

**Parameters**

| Name          | Type          | Description                    |
| ------------- | ------------- | ------------------------------ |
| `search_text` | `str`         | Search string                  |
| `max_results` | `int | None`  | Optional maximum results       |
| `is_active`   | `bool | None` | Optional active filter         |
| `is_employee` | `bool | None` | Optional employee filter       |
| `is_client`   | `bool | None` | Optional client filter         |
| `has_login`   | `bool | None` | Optional login presence filter |

**Behavior notes**

- Only includes optional fields in the request payload when explicitly provided
- Returns `[]` when no matches are found (valid)

------

### `user_list(is_active=True)`

**Endpoint:** `GET /api/people/userlist?isActive=true|false`
**Returns:** `list[Person]`

Retrieve the user list, optionally filtered by active status.

```python
active_users = people.user_list(is_active=True)
```

**Parameters**

| Name        | Type   | Description                     |
| ----------- | ------ | ------------------------------- |
| `is_active` | `bool` | Active filter (default: `True`) |

**Behavior notes**

- `isActive` is passed as a lowercase string (`"true"` / `"false"`)
- Returns `[]` when no results are returned (valid)

------

### `create(person_payload)`

**Endpoint:** `POST /api/people`
**Returns:** `Person`

Create a new person record.

```python
created = people.create({
    "FirstName": "Ada",
    "LastName": "Lovelace",
    "PrimaryEmail": "ada@example.com",
    "IsActive": True,
})

print(created.UID, created.FullName)
```

**Parameters**

| Name             | Type   | Description                      |
| ---------------- | ------ | -------------------------------- |
| `person_payload` | `dict` | Raw request body sent to the API |

**Behavior notes**

- Payload is accepted as a dict to avoid prematurely modeling the full person schema
- Raises `ValueError` if the API response is not a JSON object (`dict`)

------

### `update(uid, updates)`

**Endpoint:** `PATCH /api/people/{uid}`
**Returns:** `bool`

Apply partial updates to a person record.

```python
ok = people.update(
    uid="00000000-0000-0000-0000-000000000000",
    updates={"IsActive": False},
)
```

**Parameters**

| Name      | Type         | Description          |
| --------- | ------------ | -------------------- |
| `uid`     | `str | UUID` | Person UID           |
| `updates` | `dict`       | Patch payload (dict) |

**Behavior notes**

- Returns `True` if the request succeeds
- HTTP errors raise exceptions from `Transport`

------

### `list_functional_roles(uid)`

**Endpoint:** `GET /api/people/{uid}/functionalroles`
**Returns:** `list[dict]`

List functional roles assigned to a person.

```python
roles = people.list_functional_roles("00000000-0000-0000-0000-000000000000")
for r in roles:
    print(r.get("ID"), r.get("Name"))
```

**Behavior notes**

- Returns `[]` when none are assigned (valid)
- Returns raw dicts because the role-assignment shape is not modeled here

------

### `add_functional_role(uid, role_id, is_primary=False)`

**Endpoint:** `PUT /api/people/{uid}/functionalroles/{role_id}?isPrimary=true|false`
**Returns:** `bool`

Assign a functional role to a person.

```python
people.add_functional_role(
    uid="00000000-0000-0000-0000-000000000000",
    role_id=123,
    is_primary=True,
)
```

**Parameters**

| Name         | Type         | Description             |
| ------------ | ------------ | ----------------------- |
| `uid`        | `str | UUID` | Person UID              |
| `role_id`    | `int`        | Functional role ID      |
| `is_primary` | `bool`       | Primary assignment flag |

**Behavior notes**

- `isPrimary` is passed as a lowercase string (`"true"` / `"false"`)
- Returns `True` if the request succeeds

------

### `remove_functional_role(uid, role_id)`

**Endpoint:** `DELETE /api/people/{uid}/functionalroles/{role_id}`
**Returns:** `bool`

Remove a functional role from a person.

```python
people.remove_functional_role(
    uid="00000000-0000-0000-0000-000000000000",
    role_id=123,
)
```

**Behavior notes**

- Returns `True` if the request succeeds

------

## Raw vs Typed Methods

This module uses both raw and typed methods:

- `get_raw(...)` returns `dict | None` for full-fidelity payloads
- `get(...)` returns `Person | None` for convenience
- `search(...)` and `user_list(...)` return `list[Person]`
- Functional role methods return raw dicts or booleans

Example:

```python
raw = people.get_raw(uid)
typed = people.get(uid)
```

Use raw methods when you need nested structures not modeled by `Person`.

------

## Error Handling

- HTTP and transport errors are raised by `Transport` (e.g., `HttpError`, `TdxTimeoutError`, `TdxRequestError`)
- Empty responses are treated as valid:
  - `get/get_raw` return `None`
  - list-returning methods return `[]`
- `create(...)` raises `ValueError` if response shape is not a dict

```python
from teamdynamix.exceptions import HttpError, TdxError

try:
    person = people.get("00000000-0000-0000-0000-000000000000")
except HttpError as exc:
    print("HTTP failed:", exc.status_code, exc.url)
except TdxError as exc:
    print("SDK error:", exc)
```

------

## Design Intent

This module intentionally does **not**:

- Model the full nested People schema as DTOs
- Validate person payloads for create/update
- Provide caching or pagination helpers
- Provide non-endpoint “lookup helpers” beyond what is implemented

It exists to provide predictable access to the implemented People API surface while remaining flexible for tenant-specific person payload shapes.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`
- TeamDynamix API Documentation — People