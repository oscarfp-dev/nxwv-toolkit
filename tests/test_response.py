"""Common response envelopes do not leak sensitive request URLs."""

import httpx

from core.response import failure, success


def test_success_preserves_data() -> None:
    data = {"unknown": [1, None]}
    assert success(data) == {"ok": True, "data": data}


def test_http_error_has_status_without_request_url() -> None:
    request = httpx.Request("GET", "https://example.test/?token=private")
    response = httpx.Response(403, request=request)
    exc = httpx.HTTPStatusError("request failed", request=request, response=response)
    assert failure(exc) == {"ok": False, "status": 403, "error": "HTTP 403: request failed"}


def test_validation_error_has_null_status() -> None:
    assert failure(ValueError("invalid id")) == {"ok": False, "status": None, "error": "invalid id"}
