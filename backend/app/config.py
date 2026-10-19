"""Application settings, loaded from environment / backend/.env.

Secrets (provider API keys) are held as SecretStr so they never appear in reprs,
logs, or API responses. Only *presence* of a key is ever exposed.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Provider keys — optional. Empty string means "not configured".
    openai_api_key: SecretStr = SecretStr("")
    gemini_api_key: SecretStr = SecretStr("")
    anthropic_api_key: SecretStr = SecretStr("")

    # Paid AI guard.
    ai_features_enabled: bool = False
    ai_emergency_disable: bool = False
    ai_daily_budget_usd: float = 1.0
    # Lifetime cap across all days: the sum of every recorded call may never exceed it.
    ai_total_budget_usd: float = 4.0
    ai_max_requests_per_hour: int = 10
    ai_request_timeout_seconds: float = 20.0
    ai_max_output_tokens: int = 300

    # App.
    database_url: str = f"sqlite:///{BACKEND_DIR / 'data' / 'explodeai.sqlite3'}"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    show_draft_lessons: bool = False
    content_dir: Path = REPO_DIR / "content"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
