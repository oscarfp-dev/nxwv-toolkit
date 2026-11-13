"""Shared MCP result envelopes for OneWeb LTEF tools."""

from typing import Any

import httpx

from core.response import failure, success

from .client import download
from .config import load_config
from .storage import save, status


async def download_result() -> dict[str, Any]:
    try:
        config = load_config()
        return success(save(config, await download(config)))
    except (ValueError, OSError, httpx.HTTPError) as exc:
        return failure(exc)


def status_result() -> dict[str, Any]:
    try:
        return success(status(load_config()))
    except (ValueError, OSError, KeyError) as exc:
        return failure(exc)
