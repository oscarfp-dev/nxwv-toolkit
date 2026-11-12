"""Intellian lte_signal_info endpoint."""

from core import HttpTool

lte_signal_info = HttpTool(
    name="lte_signal_info",
    description="Read Intellian lte_signal_info",
    method="GET",
    path="/api/modem/lte_signal_info",
    fields=("sinr_dB",),
)
