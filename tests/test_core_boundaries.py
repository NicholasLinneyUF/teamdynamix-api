from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests

from teamdynamix import Config, Session
from teamdynamix.auth import Auth
from teamdynamix.exceptions import AuthError, HttpError, TdxRequestError, TdxTimeoutError
from teamdynamix.transport import Transport


class StubLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def log(self, message: str, **_: Any) -> None:
        self.messages.append(message)


class StubResponse:
    def __init__(self, *, status_code: int = 200, text: str = "", data: Any = None) -> None:
        self.status_code = status_code
        self.text = text
        self._data = data

    def json(self) -> Any:
        return self._data


def _config(log_dir: Path, *, auth_mode: str = "admin") -> Config:
    values: dict[str, Any] = {
        "tenant": "example.teamdynamix.com",
        "environment": "TD",
        "auth_mode": auth_mode,
        "log_dir": str(log_dir),
        "log_console": False,
    }
    if auth_mode == "admin":
        values.update(beid="example-beid", webserviceskey="example-key")
    else:
        values.update(username="example-user", password="example-password")
    return Config(**values)


def test_transport_returns_successful_response_and_applies_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    response = StubResponse(status_code=200, data={"ok": True})
    request = MagicMock(return_value=response)
    monkeypatch.setattr(requests, "request", request)

    transport = Transport(logger=StubLogger(), default_timeout=12)
    result = transport.request("get", "https://example.test/api/items", params={"page": 2})

    assert result is response
    request.assert_called_once_with(
        method="GET",
        url="https://example.test/api/items",
        headers=None,
        params={"page": 2},
        json=None,
        data=None,
        timeout=12,
    )


def test_transport_normalizes_patch_payload_and_content_type(monkeypatch: pytest.MonkeyPatch) -> None:
    request = MagicMock(return_value=StubResponse())
    monkeypatch.setattr(requests, "request", request)

    Transport(logger=StubLogger()).request(
        "PATCH",
        "https://example.test/api/items/1",
        headers={"X-Test": "yes"},
        json={"Name": "Updated"},
    )

    kwargs = request.call_args.kwargs
    assert kwargs["json"] == [{"op": "replace", "path": "/Name", "value": "Updated"}]
    assert kwargs["headers"] == {
        "X-Test": "yes",
        "Content-Type": "application/json; charset=utf-8",
    }


def test_transport_raises_structured_http_error_without_logging_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        requests,
        "request",
        MagicMock(return_value=StubResponse(status_code=403, text="private details")),
    )

    with pytest.raises(HttpError) as raised:
        Transport(logger=StubLogger()).request("POST", "https://example.test/api/items")

    assert raised.value.status_code == 403
    assert raised.value.method == "POST"
    assert raised.value.response_text == "private details"
    assert "private details" not in str(raised.value)


@pytest.mark.parametrize(
    ("request_error", "sdk_error"),
    [
        (requests.exceptions.Timeout("slow"), TdxTimeoutError),
        (requests.exceptions.ConnectionError("offline"), TdxRequestError),
    ],
)
def test_transport_translates_requests_errors(
    monkeypatch: pytest.MonkeyPatch,
    request_error: requests.exceptions.RequestException,
    sdk_error: type[Exception],
) -> None:
    logger = StubLogger()
    monkeypatch.setattr(requests, "request", MagicMock(side_effect=request_error))

    with pytest.raises(sdk_error):
        Transport(logger=logger).request("GET", "https://example.test/api/items")

    assert logger.messages


def test_auth_builds_admin_request_and_caches_token(tmp_path: Path) -> None:
    transport = MagicMock()
    transport.request.return_value = StubResponse(text=" token-value ")
    auth = Auth(config=_config(tmp_path), logger=StubLogger(), transport=transport)

    assert auth.get_token() == "token-value"
    assert auth.get_token() == "token-value"
    assert auth.get_token(force_refresh=True) == "token-value"
    assert transport.request.call_count == 2
    transport.request.assert_called_with(
        "POST",
        "https://example.teamdynamix.com/TDWebApi/api/auth/loginadmin",
        headers={"Content-Type": "application/json; charset=utf-8"},
        json={"BEID": "example-beid", "WebServicesKey": "example-key"},
    )


def test_auth_rejects_empty_user_token(tmp_path: Path) -> None:
    transport = MagicMock()
    transport.request.return_value = StubResponse(text="  ")
    auth = Auth(
        config=_config(tmp_path, auth_mode="user"),
        logger=StubLogger(),
        transport=transport,
    )

    with pytest.raises(AuthError, match="Empty token"):
        auth.authenticate()


def test_session_request_adds_base_url_and_lazy_auth_header(tmp_path: Path) -> None:
    session = Session(_config(tmp_path))
    session.auth = MagicMock()
    session.auth.get_token.return_value = "cached-token"
    session.transport = MagicMock()
    expected = StubResponse(data={"ID": 1})
    session.transport.request.return_value = expected

    result = session.request("GET", "/api/items/1", params={"full": True})

    assert result is expected
    session.transport.request.assert_called_once_with(
        method="GET",
        url="https://example.teamdynamix.com/TDWebApi/api/items/1",
        headers={"Authorization": "Bearer cached-token"},
        params={"full": True},
        json=None,
        data=None,
        timeout=None,
    )
