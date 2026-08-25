from teamdynamix.exceptions import (
    DataPathError,
    FingerprintMismatchError,
    HttpError,
    MigrationStateError,
    TdxError,
    ToolsError,
)


def test_http_error_formats_request_context_without_response_body() -> None:
    error = HttpError(
        status_code=403,
        method="post",
        url="https://example.teamdynamix.com/api/projects/36/resources/abc",
        response_text="sensitive response details",
    )

    assert str(error) == (
        "HTTP 403 POST https://example.teamdynamix.com/api/projects/36/resources/abc"
    )
    assert "sensitive" not in str(error)


def test_http_error_preserves_explicit_message_and_exception_hierarchy() -> None:
    error = HttpError(
        status_code=404,
        method="GET",
        url="https://example.teamdynamix.com/api/items/1",
        message="Item was not found",
    )

    assert str(error) == "Item was not found"
    assert isinstance(error, TdxError)


def test_tools_errors_are_distinct_from_api_errors_and_preserve_details() -> None:
    details = {"expected": "abc", "actual": "def"}
    error = FingerprintMismatchError("Input fingerprint changed", details=details)

    assert isinstance(error, ToolsError)
    assert not isinstance(error, TdxError)
    assert str(error) == "Input fingerprint changed"
    assert error.details is details


def test_tools_error_subclasses_share_the_local_workflow_boundary() -> None:
    assert isinstance(MigrationStateError("Tracker missing"), ToolsError)
    assert isinstance(DataPathError("Path missing"), ToolsError)
