from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(default="FastAPI Template", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    debug: bool = Field(default=False, alias="APP_DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    cors_allow_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=list,
        alias="CORS_ALLOW_ORIGINS",
    )
    auth_cookie_name: str = Field(default="access_token", alias="AUTH_COOKIE_NAME")
    auth_cookie_secure: bool = Field(default=False, alias="AUTH_COOKIE_SECURE")
    auth_cookie_samesite: str = Field(default="lax", alias="AUTH_COOKIE_SAMESITE")
    jwt_secret_key: str = Field(
        default="change-me-to-a-long-random-secret-with-at-least-32-characters",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    seed_admin_enabled: bool = Field(default=False, alias="SEED_ADMIN_ENABLED")
    seed_admin_name: str = Field(default="Admin User", alias="SEED_ADMIN_NAME")
    seed_admin_email: str = Field(default="admin@example.com", alias="SEED_ADMIN_EMAIL")
    seed_admin_password: str = Field(default="admin123456", alias="SEED_ADMIN_PASSWORD")
    database_url: str = Field(
        default="sqlite+pysqlite:///./app.db",
        alias="DATABASE_URL",
    )
    test_database_url: str = Field(
        default="sqlite+pysqlite:///:memory:",
        alias="TEST_DATABASE_URL",
    )

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def parse_cors_allow_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return []


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
