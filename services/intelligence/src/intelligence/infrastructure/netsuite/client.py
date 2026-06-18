from __future__ import annotations

import asyncio
from typing import TypeVar

import httpx
from pydantic import BaseModel

from intelligence.infrastructure.netsuite.schemas import (
    NetSuiteSnapshot,
    NsChangeOrder,
    NsCustomerPayment,
    NsInvoice,
    NsJob,
    NsVendorBill,
)

T = TypeVar("T", bound=BaseModel)

NETSUITE_TIMEOUT_SECONDS = 10.0


class NetSuiteClient:
    def __init__(self, base_url: str, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self._base_url = base_url
        self._transport = transport

    async def fetch_snapshot(self) -> NetSuiteSnapshot:
        async with httpx.AsyncClient(
            base_url=self._base_url, transport=self._transport, timeout=NETSUITE_TIMEOUT_SECONDS
        ) as client:
            jobs, bills, invoices, payments, change_orders = await asyncio.gather(
                self._records(client, "job", NsJob),
                self._records(client, "vendorbill", NsVendorBill),
                self._records(client, "invoice", NsInvoice),
                self._records(client, "customerpayment", NsCustomerPayment),
                self._records(client, "changeorder", NsChangeOrder),
            )
        return NetSuiteSnapshot(jobs, bills, invoices, payments, change_orders)

    async def _records(
        self, client: httpx.AsyncClient, record_type: str, model: type[T]
    ) -> list[T]:
        response = await client.get(f"/record/v1/{record_type}")
        response.raise_for_status()
        items = response.json().get("items", [])
        return [model.model_validate(item) for item in items]
