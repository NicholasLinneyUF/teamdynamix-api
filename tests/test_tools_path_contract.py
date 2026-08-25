from teamdynamix import tools
from teamdynamix.tools import csv_utils, data_utils, sqlite_utils


def test_tools_package_exposes_only_the_canonical_public_path_helper() -> None:
    assert tools.resolve_data_path is data_utils.resolve_data_path
    assert "resolve_data_path" in tools.__all__
    assert "clean_key" in tools.__all__
    assert "clean_str" in tools.__all__


def test_legacy_tools_modules_do_not_expose_path_helper_aliases() -> None:
    assert not hasattr(csv_utils, "resolve_data_path")
    assert not hasattr(sqlite_utils, "resolve_data_path")
    assert not hasattr(tools, "resolve_csv_data_path")
    assert not hasattr(tools, "resolve_sqlite_data_path")
