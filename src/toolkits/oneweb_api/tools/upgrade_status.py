"""OneWeb API upgrade_status tool."""

from ..client import terminal_id
from ..response import request_result


async def upgrade_status(imei: str) -> dict[str, object]:
    """Read the latest firmware upgrade status for a terminal."""
    return await request_result(
        "management", "GET", f"/userTerminal/{terminal_id(imei)}/upgrade-status"
    )
