from __future__ import annotations

from datetime import date
from decimal import Decimal

from intelligence.domain.engine import compute_project_metrics
from intelligence.domain.money import Money
from intelligence.infrastructure.netsuite.mapping import build_projects
from intelligence.infrastructure.netsuite.schemas import (
    NetSuiteSnapshot,
    NsChangeOrder,
    NsCustomerPayment,
    NsInvoice,
    NsJob,
    NsVendorBill,
)

AS_OF = date(2026, 6, 17)


def _job(internal_id: str, retainage: str, **money: str) -> NsJob:
    return NsJob(
        internalId=internal_id,
        companyName=f"Project {internal_id}",
        custentity_sls_sector="Higher Education",
        custentity_sls_billing_model="fixedFee",
        custentity_sls_contract_fee=Decimal(money.get("fee", "600000")),
        custentity_sls_budgeted_cost=Decimal(money.get("budget", "450000")),
        custentity_sls_estimated_cost_to_complete=Decimal(money.get("etc", "150000")),
        custentity_sls_retainage_pct=Decimal(retainage),
    )


def test_mapping_reconstructs_the_aged_ar_story_with_fifo_payments() -> None:
    job = _job("1003", retainage="0.05")
    invoices = [
        NsInvoice(internalId=f"INV-{i}", job="1003", tranDate=on, amount=Decimal("140000"))
        for i, on in enumerate((date(2026, 1, 15), date(2026, 2, 15), date(2026, 3, 15)), start=1)
    ]
    bills = [NsVendorBill(job="1003", amount=Decimal("100000")) for _ in range(3)]
    payments = [NsCustomerPayment(job="1003", amount=Decimal("250000"))]
    snapshot = NetSuiteSnapshot(
        jobs=[job], vendor_bills=bills, invoices=invoices, payments=payments, change_orders=[]
    )

    projects = build_projects(snapshot)
    assert len(projects) == 1
    metrics = compute_project_metrics(projects[0], AS_OF)
    assert metrics.cost_to_date == Money.of("300000")
    assert metrics.billed_to_date == Money.of("420000")
    # collectible = 420000 * 0.95 = 399000; collected 250000 -> AR 149000, all aged > 90 days.
    assert metrics.accounts_receivable == Money.of("149000")
    assert metrics.aging.days_over_90 == Money.of("149000")


def test_mapping_separates_pending_from_approved_fee_change_orders() -> None:
    job = _job("1002", retainage="0.10")
    change_orders = [
        NsChangeOrder(
            job="1002",
            amount=Decimal("90000"),
            custbody_sls_co_status="pending",
            custbody_sls_co_kind="fee",
        ),
        NsChangeOrder(
            job="1002",
            amount=Decimal("20000"),
            custbody_sls_co_status="approved",
            custbody_sls_co_kind="fee",
        ),
        NsChangeOrder(
            job="1002",
            amount=Decimal("5000"),
            custbody_sls_co_status="pending",
            custbody_sls_co_kind="cost",
        ),
    ]
    snapshot = NetSuiteSnapshot(
        jobs=[job], vendor_bills=[], invoices=[], payments=[], change_orders=change_orders
    )

    project = build_projects(snapshot)[0]
    assert project.pending_fee_change_orders == Money.of("90000")
    assert project.approved_fee_change_orders == Money.of("20000")


def test_mapping_with_zero_retainage_makes_full_billing_collectible() -> None:
    job = _job("2001", retainage="0.00")
    invoices = [
        NsInvoice(
            internalId="INV-1", job="2001", tranDate=date(2026, 6, 1), amount=Decimal("100000")
        )
    ]
    payments = [NsCustomerPayment(job="2001", amount=Decimal("40000"))]
    snapshot = NetSuiteSnapshot(
        jobs=[job], vendor_bills=[], invoices=invoices, payments=payments, change_orders=[]
    )

    metrics = compute_project_metrics(build_projects(snapshot)[0], AS_OF)
    # No retainage: collectible == billed, so AR == billed - collected = 60000.
    assert metrics.accounts_receivable == Money.of("60000")
    assert metrics.aging.current == Money.of("60000")
