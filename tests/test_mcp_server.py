"""Tests for the MCP adapter without network access."""

import httpx
import pytest

from core import HttpClient
from mcp_server.server import mcp
from toolkits.intellian_oneweb.mcp import make_handler
from toolkits.intellian_oneweb.tools import TOOLS
from toolkits.intellian_oneweb.tools.health import health


@pytest.mark.asyncio
async def test_mcp_registered_tools() -> None:
    tools = await mcp.list_tools()
    assert {tool.name for tool in tools} == (
        {name.replace(".", "_") for name in TOOLS}
        | {
            "oneweb_api_list_user_terminals",
            "oneweb_api_get_user_terminal",
            "oneweb_api_upgrade_status",
            "oneweb_api_available_installer_bundles",
            "oneweb_api_reboot_status",
            "oneweb_api_mute_status",
            "oneweb_api_performance_report",
            "opscenter_api_get_antenna_data",
            "opscenter_api_get_antenna_info",
        }
    )


@pytest.mark.asyncio
async def test_mcp_health_tool(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_run(self: HttpClient, method: str, path: str) -> httpx.Response:
        assert self.base_url == "https://example.com"
        assert method == "GET"
        assert path == "/"
        return httpx.Response(
            200, json={"healthy": True}, request=httpx.Request("GET", "https://example.com/")
        )

    monkeypatch.setattr(HttpClient, "request", fake_run)
    result = await make_handler(health)("https://example.com")
    assert result == {"ok": True, "data": {"healthy": True}}
