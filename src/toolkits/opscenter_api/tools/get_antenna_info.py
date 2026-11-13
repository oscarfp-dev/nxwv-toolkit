"""OpsCenter antenna metadata tool."""

from typing import Any

from ..response import request_result


async def get_antenna_info(antenna_id: str) -> dict[str, Any]:
    """Get OpsCenter Poller antenna metadata, firmware and blockage zones by antenna ID."""
    return await request_result("info", antenna_id)
