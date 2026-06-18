from __future__ import annotations

from collections.abc import Sequence

from intelligence.domain.project import Project
from intelligence.infrastructure.netsuite.client import NetSuiteClient
from intelligence.infrastructure.netsuite.mapping import build_projects


class NetSuiteProjectSource:
    def __init__(self, client: NetSuiteClient) -> None:
        self._client = client

    async def load_projects(self) -> Sequence[Project]:
        snapshot = await self._client.fetch_snapshot()
        return build_projects(snapshot)
