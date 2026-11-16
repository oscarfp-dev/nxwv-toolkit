"""CLI router and independent toolkit entrypoint tests."""

import asyncio
from pathlib import Path
from typing import Any

import httpx
import pytest

from main import load_inventory
from toolkits.intellian_oneweb import entrypoint as intellian
from toolkits.oneweb_api import entrypoint as oneweb
from toolkits.oneweb_ephemeris import entrypoint as ephemeris
from toolkits.opscenter_api import entrypoint as opscenter


def test_legacy_inventory_defaults_to_intellian() -> None:
    config = load_inventory(Path("inventory.example.toml"))
    assert config["targets"] == {"urls": ["https://example.com"]}


def test_router_rejects_unknown_toolkit(tmp_path: Path) -> None:
    path = tmp_path / "inventory.toml"
    path.write_text('[toolkit]\nname = "missing"\n')
    with pytest.raises(ValueError, match="Unknown toolkit"):
        load_inventory(path)


@pytest.mark.parametrize("verify_tls", [True, False])
def test_intellian_tls(monkeypatch: pytest.MonkeyPatch, verify_tls: bool) -> None:
    seen: list[bool] = []

    class FakeClient:
        def __init__(self, url: str, *, auth: object, verify: bool) -> None:
            seen.append(verify)

    class FakeTool:
        async def run(self, client: object) -> dict[str, bool]:
            return {"ok": True}

    monkeypatch.setattr(intellian, "HttpClient", FakeClient)
    monkeypatch.setattr(intellian, "TOOLS", {"health": FakeTool()})
    config: dict[str, object] = {
        "targets": {"urls": ["https://antenna.example"]},
        "pipeline": {"tools": ["health"]},
        "transport": {"verify_tls": verify_tls},
    }
    assert asyncio.run(intellian.run(config))
    assert seen == [verify_tls]


def test_intellian_invalid_tls() -> None:
    with pytest.raises(ValueError, match="verify_tls"):
        asyncio.run(
            intellian.run(
                {
                    "targets": {"urls": ["https://antenna.example"]},
                    "pipeline": {"tools": ["intellian_oneweb.health"]},
                    "transport": {"verify_tls": "false"},
                }
            )
        )


def test_intellian_unknown_tool() -> None:
    with pytest.raises(ValueError, match="known tools"):
        asyncio.run(
            intellian.run(
                {
                    "targets": {"urls": ["https://antenna.example"]},
                    "pipeline": {"tools": ["missing"]},
                }
            )
        )


def test_intellian_empty_transport_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class FakeTool:
        async def run(self, client: object) -> None:
            raise httpx.ConnectError("", request=httpx.Request("GET", "https://antenna.example"))

    monkeypatch.setattr(intellian, "TOOLS", {"test": FakeTool()})
    assert not asyncio.run(
        intellian.run(
            {"targets": {"urls": ["https://antenna.example"]}, "pipeline": {"tools": ["test"]}}
        )
    )
    assert "ConnectError" in capsys.readouterr().out


def test_oneweb_imei_routing(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    async def fake(imei: str) -> dict[str, Any]:
        seen.append(imei)
        return {"ok": True, "data": {}}

    monkeypatch.setattr(oneweb, "REGISTRY", {"get_user_terminal": fake})
    assert asyncio.run(
        oneweb.run(
            {
                "targets": {"imeis": ["123456789012345"]},
                "pipeline": {"tools": ["get_user_terminal"]},
            }
        )
    )
    assert seen == ["123456789012345"]


def test_oneweb_custom_parameters(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[int] = []

    async def fake(limit: int = 10) -> dict[str, Any]:
        seen.append(limit)
        return {"ok": True, "data": {}}

    monkeypatch.setattr(oneweb, "REGISTRY", {"list_user_terminals": fake})
    assert asyncio.run(
        oneweb.run(
            {
                "pipeline": {"tools": ["list_user_terminals"]},
                "parameters": {"list_user_terminals": {"limit": 20}},
            }
        )
    )
    assert seen == [20]


def test_opscenter_antenna_id(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    async def fake(antenna_id: str) -> dict[str, Any]:
        seen.append(antenna_id)
        return {"ok": True, "data": {}}

    monkeypatch.setattr(opscenter, "REGISTRY", {"get_antenna_info": fake})
    assert asyncio.run(
        opscenter.run(
            {"targets": {"antenna_ids": ["ant01"]}, "pipeline": {"tools": ["get_antenna_info"]}}
        )
    )
    assert seen == ["ant01"]


def test_ephemeris_no_targets(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_status() -> dict[str, Any]:
        return {"ok": True, "data": {}}

    monkeypatch.setattr(ephemeris, "get_ltef_status", fake_status)
    assert asyncio.run(ephemeris.run({"pipeline": {"tools": ["get_ltef_status"]}}))


def test_router_dispatches_to_selected_toolkit(monkeypatch: pytest.MonkeyPatch) -> None:
    from main import run_inventory

    seen: list[str] = []

    async def fake_run(config: dict[str, object]) -> bool:
        seen.append("opscenter_api")
        return True

    monkeypatch.setattr(opscenter, "run", fake_run)
    assert asyncio.run(run_inventory({"toolkit": {"name": "opscenter_api"}}))
    assert seen == ["opscenter_api"]


def test_oneweb_list_uses_imei_targets_when_provided(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    async def fake_list(imei: str = "") -> dict[str, Any]:
        seen.append(imei)
        return {"ok": True, "data": {}}

    monkeypatch.setattr(oneweb, "REGISTRY", {"list_user_terminals": fake_list})
    assert asyncio.run(
        oneweb.run(
            {
                "targets": {"imeis": ["123456789012345"]},
                "pipeline": {"tools": ["list_user_terminals"]},
            }
        )
    )
    assert seen == ["123456789012345"]
