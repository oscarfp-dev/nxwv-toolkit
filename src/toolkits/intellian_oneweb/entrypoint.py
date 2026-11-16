"""Intellian-specific inventory runner, preserving the original TOML format."""

import os
from typing import Any

import httpx

from core import BasicAuth, BearerAuth, HttpClient
from core.cli import emit, section, strings, tools

from .tools import TOOLS


def _secret(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing or empty environment variable: {name}")
    return value


async def run(config: dict[str, object]) -> bool:
    urls = strings(config, "targets", "urls")
    if not all(url.startswith(("http://", "https://")) for url in urls):
        raise ValueError("targets.urls must contain HTTP(S) URLs")
    names = tools(config, set(TOOLS))
    auth_config = section(config, "auth")
    auth_type = auth_config.get("type", "none")
    auth: BasicAuth | BearerAuth | None = None
    if auth_type == "basic":
        auth = BasicAuth(auth_config["username"], _secret(auth_config["password_env"]))
    elif auth_type == "bearer":
        auth = BearerAuth(_secret(auth_config["token_env"]))
    elif auth_type != "none":
        raise ValueError(f"Unsupported auth type: {auth_type}")
    verify_tls = section(config, "transport").get("verify_tls", True)
    if not isinstance(verify_tls, bool):
        raise ValueError("transport.verify_tls must be a boolean")
    failed = False
    for url in urls:
        client = HttpClient(url, auth=auth, verify=verify_tls)
        for name in names:
            try:
                data = await TOOLS[name].run(client)
                result: dict[str, Any] = {"ok": True, "data": data}
            except httpx.HTTPStatusError as exc:
                result = {
                    "ok": False,
                    "status": exc.response.status_code,
                    "error": str(exc) or repr(exc),
                }
            except httpx.RequestError as exc:
                result = {"ok": False, "status": None, "error": str(exc) or repr(exc)}
            if not emit(url, name, result):
                failed = True
    return not failed
