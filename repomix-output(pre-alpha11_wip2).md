This file is a merged representation of the entire codebase, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of the entire repository's contents.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
config/
  sample.config.ini
docs/
  teamdynamix/
    _template.md
    accounts.md
    applications.md
    attributes.md
    auth.md
    config.md
    events.md
    exceptions.md
    functional_roles.md
    groups.md
    logger.md
    people.md
    projects.md
    service_catalog.md
    session.md
    tickets.md
    transport.md
  ABSTRACT.md
  ARCHITECTURE.md
  CODE_AGENT.md
  CONTRIBUTING.md
  DESIGN.md
  PATTERNS.md
  RELEASING.md
  VERSIONING.md
src/
  teamdynamix/
    __init__.py
    accounts.py
    applications.py
    attributes.py
    auth.py
    config.py
    event.py
    exceptions.py
    functional_roles.py
    groups.py
    logger.py
    people.py
    projects.py
    service_catalog.py
    session.py
    tickets.py
    transport.py
  py.typed
tests/
  test_people_endpoints.py
  test_ticket_endpoints.py
.editorconfig
.gitignore
MANIFEST.in
pyproject.toml
pytest.ini
```

# Files

## File: docs/teamdynamix/_template.md
````markdown
### Module Docs Template (Authoritative)

Every file under `docs/teamdynamix/*.md` should follow this structure:

1. **Module header**
   - Module name
   - Python import path
   - API surface
   - Primary client class
   - DTOs (if any)
2. **Architectural Notes**
   - Explicitly restate architectural guarantees
   - Reference `ARCHITECTURE.md`, `DESIGN.md`, `PATTERNS.md`
3. **Importing and Instantiation**
   - Show `Session` + client construction
   - Reinforce lazy behavior
4. **Data Models (DTOs)**
   - Explicit field tables
   - Clear statement: *selective, not complete*
5. **Client Class**
   - High-level description of responsibility
   - Explicitly endpoint-representative
6. **Methods**
   For each public method:
   - Endpoint
   - Return type
   - Example usage
   - Parameters table (if applicable)
   - Behavior notes (empty results, tenant variance, etc.)
7. **Raw vs Typed Methods**
   - Explain `_raw` vs typed pattern
   - Example side-by-side usage
8. **Error Handling**
   - What raises
   - What does *not* raise
   - Example
9. **Design Intent**
   - What the module intentionally does *not* do
10. **Related Documentation**

- Cross-links to core docs
````

## File: docs/teamdynamix/accounts.md
````markdown
# `Accounts` Module

**Module:** `teamdynamix.accounts`
**API Surface:** `/api/accounts/*`
**Primary Class:** `Accounts`
**DTO:** `Account`

The `Accounts` module provides access to **TeamDynamix Account** data.
Accounts typically represent organizations, departments, or business entities within TeamDynamix.

This module is **endpoint-representative** and intentionally minimal. It mirrors the TeamDynamix Web API directly without adding workflow abstractions or business logic.

------

## Architectural Notes

This module follows all core architectural rules of the library:

- All HTTP traffic flows through `Session → Transport`
- No direct use of `requests`
- No authentication logic inside the client
- Empty results (`[]`, `{}`, `null`) are valid and expected
- Typed models are **selective views**, not full schemas

If you are unfamiliar with these rules, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.accounts import Accounts

session = Session("./config/config.ini")
accounts = Accounts(session)
```

- `Accounts` requires a **Session** instance.
- No network calls occur during construction.
- Authentication happens lazily on first request.

------

## Data Model: `Account`

### `Account` (dataclass)

A **minimal typed representation** of an Account.

This model intentionally exposes only commonly used fields.
For full payloads, use raw methods.

#### Fields

| Field      | Type          | Description                         |
| ---------- | ------------- | ----------------------------------- |
| `ID`       | `int | None`  | Account identifier                  |
| `Name`     | `str | None`  | Account name                        |
| `IsActive` | `bool | None` | Whether the account is active       |
| `ParentID` | `int | None`  | Parent account ID (if hierarchical) |

#### Notes

- Field names match TeamDynamix JSON keys where possible.
- The model is **read-only** and does not enforce schema completeness.

------

## Client Class: `Accounts`

```python
class Accounts:
    ...
```

The `Accounts` client exposes endpoint-aligned methods for retrieving and searching accounts.

------

## Methods

### `get_raw(account_id)`

**Endpoint:** `GET /api/accounts/{id}`
**Returns:** `dict | None`

Retrieve a single account by ID, returning the **raw API response**.

```python
raw = accounts.get_raw(12345)

if raw is None:
    print("Account not found")
else:
    print(raw["Name"])
```

#### Behavior

- Returns a `dict` if the account exists
- Returns `None` if:
  - The API returns `null`
  - The API returns an empty list
- HTTP errors are raised by `Transport`

------

### `get(account_id)`

**Endpoint:** `GET /api/accounts/{id}`
**Returns:** `Account | None`

Retrieve a single account by ID as a typed `Account`.

```python
account = accounts.get(12345)

if account:
    print(account.Name)
```

#### Behavior

- Wraps `get_raw()`
- Returns `None` when no account is found
- Does **not** raise errors for empty results

------

### `search(search_payload)`

**Endpoint:** `POST /api/accounts/search`
**Returns:** `list[Account]`

Search for accounts using a TeamDynamix search payload.

```python
results = accounts.search({
    "SearchText": "Library",
    "IsActive": True
})

for account in results:
    print(account.ID, account.Name)
```

#### Parameters

| Name             | Type   | Description                    |
| ---------------- | ------ | ------------------------------ |
| `search_payload` | `dict` | Raw TeamDynamix search payload |

#### Behavior

- Returns an empty list (`[]`) when no matches are found
- Only dict entries in the response are converted to `Account`
- No validation or transformation of the payload is performed

------

### `list_all(is_active=None)`

**Endpoint:** `GET /api/accounts`
**Returns:** `list[Account]`

Retrieve all accounts, optionally filtered by active status.

```python
active_accounts = accounts.list_all(is_active=True)
```

#### Parameters

| Name        | Type          | Description            |
| ----------- | ------------- | ---------------------- |
| `is_active` | `bool | None` | Optional active filter |

#### Behavior

- If `is_active` is provided, it is passed as a query parameter
- Returns an empty list if no accounts exist
- Query parameters not supported by a tenant are ignored by TeamDynamix

------

## Raw vs Typed Methods

This module follows the standard SDK pattern:

| Method Type | Returns               | Use When                         |
| ----------- | --------------------- | -------------------------------- |
| `*_raw`     | `dict` / `list[dict]` | You need full payloads           |
| Typed       | DTOs                  | You want convenience and clarity |

Example:

```python
raw_accounts = accounts.list_all_raw()
typed_accounts = accounts.list_all()
```

------

## Error Handling

- HTTP errors raise exceptions from `Transport`
- Empty responses are **not errors**
- Client methods do not catch or wrap exceptions

Example:

```python
try:
    account = accounts.get(999999)
except HttpError as e:
    print("Request failed:", e)
```

------

## Design Intent

The `Accounts` module is intentionally conservative:

- No caching
- No retries
- No pagination helpers
- No mutation endpoints (if/when those exist, they will be added explicitly)

This makes the module safe for:

- One-off scripts
- Data audits
- Automation pipelines
- Integration services

------

## Related Documentation

- `ARCHITECTURE.md` — Architectural rules
- `DESIGN.md` — Design constraints
- `PATTERNS.md` — Implementation patterns
- TeamDynamix API Docs — Accounts endpoints
````

## File: docs/teamdynamix/applications.md
````markdown
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
````

## File: docs/teamdynamix/attributes.md
````markdown
# `Attributes` Module

**Module:** `teamdynamix.attributes`
**Python Import Path:** `teamdynamix.attributes`
**API Surface:** `/api/attributes/*`
**Primary Client Class:** `Attributes`
**DTOs:** `Attribute`, `AttributeChoice`

The `Attributes` module provides access to the **TeamDynamix Attributes API surface**, including legacy attribute listing endpoints, attribute **choice management**, and **custom attribute** discovery.

This module is endpoint-representative and intentionally minimal. It mirrors TeamDynamix behavior directly without adding workflow abstractions or opinionated logic.

------

## Architectural Notes

This module follows all core architectural guarantees of the `teamdynamix-api` library:

- All HTTP requests flow through `Session → Transport`
- No direct use of `requests`
- Authentication is handled lazily by the session
- Empty responses (`[]`, `{}`, `null`) are valid and expected
- Typed models are **selective views**, not complete schemas

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.attributes import Attributes

session = Session("./config/config.ini")
attributes = Attributes(session)
```

No network calls or authentication occur during construction.

------

## Data Models (DTOs)

### `Attribute`

A **minimal** typed representation of a TeamDynamix attribute.

This DTO exposes only commonly used fields. It is not a full schema.
Use raw methods when full payload access is required.

#### Fields

| Field         | Type          | Description                      |
| ------------- | ------------- | -------------------------------- |
| `ID`          | `int | None`  | Attribute identifier             |
| `Name`        | `str | None`  | Attribute display name           |
| `Description` | `str | None`  | Attribute description            |
| `IsActive`    | `bool | None` | Whether the attribute is active  |
| `IsDefault`   | `bool | None` | Whether the attribute is default |

------

### `AttributeChoice`

A typed representation of an **attribute choice** (selectable option for an attribute).

Fields align with the TeamDynamix API schema as exposed in the Postman collection.

#### Fields

| Field          | Type          | Description                 |
| -------------- | ------------- | --------------------------- |
| `ID`           | `int | None`  | Choice identifier           |
| `Name`         | `str | None`  | Display name                |
| `IsActive`     | `bool | None` | Active status               |
| `DateCreated`  | `str | None`  | Creation timestamp          |
| `DateModified` | `str | None`  | Last modification timestamp |
| `Order`        | `int | None`  | Display order               |

------

## Client Class

### `Attributes`

```python
class Attributes:
    ...
```

The `Attributes` client maps directly to the TeamDynamix Attributes API surface.

It groups endpoints into:

- **Legacy attribute listing endpoints**
- **Attribute choice management**
- **Custom attribute discovery**

No behavior is hidden or abstracted beyond request/response normalization.

------

## Methods

### `list_for_application_component_raw(app_id, component)`

**Endpoint:** `GET /api/applications/{appId}/attributes/{component}`
**Returns:** `list[dict]`

Retrieve attributes scoped to an application and component.

```python
raw = attributes.list_for_application_component_raw(
    app_id=42,
    component="tickets",
)
```

**Behavior notes**

- Returns an empty list when no attributes exist
- Component path is passed through verbatim

------

### `list_for_application_component(app_id, component)`

**Endpoint:** `GET /api/applications/{appId}/attributes/{component}`
**Returns:** `list[Attribute]`

Typed wrapper around `list_for_application_component_raw`.

------

### `list_for_component_raw(component)`

**Endpoint:** `GET /api/attributes/{component}`
**Returns:** `list[dict]`

Retrieve attributes scoped only by component.

------

### `list_for_component(component)`

**Endpoint:** `GET /api/attributes/{component}`
**Returns:** `list[Attribute]`

Typed wrapper around `list_for_component_raw`.

------

### `list_all_raw()`

**Endpoint:** `GET /api/attributes`
**Returns:** `list[dict]`

Retrieve all attributes available to the tenant.

------

### `list_all()`

**Endpoint:** `GET /api/attributes`
**Returns:** `list[Attribute]`

Typed wrapper around `list_all_raw`.

------

### `list_choices_raw(attribute_id)`

**Endpoint:** `GET /api/attributes/{id}/choices`
**Returns:** `list[dict]`

Retrieve all choices for a specific attribute.

------

### `list_choices(attribute_id)`

**Endpoint:** `GET /api/attributes/{id}/choices`
**Returns:** `list[AttributeChoice]`

Typed wrapper around `list_choices_raw`.

------

### `add_choice_raw(attribute_id, choice_payload, *, copy_from_choice_id=None)`

**Endpoint:** `POST /api/attributes/{id}/choices`
**Returns:** `dict`

Create a new attribute choice.

```python
payload = {
    "Name": "New Choice",
    "IsActive": True,
    "Order": 10,
}

created = attributes.add_choice_raw(
    attribute_id=123,
    choice_payload=payload,
)
```

**Parameters**

| Name                  | Type         | Description           |
| --------------------- | ------------ | --------------------- |
| `choice_payload`      | `dict`       | Raw API payload       |
| `copy_from_choice_id` | `int | None` | Optional clone source |

------

### `add_choice(...)`

**Returns:** `AttributeChoice`

Typed wrapper around `add_choice_raw`.

------

### `edit_choice_raw(attribute_id, choice_id, payload)`

**Endpoint:** `PUT /api/attributes/{id}/choices/{choiceId}`
**Returns:** `dict`

Update an existing attribute choice.

------

### `edit_choice(...)`

**Returns:** `AttributeChoice`

Typed wrapper around `edit_choice_raw`.

------

### `delete_choice_raw(attribute_id, choice_id)`

**Endpoint:** `DELETE /api/attributes/{id}/choices/{choiceId}`
**Returns:** `bool`

Delete an attribute choice.

------

### `delete_choice(attribute_id, choice_id)`

Alias for `delete_choice_raw`.

------

### `list_custom_raw(*, component_id=None, associated_type_id=None, app_id=None)`

**Endpoint:** `GET /api/attributes/custom`
**Returns:** `list[dict]`

Retrieve custom attributes filtered by optional parameters.

------

### `list_custom(...)`

**Returns:** `list[Attribute]`

Typed wrapper around `list_custom_raw`.

------

## Raw vs Typed Methods

Raw methods (`*_raw`) return unmodified API dictionaries and lists.

Typed methods return lightweight dataclasses for convenience.

```python
raw = attributes.list_choices_raw(123)
typed = attributes.list_choices(123)
```

Use raw methods when full payload fidelity is required.

------

## Error Handling

- HTTP errors are raised by `Transport`
- Empty responses are valid and do not raise exceptions
- Client methods do not catch or wrap errors

```python
from teamdynamix.exceptions import HttpError

try:
    attributes.list_all()
except HttpError as exc:
    print("Request failed:", exc)
```

------

## Design Intent

This module intentionally does **not**:

- Cache attribute data
- Validate or reshape payloads
- Hide TeamDynamix quirks
- Provide workflow abstractions

It exists to expose the Attributes API surface faithfully and predictably.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- TeamDynamix API Documentation — Attributes
````

## File: docs/teamdynamix/auth.md
````markdown
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
````

## File: docs/teamdynamix/config.md
````markdown
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
````

## File: docs/teamdynamix/events.md
````markdown
You’re 100% right — I hallucinated an `/api/events` client surface. Thanks for correcting me (and for the code). Given `src/teamdynamix/event.py`, **Events are just structured log-message wrappers** (not TeamDynamix Web API endpoints), so the `events.md` doc needs to reflect that truth.

Below is a corrected, **template-compliant** `./docs/teamdynamix/events.md` (and I’ll stick to “code-proven only” for docs going forward).

------

# `Events` Module

**Module:** `teamdynamix.event`
**Python Import Path:** `teamdynamix.event`
**API Surface:** *Internal (logging/event wrapper)*
**Primary Client Class:** *None*
**DTOs:** `Event`

The `event` module defines a lightweight `Event` dataclass used as a **message wrapper** for structured logging. It is designed to work with the library’s `Logger` layer and provide consistent formatting for log messages, including timestamps and optional context.

This module does not call the TeamDynamix Web API.

------

## Architectural Notes

This module supports the project’s logging/observability philosophy:

- Logging is **observability**, not control flow
- Events are data containers; they do not perform I/O
- Consumers and client modules should not depend on log output to drive behavior

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix.event import Event

evt = Event("Something happened")
```

Creating an `Event` does not perform any network calls or filesystem access.

------

## Data Models (DTOs)

### `Event`

A structured representation of a log event.

#### Fields

| Field        | Type          | Description                       |
| ------------ | ------------- | --------------------------------- |
| `message`    | `str`         | The human-readable message        |
| `level`      | `int`         | Numeric log level (default: `20`) |
| `created_at` | `datetime`    | Timestamp in UTC by default       |
| `context`    | `dict | None` | Optional structured context       |

#### Notes

- `created_at` defaults to `datetime.now(timezone.utc)`
- `context` is optional and intended for structured key/value details

------

## String Representation (`__str__`)

The `Event` class implements a custom `__str__()` method to provide a **consistent, human-readable log format**.

This string representation is what downstream logging components typically emit.

### Format

```text
<ISO-8601 timestamp> [<level>] <message> | context=<context>
```

- Timestamp is always rendered in **UTC** using ISO-8601 format
- Log level is shown as a numeric value
- Context is included only when present

### Example (without context)

```python
from teamdynamix.event import Event

evt = Event("Session initialized")
print(str(evt))
```

Output:

```text
2025-01-15T18:42:11.123456+00:00 [20] Session initialized
```

### Example (with context)

```python
from teamdynamix.event import Event

evt = Event(
    message="HTTP request completed",
    level=20,
    context={
        "method": "GET",
        "path": "/api/attributes",
        "status_code": 200,
    },
)

print(str(evt))
```

Output:

```text
2025-01-15T18:42:11.987654+00:00 [20] HTTP request completed | context={'method': 'GET', 'path': '/api/attributes', 'status_code': 200}
```

### Notes

- The trailing newline (`\n`) is included intentionally to simplify streaming to log sinks
- Context is rendered using standard Python `dict` formatting
- No truncation or redaction is performed by `Event` itself

------

### Why this is useful

This design allows:

- Predictable log formatting across the SDK
- Structured context without forcing a logging framework
- Easy redirection to files, consoles, or external systems

The `Event` class remains a **pure data container** — formatting is provided for convenience, not control.

------

## Client Class

This module does **not** define a client class.

------

## Methods

This module does not define free functions or endpoint methods.

The primary behavior is provided by the `Event` type, especially `__str__()` formatting.

------

## Raw vs Typed Methods

This module does not use the raw vs typed method pattern.

`Event` is already a typed dataclass, and it is not a wrapper around API payloads.

------

## Error Handling

This module does not raise transport or HTTP errors.

Potential errors would only occur through standard Python usage (e.g., passing invalid types), and are not caught or transformed.

------

## Design Intent

The `event` module intentionally does **not**:

- Perform logging I/O itself
- Persist events
- Send events remotely
- Provide an event-bus or subscription system

It exists solely to provide a lightweight, consistent event structure for logging.

------

## Related Documentation

- `logger.md` (if/when you document the logger module)
- `src/teamdynamix/event.py`
````

## File: docs/teamdynamix/exceptions.md
````markdown
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
````

## File: docs/teamdynamix/functional_roles.md
````markdown
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
````

## File: docs/teamdynamix/groups.md
````markdown
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
````

## File: docs/teamdynamix/logger.md
````markdown
# `Logger` Module

**Module:** `teamdynamix.logger`
**Python Import Path:** `teamdynamix.logger`
**API Surface:** *Internal (logging support)*
**Primary Client Class:** `Logger`
**DTOs:** `Event` (from `teamdynamix.event`)

The `logger` module provides a **minimal, thread-safe logging facility** used by the SDK to record operational events.

It is intentionally simple and self-contained:

- Keeps an in-memory list of `Event` objects
- Writes events to a timestamped log file
- Optionally prints events to the console
- Does **not** depend on Python’s `logging` module

------

## Architectural Notes

Logging in `teamdynamix-api` follows these principles:

- Logging is for **observability**, not control flow
- Logging is synchronous and explicit
- Loggers are owned by higher-level components (typically `Session`)
- Logging must not interfere with request/response behavior

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

Most users will **not** instantiate `Logger` directly.
It is typically created and owned by `Session`.

For direct usage or testing, a logger can be instantiated as follows:

```python
from teamdynamix.logger import Logger

logger = Logger(
    log_dir="./logs",
    level="INFO",
    console=True,
)
```

Instantiation creates:

- A log directory (if it does not exist)
- A timestamped log file within that directory

No I/O occurs beyond directory creation.

------

## Data Models (DTOs)

### `Event`

The `Logger` records instances of `Event` (defined in `teamdynamix.event`) for each logged message.

Each event contains:

- Message text
- Numeric log level
- Timestamp (UTC)
- Optional structured context

See `events.md` for full `Event` documentation.

------

## Client Class

### `Logger`

```python
class Logger:
    ...
```

The `Logger` class is responsible for recording events and emitting them to configured outputs.

------

## Methods

### `log(message, level=None, context=None)`

Record a log event.

```python
logger.log("Session initialized")
logger.log(
    "HTTP request completed",
    level=20,
    context={"method": "GET", "status": 200},
)
```

**Parameters**

| Name      | Type          | Description                                      |
| --------- | ------------- | ------------------------------------------------ |
| `message` | `str`         | Log message                                      |
| `level`   | `int | None`  | Numeric log level (defaults to configured level) |
| `context` | `dict | None` | Optional structured context                      |

**Behavior notes**

- If `level` is lower than the configured logger level, the event is ignored
- Accepted level names map internally to numeric values:
  - `CRITICAL` → 50
  - `ERROR` → 40
  - `WARNING` / `WARN` → 30
  - `INFO` → 20
  - `DEBUG` → 10
- When recorded:
  - The event is appended to `logger.events`
  - Printed to console if `console=True`
  - Appended to the log file

------

### `clear_events()`

Clear the in-memory event list.

```python
logger.clear_events()
```

**Behavior notes**

- Does not affect the log file
- Thread-safe
- Intended for test or inspection scenarios

------

## Raw vs Typed Methods

This module does not use the raw/typed method pattern.

`Logger` records typed `Event` objects directly.

------

## Error Handling

The logger is designed to be **non-disruptive**:

- Logging failures should not affect SDK operation
- No SDK-specific exceptions are raised by `Logger`
- Standard Python I/O errors may still propagate in extreme cases (e.g., filesystem permissions)

------

## Design Intent

The `logger` module intentionally does **not**:

- Use or wrap Python’s `logging` module
- Provide log rotation or retention policies
- Perform asynchronous or background logging
- Send logs to remote systems
- Enforce structured logging schemas

It exists to provide a **predictable, dependency-free logging mechanism** suitable for scripts, automation, and SDK diagnostics.

------

## Related Documentation

- `events.md`
- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
````

## File: docs/teamdynamix/people.md
````markdown
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
````

## File: docs/teamdynamix/projects.md
````markdown
# `Projects` Module

**Module:** `teamdynamix.projects`
**Python Import Path:** `teamdynamix.projects`
**API Surface:** `/api/projects/*`
**Primary Client Class:** `Projects`
**DTOs:** `Project`

The `projects` module provides a thin, endpoint-representative client for working with **TeamDynamix Projects (PPM)**.

It intentionally stays close to the vendor API surface and exposes only minimal typed models. When richer or tenant-specific data is required, raw dictionary payloads are returned.

------

## Architectural Notes

This module follows the core architectural guarantees of `teamdynamix-api`:

- All HTTP calls flow through `Session → Transport`
- Client methods are thin endpoint wrappers
- Empty responses are valid and expected in several endpoints
- Typed models are intentionally minimal
- Response-shape normalization is defensive and conservative

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.projects import Projects

session = Session("./config/config.ini")
projects = Projects(session)
```

No network calls occur during construction.

------

## Data Models (DTOs)

### `Project`

A minimal typed representation of a TeamDynamix Project.

#### Fields

| Field         | Type          | Description         |
| ------------- | ------------- | ------------------- |
| `ID`          | `int | None`  | Project identifier  |
| `Name`        | `str | None`  | Project name        |
| `IsActive`    | `bool | None` | Active status       |
| `Description` | `str | None`  | Project description |
| `ManagerUid`  | `str | None`  | Project manager UID |

#### Notes

- ID normalization accepts `ID`, `Id`, or `id`
- Manager UID normalization accepts `ManagerUid` or `ManagerUID`
- This model is intentionally lean and may be expanded later with proven needs

------

## Client Class

### `Projects`

```python
class Projects:
    ...
```

The `Projects` client exposes the following endpoint groups:

- Core project CRUD-style operations
- Project feed operations
- Project plan and task operations
- Project issue feed operations

------

## Methods

### Core Project Endpoints

#### `search(criteria)`

**Endpoint:** `POST /api/projects/search`
**Returns:** `list[Project]`

Search for projects using a raw criteria payload.

```python
results = projects.search({
    "IsActive": True,
    "MaxResults": 25,
})

for p in results:
    print(p.ID, p.Name)
```

**Behavior notes**

- Returns `[]` when no projects match (valid)
- Only dictionary entries are converted into `Project` objects

------

#### `get(project_id)`

**Endpoint:** `GET /api/projects/{id}`
**Returns:** `Project`

Retrieve a project by ID.

```python
project = projects.get(12345)
print(project.Name, project.IsActive)
```

**Behavior notes**

- Raises `ValueError` if the response is not a JSON object

------

#### `create(project_data, *, notify_new_manager=False, notify_new_alt_managers=False)`

**Endpoint:** `POST /api/projects`
**Returns:** `Project`

Create a new project.

```python
created = projects.create(
    {
        "Name": "New Initiative",
        "IsActive": True,
    },
    notify_new_manager=True,
)
```

**Query parameters**

| Name                   | Type   |
| ---------------------- | ------ |
| `notifyNewManager`     | `bool` |
| `notifyNewAltManagers` | `bool` |

**Behavior notes**

- Query parameters are serialized as lowercase strings
- Raises `ValueError` if response shape is unexpected

------

#### `edit(project_id, updates)`

**Endpoint:** `POST /api/projects/{id}`
**Returns:** `Project`

Edit an existing project.

```python
updated = projects.edit(12345, {"Description": "Updated description"})
```

**Notes**

- TeamDynamix uses `POST` (not `PUT`) for project edits
- Raises `ValueError` on unexpected response shape

------

#### `patch(project_id, operations)`

**Endpoint:** `PATCH /api/projects/{id}`
**Returns:** `Project`

Apply partial updates using JSON Patch semantics.

```python
from teamdynamix.transport import PatchPayload

updated = projects.patch(
    12345,
    [
        PatchPayload.replace("/Name", "Renamed Project"),
    ],
)
```

**Accepted input forms**

- `dict` → converted by `Transport` into patch operations
- `list[PatchPayload]`
- `list[dict]` (assumed RFC-6902 compliant)

**Behavior notes**

- Mixed lists (dict + PatchPayload) are rejected
- Raises `TypeError` for invalid inputs
- Raises `ValueError` for unexpected response shape

------

## Project Feed Endpoints

### `get_feed(project_id)`

**Endpoint:** `GET /api/projects/{id}/feed`
**Returns:** `list[dict]`

Retrieve a project’s activity feed.

```python
feed = projects.get_feed(12345)
```

Returns `[]` when empty (valid).

------

### `add_feed(project_id, body)`

**Endpoint:** `POST /api/projects/{id}/feed`
**Returns:** `dict`

Add a feed entry to a project.

```python
entry = projects.add_feed(12345, "Project kickoff completed.")
```

------

## Plan / Task Endpoints

### `get_plan(project_id, plan_id)`

**Endpoint:** `GET /api/projects/{projectId}/plans/{planId}`
**Returns:** `dict \| None`

Retrieve a project plan.

```python
plan = projects.get_plan(12345, 678)
```

------

### `edit_task(project_id, plan_id, task_id, updates, *, notify_new_resources=False)`

**Endpoint:**
`POST /api/projects/{projectId}/plans/{planId}/tasks/{taskId}/edit`

**Returns:** `dict \| None`

Edit a project task.

```python
projects.edit_task(
    12345,
    678,
    42,
    {"Name": "Updated Task Name"},
    notify_new_resources=True,
)
```

------

## Issue Feed Endpoints

### `get_issue_feed(project_id, issue_id)`

**Endpoint:**
`GET /api/projects/{projectId}/issues/{issueId}/feed`

**Returns:** `list[dict]`

Retrieve issue feed entries.

```python
feed = projects.get_issue_feed(12345, 99)
```

------

### `add_issue_comment(project_id, issue_id, comment_payload)`

**Endpoint:**
`POST /api/projects/{projectId}/issues/{issueId}/feed`

**Returns:** `dict`

Add a comment to an issue feed.

```python
projects.add_issue_comment(
    12345,
    99,
    {"Body": "Investigating root cause."},
)
```

------

## Raw vs Typed Methods

This module uses a **mixed strategy**:

- Core project operations return typed `Project` DTOs
- Feed, plan, task, and issue endpoints return raw `dict` payloads

This reflects the complexity and variability of non-core project schemas.

------

## Error Handling

- HTTP and transport errors are raised by `Transport`
- Empty responses are valid where documented
- Unexpected response shapes raise `ValueError`
- Invalid patch inputs raise `TypeError`

```python
from teamdynamix.exceptions import HttpError

try:
    projects.get(999999)
except HttpError as exc:
    print("HTTP error:", exc.status_code)
```

------

## Design Intent

This module intentionally does **not**:

- Model full project, plan, or task schemas
- Add pagination or caching helpers
- Abstract TeamDynamix workflow logic
- Validate request payload contents

It exists to provide **thin, predictable access** to the TeamDynamix Projects API while remaining flexible for tenant-specific use cases.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`
- TeamDynamix API Documentation — Projects
````

## File: docs/teamdynamix/service_catalog.md
````markdown
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
````

## File: docs/teamdynamix/session.md
````markdown
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
````

## File: docs/teamdynamix/tickets.md
````markdown
# `Tickets` Module

**Module:** `teamdynamix.tickets`
**Python Import Path:** `teamdynamix.tickets`
**API Surface:** `/api/{ticketingAppId}/tickets/*`
**Primary Client Class:** `Tickets`
**DTOs:** `Ticket`

The `tickets` module provides a thin, endpoint-representative client for working with **TeamDynamix Tickets** within a specific ticketing application.

It intentionally models only a **minimal, commonly useful subset** of ticket fields while preserving access to raw payloads for feeds, metadata, and tenant-specific extensions.

------

## Architectural Notes

This module follows the core architectural guarantees of `teamdynamix-api`:

- All HTTP requests flow through `Session → Transport`
- Clients are scoped to a specific **ticketing app**
- Empty responses are valid and expected in multiple endpoints
- Typed DTOs are intentionally minimal
- JSON Patch is supported for updates without over-modeling

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.tickets import Tickets

session = Session("./config/config.ini")

# ticketing_app_id is required
tickets = Tickets(session, ticketing_app_id=123)
```

No network calls occur during construction.

------

## Data Models (DTOs)

### `Ticket`

A minimal typed representation of a TeamDynamix Ticket.

#### Fields

| Field                | Type         | Description            |
| -------------------- | ------------ | ---------------------- |
| `ID`                 | `int | None` | Ticket identifier      |
| `Title`              | `str | None` | Ticket title           |
| `Description`        | `str | None` | Ticket description     |
| `StatusID`           | `int | None` | Status identifier      |
| `StatusName`         | `str | None` | Status name            |
| `TypeID`             | `int | None` | Ticket type identifier |
| `TypeName`           | `str | None` | Ticket type name       |
| `PriorityID`         | `int | None` | Priority identifier    |
| `PriorityName`       | `str | None` | Priority name          |
| `RequestorUid`       | `str | None` | Requestor UID          |
| `ResponsibleUid`     | `str | None` | Responsible user UID   |
| `ResponsibleGroupID` | `int | None` | Responsible group ID   |

#### Notes

- ID normalization accepts `ID`, `Id`, or `id`
- UID normalization accepts both `Uid` and `UID` variants
- This DTO intentionally does **not** model the full ticket schema

------

## Metadata Clients

These helper clients expose **ticket metadata** scoped to a ticketing app.

### `TicketPriorities`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/priorities`

```python
from teamdynamix.tickets import TicketPriorities

priorities = TicketPriorities(session, 123).list()
```

Returns a list of raw dictionaries.

------

### `TicketTypes`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/types?isActive=`

```python
from teamdynamix.tickets import TicketTypes

types = TicketTypes(session, 123).list(is_active=True)
```

------

### `TicketStatuses`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/statuses?isActive=`

```python
from teamdynamix.tickets import TicketStatuses

statuses = TicketStatuses(session, 123).list(is_active=True)
```

------

### `TicketSources`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/sources?isActive=`

```python
from teamdynamix.tickets import TicketSources

sources = TicketSources(session, 123).list()
```

------

## Client Class

### `Tickets`

```python
class Tickets:
    ...
```

The `Tickets` client maps directly to the common TeamDynamix ticket endpoints for a specific ticketing application.

------

## Methods

### Core Ticket Operations

#### `get(ticket_id)`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/{id}`
**Returns:** `Ticket \| None`

```python
ticket = tickets.get(456)
if ticket:
    print(ticket.Title, ticket.StatusName)
```

**Behavior notes**

- Returns `None` when the API response is empty
- If the API returns a list, the first item is used

------

#### `create(ticket_payload)`

**Endpoint:** `POST /api/{ticketingAppId}/tickets`
**Returns:** `Ticket`

```python
created = tickets.create({
    "Title": "Printer not working",
    "Description": "The printer on floor 2 is jammed.",
})
```

**Behavior notes**

- Payload is passed through unchanged
- If response shape is unexpected, an empty dict is coerced before DTO creation

------

#### `search(search_payload)`

**Endpoint:** `POST /api/{ticketingAppId}/tickets/search`
**Returns:** `list[Ticket]`

```python
results = tickets.search({
    "SearchText": "printer",
    "MaxResults": 10,
})
```

**Behavior notes**

- Returns `[]` when no results are found (valid)
- Filters non-dict list entries defensively

------

#### `update(ticket_id, ops, *, notify_new_responsible=None)`

**Endpoint:**
`PATCH /api/{ticketingAppId}/tickets/{id}?notifyNewResponsible=`

**Returns:** `bool`

```python
from teamdynamix.transport import PatchPayload

tickets.update(
    456,
    {"StatusID": 3},
    notify_new_responsible=True,
)

tickets.update(
    456,
    [
        PatchPayload.replace("/Title", "Updated title"),
    ],
)
```

**Accepted update forms**

- `dict[str, Any]`
  → converted by `Transport` into JSON Patch `"replace"` operations
- `list[PatchPayload]`
- `list[dict]` (assumed RFC-6902 compliant)

**Behavior notes**

- Mixed operation lists are normalized defensively
- Returns `True` on success
- Invalid payload shapes may raise `TypeError`

------

### Ticket Feed Operations

#### `get_feed(ticket_id)`

**Endpoint:** `GET /api/{ticketingAppId}/tickets/{id}/feed`
**Returns:** `list[dict]`

```python
feed = tickets.get_feed(456)
```

Returns `[]` when empty (valid).

------

#### `add_feed_entry(ticket_id, feed_payload)`

**Endpoint:** `POST /api/{ticketingAppId}/tickets/{id}/feed`
**Returns:** `bool`

```python
tickets.add_feed_entry(
    456,
    {"Body": "Investigating the issue."},
)
```

Returns `True` on success.

------

## Raw vs Typed Methods

This module uses a **mixed approach**:

- Core ticket operations return typed `Ticket` DTOs
- Metadata endpoints return raw dictionaries
- Feed endpoints return raw dictionaries
- Updates accept both typed patch payloads and simple dicts

This balances usability with tenant-specific flexibility.

------

## Error Handling

- HTTP and transport errors are raised by `Transport`
- Empty responses are treated as valid outcomes
- Invalid patch payloads may raise `TypeError`

```python
from teamdynamix.exceptions import HttpError

try:
    tickets.get(999999)
except HttpError as exc:
    print("HTTP error:", exc.status_code)
```

------

## Design Intent

This module intentionally does **not**:

- Model the full ticket schema
- Enforce validation on ticket payloads
- Provide workflow abstractions
- Automatically resolve metadata IDs

It exists to provide **predictable, endpoint-aligned access** to TeamDynamix ticket operations while remaining flexible for scripting and automation.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`
- TeamDynamix API Documentation — Tickets
````

## File: docs/teamdynamix/transport.md
````markdown
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
````

## File: docs/ABSTRACT.md
````markdown
# Project Abstract — TeamDynamix API (Python)

## What

**teamdynamix-api** is a lightweight, modular Python library that provides structured, predictable access to the **TeamDynamix Web API**.  
Its primary goal is to make programmatic interaction with TeamDynamix **simple, explicit, and dependable**, without obscuring or reshaping the vendor’s API surface.

The library is designed to be:

- **Easy to drop into any environment**
- **Minimal in abstraction**
- **Faithful to TeamDynamix endpoint contracts**
- **Safe for scripting, automation, and integration tooling**

It exposes clear, endpoint-aligned client modules (e.g. `People`, `Tickets`, `Projects`) while keeping transport, authentication, configuration, and logging concerns cleanly separated.

---

## Why

TeamDynamix is widely used in higher education and enterprise IT environments, yet its Web API presents several challenges for Python consumers:

- Inconsistent endpoint behaviors (e.g., PATCH semantics, POST-for-edit patterns)
- Large, verbose JSON payloads
- Limited official client tooling
- High friction when writing repeatable automation scripts

Many existing wrappers attempt to “improve” the API by adding heavy abstractions, ORMs, or opinionated frameworks. While well-intentioned, this often results in:

- Loss of clarity about what endpoint is actually being called
- Difficulty debugging API-level issues
- Tight coupling to one specific workflow or application architecture

This project takes the opposite approach.

**The library exists to reduce friction, not to reinterpret the API.**  
It prioritizes *transparency, correctness, and composability* over convenience abstractions.

---

## How

### Architectural Principles

The design is guided by a small set of strict, consistently applied architectural rules:

1. **Single Transport Boundary**  
   All HTTP traffic flows through a single `Transport` layer.
   - Centralized error handling
   - Centralized timeout behavior
   - Centralized JSON Patch normalization
   - No `requests` usage outside this boundary

2. **Explicit Session Ownership**  
   A `Session` object coordinates:
   - Configuration
   - Authentication lifecycle
   - Transport usage
   - Logging context

   Client modules never manage auth or HTTP directly.

3. **Endpoint-Representative Client Modules**  
   Each client class maps *directly* to TeamDynamix endpoint groups:
   - One public method ≈ one vendor endpoint
   - No hidden helper endpoints
   - No silent retries or implicit side effects

4. **Minimal Opinionation**
   - Payloads are accepted and returned primarily as `dict` / `list`
   - Typed dataclasses are used **only where they add clarity**, not everywhere
   - No ORM-style state tracking
   - No “magic” transformations outside documented cases (e.g., JSON Patch)

5. **Vendor-Accurate Semantics**
   - PATCH uses RFC6902-style JSON Patch (as required by TeamDynamix)
   - POST-for-edit endpoints are preserved as-is
   - Empty lists and empty responses are treated as valid outcomes
   - Non-2xx responses are never silently swallowed

---

### Configuration and Ergonomics

The library is intentionally flexible in how it is configured:

- Configuration can be loaded from:
  - INI files
  - Dictionaries
  - Partially populated `Config` objects
- Defaults are applied wherever safe
- Errors are raised **only when required information is missing**
- Logging and HTTP settings are optional and sensible by default

This allows the same library to be used in:

- One-off scripts
- CI/CD jobs
- Long-running services
- Interactive notebooks
- Enterprise automation pipelines

---

### Value Delivery

By adhering to these constraints, the library delivers tangible value:

- **Predictability**  
  Developers can reason about behavior by reading the code or the API docs—no surprises.

- **Debuggability**  
  When something fails, the failure aligns with the actual API call and response.

- **Longevity**  
  Because the library mirrors TeamDynamix rather than abstracting over it, API changes are easier to accommodate without rewrites.

- **Composability**  
  The library integrates cleanly with any logging, scheduling, orchestration, or application framework.

---

## End State Vision

The end goal is a **stable, well-documented, SemVer-compliant** Python library that:

- Can be installed and used with minimal setup
- Does not force architectural decisions on its consumers
- Serves equally well as:
  - A scripting utility
  - An integration layer
  - A building block for larger systems

In short:

> **A mostly un-opinionated, drop-in Python library that makes TeamDynamix’s Web API easier to use—without hiding what it actually does.**
````

## File: docs/ARCHITECTURE.md
````markdown
- # ARCHITECTURE.md
  ## TeamDynamix API Client — Architectural Decisions

  This document describes the **architectural decisions** that govern the `teamdynamix-api` project.

  It focuses on **what decisions were made**, **why they were made**, and **how they shape the system**, rather than on implementation details.  
  Implementation guidance lives in `DESIGN.md` and `PATTERNS.md`.

  These decisions are binding across all versions unless explicitly superseded.

  ---

  ## 1. Architectural Goals

  The architecture is designed to satisfy the following goals:

  1. **Faithful representation of the TeamDynamix Web API**
  2. **Minimal opinionation**
  3. **Predictable behavior under automation**
  4. **Low cognitive load for both humans and LLMs**
  5. **Long-term maintainability without framework lock-in**

  This library is intended to be:
  - Embedded in scripts
  - Used in enterprise automation
  - Extended incrementally
  - Audited and reasoned about line-by-line

  It is *not* intended to be:
  - An ORM
  - A workflow engine
  - A high-level SDK with business logic

  ---

  ## 2. Core Architectural Decisions

  ### 2.1 Single Transport Boundary

  **Decision**  
  All HTTP communication with TeamDynamix occurs through a single component: `Transport`.

  **Why**
  - Prevents HTTP behavior from leaking across the codebase
  - Centralizes timeout, error, and protocol handling
  - Enables consistent behavior across all endpoints
  - Simplifies testing and future enhancements (retries, backoff, metrics)

  **How**
  - `Transport` is the *only* module allowed to import or call `requests`
  - All client modules call `Session.request(...)`
  - All HTTP exceptions are raised from `Transport`

  This ensures that the HTTP surface area of the library is minimal and controlled.

  ---

  ### 2.2 Session as Composition Root

  **Decision**  
  `Session` acts as the composition root for the system.

  **Why**
  - Keeps object creation and wiring in one place
  - Avoids scattered instantiation of Config, Auth, Logger, or Transport
  - Improves testability and clarity of control flow

  **How**
  - `Session` owns:
    - Config resolution
    - Auth lifecycle
    - Transport instance
    - Logging context
  - Client modules receive a `Session` instance and nothing else

  Client modules are therefore **stateless with respect to infrastructure**.

  ---

  ### 2.3 Lazy Authentication

  **Decision**  
  Authentication is performed lazily, not during object construction.

  **Why**
  - Avoids side effects in constructors
  - Enables offline configuration validation
  - Improves testability
  - Prevents unexpected network calls

  **How**
  - `Auth.authenticate()` is called only when a request requires a token
  - Tokens are cached within the Session/Auth lifecycle
  - Explicit authentication can be triggered by the developer if desired

  ---

  ### 2.4 Endpoint-Representative Clients

  **Decision**  
  Each client class corresponds directly to a TeamDynamix API surface.

  **Why**
  - Maintains a clear mental model aligned with vendor documentation
  - Prevents accidental abstraction drift
  - Makes debugging and traceability straightforward

  **How**
  - One client class per major API surface (People, Tickets, Projects, etc.)
  - Each public method maps to a single documented endpoint
  - Method names reflect endpoint intent, not “improved” semantics

  Vendor quirks are preserved intentionally.

  ---

  ### 2.5 Transport-Level JSON Patch Normalization

  **Decision**  
  RFC6902 JSON Patch handling is centralized in `Transport`.

  **Why**
  - JSON Patch is a cross-cutting concern
  - Multiple endpoints require the same transformation
  - Prevents duplication and inconsistency

  **How**
  - If HTTP method is `PATCH`:
    - `dict` payloads are converted to JSON Patch
    - `list` payloads are passed through unchanged
  - Client modules remain unaware of patch mechanics

  This keeps PATCH semantics correct while minimizing client complexity.

  ---

  ### 2.6 Explicit Error Boundaries

  **Decision**  
  Errors are raised at well-defined boundaries and are never silently handled.

  **Why**
  - Silent failures are dangerous in automation
  - TeamDynamix often returns valid-but-empty responses
  - HTTP errors must be distinguishable from “no results”

  **How**
  - Transport raises:
    - `HttpError`
    - `TdxTimeoutError`
    - `TdxRequestError`
  - Client modules do not catch HTTP errors
  - Empty responses are treated as valid data

  ---

  ## 3. Configuration Philosophy

  ### Decision: Flexible, Mergeable Configuration

  **Why**
  - Supports scripts, services, and interactive use
  - Reduces boilerplate for simple cases
  - Allows gradual override of defaults

  **How**
  - Session accepts:
    - Config object
    - Config file path
    - Dict overrides
    - Explicit literals
  - Missing values fall back to defaults
  - Errors raised only when required fields cannot be resolved

  ---

  ## 4. Logging as Observability, Not Control Flow

  **Decision**
  Logging is informational and never controls logic.

  **Why**
  - Prevents hidden dependencies
  - Enables safe debugging
  - Keeps behavior consistent across environments

  **How**
  - Default log level: INFO
  - Errors always logged
  - Client methods log intent, not outcomes

  ---

  ## 5. Stability & Evolution

  **Decision**
  Architecture stabilizes early, features evolve later.

  **Why**
  - Prevents long-term entropy
  - Enables safe iteration during pre-alpha
  - Makes future alpha/beta transitions smoother

  **How**
  - Architectural rules are enforced even during pre-alpha
  - Breaking architectural changes require explicit documentation

  ---

  ## 6. Summary

  The architecture of `teamdynamix-api` is designed to:

  - Be boring in the best way
  - Be explicit rather than clever
  - Make errors visible
  - Preserve vendor intent
  - Scale with complexity without becoming opaque

  This document defines the **shape of the system**.  
  Implementation details must conform to it.
````

## File: docs/CODE_AGENT.md
````markdown
# code_agent.md  
**LLM Contribution & Assistance Guide — teamdynamix-api**

This document exists **exclusively** to orient an LLM agent that is assisting with or generating code for this repository.  
It is not end-user documentation. It is a **design contract, style guide, and architectural boundary reference**.

If you generate code that violates this document, the code is considered incorrect even if it “works.”

---

## 1. Project Identity & Purpose

**Repository:** `teamdynamix-api`  
**Language:** Python 3.11+  
**Domain:** TeamDynamix Web API client library

### Core Goal

Provide a **drop-in, mostly un-opinionated Python library** for interacting with TeamDynamix’s Web API that:

- Preserves vendor endpoint semantics
- Avoids hidden abstractions
- Is safe for scripting, automation, and enterprise integration
- Scales from one-off scripts to long-running services

This is **not** an ORM, SDK framework, or workflow engine.

---

## 2. Architectural Non-Negotiables

These rules are absolute.

### 2.1 Single Transport Boundary

- All HTTP requests go through **`Transport`**
- No `requests.*` calls outside `transport.py`
- Transport is responsible for:
  - Timeouts
  - Request exceptions
  - HTTP status errors
  - JSON Patch normalization (RFC6902)
- Client modules **never** touch `requests` directly

If you add a new module and it imports `requests`, that is a violation.

---

### 2.2 Session Owns Coordination

`Session` coordinates:

- Config resolution
- Auth lifecycle
- Transport usage
- Logging context

Client modules:

- Receive a `Session`
- Call `session.request(...)`
- Call `.json()` on the returned `Response`
- Interpret the response

Client modules **do not**:
- Authenticate
- Retry
- Catch HTTP exceptions
- Manage headers manually

---

### 2.3 Endpoint-Representative Client Modules

Each client class maps to **one TeamDynamix API surface**.

Example:

| Class    | Represents        |
| -------- | ----------------- |
| People   | `/api/people/*`   |
| Tickets  | `/api/tickets/*`  |
| Projects | `/api/projects/*` |

Rules:

- One public method ≈ one vendor endpoint
- Method names reflect the endpoint intent
- Do **not** invent helper endpoints
- Do **not** collapse multiple endpoints into one method
- Do **not** “improve” vendor semantics

If the API is weird, **mirror the weirdness**.

---

## 3. Data Handling Rules

### 3.1 Response-First Pattern

Always follow this pattern in client modules:

```python
resp = self.session.request("GET", path)
data = resp.json()
```

Never assume:

```python
data = self.session.request(...)
```

`Session.request()` returns a `requests.Response`, not JSON.

------

### 3.2 Empty Results Are Valid

TeamDynamix often returns:

- `[]`
- `{}`
- `null`
- `200 OK` with no body

These are **not errors**.

Client modules must:

- Treat empty lists as valid
- Treat empty dicts as valid
- Avoid raising exceptions for “no results”

Only Transport raises HTTP-level exceptions.

------

### 3.3 Typed Models Are Selective

Use dataclasses **only when they add value**.

Examples:

- `Person`
- `Ticket`
- `Project`

Rules:

- Do **not** fully model massive TDX objects
- Do **not** attempt schema completeness
- Typed models are **lightweight views**, not contracts
- Raw `dict[str, Any]` is acceptable and preferred in many endpoints

------

## 4. PATCH & JSON Patch Rules

TeamDynamix PATCH endpoints use **RFC6902 JSON Patch**.

### Central Rule

**PATCH conversion happens ONLY in Transport.**

Client modules may pass:

- `dict[str, Any]` → Transport converts to JSON Patch
- `list[PatchPayload]` → must call `.to_dict()`
- `list[dict]` → passed through unchanged

Client modules must **not** build JSON Patch manually unless explicitly required.

### PatchPayload

```python
@dataclass(frozen=True, slots=True)
class PatchPayload:
    op: str
    path: str
    value: Any
```

- Never use `__dict__`
- Always use `.to_dict()`

------

## 5. Error Handling Policy

### What Raises Errors

Only these layers raise exceptions:

- `Transport`
- `Config` validation
- Explicit `ValueError` for impossible response shapes (rare)

### What Must NOT Catch Errors

- Client modules
- Test scripts
- Helper methods

No silent failures.
No per-method `try/except`.

------

## 6. Configuration Philosophy

Configuration is intentionally flexible.

### Accepted Inputs

`Session()` may receive:

- No config (defaults + file loading)
- A config file path
- A partial `Config` object
- A dict of overrides
- Explicit literals (auth mode, environment)

### Merge Semantics

- Provided values override defaults
- Missing values fall back to defaults
- Errors are raised **only** if required core fields are missing *and no defaults exist*

### Required Sections

Strict:

- `[tdx]`
- `[auth]`

Optional:

- `[logging]`
- `[http]`

------

## 7. Logging Rules

Defaults matter.

- Default log level: **INFO**
- Errors and exceptions must always log
- Client modules log intent (`People.search`, `Tickets.create`, etc.)
- Logging is informational, not control flow

Never gate logic on log output.

------

## 8. Versioning & Stability Expectations

This repository follows **strict SemVer** with **lifecycle phases**.

### Current Phase

- `pre-alpha.N`
- No backward compatibility guarantees
- Large refactors are acceptable
- API shape may change

However:

- Architectural rules **do not change**
- Patterns established now are binding forward

Do not introduce “temporary hacks.”

------

## 9. Style & Code Generation Guidelines

### Required Traits

- Explicit > clever
- Readable > concise
- Predictable > abstract
- Vendor-faithful > ergonomic sugar

### Avoid

- Metaprogramming
- Magic dispatch
- Decorator-heavy logic
- Global state
- Hidden retries
- Silent coercion

### Prefer

- Small helper functions
- Clear method boundaries
- Literal endpoint paths
- Explicit parameter passing

------

## 10. What an LLM Should Ask Before Writing Code

Before generating code, confirm:

1. What exact vendor endpoint does this represent?
2. Should this return a typed model or raw dict/list?
3. Is PATCH involved?
4. Is this behavior already handled in Transport or Session?
5. Does this add abstraction, or merely mirror the API?

If unsure — **do less, not more**.

------

## 11. Success Criteria for Generated Code

Code is considered correct if:

- It compiles
- It respects all architectural boundaries
- It preserves vendor semantics
- It introduces no hidden behavior
- It would not surprise a human reading the API docs

If it only “works” but violates these rules, it is incorrect.

------

**End of LLM Agent Guide**
````

## File: docs/CONTRIBUTING.md
````markdown
# CONTRIBUTING.md

## Contribution Guidelines

This document defines how contributions are proposed, developed, reviewed, and merged.

All contributors — human or LLM — are expected to follow these rules.

---

## 1. Contribution Philosophy

This project prioritizes:

- Architectural integrity over speed
- Predictable behavior over cleverness
- Explicit contracts over convenience
- Long-term maintainability over short-term wins

Contributions that violate architecture or patterns will be rejected, regardless of functionality.

---

## 2. Required Reading

Before contributing, **read and understand**:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

These documents define **non-negotiable constraints**.

---

## 3. Branching Model

### Long-Lived Branches

| Branch    | Purpose                              |
| --------- | ------------------------------------ |
| `main`    | Latest stable or tagged pre-release  |
| `develop` | Integration branch for upcoming work |

---

### Short-Lived Branch Types

#### Pre-Alpha Branches

pre-alpha/N

- Used only during Pre-Alpha phase
- Tagged as `0.0.0-pre-alpha.N`
- May be rebased or force-pushed
- Typically merged once, then deleted

---

#### Feature Branches

feature/

- Branched from `develop`
- Used for new functionality
- Must not be tagged
- Merged via pull request

---

#### Bugfix Branches

bugfix/

- Used for non-urgent fixes
- Branched from `develop` or release branches
- Merged back to origin branch

---

#### Release Branches

release/x.y.z

- Branched from `develop`
- Used to stabilize a version
- Tagged sequentially as:
  - `x.y.z-alpha`
  - `x.y.z-beta`
  - `x.y.z-rc.N`
  - `x.y.z`

---

#### Hotfix Branches

hotfix/x.y.z

- Branched from `main`
- Used for urgent production fixes
- Merged into both `main` and `develop`

---

## 4. Issue Hygiene

All non-trivial work must have an associated Issue.

Issues should include:

- Clear problem statement
- Scope definition
- Acceptance criteria
- References to architecture or patterns if applicable

Compliance work should be tracked via Issues, not long-lived branches.

---

## 5. Pull Request Expectations

Every PR must:

- Reference at least one Issue
- Describe **what** changed and **why**
- Confirm architectural compliance
- Avoid mixing unrelated changes

Large PRs should be split unless explicitly justified.

---

## 6. Commit Message Convention

Use the following format:

:

Allowed types:

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

Examples:

- `feat: add projects client with full endpoint coverage`
- `refactor: centralize PATCH handling in Transport`

---

## 7. Versioning Responsibilities

Contributors **must not**:

- Bump versions arbitrarily
- Create tags without approval
- Modify release metadata

Version changes occur only during:

- Release branch preparation
- Explicit release tasks

---

## 8. Testing Expectations

- New features require tests when feasible
- Pre-Alpha allows limited test coverage, but correctness is still expected
- API-breaking changes must be explicitly documented

---

## 9. LLM Contributions

LLM-assisted contributions are welcome, provided that:

- Output conforms to documented patterns
- Architecture constraints are respected
- Generated code is reviewed critically

LLMs should be guided using `code_agent.md`.

---

## 10. Enforcement

Maintainers may:

- Request revisions
- Reject PRs
- Roll back changes

Architectural violations take precedence over functionality.

---

## 11. Closing Statement

These rules exist to protect the project’s clarity, stability, and longevity.

Following them ensures that the library remains:

- Predictable
- Maintainable
- Trustworthy
````

## File: docs/DESIGN.md
````markdown
# DESIGN.md
## Design Constraints and Implementation Rules

This document defines the **design constraints** that govern how code in this repository must be written.

These constraints are **non-negotiable**.  
They exist to preserve architectural integrity, predictability, and long-term maintainability.

If a proposed change violates this document, it must be rejected or redesigned.

---

## 1. Design Goals

This project is designed to be:

- **Drop-in usable** in any Python environment
- **Mostly un-opinionated** about application structure
- **Explicit** rather than clever
- **Predictable** rather than magical
- **Vendor-aligned** with TeamDynamix Web API contracts

The library optimizes for:
- Correctness
- Transparency
- Ease of reasoning
- Low cognitive overhead for consumers

---

## 2. Separation of Concerns (Primary Constraint)

Every module has **exactly one reason to change**.

### Responsibility Boundaries

| Component                                   | Responsibility                                   |
| ------------------------------------------- | ------------------------------------------------ |
| `Config`                                    | Configuration parsing, defaults, validation      |
| `Session`                                   | Object composition, orchestration, public facade |
| `Transport`                                 | HTTP I/O, timeouts, PATCH normalization          |
| `Auth`                                      | Authentication strategy and token acquisition    |
| Client modules (`people`, `projects`, etc.) | Endpoint-to-method mapping                       |
| Models (`Person`, `Project`, etc.)          | Typed representations of API data                |

Crossing these boundaries is forbidden.

---

## 3. Constructors Must Be Side-Effect Free

### Rule
**No network calls in constructors.**

### Implications
- `Session()` must not authenticate
- `Auth()` must not fetch tokens
- `Config()` must not touch the filesystem except during `from_file()`

### Rationale
- Improves testability
- Prevents surprising side effects
- Enables lazy behavior

All side effects occur **only** when explicitly invoked (e.g., `Session.request()`).

---

## 4. Lazy Initialization Is Mandatory

Authentication, network access, and resource acquisition must be **lazy**.

### Example
```python
session = Session(config)
# No network activity yet

people = People(session)
people.search("user@example.com")  # Authentication occurs here if needed
```

### Benefits

- Faster startup
- Easier testing
- Better control for consumers

------

## 5. Single Transport Boundary

### Rule

**Only `Transport` may call `requests.\*`.**

### Forbidden

- Calling `requests.get/post/etc.` anywhere else
- Implementing retry/timeout logic outside Transport

### Allowed

- Client modules calling `session.request(...)`
- Transport transforming payloads (e.g., JSON Patch)

### Rationale

- Centralizes error handling
- Ensures consistent timeout behavior
- Simplifies mocking and testing

------

## 6. JSON Patch Handling Is Centralized

TeamDynamix PATCH endpoints require **RFC 6902 JSON Patch**.

### Rule

- Client modules may pass:
  - `dict[str, Any]`
  - `list[dict]`
  - `list[PatchPayload]`
- `Transport` is responsible for normalization

### Explicit Design Choice

Client modules must **not** implement PATCH logic themselves.

This avoids duplication and ensures consistency across modules.

------

## 7. Error Handling Philosophy

### Transport-Level Errors

- Non-2xx responses → `HttpError`
- Timeouts → `TdxTimeoutError`
- Request failures → `TdxRequestError`

### Client Modules

- Must **not** swallow exceptions
- Must **not** wrap exceptions unnecessarily
- Must rely on Transport behavior

### Rationale

- Errors should surface clearly
- Consumers decide how to handle failures
- Prevents hidden failures or silent corruption

------

## 8. Valid Empty Responses Are Not Errors

TeamDynamix frequently returns:

- `[]`
- `{}`
- `null`

### Rule

- `200 OK` with empty data is **valid**
- Client modules must treat empty results as legitimate

### Example

```python
people.search("does-not-exist")  # returns []
```

Do not raise exceptions for empty payloads unless the endpoint contract explicitly requires data.

------

## 9. Typed Models Are Minimal and Intentional

### Rule

- Only include fields that:
  - Are commonly used
  - Improve clarity
  - Provide real value

### Forbidden

- Exhaustive mirroring of API payloads
- Deep object graphs for rarely-used data

### Rationale

- Keeps models stable across API changes
- Reduces maintenance burden
- Encourages use of raw dicts for edge cases

Typed models are **helpers**, not authoritative schemas.

------

## 10. Client Modules Represent Vendor Endpoints

Each public method in a client module must map directly to **one vendor endpoint**.

### Allowed

- Thin helpers that reduce repetition
- Internal normalization helpers

### Forbidden

- High-level workflows
- Business logic
- Opinionated abstractions

This library is an **API client**, not an SDK framework.

------

## 11. Public API Surface Is Explicit

### Rule

Only explicitly exported symbols are public.

- Controlled via `__all__`
- No accidental exports
- No reliance on import side effects

Breaking changes to public API require:

- Version bump
- Documentation
- Explicit acknowledgment

------

## 12. Configuration Ergonomics

### Required

- `[tdx]`
- `[auth]`

### Optional

- `[logging]`
- `[http]`

Defaults must allow:

```python
Session("./config/config.ini")
```

to work without additional configuration.

------

## 13. Logging Philosophy

- INFO-level logs are visible by default
- Logs describe **what happened**, not **why**
- No logging of secrets or credentials
- Logging must never affect behavior

------

## 14. Extensibility Without Commitment

The design must allow future support for:

- Retries
- Rate limiting
- Backoff strategies
- Alternate transports

Without forcing them now.

This is achieved through:

- Composition
- Explicit boundaries
- Minimal assumptions

------

## 15. Design Enforcement

Any contribution must be evaluated against this document.

If code:

- Violates boundaries
- Introduces hidden behavior
- Adds unnecessary abstraction

It must be revised or rejected.

------

## Closing Statement

This design exists to make the library:

- Boring in the best way
- Easy to reason about
- Safe to embed anywhere
- Honest about what it does

Adhering to these constraints ensures long-term trust and usability.
````

## File: docs/PATTERNS.md
````markdown
# PATTERNS.md
## Programming & Architectural Patterns Used

This document describes the **specific patterns** used throughout the `teamdynamix-api` codebase.

It explains **what patterns are used**, **where they apply**, **why they were chosen**, and **how to implement them correctly**.

This document is prescriptive.

---

## 1. Composition Root Pattern

### Pattern
**Composition Root**

### Where
- `Session`

### Why
- Centralizes object wiring
- Prevents scattered instantiation
- Makes dependencies explicit

### How to Implement
- All infrastructure objects (`Config`, `Auth`, `Logger`, `Transport`) are created in `Session`
- Client modules receive only a `Session`
- No client module constructs infrastructure dependencies

---

## 2. Gateway / Adapter Pattern

### Pattern
**Gateway / Adapter**

### Where
- `Transport`

### Why
- Encapsulates external dependency (`requests`)
- Minimizes third-party surface area
- Enables uniform error handling

### How to Implement
- `Transport.request()` is the only place that calls `requests`
- Convert external exceptions into domain exceptions
- Normalize protocol quirks here (e.g., JSON Patch)

---

## 3. Lazy Initialization Pattern

### Pattern
**Lazy Initialization**

### Where
- Authentication flow in `Auth`

### Why
- Avoids side effects during construction
- Improves testability
- Allows configuration-only usage

### How to Implement
- Do not authenticate in constructors
- Fetch tokens on first authenticated request
- Cache tokens for reuse

---

## 4. Facade Pattern

### Pattern
**Facade**

### Where
- `Session`

### Why
- Simplifies client usage
- Shields callers from internal complexity
- Enables refactoring without breaking API

### How to Implement
- Expose minimal, stable methods:
  - `request()`
  - `log()`
  - `base_url`
- Do not expose internal infrastructure directly

---

## 5. Response-First Handling Pattern

### Pattern
**Response-First Processing**

### Where
- All client modules (People, Tickets, Projects, etc.)

### Why
- Preserves HTTP semantics
- Avoids type confusion
- Makes error boundaries explicit

### How to Implement
```python
resp = self.session.request(...)
data = resp.json()
```

Never assume `request()` returns JSON.

------

## 6. Endpoint-Representative Method Pattern

### Pattern

**Endpoint-Representative Methods**

### Where

- Client modules

### Why

- Keeps API surface predictable
- Mirrors vendor documentation
- Prevents abstraction creep

### How to Implement

- One public method per endpoint
- Method name reflects endpoint intent
- No “helper endpoints” unless strictly required

------

## 7. Selective Data Modeling Pattern

### Pattern

**Selective Dataclass Modeling**

### Where

- `Person`, `Ticket`, `Project`, etc.

### Why

- Avoids over-modeling
- Preserves flexibility
- Reduces maintenance burden

### How to Implement

- Use dataclasses only for high-value fields
- Accept raw dicts where appropriate
- Do not attempt schema completeness

------

## 8. Centralized Patch Transformation Pattern

### Pattern

**Centralized Transformation**

### Where

- `Transport` (PATCH handling)

### Why

- PATCH is cross-cutting
- Prevents duplication
- Ensures correctness

### How to Implement

- Detect `PATCH` method
- Convert dict payloads to JSON Patch
- Pass through list payloads unchanged

Client modules never build patch logic directly.

------

## 9. Fail-Fast Configuration Validation

### Pattern

**Fail-Fast at Boundaries**

### Where

- `Config`

### Why

- Prevents undefined runtime behavior
- Improves error clarity
- Keeps validation centralized

### How to Implement

- Validate required fields in `__post_init__`
- Allow defaults where reasonable
- Raise `ConfigError` only when required data is missing

------

## 10. Explicit Error Propagation Pattern

### Pattern

**Explicit Error Propagation**

### Where

- Entire codebase

### Why

- Silent failures are dangerous
- Automation requires certainty
- Debugging must be straightforward

### How to Implement

- Do not catch HTTP exceptions in client modules
- Do not swallow errors
- Let errors propagate naturally

------

## 11. Logging-as-Observation Pattern

### Pattern

**Logging as Observation, Not Control**

### Where

- All layers

### Why

- Prevents hidden dependencies
- Keeps logic deterministic

### How to Implement

- Log intent and context
- Never branch on logs
- Default to INFO visibility

------

## 12. Pattern Summary

The patterns used in this project emphasize:

- Clarity over cleverness
- Boundaries over convenience
- Explicitness over magic
- Vendor faithfulness over abstraction

If a proposed change violates one of these patterns, it must be reconsidered or explicitly justified.
````

## File: docs/RELEASING.md
````markdown
# RELEASING.md
## Release Process Checklist

This document defines the **authoritative checklist** for preparing, validating, tagging, and publishing a new release of the TeamDynamix API Python client.

Every release — pre-alpha, alpha, beta, RC, or stable — must follow this process.

---

## 0. Preconditions

Before starting a release:

- All intended work for the release is complete
- All related Issues are closed or explicitly deferred
- The working tree is clean
- CI (if present) is passing
- The release scope is clearly defined

---

## 1. Version Planning

- [ ] Confirm the **target version** (e.g. `0.0.0-pre-alpha.11`, `0.1.0-alpha`)
- [ ] Confirm lifecycle phase (Pre-Alpha / Alpha / Beta / RC / Stable)
- [ ] Confirm compatibility expectations for this release
- [ ] Confirm whether this is:
  - Feature snapshot
  - Bugfix release
  - Architecture milestone

---

## 2. Documentation Updates (Required)

### Core Project Documents

These **must** be reviewed and updated as applicable:

- [ ] `VERSION.md`
  - Replace entirely with release-specific content
  - Describe what is unique to this version
- [ ] `CHANGELOG.md`
  - Add a new entry at the top
  - Accurately list all changes in this release
- [ ] `README.md`
  - Verify version string
  - Update status notes if lifecycle phase changed

### Architecture & Process Docs

Review for accuracy; update only if changes occurred:

- [ ] `ARCHITECTURE.md`
- [ ] `DESIGN.md`
- [ ] `PATTERNS.md`
- [ ] `CONTRIBUTING.md`
- [ ] `VERSIONING.md`
- [ ] `CODE_AGENT.md`
- [ ] `ABSTRACT.md`

> These documents should only change when the underlying rules or philosophy change.

---

## 3. Module-Level Documentation (Selective)

The following files live under `docs/teamdynamix/` and act as **module reference guides**.

Update **only** if the corresponding module changed:

- [ ] `accounts.md`
- [ ] `applications.md`
- [ ] `attributes.md`
- [ ] `auth.md`
- [ ] `config.md`
- [ ] `events.md`
- [ ] `exceptions.md`
- [ ] `functional_roles.md`
- [ ] `groups.md`
- [ ] `people.md`
- [ ] `projects.md`
- [ ] `service_catalog.md`
- [ ] `session.md`
- [ ] `tickets.md`
- [ ] `transport.md`

---

## 4. Code Review and Validation

- [ ] Verify no architecture violations were introduced
- [ ] Verify no direct `requests.*` calls outside Transport
- [ ] Verify constructors remain side-effect free
- [ ] Verify PATCH behavior is centralized in Transport
- [ ] Verify public API surface matches `__all__`
- [ ] Verify logging defaults behave as intended
- [ ] Verify config defaults allow minimal startup

---

## 5. Tests

- [ ] Run all existing tests
- [ ] Manually validate critical workflows if tests are limited
- [ ] Ensure test failures are either:
  - Fixed, or
  - Explicitly documented as known limitations

---

## 6. Version Metadata Updates

- [ ] Update version string in:
  - `src/teamdynamix/__init__.py`
- [ ] Verify version matches:
  - `VERSION.md`
  - `CHANGELOG.md`
- [ ] Ensure version string conforms to SemVer and project rules

---

## 7. Git Branch Preparation

### Pre-Alpha Releases

- [ ] Ensure work is on `pre-alpha/N` branch
- [ ] Ensure branch represents a **feature-complete snapshot**
- [ ] Merge `pre-alpha/N` → `main` (fast-forward preferred)
- [ ] Delete branch after merge (optional)

### Alpha and Later Releases

- [ ] Create or update `release/x.y.z` branch
- [ ] Freeze feature work
- [ ] Allow only fixes and documentation changes

---

## 8. Commit Hygiene

- [ ] Ensure commits are logically grouped
- [ ] Ensure commit messages follow project conventions
- [ ] Avoid mixing unrelated changes
- [ ] Squash commits if necessary for clarity

---

## 9. Tagging

- [ ] Create an **annotated Git tag** matching the version exactly
- [ ] Tag must point to the merge commit on the correct branch
- [ ] Tags are immutable once created

Examples:

```bash
git tag -a 0.0.0-pre-alpha.10 -m "Pre-Alpha 10: architecture-stabilized snapshot"
git push --tags
```

------

## 10. Release Publication (Optional but Recommended)

If using a platform with releases (GitHub/GitLab/Gitea):

-  Publish a release from the tag
-  Copy summary from `VERSION.md`
-  Link to `CHANGELOG.md`
-  Clearly mark pre-release status if applicable

------

## 11. Post-Release Cleanup

-  Close remaining Issues tied to the release
-  Update milestone status (if used)
-  Verify documentation links remain correct
-  Prepare next development branch if applicable

------

## 12. Final Verification

Before declaring the release complete:

-  Repository builds cleanly
-  Documentation accurately reflects reality
-  Version identifiers are consistent everywhere
-  No uncommitted changes remain

------

## Release Invariant

A release must be:

- Internally consistent
- Architecturally compliant
- Accurately documented
- Reproducible from the tagged commit

If any of these conditions are not met, **do not release**.

------

## Closing Note

Releases are **communication artifacts**, not just code snapshots.

This checklist exists to ensure that every release:

- Can be trusted
- Can be understood
- Can be built upon

Follow it exactly.
````

## File: docs/VERSIONING.md
````markdown
# VERSIONING.md
## Versioning Strategy and Naming Conventions

This project follows **Semantic Versioning 2.0.0**, with additional, explicitly-defined lifecycle phases to accurately communicate stability and intent during early development.

Versioning is used as a **communication tool**, not merely a technical artifact.

---

## 1. Semantic Versioning Baseline

All versions conform to:

MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Where:

- **MAJOR** — incompatible API changes
- **MINOR** — backward-compatible feature additions
- **PATCH** — backward-compatible bug fixes
- **PRERELEASE** — lifecycle or stability indicators
- **BUILD** — optional metadata (not used for precedence)

---

## 2. Lifecycle Phases

This project distinguishes **lifecycle phases** from **numeric progression**.

### 2.1 Pre-Alpha (Draft Phase)

#### Intent
Pre-Alpha represents exploratory, architecture-shaping drafts prior to formal stability guarantees.

#### Characteristics
- Architecture is being finalized
- Breaking changes are expected
- No API stability guarantees
- Versions represent **snapshots**, not incremental releases

#### Version Format

0.0.0-pre-alpha.N

Examples:
- `0.0.0-pre-alpha.1`
- `0.0.0-pre-alpha.10`

#### Rules
- `N` is a chronological draft counter
- No use of MINOR or PATCH
- Each Pre-Alpha version represents a **feature-complete draft for its scope**
- Drafts are immutable once tagged

---

### 2.2 Alpha Phase

#### Intent
Alpha indicates that **architecture is stable** and feature development proceeds within defined constraints.

#### First Alpha Release

0.1.0-alpha

#### Version Format

0.MINOR.0-alpha

Examples:
- `0.1.0-alpha`
- `0.2.0-alpha`

#### Rules
- MINOR increments reflect meaningful feature expansion
- PATCH remains `0`
- No numeric alpha sequencing (`alpha.1`, `alpha.2`) is used
- Alpha is a **phase descriptor**, not a counter

---

### 2.3 Beta Phase

#### Intent
Beta represents **feature completeness** and a shift to stabilization, validation, and refinement.

#### Version Format

0.MINOR.0-beta

Examples:
- `0.1.0-beta`
- `0.2.0-beta`

#### Rules
- No new features without explicit approval
- Focus on correctness, performance, and compatibility
- PATCH remains `0`

---

### 2.4 Release Candidates (RC)

#### Intent
Release Candidates are production-grade builds intended for final validation.

#### Version Format

MAJOR.MINOR.PATCH-rc.N

Examples:
- `1.0.0-rc.1`
- `1.0.1-rc.2`

#### Use Cases
- Final QA
- Security review
- Integration validation
- Controlled production testing

---

### 2.5 General Availability (Stable)

#### Intent
Stable releases are fully validated and production-ready.

#### Version Format

MAJOR.MINOR.PATCH

Examples:
- `1.0.0`
- `1.1.2`

---

## 3. Version Authority

- Versions are set **only** during release preparation
- Contributors do not modify version numbers unless explicitly tasked
- Version changes are always accompanied by:
  - Release notes
  - Changelog updates
  - Tagged commits

---

## 4. Version Guarantees

| Phase       | Backward Compatibility | Breaking Changes |
| ----------- | ---------------------- | ---------------- |
| Pre-Alpha   | None                   | Allowed          |
| Alpha       | Best-effort            | Discouraged      |
| Beta        | Expected               | Strongly limited |
| RC / Stable | Required               | Only via MAJOR   |

---

## 5. Summary

This versioning strategy:

- Strictly complies with SemVer 2.0.0
- Avoids false precision during early development
- Communicates stability clearly
- Scales cleanly from experimentation to production
````

## File: src/teamdynamix/accounts.py
````python
# =====================================================================
# FILE: src/teamdynamix/accounts.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _first_or_none(data: Any) -> Optional[Dict[str, Any]]:
    """
    TDX endpoints sometimes return:
      - object (dict)
      - list[dict]
      - empty list []
    Normalize to first dict or None.
    """
    if data is None:
        return None
    if isinstance(data, list):
        if not data:
            return None
        first = data[0]
        return first if isinstance(first, dict) else None
    return data if isinstance(data, dict) else None


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Account:
    """
    Minimal Account DTO. Keep intentionally small; use Accounts.get_raw(...) for full dict.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    IsActive: Optional[bool] = None
    ParentID: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Account":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            IsActive=data.get("IsActive"),
            ParentID=data.get("ParentID") or data.get("ParentId"),
        )


class Accounts:
    """
    Accounts client.

    Endpoint-representative methods only (minimal helpers):
      - GET  /api/accounts/{id}
      - POST /api/accounts/search
      - GET  /api/accounts
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/accounts"

    def get_raw(self, account_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/accounts/{id}
        Returns raw dict or None (if API returns empty/None).
        """
        self.session.log(f"Accounts.get_raw: id={account_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(account_id)}")
        return _first_or_none(resp.json())

    def get(self, account_id: int) -> Optional[Account]:
        """
        GET /api/accounts/{id}
        Returns typed Account or None.
        """
        raw = self.get_raw(account_id)
        return Account.from_dict(raw) if raw is not None else None

    def search(self, search_payload: Dict[str, Any]) -> List[Account]:
        """
        POST /api/accounts/search
        Returns [] when no results (valid).
        """
        self.session.log("Accounts.search")
        resp = self.session.request("POST", f"{self._base_path}/search", json=search_payload)
        rows = resp.json() or []
        return [Account.from_dict(x) for x in rows if isinstance(x, dict)]

    def list_all(self, *, is_active: Optional[bool] = None) -> List[Account]:
        """
        GET /api/accounts
        Optional query param: isActive=true|false (if supported by tenant; harmless otherwise)

        Returns [] when no results (valid).
        """
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()

        self.session.log(f"Accounts.list_all: params={params}")
        resp = self.session.request("GET", self._base_path, params=params if params else None)
        rows = _as_list_of_dicts(resp.json())
        return [Account.from_dict(x) for x in rows]
````

## File: src/teamdynamix/applications.py
````python
# =====================================================================
# FILE: src/teamdynamix/applications.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Application:
    """
    Minimal Application DTO. Keep intentionally small; use Applications.list_raw() for full dicts.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    SystemClass: Optional[str] = None
    IsActive: Optional[bool] = None
    IsDefault: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Application":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            SystemClass=data.get("SystemClass"),
            IsActive=data.get("IsActive"),
            IsDefault=data.get("IsDefault"),
        )


class Applications:
    """
    Applications client.

    TeamDynamix commonly exposes application metadata endpoints under /api/applications.
    This module is intentionally minimal and endpoint-representative.

    Methods:
      - GET /api/applications
      - GET /api/applications/{id}   (if supported by tenant)
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/applications"

    def list_raw(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        GET /api/applications
        Returns raw list[dict]. [] is valid.
        """
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()

        self.session.log(f"Applications.list_raw: params={params}")
        resp = self.session.request("GET", self._base_path, params=params if params else None)
        return _as_list_of_dicts(resp.json())

    def list(self, *, is_active: Optional[bool] = None) -> List[Application]:
        """
        GET /api/applications
        Returns typed Application list.
        """
        return [Application.from_dict(x) for x in self.list_raw(is_active=is_active)]

    def get_raw(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/applications/{id}
        Some tenants may not support this. If unsupported, it will raise HttpError.
        """
        self.session.log(f"Applications.get_raw: id={app_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(app_id)}")
        data = resp.json()
        return data if isinstance(data, dict) else None

    def get(self, app_id: int) -> Optional[Application]:
        """
        GET /api/applications/{id}
        Returns typed Application or None if API returns non-dict/empty.
        """
        raw = self.get_raw(app_id)
        return Application.from_dict(raw) if raw is not None else None
````

## File: src/teamdynamix/attributes.py
````python
# =====================================================================
# FILE: src/teamdynamix/attributes.py
# =====================================================================
"""
Client for the TeamDynamix *Attributes* API surface.

This module preserves the legacy listing endpoints and adds parity with the
Postman Attributes folder for:

- Attribute Choices sub-resource:
    GET    /api/attributes/{id}/choices
    POST   /api/attributes/{id}/choices?copyFromChoiceId=
    PUT    /api/attributes/{id}/choices/{choiceId}
    DELETE /api/attributes/{id}/choices/{choiceId}

- Custom Attributes lookup:
    GET /api/attributes/custom?componentId=&associatedTypeId=&appId=

Patterns:
- Client modules receive a Session and call session.request(...)
- Response-first: resp = session.request(...); data = resp.json()
- Raw methods return dict/list[dict]; typed wrappers return DTOs
- Empty responses are valid and must not throw
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


# -------------------------------------------------------------------
# Response normalization helpers (consistent with pre-alpha10 style)
# -------------------------------------------------------------------
def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize an API response into list[dict].

    Rules:
      - None / [] / {} -> []
      - dict -> [dict]
      - list -> dict entries only
      - anything else -> []
    """
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _as_dict(data: Any) -> Optional[Dict[str, Any]]:
    """
    Normalize an API response into dict | None.

    Rules:
      - None / {} -> None
      - dict -> dict
      - anything else -> None
    """
    if not data:
        return None
    return data if isinstance(data, dict) else None


# -------------------------------------------------------------------
# DTOs (selective / lightweight)
# -------------------------------------------------------------------
@dataclass(slots=True)
class Attribute:
    """
    Minimal Attribute DTO – intentionally lean.

    Keep fields small and stable; callers can use raw methods for full payloads.
    """

    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None
    IsDefault: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attribute":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
            IsDefault=data.get("IsDefault"),
        )


@dataclass(slots=True)
class AttributeChoice:
    """
    DTO representing an Attribute Choice (selectable options for an Attribute).

    Fields align with the Postman/OpenAPI schema:
      ID, Name, IsActive, DateCreated, DateModified, Order
    """

    ID: Optional[int] = None
    Name: Optional[str] = None
    IsActive: Optional[bool] = None
    DateCreated: Optional[str] = None
    DateModified: Optional[str] = None
    Order: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AttributeChoice":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            IsActive=data.get("IsActive"),
            DateCreated=data.get("DateCreated"),
            DateModified=data.get("DateModified"),
            Order=data.get("Order"),
        )


# -------------------------------------------------------------------
# Client
# -------------------------------------------------------------------
class Attributes:
    """
    Attributes client.

    Legacy list endpoints preserved:
      - GET /api/applications/{appId}/attributes/{component}
      - GET /api/attributes/{component}
      - GET /api/attributes

    Added endpoints (Postman parity):
      - GET    /api/attributes/{id}/choices
      - POST   /api/attributes/{id}/choices?copyFromChoiceId=
      - PUT    /api/attributes/{id}/choices/{choiceId}
      - DELETE /api/attributes/{id}/choices/{choiceId}
      - GET    /api/attributes/custom?componentId=&associatedTypeId=&appId=
    """

    _base_path = "/api/attributes"

    def __init__(self, session: Session):
        self.session = session

    # -----------------------------------------------------------------
    # Legacy “Attributes” listing helpers (preserve names/behavior)
    # -----------------------------------------------------------------
    def list_for_application_component_raw(self, app_id: int, component: str) -> List[Dict[str, Any]]:
        """
        GET /api/applications/{appId}/attributes/{component}
        Returns raw list[dict] (possibly empty, valid).
        """
        component = component.strip().strip("/")
        path = f"/api/applications/{int(app_id)}/attributes/{component}"
        self.session.log(f"Attributes.list_for_application_component_raw: app_id={app_id}, component={component}")
        resp = self.session.request("GET", path)
        return _as_list_of_dicts(resp.json())

    def list_for_application_component(self, app_id: int, component: str) -> List[Attribute]:
        """
        GET /api/applications/{appId}/attributes/{component}
        Returns typed Attribute list (possibly empty, valid).
        """
        return [Attribute.from_dict(x) for x in self.list_for_application_component_raw(app_id, component)]

    def list_for_component_raw(self, component: str) -> List[Dict[str, Any]]:
        """
        GET /api/attributes/{component}
        Returns raw list[dict] (possibly empty, valid).
        """
        component = component.strip().strip("/")
        path = f"{self._base_path}/{component}"
        self.session.log(f"Attributes.list_for_component_raw: component={component}")
        resp = self.session.request("GET", path)
        return _as_list_of_dicts(resp.json())

    def list_for_component(self, component: str) -> List[Attribute]:
        """
        GET /api/attributes/{component}
        Returns typed Attribute list (possibly empty, valid).
        """
        return [Attribute.from_dict(x) for x in self.list_for_component_raw(component)]

    def list_all_raw(self) -> List[Dict[str, Any]]:
        """
        GET /api/attributes
        Returns raw list[dict] (possibly empty, valid).
        """
        self.session.log("Attributes.list_all_raw")
        resp = self.session.request("GET", self._base_path)
        return _as_list_of_dicts(resp.json())

    def list_all(self) -> List[Attribute]:
        """
        GET /api/attributes
        Returns typed Attribute list (possibly empty, valid).
        """
        return [Attribute.from_dict(x) for x in self.list_all_raw()]

    # -----------------------------------------------------------------
    # Attribute Choices (Postman parity)
    # -----------------------------------------------------------------
    def list_choices_raw(self, attribute_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/attributes/{id}/choices
        Returns raw list[dict] (possibly empty, valid).
        """
        self.session.log(f"Attributes.list_choices_raw: attribute_id={attribute_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(attribute_id)}/choices")
        return _as_list_of_dicts(resp.json())

    def list_choices(self, attribute_id: int) -> List[AttributeChoice]:
        """
        GET /api/attributes/{id}/choices
        Returns typed AttributeChoice list (possibly empty, valid).
        """
        return [AttributeChoice.from_dict(x) for x in self.list_choices_raw(attribute_id)]

    def add_choice_raw(
        self,
        attribute_id: int,
        choice_payload: Dict[str, Any],
        *,
        copy_from_choice_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        POST /api/attributes/{id}/choices?copyFromChoiceId=

        Parameters
        ----------
        choice_payload:
            Raw payload dict per TDX schema (typically includes Name, IsActive, Order; ID may be blank).
        copy_from_choice_id:
            Optional query param to clone from an existing choice.

        Returns
        -------
        Dict[str, Any]
            Raw created choice dict (or {} if API returns non-dict/empty).
        """
        params: Dict[str, Any] = {}
        if copy_from_choice_id is not None:
            params["copyFromChoiceId"] = str(int(copy_from_choice_id))

        self.session.log(f"Attributes.add_choice_raw: attribute_id={attribute_id}, params={params}")
        resp = self.session.request(
            "POST",
            f"{self._base_path}/{int(attribute_id)}/choices",
            params=params if params else None,
            json=choice_payload,
        )
        return _as_dict(resp.json()) or {}

    def add_choice(
        self,
        attribute_id: int,
        choice_payload: Dict[str, Any],
        *,
        copy_from_choice_id: Optional[int] = None,
    ) -> AttributeChoice:
        """
        POST /api/attributes/{id}/choices?copyFromChoiceId=
        Returns typed AttributeChoice.
        """
        raw = self.add_choice_raw(attribute_id, choice_payload, copy_from_choice_id=copy_from_choice_id)
        return AttributeChoice.from_dict(raw)

    def edit_choice_raw(self, attribute_id: int, choice_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        PUT /api/attributes/{id}/choices/{choiceId}
        Returns raw updated choice dict (or {} if API returns non-dict/empty).
        """
        self.session.log(f"Attributes.edit_choice_raw: attribute_id={attribute_id}, choice_id={choice_id}")
        resp = self.session.request(
            "PUT",
            f"{self._base_path}/{int(attribute_id)}/choices/{int(choice_id)}",
            json=payload,
        )
        return _as_dict(resp.json()) or {}

    def edit_choice(self, attribute_id: int, choice_id: int, payload: Dict[str, Any]) -> AttributeChoice:
        """
        PUT /api/attributes/{id}/choices/{choiceId}
        Returns typed AttributeChoice.
        """
        raw = self.edit_choice_raw(attribute_id, choice_id, payload)
        return AttributeChoice.from_dict(raw)

    def delete_choice_raw(self, attribute_id: int, choice_id: int) -> bool:
        """
        DELETE /api/attributes/{id}/choices/{choiceId}
        Returns True on success.
        """
        self.session.log(f"Attributes.delete_choice_raw: attribute_id={attribute_id}, choice_id={choice_id}")
        self.session.request("DELETE", f"{self._base_path}/{int(attribute_id)}/choices/{int(choice_id)}")
        return True

    def delete_choice(self, attribute_id: int, choice_id: int) -> bool:
        """
        DELETE /api/attributes/{id}/choices/{choiceId}
        Returns True on success.
        """
        return self.delete_choice_raw(attribute_id, choice_id)

    # -----------------------------------------------------------------
    # Custom Attributes (Postman parity)
    # -----------------------------------------------------------------
    def list_custom_raw(
        self,
        *,
        component_id: Optional[int] = None,
        associated_type_id: Optional[int] = None,
        app_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        GET /api/attributes/custom?componentId=&associatedTypeId=&appId=

        All query params are optional; omitted params are not sent.
        Returns raw list[dict] (possibly empty, valid).
        """
        params: Dict[str, Any] = {}
        if component_id is not None:
            params["componentId"] = str(int(component_id))
        if associated_type_id is not None:
            params["associatedTypeId"] = str(int(associated_type_id))
        if app_id is not None:
            params["appId"] = str(int(app_id))

        self.session.log(f"Attributes.list_custom_raw: params={params}")
        resp = self.session.request("GET", f"{self._base_path}/custom", params=params if params else None)
        return _as_list_of_dicts(resp.json())

    def list_custom(
        self,
        *,
        component_id: Optional[int] = None,
        associated_type_id: Optional[int] = None,
        app_id: Optional[int] = None,
    ) -> List[Attribute]:
        """
        GET /api/attributes/custom?componentId=&associatedTypeId=&appId=
        Returns typed Attribute list (possibly empty, valid).
        """
        return [
            Attribute.from_dict(x)
            for x in self.list_custom_raw(
                component_id=component_id,
                associated_type_id=associated_type_id,
                app_id=app_id,
            )
        ]

    # Back-compat / symmetry aliases (optional but harmless)
    get_custom_by_component_raw = list_custom_raw
    get_custom_by_component = list_custom
    list_custom_by_component_raw = list_custom_raw
    list_custom_by_component = list_custom
````

## File: src/teamdynamix/auth.py
````python
# =====================================================================
# FILE: src/teamdynamix/auth.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import threading

from .config import Config
from .exceptions import AuthError
from .transport import Transport


@dataclass(slots=True)
class Auth:
    """
    Auth is responsible for:
    - determining auth mode (admin vs user) from validated Config
    - making the auth call (via Transport)
    - caching the token
    """
    config: Config
    logger: Any          # Logger-like
    transport: Transport

    _token: Optional[str] = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def _auth_url(self) -> str:
        if self.config.auth_mode == "admin":
            return f"{self.config.base_url}/api/auth/loginadmin"
        return f"{self.config.base_url}/api/auth/login"

    def _payload(self) -> Dict[str, str]:
        if self.config.auth_mode == "admin":
            # Config validation guarantees these exist
            return {"BEID": self.config.beid or "", "WebServicesKey": self.config.webserviceskey or ""}
        return {"username": self.config.username or "", "password": self.config.password or ""}

    def authenticate(self) -> str:
        """
        Forces a network authentication and returns a token (does not cache unless caller sets it).
        """
        url = self._auth_url()
        headers = {"Content-Type": "application/json; charset=utf-8"}
        payload = self._payload()

        self.logger.log(f"Auth.authenticate: mode={self.config.auth_mode}\n")
        resp = self.transport.request("POST", url, headers=headers, json=payload)
        token = (resp.text or "").strip()
        if not token:
            raise AuthError("Empty token received from authentication endpoint.")
        return token

    def get_token(self, *, force_refresh: bool = False) -> str:
        """
        Returns cached token. If missing or force_refresh=True, authenticates.
        """
        with self._lock:
            if self._token is None or force_refresh:
                self._token = self.authenticate()
            return self._token
````

## File: src/teamdynamix/config.py
````python
# =====================================================================
# FILE: src/teamdynamix/config.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import configparser
from typing import Optional, Literal

from .exceptions import ConfigError

AuthMode = Literal["admin", "user"]


def _as_bool(value: str | None, default: bool) -> bool:
    v = (value or "").strip().lower()
    if v == "":
        return default
    if v in ("1", "true", "yes", "y", "on"):
        return True
    if v in ("0", "false", "no", "n", "off"):
        return False
    raise ConfigError(f"Invalid boolean value: {value!r}")


def _as_int(value: str | None, default: int) -> int:
    v = (value or "").strip()
    if v == "":
        return default
    try:
        return int(v)
    except ValueError as e:
        raise ConfigError(f"Invalid integer value: {value!r}") from e


@dataclass(frozen=True, slots=True)
class Config:
    # ---- Core TDX
    tenant: str
    environment: str
    base_url_override: Optional[str] = None

    # ---- Auth
    auth_mode: AuthMode = "admin"
    beid: Optional[str] = None
    webserviceskey: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    # ---- Logging (optional)
    log_dir: str = "./logs"
    log_level: str = "INFO"      # ← CHANGED DEFAULT
    log_console: bool = True

    # ---- HTTP (optional)
    default_timeout_seconds: int = 10   # 0 disables

    def __post_init__(self) -> None:
        # Validate core
        if not self.tenant or not self.tenant.strip():
            raise ConfigError("Missing required setting: [tdx].tenant")
        if not self.environment or not self.environment.strip():
            raise ConfigError("Missing required setting: [tdx].environment")

        mode = (self.auth_mode or "").strip().lower()
        if mode not in ("admin", "user"):
            raise ConfigError("Invalid [auth].mode. Expected 'admin' or 'user'.")

        # Validate creds based on mode
        if mode == "admin":
            if not (self.beid and self.beid.strip()) or not (self.webserviceskey and self.webserviceskey.strip()):
                raise ConfigError("Auth mode 'admin' requires [auth].beid and [auth].webserviceskey.")
        else:
            if not (self.username and self.username.strip()) or not (self.password and self.password.strip()):
                raise ConfigError("Auth mode 'user' requires [auth].username and [auth].password.")

        # Validate timeout semantics
        if self.default_timeout_seconds < 0:
            raise ConfigError("[http].default_timeout_seconds must be >= 0 (0 disables).")

        # Validate log_dir is at least non-empty
        if not self.log_dir or not self.log_dir.strip():
            raise ConfigError("[logging].log_dir must be a non-empty path.")

    @property
    def base_url(self) -> str:
        if self.base_url_override and self.base_url_override.strip():
            return self.base_url_override.strip().rstrip("/")
        return f"https://{self.tenant.strip().rstrip('/')}/{self.environment.strip()}WebApi"

    @property
    def timeout(self) -> Optional[int]:
        return None if self.default_timeout_seconds == 0 else self.default_timeout_seconds

    @classmethod
    def from_file(cls, config_path: str | Path = "./config/config.ini") -> "Config":
        """
        Required:
          [tdx]
          [auth]

        Optional:
          [logging]
          [http]
        """
        path = Path(config_path)
        if not path.exists():
            raise ConfigError(f"Config file not found: {path}")

        parser = configparser.ConfigParser()
        parser.read(path)

        # ---- Required sections
        missing_required = [sec for sec in ("tdx", "auth") if sec not in parser]
        if missing_required:
            raise ConfigError(f"Missing required INI sections: {', '.join(missing_required)}")

        tdx = parser["tdx"]
        auth = parser["auth"]

        logging_sec = parser["logging"] if "logging" in parser else None
        http = parser["http"] if "http" in parser else None

        # ---- [tdx]
        tenant = (tdx.get("tenant", "") or "").strip()
        environment = (tdx.get("environment", "") or "").strip()
        base_url_override = (tdx.get("base_url", "") or "").strip() or None

        # ---- [auth]
        auth_mode: AuthMode = (auth.get("mode", "admin") or "admin").strip().lower()  # type: ignore[assignment]
        beid = (auth.get("beid", "") or "").strip() or None
        webserviceskey = (auth.get("webserviceskey", "") or "").strip() or None
        username = (auth.get("username", "") or "").strip() or None
        password = (auth.get("password", "") or "").strip() or None

        # ---- [logging] (optional)
        log_dir = "./logs"
        log_level = "INFO"   # ← CHANGED DEFAULT
        log_console = True
        if logging_sec is not None:
            log_dir = (logging_sec.get("log_dir", "./logs") or "./logs").strip()
            log_level = (logging_sec.get("level", "INFO") or "INFO").strip().upper()
            log_console = _as_bool(logging_sec.get("console", "true"), default=True)

        # ---- [http] (optional)
        default_timeout_seconds = 10
        if http is not None:
            default_timeout_seconds = _as_int(http.get("default_timeout_seconds", "10"), default=10)

        return cls(
            tenant=tenant,
            environment=environment,
            base_url_override=base_url_override,
            auth_mode=auth_mode,  # type: ignore[arg-type]
            beid=beid,
            webserviceskey=webserviceskey,
            username=username,
            password=password,
            log_dir=log_dir,
            log_level=log_level,
            log_console=log_console,
            default_timeout_seconds=default_timeout_seconds,
        )
````

## File: src/teamdynamix/event.py
````python
# =====================================================================
# FILE: src/teamdynamix/event.py
# (kept close to refactor style; compatible with Logger above)
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any


@dataclass(slots=True)
class Event:
    message: str
    level: int = 20
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        ts = self.created_at.isoformat()
        ctx = f" | context={self.context}" if self.context else ""
        return f"{ts} [{self.level}] {self.message}{ctx}\n"
````

## File: src/teamdynamix/exceptions.py
````python
# =====================================================================
# FILE: src/teamdynamix/exceptions.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


class TdxError(Exception):
    """Base exception for the TeamDynamix client."""


class ConfigError(TdxError):
    """Raised when configuration is missing or invalid."""


class AuthError(TdxError):
    """Raised when authentication fails or credentials are missing."""


@dataclass(slots=True)
class HttpError(TdxError):
    """Raised for HTTP responses with non-success status codes."""
    status_code: int
    method: str
    url: str
    message: str = ""
    response_text: str = ""


class TdxTimeoutError(TdxError):
    """Raised when a request times out."""


class TdxRequestError(TdxError):
    """Raised for non-timeout transport errors (connection errors, etc.)."""
````

## File: src/teamdynamix/functional_roles.py
````python
# =====================================================================
# FILE: src/teamdynamix/functional_roles.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


@dataclass(slots=True)
class FunctionalRole:
    """
    Minimal Functional Role DTO based on the Postman export.

    Fields observed in the Postman body examples:
      ID, Name, CreatedDate, ModifiedDate, IsActive,
      NotifyOnAssignment, RequiresApproval, ManagerFullName, ManagerUID, ResourceCount
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    CreatedDate: Optional[str] = None
    ModifiedDate: Optional[str] = None
    IsActive: Optional[bool] = None
    NotifyOnAssignment: Optional[bool] = None
    RequiresApproval: Optional[bool] = None
    ManagerFullName: Optional[str] = None
    ManagerUID: Optional[str] = None  # Guid string
    ResourceCount: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionalRole":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            CreatedDate=data.get("CreatedDate"),
            ModifiedDate=data.get("ModifiedDate"),
            IsActive=data.get("IsActive"),
            NotifyOnAssignment=data.get("NotifyOnAssignment"),
            RequiresApproval=data.get("RequiresApproval"),
            ManagerFullName=data.get("ManagerFullName"),
            ManagerUID=data.get("ManagerUID"),
            ResourceCount=data.get("ResourceCount"),
        )


class FunctionalRoles:
    """
    Functional Roles API client (restricted to endpoints confirmed in your docs/Postman):

      POST /api/functionalroles              -> create()
      PUT  /api/functionalroles/{id}         -> edit()
      POST /api/functionalroles/search       -> search()

    Notes:
    - We intentionally keep this close to the vendor surface. No extra helper endpoints.
    - 200 OK with [] is treated as a valid “no results” outcome.
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/functionalroles"

    def create(self, payload: Dict[str, Any]) -> FunctionalRole:
        """
        POST /api/functionalroles

        Payload example fields (per Postman):
          Name, IsActive, NotifyOnAssignment, RequiresApproval, ManagerFullName, ManagerUID
        """
        self.session.log("FunctionalRoles.create")
        resp = self.session.request("POST", self._base_path, json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from FunctionalRoles.create (expected dict).")
        return FunctionalRole.from_dict(data)

    def edit(self, role_id: int, payload: Dict[str, Any]) -> FunctionalRole:
        """
        PUT /api/functionalroles/{id}

        Postman indicates the body includes the full role object (including ID).
        We do not force the ID into the payload here, but you can include it if required
        by your tenant’s validation rules.
        """
        self.session.log(f"FunctionalRoles.edit: id={role_id}")
        resp = self.session.request("PUT", f"{self._base_path}/{int(role_id)}", json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from FunctionalRoles.edit (expected dict).")
        return FunctionalRole.from_dict(data)

    def search(self, search_payload: Dict[str, Any]) -> List[FunctionalRole]:
        """
        POST /api/functionalroles/search

        Postman search body example fields:
          Name, ManagerUID, MaxResults, IsActive, ReturnItemCounts
        """
        self.session.log("FunctionalRoles.search")
        resp = self.session.request("POST", f"{self._base_path}/search", json=search_payload)
        data: Any = resp.json()

        if not data:
            return []
        if isinstance(data, list):
            return [FunctionalRole.from_dict(x) for x in data if isinstance(x, dict)]
        if isinstance(data, dict):
            return [FunctionalRole.from_dict(data)]
        return []
````

## File: src/teamdynamix/groups.py
````python
# =====================================================================
# FILE: src/teamdynamix/groups.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _first_or_none(data: Any) -> Optional[Dict[str, Any]]:
    """
    Normalize:
      - dict -> dict
      - list[dict] -> first dict
      - []/None -> None
    """
    if data is None:
        return None
    if isinstance(data, list):
        if not data:
            return None
        first = data[0]
        return first if isinstance(first, dict) else None
    return data if isinstance(data, dict) else None


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Group:
    """
    Minimal Group DTO. Keep small; use Groups.get_raw(...) if you need full dict fields.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Group":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
        )


class Groups:
    """
    Groups client (endpoint-representative, minimal helpers).

    Common TeamDynamix WebAPI endpoints:
      - GET  /api/groups/{id}
      - POST /api/groups/search
      - GET  /api/groups
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/groups"

    def get_raw(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/groups/{id}
        Returns raw dict or None when API returns empty/None.
        """
        self.session.log(f"Groups.get_raw: id={group_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(group_id)}")
        return _first_or_none(resp.json())

    def get(self, group_id: int) -> Optional[Group]:
        """
        GET /api/groups/{id}
        Returns typed Group or None.
        """
        raw = self.get_raw(group_id)
        return Group.from_dict(raw) if raw is not None else None

    def search_raw(self, search_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        POST /api/groups/search
        Returns [] when no matches (valid).
        """
        self.session.log("Groups.search_raw")
        resp = self.session.request("POST", f"{self._base_path}/search", json=search_payload)
        return _as_list_of_dicts(resp.json())

    def search(self, search_payload: Dict[str, Any]) -> List[Group]:
        """
        POST /api/groups/search
        Returns typed list (possibly empty []).
        """
        return [Group.from_dict(x) for x in self.search_raw(search_payload)]

    def list_all_raw(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        GET /api/groups
        Optional query param: isActive=true|false (if supported by tenant; harmless otherwise)
        """
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()

        self.session.log(f"Groups.list_all_raw: params={params}")
        resp = self.session.request("GET", self._base_path, params=params if params else None)
        return _as_list_of_dicts(resp.json())

    def list_all(self, *, is_active: Optional[bool] = None) -> List[Group]:
        """
        GET /api/groups
        Returns typed list (possibly empty []).
        """
        return [Group.from_dict(x) for x in self.list_all_raw(is_active=is_active)]
````

## File: src/teamdynamix/logger.py
````python
# =====================================================================
# FILE: src/teamdynamix/logger.py
# =====================================================================
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import threading
import time

from .event import Event


_LEVELS = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "WARN": 30,
    "INFO": 20,
    "DEBUG": 10,
}


class Logger:
    """
    Minimal logger:
    - Keeps an in-memory list of Event objects
    - Writes to a timestamped file under log_dir
    - Prints to console (optional)
    - Default level behavior: ERROR (catches errors/exceptions, ignores warnings)
    """
    def __init__(
        self,
        log_dir: str | Path = "./logs",
        level: str = "ERROR",
        console: bool = True,
        name_prefix: str = "log",
    ):
        self._lock = threading.RLock()
        self.events: List[Event] = []

        self.level_name = (level or "ERROR").strip().upper()
        self.level = _LEVELS.get(self.level_name, 40)

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        ts = time.strftime("%Y%m%d%H%M%S")
        self.log_file = self.log_dir / f"{name_prefix}-{ts}.txt"
        self.console = bool(console)

    def log(self, message: str, level: int | None = None, context: Optional[dict] = None) -> None:
        lvl = self.level if level is None else int(level)

        # Filter: only record if lvl >= configured level
        if lvl < self.level:
            return

        event = Event(message=message, level=lvl, context=context)
        with self._lock:
            self.events.append(event)

        # Console behavior requirement: print(event, end='')
        if self.console:
            print(event, end="")

        # File append
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(str(event))

    def clear_events(self) -> None:
        with self._lock:
            self.events.clear()
````

## File: src/teamdynamix/people.py
````python
# =====================================================================
# FILE: src/teamdynamix/people.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from .session import Session


@dataclass(slots=True)
class Person:
    """
    Minimal, commonly-used subset of a TeamDynamix Person record.

    We intentionally do NOT model the full People.get() payload (it is large and nested).
    Use People.get_raw(...) when you need the full dict.
    """
    UID: Optional[str] = None
    ReferenceID: Optional[int] = None
    BEID: Optional[str] = None

    IsActive: Optional[bool] = None
    IsEmployee: Optional[bool] = None

    UserName: Optional[str] = None
    FullName: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    PrimaryEmail: Optional[str] = None

    SecurityRoleName: Optional[str] = None
    DefaultAccountID: Optional[int] = None
    DefaultAccountName: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        # UID appears as UID/Id/id depending on endpoint shape
        uid = data.get("UID") or data.get("Id") or data.get("id")

        return cls(
            UID=uid,
            ReferenceID=data.get("ReferenceID"),
            BEID=data.get("BEID"),
            IsActive=data.get("IsActive"),
            IsEmployee=data.get("IsEmployee"),
            UserName=data.get("UserName"),
            FullName=data.get("FullName"),
            FirstName=data.get("FirstName"),
            LastName=data.get("LastName"),
            PrimaryEmail=data.get("PrimaryEmail"),
            SecurityRoleName=data.get("SecurityRoleName"),
            DefaultAccountID=data.get("DefaultAccountID"),
            DefaultAccountName=data.get("DefaultAccountName"),
        )


class People:
    """
    People API client.

    Design rules (per the new architecture):
    - No direct requests.* usage here. All calls go through Session.request().
    - No manual header/token handling here. Session injects auth headers.
    - 200 OK with [] is valid and should return []/None as appropriate.
    - Prefer endpoint-representative methods; avoid non-endpoint "helper" methods unless required.
    """
    def __init__(self, session: Session):
        self.session = session
        self._base_path = "/api/people"

    # --- Core endpoints --------------------------------------------------

    def get_raw(self, uid: Union[str, UUID]) -> Optional[Dict[str, Any]]:
        """
        GET /api/people/{uid}

        Returns the raw dict payload (or None when API returns empty/None).
        This is the escape hatch for large/nested fields.
        """
        self.session.log(f"People.get_raw: uid={uid}")
        resp = self.session.request("GET", f"{self._base_path}/{uid}")
        data: Any = resp.json()

        if not data:
            return None
        if isinstance(data, list):
            item = data[0] if data else None
            return item if isinstance(item, dict) else None
        return data if isinstance(data, dict) else None

    def get(self, uid: Union[str, UUID]) -> Optional[Person]:
        """
        GET /api/people/{uid}

        Returns:
        - Person if found
        - None if API returns empty/None (valid behavior in some TDX responses)
        """
        raw = self.get_raw(uid)
        return Person.from_dict(raw) if raw is not None else None

    def search(
        self,
        search_text: str,
        *,
        max_results: Optional[int] = None,
        is_active: Optional[bool] = None,
        is_employee: Optional[bool] = None,
        is_client: Optional[bool] = None,
        has_login: Optional[bool] = None,
    ) -> List[Person]:
        """
        POST /api/people/search

        Returns [] when no results (valid).
        """
        payload: Dict[str, Any] = {"SearchText": search_text}

        # Include optional filters only if explicitly provided
        if max_results is not None:
            payload["MaxResults"] = max_results
        if is_active is not None:
            payload["IsActive"] = is_active
        if is_employee is not None:
            payload["IsEmployee"] = is_employee
        if is_client is not None:
            payload["IsClient"] = is_client
        if has_login is not None:
            payload["HasLogin"] = has_login

        self.session.log(f"People.search: {payload}")
        resp = self.session.request("POST", f"{self._base_path}/search", json=payload)
        data: Any = resp.json()

        if not data:
            return []
        if isinstance(data, list):
            return [Person.from_dict(item) for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [Person.from_dict(data)]
        return []

    def user_list(self, is_active: bool = True) -> List[Person]:
        """
        GET /api/people/userlist?isActive=true|false

        Returns [] when no results (valid).
        """
        params = {"isActive": str(is_active).lower()}
        self.session.log(f"People.user_list: params={params}")
        resp = self.session.request("GET", f"{self._base_path}/userlist", params=params)
        data: Any = resp.json()

        if not data:
            return []
        if isinstance(data, list):
            return [Person.from_dict(item) for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [Person.from_dict(data)]
        return []

    def create(self, person_payload: Dict[str, Any]) -> Person:
        """
        POST /api/people

        Note: We intentionally accept dict payloads to avoid prematurely modeling
        the full TDX person schema.
        """
        self.session.log("People.create")
        resp = self.session.request("POST", self._base_path, json=person_payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from People.create (expected dict).")
        return Person.from_dict(data)

    def update(self, uid: Union[str, UUID], updates: Dict[str, Any]) -> bool:
        """
        PATCH /api/people/{uid}

        Returns True on success.
        """
        self.session.log(f"People.update: uid={uid}, updates={updates}")
        self.session.request("PATCH", f"{self._base_path}/{uid}", json=updates)
        return True

    # --- Functional roles -------------------------------------------------

    def list_functional_roles(self, uid: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        GET /api/people/{uid}/functionalroles

        Returns [] when none (valid).
        """
        self.session.log(f"People.list_functional_roles: uid={uid}")
        resp = self.session.request("GET", f"{self._base_path}/{uid}/functionalroles")
        data: Any = resp.json()

        if not data:
            return []
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if isinstance(data, dict):
            return [data]
        return []

    def add_functional_role(self, uid: Union[str, UUID], role_id: int, is_primary: bool = False) -> bool:
        """
        PUT /api/people/{uid}/functionalroles/{role_id}?isPrimary=true|false

        Returns True on success.
        """
        params = {"isPrimary": str(is_primary).lower()}
        self.session.log(f"People.add_functional_role: uid={uid}, role_id={role_id}, params={params}")
        self.session.request("PUT", f"{self._base_path}/{uid}/functionalroles/{role_id}", params=params)
        return True

    def remove_functional_role(self, uid: Union[str, UUID], role_id: int) -> bool:
        """
        DELETE /api/people/{uid}/functionalroles/{role_id}

        Returns True on success.
        """
        self.session.log(f"People.remove_functional_role: uid={uid}, role_id={role_id}")
        self.session.request("DELETE", f"{self._base_path}/{uid}/functionalroles/{role_id}")
        return True
````

## File: src/teamdynamix/service_catalog.py
````python
# =====================================================================
# FILE: src/teamdynamix/service_catalog.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .session import Session


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


@dataclass(slots=True)
class Service:
    """
    Minimal Service Catalog DTO.

    The service catalog payload/response shape varies by tenant configuration, so we keep
    this intentionally small and rely on raw dicts for everything else.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    Description: Optional[str] = None
    IsActive: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Service":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            Description=data.get("Description"),
            IsActive=data.get("IsActive"),
        )


class ServiceCatalog:
    """
    Service Catalog client, matching the Postman collection endpoints:

      GET    /api/{portalAppId}/services
      POST   /api/{portalAppId}/services
      GET    /api/{portalAppId}/services/{id}
      PUT    /api/{portalAppId}/services/{id}
      DELETE /api/{portalAppId}/services/{id}

    Notes:
    - We keep helper methods minimal and endpoint-representative.
    - 200 OK with [] is a valid “no results” outcome.
    """

    def __init__(self, session: Session, portal_app_id: int):
        self.session = session
        self.portal_app_id = int(portal_app_id)
        self._base_path = f"/api/{self.portal_app_id}/services"

    # ---- List
    def list_raw(self) -> List[Dict[str, Any]]:
        self.session.log(f"ServiceCatalog.list_raw: portal_app_id={self.portal_app_id}")
        resp = self.session.request("GET", self._base_path)
        return _as_list_of_dicts(resp.json())

    def list(self) -> List[Service]:
        return [Service.from_dict(x) for x in self.list_raw()]

    # ---- Get
    def get_raw(self, service_id: int) -> Dict[str, Any]:
        self.session.log(
            f"ServiceCatalog.get_raw: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        resp = self.session.request("GET", f"{self._base_path}/{int(service_id)}")
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.get (expected dict).")
        return data

    def get(self, service_id: int) -> Service:
        return Service.from_dict(self.get_raw(service_id))

    # ---- Create
    def create_raw(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.session.log(f"ServiceCatalog.create_raw: portal_app_id={self.portal_app_id}")
        resp = self.session.request("POST", self._base_path, json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.create (expected dict).")
        return data

    def create(self, payload: Dict[str, Any]) -> Service:
        return Service.from_dict(self.create_raw(payload))

    # ---- Update
    def update_raw(self, service_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        self.session.log(
            f"ServiceCatalog.update_raw: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        resp = self.session.request("PUT", f"{self._base_path}/{int(service_id)}", json=payload)
        data: Any = resp.json()
        if not isinstance(data, dict):
            raise ValueError("Unexpected response shape from ServiceCatalog.update (expected dict).")
        return data

    def update(self, service_id: int, payload: Dict[str, Any]) -> Service:
        return Service.from_dict(self.update_raw(service_id, payload))

    # ---- Delete
    def delete(self, service_id: int) -> bool:
        self.session.log(
            f"ServiceCatalog.delete: portal_app_id={self.portal_app_id}, service_id={service_id}"
        )
        self.session.request("DELETE", f"{self._base_path}/{int(service_id)}")
        return True
````

## File: src/teamdynamix/tickets.py
````python
# =====================================================================
# FILE: src/teamdynamix/tickets.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .session import Session
from .transport import PatchPayload  # exported publicly via __init__.py per your plan


def _first_or_none(data: Any) -> Optional[Dict[str, Any]]:
    """
    TDX endpoints sometimes return either:
      - an object (dict)
      - a list of objects (list[dict])
      - an empty list []
    Normalize to "first dict or None".
    """
    if data is None:
        return None
    if isinstance(data, list):
        if not data:
            return None
        first = data[0]
        return first if isinstance(first, dict) else None
    return data if isinstance(data, dict) else None


def _as_list_of_dicts(data: Any) -> List[Dict[str, Any]]:
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _patch_ops_json(
    ops: Union[Dict[str, Any], List[PatchPayload], List[Dict[str, Any]]]
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    We allow three shapes:
      1) dict[str, Any]  -> Transport will convert to JSON Patch (replace ops) for PATCH
      2) list[PatchPayload] -> we convert to list[dict]
      3) list[dict] -> passed through

    This keeps Tickets.update() endpoint-aligned (PATCH = JSON Patch),
    but still lets callers use the simple {"Field": "Value"} form.
    """
    if isinstance(ops, dict):
        return ops

    out: List[Dict[str, Any]] = []
    for item in ops:
        if isinstance(item, PatchPayload):
            out.append({"op": item.op, "path": item.path, "value": item.value})
        elif isinstance(item, dict):
            out.append(item)
    return out


# ---------------------------------------------------------------------
# DTOs (minimal: just enough to be useful without over-modeling)
# ---------------------------------------------------------------------
@dataclass(slots=True)
class Ticket:
    ID: Optional[int] = None
    Title: Optional[str] = None
    Description: Optional[str] = None
    StatusID: Optional[int] = None
    StatusName: Optional[str] = None
    TypeID: Optional[int] = None
    TypeName: Optional[str] = None
    PriorityID: Optional[int] = None
    PriorityName: Optional[str] = None
    RequestorUid: Optional[str] = None
    ResponsibleUid: Optional[str] = None
    ResponsibleGroupID: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ticket":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Title=data.get("Title"),
            Description=data.get("Description"),
            StatusID=data.get("StatusID"),
            StatusName=data.get("StatusName"),
            TypeID=data.get("TypeID"),
            TypeName=data.get("TypeName"),
            PriorityID=data.get("PriorityID"),
            PriorityName=data.get("PriorityName"),
            RequestorUid=data.get("RequestorUid") or data.get("RequestorUID"),
            ResponsibleUid=data.get("ResponsibleUid") or data.get("ResponsibleUID"),
            ResponsibleGroupID=data.get("ResponsibleGroupID") or data.get("ResponsibleGroupId"),
        )


# ---------------------------------------------------------------------
# Meta endpoints (priorities/types/statuses/sources)
# ---------------------------------------------------------------------
class TicketPriorities:
    """
    Ticket priorities are per ticketing app.

    GET /api/{ticketingAppId}/tickets/priorities
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self) -> List[Dict[str, Any]]:
        self.session.log("TicketPriorities.list")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/priorities")
        return resp.json() or []


class TicketTypes:
    """
    Ticket types are per ticketing app.

    GET /api/{ticketingAppId}/tickets/types?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketTypes.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/types", params=params)
        return resp.json() or []


class TicketStatuses:
    """
    Ticket statuses are per ticketing app.

    GET /api/{ticketingAppId}/tickets/statuses?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketStatuses.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/statuses", params=params)
        return resp.json() or []


class TicketSources:
    """
    Ticket sources are per ticketing app.

    GET /api/{ticketingAppId}/tickets/sources?isActive=
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)

    def list(self, *, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if is_active is not None:
            params["isActive"] = str(is_active).lower()
        self.session.log(f"TicketSources.list: params={params}")
        resp = self.session.request("GET", f"/api/{self.ticketing_app_id}/tickets/sources", params=params)
        return resp.json() or []


# ---------------------------------------------------------------------
# Tickets client
# ---------------------------------------------------------------------
class Tickets:
    """
    Tickets client is per ticketing app.

    Common endpoints (per Postman):
      - GET    /api/{ticketingAppId}/tickets/{id}
      - POST   /api/{ticketingAppId}/tickets/search
      - POST   /api/{ticketingAppId}/tickets
      - PATCH  /api/{ticketingAppId}/tickets/{id}?notifyNewResponsible=
      - GET    /api/{ticketingAppId}/tickets/{id}/feed
      - POST   /api/{ticketingAppId}/tickets/{id}/feed
    """
    def __init__(self, session: Session, ticketing_app_id: int):
        self.session = session
        self.ticketing_app_id = int(ticketing_app_id)
        self._base = f"/api/{self.ticketing_app_id}/tickets"

    # --- Core CRUD-ish
    def get(self, ticket_id: int) -> Optional[Ticket]:
        self.session.log(f"Tickets.get: id={ticket_id}")
        resp = self.session.request("GET", f"{self._base}/{int(ticket_id)}")
        item = _first_or_none(resp.json())
        return Ticket.from_dict(item) if item is not None else None

    def create(self, ticket_payload: Dict[str, Any]) -> Ticket:
        """
        POST /api/{ticketingAppId}/tickets
        Returns created ticket object.
        """
        self.session.log("Tickets.create")
        resp = self.session.request("POST", self._base, json=ticket_payload)
        data = resp.json()
        if not isinstance(data, dict):
            # keep minimal: if API ever returns non-object here, just coerce to empty dict
            data = {}
        return Ticket.from_dict(data)

    def search(self, search_payload: Dict[str, Any]) -> List[Ticket]:
        """
        POST /api/{ticketingAppId}/tickets/search
        Returns list of tickets (possibly empty list []).
        """
        self.session.log("Tickets.search")
        resp = self.session.request("POST", f"{self._base}/search", json=search_payload)
        rows = resp.json() or []
        return [Ticket.from_dict(x) for x in rows if isinstance(x, dict)]

    def update(
        self,
        ticket_id: int,
        ops: Union[Dict[str, Any], List[PatchPayload], List[Dict[str, Any]]],
        *,
        notify_new_responsible: Optional[bool] = None,
    ) -> bool:
        """
        PATCH /api/{ticketingAppId}/tickets/{id}?notifyNewResponsible=
        Body is JSON Patch list. We also accept a simple dict of field->value,
        which Transport will convert into JSON Patch "replace" operations.

        Returns True on success.
        """
        params: Dict[str, Any] = {}
        if notify_new_responsible is not None:
            params["notifyNewResponsible"] = str(notify_new_responsible).lower()

        payload = _patch_ops_json(ops)
        self.session.log(f"Tickets.update: id={ticket_id}, params={params}")
        self.session.request("PATCH", f"{self._base}/{int(ticket_id)}", params=params, json=payload)
        return True

    # --- Feed
    def get_feed(self, ticket_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/{ticketingAppId}/tickets/{id}/feed
        """
        self.session.log(f"Tickets.get_feed: id={ticket_id}")
        resp = self.session.request("GET", f"{self._base}/{int(ticket_id)}/feed")
        return _as_list_of_dicts(resp.json())

    def add_feed_entry(self, ticket_id: int, feed_payload: Dict[str, Any]) -> bool:
        """
        POST /api/{ticketingAppId}/tickets/{id}/feed
        Returns True on success.
        """
        self.session.log(f"Tickets.add_feed_entry: id={ticket_id}")
        self.session.request("POST", f"{self._base}/{int(ticket_id)}/feed", json=feed_payload)
        return True
````

## File: src/teamdynamix/transport.py
````python
# =====================================================================
# FILE: src/teamdynamix/transport.py
#
# Change summary (per your decision):
# - JSON Patch support lives in Transport because it is cross-cutting across client modules.
# - If method == PATCH and json is a dict, Transport converts it to RFC6902-style JSON Patch.
# - If method == PATCH and json is already a list, Transport passes it through unchanged.
# - Transport also ensures Content-Type is set for PATCH if caller didn't provide it.
#
# Notes:
# - This assumes TeamDynamix PATCH endpoints consistently use JSON Patch (common in TDX).
# - Client modules can now call session.request("PATCH", ..., json={"FirstName": "X"}) and it "just works".
# =====================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, Dict, List
import requests

from .exceptions import HttpError, TdxTimeoutError, TdxRequestError


@dataclass(frozen=True, slots=True)
class PatchPayload:
    """
    Represents a single JSON Patch operation (RFC 6902 style), as required by TeamDynamix PATCH endpoints.

    Example:
      {"op": "replace", "path": "/FirstName", "value": "NewFirstName"}
    """
    op: str
    path: str
    value: Any

    def to_dict(self) -> Dict[str, Any]:
        return {"op": self.op, "path": self.path, "value": self.value}


def _build_replace_patch(updates: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Converts a dict of field updates into a JSON Patch list.

    Input:
      {"FirstName": "NewFirstName", "LastName": "NewLastName"}

    Output:
      [
        {"op": "replace", "path": "/FirstName", "value": "NewFirstName"},
        {"op": "replace", "path": "/LastName", "value": "NewLastName"}
      ]
    """
    ops: List[Dict[str, Any]] = []
    for key, value in updates.items():
        ops.append(PatchPayload(op="replace", path=f"/{key}", value=value).to_dict())
    return ops


@dataclass(slots=True)
class Transport:
    """
    Single transport boundary:
    - The only place that touches requests.*
    - Applies the default timeout (optional)
    - Translates timeouts / request exceptions into library exceptions
    - Normalizes TeamDynamix PATCH payloads (JSON Patch) centrally
    """
    logger: Any  # Logger-like: must have .log(str, ...)
    default_timeout: Optional[int] = None

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Any = None,
        data: Any = None,
        timeout: Optional[int] = None,
    ) -> requests.Response:
        m = method.upper()
        effective_timeout = self.default_timeout if timeout is None else timeout

        # ---- PATCH normalization (TeamDynamix JSON Patch) ----
        # If caller passes a dict for PATCH, convert it to a JSON Patch list.
        # If caller passes a list, assume it's already a JSON Patch list and pass through.
        req_headers: Dict[str, str] = {}
        if headers:
            req_headers.update(headers)

        if m == "PATCH":
            if isinstance(json, dict):
                json = _build_replace_patch(json)
            # Ensure PATCH content-type if not specified
            if not any(k.lower() == "content-type" for k in req_headers.keys()):
                req_headers["Content-Type"] = "application/json; charset=utf-8"

        try:
            resp = requests.request(
                method=m,
                url=url,
                headers=req_headers if req_headers else None,
                params=params,
                json=json,
                data=data,
                timeout=effective_timeout,  # None means "no timeout"
            )
        except requests.exceptions.Timeout as e:
            self.logger.log(f"Timeout calling {m} {url} (timeout={effective_timeout})\n", level=40)
            raise TdxTimeoutError(f"Timeout calling {m} {url}") from e
        except requests.exceptions.RequestException as e:
            self.logger.log(f"Request error calling {m} {url}: {e}\n", level=40)
            raise TdxRequestError(f"Request error calling {m} {url}: {e}") from e

        if resp.status_code >= 400:
            text = ""
            try:
                text = (resp.text or "").strip()
            except Exception:
                text = ""
            raise HttpError(
                status_code=resp.status_code,
                method=m,
                url=url,
                message=f"HTTP {resp.status_code} for {m} {url}",
                response_text=text,
            )
        return resp
````

## File: src/py.typed
````
# (Leave this file empty)
````

## File: tests/test_people_endpoints.py
````python
# =====================================================================
# FILE: test_people_endpoints.py
#
# Minimal endpoint test script for People API client.
# - Assumes your config is valid at ./config/sandbox.config.ini (adjust as needed).
# - Uses the library as currently implemented: Session + People + Person.
# =====================================================================

from __future__ import annotations

from teamdynamix.session import Session
from teamdynamix.people import People


def main() -> None:
    # 0) Initialize session + client
    session = Session("./config/sandbox.config.ini")
    people = People(session)

    # Optional: prime authentication explicitly (useful for deterministic testing)
    session.authenticate()

    # 1) Search a person based on the string "000000"
    search_text = "000000"
    results = people.search(search_text, max_results=10)

    if not results:
        print(f"No people matched search text: {search_text}")
        return

    # Choose the first match for this test
    person = results[0]
    if not person.UID:
        print("Search result missing UID; cannot proceed.")
        return

    uid = person.UID
    print(f"[1] Search OK: UID={uid}, FullName={person.FullName}, Email={person.PrimaryEmail}")

    # 2) Get the full user object (raw dict) via People.get_raw + typed view via People.get
    typed_person = people.get(uid)
    raw_person = people.get_raw(uid)

    if typed_person is None or raw_person is None:
        print(f"[2] People.get/get_raw returned no data for UID={uid}")
        return

    print(f"[2] Get OK: FirstName={typed_person.FirstName!r}, LastName={typed_person.LastName!r}, UserName={typed_person.UserName!r}")

    # Capture original FirstName from raw payload (authoritative for patching)
    original_first_name = raw_person.get("FirstName") or ""
    if not isinstance(original_first_name, str):
        original_first_name = str(original_first_name)

    # 3) Update the User's FirstName by appending "TestPatch"
    suffix = "TestPatch"
    if original_first_name.endswith(suffix):
        patched_first_name = original_first_name
    else:
        patched_first_name = f"{original_first_name}{suffix}"

    print(f"[3] Patching FirstName -> {patched_first_name!r}")
    people.update(uid, {"FirstName": patched_first_name})

    # Confirm (re-fetch)
    verify_after_patch = people.get_raw(uid) or {}
    print(f"[3] Verify FirstName: {verify_after_patch.get('FirstName')!r}")

    # 4) Update the User's FirstName by removing "TestPatch" from the end
    current_first_name = verify_after_patch.get("FirstName") or ""
    if not isinstance(current_first_name, str):
        current_first_name = str(current_first_name)

    if current_first_name.endswith(suffix):
        reverted_first_name = current_first_name[: -len(suffix)]
    else:
        # If suffix is not present, revert to original to be safe
        reverted_first_name = original_first_name

    print(f"[4] Reverting FirstName -> {reverted_first_name!r}")
    people.update(uid, {"FirstName": reverted_first_name})

    # Confirm (re-fetch)
    verify_after_revert = people.get_raw(uid) or {}
    print(f"[4] Verify FirstName: {verify_after_revert.get('FirstName')!r}")

    # 5) List the user's functional roles
    roles_before = people.list_functional_roles(uid)
    print(f"[5] Functional roles before: {roles_before}")

    # 6) Add the user to Functional Role with ID 6
    role_id = 6
    print(f"[6] Adding functional role {role_id} (is_primary=False)")
    people.add_functional_role(uid, role_id, is_primary=False)

    roles_after_add = people.list_functional_roles(uid)
    print(f"[6] Functional roles after add: {roles_after_add}")

    # 7) Remove Functional Role with ID 6 from the User
    print(f"[7] Removing functional role {role_id}")
    people.remove_functional_role(uid, role_id)

    roles_after_remove = people.list_functional_roles(uid)
    print(f"[7] Functional roles after remove: {roles_after_remove}")

    print("Done.")


if __name__ == "__main__":
    main()
````

## File: tests/test_ticket_endpoints.py
````python
# =====================================================================
# FILE: tests/test_ticket_endpoints.py
#
# Minimal endpoint test script for Tickets API client.
# - Assumes your config is valid at ./config/sandbox.config.ini (adjust as needed).
# - Assumes you have implemented: Tickets, TicketPriorities, TicketStatuses, TicketSources, TicketTypes.
# - Assumes PATCH JSON Patch handling is centralized in Transport (dict -> JSON Patch list).
#
# Workflow:
# 0) Generate unique string for Description (used later for search)
# 1) List priorities
# 2) List statuses
# 3) List sources
# 4) List types
# 5) Create ticket with:
#    - TypeID: 1 if available else fallback
#    - StatusID: "New"
#    - SourceID: "API"
#    - PriorityID: middle priority (by sorted ID)
# 6) Search tickets by the random string
# 7) Get full ticket by ID
# 8) Add feed entry
# 9) Update ticket StatusID to "Cancelled"
# =====================================================================

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from teamdynamix.session import Session
from teamdynamix.tickets import (
    Tickets,
    TicketPriorities,
    TicketStatuses,
    TicketSources,
    TicketTypes,
)


def _pick_by_name(
    rows: List[Dict[str, Any]],
    desired: str,
    *,
    name_keys: Tuple[str, ...] = ("Name", "name", "StatusName", "SourceName", "TypeName"),
    id_keys: Tuple[str, ...] = ("ID", "Id", "id"),
) -> Optional[int]:
    """
    Find a row whose name matches desired (case-insensitive) and return its ID.
    """
    desired_norm = desired.strip().lower()
    for row in rows:
        if not isinstance(row, dict):
            continue
        name_val = None
        for k in name_keys:
            if k in row and row.get(k) is not None:
                name_val = str(row.get(k))
                break
        if name_val is None:
            continue
        if name_val.strip().lower() == desired_norm:
            for ik in id_keys:
                if ik in row and row.get(ik) is not None:
                    try:
                        return int(row.get(ik))
                    except Exception:
                        pass
    return None


def _pick_id_1_if_available(rows: List[Dict[str, Any]]) -> Optional[int]:
    """
    If any row has ID == 1, return 1, else return first available ID.
    """
    ids: List[int] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k in ("ID", "Id", "id"):
            if k in row and row.get(k) is not None:
                try:
                    ids.append(int(row.get(k)))
                except Exception:
                    pass
                break
    if not ids:
        return None
    if 1 in ids:
        return 1
    return ids[0]


def _pick_middle_id(rows: List[Dict[str, Any]]) -> Optional[int]:
    """
    Pick the "middle" ID (by sorted numeric ID).
    """
    ids: List[int] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k in ("ID", "Id", "id"):
            if k in row and row.get(k) is not None:
                try:
                    ids.append(int(row.get(k)))
                except Exception:
                    pass
                break
    ids = sorted(set(ids))
    if not ids:
        return None
    return ids[len(ids) // 2]


def main() -> None:
    # -----------------------------------------------------------------
    # USER PARAMETERS (edit these)
    # -----------------------------------------------------------------
    CONFIG_PATH = "./config/sandbox.config.ini"

    # You MUST set this to your Ticketing App ID in TeamDynamix
    TICKETING_APP_ID = 0  # <-- CHANGE ME

    # Ticket "base" parameters (IDs will be selected dynamically in the script)
    TEST_TICKET_PARAMS: Dict[str, Any] = {
        "Title": "API Test Ticket (teamdynamix-api)",
        # Description will be appended with a unique string below
        "Description": "Created by automated endpoint test.",
        # Depending on your TDX configuration, you may need additional fields.
        # Add them here if create() fails with validation errors.
        # Example possibilities (varies by org):
        # "RequestorUid": "<some-guid>",
        # "AccountID": 0,
        # "CategoryID": 0,
    }

    # -----------------------------------------------------------------
    # 0) Generate unique string for Description
    # -----------------------------------------------------------------
    unique = f"TDX_API_TEST_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    print(f"[0] Unique search token: {unique}")

    # -----------------------------------------------------------------
    # Init session + clients
    # -----------------------------------------------------------------
    session = Session(CONFIG_PATH)

    # Optional: deterministic testing (force auth early)
    session.authenticate()

    tickets = Tickets(session, ticketing_app_id=TICKETING_APP_ID)
    priorities_client = TicketPriorities(session, ticketing_app_id=TICKETING_APP_ID)
    statuses_client = TicketStatuses(session, ticketing_app_id=TICKETING_APP_ID)
    sources_client = TicketSources(session, ticketing_app_id=TICKETING_APP_ID)
    types_client = TicketTypes(session, ticketing_app_id=TICKETING_APP_ID)

    # -----------------------------------------------------------------
    # 1) Get TicketPriorities via list()
    # -----------------------------------------------------------------
    priorities = priorities_client.list()
    print(f"[1] Priorities count: {len(priorities)}")

    # -----------------------------------------------------------------
    # 2) Get TicketStatuses via list()
    # -----------------------------------------------------------------
    statuses = statuses_client.list(is_active=True)
    print(f"[2] Statuses (active) count: {len(statuses)}")

    # -----------------------------------------------------------------
    # 3) Get TicketSources via list()
    # -----------------------------------------------------------------
    sources = sources_client.list(is_active=True)
    print(f"[3] Sources (active) count: {len(sources)}")

    # -----------------------------------------------------------------
    # 4) Get TicketTypes via list()
    # -----------------------------------------------------------------
    types = types_client.list(is_active=True)
    print(f"[4] Types (active) count: {len(types)}")

    # -----------------------------------------------------------------
    # 5) Create ticket with selected IDs
    # -----------------------------------------------------------------
    type_id = _pick_id_1_if_available(types)
    status_new_id = _pick_by_name(statuses, "New")
    status_cancelled_id = _pick_by_name(statuses, "Cancelled")
    source_api_id = _pick_by_name(sources, "API")
    priority_middle_id = _pick_middle_id(priorities)

    missing = []
    if type_id is None:
        missing.append("TypeID (no types returned)")
    if status_new_id is None:
        missing.append("StatusID for 'New' (no match)")
    if status_cancelled_id is None:
        missing.append("StatusID for 'Cancelled' (no match)")
    if source_api_id is None:
        missing.append("SourceID for 'API' (no match)")
    if priority_middle_id is None:
        missing.append("PriorityID (no priorities returned)")

    if missing:
        print("[5] Cannot proceed; missing required IDs:")
        for m in missing:
            print(f"    - {m}")
        return

    ticket_payload = dict(TEST_TICKET_PARAMS)
    ticket_payload["Description"] = f"{ticket_payload.get('Description', '')}\n\n{unique}"
    ticket_payload["TypeID"] = type_id
    ticket_payload["StatusID"] = status_new_id
    ticket_payload["SourceID"] = source_api_id
    ticket_payload["PriorityID"] = priority_middle_id

    print(f"[5] Creating ticket with IDs: TypeID={type_id}, StatusID(New)={status_new_id}, "
          f"SourceID(API)={source_api_id}, PriorityID(mid)={priority_middle_id}")

    created = tickets.create(ticket_payload)

    if not created.ID:
        print("[5] Ticket create returned no ID; cannot proceed.")
        return

    ticket_id = int(created.ID)
    print(f"[5] Created ticket ID: {ticket_id}")

    # -----------------------------------------------------------------
    # 6) Search tickets by SearchText = unique token
    # -----------------------------------------------------------------
    search_payload = {"SearchText": unique}
    print(f"[6] Searching tickets with payload: {search_payload}")
    search_results = tickets.search(search_payload)
    print(f"[6] Search results count: {len(search_results)}")

    if not search_results:
        print("[6] No search results found; cannot proceed.")
        return

    # Prefer the created ticket if it appears in results; else use the first result
    found_id = None
    for t in search_results:
        if t.ID == ticket_id:
            found_id = ticket_id
            break
    if found_id is None:
        found_id = int(search_results[0].ID) if search_results[0].ID else None

    if found_id is None:
        print("[6] Search returned tickets but none had an ID; cannot proceed.")
        return

    print(f"[6] Using ticket ID from search: {found_id}")

    # -----------------------------------------------------------------
    # 7) Get full ticket using Tickets.get()
    # -----------------------------------------------------------------
    got = tickets.get(found_id)
    if got is None or not got.ID:
        print(f"[7] Tickets.get failed for ID={found_id}")
        return
    print(f"[7] Got ticket: ID={got.ID}, Title={got.Title!r}, StatusID={got.StatusID}, TypeID={got.TypeID}")

    # -----------------------------------------------------------------
    # 8) Add a feed entry
    # -----------------------------------------------------------------
    feed_payload = {"Body": "Ticket feed test via API."}
    print(f"[8] Adding feed entry: {feed_payload}")
    tickets.add_feed_entry(found_id, feed_payload)
    print("[8] Feed entry added.")

    # -----------------------------------------------------------------
    # 9) Update the ticket: set StatusID -> 'Cancelled'
    # -----------------------------------------------------------------
    print(f"[9] Updating ticket StatusID -> Cancelled ({status_cancelled_id})")
    tickets.update(found_id, {"StatusID": status_cancelled_id})
    print("[9] Ticket updated to Cancelled.")

    # Optional: verify status changed
    verify = tickets.get(found_id)
    if verify is not None:
        print(f"[9] Verify status: StatusID={verify.StatusID}, StatusName={verify.StatusName}")

    print("Done.")


if __name__ == "__main__":
    main()
````

## File: .editorconfig
````
# .editorconfig
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 4
trim_trailing_whitespace = true
````

## File: MANIFEST.in
````
include LICENSE
include README.md
recursive-include src/teamdynamix *.py
include src/teamdynamix/py.typed
````

## File: pyproject.toml
````toml
# =====================================================================
# FILE: pyproject.toml
# =====================================================================
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "teamdynamix-api"
version = "0.1.0"
description = "A Python SDK for the TeamDynamix Web API."
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "University of Florida" }]
keywords = ["teamdynamix", "api", "sdk", "requests", "tdx"]
classifiers = [
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  "Typing :: Typed",
]
dependencies = [
  "requests>=2.31",
]

[project.optional-dependencies]
dev = [
  "pytest>=7.0",
  "pytest-cov>=4.1",
  "ruff>=0.5",
  "mypy>=1.10",
  "build>=1.2",
  "twine>=5.0",
]

[project.urls]
Homepage = "https://gitlab.it.ufl.edu/nicholas.linney/teamdynamix-api"
Repository = "https://gitlab.it.ufl.edu/nicholas.linney/teamdynamix-api"
"Issue Tracker" = "https://gitlab.it.ufl.edu/nicholas.linney/teamdynamix-api/-/issues"

[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.packages.find]
where = ["src"]
include = ["teamdynamix*"]

[tool.setuptools.package-data]
teamdynamix = ["py.typed"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
warn_unused_ignores = true
ignore_missing_imports = true
strict = false
````

## File: pytest.ini
````
[pytest]
pythonpath = ["src"]
addopts = -q --cov=src/teamdynamix --cov-report=term-missing --cov-fail-under=80
````

## File: config/sample.config.ini
````
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
````

## File: src/teamdynamix/__init__.py
````python
# src/teamdynamix/__init__.py
from __future__ import annotations

__version__ = "0.0.0-pre-alpha.10"

# Core
from .config import Config
from .logger import Logger
from .event import Event
from .auth import Auth
from .session import Session
from .transport import Transport, PatchPayload

# Clients
from .people import People, Person

__all__ = [
    "__version__",
    # Core
    "Config",
    "Logger",
    "Event",
    "Auth",
    "Session",
    "Transport",
    "PatchPayload",
    # Clients
    "People",
    "Person",
]
````

## File: src/teamdynamix/projects.py
````python
# =====================================================================
# FILE: src/teamdynamix/projects.py
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

from .session import Session
from .transport import PatchPayload


def _as_list(data: Any) -> List[Dict[str, Any]]:
    """
    Normalize an API response into list[dict].

    Rules:
      - None / [] -> []
      - dict -> [dict]
      - list -> only dict entries (filters safely)
      - anything else -> []
    """
    if not data:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def _as_dict(data: Any) -> Optional[Dict[str, Any]]:
    """
    Normalize an API response into dict | None.

    Rules:
      - None / {} -> None
      - dict -> dict
      - anything else -> None
    """
    if not data:
        return None
    return data if isinstance(data, dict) else None


@dataclass(slots=True)
class Project:
    """
    Minimal Project model.

    Keep this intentionally lean: the SDK should stay close to the vendor API
    surface. If callers need additional fields, they can access raw dicts from
    response.json() or we can expand this dataclass later with proven needs.
    """
    ID: Optional[int] = None
    Name: Optional[str] = None
    IsActive: Optional[bool] = None
    Description: Optional[str] = None
    ManagerUid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        return cls(
            ID=data.get("ID") or data.get("Id") or data.get("id"),
            Name=data.get("Name"),
            IsActive=data.get("IsActive"),
            Description=data.get("Description"),
            ManagerUid=data.get("ManagerUid") or data.get("ManagerUID"),
        )


class Projects:
    """
    Projects client for TeamDynamix PPM endpoints.

    Pattern: thin endpoint wrapper (keeps vendor API surface recognizable),
    using Session as the facade and Transport as the sole HTTP boundary.
    """

    _base_path = "/api/projects"

    def __init__(self, session: Session):
        self.session = session

    # ---------------------------
    # Core endpoints
    # ---------------------------

    def search(self, criteria: Dict[str, Any]) -> List[Project]:
        """
        POST /api/projects/search
        Returns: list of projects (possibly empty, which is valid).
        """
        self.session.log(f"Projects.search: keys={list(criteria.keys())}")
        resp = self.session.request("POST", f"{self._base_path}/search", json=criteria)
        items = _as_list(resp.json())
        return [Project.from_dict(item) for item in items]

    def get(self, project_id: int) -> Project:
        """
        GET /api/projects/{id}
        """
        self.session.log(f"Projects.get: id={project_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(project_id)}")
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.get (expected dict).")
        return Project.from_dict(data)

    def create(
        self,
        project_data: Dict[str, Any],
        *,
        notify_new_manager: bool = False,
        notify_new_alt_managers: bool = False,
    ) -> Project:
        """
        POST /api/projects
        Query:
          notifyNewManager (bool)
          notifyNewAltManagers (bool)
        """
        params = {
            "notifyNewManager": str(bool(notify_new_manager)).lower(),
            "notifyNewAltManagers": str(bool(notify_new_alt_managers)).lower(),
        }
        self.session.log(f"Projects.create: params={params}, keys={list(project_data.keys())}")
        resp = self.session.request("POST", self._base_path, params=params, json=project_data)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.create (expected dict).")
        return Project.from_dict(data)

    def edit(self, project_id: int, updates: Dict[str, Any]) -> Project:
        """
        POST /api/projects/{id}
        (TDX uses POST for edit on this resource.)
        """
        self.session.log(f"Projects.edit: id={project_id}, keys={list(updates.keys())}")
        resp = self.session.request("POST", f"{self._base_path}/{int(project_id)}", json=updates)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.edit (expected dict).")
        return Project.from_dict(data)

    def patch(
        self,
        project_id: int,
        operations: Union[List[PatchPayload], List[Dict[str, Any]], Dict[str, Any]],
    ) -> Project:
        """
        PATCH /api/projects/{id}

        Accepts:
          - list[PatchPayload]       -> serialized via .to_dict()
          - list[dict[str, Any]]     -> passed through unchanged (assumed already RFC6902)
          - dict[str, Any]           -> passed through; Transport converts dict->JSON Patch list for PATCH
        """
        payload: Any
        if isinstance(operations, dict):
            payload = operations  # Transport converts dict -> patch list (replace ops)
        elif isinstance(operations, list):
            if all(isinstance(op, PatchPayload) for op in operations):
                payload = [op.to_dict() for op in operations]
            elif all(isinstance(op, dict) for op in operations):
                payload = operations
            else:
                raise TypeError("Projects.patch operations list must be all PatchPayload or all dict.")
        else:
            raise TypeError("Projects.patch operations must be a dict, list[PatchPayload], or list[dict].")

        self.session.log(f"Projects.patch: id={project_id}")
        resp = self.session.request("PATCH", f"{self._base_path}/{int(project_id)}", json=payload)
        data = _as_dict(resp.json())
        if data is None:
            raise ValueError("Unexpected response shape from Projects.patch (expected dict).")
        return Project.from_dict(data)

    # ---------------------------
    # Project Feed endpoints
    # ---------------------------

    def get_feed(self, project_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/projects/{id}/feed
        Returns [] when empty (valid).
        """
        self.session.log(f"Projects.get_feed: project_id={project_id}")
        resp = self.session.request("GET", f"{self._base_path}/{int(project_id)}/feed")
        return _as_list(resp.json())

    def add_feed(self, project_id: int, body: str) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/feed
        Body: { "Body": "<string>" }
        """
        payload = {"Body": body}
        self.session.log(f"Projects.add_feed: project_id={project_id}")
        resp = self.session.request("POST", f"{self._base_path}/{int(project_id)}/feed", json=payload)
        return _as_dict(resp.json()) or {}

    # ---------------------------
    # Plan / task endpoints
    # ---------------------------

    def get_plan(self, project_id: int, plan_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /api/projects/{projectId}/plans/{planId}
        """
        self.session.log(f"Projects.get_plan: project_id={project_id}, plan_id={plan_id}")
        resp = self.session.request(
            "GET",
            f"{self._base_path}/{int(project_id)}/plans/{int(plan_id)}",
        )
        return _as_dict(resp.json())

    def edit_task(
        self,
        project_id: int,
        plan_id: int,
        task_id: int,
        updates: Dict[str, Any],
        *,
        notify_new_resources: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        POST /api/projects/{projectId}/plans/{planId}/tasks/{taskId}/edit
        Query:
          notifyNewResources (bool)
        """
        params = {"notifyNewResources": str(bool(notify_new_resources)).lower()}
        self.session.log(
            f"Projects.edit_task: project_id={project_id}, plan_id={plan_id}, task_id={task_id}, params={params}"
        )
        resp = self.session.request(
            "POST",
            f"{self._base_path}/{int(project_id)}/plans/{int(plan_id)}/tasks/{int(task_id)}/edit",
            params=params,
            json=updates,
        )
        return _as_dict(resp.json())

    # ---------------------------
    # Issue feed endpoints
    # ---------------------------

    def get_issue_feed(self, project_id: int, issue_id: int) -> List[Dict[str, Any]]:
        """
        GET /api/projects/{projectId}/issues/{issueId}/feed
        Returns [] when empty (valid).
        """
        self.session.log(f"Projects.get_issue_feed: project_id={project_id}, issue_id={issue_id}")
        resp = self.session.request(
            "GET",
            f"{self._base_path}/{int(project_id)}/issues/{int(issue_id)}/feed",
        )
        return _as_list(resp.json())

    def add_issue_comment(self, project_id: int, issue_id: int, comment_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/projects/{projectId}/issues/{issueId}/feed
        Body: (per Postman / TDX schema; typically includes "Body")
        """
        self.session.log(f"Projects.add_issue_comment: project_id={project_id}, issue_id={issue_id}")
        resp = self.session.request(
            "POST",
            f"{self._base_path}/{int(project_id)}/issues/{int(issue_id)}/feed",
            json=comment_payload,
        )
        return _as_dict(resp.json()) or {}
````

## File: src/teamdynamix/session.py
````python
# =====================================================================
# FILE: src/teamdynamix/session.py
# =====================================================================
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Union, Literal, Mapping

from .auth import Auth
from .config import Config, AuthMode
from .logger import Logger
from .transport import Transport
from .exceptions import ConfigError


TdxEnvironment = Literal["TD", "SBTD"]
ConfigSource = Union[str, Path, Config, Mapping[str, Any], None]


class Session:
    """
    Composition Root / Facade for the TeamDynamix client library.

    Enhanced constructor (pre-alpha.10):
      - config may be: path | Config | dict-like overlay | None
      - overrides may be: dict of key-value pairs applied after base config
      - auth_mode/environment can be overridden explicitly (validated literals)
    """

    def __init__(
        self,
        config: ConfigSource = "./config/config.ini",
        *,
        auth_mode: Optional[AuthMode] = None,
        environment: Optional[TdxEnvironment] = None,
        overrides: Optional[Mapping[str, Any]] = None,
    ):
        # 1) Resolve base config
        base_cfg: Optional[Config] = None
        overlay: Dict[str, Any] = {}

        if config is None:
            # default behavior: load from default ini path
            base_cfg = Config.from_file("./config/config.ini")
        elif isinstance(config, (str, Path)):
            base_cfg = Config.from_file(config)
        elif isinstance(config, Config):
            # Config is already validated and complete by design.
            base_cfg = config
        elif isinstance(config, Mapping):
            # Partial overlays are allowed here (validated only after merge/build).
            overlay.update(dict(config))
        else:
            raise ConfigError("Invalid config argument. Expected path, Config, mapping, or None.")

        # 2) Merge overlays in correct precedence order:
        #    base_cfg < config-mapping (if provided) < overrides < explicit keyword overrides
        merged: Dict[str, Any] = {}
        if base_cfg is not None:
            merged.update(asdict(base_cfg))

        merged.update(overlay)
        if overrides:
            merged.update(dict(overrides))

        if auth_mode is not None:
            mode = (auth_mode or "").strip().lower()
            if mode not in ("admin", "user"):
                raise ConfigError("Invalid auth_mode override. Expected 'admin' or 'user'.")
            merged["auth_mode"] = mode

        if environment is not None:
            env = (environment or "").strip().upper()
            if env not in ("TD", "SBTD"):
                raise ConfigError("Invalid environment override. Expected 'TD' or 'SBTD'.")
            merged["environment"] = env

        # 3) Build Config once (single validation point)
        #    ConfigError should only occur here if required fields remain missing/invalid.
        try:
            self.config = Config(**merged)  # type: ignore[arg-type]
        except TypeError as e:
            # Common cause: unknown key in overrides dict
            raise ConfigError(f"Invalid configuration keys provided: {e}") from e

        # 4) Wire dependencies (Composition Root)
        self.logger = Logger(
            log_dir=self.config.log_dir,
            level=self.config.log_level,
            console=self.config.log_console,
        )

        self.transport = Transport(
            logger=self.logger,
            default_timeout=self.config.timeout,
        )

        self.auth = Auth(
            config=self.config,
            logger=self.logger,
            transport=self.transport,
        )

    # ---- Facade properties/methods used by client modules ----

    @property
    def base_url(self) -> str:
        return self.config.base_url

    def log(self, message: str, *, level: int = 20) -> None:
        self.logger.log(message, level=level)

    def authenticate(self) -> str:
        """
        Optional explicit auth call for intentionality/testing.
        Otherwise token retrieval happens lazily when auth_header() is requested.
        """
        return self.auth.authenticate()

    def auth_header(self) -> Dict[str, str]:
        token = self.auth.get_token()
        return {"Authorization": f"Bearer {token}"}

    def request(self, method: str, path: str, **kwargs: Any):
        """
        Primary request entrypoint for all client modules.

        Returns: requests.Response
        """
        url = f"{self.base_url}{path}"
        return self.transport.request(
            method=method,
            url=url,
            headers=kwargs.pop("headers", None) or self.auth_header(),
            params=kwargs.pop("params", None),
            json=kwargs.pop("json", None),
            data=kwargs.pop("data", None),
            timeout=kwargs.pop("timeout", None),
        )
````

## File: .gitignore
````
# .gitignore
.DS_Store
__pycache__/
*.pyc
*.pyo
*.pyd
*.egg-info/
.cache/
.dist/
build/
dist/
.venv/
venv/
.env
.pytest_cache/
.mypy_cache/
coverage.xml
htmlcov/
logs/

# Ignore everything in config/
config/*

# But keep this specific file
!config/sample.config.ini
````
