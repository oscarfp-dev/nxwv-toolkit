"""Intellian product endpoint."""

from core import HttpTool

product = HttpTool(
    name="product",
    description="Read Intellian product",
    method="GET",
    path="/aim/api/lui/data/status/product",
    fields=(
        "pn0",
        "sn0",
    ),
)
