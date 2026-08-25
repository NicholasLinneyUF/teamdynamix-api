import argparse
from pathlib import Path

import pytest

from teamdynamix.tools.script_utils import build_parser, get_mode, normalize_paths


def test_build_parser_includes_and_parses_the_full_baseline() -> None:
    parser = build_parser(
        description="Import records",
        default_csv_path="input.csv",
        default_db_path=Path("tracker.db"),
        default_config_path="config.ini",
        default_log_dir="logs",
        default_sleep_seconds=0.5,
    )
    args = parser.parse_args(
        [
            "--resume",
            "--csv-path",
            "override.csv",
            "--log-level",
            "DEBUG",
            "--log-console",
            "--sleep-seconds",
            "1.25",
            "--dry-run",
        ]
    )

    assert parser.description == "Import records"
    assert args.resume is True
    assert args.new is False
    assert args.overwrite is False
    assert args.csv_path == Path("override.csv")
    assert args.db_path == Path("tracker.db")
    assert args.config_path == Path("config.ini")
    assert args.log_dir == Path("logs")
    assert args.log_level == "DEBUG"
    assert args.log_console is True
    assert args.sleep_seconds == 1.25
    assert args.dry_run is True


def test_build_parser_sections_are_optional_and_parser_is_extensible() -> None:
    parser = build_parser(
        description="Minimal",
        include_mode=False,
        include_paths=False,
        include_logging=False,
        include_sleep=False,
        include_dry_run=False,
    )
    parser.add_argument("--custom", required=True)

    assert vars(parser.parse_args(["--custom", "value"])) == {"custom": "value"}


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ({}, "new"),
        ({"new": True}, "new"),
        ({"overwrite": True}, "overwrite"),
        ({"resume": True}, "resume"),
    ],
)
def test_get_mode_is_deterministic(values: dict[str, bool], expected: str) -> None:
    assert get_mode(argparse.Namespace(**values)) == expected


def test_mode_flags_are_mutually_exclusive() -> None:
    parser = build_parser(description="Modes")

    with pytest.raises(SystemExit):
        parser.parse_args(["--new", "--resume"])


def test_normalize_paths_uses_data_utils_without_requiring_all_arguments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    csv_path = data_dir / "input.csv"
    csv_path.touch()
    monkeypatch.setenv("SCRIPT_DATA_DIR", str(data_dir))
    monkeypatch.chdir(tmp_path)
    args = argparse.Namespace(csv_path=Path("input.csv"), db_path=Path("future.db"))

    normalized = normalize_paths(args, env_var="SCRIPT_DATA_DIR")

    assert normalized == {
        "csv_path": csv_path,
        "db_path": tmp_path / "future.db",
    }
