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