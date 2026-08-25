# `Config` Module

**Module:** `teamdynamix.config`
**Python Import Path:** `teamdynamix.config`
**API Surface:** *Internal (configuration support)*
**Primary Client Class:** *None*
**DTOs:** *None*

The `config` module provides **configuration loading and resolution utilities** used by the `Session` and authentication layers.

It is responsible for interpreting configuration sources (such as INI files and environment overrides) and producing a resolved configuration that controls how the SDK connects to TeamDynamix.

Most users interact with this module **indirectly** via `Session`.

------

## Architectural Notes

Configuration handling in `teamdynamix-api` follows these architectural guarantees:

- Configuration is **centralized** and resolved once per `Session`
- Client modules do not read configuration directly
- Environment overrides are supported and applied deterministically
- Configuration is treated as **input**, not mutable runtime state

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

Most users do **not** need to import the `config` module directly.

The most common entry point is `Session`, which accepts a configuration path or configuration object:

```python
from teamdynamix import Session

session = Session("./config/config.ini")
```

Internally, the `config` module is used to:

- Load configuration files
- Apply environment-level overrides
- Validate required configuration fields
- Expose resolved values to authentication and transport layers

------

## Using Config Overrides with `Session`

See (**'docs/teamdynamix/session.md'** and **'src/teamdynamix/session.py'**)

The `Session` constructor supports multiple configuration inputs and override mechanisms. This is designed to make one-off scripts and automation easier to write **without editing config files**.

### Supported `Session` constructor inputs

`Session` accepts a `config` argument that may be any of the following:

* A **file path** (`str` or `Path`) to an INI file
* A fully-built **`Config` object**
* A **mapping overlay** (`Mapping[str, Any]`) representing partial config values
* `None` (meaning “load the default INI path”)

Additionally, `Session` accepts:

* `overrides: Mapping[str, Any] | None`
* `auth_mode: "admin" | "user" | None`
* `environment: "TD" | "SBTD" | None`

### Override precedence (important)

Overrides are applied in a strict order:

1. **Base Config** (loaded from file or provided as `Config`)
2. **`config` mapping overlay** (if `config` was provided as a mapping)
3. **`overrides` mapping** (explicit keyword argument)
4. **Explicit keyword overrides** (`auth_mode`, `environment`)

In other words:

> `base_cfg < config_mapping < overrides < explicit_literals`

This means you can safely keep a “standard” config file and override just the few values your script needs.

### Pattern 1 — Override a few keys for a one-off script

Use a normal config file path, but override specific values at construction time:

```python
from teamdynamix import Session

session = Session(
    "./config/config.ini",
    overrides={
        # example: point to an alternate base URL for a script run
        "base_url_override": "https://solutions.teamdynamix.com/SBTDWebApi",
        # example: tighten timeout just for this script
        "default_timeout_seconds": 5,
    },
)
```

This preserves your file-based defaults, but lets the script “tweak” runtime behavior.

### Pattern 2 — Use a config overlay without a file

If you don’t want a file at all (e.g., ephemeral CI job), you can provide a mapping as the `config` argument:

```python
from teamdynamix import Session

session = Session(
    {
        "tenant": "solutions.teamdynamix.com",
        "environment": "SBTD",
        "auth_mode": "admin",
        "beid": "YOUR_BEID",
        "webserviceskey": "YOUR_KEY",
        "default_timeout_seconds": 10,
        "log_level": "INFO",
        "log_console": True,
        "log_dir": "./logs",
    }
)
```

Because this is treated as an overlay, `Session` will merge it and then build a `Config` once as the single validation point. 

### Pattern 3 — Explicitly override environment or auth mode (validated)

If you want to force environment or auth mode regardless of config file contents, use the dedicated keyword arguments:

```python
from teamdynamix import Session

session = Session(
    "./config/config.ini",
    environment="SBTD",
    auth_mode="admin",
)
```

These values are validated as strict literals (`"TD"` / `"SBTD"` and `"admin"` / `"user"`). Invalid values raise `ConfigError`.

### Practical examples

#### Switch tenants/environments without duplicating config files

```python
from teamdynamix import Session

def make_session_for(env: str) -> Session:
    # env is validated: must be "TD" or "SBTD"
    return Session("./config/config.ini", environment=env)
```

#### Temporarily change credentials mode for a script

```python
from teamdynamix import Session

session = Session(
    "./config/config.ini",
    auth_mode="user",
    overrides={
        "username": "user@example.com",
        "password": "secret",
    },
)
```

### Common pitfalls

* **Unknown keys in overlays/overrides:**
  `Session` builds a `Config(**merged)` as a single validation point. If you pass unknown keys, you will get a `ConfigError` (commonly surfacing as “Invalid configuration keys provided”).

* **Overriding `auth_mode` without matching credentials:**
  If `auth_mode="admin"` you must have `beid` and `webserviceskey`. If `auth_mode="user"` you must have `username` and `password`. (These are validated by `Config`.)

* **Expecting overrides to mutate an existing `Session`:**
  Overrides are applied at construction time only. If you need different behavior, create a new `Session`.

### Why this design exists

This approach supports a “script-first” workflow:

* Keep one standard config file for daily use
* Override only what you need per script run
* Ensure validation happens once, deterministically, before requests are made

---

## Configuration File Reference

Below is a **standard example configuration file** illustrating the expected structure and commonly used settings.

This file is typically passed to `Session` during initialization.

```ini
# =====================================================================
# Sample TeamDynamix API configuration
# =====================================================================

[tdx]
# Required
tenant = solutions.teamdynamix.com
# Environment literal expected by the API:
#   TD   = Production
#   SBTD = Sandbox
environment = SBTD

# Optional: override full base URL if needed
# base_url = https://solutions.teamdynamix.com/TDWebApi

[auth]
# Required
# mode = admin | user
mode = admin

# Admin authentication
beid = YOUR_BEID_HERE
webserviceskey = YOUR_WEBSERVICES_KEY_HERE

# User authentication (used when mode = user)
# username = user@example.com
# password = your_password_here

[logging]
# Optional (defaults apply if section is omitted)
log_dir = ./logs
level = INFO
console = true

[http]
# Optional (defaults apply if section is omitted)
# Default timeout in seconds; set to 0 to disable timeouts
default_timeout_seconds = 10
```

### Notes

- Sections are optional unless explicitly marked **Required**
- Unknown keys are ignored
- Missing required values will result in configuration errors
- Environment variables may override file-based values depending on deployment context

------

## Data Models (DTOs)

This module does **not** expose public DTOs.

Configuration data is represented internally using standard Python data structures and is not surfaced as typed models.

------

## Client Class

This module does **not** define a public client class.

Instead, it provides internal helpers that are used during `Session` initialization to resolve configuration values needed for:

- Authentication
- Base URL construction
- Transport behavior

------

## Methods

The `config` module does not define public, user-facing methods.

All functions and helpers in this module are considered **internal implementation details** and may evolve without affecting the public API, provided `Session` behavior remains stable.

------

## Raw vs Typed Methods

This module does not follow the raw/typed method pattern.

Configuration is an internal concern and does not expose raw or typed API responses.

------

## Error Handling

Configuration-related errors are surfaced early:

- Missing or invalid configuration values may raise exceptions during `Session` construction
- Some configuration issues may only surface when an API request is first attempted
- Errors are not silently ignored

```python
from teamdynamix.exceptions import ConfigurationError

try:
    session = Session("./config/config.ini")
except ConfigurationError as exc:
    print("Invalid configuration:", exc)
```

------

## Design Intent

The `config` module intentionally does **not**:

- Provide dynamic configuration mutation at runtime
- Read configuration directly from client modules
- Guess or infer missing configuration values
- Hide configuration errors

Its purpose is to ensure that **configuration is explicit, predictable, and validated** before requests are made.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `auth.md