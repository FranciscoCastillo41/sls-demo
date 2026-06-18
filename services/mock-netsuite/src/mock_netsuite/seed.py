from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from mock_netsuite.db import Base
from mock_netsuite.models import (
    ChangeOrderRow,
    CustomerPaymentRow,
    InvoiceRow,
    JobRow,
    VendorBillRow,
)
from mock_netsuite.records import BillingModel, ChangeOrderKind, ChangeOrderStatus

CENTS = Decimal("0.01")


def split_evenly(total: Decimal, parts: int) -> list[Decimal]:
    cents = int((total / CENTS).to_integral_value())
    base, remainder = divmod(cents, parts)
    return [(base + (1 if i < remainder else 0)) * CENTS for i in range(parts)]


@dataclass(frozen=True)
class ChangeOrderSpec:
    on: date
    amount: Decimal
    status: ChangeOrderStatus
    kind: ChangeOrderKind
    memo: str


@dataclass(frozen=True)
class ProjectSpec:
    internal_id: str
    entity_id: str
    company_name: str
    sector: str
    billing_model: BillingModel
    contract_fee: Decimal
    budgeted_cost: Decimal
    estimated_cost_to_complete: Decimal
    retainage_pct: Decimal
    owner: str
    vendor: str
    start_date: date
    cost_to_date: Decimal
    cost_dates: tuple[date, ...]
    billed_to_date: Decimal
    invoice_dates: tuple[date, ...]
    collected_to_date: Decimal
    payment_dates: tuple[date, ...]
    change_orders: tuple[ChangeOrderSpec, ...] = ()


# DFW: cost burning hot vs progress (EAC > budget) -> margin-at-completion erosion.
# Omaha: margin erosion plus a PENDING fee change order -> unrecovered revenue.
# UT: invoices dated months back, collections lagging -> aged A/R / cash gap.
# PHX: on-budget, current collections -> the healthy control.
PROJECTS: tuple[ProjectSpec, ...] = (
    ProjectSpec(
        internal_id="1001",
        entity_id="PRJ-DFW-001",
        company_name="Sterling Medical Center",
        sector="Healthcare",
        billing_model=BillingModel.FIXED_FEE,
        contract_fee=Decimal("1200000.00"),
        budgeted_cost=Decimal("900000.00"),
        estimated_cost_to_complete=Decimal("290000.00"),
        retainage_pct=Decimal("0.10"),
        owner="Sterling Health Partners LP",
        vendor="Lone Star General Contractors",
        start_date=date(2025, 11, 3),
        cost_to_date=Decimal("760000.00"),
        cost_dates=(date(2026, 2, 28), date(2026, 3, 31), date(2026, 4, 30), date(2026, 5, 31)),
        billed_to_date=Decimal("800000.00"),
        invoice_dates=(date(2026, 4, 30), date(2026, 5, 31), date(2026, 6, 15)),
        collected_to_date=Decimal("760000.00"),
        payment_dates=(date(2026, 5, 20), date(2026, 6, 12)),
    ),
    ProjectSpec(
        internal_id="1002",
        entity_id="PRJ-OMA-002",
        company_name="Heartland Surgical Institute",
        sector="Healthcare",
        billing_model=BillingModel.FIXED_FEE,
        contract_fee=Decimal("850000.00"),
        budgeted_cost=Decimal("640000.00"),
        estimated_cost_to_complete=Decimal("170000.00"),
        retainage_pct=Decimal("0.10"),
        owner="Heartland Health System",
        vendor="Prairie Build Group",
        start_date=date(2025, 12, 1),
        cost_to_date=Decimal("540000.00"),
        cost_dates=(date(2026, 3, 31), date(2026, 4, 30), date(2026, 5, 31)),
        billed_to_date=Decimal("560000.00"),
        invoice_dates=(date(2026, 4, 30), date(2026, 5, 31), date(2026, 6, 15)),
        collected_to_date=Decimal("540000.00"),
        payment_dates=(date(2026, 5, 22), date(2026, 6, 10)),
        change_orders=(
            ChangeOrderSpec(
                on=date(2026, 5, 15),
                amount=Decimal("90000.00"),
                status=ChangeOrderStatus.PENDING,
                kind=ChangeOrderKind.FEE,
                memo="Added OR-3 scope; fee increase awaiting owner approval",
            ),
        ),
    ),
    ProjectSpec(
        internal_id="1003",
        entity_id="PRJ-UT-003",
        company_name="Longhorn Engineering Hall",
        sector="Higher Education",
        billing_model=BillingModel.FIXED_FEE,
        contract_fee=Decimal("600000.00"),
        budgeted_cost=Decimal("450000.00"),
        estimated_cost_to_complete=Decimal("150000.00"),
        retainage_pct=Decimal("0.05"),
        owner="University of Texas System",
        vendor="Capitol Construction Co",
        start_date=date(2025, 9, 15),
        cost_to_date=Decimal("300000.00"),
        cost_dates=(date(2025, 12, 31), date(2026, 2, 28), date(2026, 4, 30)),
        billed_to_date=Decimal("420000.00"),
        invoice_dates=(date(2026, 1, 15), date(2026, 2, 15), date(2026, 3, 15)),
        collected_to_date=Decimal("250000.00"),
        payment_dates=(date(2026, 3, 1),),
    ),
    ProjectSpec(
        internal_id="1004",
        entity_id="PRJ-PHX-004",
        company_name="Sky Harbor Concourse F",
        sector="Aviation",
        billing_model=BillingModel.FIXED_FEE,
        contract_fee=Decimal("1500000.00"),
        budgeted_cost=Decimal("1125000.00"),
        estimated_cost_to_complete=Decimal("525000.00"),
        retainage_pct=Decimal("0.10"),
        owner="Phoenix Aviation Authority",
        vendor="Desert Sky Builders",
        start_date=date(2026, 1, 12),
        cost_to_date=Decimal("600000.00"),
        cost_dates=(date(2026, 3, 31), date(2026, 4, 30), date(2026, 5, 31)),
        billed_to_date=Decimal("660000.00"),
        invoice_dates=(date(2026, 5, 31), date(2026, 6, 15)),
        collected_to_date=Decimal("640000.00"),
        payment_dates=(date(2026, 6, 13),),
    ),
)


def _job(spec: ProjectSpec) -> JobRow:
    return JobRow(
        internalId=spec.internal_id,
        entityId=spec.entity_id,
        companyName=spec.company_name,
        custentity_sls_sector=spec.sector,
        custentity_sls_billing_model=spec.billing_model.value,
        custentity_sls_contract_fee=spec.contract_fee,
        custentity_sls_budgeted_cost=spec.budgeted_cost,
        custentity_sls_estimated_cost_to_complete=spec.estimated_cost_to_complete,
        custentity_sls_retainage_pct=spec.retainage_pct,
        startDate=spec.start_date,
    )


def _vendor_bills(spec: ProjectSpec) -> list[VendorBillRow]:
    amounts = split_evenly(spec.cost_to_date, len(spec.cost_dates))
    return [
        VendorBillRow(
            internalId=f"VB-{spec.internal_id}-{i + 1}",
            tranId=f"BILL{spec.internal_id}{i + 1:02d}",
            tranDate=on,
            entity=spec.vendor,
            job=spec.internal_id,
            amount=amount,
            memo=f"Construction draw {i + 1}",
        )
        for i, (on, amount) in enumerate(zip(spec.cost_dates, amounts, strict=True))
    ]


def _invoices(spec: ProjectSpec) -> list[InvoiceRow]:
    amounts = split_evenly(spec.billed_to_date, len(spec.invoice_dates))
    return [
        InvoiceRow(
            internalId=f"INV-{spec.internal_id}-{i + 1}",
            tranId=f"INV{spec.internal_id}{i + 1:02d}",
            tranDate=on,
            entity=spec.owner,
            job=spec.internal_id,
            amount=amount,
            memo=f"Owner's-rep fee, progress billing {i + 1}",
        )
        for i, (on, amount) in enumerate(zip(spec.invoice_dates, amounts, strict=True))
    ]


def _payments(spec: ProjectSpec, invoices: list[InvoiceRow]) -> list[CustomerPaymentRow]:
    amounts = split_evenly(spec.collected_to_date, len(spec.payment_dates))
    return [
        CustomerPaymentRow(
            internalId=f"PMT-{spec.internal_id}-{i + 1}",
            tranId=f"PMT{spec.internal_id}{i + 1:02d}",
            tranDate=on,
            entity=spec.owner,
            job=spec.internal_id,
            amount=amount,
            appliedToInvoice=invoices[i % len(invoices)].internalId,
        )
        for i, (on, amount) in enumerate(zip(spec.payment_dates, amounts, strict=True))
    ]


def _change_orders(spec: ProjectSpec) -> list[ChangeOrderRow]:
    return [
        ChangeOrderRow(
            internalId=f"CO-{spec.internal_id}-{i + 1}",
            tranDate=co.on,
            job=spec.internal_id,
            amount=co.amount,
            custbody_sls_co_status=co.status.value,
            custbody_sls_co_kind=co.kind.value,
            memo=co.memo,
        )
        for i, co in enumerate(spec.change_orders)
    ]


def build_rows() -> list[Base]:
    rows: list[Base] = []
    for spec in PROJECTS:
        invoices = _invoices(spec)
        rows.append(_job(spec))
        rows.extend(_vendor_bills(spec))
        rows.extend(invoices)
        rows.extend(_payments(spec, invoices))
        rows.extend(_change_orders(spec))
    return rows
