"""Inspect a local LTEF snapshot without contacting OneWeb."""

from typing import Any

from ..response import status_result


def get_ltef_status() -> dict[str, Any]:
    """Report local LTEF download time, age, size, checksum and source Last-Modified."""
    return status_result()
