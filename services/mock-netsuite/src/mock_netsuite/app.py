from __future__ import annotations

import asyncio
import itertools
from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sse_starlette.sse import EventSourceResponse

from mock_netsuite.config import Settings, get_settings
from mock_netsuite.db import Base, create_engine, create_sessionmaker
from mock_netsuite.records import (
    ChangeOrder,
    CustomerPayment,
    Invoice,
    Job,
    NsRecord,
    VendorBill,
)
from mock_netsuite.repository import (
    RECORD_MODELS,
    fetch_collection,
    fetch_record,
    seed_if_empty,
)

STREAM_DATE = date(2026, 6, 17)

WIRE_MODELS: dict[str, type[NsRecord]] = {
    "job": Job,
    "vendorbill": VendorBill,
    "invoice": Invoice,
    "customerpayment": CustomerPayment,
    "changeorder": ChangeOrder,
}

# Scripted live feed: each posting nudges a project's story when applied —
# DFW cost overrun deepens, UT cash arrives, PHX bills more progress.
LIVE_POSTINGS: tuple[NsRecord, ...] = (
    VendorBill(
        internalId="VB-1001-live",
        tranId="BILL1001LIVE",
        tranDate=STREAM_DATE,
        entity="Lone Star General Contractors",
        job="1001",
        amount=Decimal("45000.00"),
        memo="Unplanned MEP rework",
    ),
    CustomerPayment(
        internalId="PMT-1003-live",
        tranId="PMT1003LIVE",
        tranDate=STREAM_DATE,
        entity="University of Texas System",
        job="1003",
        amount=Decimal("75000.00"),
        appliedToInvoice="INV-1003-1",
    ),
    Invoice(
        internalId="INV-1004-live",
        tranId="INV1004LIVE",
        tranDate=STREAM_DATE,
        entity="Phoenix Aviation Authority",
        job="1004",
        amount=Decimal("120000.00"),
        memo="Progress billing 3",
    ),
)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    state: dict[str, async_sessionmaker[AsyncSession]] = {}

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
        engine = create_engine(settings.database_url)
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessionmaker = create_sessionmaker(engine)
        async with sessionmaker() as session:
            await seed_if_empty(session)
        state["sessionmaker"] = sessionmaker
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(title="Mock NetSuite", version="0.1.0", lifespan=lifespan)

    async def get_session() -> AsyncIterator[AsyncSession]:
        async with state["sessionmaker"]() as session:
            yield session

    def _wire_model(record_type: str) -> type[NsRecord]:
        wire = WIRE_MODELS.get(record_type)
        if wire is None:
            raise HTTPException(status_code=404, detail=f"Unknown record type: {record_type}")
        return wire

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/record/v1/{record_type}", response_model=None)
    async def list_records(
        record_type: str, session: AsyncSession = Depends(get_session)
    ) -> dict[str, object]:
        wire = _wire_model(record_type)
        rows = await fetch_collection(session, RECORD_MODELS[record_type])
        items = [wire.model_validate(row) for row in rows]
        return {
            "count": len(items),
            "hasMore": False,
            "totalResults": len(items),
            "items": items,
        }

    @app.get("/record/v1/{record_type}/{internal_id}", response_model=None)
    async def get_record(
        record_type: str, internal_id: str, session: AsyncSession = Depends(get_session)
    ) -> NsRecord:
        wire = _wire_model(record_type)
        row = await fetch_record(session, RECORD_MODELS[record_type], internal_id)
        if row is None:
            raise HTTPException(status_code=404, detail=f"{record_type} {internal_id} not found")
        return wire.model_validate(row)

    @app.get("/stream")
    async def stream(request: Request) -> EventSourceResponse:
        async def postings() -> AsyncIterator[dict[str, str]]:
            for sequence, posting in enumerate(itertools.cycle(LIVE_POSTINGS), start=1):
                if await request.is_disconnected():
                    break
                await asyncio.sleep(settings.stream_interval_seconds)
                yield {"event": "posting", "id": str(sequence), "data": posting.model_dump_json()}

        return EventSourceResponse(postings())

    return app


app = create_app()
