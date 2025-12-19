# `Session` Module

**Module:** `teamdynamix.session`
**Python Import Path:** `teamdynamix.session`
**API Surface:** *Internal (composition root / facade)*
**Primary Client Class:** `Session`
**DTOs:** *None*

The `session` module defines the **composition root and facade** for the `teamdynamix-api` library.

A `Session` instance owns and wires together:

- Configuration resolution
- Authentication
- Transport (HTTP)
- Logging

All client modules depend on `Session` and **must not** perform their own authentication, configuration loading, or HTTP setup.

------

## Architectural Notes

The `Session` class enforces the core architectural guarantees of the SDK:

- Configuration is resolved **once**, up front
- Authentication is centralized and lazy
- Transport is the sole HTTP boundary
- Logging is consistent and inspectable
- Client modules remain thin and stateless

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session

session = Session("./config/config.ini")
```

Instantiation performs:

1. Configuration resolution and validation
2. Logger creation
3. Transport wiring
4. Authentication wiring

No HTTP requests are made during construction.

------

## Constructor

```python
Session(
    config: str | Path | Config | Mapping[str, Any] | None = "./config/config.ini",
    *,
    auth_mode: Literal["admin", "user"] | None = None,
    environment: Literal["TD", "SBTD"] | None = None,
    overrides: Mapping[str, Any] | None = None,
)
```

### Parameters

| Name          | Type                                | Description                   |
| ------------- | ----------------------------------- | ----------------------------- |
| `config`      | path \| `Config` | mapping | `None` | Base configuration source     |
| `auth_mode`   | `"admin"` | `"user"` | `None`       | Explicit auth mode override   |
| `environment` | `"TD"` | `"SBTD"` | `None`          | Explicit environment override |
| `overrides`   | `Mapping[str, Any] | None`          | Late-applied config overrides |

------

## Configuration Resolution (High Level)

Configuration is resolved using a **strict precedence order**:

```
base config
  < config mapping (if provided)
  < overrides mapping
  < explicit auth_mode / environment
```

All configuration validation occurs **once**, when building the final `Config` object.

If required values are missing or invalid, `ConfigError` is raised during `Session` construction.

------

## Using Config Overrides with `Session` (Short Version)

For a full deep dive, see **`config.md`**.
This section provides the **quick, practical patterns** most users need.

### Pattern 1 — Override a few values at runtime

Keep a standard config file, but override selected keys:

```python
from teamdynamix import Session

session = Session(
    "./config/config.ini",
    overrides={
        "default_timeout_seconds": 5,
    },
)
```

Overrides are merged *after* the base config and validated once.

------

### Pattern 2 — No config file (script-first usage)

Provide configuration entirely as a mapping:

```python
session = Session(
    {
        "tenant": "solutions.teamdynamix.com",
        "environment": "SBTD",
        "auth_mode": "admin",
        "beid": "YOUR_BEID",
        "webserviceskey": "YOUR_KEY",
    }
)
```

This is useful for CI jobs or one-off scripts.

------

### Pattern 3 — Force auth mode or environment

Explicit keyword overrides take highest precedence:

```python
session = Session(
    "./config/config.ini",
    environment="SBTD",
    auth_mode="admin",
)
```

Invalid values raise `ConfigError`.

------

### Important Notes

- Overrides apply **only at construction time**
- Unknown keys in overlays or overrides raise `ConfigError`
- Changing behavior requires creating a new `Session`

------

## Composition Root Responsibilities

After configuration is resolved, `Session` wires:

### Logger

```python
self.logger = Logger(
    log_dir=self.config.log_dir,
    level=self.config.log_level,
    console=self.config.log_console,
)
```

### Transport

```python
self.transport = Transport(
    logger=self.logger,
    default_timeout=self.config.timeout,
)
```

### Authentication

```python
self.auth = Auth(
    config=self.config,
    logger=self.logger,
    transport=self.transport,
)
```

Client modules **must not** create or replace these components.

------

## Facade Methods and Properties

### `base_url`

```python
session.base_url
```

Returns the fully resolved base URL for the current environment.

------

### `log(message, *, level=20)`

```python
session.log("Projects.search called")
```

Thin wrapper around the internal logger.

------

### `authenticate()`

```python
token = session.authenticate()
```

Explicitly authenticate and return a bearer token.

Notes:

- Normally not required
- Authentication is performed lazily when needed

------

### `auth_header()`

```python
headers = session.auth_header()
```

Returns the Authorization header dictionary.

------

### `request(method, path, **kwargs)`

Primary HTTP entrypoint for **all client modules**.

```python
resp = session.request(
    "GET",
    "/api/projects/123",
)
```

**Behavior**

- Prepends `base_url` to `path`
- Injects authorization headers
- Delegates all I/O to `Transport`
- Returns `requests.Response`

Client modules must call this method instead of making direct HTTP calls.

------

## Error Handling

- Configuration errors raise `ConfigError` during construction
- HTTP and transport errors are raised by `Transport`
- Authentication failures surface as `AuthError`

```python
from teamdynamix.exceptions import ConfigError

try:
    session = Session("./config/config.ini")
except ConfigError as exc:
    print("Invalid configuration:", exc)
```

------

## Design Intent

The `Session` module intentionally does **not**:

- Expose transport or auth internals to consumers
- Allow runtime mutation of configuration
- Perform implicit retries or backoff
- Cache client module instances

It exists to provide a **single, explicit, validated entrypoint** into the SDK.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `config.md`
- `auth.md`
- `transport.md`
- `logger.md`