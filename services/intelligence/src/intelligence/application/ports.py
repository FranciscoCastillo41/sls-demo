from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from intelligence.domain.project import Project


class ProjectSource(Protocol):
    async def load_projects(self) -> Sequence[Project]: ...
