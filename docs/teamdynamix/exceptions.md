# `Exceptions` Module

**Module:** `teamdynamix.exceptions`
**Python Import Path:** `teamdynamix.exceptions`
**API Surface:** *Internal (error types)*
**Primary Client Class:** *None*
**DTOs:** `HttpError`

The `exceptions` module defines the **canonical exception hierarchy** for `teamdynamix-api`.

These exception types establish clear error boundaries across the library:

- Configuration and authentication failures are reported explicitly
- HTTP failures are represented as structured exceptions
- Transport failures (timeouts, connection errors, etc.) are surfaced as SDK-specific exceptions

------

## Architectural Notes

Error handling in `teamdynamix-api` follows these guarantees:

- Errors are raised at well-defined boundaries (primarily `Transport`, plus config/auth validation)
- Client modules do not silently swallow HTTP or transport errors
- Empty results (`[]`, `{}`, `null`) are valid outcomes and are not treated as errors
- Exception types are stable contracts for consumers writing automation

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

Most consumers will import exceptions to catch them:

```python
from teamdynamix.exceptions import (
    TdxError,
    ConfigError,
    AuthError,
    HttpError,
    TdxTimeoutError,
    TdxRequestError,
)
```

You typically do not instantiate exceptions directly (except in tests). They are raised by the SDK.

------

## Data Models (DTOs)

### `HttpError`

`HttpError` is a dataclass that carries structured information about an HTTP failure.

#### Fields

| Field           | Type  | Description                            |
| --------------- | ----- | -------------------------------------- |
| `status_code`   | `int` | HTTP response status code              |
| `method`        | `str` | HTTP method used (e.g., `GET`, `POST`) |
| `url`           | `str` | Fully qualified request URL            |
| `message`       | `str` | Optional error message                 |
| `response_text` | `str` | Optional raw response body text        |

#### Notes

- `HttpError` is raised when a response returns a **non-success status code**.
- The error is intended to be actionable: method + URL + status + any available body.

------

## Client Class

This module does **not** define a client class.

------

## Methods

This module does not define free functions.

It defines exception classes intended to be raised by other SDK layers.

------

## Raw vs Typed Methods

This module does not use the raw/typed method pattern.

Exceptions represent failure conditions rather than API payloads.

------

## Error Handling

### Exception Hierarchy

All SDK exceptions inherit from:

- `TdxError`

Specific subclasses include:

- `ConfigError` — configuration missing or invalid
- `AuthError` — authentication failure or missing credentials
- `HttpError` — HTTP non-success responses (structured dataclass)
- `TdxTimeoutError` — request timeout
- `TdxRequestError` — non-timeout transport errors (connection failures, etc.)

### Common catching patterns

Catch the base type if you want to handle all SDK-originated failures:

```python
from teamdynamix.exceptions import TdxError

try:
    people.search("user@example.com")
except TdxError as exc:
    print("TeamDynamix SDK failure:", exc)
```

Catch `HttpError` if you want HTTP-specific context:

```python
from teamdynamix.exceptions import HttpError

try:
    accounts.get(12345)
except HttpError as exc:
    print("Request failed")
    print("Status:", exc.status_code)
    print("Method:", exc.method)
    print("URL:", exc.url)
    print("Body:", exc.response_text)
```

Catch `TdxTimeoutError` when timeouts should be treated differently:

```python
from teamdynamix.exceptions import TdxTimeoutError

try:
    tickets.search({"MaxResults": 1})
except TdxTimeoutError:
    print("Timed out; retrying later...")
```

------

## Where These Exceptions Are Raised

The table below summarizes **which layer of the SDK typically raises each exception type**, to help diagnose failures quickly.

| Exception Type    | Raised By                              | Indicates                                                    |
| ----------------- | -------------------------------------- | ------------------------------------------------------------ |
| `ConfigError`     | `Config` / `Session` initialization    | Missing or invalid configuration values                      |
| `AuthError`       | Authentication helpers (via `Session`) | Authentication failed or required credentials are missing    |
| `HttpError`       | `Transport`                            | HTTP request completed but returned a non-success status code |
| `TdxTimeoutError` | `Transport`                            | Request exceeded the configured timeout                      |
| `TdxRequestError` | `Transport`                            | Non-timeout request failure (connection errors, DNS issues, etc.) |
| `TdxError`        | Base type                              | Catch-all for any SDK-originated exception                   |

### Practical interpretation

- **`ConfigError`**
  Investigate your configuration file, overrides, or environment variables.
- **`AuthError`**
  Verify credentials, auth mode (`admin` vs `user`), and tenant permissions.
- **`HttpError`**
  The request reached TeamDynamix successfully, but the API rejected it.
  Inspect `status_code`, `method`, `url`, and `response_text`.
- **`TdxTimeoutError` / `TdxRequestError`**
  The request failed before a valid HTTP response was received.
  Investigate network connectivity, timeouts, or proxy configuration.

### Recommended handling strategy

For most applications:

- Catch **`TdxError`** at your outer boundary
- Handle **`HttpError`** explicitly when you need request/response details
- Handle **timeouts** separately if retries or backoff logic is required

---

## Design Intent

The `exceptions` module intentionally:

- Provides a small, explicit exception surface
- Avoids leaking `requests` exception types to consumers
- Makes HTTP failures debuggable with structured data (`HttpError`)
- Allows consumers to catch either broad (`TdxError`) or specific errors

It intentionally does **not**:

- Add complex error taxonomy beyond what the SDK can guarantee
- Automatically retry or “heal” errors
- Transform empty responses into errors

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `transport.md`
- `session.md`