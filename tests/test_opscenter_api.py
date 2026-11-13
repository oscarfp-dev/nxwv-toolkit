"""OpsCenter API adapter tests, without network or real credentials."""

from pathlib import Path
from typing import Any

import httpx
import pytest

from toolkits.opscenter_api.tools import get_antenna_data, get_antenna_info


@pytest.fixture
def cookie_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "cookie"
    path.write_text("session=example; other=value", encoding="utf-8")
    path.chmod(0o600)
    monkeypatch.setenv("OPSCENTER_COOKIE_FILE", str(path))
    return path


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint", ["data", "info"])
async def test_native_payload_and_private_cookie(
    cookie_file: Path, monkeypatch: pytest.MonkeyPatch, endpoint: str
) -> None:
    payload: dict[str, Any] = {"unknown_field": [1, {"nested": True}]}
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        return httpx.Response(200, json=payload)

    original = httpx.AsyncClient

    def fake_client(**kwargs: Any) -> httpx.AsyncClient:
        assert kwargs["follow_redirects"] is False
        assert "verify" not in kwargs or kwargs["verify"] is not False
        return original(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", fake_client)
    tool = get_antenna_data if endpoint == "data" else get_antenna_info
    assert await tool("Sh2Fl6") == {"ok": True, "data": payload}
    assert seen[0].url.path == f"/api/v1/antennas/{endpoint}/Sh2Fl6"
    assert seen[0].headers["cookie"] == "session=example; other=value"
    assert seen[0].url.host == "poller.opscenter-preprod.viasat.io"


@pytest.mark.asyncio
async def test_expired_session_is_reported_without_redirect(
    cookie_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = httpx.AsyncClient

    def fake_client(**kwargs: Any) -> httpx.AsyncClient:
        return original(
            transport=httpx.MockTransport(
                lambda req: httpx.Response(302, headers={"location": "https://login.example.test/"})
            ),
            **kwargs,
        )

    monkeypatch.setattr(httpx, "AsyncClient", fake_client)
    result = await get_antenna_info("Sh2Fl6")
    assert result["ok"] is False
    assert "HTTP 302" in result["error"]
    assert "session=example" not in result["error"]


@pytest.mark.asyncio
async def test_invalid_antenna_id(cookie_file: Path) -> None:
    result = await get_antenna_data("../other")
    assert result["ok"] is False


@pytest.mark.asyncio
async def test_missing_or_insecure_cookie(
    cookie_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cookie_file.chmod(0o644)
    assert "permissions 600" in (await get_antenna_data("Sh2Fl6"))["error"]
    monkeypatch.setenv("OPSCENTER_COOKIE_FILE", str(cookie_file.parent / "missing"))
    assert "cookie missing" in (await get_antenna_info("Sh2Fl6"))["error"]
