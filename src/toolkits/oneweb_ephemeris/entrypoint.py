"""OneWeb ephemeris CLI: no target list required."""

from core.cli import emit, tools

from .tools import TOOLS
from .tools.download_ltef import download_ltef
from .tools.get_ltef_status import get_ltef_status

REGISTRY = {tool.__name__: tool for tool in TOOLS}


async def run(config: dict[str, object]) -> bool:
    names = tools(config, set(REGISTRY))
    failed = False
    for name in names:
        if name == "download_ltef":
            result = await download_ltef()
        else:
            result = get_ltef_status()
        if not emit("oneweb_ephemeris", name, result):
            failed = True
    return not failed
