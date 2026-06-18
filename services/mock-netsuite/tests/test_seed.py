from __future__ import annotations

from decimal import Decimal

from mock_netsuite.db import Base
from mock_netsuite.models import (
    ChangeOrderRow,
    CustomerPaymentRow,
    InvoiceRow,
    JobRow,
    VendorBillRow,
)
from mock_netsuite.seed import PROJECTS, build_rows, split_evenly


def _sum_amounts(rows: list[Base], row_type: type, job: str) -> Decimal:
    return sum(
        (r.amount for r in rows if isinstance(r, row_type) and r.job == job),
        Decimal(0),
    )


def test_split_evenly_conserves_the_total_to_the_cent() -> None:
    parts = split_evenly(Decimal("100.00"), 3)
    assert sum(parts) == Decimal("100.00")
    assert parts == [Decimal("33.34"), Decimal("33.33"), Decimal("33.33")]


def test_split_evenly_handles_a_single_part() -> None:
    assert split_evenly(Decimal("250000.00"), 1) == [Decimal("250000.00")]


def test_seed_transactions_reconcile_to_each_project_total() -> None:
    rows = build_rows()
    for spec in PROJECTS:
        assert _sum_amounts(rows, VendorBillRow, spec.internal_id) == spec.cost_to_date
        assert _sum_amounts(rows, InvoiceRow, spec.internal_id) == spec.billed_to_date
        assert _sum_amounts(rows, CustomerPaymentRow, spec.internal_id) == spec.collected_to_date


def test_seed_has_the_four_projects_and_the_one_pending_change_order() -> None:
    rows = build_rows()
    assert len([r for r in rows if isinstance(r, JobRow)]) == 4
    assert len([r for r in rows if isinstance(r, ChangeOrderRow)]) == 1
