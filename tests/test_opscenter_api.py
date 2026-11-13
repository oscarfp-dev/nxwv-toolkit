"""OpsCenter API adapter tests, without network or real credentials."""

from pathlib import Path
from typing import Any

import httpx
import pytest

from toolkits.opscenter_api.config import load_config
from toolkits.opscenter_api.tools import get_antenna_data, get_antenna_info


@pytest.fixture
def cookie_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "cookie"
    path.write_text("session=example; other=value", encoding="utf-8")
    path.chmod(0o600)
    monkeypatch.setenv("OPSCENTER_COOKIE_FILE", str(path))
    monkeypatch.setenv("OPSCENTER_BASE_URL", "https://opscenter.example.test")
    return path


def test_default_cookie_file_is_project_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPSCENTER_COOKIE_FILE", raising=False)
    monkeypatch.setenv("OPSCENTER_BASE_URL", "https://opscenter.example.test")
    project_root = Path(__file__).resolve().parents[1]
    assert load_config().cookie_file == project_root / ".local" / "auth" / "opscenter.cookie"


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
        kwargs["transport"] = httpx.MockTransport(handler)
        return original(**kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", fake_client)
    tool = get_antenna_data if endpoint == "data" else get_antenna_info
    assert await tool("test-antenna-001") == {"ok": True, "data": payload}
    assert seen[0].url.path == f"/api/v1/antennas/{endpoint}/test-antenna-001"
    assert seen[0].headers["cookie"] == "session=example; other=value"
    assert seen[0].url.host == "opscenter.example.test"


@pytest.mark.asyncio
async def test_expired_session_is_reported_without_redirect(
    cookie_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = httpx.AsyncClient

    def fake_client(**kwargs: Any) -> httpx.AsyncClient:
        kwargs["transport"] = httpx.MockTransport(
            lambda req: httpx.Response(302, headers={"location": "https://login.example.test/"})
        )
        return original(**kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", fake_client)
    result = await get_antenna_info("test-antenna-001")
    assert result["ok"] is False
    assert result["status"] == 302
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
    assert "permissions 600" in (await get_antenna_data("test-antenna-001"))["error"]
    monkeypatch.setenv("OPSCENTER_COOKIE_FILE", str(cookie_file.parent / "missing"))
    assert "cookie missing" in (await get_antenna_info("test-antenna-001"))["error"]


@pytest.mark.asyncio
async def test_missing_base_url(cookie_file: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPSCENTER_BASE_URL")
    result = await get_antenna_data("test-antenna-001")
    assert result["ok"] is False
    assert "OPSCENTER_BASE_URL must be configured" in result["error"]
