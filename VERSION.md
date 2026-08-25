# Pre-Alpha 11

- Release label and Git tag: `0.0.0-pre-alpha.11`
- Python distribution version: `0.0.0a11`
- Release type: Pre-alpha feature snapshot
- Release date: 2026-08-25

Python package indexes require PEP 440 versions. The distribution therefore
uses `0.0.0a11`, the installable equivalent of the project’s SemVer release
label `0.0.0-pre-alpha.11`.

## Release identity

Pre-Alpha 11 is the final SDK baseline derived from the legacy TeamDynamix
Postman corpus. It does not claim conformance with the subsequently published
Swagger/OpenAPI specification. OpenAPI path, operation, and schema alignment is
planned for Pre-Alpha 12.

## Highlights

- Expanded the `Attributes` client with attribute-choice lifecycle operations,
  custom-attribute discovery, raw response methods, and typed wrappers.
- Added the first `teamdynamix.tools` package with pandas-backed CSV helpers,
  SQLite tracking utilities, canonical data-path/string helpers, and neutral
  command-line parser scaffolding for local scripts.
- Added immutable source-file fingerprints, field-level mismatch diagnostics,
  SQLite fingerprint persistence, and fail-closed `new`, `overwrite`, and
  `resume` migration tracker preparation.
- Added a distinct local-workflow exception hierarchy: `ToolsError`,
  `FingerprintMismatchError`, `MigrationStateError`, and `DataPathError`.
- Preserved the established `Session` / `Transport` / `Auth` architecture and
  centralized JSON Patch handling and API response normalization.
- Added concise `HttpError` string output without automatically exposing
  response bodies.
- Added script-specific logger filename prefixes through `Session`.

## Release stabilization

- Added deterministic tests for Session, Transport, Auth, Attributes, logging,
  exceptions, shared data helpers, script CLI parsing, tools import contracts,
  and distribution artifacts; no live tenant credentials are required.
- Reclassified state-changing endpoint exercises as manual examples.
- Added build/install smoke coverage for both `teamdynamix` and
  `teamdynamix.tools`.
- Declared pandas as a runtime dependency so the public tools package imports
  from a normal installation.
- Added README and MIT license files, corrected project URLs, and packaged the
  PEP 561 `py.typed` marker in the library namespace.
- Reconciled documentation links, method names, branch flow, and the historical
  Postman/OpenAPI boundary.
- Consolidated `resolve_data_path` into `teamdynamix.tools.data_utils`, removed
  legacy module exports, and established a single package-level import contract.

## Known limitations

- API coverage remains intentionally limited to modules already present in the
  repository.
- Broader `teamdynamix.tools` scalability, state-model, and packaging boundaries
  remain scheduled for redesign in Pre-Alpha 12; Pre-Alpha 11 now includes the
  source-integrity and tracker-lifecycle safeguards required by local migrations.
- Several existing client modules have only import-level or incidental test
  coverage; the configured 35% project floor records the current baseline
  rather than overstating maturity.

## Compatibility

This is an experimental snapshot with no backward-compatibility guarantee.
Python 3.10 or newer is required.
