from __future__ import annotations

from datetime import date

from intelligence.application.ports import ProjectSource
from intelligence.domain.engine import compute_portfolio
from intelligence.domain.metrics import PortfolioMetrics


async def build_portfolio(source: ProjectSource, as_of: date) -> PortfolioMetrics:
    projects = await source.load_projects()
    return compute_portfolio(projects, as_of)
