from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient


def test_healthz_reports_ok(client: TestClient) -> None:
    assert client.get("/healthz").json() == {"status": "ok"}


def test_listing_jobs_returns_every_project(client: TestClient) -> None:
    body = client.get("/record/v1/job").json()
    assert body["count"] == 4
    assert {job["entityId"] for job in body["items"]} == {
        "PRJ-DFW-001",
        "PRJ-OMA-002",
        "PRJ-UT-003",
        "PRJ-PHX-004",
    }


def test_fetching_a_job_returns_its_full_custom_fields(client: TestClient) -> None:
    job = client.get("/record/v1/job/1001").json()
    assert job["recordType"] == "job"
    assert Decimal(job["custentity_sls_contract_fee"]) == Decimal("1200000.00")
    assert job["custentity_sls_billing_model"] == "fixedFee"


def test_money_is_serialized_as_a_string_never_a_float(client: TestClient) -> None:
    bill = client.get("/record/v1/vendorbill/VB-1001-1").json()
    assert isinstance(bill["amount"], str)
    assert Decimal(bill["amount"]) == Decimal("190000.00")


def test_unknown_record_type_is_404(client: TestClient) -> None:
    assert client.get("/record/v1/widget").status_code == 404


def test_unknown_internal_id_is_404(client: TestClient) -> None:
    assert client.get("/record/v1/job/9999").status_code == 404
