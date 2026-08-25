# `Groups` Module

**Module:** `teamdynamix.groups`
**Python Import Path:** `teamdynamix.groups`
**API Surface:** `/api/groups/*`
**Primary Client Class:** `Groups`
**DTOs:** `Group`

The `groups` module provides a minimal client and DTO for interacting with **TeamDynamix Groups**.

It exposes endpoint-representative methods for retrieving, searching, and listing groups, while intentionally keeping the data model small. When full payload fidelity is required, raw methods are available.

------

## Architectural Notes

This module follows all core architectural guarantees of the `teamdynamix-api` library:

- All HTTP requests flow through `Session → Transport`
- Client modules do not manage authentication or headers
- Empty responses (`[]`, `{}`, `null`) are valid and expected
- Typed models are **selective views**, not complete schemas
- Helper logic is limited to response-shape normalization

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.groups import Groups

session = Session("./config/config.ini")
groups = Groups(session)
```

No network calls occur during construction.

------

## Data Models (DTOs)

### `Group`

A minimal typed representation of a TeamDynamix Group.

#### Fields

| Field         | Type          | Description       |
| ------------- | ------------- | ----------------- |
| `ID`          | `int | None`  | Group identifier  |
| `Name`        | `str | None`  | Group name        |
| `Description` | `str | None`  | Group description |
| `IsActive`    | `bool | None` | Active status     |

#### Notes

- ID normalization accepts `ID`, `Id`, or `id`
- This DTO intentionally models only commonly used fields
- Use raw methods when additional fields are required

------

## Client Class

### `Groups`

```python
class Groups:
    ...
```

The `Groups` client provides access to the following TeamDynamix endpoints:

- `GET /api/groups/{id}`
- `POST /api/groups/search`
- `GET /api/groups`

------

## Methods

### `get_raw(group_id)`

**Endpoint:** `GET /api/groups/{id}`
**Returns:** `dict \| None`

Retrieve a group by ID, returning the raw payload.

```python
raw = groups.get_raw(123)
if raw:
    print(raw.get("Name"))
```

**Behavior notes**

- Returns `None` when the API response is empty or `null`
- If the API returns a list, the first dict element is used

------

### `get(group_id)`

**Endpoint:** `GET /api/groups/{id}`
**Returns:** `Group \| None`

Typed wrapper around `get_raw(...)`.

```python
group = groups.get(123)
if group:
    print(group.Name, group.IsActive)
```

------

### `search_raw(search_payload)`

**Endpoint:** `POST /api/groups/search`
**Returns:** `list[dict]`

Search for groups using a raw TeamDynamix search payload.

```python
raw_results = groups.search_raw({
    "Name": "IT",
    "IsActive": True,
})
```

**Behavior notes**

- Returns `[]` when no matches are found (valid)
- Non-dict list items are ignored

------

### `search(search_payload)`

**Endpoint:** `POST /api/groups/search`
**Returns:** `list[Group]`

Typed wrapper around `search_raw(...)`.

```python
results = groups.search({"Name": "IT"})
for g in results:
    print(g.ID, g.Name)
```

------

### `list_all_raw(is_active=None)`

**Endpoint:** `GET /api/groups`
**Returns:** `list[dict]`

Retrieve all groups, optionally filtered by active status.

```python
raw_groups = groups.list_all_raw(is_active=True)
```

**Parameters**

| Name        | Type          | Description            |
| ----------- | ------------- | ---------------------- |
| `is_active` | `bool | None` | Optional active filter |

**Behavior notes**

- `isActive` is passed as a lowercase string (`"true"` / `"false"`)
- Unsupported query parameters are ignored by some tenants
- Returns `[]` when no groups exist

------

### `list_all(is_active=None)`

**Endpoint:** `GET /api/groups`
**Returns:** `list[Group]`

Typed wrapper around `list_all_raw(...)`.

```python
active_groups = groups.list_all(is_active=True)
```

------

## Raw vs Typed Methods

This module provides both raw and typed access patterns:

| Method         | Returns        |
| -------------- | -------------- |
| `get_raw`      | `dict | None`  |
| `get`          | `Group | None` |
| `search_raw`   | `list[dict]`   |
| `search`       | `list[Group]`  |
| `list_all_raw` | `list[dict]`   |
| `list_all`     | `list[Group]`  |

Example:

```python
raw = groups.list_all_raw()
typed = groups.list_all()
```

Use raw methods when you need fields not exposed by the `Group` DTO.

------

## Error Handling

- HTTP and transport errors are raised by `Transport`
- Empty responses are valid and do not raise exceptions
- No additional error wrapping is performed

```python
from teamdynamix.exceptions import HttpError

try:
    groups.get(999999)
except HttpError as exc:
    print("Request failed:", exc.status_code)
```

------

## Design Intent

This module intentionally does **not**:

- Model the full Group schema
- Add pagination or caching helpers
- Validate search payloads
- Add non-endpoint convenience methods

It exists to provide **predictable, endpoint-aligned access** to TeamDynamix Groups.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`
- TeamDynamix API Documentation — Groups