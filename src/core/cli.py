"""Small CLI helpers shared by independent toolkit entrypoints."""

import json
from typing import Any, cast


def section(config: dict[str, object], name: str) -> dict[str, Any]:
    value = config.get(name, {})
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a TOML table")
    return cast(dict[str, Any], value)


def tools(config: dict[str, object], allowed: set[str]) -> list[str]:
    names = section(config, "pipeline").get("tools")
    items = cast(list[object], names) if isinstance(names, list) else []
    if (
        not isinstance(names, list)
        or not names
        or not all(isinstance(name, str) and name in allowed for name in items)
    ):
        raise ValueError(f"pipeline.tools must contain known tools: {', '.join(sorted(allowed))}")
    return cast(list[str], names)


def strings(config: dict[str, object], section_name: str, key: str) -> list[str]:
    values = section(config, section_name).get(key)
    items = cast(list[object], values) if isinstance(values, list) else []
    if (
        not isinstance(values, list)
        or not values
        or not all(isinstance(value, str) and value for value in items)
    ):
        raise ValueError(f"{section_name}.{key} must be a non-empty list of strings")
    return cast(list[str], values)


def emit(target: str, tool: str, result: dict[str, Any]) -> bool:
    print(json.dumps({"target": target, "tool": tool, **result}, ensure_ascii=False))
    return result.get("ok") is True
