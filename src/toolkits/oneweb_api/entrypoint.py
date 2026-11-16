"""OneWeb API CLI: IMEI-based and parameterized operations."""

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, cast

from core.cli import emit, section, tools

from .tools import TOOLS

REGISTRY = {tool.__name__: tool for tool in TOOLS}
IMEI_TOOLS = {
    "get_user_terminal",
    "upgrade_status",
    "available_installer_bundles",
    "reboot_status",
    "mute_status",
}


async def run(config: dict[str, object]) -> bool:
    names = tools(config, set(REGISTRY))
    target_config = section(config, "targets")
    imeis: object = target_config.get("imeis", [])
    items = cast(list[object], imeis) if isinstance(imeis, list) else []
    if not isinstance(imeis, list) or not all(isinstance(v, str) and v for v in items):
        raise ValueError("targets.imeis must be a list of strings")
    target_imeis = cast(list[str], imeis)
    params = section(config, "parameters")
    failed = False
    for name in names:
        kwargs: object = params.get(name, {})
        if not isinstance(kwargs, dict):
            raise ValueError(f"parameters.{name} must be a TOML table")
        arguments_config = cast(dict[str, Any], kwargs)
        signature = inspect.signature(REGISTRY[name])
        if any(key not in signature.parameters for key in arguments_config):
            raise ValueError(f"Unknown parameter for {name}")
        if name in IMEI_TOOLS or (name == "list_user_terminals" and target_imeis):
            if not target_imeis:
                raise ValueError(f"targets.imeis is required for {name}")
            if "imei" in arguments_config:
                raise ValueError(f"parameters.{name}.imei conflicts with targets.imeis")
            targets = target_imeis
        else:
            targets = [""]
        for imei in targets:
            arguments = {**arguments_config, **({"imei": imei} if imei else {})}
            try:
                tool = cast(Callable[..., Awaitable[dict[str, Any]]], REGISTRY[name])
                result = await tool(**arguments)
            except (TypeError, ValueError) as exc:
                result = {"ok": False, "error": str(exc)}
            if not emit(imei or "oneweb_api", name, result):
                failed = True
    return not failed
