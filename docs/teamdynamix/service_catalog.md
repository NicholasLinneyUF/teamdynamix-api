# `Service Catalog` Module

**Module:** `teamdynamix.service_catalog`
**Python Import Path:** `teamdynamix.service_catalog`
**API Surface:** `/api/{portalAppId}/services/*`
**Primary Client Class:** `ServiceCatalog`
**DTOs:** `Service`

The `service_catalog` module provides a thin client for interacting with **TeamDynamix Service Catalog** endpoints within a specific portal application.

Service Catalog payload shapes vary widely by tenant configuration. For this reason, the SDK exposes both raw and typed methods, keeping the typed model intentionally minimal.

------

## Architectural Notes

This module follows the core architectural guarantees of `teamdynamix-api`:

- All HTTP requests flow through `Session → Transport`
- Client methods are endpoint-representative
- Typed DTOs model only commonly used fields
- Raw dict access is preserved for full payload fidelity
- Empty list responses are valid and expected

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.service_catalog import ServiceCatalog

session = Session("./config/config.ini")

# portal_app_id is required for Service Catalog operations
catalog = ServiceCatalog(session, portal_app_id=123)
```

No network calls occur during construction.

------

## Data Models (DTOs)

### `Service`

A minimal typed representation of a Service Catalog item.

#### Fields

| Field         | Type          | Description         |
| ------------- | ------------- | ------------------- |
| `ID`          | `int | None`  | Service identifier  |
| `Name`        | `str | None`  | Service name        |
| `Description` | `str | None`  | Service description |
| `IsActive`    | `bool | None` | Active status       |

#### Notes

- ID normalization accepts `ID`, `Id`, or `id`
- This DTO intentionally does **not** model tenant-specific catalog fields
- Use raw methods to access extended catalog metadata

------

## Client Class

### `ServiceCatalog`

```python
class ServiceCatalog:
    ...
```

The `ServiceCatalog` client maps directly to the following endpoints:

- `GET /api/{portalAppId}/services`
- `POST /api/{portalAppId}/services`
- `GET /api/{portalAppId}/services/{id}`
- `PUT /api/{portalAppId}/services/{id}`
- `DELETE /api/{portalAppId}/services/{id}`

------

## Methods

### List Services

#### `list_raw()`

**Endpoint:** `GET /api/{portalAppId}/services`
**Returns:** `list[dict]`

Retrieve all services as raw dictionaries.

```python
raw_services = catalog.list_raw()
```

**Behavior notes**

- Returns `[]` when no services exist (valid)
- Filters out non-dict entries defensively

------

#### `list()`

**Endpoint:** `GET /api/{portalAppId}/services`
**Returns:** `list[Service]`

Typed wrapper around `list_raw(...)`.

```python
services = catalog.list()
for s in services:
    print(s.ID, s.Name)
```

------

### Get Service

#### `get_raw(service_id)`

**Endpoint:** `GET /api/{portalAppId}/services/{id}`
**Returns:** `dict`

Retrieve a single service as a raw dictionary.

```python
raw = catalog.get_raw(456)
print(raw.get("Name"))
```

**Behavior notes**

- Raises `ValueError` if the response is not a JSON object

------

#### `get(service_id)`

**Endpoint:** `GET /api/{portalAppId}/services/{id}`
**Returns:** `Service`

Typed wrapper around `get_raw(...)`.

```python
service = catalog.get(456)
print(service.Name, service.IsActive)
```

------

### Create Service

#### `create_raw(payload)`

**Endpoint:** `POST /api/{portalAppId}/services`
**Returns:** `dict`

Create a new service using a raw payload.

```python
raw = catalog.create_raw({
    "Name": "New Service",
    "IsActive": True,
})
```

**Behavior notes**

- Payload is passed through unchanged
- Raises `ValueError` on unexpected response shape

------

#### `create(payload)`

**Endpoint:** `POST /api/{portalAppId}/services`
**Returns:** `Service`

Typed wrapper around `create_raw(...)`.

```python
service = catalog.create({
    "Name": "New Service",
    "Description": "Service description",
})
```

------

### Update Service

#### `update_raw(service_id, payload)`

**Endpoint:** `PUT /api/{portalAppId}/services/{id}`
**Returns:** `dict`

Update an existing service using a raw payload.

```python
raw = catalog.update_raw(
    456,
    {"Description": "Updated description"},
)
```

**Behavior notes**

- Raises `ValueError` on unexpected response shape

------

#### `update(service_id, payload)`

**Endpoint:** `PUT /api/{portalAppId}/services/{id}`
**Returns:** `Service`

Typed wrapper around `update_raw(...)`.

```python
service = catalog.update(
    456,
    {"IsActive": False},
)
```

------

### Delete Service

#### `delete(service_id)`

**Endpoint:** `DELETE /api/{portalAppId}/services/{id}`
**Returns:** `bool`

Delete a service.

```python
catalog.delete(456)
```

**Behavior notes**

- Returns `True` if the request succeeds
- HTTP/transport failures raise exceptions

------

## Raw vs Typed Methods

This module explicitly supports both patterns:

| Method       | Returns         |
| ------------ | --------------- |
| `list_raw`   | `list[dict]`    |
| `list`       | `list[Service]` |
| `get_raw`    | `dict`          |
| `get`        | `Service`       |
| `create_raw` | `dict`          |
| `create`     | `Service`       |
| `update_raw` | `dict`          |
| `update`     | `Service`       |
| `delete`     | `bool`          |

Use raw methods when you need tenant-specific or extended catalog fields.

------

## Error Handling

- HTTP and transport errors are raised by `Transport`
- Empty list responses are valid and return `[]`
- Unexpected response shapes raise `ValueError`

```python
from teamdynamix.exceptions import HttpError

try:
    catalog.get(999999)
except HttpError as exc:
    print("Request failed:", exc.status_code)
```

------

## Design Intent

This module intentionally does **not**:

- Model the full Service Catalog schema
- Validate service payload contents
- Provide pagination or caching helpers
- Abstract tenant-specific catalog behavior

It exists to provide **predictable, endpoint-aligned access** to TeamDynamix Service Catalog endpoints.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`
- TeamDynamix API Documentation — Service Catalog