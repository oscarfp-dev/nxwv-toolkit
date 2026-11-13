"""Execute declarative Intellian HTTP tools through the shared client."""

from typing import Any

from core import HttpClient, HttpTool

from .config import resolve_auth


async def request(tool: HttpTool, url: str, auth_type: str, username: str, secret_env: str) -> Any:
    auth = resolve_auth(auth_type, username, secret_env)
    return await tool.run(HttpClient(url, auth=auth))
