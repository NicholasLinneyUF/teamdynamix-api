from teamdynamix.exceptions import HttpError, TdxError


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
