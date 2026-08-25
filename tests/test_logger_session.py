from pathlib import Path

from teamdynamix import Config, Logger, Session


def _config(log_dir: Path) -> Config:
    return Config(
        tenant="example.teamdynamix.com",
        environment="TD",
        beid="example-beid",
        webserviceskey="example-key",
        log_dir=str(log_dir),
        log_console=False,
    )


def test_logger_uses_default_name_prefix(tmp_path: Path) -> None:
    logger = Logger(log_dir=tmp_path, console=False)

    assert logger.log_file.parent == tmp_path
    assert logger.log_file.name.startswith("log-")
    assert logger.log_file.suffix == ".txt"


def test_session_forwards_custom_name_prefix(tmp_path: Path) -> None:
    session = Session(_config(tmp_path), name_prefix="log-mytool")

    assert session.logger.log_file.name.startswith("log-mytool-")
    session.log("session initialized")
    assert session.logger.log_file.exists()


def test_session_without_name_prefix_preserves_default(tmp_path: Path) -> None:
    session = Session(_config(tmp_path))

    assert session.logger.log_file.name.startswith("log-")
