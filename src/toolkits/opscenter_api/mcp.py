"""Register read-only OpsCenter API tools."""

from mcp.server.fastmcp import FastMCP

from .tools import get_antenna_data, get_antenna_info


def register(mcp: FastMCP) -> None:
    mcp.add_tool(get_antenna_data, name="opscenter_api_get_antenna_data")
    mcp.add_tool(get_antenna_info, name="opscenter_api_get_antenna_info")
