"""Register per-device Intellian HTTP tools with MCP."""

from mcp.server.fastmcp import FastMCP

from core import HttpTool

from .response import request_result
from .tools import TOOLS


def make_handler(tool: HttpTool):
    async def execute(
        url: str,
        auth_type: str = "none",
        username: str = "",
        secret_env: str = "",
    ) -> dict[str, object]:
        """Query a device URL; optionally supply basic/bearer credentials via env."""
        return await request_result(tool, url, auth_type, username, secret_env)

    return execute


def register(mcp: FastMCP) -> None:
    for name, declaration in TOOLS.items():
        mcp.add_tool(
            make_handler(declaration),
            name=name.replace(".", "_"),
            description=declaration.description,
        )
