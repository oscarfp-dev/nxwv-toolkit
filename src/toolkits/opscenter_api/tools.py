"""OpsCenter tools expose native API responses without schema transformations."""

from typing import Any

import httpx

from .client import request


async def _result(endpoint: str, antenna_id: str) -> dict[str, Any]:
    try:
        return {"ok": True, "data": await request(endpoint, antenna_id)}
    except (ValueError, httpx.HTTPError) as exc:
        return {"ok": False, "error": str(exc)}


async def get_antenna_data(antenna_id: str) -> dict[str, Any]:
    """Get live OpsCenter Poller antenna telemetry by antenna ID (not IMEI)."""
    return await _result("data", antenna_id)


async def get_antenna_info(antenna_id: str) -> dict[str, Any]:
    """Get OpsCenter Poller antenna metadata, firmware and blockage zones by antenna ID."""
    return await _result("info", antenna_id)
