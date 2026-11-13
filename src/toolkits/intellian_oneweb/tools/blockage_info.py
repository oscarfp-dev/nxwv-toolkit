"""Intellian blockage_info endpoint."""

from core import HttpTool

blockage_info = HttpTool(
    name="blockage_info",
    description="Read Intellian blockage_info",
    method="GET",
    path="/api/antenna/blockageinfo",
    fields=("regions",),
)
