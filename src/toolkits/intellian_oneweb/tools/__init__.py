"""Intellian OneWeb declarative tools."""

from core import HttpTool

from .antenna_info import antenna_info
from .antenna_status import antenna_status
from .blockage_info import blockage_info
from .cuc_info import cuc_info
from .gnss_stats import gnss_stats
from .health import health
from .lte_signal_info import lte_signal_info
from .modem_info import modem_info
from .modem_status import modem_status
from .product import product

TOOLS: dict[str, HttpTool] = {
    "intellian_oneweb.health": health,
    "intellian_oneweb.antenna_info": antenna_info,
    "intellian_oneweb.modem_info": modem_info,
    "intellian_oneweb.product": product,
    "intellian_oneweb.blockage_info": blockage_info,
    "intellian_oneweb.gnss_stats": gnss_stats,
    "intellian_oneweb.antenna_status": antenna_status,
    "intellian_oneweb.lte_signal_info": lte_signal_info,
    "intellian_oneweb.modem_status": modem_status,
    "intellian_oneweb.cuc_info": cuc_info,
}
