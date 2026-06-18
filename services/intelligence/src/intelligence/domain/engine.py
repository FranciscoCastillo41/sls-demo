from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date
from decimal import Decimal
from typing import NamedTuple

from intelligence.domain.enums import BillingModel
from intelligence.domain.metrics import AgingBuckets, PortfolioMetrics, ProjectMetrics
from intelligence.domain.money import Money, sum_money
from intelligence.domain.project import Project, Receivable

ZERO = Decimal(0)
ONE = Decimal(1)

CURRENT_MAX_DAYS = 30
DAYS_31_60_MAX = 60
DAYS_61_90_MAX = 90


class _Recognition(NamedTuple):
    recognized: Money
    revenue_basis: Money
    cost_at_completion: Money


def _percent_complete(cost_to_date: Money, estimate_at_completion: Money) -> Decimal:
    return min(ONE, max(ZERO, cost_to_date.ratio_to(estimate_at_completion)))


def _recognize(
    project: Project, percent_complete: Decimal, estimate_at_completion: Money
) -> _Recognition:
    if project.billing_model is BillingModel.TIME_AND_MATERIALS:
        work = project.billable_work_to_date
        return _Recognition(work, work, project.cost_to_date)
    fee = project.contract_fee + project.approved_fee_change_orders
    return _Recognition(fee * percent_complete, fee, estimate_at_completion)


def _margin(revenue: Money, cost: Money) -> Decimal:
    if revenue.is_zero:
        return ZERO
    return (revenue - cost).ratio_to(revenue)


def _age(receivables: Iterable[Receivable], as_of: date) -> AgingBuckets:
    current: list[Money] = []
    days_31_60: list[Money] = []
    days_61_90: list[Money] = []
    days_over_90: list[Money] = []
    for receivable in receivables:
        age_in_days = (as_of - receivable.invoice_date).days
        if age_in_days <= CURRENT_MAX_DAYS:
            current.append(receivable.outstanding)
        elif age_in_days <= DAYS_31_60_MAX:
            days_31_60.append(receivable.outstanding)
        elif age_in_days <= DAYS_61_90_MAX:
            days_61_90.append(receivable.outstanding)
        else:
            days_over_90.append(receivable.outstanding)
    return AgingBuckets(
        current=sum_money(current).quantized(),
        days_31_60=sum_money(days_31_60).quantized(),
        days_61_90=sum_money(days_61_90).quantized(),
        days_over_90=sum_money(days_over_90).quantized(),
    )


def compute_project_metrics(project: Project, as_of: date) -> ProjectMetrics:
    estimate_at_completion = project.cost_to_date + project.estimated_cost_to_complete
    percent_complete = _percent_complete(project.cost_to_date, estimate_at_completion)
    recognition = _recognize(project, percent_complete, estimate_at_completion)

    revenue_recognized = recognition.recognized.quantized()
    billed_to_date = project.billed_to_date.quantized()
    work_in_progress = revenue_recognized - billed_to_date
    underbilled = Money.zero() if work_in_progress.is_negative else work_in_progress
    overbilled = -work_in_progress if work_in_progress.is_negative else Money.zero()

    original_margin = _margin(project.contract_fee, project.budgeted_cost)
    projected_margin = _margin(recognition.revenue_basis, recognition.cost_at_completion)
    aging = _age(project.receivables, as_of)

    return ProjectMetrics(
        project_id=project.id,
        name=project.name,
        sector=project.sector,
        percent_complete=percent_complete,
        estimate_at_completion=estimate_at_completion.quantized(),
        revenue_recognized=revenue_recognized,
        cost_to_date=project.cost_to_date.quantized(),
        billed_to_date=billed_to_date,
        work_in_progress=work_in_progress,
        underbilled=underbilled,
        overbilled=overbilled,
        original_margin=original_margin,
        projected_margin=projected_margin,
        margin_erosion=original_margin - projected_margin,
        retainage_held=(project.billed_to_date * project.retainage_pct).quantized(),
        accounts_receivable=aging.total,
        aging=aging,
        unrecovered_change_orders=project.pending_fee_change_orders.quantized(),
    )


def compute_portfolio(projects: Sequence[Project], as_of: date) -> PortfolioMetrics:
    metrics = tuple(compute_project_metrics(project, as_of) for project in projects)
    return PortfolioMetrics(
        revenue_recognized=sum_money(m.revenue_recognized for m in metrics),
        cost_to_date=sum_money(m.cost_to_date for m in metrics),
        billed_to_date=sum_money(m.billed_to_date for m in metrics),
        work_in_progress=sum_money(m.work_in_progress for m in metrics),
        accounts_receivable=sum_money(m.accounts_receivable for m in metrics),
        projects=metrics,
    )
