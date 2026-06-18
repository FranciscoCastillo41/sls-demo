from __future__ import annotations

import logging
from collections.abc import Callable
from decimal import ROUND_HALF_EVEN, getcontext

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from intelligence.application.ports import ProjectSource
from intelligence.application.use_cases import build_portfolio
from intelligence.infrastructure.netsuite.adapter import NetSuiteProjectSource
from intelligence.infrastructure.netsuite.client import NetSuiteClient
from intelligence.interface.api.schemas import PortfolioReport, to_portfolio_report
from intelligence.interface.config import Settings, get_settings

logger = logging.getLogger(__name__)

DECIMAL_PRECISION = 28


def configure_decimal_context() -> None:
    context = getcontext()
    context.prec = DECIMAL_PRECISION
    context.rounding = ROUND_HALF_EVEN


def create_app(
    settings: Settings | None = None,
    source_factory: Callable[[], ProjectSource] | None = None,
) -> FastAPI:
    resolved = settings or get_settings()
    configure_decimal_context()

    def default_source() -> ProjectSource:
        return NetSuiteProjectSource(NetSuiteClient(resolved.netsuite_base_url))

    provide_source = source_factory or default_source
    app = FastAPI(title="Intelligence", version="0.1.0")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/portfolio", response_model=PortfolioReport)
    async def portfolio() -> PortfolioReport:
        try:
            metrics = await build_portfolio(provide_source(), resolved.as_of)
        except (httpx.HTTPError, ValidationError) as error:
            logger.exception("failed to load portfolio from NetSuite source")
            raise HTTPException(status_code=502, detail="NetSuite source unavailable") from error
        return to_portfolio_report(metrics)

    return app


app = create_app()
