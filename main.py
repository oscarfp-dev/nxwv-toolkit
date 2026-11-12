"""Run the same declarative tools against every configured target."""

import argparse
import asyncio
import json
import os
import sys
import tomllib
from pathlib import Path
from typing import cast

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import httpx

from core import BasicAuth, BearerAuth, HttpClient
from toolkits import TOOLS


def load_inventory(path: Path) -> tuple[list[str], list[str], BasicAuth | BearerAuth | None]:
    with path.open("rb") as file:
        config = tomllib.load(file)

    targets: object = config["targets"]["urls"]
    tools: object = config["pipeline"]["tools"]
    if not isinstance(targets, list) or not targets:
        raise ValueError("targets.urls must be a non-empty list of HTTP(S) URLs")
    target_items = cast(list[object], targets)
    if not all(
        isinstance(url, str) and url.startswith(("http://", "https://")) for url in target_items
    ):
        raise ValueError("targets.urls must be a non-empty list of HTTP(S) URLs")
    if not isinstance(tools, list) or not tools:
        raise ValueError("pipeline.tools must be a non-empty list")
    tool_items = cast(list[object], tools)
    if not all(isinstance(tool, str) and tool in TOOLS for tool in tool_items):
        raise ValueError(f"pipeline.tools must contain known tools: {', '.join(TOOLS)}")

    auth_config = config.get("auth", {})
    auth_type = auth_config.get("type", "none")
    auth: BasicAuth | BearerAuth | None = None
    if auth_type == "basic":
        auth = BasicAuth(auth_config["username"], _secret(auth_config["password_env"]))
    elif auth_type == "bearer":
        auth = BearerAuth(_secret(auth_config["token_env"]))
    elif auth_type != "none":
        raise ValueError(f"Unsupported auth type: {auth_type}")
    return cast(list[str], targets), cast(list[str], tools), auth


def _secret(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing or empty environment variable: {name}")
    return value


async def run_inventory(
    urls: list[str], tools: list[str], auth: BasicAuth | BearerAuth | None
) -> bool:
    failed = False
    for url in urls:
        client = HttpClient(url, auth=auth)
        for name in tools:
            try:
                data = await TOOLS[name].run(client)
                result = {
                    "target": url,
                    "tool": name,
                    "ok": True,
                    "data": data,
                }
            except httpx.HTTPStatusError as exc:
                failed = True
                result = {
                    "target": url,
                    "tool": name,
                    "ok": False,
                    "status": exc.response.status_code,
                    "error": str(exc),
                }
            except httpx.RequestError as exc:
                failed = True
                result = {
                    "target": url,
                    "tool": name,
                    "ok": False,
                    "status": None,
                    "error": str(exc),
                }
            print(json.dumps(result, ensure_ascii=False))
    return not failed


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a declarative HTTP tool pipeline")
    parser.add_argument("inventory", type=Path, help="Path to the TOML inventory")
    args = parser.parse_args()
    try:
        urls, tools, auth = load_inventory(args.inventory)
    except (OSError, KeyError, TypeError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"Invalid inventory: {exc}", file=sys.stderr)
        return 2
    return 0 if asyncio.run(run_inventory(urls, tools, auth)) else 1


if __name__ == "__main__":
    sys.exit(main())
