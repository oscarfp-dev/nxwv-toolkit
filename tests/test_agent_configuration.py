"""Operational-agent configuration must be portable and MCP-enabled."""

import json
from pathlib import Path

from mcp_server.server import mcp

ROOT = Path(__file__).resolve().parents[1]


def test_shared_operational_instructions() -> None:
    instructions = (ROOT / "AGENTS.md").read_text()
    assert "operational satellite communications assistant" in instructions
    assert "not" in instructions and "software developer" in instructions
    assert "oneweb_api_*" in instructions
    assert "intellian_oneweb_*" in instructions
    assert "opscenter_api_get_antenna_data" in instructions
    assert "opscenter_api_get_antenna_info" in instructions
    assert "not for agent-driven development" in instructions
    assert "read-only" in instructions


def test_no_duplicate_claude_instructions() -> None:
    assert not (ROOT / "CLAUDE.md").exists()


def test_both_clients_use_local_mcp_entry() -> None:
    opencode = json.loads((ROOT / "opencode.json").read_text())
    claude = json.loads((ROOT / ".mcp.json").read_text())
    assert opencode["mcp"]["nxwv-toolkit"]["command"] == [
        "uv",
        "run",
        "--project",
        ".",
        "python",
        "mcp_entry.py",
    ]
    assert claude["mcpServers"]["nxwv-toolkit"]["command"] == "uv"
    assert claude["mcpServers"]["nxwv-toolkit"]["args"] == [
        "run",
        "--project",
        ".",
        "python",
        "mcp_entry.py",
    ]
    assert opencode["permission"]["edit"] == "deny"
    assert opencode["permission"]["bash"] == "deny"


async def test_operational_mcp_tool_count() -> None:
    names = {tool.name for tool in await mcp.list_tools()}
    assert len(names) == 21
    assert {"opscenter_api_get_antenna_data", "opscenter_api_get_antenna_info"} <= names
    assert {"oneweb_ephemeris_download_ltef", "oneweb_ephemeris_get_ltef_status"} <= names
