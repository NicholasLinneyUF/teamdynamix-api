# CHANGELOG.md

All notable changes to the **TeamDynamix API Python SDK** are documented in this file.

This project follows **reverse-chronological pre-alpha versioning**.
Breaking changes *may* occur between pre-alpha releases.

---

## [pre-alpha0x] — Initial Experimental Foundation

**Focus:** Exploration and architectural discovery

### Characteristics

* Early API client experiments
* Mixed patterns and approaches
* Limited documentation
* Inconsistent abstractions
* No formal release discipline

### Outcome

* Served as the proving ground for:

  * Session/Transport split
  * Lazy authentication
  * Minimal DTO philosophy
* Fully consolidated and retired prior to `pre-alpha10`

---

## Versioning Notes

* Pre-alpha releases prioritize learning and structure over stability
* Backward compatibility is **not guaranteed**
* Breaking changes are documented explicitly when they occur

---

## [pre-alpha10] — Structural Consolidation & API Surface Growth

**Focus:** Architectural clarity, core API coverage, internal consistency

### Major Changes

* Consolidated all legacy and experimental work into a clean baseline
* Formalized architectural decisions:

  * Session as composition root
  * Transport as sole HTTP boundary
  * Centralized JSON Patch handling
* Introduced consistent DTO patterns across modules
* Added or expanded clients:

  * People
  * Groups
  * Accounts
  * Applications
  * Functional Roles
  * Tickets
  * Projects
* Established consistent logging and exception strategy
* Introduced `Event` model for structured logging

### Documentation

* Added `Architectural_Decisions.md`
* Improved module-level docstrings across core and client modules

---

## [Unreleased] — Pre-Alpha 11 (WIP → Final)

**Focus:** Documentation maturity, Attributes API parity, script-oriented tooling

### Core Architecture & Infrastructure

* No breaking architectural changes.
* Session remains the composition root.
* Transport remains the single HTTP boundary.
* Auth remains lazily evaluated and thread-safe.

---

### Attributes API — Major Expansion (Issue #5)

**New capabilities added to `src/teamdynamix/attributes.py`:**

* Added full support for **Attribute Choices**:

  * `GET /api/attributes/{id}/choices`
  * `POST /api/attributes/{id}/choices`

    * Supports `copyFromChoiceId`
  * `PUT /api/attributes/{id}/choices/{choiceId}`
  * `DELETE /api/attributes/{id}/choices/{choiceId}`

* Added support for **Custom Attributes**:

  * `GET /api/attributes/custom`
  * Optional filters:

    * `componentId`
    * `associatedTypeId`
    * `appId`

* Introduced **dual-method pattern**:

  * Raw methods returning `Dict[str, Any]` / `List[Dict[str, Any]]`
  * Typed wrapper methods returning DTOs

* Added new `AttributeChoice` DTO aligned with observed API schema:

  * ID
  * Name
  * IsActive
  * DateCreated
  * DateModified
  * Order

**Result:**
The Attributes client now reaches practical parity with the TeamDynamix Web API and Postman collection.

---

### New Sub-Package: `teamdynamix.tools`

Introduced a dedicated namespace for **script-oriented utilities** that are intentionally *not* API clients.

Design principles:

* No HTTP calls
* No dependency on client modules
* Safe for one-off scripts
* Explicit, predictable behavior

---

### CSV Utilities (`csv_utils.py`)

**Purpose:** Safe, unopinionated CSV ingestion for scripts and automation.

Key features:

* Load any CSV file into a searchable table object
* Supports arbitrary column counts
* Global default delimiter (ASCII code–based)
* Runtime override via `set_separator()`
* Pandas-backed for robustness

Supported operations:

* Load full CSV into memory
* Row count / column count
* Retrieve row by index
* Retrieve cell by row/column
* Retrieve all values in a column
* Case-sensitive and insensitive search:

  * `search_contains`
  * `search_exact`
* Structured search results via `CellMatch` objects

  * `.row` / `.column` / `.value`
  * `.x` / `.y` aliases for ergonomic access

All operations are **read-only by design**.

---

### SQLite Utilities (`sqlite_utils.py`)

**Purpose:** Lightweight, temporary SQLite tracking for long-running or restartable scripts.

Primary use cases:

* CSV-driven imports
* API batch processing
* SQL query result iteration
* Error capture and replay

Key capabilities:

* Create or reuse SQLite database files
* Automatic backup and archive support
* Standard schema enforced:

  * `data` table with `processed` flag
  * `errors` table mirroring source columns + `error_msg`

Row-processing workflow:

* `pop()` retrieves the next unprocessed row
* `mark_as_processed()` updates state
* `write_error()` records failures while preserving original row data

Query helpers:

* Row count / column count
* Column name ↔ index resolution
* Retrieve rows or cells
* Column value extraction
* Search helpers:

  * `search_contains`
  * `search_exact`
  * Row-index variants for control-flow usage

Explicitly **not** an ORM and **not** intended for long-term persistence.

---

### Documentation Improvements

* Adopted **documentation as a first-class artifact**
* Added full docs for:

  * `csv_utils`
  * `sqlite_utils`
* Introduced tools README
* Documentation aligns with:

  * Module intent
  * Public API surface
  * Script usage patterns
* Prepared groundwork for a docs index (`docs/INDEX.md`)
* Planned addition of a documentation completeness checklist in `CONTRIBUTING.md`

---

### Known Gaps (Accepted for Pre-Alpha)

* Unit test coverage for new Attributes endpoints is limited
* Some tooling behaviors intentionally trade type fidelity for predictability
* Release metadata (version string, VERSION.md) pending final update