"""OneWeb API read-only tools."""

from .available_installer_bundles import available_installer_bundles
from .get_user_terminal import get_user_terminal
from .list_user_terminals import list_user_terminals
from .mute_status import mute_status
from .performance_report import performance_report
from .reboot_status import reboot_status
from .upgrade_status import upgrade_status

TOOLS = (
    list_user_terminals,
    get_user_terminal,
    upgrade_status,
    available_installer_bundles,
    reboot_status,
    mute_status,
    performance_report,
)
