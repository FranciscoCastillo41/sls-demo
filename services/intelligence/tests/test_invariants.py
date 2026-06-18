from __future__ import annotations

from datetime import date
from decimal import Decimal

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from intelligence.domain.engine import compute_portfolio, compute_project_metrics
from intelligence.domain.enums import BillingModel
from intelligence.domain.money import Money, sum_money
from intelligence.domain.project import Project, Receivable

AS_OF = date(2026, 6, 17)
ZERO = Decimal(0)
ONE = Decimal(1)

# 4 decimal places mirrors NetSuite's NUMERIC(19,4) — the scale the engine must
# survive, not just clean cents.
money_amounts = st.decimals(
    min_value=Decimal(0),
    max_value=Decimal(10_000_000),
    places=4,
    allow_nan=False,
    allow_infinity=False,
)
retainage_amounts = st.decimals(min_value=ZERO, max_value=Decimal("0.20"), places=2)
receivables = st.builds(
    Receivable,
    invoice_date=st.dates(min_value=date(2024, 1, 1), max_value=date(2026, 12, 31)),
    outstanding=money_amounts.map(Money),
)


@st.composite
def projects(draw: st.DrawFn) -> Project:
    return Project(
        id="p",
        name="n",
        sector="s",
        billing_model=draw(st.sampled_from(list(BillingModel))),
        contract_fee=Money(draw(money_amounts)),
        budgeted_cost=Money(draw(money_amounts)),
        cost_to_date=Money(draw(money_amounts)),
        estimated_cost_to_complete=Money(draw(money_amounts)),
        billed_to_date=Money(draw(money_amounts)),
        retainage_pct=draw(retainage_amounts),
        billable_work_to_date=Money(draw(money_amounts)),
        receivables=tuple(draw(st.lists(receivables, max_size=6))),
    )


@settings(max_examples=300)
@given(projects())
def test_recognized_equals_billed_plus_wip(project: Project) -> None:
    metrics = compute_project_metrics(project, AS_OF)
    assert metrics.revenue_recognized == metrics.billed_to_date + metrics.work_in_progress


@given(projects())
def test_underbilled_and_overbilled_partition_wip(project: Project) -> None:
    metrics = compute_project_metrics(project, AS_OF)
    assert metrics.underbilled - metrics.overbilled == metrics.work_in_progress
    assert not (metrics.underbilled.amount > 0 and metrics.overbilled.amount > 0)


@given(projects())
def test_percent_complete_is_bounded(project: Project) -> None:
    metrics = compute_project_metrics(project, AS_OF)
    assert ZERO <= metrics.percent_complete <= ONE


@given(projects())
def test_fee_based_revenue_never_exceeds_the_fee(project: Project) -> None:
    assume(project.billing_model is not BillingModel.TIME_AND_MATERIALS)
    metrics = compute_project_metrics(project, AS_OF)
    fee = project.contract_fee + project.approved_fee_change_orders
    assert metrics.revenue_recognized.amount <= fee.quantized().amount


@given(projects())
def test_aging_buckets_reconcile_to_accounts_receivable(project: Project) -> None:
    metrics = compute_project_metrics(project, AS_OF)
    assert metrics.aging.total == metrics.accounts_receivable
    assert not metrics.accounts_receivable.is_negative


@given(projects())
def test_computation_is_deterministic(project: Project) -> None:
    assert compute_project_metrics(project, AS_OF) == compute_project_metrics(project, AS_OF)


@settings(max_examples=200)
@given(st.lists(projects(), max_size=5))
def test_portfolio_totals_equal_the_sum_of_projects(portfolio_projects: list[Project]) -> None:
    portfolio = compute_portfolio(portfolio_projects, AS_OF)
    assert portfolio.revenue_recognized == sum_money(
        m.revenue_recognized for m in portfolio.projects
    )
    assert portfolio.work_in_progress == sum_money(m.work_in_progress for m in portfolio.projects)
    assert portfolio.accounts_receivable == sum_money(
        m.accounts_receivable for m in portfolio.projects
    )
