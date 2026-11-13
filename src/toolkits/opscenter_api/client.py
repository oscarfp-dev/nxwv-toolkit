"""OpsCenter Poller client; authentication stays private to the MCP process."""

import os
import re
import stat
from pathlib import Path
from typing import Any

import httpx

DEFAULT_COOKIE_FILE = Path.home() / ".config/nxwv-toolkit/auth/opscenter.cookie"


def _cookie() -> str:
    path = Path(os.environ.get("OPSCENTER_COOKIE_FILE", str(DEFAULT_COOKIE_FILE))).expanduser()
    if path.is_symlink():
        raise ValueError("OpsCenter cookie file must not be a symbolic link")
    try:
        mode = path.stat().st_mode
        if not stat.S_ISREG(mode) or mode & 0o077:
            raise ValueError("OpsCenter cookie file must be a regular file with permissions 600")
        value = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise ValueError(
            "OpsCenter cookie missing; create ~/.config/nxwv-toolkit/auth/opscenter.cookie"
        ) from exc
    if not value or "\n" in value or "\r" in value:
        raise ValueError("OpsCenter cookie must be a nonempty single-line Cookie header value")
    return value


async def request(endpoint: str, antenna_id: str) -> Any:
    """Return the unmodified JSON payload for an antenna endpoint."""
    if endpoint not in {"data", "info"}:
        raise ValueError("Unsupported OpsCenter endpoint")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", antenna_id):
        raise ValueError("antenna_id must contain only letters, numbers, '_' or '-'")

    base_url = os.getenv("OPSCENTER_BASE_URL", "").strip().rstrip("/")
    if not base_url:
        raise ValueError("OPSCENTER_BASE_URL must be configured in the MCP environment")
    if not base_url.startswith("https://"):
        raise ValueError("OPSCENTER_BASE_URL must use HTTPS")
    async with httpx.AsyncClient(base_url=base_url, follow_redirects=False, timeout=20.0) as client:
        response = await client.get(
            f"/api/v1/antennas/{endpoint}/{antenna_id}",
            headers={"Cookie": _cookie(), "Accept": "application/json"},
        )
        if response.status_code in (301, 302, 303, 307, 308, 401, 403):
            raise ValueError(
                f"OpsCenter authentication or access failed (HTTP {response.status_code}); "
                "check the saved session cookie"
            )
        response.raise_for_status()
        return response.json()
