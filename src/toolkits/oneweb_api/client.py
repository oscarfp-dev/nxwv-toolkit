"""OneWeb API calls; only read-only operations are exposed."""

import re
from typing import Any

from core import HttpClient

from .config import load_config


def terminal_id(imei: str) -> str:
    if not re.fullmatch(r"[0-9]{15}", imei):
        raise ValueError("imei must be a 15-digit string")
    return imei


async def request(
    service: str,
    method: str,
    path: str,
    *,
    params: dict[str, str | int] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    if method not in ("GET", "POST") or (method == "POST" and service != "performance"):
        raise ValueError("Only GET and read-only performance report POST are permitted")
    config = load_config()
    url = {
        "inventory": config.inventory_url,
        "management": config.management_url,
        "performance": config.performance_url,
    }[service]
    if not url:
        raise ValueError(f"Missing ONEWEB_{service.upper()}_URL")
    response = await HttpClient(url, auth=config.auth).request(
        method, path, params=params, json=body
    )
    try:
        return response.json()
    except ValueError:
        return response.text
