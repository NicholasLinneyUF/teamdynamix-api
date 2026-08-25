from pathlib import Path

from teamdynamix.tools import clean_key, clean_str, resolve_data_path


def test_resolve_data_path_returns_absolute_input_unchanged(tmp_path: Path) -> None:
    absolute = tmp_path / "input.csv"

    assert resolve_data_path(absolute) == absolute


def test_resolve_data_path_prefers_existing_base_then_existing_environment(
    tmp_path: Path,
    monkeypatch,
) -> None:
    base_dir = tmp_path / "base"
    env_dir = tmp_path / "environment"
    base_dir.mkdir()
    env_dir.mkdir()
    base_file = base_dir / "input.csv"
    env_file = env_dir / "input.csv"
    base_file.touch()
    env_file.touch()
    monkeypatch.setenv("TDX_DATA_DIR", str(env_dir))

    assert resolve_data_path("input.csv", base_dir=base_dir) == base_file
    base_file.unlink()
    assert resolve_data_path("input.csv", base_dir=base_dir) == env_file


def test_resolve_data_path_falls_back_to_cwd_without_requiring_existence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TDX_DATA_DIR", raising=False)

    assert resolve_data_path("future.csv") == tmp_path / "future.csv"


def test_clean_key_and_clean_str_normalize_script_values() -> None:
    assert clean_key("  'Project Managed'  ") == "Project Managed"
    assert clean_key('"Hello"') == "Hello"
    assert clean_key(" Hello ") == "Hello"
    assert clean_str(None) == ""
    assert clean_str("  'value' ") == "value"
    assert clean_str(42) == "42"
