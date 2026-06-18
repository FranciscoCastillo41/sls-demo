from __future__ import annotations

import asyncio
from datetime import date
from decimal import Decimal

import httpx

from intelligence.infrastructure.netsuite.client import NetSuiteClient

_BODIES: dict[str, dict[str, object]] = {
    "/record/v1/job": {
        "items": [
            {
                "internalId": "1",
                "companyName": "Acme",
                "custentity_sls_sector": "Aviation",
                "custentity_sls_billing_model": "fixedFee",
                "custentity_sls_contract_fee": "100.00",
                "custentity_sls_budgeted_cost": "50.00",
                "custentity_sls_estimated_cost_to_complete": "25.00",
                "custentity_sls_retainage_pct": "0.10",
            }
        ]
    },
    "/record/v1/vendorbill": {"items": [{"job": "1", "amount": "10.0000"}]},
    "/record/v1/invoice": {
        "items": [{"internalId": "i1", "job": "1", "tranDate": "2026-05-01", "amount": "40.00"}]
    },
    "/record/v1/customerpayment": {"items": [{"job": "1", "amount": "5.00"}]},
    "/record/v1/changeorder": {"items": []},
}


def _handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=_BODIES[request.url.path])


def test_client_fetches_and_parses_every_record_type() -> None:
    client = NetSuiteClient("http://netsuite", transport=httpx.MockTransport(_handler))
    snapshot = asyncio.run(client.fetch_snapshot())
    assert snapshot.jobs[0].custentity_sls_contract_fee == Decimal("100.00")
    assert snapshot.vendor_bills[0].amount == Decimal("10.0000")
    assert snapshot.invoices[0].amount == Decimal("40.00")
    assert snapshot.invoices[0].tranDate == date(2026, 5, 1)
    assert snapshot.payments[0].amount == Decimal("5.00")
    assert snapshot.change_orders == []
