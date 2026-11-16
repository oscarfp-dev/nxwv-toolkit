import asyncio
from pathlib import Path

import httpx
import pytest

from main import load_inventory, run_inventory


def test_example_inventory() -> None:
    urls, tools, auth, verify_tls = load_inventory(Path("inventory.example.toml"))
    assert urls == ["https://example.com"]
    assert tools == ["intellian_oneweb.health"]
    assert auth is None
    assert verify_tls is True


def test_unknown_tool(tmp_path: Path) -> None:
    path = tmp_path / "inventory.toml"
    path.write_text('[targets]\nurls = ["https://example.com"]\n[pipeline]\ntools = ["missing"]\n')
    with pytest.raises(ValueError, match="known tools"):
        load_inventory(path)


def test_basic_auth_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TEST_PASSWORD", "secret")
    path = tmp_path / "inventory.toml"
    path.write_text(
        '[targets]\nurls = ["https://example.com"]\n'
        '[pipeline]\ntools = ["intellian_oneweb.health"]\n'
        '[auth]\ntype = "basic"\nusername = "admin"\npassword_env = "TEST_PASSWORD"\n'
    )
    _, _, auth, _verify_tls = load_inventory(path)
    assert auth is not None
    assert auth.password == "secret"  # type: ignore[union-attr]


def test_declarative_pipeline_uses_local_intellian_registry(tmp_path: Path) -> None:
    path = tmp_path / "inventory.toml"
    path.write_text(
        '[targets]\nurls = ["https://antenna.example"]\n'
        '[pipeline]\ntools = ["intellian_oneweb.health", "intellian_oneweb.antenna_info"]\n'
    )
    urls, tools, auth, verify_tls = load_inventory(path)
    assert urls == ["https://antenna.example"]
    assert tools == ["intellian_oneweb.health", "intellian_oneweb.antenna_info"]
    assert auth is None
    assert verify_tls is True


@pytest.mark.parametrize("value, expected", [("true", True), ("false", False)])
def test_inventory_tls_setting(tmp_path: Path, value: str, expected: bool) -> None:
    path = tmp_path / "inventory.toml"
    path.write_text(
        '[targets]\nurls = ["https://antenna.example"]\n'
        '[pipeline]\ntools = ["intellian_oneweb.health"]\n'
        f"[transport]\nverify_tls = {value}\n"
    )
    assert load_inventory(path)[3] is expected


def test_inventory_tls_rejects_invalid_type(tmp_path: Path) -> None:
    path = tmp_path / "inventory.toml"
    path.write_text(
        '[targets]\nurls = ["https://antenna.example"]\n'
        '[pipeline]\ntools = ["intellian_oneweb.health"]\n'
        '[transport]\nverify_tls = "false"\n'
    )
    with pytest.raises(ValueError, match=r"transport\.verify_tls must be a boolean"):
        load_inventory(path)


@pytest.mark.parametrize("verify_tls", [True, False])
def test_pipeline_passes_tls_verification(
    monkeypatch: pytest.MonkeyPatch, verify_tls: bool
) -> None:
    import main

    seen: list[bool] = []

    class FakeClient:
        def __init__(self, url: str, *, auth: object, verify: bool) -> None:
            seen.append(verify)

    class FakeTool:
        async def run(self, client: object) -> dict[str, bool]:
            return {"ok": True}

    monkeypatch.setattr(main, "HttpClient", FakeClient)
    monkeypatch.setattr(main, "TOOLS", {"test": FakeTool()})
    assert asyncio.run(run_inventory(["https://antenna.example"], ["test"], None, verify_tls))
    assert seen == [verify_tls]


def test_pipeline_reports_empty_transport_error(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import main

    class FakeTool:
        async def run(self, client: object) -> None:
            request = httpx.Request("GET", "https://antenna.example")
            raise httpx.ConnectError("", request=request)

    monkeypatch.setattr(main, "TOOLS", {"test": FakeTool()})
    assert not asyncio.run(run_inventory(["https://antenna.example"], ["test"], None))
    assert "ConnectError" in capsys.readouterr().out
