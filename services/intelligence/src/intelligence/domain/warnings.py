from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from intelligence.domain.metrics import PortfolioMetrics, ProjectMetrics
from intelligence.domain.money import CENTS, Money

ZERO = Decimal(0)
MARGIN_EROSION_WARNING = Decimal("0.05")
MARGIN_EROSION_CRITICAL = Decimal("0.10")
PERCENT = Decimal(100)
PERCENT_PRECISION = Decimal("0.1")


class Severity(StrEnum):
    WARNING = "warning"
    CRITICAL = "critical"


class WarningCode(StrEnum):
    PROJECTED_LOSS = "projectedLoss"
    MARGIN_EROSION = "marginErosion"
    AGED_RECEIVABLES = "agedReceivables"
    UNRECOVERED_CHANGE_ORDERS = "unrecoveredChangeOrders"
    OVERBILLED = "overbilled"


@dataclass(frozen=True)
class ProjectWarning:
    project_id: str
    name: str
    code: WarningCode
    severity: Severity
    message: str


def _pct(ratio: Decimal) -> str:
    return f"{(ratio * PERCENT).quantize(PERCENT_PRECISION)}%"


def _dollars(money: Money) -> str:
    return f"${money.amount.quantize(CENTS):,.2f}"


def evaluate_project(metrics: ProjectMetrics) -> list[ProjectWarning]:
    candidates = (
        _margin_warning(metrics),
        _aged_receivables_warning(metrics),
        _unrecovered_change_orders_warning(metrics),
        _overbilled_warning(metrics),
    )
    return [warning for warning in candidates if warning is not None]


def evaluate_portfolio(portfolio: PortfolioMetrics) -> list[ProjectWarning]:
    return [warning for project in portfolio.projects for warning in evaluate_project(project)]


def _warning(
    metrics: ProjectMetrics, code: WarningCode, severity: Severity, message: str
) -> ProjectWarning:
    return ProjectWarning(metrics.project_id, metrics.name, code, severity, message)


def _margin_warning(metrics: ProjectMetrics) -> ProjectWarning | None:
    if metrics.projected_margin < ZERO:
        return _warning(
            metrics,
            WarningCode.PROJECTED_LOSS,
            Severity.CRITICAL,
            f"Projected to finish at a loss ({_pct(metrics.projected_margin)} margin).",
        )
    erosion = metrics.margin_erosion
    if erosion < MARGIN_EROSION_WARNING:
        return None
    severity = Severity.CRITICAL if erosion >= MARGIN_EROSION_CRITICAL else Severity.WARNING
    message = (
        f"Margin eroded to {_pct(metrics.projected_margin)} "
        f"from {_pct(metrics.original_margin)} budgeted."
    )
    return _warning(metrics, WarningCode.MARGIN_EROSION, severity, message)


def _aged_receivables_warning(metrics: ProjectMetrics) -> ProjectWarning | None:
    aged = metrics.aging.days_over_90
    if aged.is_zero:
        return None
    return _warning(
        metrics,
        WarningCode.AGED_RECEIVABLES,
        Severity.WARNING,
        f"{_dollars(aged)} in receivables aged over 90 days.",
    )


def _unrecovered_change_orders_warning(metrics: ProjectMetrics) -> ProjectWarning | None:
    pending = metrics.unrecovered_change_orders
    if pending.is_zero:
        return None
    return _warning(
        metrics,
        WarningCode.UNRECOVERED_CHANGE_ORDERS,
        Severity.WARNING,
        f"{_dollars(pending)} in change orders billed in scope but not yet in the fee.",
    )


def _overbilled_warning(metrics: ProjectMetrics) -> ProjectWarning | None:
    if metrics.overbilled.is_zero:
        return None
    return _warning(
        metrics,
        WarningCode.OVERBILLED,
        Severity.WARNING,
        f"Billed {_dollars(metrics.overbilled)} ahead of revenue earned.",
    )
