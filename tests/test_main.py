from pathlib import Path

import pytest

from main import load_inventory


def test_example_inventory() -> None:
    urls, tools, auth = load_inventory(Path("inventory.example.toml"))
    assert urls == ["https://example.com"]
    assert tools == ["intellian_oneweb.health"]
    assert auth is None


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
    _, _, auth = load_inventory(path)
    assert auth is not None
    assert auth.password == "secret"  # type: ignore[union-attr]
