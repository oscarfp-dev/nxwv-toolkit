"""Offline tests for LTEF tools."""

from pathlib import Path
from typing import Any

import httpx
import pytest

from toolkits.oneweb_ephemeris.config import load_config
from toolkits.oneweb_ephemeris.tools import download_ltef, get_ltef_status


@pytest.fixture
def directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("ONEWEB_EPHEMERIS_DIR", str(tmp_path))
    monkeypatch.setenv("ONEWEB_EPHEMERIS_URL", "https://example.test/ltef/ltef.csv")
    return tmp_path


def test_default_directory_is_project_local(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ONEWEB_EPHEMERIS_DIR", raising=False)
    monkeypatch.setenv("ONEWEB_EPHEMERIS_URL", "https://example.test/ltef/ltef.csv")
    project_root = Path(__file__).resolve().parents[1]
    assert load_config().directory == project_root / ".local" / "ephemeris"


def test_missing(directory: Path) -> None:
    assert get_ltef_status() == {"ok": True, "data": {"exists": False}}


@pytest.mark.asyncio
async def test_download_status_and_last_modified(
    directory: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = httpx.AsyncClient
    requests: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        requests.append(req)
        return httpx.Response(
            200,
            content=b"satellite,time\n123,now\n",
            headers={"Last-Modified": "Thu, 12 Nov 2026 17:14:43 GMT"},
        )

    def fake(**kwargs: Any) -> httpx.AsyncClient:
        kwargs["transport"] = httpx.MockTransport(handler)
        return original(**kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", fake)
    result = await download_ltef()
    assert result["ok"] is True
    assert result["data"]["source_last_modified"] == "2026-11-12T17:14:43+00:00"
    assert (directory / "ltef.csv").read_bytes() == b"satellite,time\n123,now\n"
    assert requests[0].url == "https://example.test/ltef/ltef.csv"
    assert get_ltef_status()["data"]["sha256"] == result["data"]["sha256"]
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_http_failure_preserves_snapshot(
    directory: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = httpx.AsyncClient

    def client_for(status: int) -> Any:
        def factory(**kwargs: Any) -> httpx.AsyncClient:
            kwargs["transport"] = httpx.MockTransport(
                lambda _: httpx.Response(status, content=b"previous")
            )
            return original(**kwargs)

        return factory

    monkeypatch.setattr(httpx, "AsyncClient", client_for(200))
    assert (await download_ltef())["ok"] is True
    monkeypatch.setattr(httpx, "AsyncClient", client_for(503))
    assert (await download_ltef())["status"] == 503
    assert (directory / "ltef.csv").read_bytes() == b"previous"
