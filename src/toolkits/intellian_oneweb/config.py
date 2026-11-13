"""Per-device authentication configuration for Intellian."""

import os

from core import BasicAuth, BearerAuth


def resolve_auth(auth_type: str, username: str, secret_env: str) -> BasicAuth | BearerAuth | None:
    if auth_type == "none":
        return None
    if auth_type not in ("basic", "bearer"):
        raise ValueError("auth_type must be none, basic, or bearer")
    if not secret_env:
        raise ValueError("secret_env is required for authentication")
    secret = os.environ.get(secret_env)
    if not secret:
        raise ValueError(f"Missing environment variable: {secret_env}")
    if auth_type == "basic":
        if not username:
            raise ValueError("username is required for basic authentication")
        return BasicAuth(username, secret)
    return BearerAuth(secret)
