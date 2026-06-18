from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from intelligence.domain.money import Money, sum_money


@dataclass(frozen=True)
class AgingBuckets:
    current: Money
    days_31_60: Money
    days_61_90: Money
    days_over_90: Money

    @property
    def total(self) -> Money:
        return sum_money((self.current, self.days_31_60, self.days_61_90, self.days_over_90))


@dataclass(frozen=True)
class ProjectMetrics:
    project_id: str
    name: str
    sector: str
    percent_complete: Decimal
    estimate_at_completion: Money
    revenue_recognized: Money
    cost_to_date: Money
    billed_to_date: Money
    work_in_progress: Money
    underbilled: Money
    overbilled: Money
    original_margin: Decimal
    projected_margin: Decimal
    margin_erosion: Decimal
    retainage_held: Money
    accounts_receivable: Money
    aging: AgingBuckets
    unrecovered_change_orders: Money


@dataclass(frozen=True)
class PortfolioMetrics:
    revenue_recognized: Money
    cost_to_date: Money
    billed_to_date: Money
    work_in_progress: Money
    accounts_receivable: Money
    projects: tuple[ProjectMetrics, ...]
