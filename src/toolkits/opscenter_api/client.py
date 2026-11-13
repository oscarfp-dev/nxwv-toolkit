"""OpsCenter read-only requests via the shared HTTP client."""

import re
from typing import Any

from core import HttpClient

from .config import load_config, read_cookie


async def request(endpoint: str, antenna_id: str) -> Any:
    """Return unmodified antenna JSON; cookie stays private to the MCP process."""
    if endpoint not in {"data", "info"}:
        raise ValueError("Unsupported OpsCenter endpoint")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", antenna_id):
        raise ValueError("antenna_id must contain only letters, numbers, '_' or '-'")
    config = load_config()
    response = await HttpClient(config.base_url, timeout=20.0).request(
        "GET",
        f"/api/v1/antennas/{endpoint}/{antenna_id}",
        headers={"Cookie": read_cookie(config.cookie_file), "Accept": "application/json"},
    )
    return response.json()
