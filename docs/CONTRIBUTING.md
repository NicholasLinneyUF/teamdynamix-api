# CONTRIBUTING.md

## Contribution Guidelines

This document defines how contributions are proposed, developed, reviewed, and merged.

All contributors — human or LLM — are expected to follow these rules.

---

## 1. Contribution Philosophy

This project prioritizes:

- Architectural integrity over speed
- Predictable behavior over cleverness
- Explicit contracts over convenience
- Long-term maintainability over short-term wins

Contributions that violate architecture or patterns will be rejected, regardless of functionality.

---

## 2. Required Reading

Before contributing, **read and understand**:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

These documents define **non-negotiable constraints**.

---

## 3. Branching Model

### Long-Lived Branches

| Branch    | Purpose                              |
| --------- | ------------------------------------ |
| `main`    | Latest stable or tagged pre-release  |
| `develop` | Integration branch for upcoming work |

---

### Short-Lived Branch Types

#### Pre-Alpha Branches

pre-alpha/N

- Used only during Pre-Alpha phase
- Tagged as `0.0.0-pre-alpha.N`
- May be rebased or force-pushed
- Typically merged once, then deleted

---

#### Feature Branches

feature/

- Branched from `develop`
- Used for new functionality
- Must not be tagged
- Merged via pull request

---

#### Bugfix Branches

bugfix/

- Used for non-urgent fixes
- Branched from `develop` or release branches
- Merged back to origin branch

---

#### Release Branches

release/x.y.z

- Branched from `develop`
- Used to stabilize a version
- Tagged sequentially as:
  - `x.y.z-alpha`
  - `x.y.z-beta`
  - `x.y.z-rc.N`
  - `x.y.z`

---

#### Hotfix Branches

hotfix/x.y.z

- Branched from `main`
- Used for urgent production fixes
- Merged into both `main` and `develop`

---

## 4. Issue Hygiene

All non-trivial work must have an associated Issue.

Issues should include:

- Clear problem statement
- Scope definition
- Acceptance criteria
- References to architecture or patterns if applicable

Compliance work should be tracked via Issues, not long-lived branches.

---

## 5. Pull Request Expectations

Every PR must:

- Reference at least one Issue
- Describe **what** changed and **why**
- Confirm architectural compliance
- Avoid mixing unrelated changes

Large PRs should be split unless explicitly justified.

---

## 6. Commit Message Convention

Use the following format:

:

Allowed types:

- `feat`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

Examples:

- `feat: add projects client with full endpoint coverage`
- `refactor: centralize PATCH handling in Transport`

---

## 7. Versioning Responsibilities

Contributors **must not**:

- Bump versions arbitrarily
- Create tags without approval
- Modify release metadata

Version changes occur only during:

- Release branch preparation
- Explicit release tasks

---

## 8. Testing Expectations

- New features require tests when feasible
- Pre-Alpha allows limited test coverage, but correctness is still expected
- API-breaking changes must be explicitly documented

---

## 9. LLM Contributions

LLM-assisted contributions are welcome, provided that:

- Output conforms to documented patterns
- Architecture constraints are respected
- Generated code is reviewed critically

LLMs should be guided using `code_agent.md`.

---

## 10. Enforcement

Maintainers may:

- Request revisions
- Reject PRs
- Roll back changes

Architectural violations take precedence over functionality.

---

## 11. Closing Statement

These rules exist to protect the project’s clarity, stability, and longevity.

Following them ensures that the library remains:

- Predictable
- Maintainable
- Trustworthy