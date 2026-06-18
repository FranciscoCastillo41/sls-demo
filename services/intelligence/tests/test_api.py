from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal

from fastapi.testclient import TestClient

from intelligence.domain.enums import BillingModel
from intelligence.domain.money import Money
from intelligence.domain.project import Project
from intelligence.interface.app import create_app


class _FakeSource:
    def __init__(self, projects: Sequence[Project]) -> None:
        self._projects = projects

    async def load_projects(self) -> Sequence[Project]:
        return self._projects


def _project(internal_id: str, fee: str, cost: str, etc: str, billed: str) -> Project:
    return Project(
        id=internal_id,
        name=f"Project {internal_id}",
        sector="Aviation",
        billing_model=BillingModel.FIXED_FEE,
        contract_fee=Money.of(fee),
        budgeted_cost=Money.of("0"),
        cost_to_date=Money.of(cost),
        estimated_cost_to_complete=Money.of(etc),
        billed_to_date=Money.of(billed),
        retainage_pct=Decimal("0.10"),
    )


def _client() -> TestClient:
    projects = [
        _project("1", fee="1200000", cost="600000", etc="600000", billed="500000"),
        _project("2", fee="800000", cost="200000", etc="600000", billed="150000"),
    ]
    app = create_app(source_factory=lambda: _FakeSource(projects))
    return TestClient(app)


def test_healthz_reports_ok() -> None:
    assert _client().get("/healthz").json() == {"status": "ok"}


def test_portfolio_lists_every_project_with_usd_currency() -> None:
    body = _client().get("/portfolio").json()
    assert body["currency"] == "USD"
    assert {p["project_id"] for p in body["projects"]} == {"1", "2"}


def test_portfolio_totals_reconcile_to_the_sum_of_projects() -> None:
    body = _client().get("/portfolio").json()
    project_revenue = sum(Decimal(p["revenue_recognized"]) for p in body["projects"])
    assert Decimal(body["revenue_recognized"]) == project_revenue


def test_money_is_serialized_as_a_string() -> None:
    body = _client().get("/portfolio").json()
    assert isinstance(body["revenue_recognized"], str)
