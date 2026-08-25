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