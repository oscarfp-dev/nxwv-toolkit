import base64

import httpx
import pytest

from core import BasicAuth, BearerAuth, HttpClient


@pytest.mark.parametrize("scheme", ["http", "https"])
@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "PATCH", "DELETE"])
@pytest.mark.asyncio
async def test_methods_and_schemes(scheme: str, method: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == method
        assert str(request.url) == f"{scheme}://example.test/status"
        return httpx.Response(200, json={"ok": True})

    client = HttpClient(f"{scheme}://example.test", transport=httpx.MockTransport(handler))
    response = await client.request(method, "/status")
    assert response.json() == {"ok": True}


@pytest.mark.asyncio
async def test_basic_auth() -> None:
    expected = "Basic " + base64.b64encode(b"user:secret").decode()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == expected
        return httpx.Response(200)

    client = HttpClient(
        "https://example.test",
        auth=BasicAuth("user", "secret"),
        transport=httpx.MockTransport(handler),
    )
    await client.request("GET", "/")


@pytest.mark.asyncio
async def test_bearer_auth() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200)

    client = HttpClient(
        "https://example.test",
        auth=BearerAuth("token"),
        transport=httpx.MockTransport(handler),
    )
    await client.request("GET", "/")


@pytest.mark.asyncio
async def test_no_auth_by_default() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "Authorization" not in request.headers
        return httpx.Response(200)

    await HttpClient("http://example.test", transport=httpx.MockTransport(handler)).request(
        "GET", "/"
    )


@pytest.mark.asyncio
async def test_http_error_propagates() -> None:
    client = HttpClient(
        "https://example.test",
        transport=httpx.MockTransport(lambda _: httpx.Response(401)),
    )
    with pytest.raises(httpx.HTTPStatusError) as exc:
        await client.request("GET", "/status")
    assert exc.value.response.status_code == 401


def test_requires_http_scheme() -> None:
    with pytest.raises(ValueError):
        HttpClient("example.test")


@pytest.mark.asyncio
async def test_redirect_is_error_without_following() -> None:
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(302, headers={"location": "https://login.example.test/"})

    client = HttpClient("https://example.test", transport=httpx.MockTransport(handler))
    with pytest.raises(httpx.HTTPStatusError) as exc:
        await client.request("GET", "/status")
    assert exc.value.response.status_code == 302
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_redirect_rejected_without_location() -> None:
    client = HttpClient(
        "https://example.test",
        transport=httpx.MockTransport(lambda _: httpx.Response(307)),
    )
    with pytest.raises(httpx.HTTPStatusError) as exc:
        await client.request("GET", "/status")
    assert exc.value.response.status_code == 307
