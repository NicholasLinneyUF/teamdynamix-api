# VERSIONING.md
## Versioning Strategy and Naming Conventions

This project follows **Semantic Versioning 2.0.0**, with additional, explicitly-defined lifecycle phases to accurately communicate stability and intent during early development.

Versioning is used as a **communication tool**, not merely a technical artifact.

---

## 1. Semantic Versioning Baseline

All versions conform to:

MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]

Where:

- **MAJOR** — incompatible API changes
- **MINOR** — backward-compatible feature additions
- **PATCH** — backward-compatible bug fixes
- **PRERELEASE** — lifecycle or stability indicators
- **BUILD** — optional metadata (not used for precedence)

---

## 2. Lifecycle Phases

This project distinguishes **lifecycle phases** from **numeric progression**.

### 2.1 Pre-Alpha (Draft Phase)

#### Intent
Pre-Alpha represents exploratory, architecture-shaping drafts prior to formal stability guarantees.

#### Characteristics
- Architecture is being finalized
- Breaking changes are expected
- No API stability guarantees
- Versions represent **snapshots**, not incremental releases

#### Version Format

0.0.0-pre-alpha.N

Examples:
- `0.0.0-pre-alpha.1`
- `0.0.0-pre-alpha.10`

#### Rules
- `N` is a chronological draft counter
- No use of MINOR or PATCH
- Each Pre-Alpha version represents a **feature-complete draft for its scope**
- Drafts are immutable once tagged

---

### 2.2 Alpha Phase

#### Intent
Alpha indicates that **architecture is stable** and feature development proceeds within defined constraints.

#### First Alpha Release

0.1.0-alpha

#### Version Format

0.MINOR.0-alpha

Examples:
- `0.1.0-alpha`
- `0.2.0-alpha`

#### Rules
- MINOR increments reflect meaningful feature expansion
- PATCH remains `0`
- No numeric alpha sequencing (`alpha.1`, `alpha.2`) is used
- Alpha is a **phase descriptor**, not a counter

---

### 2.3 Beta Phase

#### Intent
Beta represents **feature completeness** and a shift to stabilization, validation, and refinement.

#### Version Format

0.MINOR.0-beta

Examples:
- `0.1.0-beta`
- `0.2.0-beta`

#### Rules
- No new features without explicit approval
- Focus on correctness, performance, and compatibility
- PATCH remains `0`

---

### 2.4 Release Candidates (RC)

#### Intent
Release Candidates are production-grade builds intended for final validation.

#### Version Format

MAJOR.MINOR.PATCH-rc.N

Examples:
- `1.0.0-rc.1`
- `1.0.1-rc.2`

#### Use Cases
- Final QA
- Security review
- Integration validation
- Controlled production testing

---

### 2.5 General Availability (Stable)

#### Intent
Stable releases are fully validated and production-ready.

#### Version Format

MAJOR.MINOR.PATCH

Examples:
- `1.0.0`
- `1.1.2`

---

## 3. Version Authority

- Versions are set **only** during release preparation
- Contributors do not modify version numbers unless explicitly tasked
- Version changes are always accompanied by:
  - Release notes
  - Changelog updates
  - Tagged commits

---

## 4. Version Guarantees

| Phase       | Backward Compatibility | Breaking Changes |
| ----------- | ---------------------- | ---------------- |
| Pre-Alpha   | None                   | Allowed          |
| Alpha       | Best-effort            | Discouraged      |
| Beta        | Expected               | Strongly limited |
| RC / Stable | Required               | Only via MAJOR   |

---

## 5. Summary

This versioning strategy:

- Strictly complies with SemVer 2.0.0
- Avoids false precision during early development
- Communicates stability clearly
- Scales cleanly from experimentation to production