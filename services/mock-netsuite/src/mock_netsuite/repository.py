from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from mock_netsuite.db import Base
from mock_netsuite.models import (
    ChangeOrderRow,
    CustomerPaymentRow,
    InvoiceRow,
    JobRow,
    VendorBillRow,
)
from mock_netsuite.seed import build_rows

RECORD_MODELS: dict[str, type[Base]] = {
    "job": JobRow,
    "vendorbill": VendorBillRow,
    "invoice": InvoiceRow,
    "customerpayment": CustomerPaymentRow,
    "changeorder": ChangeOrderRow,
}


async def seed_if_empty(session: AsyncSession) -> None:
    existing = await session.scalar(select(func.count()).select_from(JobRow))
    if existing:
        return
    session.add_all(build_rows())
    await session.commit()


async def fetch_collection(session: AsyncSession, model: type[Base]) -> Sequence[Base]:
    result = await session.scalars(select(model))
    return result.all()


async def fetch_record(session: AsyncSession, model: type[Base], internal_id: str) -> Base | None:
    return await session.get(model, internal_id)
