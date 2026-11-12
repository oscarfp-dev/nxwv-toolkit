"""Verify Intellian endpoint declarations and native field extraction."""

import httpx
import pytest

from core import HttpClient
from core.json import extract_fields
from toolkits import TOOLS

EXPECTED = {
    "antenna_info": "/api/antenna/antennainfo",
    "modem_info": "/api/modem/modeminfo",
    "product": "/aim/api/lui/data/status/product",
    "blockage_info": "/api/antenna/blockageinfo",
    "gnss_stats": "/api/gnss/gnssstats",
    "antenna_status": "/aim/api/lui/data/status/antenna",
    "lte_signal_info": "/api/modem/lte_signal_info",
    "modem_status": "/api/modem/modemstatus",
    "cuc_info": "/api/cuc/info",
}


@pytest.mark.asyncio
@pytest.mark.parametrize(("name", "path"), EXPECTED.items())
async def test_endpoint_path(name: str, path: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == path
        assert request.url.port == 8443
        return httpx.Response(200, json={})

    client = HttpClient("https://antenna.test:8443", transport=httpx.MockTransport(handler))
    assert await TOOLS[f"intellian_oneweb.{name}"].run(client) == {}


def test_nested_mapping_and_missing_fields() -> None:
    tool = TOOLS["intellian_oneweb.gnss_stats"]
    response = httpx.Response(200, json={"nmea_data": {"latitude": 18.2, "longitude": -91.8}})
    assert extract_fields(response.json(), tool.fields) == {
        "nmea_data": {"latitude": 18.2, "longitude": -91.8}
    }
    assert extract_fields({"nmea_data": {}}, tool.fields) == {}


def test_mapping_preserves_original_names() -> None:
    tool = TOOLS["intellian_oneweb.antenna_status"]
    response = httpx.Response(200, json={"target_az0": 120, "blockage_detected0": False})
    assert extract_fields(response.json(), tool.fields) == {
        "target_az0": 120,
        "blockage_detected0": False,
    }
