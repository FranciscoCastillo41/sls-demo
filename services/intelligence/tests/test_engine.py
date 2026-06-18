from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from intelligence.domain.engine import compute_project_metrics
from intelligence.domain.enums import BillingModel
from intelligence.domain.money import Money
from intelligence.domain.project import Project, Receivable

AS_OF = date(2026, 6, 17)


def _fixed_fee(**overrides: object) -> Project:
    base: dict[str, object] = {
        "id": "p",
        "name": "n",
        "sector": "s",
        "billing_model": BillingModel.FIXED_FEE,
        "contract_fee": Money.of("1500000"),
        "budgeted_cost": Money.of("1125000"),
        "cost_to_date": Money.of("600000"),
        "estimated_cost_to_complete": Money.of("525000"),
        "billed_to_date": Money.of("660000"),
        "retainage_pct": Decimal("0.10"),
    }
    base.update(overrides)
    return Project(**base)  # type: ignore[arg-type]


def test_healthy_project_recognizes_on_budget_with_no_erosion() -> None:
    phx = _fixed_fee()
    metrics = compute_project_metrics(phx, AS_OF)
    assert metrics.revenue_recognized == Money.of("800000.00")
    assert metrics.original_margin == Decimal("0.25")
    assert metrics.projected_margin == Decimal("0.25")
    assert metrics.margin_erosion == Decimal("0")
    assert metrics.underbilled == metrics.work_in_progress
    assert metrics.overbilled == Money.zero()


def test_cost_overrun_erodes_margin_at_completion() -> None:
    dfw = _fixed_fee(
        contract_fee=Money.of("1200000"),
        budgeted_cost=Money.of("900000"),
        cost_to_date=Money.of("760000"),
        estimated_cost_to_complete=Money.of("290000"),
        billed_to_date=Money.of("800000"),
    )
    metrics = compute_project_metrics(dfw, AS_OF)
    assert metrics.estimate_at_completion == Money.of("1050000")
    assert metrics.original_margin == Decimal("0.25")
    assert metrics.projected_margin == Decimal("0.125")
    assert metrics.margin_erosion == Decimal("0.125")
    assert not metrics.work_in_progress.is_negative


def test_pending_change_order_surfaces_as_unrecovered_revenue() -> None:
    omaha = _fixed_fee(
        contract_fee=Money.of("850000"),
        budgeted_cost=Money.of("640000"),
        cost_to_date=Money.of("540000"),
        estimated_cost_to_complete=Money.of("170000"),
        billed_to_date=Money.of("560000"),
        pending_fee_change_orders=Money.of("90000"),
    )
    metrics = compute_project_metrics(omaha, AS_OF)
    assert metrics.unrecovered_change_orders == Money.of("90000")
    assert metrics.margin_erosion > Decimal("0")


def test_aged_receivables_land_in_the_over_90_bucket_and_tie_to_ar() -> None:
    ut = _fixed_fee(
        contract_fee=Money.of("600000"),
        budgeted_cost=Money.of("450000"),
        cost_to_date=Money.of("300000"),
        estimated_cost_to_complete=Money.of("150000"),
        billed_to_date=Money.of("420000"),
        retainage_pct=Decimal("0.05"),
        receivables=(
            Receivable(date(2026, 1, 15), Money.of("80000")),
            Receivable(date(2026, 3, 15), Money.of("69000")),
        ),
    )
    metrics = compute_project_metrics(ut, AS_OF)
    assert metrics.accounts_receivable == Money.of("149000")
    assert metrics.aging.days_over_90 == Money.of("149000")
    assert metrics.aging.total == metrics.accounts_receivable


def test_time_and_materials_recognizes_work_performed() -> None:
    tm = _fixed_fee(
        billing_model=BillingModel.TIME_AND_MATERIALS,
        billable_work_to_date=Money.of("500000"),
        billed_to_date=Money.of("450000"),
    )
    metrics = compute_project_metrics(tm, AS_OF)
    assert metrics.revenue_recognized == Money.of("500000")
    assert metrics.work_in_progress == Money.of("50000")


@pytest.mark.parametrize(
    ("age_in_days", "bucket"),
    [
        (0, "current"),
        (30, "current"),
        (31, "days_31_60"),
        (60, "days_31_60"),
        (61, "days_61_90"),
        (90, "days_61_90"),
        (91, "days_over_90"),
        (200, "days_over_90"),
    ],
)
def test_receivable_lands_in_the_expected_aging_bucket(age_in_days: int, bucket: str) -> None:
    invoice_date = AS_OF - timedelta(days=age_in_days)
    project = _fixed_fee(receivables=(Receivable(invoice_date, Money.of("1000")),))
    aging = compute_project_metrics(project, AS_OF).aging
    buckets = {
        "current": aging.current,
        "days_31_60": aging.days_31_60,
        "days_61_90": aging.days_61_90,
        "days_over_90": aging.days_over_90,
    }
    assert buckets.pop(bucket) == Money.of("1000.00")
    assert all(amount == Money.zero() for amount in buckets.values())
