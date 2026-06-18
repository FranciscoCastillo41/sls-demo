# Field names stay camelCase to mirror NetSuite exactly; money stays Decimal,
# never float. Both are load-bearing — see docs/architecture.md and docs/domain-accounting.md.

from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class BillingModel(StrEnum):
    FIXED_FEE = "fixedFee"
    PERCENT_OF_COST = "percentOfCost"
    TIME_AND_MATERIALS = "timeAndMaterials"


class ChangeOrderStatus(StrEnum):
    APPROVED = "approved"
    PENDING = "pending"


class ChangeOrderKind(StrEnum):
    FEE = "fee"
    COST = "cost"


class NsRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    internalId: str
    recordType: str


class Job(NsRecord):
    recordType: str = "job"
    entityId: str
    companyName: str
    custentity_sls_sector: str
    custentity_sls_billing_model: BillingModel
    custentity_sls_contract_fee: Decimal
    custentity_sls_budgeted_cost: Decimal
    custentity_sls_estimated_cost_to_complete: Decimal
    custentity_sls_retainage_pct: Decimal
    custentity_sls_billing_rate: Decimal | None = None
    startDate: date
    status: str = "In Progress"


class VendorBill(NsRecord):
    recordType: str = "vendorbill"
    tranId: str
    tranDate: date
    entity: str
    job: str
    amount: Decimal
    memo: str = ""


class Invoice(NsRecord):
    recordType: str = "invoice"
    tranId: str
    tranDate: date
    entity: str
    job: str
    amount: Decimal
    memo: str = ""


class CustomerPayment(NsRecord):
    recordType: str = "customerpayment"
    tranId: str
    tranDate: date
    entity: str
    job: str
    amount: Decimal
    appliedToInvoice: str


class TimeBill(NsRecord):
    recordType: str = "timebill"
    tranDate: date
    employee: str
    job: str
    hours: Decimal
    rate: Decimal
    amount: Decimal


class ChangeOrder(NsRecord):
    recordType: str = "changeorder"
    tranDate: date
    job: str
    amount: Decimal
    custbody_sls_co_status: ChangeOrderStatus
    custbody_sls_co_kind: ChangeOrderKind
    memo: str = ""
