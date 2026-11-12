"""Intellian modem_status endpoint."""

from core import HttpTool

modem_status = HttpTool(
    name="modem_status",
    description="Read Intellian modem_status",
    method="GET",
    path="/api/modem/modemstatus",
    fields=("operating_mode",),
)
