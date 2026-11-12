"""Intellian antenna_status endpoint."""

from core import HttpTool

antenna_status = HttpTool(
    name="antenna_status",
    description="Read Intellian antenna_status",
    method="GET",
    path="/aim/api/lui/data/status/antenna",
    fields=(
        "target_az0",
        "target_el0",
        "ins_yaw0",
        "pcu_temp0",
        "sensor_temp0",
        "blockage_detected0",
        "mode0",
    ),
)
