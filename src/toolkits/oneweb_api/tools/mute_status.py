"""OneWeb API mute_status tool."""

from ..client import terminal_id
from ..response import request_result


async def mute_status(imei: str) -> dict[str, object]:
    """Read the latest mute status for a terminal; does not change mute state."""
    return await request_result(
        "management", "GET", f"/userTerminal/{terminal_id(imei)}/mute-status"
    )
