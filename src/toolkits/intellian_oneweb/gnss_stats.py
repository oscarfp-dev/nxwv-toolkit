"""Intellian gnss_stats endpoint."""

from core import HttpTool

gnss_stats = HttpTool(
    name="gnss_stats",
    description="Read Intellian gnss_stats",
    method="GET",
    path="/api/gnss/gnssstats",
    fields=(
        "nmea_data.latitude",
        "nmea_data.longitude",
    ),
)
