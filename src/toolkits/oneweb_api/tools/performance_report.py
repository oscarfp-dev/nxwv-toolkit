"""OneWeb API performance_report tool."""

from typing import Any

from ..response import request_result


async def performance_report(payload: dict[str, Any]) -> dict[str, object]:
    """Retrieve a OneWeb performance report using the RAML-defined read-only POST.

    Payload must follow the chosen metric's reportingTimeframe and performanceJob schema.
    This endpoint returns report data (201) and does not change terminal state.
    """
    if not isinstance(payload.get("reportingTimeframe"), dict):
        raise ValueError("payload must contain reportingTimeframe")
    if not isinstance(payload.get("performanceJob"), dict):
        raise ValueError("payload must contain performanceJob")
    return await request_result("performance", "POST", "/performanceReport", body=payload)
