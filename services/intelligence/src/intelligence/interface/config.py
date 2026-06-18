from __future__ import annotations

from datetime import date

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict()

    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000
    netsuite_base_url: str = "http://localhost:8001"
    # Anchored to the seeded invoice dates so the demo's aging stays stable; set
    # AS_OF (or wire to today) for a live deployment.
    as_of: date = date(2026, 6, 17)


def get_settings() -> Settings:
    return Settings()
