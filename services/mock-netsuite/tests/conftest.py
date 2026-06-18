from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from testcontainers.postgres import PostgresContainer

from mock_netsuite.app import create_app
from mock_netsuite.config import Settings


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    with PostgresContainer("postgres:16-alpine", driver="asyncpg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def client(database_url: str) -> Iterator[TestClient]:
    app = create_app(Settings(database_url=database_url))
    with TestClient(app) as test_client:
        yield test_client
