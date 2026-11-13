"""Register read-only OpsCenter API tools."""

from mcp.server.fastmcp import FastMCP

from .tools import TOOLS


def register(mcp: FastMCP) -> None:
    for tool in TOOLS:
        mcp.add_tool(tool, name=f"opscenter_api_{tool.__name__}")
