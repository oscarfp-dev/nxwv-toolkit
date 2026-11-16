"""OpsCenter CLI: antenna-ID-based operations."""

from core.cli import emit, strings, tools

from .tools import TOOLS

REGISTRY = {tool.__name__: tool for tool in TOOLS}


async def run(config: dict[str, object]) -> bool:
    names = tools(config, set(REGISTRY))
    antenna_ids = strings(config, "targets", "antenna_ids")
    failed = False
    for antenna_id in antenna_ids:
        for name in names:
            result = await REGISTRY[name](antenna_id)
            if not emit(antenna_id, name, result):
                failed = True
    return not failed
