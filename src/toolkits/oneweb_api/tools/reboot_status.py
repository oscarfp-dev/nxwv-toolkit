"""OneWeb API reboot_status tool."""

from ..client import terminal_id
from ..response import request_result


async def reboot_status(imei: str) -> dict[str, object]:
    """Read the latest reboot status for a terminal; does not initiate a reboot."""
    return await request_result(
        "management", "GET", f"/userTerminal/{terminal_id(imei)}/reboot-status"
    )
