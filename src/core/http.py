"""Small HTTP/HTTPS client primitive."""

from dataclasses import dataclass
from typing import Any, Literal

import httpx


@dataclass(frozen=True)
class BasicAuth:
    username: str
    password: str


@dataclass(frozen=True)
class BearerAuth:
    token: str


class HttpClient:
    def __init__(
        self,
        base_url: str,
        auth: BasicAuth | BearerAuth | None = None,
        *,
        timeout: float = 10.0,
        verify: bool = True,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not base_url.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")

        self.base_url = base_url.rstrip("/")
        self.auth = auth
        self.timeout = timeout
        self.verify = verify
        self.transport = transport

    async def request(
        self,
        method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] | str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        if isinstance(self.auth, BasicAuth):
            auth: httpx.Auth | None = httpx.BasicAuth(self.auth.username, self.auth.password)
        else:
            auth = None

        request_headers = dict(headers or {})
        if isinstance(self.auth, BearerAuth):
            request_headers["Authorization"] = f"Bearer {self.auth.token}"

        async with httpx.AsyncClient(
            base_url=self.base_url,
            auth=auth,
            timeout=self.timeout,
            verify=self.verify,
            transport=self.transport,
            follow_redirects=False,
        ) as client:
            response = await client.request(
                method,
                path,
                params=params,
                json=json,
                headers=request_headers,
            )
            if response.is_redirect:
                raise httpx.HTTPStatusError(
                    f"Unexpected HTTP redirect ({response.status_code})",
                    request=response.request,
                    response=response,
                )
            response.raise_for_status()
            return response
