"""OneWeb API list_user_terminals tool."""

from ..response import request_result


async def list_user_terminals(
    imei: str = "",
    fields: str = "",
    limit: int = 10,
    offset: int = 0,
    imsi: str = "",
    serial_number: str = "",
    product_status: str = "",
) -> dict[str, object]:
    """List or filter OneWeb terminals; limit 1-1000, offset >= 0."""
    if not 1 <= limit <= 1000 or offset < 0:
        raise ValueError("limit must be 1-1000 and offset must be nonnegative")
    params: dict[str, str | int] = {"limit": limit, "offset": offset}
    for key, value in (
        ("imei", imei),
        ("fields", fields),
        ("imsi", imsi),
        ("serialNumber", serial_number),
        ("product.status", product_status),
    ):
        if value:
            params[key] = value
    return await request_result("inventory", "GET", "/userTerminal", params=params)
