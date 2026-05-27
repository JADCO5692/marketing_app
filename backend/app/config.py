from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://marketing_user:marketing_pass@localhost:5432/marketing_db"

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Security ──────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # ── AI ────────────────────────────────────────────────────────────────────
    CLAUDE_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # ── Research APIs ─────────────────────────────────────────────────────────
    SERPER_API_KEY: str = ""
    HUNTER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    APOLLO_API_KEY: str = ""

    # ── Feature flags ─────────────────────────────────────────────────────────
    RESEARCH_ENABLED: bool = True
    DEDUP_AUTO_MERGE_THRESHOLD: float = 0.97
    DEDUP_REVIEW_THRESHOLD: float = 0.92
    MAX_CONCURRENT_RESEARCH_WORKERS: int = 4

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
