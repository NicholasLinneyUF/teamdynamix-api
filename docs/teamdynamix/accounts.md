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