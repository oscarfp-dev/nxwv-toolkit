"""Read-only OpsCenter endpoint tools, one file per operation."""

from .get_antenna_data import get_antenna_data
from .get_antenna_info import get_antenna_info

TOOLS = (get_antenna_data, get_antenna_info)
