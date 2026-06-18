from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from intelligence.domain.engine import compute_project_metrics
from intelligence.domain.enums import BillingModel
from intelligence.domain.money import Money
from intelligence.domain.project import Project, Receivable
from intelligence.domain.warnings import Severity, WarningCode, evaluate_project

AS_OF = date(2026, 6, 17)


def _project(
    *,
    fee: str = "1000000",
    budget: str = "750000",
    cost: str = "500000",
    etc: str = "250000",
    billed: str = "0",
    pending_co: str = "0",
    receivables: tuple[Receivable, ...] = (),
) -> Project:
    return Project(
        id="p",
        name="Test Project",
        sector="s",
        billing_model=BillingModel.FIXED_FEE,
        contract_fee=Money.of(fee),
        budgeted_cost=Money.of(budget),
        cost_to_date=Money.of(cost),
        estimated_cost_to_complete=Money.of(etc),
        billed_to_date=Money.of(billed),
        retainage_pct=Decimal("0"),
        pending_fee_change_orders=Money.of(pending_co),
        receivables=receivables,
    )


def _codes(project: Project) -> set[WarningCode]:
    metrics = compute_project_metrics(project, AS_OF)
    return {warning.code for warning in evaluate_project(metrics)}


def test_on_budget_project_raises_no_warnings() -> None:
    # On budget, fully billed-to-earned, no aged A/R, no change orders.
    assert _codes(_project(billed="500000")) == set()


def test_severe_margin_erosion_is_critical() -> None:
    project = _project(cost="850000", etc="0", billed="1000000")  # EAC 850k -> 10pt erosion
    metrics = compute_project_metrics(project, AS_OF)
    warnings = evaluate_project(metrics)
    erosion = next(w for w in warnings if w.code == WarningCode.MARGIN_EROSION)
    assert erosion.severity == Severity.CRITICAL


@pytest.mark.parametrize(
    ("eac_cost", "expected"),
    [("799000", False), ("800000", True)],  # erosion 4.9% (no) vs exactly 5% (yes)
)
def test_margin_erosion_threshold_boundary(eac_cost: str, expected: bool) -> None:
    project = _project(cost=eac_cost, etc="0", billed="1000000")
    assert (WarningCode.MARGIN_EROSION in _codes(project)) is expected


def test_projected_loss_is_flagged_critical() -> None:
    project = _project(cost="1100000", etc="0", billed="1000000")  # EAC 1.1M > 1M fee
    metrics = compute_project_metrics(project, AS_OF)
    loss = next(w for w in evaluate_project(metrics) if w.code == WarningCode.PROJECTED_LOSS)
    assert loss.severity == Severity.CRITICAL


def test_aged_receivables_are_flagged() -> None:
    project = _project(
        billed="500000",
        receivables=(Receivable(date(2026, 1, 1), Money.of("120000")),),
    )
    assert WarningCode.AGED_RECEIVABLES in _codes(project)


def test_pending_change_orders_are_flagged() -> None:
    assert WarningCode.UNRECOVERED_CHANGE_ORDERS in _codes(
        _project(billed="500000", pending_co="90000")
    )


def test_overbilling_is_flagged() -> None:
    # Recognized 500000 (poc .667 * 1M ... ) but billed far ahead.
    assert WarningCode.OVERBILLED in _codes(_project(billed="900000"))
