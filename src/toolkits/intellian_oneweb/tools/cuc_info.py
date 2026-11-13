"""Intellian cuc_info endpoint."""

from core import HttpTool

cuc_info = HttpTool(
    name="cuc_info",
    description="Read Intellian cuc_info",
    method="GET",
    path="/api/cuc/info",
    fields=(
        "availability_status",
        "vr_status",
    ),
)
