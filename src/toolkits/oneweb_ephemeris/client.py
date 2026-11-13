"""Download OneWeb LTEF using the shared HTTP client."""

from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime

from core import HttpClient

from .config import Config


@dataclass(frozen=True)
class Download:
    content: bytes
    source_last_modified: datetime | None
    source_etag: str | None


async def download(config: Config) -> Download:
    response = await HttpClient(config.base_url, timeout=60.0).request(
        "GET", config.source_path, headers={"Accept": "text/csv"}
    )
    content = response.content
    if not content.strip():
        raise ValueError("OneWeb LTEF response is empty")
    modified = response.headers.get("Last-Modified")
    parsed = parsedate_to_datetime(modified) if modified else None
    if parsed is not None and parsed.tzinfo is None:
        raise ValueError("OneWeb LTEF Last-Modified header has no timezone")
    return Download(
        content=content, source_last_modified=parsed, source_etag=response.headers.get("ETag")
    )
