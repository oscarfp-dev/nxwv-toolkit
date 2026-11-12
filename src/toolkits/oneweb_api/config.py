"""Runtime OneWeb API configuration, independent of the MCP arguments."""

import os
from dataclasses import dataclass

from core import BasicAuth, BearerAuth


@dataclass(frozen=True)
class Config:
    inventory_url: str
    management_url: str
    performance_url: str
    auth: BasicAuth | BearerAuth


def load_config() -> Config:
    auth_type = os.getenv("ONEWEB_AUTH_TYPE", "basic").lower()
    if auth_type == "basic":
        username = os.getenv("ONEWEB_USERNAME")
        password = os.getenv("ONEWEB_PASSWORD")
        if not username or not password:
            raise ValueError("ONEWEB_USERNAME and ONEWEB_PASSWORD must be set")
        auth: BasicAuth | BearerAuth = BasicAuth(username, password)
    elif auth_type == "bearer":
        token = os.getenv("ONEWEB_TOKEN")
        if not token:
            raise ValueError("ONEWEB_TOKEN must be set for bearer authentication")
        auth = BearerAuth(token)
    else:
        raise ValueError("ONEWEB_AUTH_TYPE must be basic or bearer")

    return Config(
        inventory_url=os.getenv("ONEWEB_INVENTORY_URL", ""),
        management_url=os.getenv("ONEWEB_MANAGEMENT_URL", ""),
        performance_url=os.getenv("ONEWEB_PERFORMANCE_URL", ""),
        auth=auth,
    )
