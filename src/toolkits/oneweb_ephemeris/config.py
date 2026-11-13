"""Local storage configuration for OneWeb LTEF snapshots."""

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Config:
    directory: Path
    source_url: str
    base_url: str
    source_path: str


def load_config() -> Config:
    default = Path.home() / ".local/share/nxwv-toolkit/ephemeris"
    directory = Path(os.getenv("ONEWEB_EPHEMERIS_DIR", str(default))).expanduser()
    source_url = os.getenv("ONEWEB_EPHEMERIS_URL", "").strip()
    parsed = urlsplit(source_url)
    if parsed.scheme != "https" or not parsed.netloc or not parsed.path:
        raise ValueError("ONEWEB_EPHEMERIS_URL must be a complete HTTPS URL")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("ONEWEB_EPHEMERIS_URL must not contain credentials or fragments")
    return Config(
        directory=directory,
        source_url=source_url,
        base_url=f"{parsed.scheme}://{parsed.netloc}",
        source_path=parsed.path + (f"?{parsed.query}" if parsed.query else ""),
    )
