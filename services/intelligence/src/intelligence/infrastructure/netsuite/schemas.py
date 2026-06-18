from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from intelligence.domain.enums import BillingModel


class NsJob(BaseModel):
    internalId: str
    companyName: str
    custentity_sls_sector: str
    custentity_sls_billing_model: BillingModel
    custentity_sls_contract_fee: Decimal
    custentity_sls_budgeted_cost: Decimal
    custentity_sls_estimated_cost_to_complete: Decimal
    custentity_sls_retainage_pct: Decimal


class NsVendorBill(BaseModel):
    job: str
    amount: Decimal


class NsInvoice(BaseModel):
    internalId: str
    job: str
    tranDate: date
    amount: Decimal


class NsCustomerPayment(BaseModel):
    job: str
    amount: Decimal


class NsChangeOrder(BaseModel):
    job: str
    amount: Decimal
    custbody_sls_co_status: str
    custbody_sls_co_kind: str


@dataclass(frozen=True)
class NetSuiteSnapshot:
    jobs: list[NsJob]
    vendor_bills: list[NsVendorBill]
    invoices: list[NsInvoice]
    payments: list[NsCustomerPayment]
    change_orders: list[NsChangeOrder]
