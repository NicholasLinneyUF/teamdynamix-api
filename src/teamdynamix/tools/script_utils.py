"""Neutral command-line parsing helpers for script-oriented tooling.

The module defines common arguments and normalizes parsed values. It does not
load files, create databases, configure logging, authenticate, create SDK
sessions, or execute workflow behavior.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .data_utils import resolve_data_path


def _path_default(value: str | Path | None) -> Path | None:
    return None if value is None else Path(value)


def build_parser(
    *,
    description: str,
    default_csv_path: str | Path | None = None,
    default_db_path: str | Path | None = None,
    default_config_path: str | Path | None = None,
    default_log_dir: str | Path | None = None,
    default_sleep_seconds: float | None = None,
    include_mode: bool = True,
    include_paths: bool = True,
    include_logging: bool = True,
    include_sleep: bool = True,
    include_dry_run: bool = True,
) -> argparse.ArgumentParser:
    """Build an extensible parser containing the requested baseline sections.

    Parsing does not interpret workflow behavior. In particular, ``dry_run``
    and the selected mode are values for the calling script to enforce.
    """
    parser = argparse.ArgumentParser(description=description)

    if include_mode:
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument("--new", action="store_true", help="Start a new workflow.")
        mode.add_argument(
            "--overwrite",
            action="store_true",
            help="Allow the calling script to replace prior workflow state.",
        )
        mode.add_argument(
            "--resume",
            action="store_true",
            help="Resume workflow state according to the calling script.",
        )

    if include_paths:
        parser.add_argument(
            "--csv-path",
            type=Path,
            default=_path_default(default_csv_path),
            help="CSV input path.",
        )
        parser.add_argument(
            "--db-path",
            type=Path,
            default=_path_default(default_db_path),
            help="Local tracker database path.",
        )
        parser.add_argument(
            "--config-path",
            type=Path,
            default=_path_default(default_config_path),
            help="Configuration file path.",
        )

    if include_logging:
        parser.add_argument(
            "--log-dir",
            type=Path,
            default=_path_default(default_log_dir),
            help="Log output directory.",
        )
        parser.add_argument("--log-level", default="INFO", help="Requested log level.")
        parser.add_argument(
            "--log-console",
            action="store_true",
            default=False,
            help="Request console log output.",
        )

    if include_sleep:
        parser.add_argument(
            "--sleep-seconds",
            type=float,
            default=default_sleep_seconds,
            help="Requested delay between operations.",
        )

    if include_dry_run:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Request a non-mutating run; enforcement belongs to the script.",
        )

    return parser


def get_mode(args: argparse.Namespace) -> str:
    """Return ``new``, ``overwrite``, or ``resume``; default to ``new``."""
    for mode in ("new", "overwrite", "resume"):
        if bool(getattr(args, mode, False)):
            return mode
    return "new"


def normalize_paths(
    args: argparse.Namespace,
    *,
    env_var: str = "TDX_DATA_DIR",
) -> dict[str, Path]:
    """Resolve non-``None`` path arguments without validating their existence."""
    normalized: dict[str, Path] = {}
    for name in ("csv_path", "db_path", "config_path", "log_dir"):
        value = getattr(args, name, None)
        if value is not None:
            normalized[name] = resolve_data_path(value, env_var=env_var)
    return normalized
