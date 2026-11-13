"""Private runtime configuration for OpsCenter API."""

import os
import stat
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    base_url: str
    cookie_file: Path


def load_config() -> Config:
    url = os.getenv("OPSCENTER_BASE_URL", "").strip().rstrip("/")
    if not url:
        raise ValueError("OPSCENTER_BASE_URL must be configured in the MCP environment")
    if not url.startswith("https://"):
        raise ValueError("OPSCENTER_BASE_URL must use HTTPS")
    cookie_file = Path(
        os.getenv(
            "OPSCENTER_COOKIE_FILE", str(Path.home() / ".config/nxwv-toolkit/auth/opscenter.cookie")
        )
    ).expanduser()
    return Config(base_url=url, cookie_file=cookie_file)


def read_cookie(path: Path) -> str:
    if path.is_symlink():
        raise ValueError("OpsCenter cookie file must not be a symbolic link")
    try:
        mode = path.stat().st_mode
        if not stat.S_ISREG(mode) or mode & 0o077:
            raise ValueError("OpsCenter cookie file must be a regular file with permissions 600")
        value = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise ValueError("OpsCenter cookie missing; configure the private cookie file") from exc
    if not value or "\n" in value or "\r" in value:
        raise ValueError("OpsCenter cookie must be a nonempty single-line Cookie header value")
    return value
