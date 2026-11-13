"""Intellian MCP result handling."""

from typing import Any

import httpx

from core import HttpTool
from core.response import failure, success

from .client import request


async def request_result(
    tool: HttpTool, url: str, auth_type: str, username: str, secret_env: str
) -> dict[str, Any]:
    try:
        return success(await request(tool, url, auth_type, username, secret_env))
    except (ValueError, httpx.HTTPError) as exc:
        return failure(exc)
