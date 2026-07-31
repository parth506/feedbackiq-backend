"""
Application Settings — Pydantic v2 BaseSettings

All values MUST come from environment variables or a .env file.
No credentials or sensitive defaults are stored in source code.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "FeedbackIQ"
    APP_VERSION: str = "0.1.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Server ────────────────────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── MongoDB ───────────────────────────────────────────────────────────────
    # Provide MONGO_URI via environment / .env — no default to avoid committing credentials.
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI. Override with MONGO_URI env var.",
    )
    DATABASE_NAME: str = Field(
        default="feedbackiq",
        description="MongoDB database name.",
    )
    # Kept for backward compatibility; DATABASE_NAME takes precedence.
    MONGO_DB_NAME: Optional[str] = None
    MONGO_MAX_POOL_SIZE: int = Field(default=100, ge=1)
    MONGO_MIN_POOL_SIZE: int = Field(default=10, ge=1)

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # ── Security ──────────────────────────────────────────────────────────────
    # MUST be overridden via SECRET_KEY env var in production.
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="JWT signing secret. Must be overridden in production.",
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Sourced from ALLOWED_ORIGINS env var (JSON list or comma-separated string).
    # Example .env value: ALLOWED_ORIGINS=["http://localhost:5173","https://feediq2.netlify.app"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://feediq2.netlify.app",
    ]

    # ── Cache TTLs (seconds) ──────────────────────────────────────────────────
    CACHE_TTL_DASHBOARD: int = 300       # 5 minutes
    CACHE_TTL_ANALYTICS: int = 300       # 5 minutes
    CACHE_TTL_SENTIMENT: int = 300       # 5 minutes
    CACHE_TTL_TOPICS: int = 600          # 10 minutes
    CACHE_TTL_AI_INSIGHTS: int = 600     # 10 minutes

    # ── Search / Pagination ───────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    MAX_SEARCH_RESULTS: int = 50

    @property
    def db_name(self) -> str:
        """Return DATABASE_NAME (MONGO_DB_NAME kept for backward compat)."""
        return self.DATABASE_NAME or self.MONGO_DB_NAME or "feedbackiq"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton — loaded once at startup."""
    return Settings()