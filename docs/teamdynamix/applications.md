# `Applications` Module

**Module:** `teamdynamix.applications`
**API Surface:** `/api/applications/*`
**Primary Class:** `Applications`
**DTO:** `Application`

The `Applications` module provides access to **TeamDynamix Application metadata**.

Applications represent logical TeamDynamix systems (e.g., Ticketing, Asset Management, Projects) and are commonly used when interacting with application-scoped endpoints.

This module is intentionally minimal and mirrors the TeamDynamix Web API directly.

------

## Architectural Notes

This module adheres to all core architectural rules of the library:

- All HTTP requests flow through `Session → Transport`
- No direct use of `requests`
- Authentication is lazy
- Empty responses are valid outcomes
- Typed models are selective views, not complete schemas

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.applications import Applications

session = Session("./config/config.ini")
applications = Applications(session)
```

No network calls occur during construction.

------

## Data Model: `Application`

### `Application` (dataclass)

A minimal typed representation of a TeamDynamix Application.

#### Fields

| Field         | Type          | Description                       |
| ------------- | ------------- | --------------------------------- |
| `ID`          | `int | None`  | Application identifier            |
| `Name`        | `str | None`  | Application name                  |
| `Description` | `str | None`  | Application description           |
| `SystemClass` | `str | None`  | Application system class          |
| `IsActive`    | `bool | None` | Whether the application is active |
| `IsDefault`   | `bool | None` | Whether this is the default app   |

#### Notes

- This model intentionally omits many rarely-used fields.
- Use raw methods for full payload access.

------

## Client Class: `Applications`

```python
class Applications:
    ...
```

The `Applications` client provides access to application metadata endpoints exposed by TeamDynamix.

------

## Methods

### `list_raw(is_active=None)`

**Endpoint:** `GET /api/applications`
**Returns:** `list[dict]`

Retrieve all applications as raw dictionaries.

```python
raw_apps = applications.list_raw()
```

#### Parameters

| Name        | Type          | Description            |
| ----------- | ------------- | ---------------------- |
| `is_active` | `bool | None` | Optional active filter |

#### Behavior

- Returns an empty list (`[]`) if no applications exist
- Query parameters unsupported by a tenant are ignored by TeamDynamix

------

### `list(is_active=None)`

**Endpoint:** `GET /api/applications`
**Returns:** `list[Application]`

Retrieve all applications as typed `Application` objects.

```python
apps = applications.list(is_active=True)

for app in apps:
    print(app.ID, app.Name)
```

------

### `get_raw(app_id)`

**Endpoint:** `GET /api/applications/{id}`
**Returns:** `dict | None`

Retrieve a single application by ID, returning the raw API response.

```python
raw = applications.get_raw(5)
```

#### Notes

- Not all TeamDynamix tenants support this endpoint
- If unsupported, an HTTP error will be raised
- If supported but empty, returns `None`

------

### `get(app_id)`

**Endpoint:** `GET /api/applications/{id}`
**Returns:** `Application | None`

Retrieve a single application by ID as a typed `Application`.

```python
app = applications.get(5)

if app:
    print(app.Name)
```

------

## Raw vs Typed Methods

| Method Type | Returns               | When to Use             |
| ----------- | --------------------- | ----------------------- |
| Raw         | `dict` / `list[dict]` | Full payload access     |
| Typed       | DTOs                  | Convenience and clarity |

Example:

```python
apps_raw = applications.list_raw()
apps_typed = applications.list()
```

------

## Error Handling

- HTTP-level errors are raised by `Transport`
- Empty responses are valid and not treated as errors
- Client methods do not catch or suppress exceptions

------

## Design Intent

The `Applications` module intentionally avoids:

- Caching
- Pagination helpers
- Mutation endpoints
- Application-scoped convenience logic

It exists solely to reflect the TeamDynamix application metadata API.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- TeamDynamix API Documentation — Applications