from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel

from intelligence.domain.metrics import AgingBuckets, PortfolioMetrics, ProjectMetrics
from intelligence.domain.money import DEFAULT_CURRENCY, Money
from intelligence.domain.warnings import (
    ProjectWarning,
    Severity,
    WarningCode,
    evaluate_portfolio,
)


class AgingReport(BaseModel):
    current: Decimal
    days_31_60: Decimal
    days_61_90: Decimal
    days_over_90: Decimal


class ProjectReport(BaseModel):
    project_id: str
    name: str
    sector: str
    percent_complete: Decimal
    estimate_at_completion: Decimal
    revenue_recognized: Decimal
    cost_to_date: Decimal
    billed_to_date: Decimal
    work_in_progress: Decimal
    underbilled: Decimal
    overbilled: Decimal
    original_margin: Decimal
    projected_margin: Decimal
    margin_erosion: Decimal
    retainage_held: Decimal
    accounts_receivable: Decimal
    unrecovered_change_orders: Decimal
    aging: AgingReport


class WarningReport(BaseModel):
    project_id: str
    name: str
    code: WarningCode
    severity: Severity
    message: str


class PortfolioReport(BaseModel):
    currency: str
    revenue_recognized: Decimal
    cost_to_date: Decimal
    billed_to_date: Decimal
    work_in_progress: Decimal
    accounts_receivable: Decimal
    projects: list[ProjectReport]
    warnings: list[WarningReport]


def _amount(money: Money) -> Decimal:
    return money.amount


def _aging(aging: AgingBuckets) -> AgingReport:
    return AgingReport(
        current=_amount(aging.current),
        days_31_60=_amount(aging.days_31_60),
        days_61_90=_amount(aging.days_61_90),
        days_over_90=_amount(aging.days_over_90),
    )


def _project(metrics: ProjectMetrics) -> ProjectReport:
    return ProjectReport(
        project_id=metrics.project_id,
        name=metrics.name,
        sector=metrics.sector,
        percent_complete=metrics.percent_complete,
        estimate_at_completion=_amount(metrics.estimate_at_completion),
        revenue_recognized=_amount(metrics.revenue_recognized),
        cost_to_date=_amount(metrics.cost_to_date),
        billed_to_date=_amount(metrics.billed_to_date),
        work_in_progress=_amount(metrics.work_in_progress),
        underbilled=_amount(metrics.underbilled),
        overbilled=_amount(metrics.overbilled),
        original_margin=metrics.original_margin,
        projected_margin=metrics.projected_margin,
        margin_erosion=metrics.margin_erosion,
        retainage_held=_amount(metrics.retainage_held),
        accounts_receivable=_amount(metrics.accounts_receivable),
        unrecovered_change_orders=_amount(metrics.unrecovered_change_orders),
        aging=_aging(metrics.aging),
    )


def _warning(warning: ProjectWarning) -> WarningReport:
    return WarningReport(
        project_id=warning.project_id,
        name=warning.name,
        code=warning.code,
        severity=warning.severity,
        message=warning.message,
    )


def to_portfolio_report(metrics: PortfolioMetrics) -> PortfolioReport:
    return PortfolioReport(
        currency=DEFAULT_CURRENCY,
        revenue_recognized=_amount(metrics.revenue_recognized),
        cost_to_date=_amount(metrics.cost_to_date),
        billed_to_date=_amount(metrics.billed_to_date),
        work_in_progress=_amount(metrics.work_in_progress),
        accounts_receivable=_amount(metrics.accounts_receivable),
        projects=[_project(project) for project in metrics.projects],
        warnings=[_warning(warning) for warning in evaluate_portfolio(metrics)],
    )
