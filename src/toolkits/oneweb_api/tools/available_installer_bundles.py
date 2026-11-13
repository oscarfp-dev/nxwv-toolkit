"""OneWeb API available_installer_bundles tool."""

from ..client import terminal_id
from ..response import request_result


async def available_installer_bundles(imei: str) -> dict[str, object]:
    """Read available firmware installer bundles for a terminal."""
    return await request_result(
        "management", "GET", f"/userTerminal/{terminal_id(imei)}/availableInstallerBundles"
    )
