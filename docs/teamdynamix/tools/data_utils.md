# `data_utils` Module

**Module:** `teamdynamix.tools.data_utils`  
**Purpose:** Shared local data-path and string-normalization helpers

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
