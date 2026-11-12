"""Intellian modem_info endpoint."""

from core import HttpTool

modem_info = HttpTool(
    name="modem_info",
    description="Read Intellian modem_info",
    method="GET",
    path="/api/modem/modeminfo",
    fields=("sw_version_current",),
)
