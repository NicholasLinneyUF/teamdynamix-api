# Changelog

All notable changes to the TeamDynamix API Python SDK are documented here.
Pre-alpha releases are experimental snapshots and may contain breaking changes.

## [0.0.0-pre-alpha.11] - 2026-08-25

Python distribution metadata uses the PEP 440 equivalent `0.0.0a11`.

### Added

- Attribute-choice list, create/copy, edit, and delete operations.
- Custom-attribute discovery with optional component, associated-type, and
  application filters.
- `AttributeChoice` and raw/typed Attributes response patterns.
- `teamdynamix.tools` CSV and SQLite helpers for local automation scripts.
- Canonical `data_utils` path and string-normalization helpers, exported through
  `teamdynamix.tools`.
- Neutral `script_utils` helpers for baseline CLI flags, deterministic mode
  selection, and path normalization without workflow execution.
- A distinct `ToolsError` hierarchy for local path, fingerprint, and migration
  state failures.
- Script-specific logger filename prefixes exposed through `Session`.
- README, MIT license, PEP 561 marker, deterministic core tests, and built-wheel
  import smoke tests.

### Changed

- Declared pandas as a runtime dependency because importing
  `teamdynamix.tools` imports its pandas-backed CSV implementation.
- Reclassified live, state-changing endpoint scripts as manual examples.
- Corrected package project URLs to GitHub and aligned release branch guidance
  with the project promotion model.
- Removed duplicate and legacy `resolve_data_path` implementations and exports;
  the canonical implementation now lives in `teamdynamix.tools.data_utils`.
- Set an honest 35% coverage floor; the release suite currently exceeds it.

### Fixed

- `HttpError` now renders useful HTTP request context while omitting response
  text from its default string form.
- Core documentation links and Attributes method names now resolve to the
  implemented surface.
- The `py.typed` marker is now located and packaged under `teamdynamix`.

### Historical boundary

This release is the final baseline derived from the legacy TeamDynamix Postman
corpus. Swagger/OpenAPI realignment begins in Pre-Alpha 12.

## [0.0.0-pre-alpha.10]

### Added

- Consolidated the Session, Transport, Auth, Config, and logging architecture.
- Added or expanded People, Groups, Accounts, Applications, Functional Roles,
  Tickets, Projects, and Service Catalog clients.
- Added structured logging events and centralized JSON Patch normalization.

### Changed

- Standardized thin, endpoint-oriented clients and selective dataclass DTOs.
- Consolidated earlier experimental branches into a documented baseline.

## [pre-alpha0x]

- Established the initial experimental API clients and architectural proving
  ground that preceded the numbered pre-alpha releases.
