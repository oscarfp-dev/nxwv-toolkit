"""Uniform MCP result envelopes; domain payloads remain untouched."""

from typing import Any

import httpx


def success(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


def failure(exc: Exception) -> dict[str, Any]:
    status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
    if isinstance(exc, httpx.HTTPStatusError):
        message = f"HTTP {status}: request failed"
    elif isinstance(exc, httpx.RequestError):
        message = f"HTTP transport error: {type(exc).__name__}"
    else:
        message = str(exc)
    return {"ok": False, "status": status, "error": message}
