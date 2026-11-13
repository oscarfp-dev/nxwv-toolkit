"""OpsCenter tools expose native API responses without schema transformations."""

from typing import Any

import httpx

from .client import request


async def request_result(endpoint: str, antenna_id: str) -> dict[str, Any]:
    try:
        return {"ok": True, "data": await request(endpoint, antenna_id)}
    except (ValueError, httpx.HTTPError) as exc:
        return {"ok": False, "error": str(exc)}
