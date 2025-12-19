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