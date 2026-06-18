from __future__ import annotations

from decimal import Decimal

from intelligence.domain.money import Money, sum_money
from intelligence.domain.project import Project, Receivable
from intelligence.infrastructure.netsuite.schemas import (
    NetSuiteSnapshot,
    NsChangeOrder,
    NsInvoice,
    NsJob,
)

ONE = Decimal(1)
APPROVED = "approved"
PENDING = "pending"
FEE = "fee"


def build_projects(snapshot: NetSuiteSnapshot) -> list[Project]:
    return [_build_project(job, snapshot) for job in snapshot.jobs]


def _build_project(job: NsJob, snapshot: NetSuiteSnapshot) -> Project:
    job_id = job.internalId
    bills = [b for b in snapshot.vendor_bills if b.job == job_id]
    invoices = sorted((i for i in snapshot.invoices if i.job == job_id), key=lambda i: i.tranDate)
    payments = [p for p in snapshot.payments if p.job == job_id]
    change_orders = [c for c in snapshot.change_orders if c.job == job_id]
    retainage_pct = job.custentity_sls_retainage_pct

    collected = sum_money(Money(p.amount) for p in payments)
    # T&M revenue comes from timebill records, which the source does not emit yet,
    # so billable_work_to_date stays zero (a T&M job recognizes no revenue until then).
    return Project(
        id=job_id,
        name=job.companyName,
        sector=job.custentity_sls_sector,
        billing_model=job.custentity_sls_billing_model,
        contract_fee=Money(job.custentity_sls_contract_fee),
        budgeted_cost=Money(job.custentity_sls_budgeted_cost),
        cost_to_date=sum_money(Money(b.amount) for b in bills),
        estimated_cost_to_complete=Money(job.custentity_sls_estimated_cost_to_complete),
        billed_to_date=sum_money(Money(i.amount) for i in invoices),
        retainage_pct=retainage_pct,
        approved_fee_change_orders=_fee_change_orders(change_orders, APPROVED),
        pending_fee_change_orders=_fee_change_orders(change_orders, PENDING),
        receivables=_receivables(invoices, collected, retainage_pct),
    )


def _fee_change_orders(change_orders: list[NsChangeOrder], status: str) -> Money:
    return sum_money(
        Money(c.amount)
        for c in change_orders
        if c.custbody_sls_co_status == status and c.custbody_sls_co_kind == FEE
    )


def _receivables(
    invoices: list[NsInvoice], collected: Money, retainage_pct: Decimal
) -> tuple[Receivable, ...]:
    remaining = collected
    collectible_rate = ONE - retainage_pct
    receivables: list[Receivable] = []
    # Standard A/R aging: apply collected cash to the oldest invoices first. NetSuite
    # payment→invoice links are nominal for owner's-rep work, so we age by total, not by link.
    for invoice in invoices:
        collectible = Money(invoice.amount) * collectible_rate
        applied = collectible if collectible <= remaining else remaining
        remaining = remaining - applied
        outstanding = (collectible - applied).quantized()
        if not outstanding.is_zero:
            receivables.append(Receivable(invoice.tranDate, outstanding))
    return tuple(receivables)
