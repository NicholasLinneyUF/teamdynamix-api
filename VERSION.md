# VERSION.md

## Pre-Alpha 11 (`pre-alpha11`)

**Release Type:** Pre-Alpha
**Audience:** SDK contributors, internal integrators, advanced script authors
**Stability:** Experimental (no backward-compatibility guarantees)

---

### API Clients & Core Functionality

* Expanded `Attributes` client to support full **Attribute Choices** lifecycle:

  * List, create (with optional copy), update, and delete attribute choices
* Added support for **Custom Attribute** discovery via `/api/attributes/custom`

  * Optional filtering by component, associated type, and application
* Introduced `AttributeChoice` DTO aligned with observed TeamDynamix API schema
* Preserved minimal, vendor-surface-aligned DTO philosophy for all attribute models
* Maintained existing Session / Transport / Auth architecture without breaking changes

---

### New Script-Oriented Utilities (`teamdynamix.tools`)

* Introduced `teamdynamix.tools` subpackage for non-API helper utilities
* Explicitly decoupled tools from:

  * HTTP transport
  * API clients
  * SDK workflows

#### CSV Utilities

* Added `csv_utils.py` for safe, unopinionated CSV ingestion
* Supports arbitrary column counts and schemas
* Global default delimiter defined via ASCII character code (default: comma)
* Runtime delimiter override supported via setter (script-scoped)
* Pandas-backed parsing for robustness and performance
* Read-only operations including:

  * Row and column access
  * Column value extraction
  * Cell-level access
  * Case-sensitive and insensitive searching
* Introduced `CellMatch` result object for structured search results

#### SQLite Utilities

* Added `sqlite_utils.py` for temporary, script-lifetime SQLite tracking
* Supports creation, backup, and archival of SQLite database files
* Enforces standard schema:

  * `data` table with `processed` flag
  * `errors` table mirroring source columns plus `error_msg`
* Designed for restartable, row-by-row processing workflows
* Provides helpers for:

  * Row, column, and cell access
  * Column name/index resolution
  * Value searching (exact and contains)
  * Error recording independent of processing state
* Explicitly not an ORM and not intended for long-term persistence

---

### Documentation

* Formalized documentation as a first-class release artifact
* Added full developer documentation for:

  * `csv_utils`
  * `sqlite_utils`
* Introduced `docs/teamdynamix/tools/README.md`
* Established and locked a reusable “JavaDocs-style” module documentation template
* Updated architecture and module docs to align with current SDK design
* Prepared groundwork for:

  * Central docs index (`docs/INDEX.md`)
  * Documentation completeness checklist in `CONTRIBUTING.md`

---

### Known Limitations (Accepted for Pre-Alpha)

* Unit test coverage for new Attributes endpoints is limited
* Script utilities prioritize predictability over strict type preservation
* Release metadata updates (version string sync) pending final tagging

---

### Compatibility Notes

* This release is additive but **not guaranteed backward-compatible**
* APIs, DTOs, and helper utilities may change without notice
* Intended for early adopters, internal tooling, and feedback-driven iteration