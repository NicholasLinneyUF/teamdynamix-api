# `Auth` Module

**Module:** `teamdynamix.auth`
**Python Import Path:** `teamdynamix.auth`
**API Surface:** *Internal (no direct TeamDynamix API endpoints)*
**Primary Client Class:** *None*
**DTOs:** *None*

The `auth` module contains **authentication helpers and primitives** used internally by the SDK to acquire and manage authorization tokens for TeamDynamix API requests.

This module does **not** expose a standalone client and is **not** intended to be used directly by most consumers.

------

## Architectural Notes

Authentication in `teamdynamix-api` follows these architectural guarantees:

- Authentication is **lazy** — no tokens are requested until an API call is made
- Authentication is **owned by `Session`**, not by individual clients
- Client modules never construct headers or manage tokens
- The authentication mechanism is replaceable without affecting client APIs

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

Most users **do not import this module directly**.

Authentication helpers are instantiated internally by `Session` based on configuration.

Typical usage looks like this:

```python
from teamdynamix import Session

session = Session("./config/config.ini")
```

At this point:

- No authentication request has been made
- No tokens have been cached
- No headers have been constructed

Authentication occurs automatically on the first API request.

------

## Data Models (DTOs)

This module does **not** define public DTOs.

Authentication responses are treated as **internal implementation details** and are not exposed as typed models.

------

## Client Class

This module does **not** expose a public client class.

Instead, it provides internal helpers used by:

- `Session`
- `Transport`

These helpers are responsible for:

- Constructing authentication requests
- Parsing authentication responses
- Providing authorization headers to outbound requests

------

## Methods

The `auth` module does not define public, user-facing methods.

All functions and classes within this module are considered **internal** and may change without notice, provided the public `Session` API remains stable.

------

## Raw vs Typed Methods

This module does not follow the raw/typed method pattern.

Authentication is an internal concern and does not expose API payloads or DTOs to consumers.

------

## Error Handling

Authentication-related errors are surfaced indirectly:

- Failures during token acquisition raise exceptions from `Transport`
- Authentication errors are not swallowed or retried silently
- Client modules do not catch authentication failures

Example:

```python
from teamdynamix.exceptions import HttpError

try:
    # Any API call may trigger authentication
    accounts.list_all()
except HttpError as exc:
    print("Authentication or request failed:", exc)
```

------

## Design Intent

The `auth` module intentionally does **not**:

- Expose token management APIs
- Cache credentials outside the session lifecycle
- Require consumers to manage headers or tokens
- Provide multiple competing authentication workflows

Its sole purpose is to support **secure, consistent authentication** through `Session` and `Transport`.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`

------

### Notes on tone & accuracy (for you)

- This doc is intentionally **boring** — that’s a good thing.
- It sets expectations correctly: *auth exists, but you shouldn’t touch it*.
- It reinforces that **Session is the public contract**, not auth helpers.
- It avoids promising specific auth flows (JWT vs other) that could change.