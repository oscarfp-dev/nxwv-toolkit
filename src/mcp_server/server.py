"""Expose registered HTTP tools over local MCP stdio."""

import os

import httpx
from mcp.server.fastmcp import FastMCP

from core import BasicAuth, BearerAuth, HttpClient, HttpTool
from toolkits import TOOLS

mcp = FastMCP("nxwv-toolkit")


def make_handler(tool: HttpTool):
    async def execute(
        url: str,
        auth_type: str = "none",
        username: str = "",
        secret_env: str = "",
    ) -> dict[str, object]:
        """Run against a URL. Optional auth: basic/bearer, with secret_env variable name."""
        auth: BasicAuth | BearerAuth | None = None
        if auth_type != "none":
            if auth_type not in ("basic", "bearer"):
                raise ValueError("auth_type must be none, basic, or bearer")
            if not secret_env:
                raise ValueError("secret_env is required for authentication")
            secret = os.environ.get(secret_env)
            if not secret:
                raise ValueError(f"Missing environment variable: {secret_env}")
            if auth_type == "basic":
                if not username:
                    raise ValueError("username is required for basic authentication")
                auth = BasicAuth(username, secret)
            else:
                auth = BearerAuth(secret)
        try:
            data = await tool.run(HttpClient(url, auth=auth))
        except httpx.HTTPStatusError as exc:
            return {"ok": False, "status": exc.response.status_code, "error": str(exc)}
        except httpx.RequestError as exc:
            return {"ok": False, "status": None, "error": str(exc)}
        return {"ok": True, "data": data}

    return execute


for tool_name, declaration in TOOLS.items():
    mcp.add_tool(
        make_handler(declaration),
        name=tool_name.replace(".", "_"),
        description=declaration.description,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
