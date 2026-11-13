"""OpsCenter tools expose native API responses without schema transformations."""

from typing import Any

import httpx

from core.response import failure, success

from .client import request


async def request_result(endpoint: str, antenna_id: str) -> dict[str, Any]:
    try:
        return success(await request(endpoint, antenna_id))
    except (ValueError, httpx.HTTPError) as exc:
        return failure(exc)
