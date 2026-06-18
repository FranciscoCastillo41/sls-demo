from __future__ import annotations

from decimal import Decimal

import httpx
from fastapi.testclient import TestClient

from intelligence.infrastructure.netsuite.adapter import NetSuiteProjectSource
from intelligence.infrastructure.netsuite.client import NetSuiteClient
from intelligence.interface.app import create_app

# Two seeded stories driven entirely through the HTTP boundary: DFW (cost overrun,
# margin erosion) and UT (aged A/R). Exercises client -> adapter -> mapping ->
# domain -> response in one pass.
_RECORDS: dict[str, list[dict[str, object]]] = {
    "/record/v1/job": [
        {
            "internalId": "1001",
            "companyName": "Sterling Medical Center",
            "custentity_sls_sector": "Healthcare",
            "custentity_sls_billing_model": "fixedFee",
            "custentity_sls_contract_fee": "1200000.00",
            "custentity_sls_budgeted_cost": "900000.00",
            "custentity_sls_estimated_cost_to_complete": "290000.00",
            "custentity_sls_retainage_pct": "0.10",
        },
        {
            "internalId": "1003",
            "companyName": "Longhorn Engineering Hall",
            "custentity_sls_sector": "Higher Education",
            "custentity_sls_billing_model": "fixedFee",
            "custentity_sls_contract_fee": "600000.00",
            "custentity_sls_budgeted_cost": "450000.00",
            "custentity_sls_estimated_cost_to_complete": "150000.00",
            "custentity_sls_retainage_pct": "0.05",
        },
    ],
    "/record/v1/vendorbill": [
        {"job": "1001", "amount": "760000.00"},
        {"job": "1003", "amount": "300000.00"},
    ],
    "/record/v1/invoice": [
        {
            "internalId": "INV-1001-1",
            "job": "1001",
            "tranDate": "2026-06-15",
            "amount": "800000.00",
        },
        {
            "internalId": "INV-1003-1",
            "job": "1003",
            "tranDate": "2026-01-15",
            "amount": "140000.00",
        },
        {
            "internalId": "INV-1003-2",
            "job": "1003",
            "tranDate": "2026-02-15",
            "amount": "140000.00",
        },
        {
            "internalId": "INV-1003-3",
            "job": "1003",
            "tranDate": "2026-03-15",
            "amount": "140000.00",
        },
    ],
    "/record/v1/customerpayment": [
        {"job": "1001", "amount": "760000.00"},
        {"job": "1003", "amount": "250000.00"},
    ],
    "/record/v1/changeorder": [],
}


def _ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"items": _RECORDS[request.url.path]})


def _client(handler: httpx.MockTransport) -> TestClient:
    source = NetSuiteProjectSource(NetSuiteClient("http://netsuite", transport=handler))
    return TestClient(create_app(source_factory=lambda: source))


def test_portfolio_reconstructs_the_seeded_stories_end_to_end() -> None:
    body = _client(httpx.MockTransport(_ok)).get("/portfolio").json()

    project_revenue = sum(Decimal(p["revenue_recognized"]) for p in body["projects"])
    assert Decimal(body["revenue_recognized"]) == project_revenue

    by_id = {p["project_id"]: p for p in body["projects"]}
    assert Decimal(by_id["1001"]["margin_erosion"]) > 0
    assert Decimal(by_id["1003"]["aging"]["days_over_90"]) == Decimal("149000.00")

    codes = {(w["project_id"], w["code"]) for w in body["warnings"]}
    assert ("1001", "marginErosion") in codes
    assert ("1003", "agedReceivables") in codes


def test_portfolio_returns_502_when_netsuite_fails() -> None:
    def _fail(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "boom"})

    response = _client(httpx.MockTransport(_fail)).get("/portfolio")
    assert response.status_code == 502
    assert "unavailable" in response.json()["detail"]
