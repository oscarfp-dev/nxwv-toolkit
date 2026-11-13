"""OneWeb API response handling."""

from typing import Any

import httpx

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
    except httpx.HTTPStatusError as exc:
        return {"ok": False, "status": exc.response.status_code, "error": str(exc)}
    except httpx.RequestError as exc:
        return {"ok": False, "status": None, "error": str(exc)}
    return {"ok": True, "data": data}
