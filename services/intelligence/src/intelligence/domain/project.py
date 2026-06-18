from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from intelligence.domain.enums import BillingModel
from intelligence.domain.money import Money


@dataclass(frozen=True)
class Receivable:
    invoice_date: date
    outstanding: Money

    def __post_init__(self) -> None:
        if self.outstanding.is_negative:
            raise ValueError("receivable outstanding cannot be negative")


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    sector: str
    billing_model: BillingModel
    contract_fee: Money
    budgeted_cost: Money
    cost_to_date: Money
    estimated_cost_to_complete: Money
    billed_to_date: Money
    retainage_pct: Decimal
    approved_fee_change_orders: Money = field(default_factory=Money.zero)
    pending_fee_change_orders: Money = field(default_factory=Money.zero)
    billable_work_to_date: Money = field(default_factory=Money.zero)
    receivables: tuple[Receivable, ...] = ()
