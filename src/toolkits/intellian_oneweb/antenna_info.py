"""Intellian antenna_info endpoint."""

from core import HttpTool

antenna_info = HttpTool(
    name="antenna_info",
    description="Read Intellian antenna_info",
    method="GET",
    path="/api/antenna/antennainfo",
    fields=(
        "firmware_version_current",
        "model",
        "vendor",
    ),
)
