"""Register OneWeb LTEF tools with MCP."""

from mcp.server.fastmcp import FastMCP

from .tools import TOOLS


def register(mcp: FastMCP) -> None:
    for tool in TOOLS:
        mcp.add_tool(tool, name=f"oneweb_ephemeris_{tool.__name__}")
