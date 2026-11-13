"""OneWeb API response handling."""

from typing import Any

import httpx

from core.response import failure, success

from .client import request


async def request_result(
    service: str,
    method: str,
    path: str,
    *,
    params: dict[str, str | int] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, object]:
    try:
        data = await request(service, method, path, params=params, body=body)
    except (ValueError, httpx.HTTPError) as exc:
        return failure(exc)
    return success(data)
