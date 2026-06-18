from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MOCK_NETSUITE_")

    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    stream_interval_seconds: float = 2.6
    database_url: str = "postgresql+asyncpg://sls:sls@localhost:5432/mock_netsuite"


def get_settings() -> Settings:
    return Settings()
