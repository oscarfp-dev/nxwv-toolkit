"""OneWeb API get_user_terminal tool."""

from ..client import terminal_id
from ..response import request_result


async def get_user_terminal(imei: str, fields: str = "") -> dict[str, object]:
    """Retrieve a terminal by its 15-digit IMEI."""
    params: dict[str, str | int] | None = {"fields": fields} if fields else None
    return await request_result(
        "inventory", "GET", f"/userTerminal/{terminal_id(imei)}", params=params
    )
