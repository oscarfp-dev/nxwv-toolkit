"""OneWeb API MCP adapter with business-level arguments."""

from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from .client import request, terminal_id


async def _result(
    service: str,
    method: str,
    path: str,
    *,
    params: dict[str, str | int] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, object]:
    try:
        data = await request(service, method, path, params=params, body=body)
    except httpx.HTTPStatusError as exc:
        return {"ok": False, "status": exc.response.status_code, "error": str(exc)}
    except httpx.RequestError as exc:
        return {"ok": False, "status": None, "error": str(exc)}
    return {"ok": True, "data": data}


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
    return await _result("inventory", "GET", "/userTerminal", params=params)


async def get_user_terminal(imei: str, fields: str = "") -> dict[str, object]:
    """Retrieve a terminal by its 15-digit IMEI."""
    params: dict[str, str | int] | None = {"fields": fields} if fields else None
    return await _result("inventory", "GET", f"/userTerminal/{terminal_id(imei)}", params=params)


async def upgrade_status(imei: str) -> dict[str, object]:
    """Read the latest firmware upgrade status for a terminal."""
    return await _result("management", "GET", f"/userTerminal/{terminal_id(imei)}/upgrade-status")


async def available_installer_bundles(imei: str) -> dict[str, object]:
    """Read available firmware installer bundles for a terminal."""
    return await _result(
        "management", "GET", f"/userTerminal/{terminal_id(imei)}/availableInstallerBundles"
    )


async def reboot_status(imei: str) -> dict[str, object]:
    """Read the latest reboot status for a terminal; does not initiate a reboot."""
    return await _result("management", "GET", f"/userTerminal/{terminal_id(imei)}/reboot-status")


async def mute_status(imei: str) -> dict[str, object]:
    """Read the latest mute status for a terminal; does not change mute state."""
    return await _result("management", "GET", f"/userTerminal/{terminal_id(imei)}/mute-status")


async def performance_report(payload: dict[str, Any]) -> dict[str, object]:
    """Retrieve a OneWeb performance report using the RAML-defined read-only POST.

    Payload must follow the chosen metric's reportingTimeframe and performanceJob schema.
    This endpoint returns report data (201) and does not change terminal state.
    """
    if not isinstance(payload.get("reportingTimeframe"), dict):
        raise ValueError("payload must contain reportingTimeframe")
    if not isinstance(payload.get("performanceJob"), dict):
        raise ValueError("payload must contain performanceJob")
    return await _result("performance", "POST", "/performanceReport", body=payload)


def register(mcp: FastMCP) -> None:
    for tool in (
        list_user_terminals,
        get_user_terminal,
        upgrade_status,
        available_installer_bundles,
        reboot_status,
        mute_status,
        performance_report,
    ):
        mcp.add_tool(tool, name=f"oneweb_api_{tool.__name__}")
