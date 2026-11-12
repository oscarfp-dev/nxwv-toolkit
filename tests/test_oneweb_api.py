"""OneWeb read-only adapter tests without network access."""

from typing import Any

import httpx
import pytest

from core import HttpClient
from toolkits.oneweb_api import mcp as oneweb


@pytest.mark.asyncio
async def test_terminal_get_uses_configured_url_and_params(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ONEWEB_INVENTORY_URL", "https://example.test/inventory/v3")
    monkeypatch.setenv("ONEWEB_USERNAME", "test")
    monkeypatch.setenv("ONEWEB_PASSWORD", "secret")

    async def fake_request(
        self: HttpClient,
        method: str,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
        json: object = None,
    ) -> httpx.Response:
        assert self.base_url == "https://example.test/inventory/v3"
        assert method == "GET"
        assert path == "/userTerminal/350357139990004"
        assert params == {"fields": "imei,name"}
        return httpx.Response(
            200,
            json={"imei": "350357139990004"},
            request=httpx.Request(
                "GET", "https://example.test/inventory/v3/userTerminal/350357139990004"
            ),
        )

    monkeypatch.setattr(HttpClient, "request", fake_request)
    result = await oneweb.get_user_terminal("350357139990004", fields="imei,name")
    assert result == {"ok": True, "data": {"imei": "350357139990004"}}


@pytest.mark.asyncio
async def test_invalid_imei_rejected() -> None:
    with pytest.raises(ValueError, match="15-digit"):
        await oneweb.reboot_status("../bad")


@pytest.mark.asyncio
async def test_performance_report_uses_read_only_post(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ONEWEB_PERFORMANCE_URL", "https://example.test/performance/v2")
    monkeypatch.setenv("ONEWEB_USERNAME", "test")
    monkeypatch.setenv("ONEWEB_PASSWORD", "secret")
    payload: dict[str, Any] = {"reportingTimeframe": {}, "performanceJob": {}}

    async def fake_request(
        self: HttpClient,
        method: str,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
        json: object = None,
    ) -> httpx.Response:
        assert method == "POST"
        assert path == "/performanceReport"
        assert json == payload
        return httpx.Response(
            201,
            json={"report": []},
            request=httpx.Request("POST", "https://example.test/performance/v2/performanceReport"),
        )

    monkeypatch.setattr(HttpClient, "request", fake_request)
    result = await oneweb.performance_report(payload)
    assert result == {"ok": True, "data": {"report": []}}


@pytest.mark.asyncio
async def test_mutating_post_rejected() -> None:
    from toolkits.oneweb_api.client import request

    with pytest.raises(ValueError, match="Only GET"):
        await request("management", "POST", "/userTerminal/123/reboot")
