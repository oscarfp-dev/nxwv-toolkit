import httpx
import pytest

from core import BasicAuth, HttpClient, HttpTool
from toolkits.intellian_oneweb.health import health


@pytest.mark.asyncio
async def test_health_tool_executes_get() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://antenna.test/"
        assert "Authorization" not in request.headers
        return httpx.Response(200, json={"state": "online"})

    client = HttpClient("https://antenna.test", transport=httpx.MockTransport(handler))
    response = await health.run(client)
    assert response == {"state": "online"}


@pytest.mark.asyncio
async def test_tool_uses_client_authentication() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"].startswith("Basic ")
        return httpx.Response(200)

    client = HttpClient(
        "http://antenna.test",
        auth=BasicAuth("user", "secret"),
        transport=httpx.MockTransport(handler),
    )
    await health.run(client)


def test_tool_is_declarative() -> None:
    tool = HttpTool("test", "A test tool", "GET", "/test")
    assert tool.name == "test"
    assert tool.path == "/test"
