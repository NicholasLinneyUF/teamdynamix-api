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