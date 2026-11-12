"""Declarative HTTP tool that returns its extracted data."""

from dataclasses import dataclass
from typing import Any

from .http import HttpClient
from .json import extract_fields


@dataclass(frozen=True)
class HttpTool:
    name: str
    description: str
    method: str
    path: str
    fields: tuple[str, ...] = ()

    async def run(self, client: HttpClient) -> Any:
        response = await client.request(self.method, self.path)
        if self.fields:
            return extract_fields(response.json(), self.fields)
        try:
            return response.json()
        except ValueError:
            return response.text
