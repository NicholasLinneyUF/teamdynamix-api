# `script_utils` Module

**Module:** `teamdynamix.tools.script_utils`  
**Purpose:** Neutral, reusable command-line argument definitions and normalization

`script_utils` standardizes the interface shared by script-oriented workflows.
It parses values only. It does not load files, create databases, configure
logging, authenticate, construct SDK sessions, or execute work.

## `build_parser(...)`

Creates an extensible `argparse.ArgumentParser`. Optional sections provide:

- Mutually exclusive `--new`, `--overwrite`, and `--resume` flags
- CSV, database, configuration, and log paths
- Log level and console-output requests
- Sleep throttling
- A dry-run request

```python
from teamdynamix.tools.script_utils import build_parser

parser = build_parser(
    description="Import TeamDynamix records",
    default_csv_path="input.csv",
    default_db_path="tracker.db",
)
parser.add_argument("--application-id", type=int, required=True)
args = parser.parse_args()
```

The calling script remains responsible for enforcing mode and dry-run behavior.

## `get_mode(args)`

Returns `"new"`, `"overwrite"`, or `"resume"`. When no mode flag is set, the
deterministic default is `"new"`.

## `normalize_paths(args, env_var="TDX_DATA_DIR")`

Returns a `dict[str, Path]` for non-null `csv_path`, `db_path`, `config_path`,
and `log_dir` attributes. Resolution delegates to the canonical
`data_utils.resolve_data_path`; it does not require paths to exist.
