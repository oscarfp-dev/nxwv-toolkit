"""OpsCenter antenna telemetry tool."""

from typing import Any

from ..response import request_result


async def get_antenna_data(antenna_id: str) -> dict[str, Any]:
    """Get live OpsCenter Poller antenna telemetry by antenna ID (not IMEI)."""
    return await request_result("data", antenna_id)
