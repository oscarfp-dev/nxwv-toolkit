"""Explicitly refresh the local LTEF snapshot."""

from typing import Any

from ..response import download_result


async def download_ltef() -> dict[str, Any]:
    """Download OneWeb LTEF CSV and save it locally with source modification metadata."""
    return await download_result()
