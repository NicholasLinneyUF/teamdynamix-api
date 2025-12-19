# `Transport` Module

**Module:** `teamdynamix.transport`
**Python Import Path:** `teamdynamix.transport`
**API Surface:** *Internal (HTTP boundary)*
**Primary Client Class:** `Transport`
**DTOs:** `PatchPayload`

The `transport` module defines the **single HTTP boundary** for the SDK.

It is the only place that directly uses `requests`, and it centralizes cross-cutting request concerns:

- Applying default timeouts
- Translating `requests` exceptions into SDK exceptions
- Raising structured `HttpError` for non-success status codes
- Normalizing TeamDynamix `PATCH` request payloads to **RFC 6902 JSON Patch**

Client modules must not call `requests` directly; they call `Session.request(...)`, which delegates to `Transport.request(...)`.

------

## Architectural Notes

This module enforces critical architecture rules:

- **Single transport boundary:** only `Transport` touches `requests.*`
- **Centralized error translation:** timeouts and request errors become SDK exceptions
- **Centralized PATCH normalization:** if `PATCH` is used with a JSON dict body, the transport converts it into JSON Patch operations automatically
- **No client-specific logic:** transport stays generic and reusable across all clients

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

Most users do not instantiate `Transport` directly; it is created by `Session`.

For direct usage (tests or advanced control), you can construct it:

```python
from teamdynamix.logger import Logger
from teamdynamix.transport import Transport

logger = Logger(level="INFO", console=True)
transport = Transport(logger=logger, default_timeout=10)
```

------

## Data Models (DTOs)

### `PatchPayload`

Represents a single RFC 6902 JSON Patch operation.

#### Fields

| Field   | Type  | Description                                 |
| ------- | ----- | ------------------------------------------- |
| `op`    | `str` | JSON Patch operation (commonly `"replace"`) |
| `path`  | `str` | JSON pointer path (e.g., `"/FirstName"`)    |
| `value` | `Any` | Replacement value                           |

#### Example

```python
from teamdynamix.transport import PatchPayload

op = PatchPayload(op="replace", path="/Title", value="New Title")
payload = op.to_dict()
# {"op": "replace", "path": "/Title", "value": "New Title"}
```

------

## Client Class

### `Transport`

```python
class Transport:
    ...
```

The `Transport` class is responsible for making HTTP requests and enforcing consistent SDK behavior around:

- Timeouts
- Error handling
- PATCH payload normalization

------

## Methods

### `request(method, url, *, headers=None, params=None, json=None, data=None, timeout=None)`

Primary HTTP request method for the SDK.

**Returns:** `requests.Response`

```python
resp = transport.request(
    method="GET",
    url="https://example/TDWebApi/api/people/...",
    headers={"Authorization": "Bearer ..."},
)
data = resp.json()
```

**Parameters**

| Name      | Type          | Description                                      |
| --------- | ------------- | ------------------------------------------------ |
| `method`  | `str`         | HTTP method (e.g., `"GET"`, `"POST"`, `"PATCH"`) |
| `url`     | `str`         | Fully qualified request URL                      |
| `headers` | `dict | None` | Optional headers                                 |
| `params`  | `dict | None` | Optional query parameters                        |
| `json`    | `Any`         | JSON request body                                |
| `data`    | `Any`         | Raw request body                                 |
| `timeout` | `int | None`  | Per-request timeout override                     |

------

## PATCH Normalization (TeamDynamix JSON Patch)

TeamDynamix `PATCH` endpoints commonly expect **RFC 6902 JSON Patch** lists.

To make patching ergonomic and consistent, `Transport` applies normalization:

### Behavior

If:

- `method == "PATCH"` **and**
- `json` is a `dict`

Then:

- `Transport` converts the dict into a JSON Patch list of `"replace"` operations.

If:

- `method == "PATCH"` **and**
- `json` is already a `list`

Then:

- `Transport` passes it through unchanged.

### Example: simple dict form

Client code can pass a simple field/value dict:

```python
session.request(
    "PATCH",
    "/api/people/{uid}",
    json={"FirstName": "Ada", "LastName": "Lovelace"},
)
```

Transport converts it internally into:

```json
[
  {"op": "replace", "path": "/FirstName", "value": "Ada"},
  {"op": "replace", "path": "/LastName", "value": "Lovelace"}
]
```

### Content-Type enforcement

For `PATCH` requests, if the caller did not provide a `Content-Type` header, `Transport` ensures:

```text
Content-Type: application/json; charset=utf-8
```

------

## Raw vs Typed Methods

This module does not use the raw/typed method pattern.

- It returns `requests.Response` directly
- JSON parsing is performed by callers (`Session` or client modules)
- `PatchPayload` is a typed helper to construct JSON Patch operations

------

## Error Handling

Transport translates and raises SDK exceptions:

### Timeouts

- `requests.exceptions.Timeout` → `TdxTimeoutError`

### Other request failures

- `requests.exceptions.RequestException` → `TdxRequestError`

### HTTP non-success responses

- `status_code >= 400` → `HttpError` (structured dataclass)

Example:

```python
from teamdynamix.exceptions import HttpError, TdxTimeoutError, TdxRequestError

try:
    transport.request("GET", "https://.../api/projects/123")
except HttpError as exc:
    print("HTTP failed:", exc.status_code, exc.response_text)
except TdxTimeoutError:
    print("Timed out")
except TdxRequestError as exc:
    print("Transport error:", exc)
```

------

## Design Intent

The `transport` module intentionally does **not**:

- Retry requests automatically
- Implement backoff strategies
- Provide caching
- Hide `requests.Response` details from callers
- Add client-specific logic or endpoint knowledge

It exists to provide a **single, predictable HTTP boundary** with centralized error translation and cross-cutting behaviors (notably JSON Patch support).

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `exceptions.md`