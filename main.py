"""Route a single TOML inventory to its toolkit-specific CLI entrypoint."""

import argparse
import asyncio
import sys
import tomllib
from pathlib import Path
from typing import cast

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))


def load_inventory(path: Path) -> dict[str, object]:
    with path.open("rb") as file:
        config: dict[str, object] = tomllib.load(file)
    toolkit = config.get("toolkit", {})
    if not isinstance(toolkit, dict):
        raise ValueError("toolkit must be a TOML table")
    name: object = cast(dict[str, object], toolkit).get("name", "intellian_oneweb")
    if not isinstance(name, str) or name not in ENTRYPOINTS:
        raise ValueError(f"Unknown toolkit: {name}")
    return config


ENTRYPOINTS = {
    "intellian_oneweb": "toolkits.intellian_oneweb.entrypoint",
    "oneweb_api": "toolkits.oneweb_api.entrypoint",
    "opscenter_api": "toolkits.opscenter_api.entrypoint",
    "oneweb_ephemeris": "toolkits.oneweb_ephemeris.entrypoint",
}


async def run_inventory(config: dict[str, object]) -> bool:
    from importlib import import_module

    toolkit = config.get("toolkit", {})
    name: object = (
        cast(dict[str, object], toolkit).get("name", "intellian_oneweb")
        if isinstance(toolkit, dict)
        else ""
    )
    if not isinstance(name, str) or name not in ENTRYPOINTS:
        raise ValueError(f"Unknown toolkit: {name}")
    entrypoint = import_module(ENTRYPOINTS[name])
    return bool(await entrypoint.run(config))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a declarative HTTP tool pipeline")
    parser.add_argument("inventory", type=Path, help="Path to the TOML inventory")
    args = parser.parse_args()
    load_dotenv(Path(__file__).resolve().parent / ".env")
    try:
        config = load_inventory(args.inventory)
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"Invalid inventory: {exc}", file=sys.stderr)
        return 2
    try:
        return 0 if asyncio.run(run_inventory(config)) else 1
    except (KeyError, TypeError, ValueError) as exc:
        print(f"Invalid inventory: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
