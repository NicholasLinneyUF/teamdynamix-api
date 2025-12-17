# Architectural_Decisions.md

## Introduction

This document records the architectural decisions made during the design and implementation of the **TeamDynamix API Python library**.  
The library is a clean-slate implementation informed by prior working code, but **not constrained by backward compatibility**. The primary goals are:

- Strong alignment with **SOLID principles**, especially *Separation of Concerns*
- A **clear, explicit architecture** that mirrors the vendor’s API surface
- Minimal abstraction and minimal “magic”
- Predictable behavior suitable for scripting, automation, and long-term maintenance
- A structure that can **scale naturally** as additional TeamDynamix endpoints are added

The design favors:
- Explicit object roles
- Centralized cross-cutting behavior
- Lazy execution of network-dependent operations
- Typed representations only where they provide clear value

The sections below document the major architectural decisions, including **what was decided, why it was decided, and how it is implemented**.

---

## Decision 1: Session as the Composition Root

### What
`Session` is the **composition root** of the library. All core objects (`Config`, `Logger`, `Transport`, `Auth`) are instantiated and owned by `Session`.

### Why
- Centralizes object creation
- Prevents duplicated initialization logic
- Makes dependency flow explicit and testable
- Avoids “utility object sprawl” across client modules

### How
- `Session.__init__()` loads and validates `Config`
- `Session` constructs `Logger`, `Transport`, and `Auth`
- Client modules (e.g., `People`) receive a `Session` instance and nothing else

---

## Decision 2: Lazy Authentication

### What
Authentication is **lazy**: no network calls are made during object construction.

### Why
- Improves ergonomics (`Session(...)` should always succeed if config is valid)
- Avoids unexpected side effects during import or initialization
- Enables deterministic testing
- Defers failure until an authenticated request is actually needed

### How
- `Auth` does not authenticate during construction
- `Session.request()` triggers authentication implicitly when required
- `Session.authenticate()` exists as an *explicit, optional* way to force authentication early

---

## Decision 3: Single Transport Boundary

### What
All HTTP traffic goes through a single class: `Transport`.

### Why
- Ensures consistent timeout behavior
- Ensures consistent error handling
- Provides a single place to adapt vendor quirks
- Minimizes the surface area that touches `requests`

### How
- `Transport.request()` is the only place that calls `requests.request`
- Client modules never import or reference `requests`
- `Session.request()` delegates directly to `Transport.request()`

---

## Decision 4: Centralized JSON Patch Handling

### What
**JSON Patch (RFC 6902)** logic is implemented in `Transport`, not in individual client modules.

### Why
- TeamDynamix uses JSON Patch across multiple PATCH endpoints
- PATCH semantics are cross-cutting, not endpoint-specific
- Prevents duplicated or inconsistent PATCH implementations
- Keeps client modules aligned with vendor semantics

### How
- If `method == PATCH` and `json` is a `dict`, `Transport` converts it into a JSON Patch list
- If `json` is already a list, it is passed through unchanged
- `Transport` ensures the correct `Content-Type` header is set
- Client modules simply pass `json={"Field": "Value"}`

---

## Decision 5: Minimal, Typed DTOs

### What
Typed dataclasses (e.g., `Person`) represent **only commonly used fields**, not full API payloads.

### Why
- TeamDynamix payloads are large, nested, and volatile
- Over-modeling increases maintenance cost
- Most scripts only need a small subset of fields
- Full payloads should still be accessible when needed

### How
- `Person` includes identity and commonly referenced fields
- `People.get_raw()` returns the full raw dictionary
- Typed DTOs are used for *reading*, not for enforcing schema completeness

---

## Decision 6: Endpoint-Representative Client Modules

### What
Client modules map **directly** to vendor API endpoints and avoid “helper” abstractions.

### Why
- Keeps the library aligned with the vendor API surface
- Avoids opinionated behavior that may not generalize
- Makes future API changes easier to track and implement
- Reduces cognitive load for users familiar with TeamDynamix

### How
- Each public method corresponds to a specific API endpoint
- Convenience methods are added only when architecturally justified
- No hidden side effects or implicit workflows inside client modules

---

## Decision 7: Validation Belongs in Config

### What
All configuration validation happens in `Config`, not in `Session` or client modules.

### Why
- Validation is a configuration concern, not a runtime concern
- Keeps `Session` lightweight and focused on orchestration
- Enables fail-fast behavior at application startup

### How
- `Config.__post_init__()` validates required fields and semantics
- `Session` trusts that `Config` is valid
- Runtime errors are reserved for runtime conditions (network, permissions, etc.)

---

## Decision 8: Simple, Optional Timeouts

### What
Timeout support is **minimal and optional**.

### Why
- Avoids over-engineering timeout policies
- Matches common scripting and automation needs
- Prevents crashes due to unhandled timeouts
- Keeps the configuration surface small

### How
- Timeout is configured once in `Config`
- `Transport` applies the timeout uniformly
- Timeout can be disabled by configuration (`0` or `None`)
- No retry or backoff logic is included by default

---

## Decision 9: Explicit Public API Surface

### What
The public API is explicitly defined via `__all__` in `teamdynamix/__init__.py`.

### Why
- Prevents accidental exposure of internal helpers
- Makes the intended usage surface obvious
- Improves long-term maintainability

### How
- All public classes and exceptions are imported and listed explicitly
- Internal helpers remain unexported unless intentionally exposed

---

## Summary

The architecture intentionally favors:

- **Clarity over cleverness**
- **Explicit boundaries over implicit behavior**
- **Vendor alignment over abstraction purity**

As a result, the library is:
- Easy to reason about
- Predictable in behavior
- Resistant to accidental complexity
- Well-positioned for incremental growth

This document should be updated as new architectural decisions are made.
