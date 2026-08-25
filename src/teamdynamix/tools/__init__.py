# =====================================================================
# FILE: src/teamdynamix/tools/__init__.py
# =====================================================================
"""
teamdynamix.tools

Local, script-oriented helper utilities (non-HTTP).

This subpackage is intentionally independent of TeamDynamix Web API client
modules (Session/Auth/Transport). It exists to support one-time scripts and
automation workflows with predictable local data tooling.
"""

from __future__ import annotations

from .data_utils import clean_key, clean_str, resolve_data_path

# CSV utilities
from .csv_utils import (
    DEFAULT_SEPARATOR_ORD,
    CellMatch as CsvCellMatch,
    CsvTable,
    get_separator,
    get_separator_ord,
    load_csv,
    reset_separator_default,
    set_separator,
    set_separator_ord,
)

# SQLite utilities
from .sqlite_utils import (
    DEFAULT_DB_PATH,
    CellMatch as SqliteCellMatch,
    SqliteTracker,
    archive_db_file,
    backup_db_file,
    create_db_file,
)

__all__ = [
    # data_utils
    "clean_key",
    "clean_str",
    "resolve_data_path",
    # csv_utils
    "DEFAULT_SEPARATOR_ORD",
    "CsvCellMatch",
    "CsvTable",
    "get_separator",
    "get_separator_ord",
    "set_separator",
    "set_separator_ord",
    "reset_separator_default",
    "load_csv",
    # sqlite_utils
    "DEFAULT_DB_PATH",
    "SqliteCellMatch",
    "SqliteTracker",
    "create_db_file",
    "backup_db_file",
    "archive_db_file",
]
