# `data_utils` Module

**Module:** `teamdynamix.tools.data_utils`  
**Purpose:** Shared local data-path, string-normalization, and file-fingerprint helpers

`data_utils` is the single canonical home for helpers shared by local script
tooling. It does not import Session, authentication, transport, API clients, or
other workflow components.

## Public API

### `resolve_data_path(path, base_dir=None, env_var="TDX_DATA_DIR")`

Returns a `Path` using this precedence:

1. An absolute input path is returned unchanged.
2. An existing path beneath `base_dir` is returned.
3. An existing path beneath the configured environment directory is returned.
4. The path is returned beneath the current working directory, whether or not
   it exists.

```python
from teamdynamix.tools import resolve_data_path

input_path = resolve_data_path("input.csv")
```

The function resolves location only; callers decide whether a path must exist.

### `clean_key(value)`

Trims whitespace and removes one matching pair of surrounding single or double
quotes.

### `clean_str(value)`

Maps `None` to an empty string, applies `clean_key` to strings, and converts
other values with `str()`.

## File fingerprints

`compute_fingerprint(path)` returns an immutable `FileFingerprint` containing
the absolute resolved path, hash algorithm and digest, nanosecond modification
time, CSV data-row count, and ordered header columns. By default, identity is
determined by the digest, columns, row count, and modification time. The path is
recorded for diagnostics but does not make two otherwise identical files differ.

```python
from teamdynamix.tools import compute_fingerprint, fingerprints_match

before = compute_fingerprint("input.csv")
after = compute_fingerprint("input.csv")
assert fingerprints_match(before, after)
```

`compare_fingerprint(left, right)` returns a `FingerprintDiff` whose
`mismatches` map contains `(left, right)` values for each differing field.
`assert_fingerprint_match(left, right)` raises `FingerprintMismatchError` with
the same structured mismatch details when identity cannot be established.

The comparison always checks the selected algorithm and the ordered
`fingerprint_fields` policy, then checks the union of fields declared by both
fingerprints. `fingerprint_version` is optional and can be included in
`fingerprint_fields` when a workflow needs version-sensitive identity.
