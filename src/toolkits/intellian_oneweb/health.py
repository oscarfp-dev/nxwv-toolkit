"""Health tool declaration for an Intellian OneWeb system."""

from core import HttpTool

health = HttpTool(
    name="health",
    description="Get antenna health status",
    method="GET",
    path="/",
)
