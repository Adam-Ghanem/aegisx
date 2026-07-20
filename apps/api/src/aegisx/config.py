from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AEGISX_", env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql+psycopg://aegisx:aegisx@postgres:5432/aegisx"
    redis_url: str = "redis://redis:6379/0"
    token_signing_key: str = Field(default="development-only-change-me-32-bytes", min_length=32)
    token_hash_key: str = Field(default="development-refresh-hash-key-32bytes", min_length=32)
    allowed_origins: list[str] = ["http://localhost:5173"]

    @model_validator(mode="after")
    def fail_closed_in_production(self) -> "Settings":
        if self.environment == "production" and (
            "development" in self.token_signing_key or "development" in self.token_hash_key
        ):
            raise ValueError("production token keys must be explicitly configured")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
