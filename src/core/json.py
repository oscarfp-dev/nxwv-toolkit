"""Extract selected JSON paths without renaming or flattening their structure."""

from typing import Any, cast


def extract_fields(payload: object, fields: tuple[str, ...]) -> dict[str, Any]:
    selected: dict[str, Any] = {}
    for path in fields:
        parts = path.split(".")
        current: object = payload
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                break
            current = cast(dict[str, object], current)[part]
        else:
            destination: dict[str, Any] = selected
            for part in parts[:-1]:
                if part not in destination:
                    destination[part] = {}
                destination = cast(dict[str, Any], destination[part])
            destination[parts[-1]] = current
    return selected
