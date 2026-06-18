# Money columns are NUMERIC(19, 4) -> Decimal round-trips; no float touches a dollar.
# Attribute names mirror the wire records so Pydantic validates a row directly.

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from mock_netsuite.db import Base

_MONEY = Numeric(19, 4)


class JobRow(Base):
    __tablename__ = "job"

    internalId: Mapped[str] = mapped_column(String, primary_key=True)
    recordType: Mapped[str] = mapped_column(String, default="job")
    entityId: Mapped[str]
    companyName: Mapped[str]
    custentity_sls_sector: Mapped[str]
    custentity_sls_billing_model: Mapped[str]
    custentity_sls_contract_fee: Mapped[Decimal] = mapped_column(_MONEY)
    custentity_sls_budgeted_cost: Mapped[Decimal] = mapped_column(_MONEY)
    custentity_sls_estimated_cost_to_complete: Mapped[Decimal] = mapped_column(_MONEY)
    custentity_sls_retainage_pct: Mapped[Decimal] = mapped_column(Numeric(6, 4))
    custentity_sls_billing_rate: Mapped[Decimal | None] = mapped_column(_MONEY, nullable=True)
    startDate: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String, default="In Progress")


class VendorBillRow(Base):
    __tablename__ = "vendorbill"

    internalId: Mapped[str] = mapped_column(String, primary_key=True)
    recordType: Mapped[str] = mapped_column(String, default="vendorbill")
    tranId: Mapped[str]
    tranDate: Mapped[date] = mapped_column(Date)
    entity: Mapped[str]
    job: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[Decimal] = mapped_column(_MONEY)
    memo: Mapped[str] = mapped_column(String, default="")


class InvoiceRow(Base):
    __tablename__ = "invoice"

    internalId: Mapped[str] = mapped_column(String, primary_key=True)
    recordType: Mapped[str] = mapped_column(String, default="invoice")
    tranId: Mapped[str]
    tranDate: Mapped[date] = mapped_column(Date)
    entity: Mapped[str]
    job: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[Decimal] = mapped_column(_MONEY)
    memo: Mapped[str] = mapped_column(String, default="")


class CustomerPaymentRow(Base):
    __tablename__ = "customerpayment"

    internalId: Mapped[str] = mapped_column(String, primary_key=True)
    recordType: Mapped[str] = mapped_column(String, default="customerpayment")
    tranId: Mapped[str]
    tranDate: Mapped[date] = mapped_column(Date)
    entity: Mapped[str]
    job: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[Decimal] = mapped_column(_MONEY)
    appliedToInvoice: Mapped[str]


class ChangeOrderRow(Base):
    __tablename__ = "changeorder"

    internalId: Mapped[str] = mapped_column(String, primary_key=True)
    recordType: Mapped[str] = mapped_column(String, default="changeorder")
    tranDate: Mapped[date] = mapped_column(Date)
    job: Mapped[str] = mapped_column(String, index=True)
    amount: Mapped[Decimal] = mapped_column(_MONEY)
    custbody_sls_co_status: Mapped[str]
    custbody_sls_co_kind: Mapped[str]
    memo: Mapped[str] = mapped_column(String, default="")
