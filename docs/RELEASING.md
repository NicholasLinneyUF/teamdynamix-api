# RELEASING.md
## Release Process Checklist

This document defines the **authoritative checklist** for preparing, validating, tagging, and publishing a new release of the TeamDynamix API Python client.

Every release — pre-alpha, alpha, beta, RC, or stable — must follow this process.

---

## 0. Preconditions

Before starting a release:

- All intended work for the release is complete
- All related Issues are closed or explicitly deferred
- The working tree is clean
- CI (if present) is passing
- The release scope is clearly defined

---

## 1. Version Planning

- [ ] Confirm the **target version** (e.g. `0.0.0-pre-alpha.11`, `0.1.0-alpha`)
- [ ] Confirm lifecycle phase (Pre-Alpha / Alpha / Beta / RC / Stable)
- [ ] Confirm compatibility expectations for this release
- [ ] Confirm whether this is:
  - Feature snapshot
  - Bugfix release
  - Architecture milestone

---

## 2. Documentation Updates (Required)

### Core Project Documents

These **must** be reviewed and updated as applicable:

- [ ] `VERSION.md`
  - Replace entirely with release-specific content
  - Describe what is unique to this version
- [ ] `CHANGELOG.md`
  - Add a new entry at the top
  - Accurately list all changes in this release
- [ ] `README.md`
  - Verify version string
  - Update status notes if lifecycle phase changed

### Architecture & Process Docs

Review for accuracy; update only if changes occurred:

- [ ] `ARCHITECTURE.md`
- [ ] `DESIGN.md`
- [ ] `PATTERNS.md`
- [ ] `CONTRIBUTING.md`
- [ ] `VERSIONING.md`
- [ ] `CODE_AGENT.md`
- [ ] `ABSTRACT.md`

> These documents should only change when the underlying rules or philosophy change.

---

## 3. Module-Level Documentation (Selective)

The following files live under `docs/teamdynamix/` and act as **module reference guides**.

Update **only** if the corresponding module changed:

- [ ] `accounts.md`
- [ ] `applications.md`
- [ ] `attributes.md`
- [ ] `auth.md`
- [ ] `config.md`
- [ ] `events.md`
- [ ] `exceptions.md`
- [ ] `functional_roles.md`
- [ ] `groups.md`
- [ ] `people.md`
- [ ] `projects.md`
- [ ] `service_catalog.md`
- [ ] `session.md`
- [ ] `tickets.md`
- [ ] `transport.md`

---

## 4. Code Review and Validation

- [ ] Verify no architecture violations were introduced
- [ ] Verify no direct `requests.*` calls outside Transport
- [ ] Verify constructors remain side-effect free
- [ ] Verify PATCH behavior is centralized in Transport
- [ ] Verify public API surface matches `__all__`
- [ ] Verify logging defaults behave as intended
- [ ] Verify config defaults allow minimal startup

---

## 5. Tests

- [ ] Run all existing tests
- [ ] Manually validate critical workflows if tests are limited
- [ ] Ensure test failures are either:
  - Fixed, or
  - Explicitly documented as known limitations

---

## 6. Version Metadata Updates

- [ ] Update version string in:
  - `src/teamdynamix/__init__.py`
- [ ] Verify version matches:
  - `VERSION.md`
  - `CHANGELOG.md`
- [ ] Ensure version string conforms to SemVer and project rules

---

## 7. Git Branch Preparation

### Pre-Alpha Releases

- [ ] Ensure work is on `pre-alpha/N` branch
- [ ] Ensure branch represents a **feature-complete snapshot**
- [ ] Merge `pre-alpha/N` → `main` (fast-forward preferred)
- [ ] Delete branch after merge (optional)

### Alpha and Later Releases

- [ ] Create or update `release/x.y.z` branch
- [ ] Freeze feature work
- [ ] Allow only fixes and documentation changes

---

## 8. Commit Hygiene

- [ ] Ensure commits are logically grouped
- [ ] Ensure commit messages follow project conventions
- [ ] Avoid mixing unrelated changes
- [ ] Squash commits if necessary for clarity

---

## 9. Tagging

- [ ] Create an **annotated Git tag** matching the version exactly
- [ ] Tag must point to the merge commit on the correct branch
- [ ] Tags are immutable once created

Examples:

```bash
git tag -a 0.0.0-pre-alpha.10 -m "Pre-Alpha 10: architecture-stabilized snapshot"
git push --tags
```

------

## 10. Release Publication (Optional but Recommended)

If using a platform with releases (GitHub/GitLab/Gitea):

-  Publish a release from the tag
-  Copy summary from `VERSION.md`
-  Link to `CHANGELOG.md`
-  Clearly mark pre-release status if applicable

------

## 11. Post-Release Cleanup

-  Close remaining Issues tied to the release
-  Update milestone status (if used)
-  Verify documentation links remain correct
-  Prepare next development branch if applicable

------

## 12. Final Verification

Before declaring the release complete:

-  Repository builds cleanly
-  Documentation accurately reflects reality
-  Version identifiers are consistent everywhere
-  No uncommitted changes remain

------

## Release Invariant

A release must be:

- Internally consistent
- Architecturally compliant
- Accurately documented
- Reproducible from the tagged commit

If any of these conditions are not met, **do not release**.

------

## Closing Note

Releases are **communication artifacts**, not just code snapshots.

This checklist exists to ensure that every release:

- Can be trusted
- Can be understood
- Can be built upon

Follow it exactly.