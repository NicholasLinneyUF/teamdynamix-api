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