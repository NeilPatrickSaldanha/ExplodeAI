"""Guard for paid AI provider calls. Every paid request passes through `authorize`.

A request is refused unless ALL of these hold, checked in this order:
 1. AI_EMERGENCY_DISABLE is false                 (kill switch wins over everything)
 2. AI_FEATURES_ENABLED is true                   (off by default)
 3. the provider's API key is configured          (presence only; value never leaves Settings)
 4. the model is allow-listed with prices in pricing.yaml   (fail closed)
 5. the caller sent confirm_paid = true           (explicit, per request)
 6. requested output tokens ≤ AI_MAX_OUTPUT_TOKENS
 7. learner is under AI_MAX_REQUESTS_PER_HOUR
 8. today's estimated spend + this request's worst-case estimate ≤ AI_DAILY_BUDGET_USD

Cost estimates are deliberately conservative (≈ 1 token per 3 characters of
input, and the full output allowance) and are labelled as estimates everywhere.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel
from sqlmodel import Session, func, select

from app.config import Settings
from app.db import AIUsage

PRICING_FILE = Path(__file__).with_name("pricing.yaml")
PROVIDERS = ("anthropic", "openai", "gemini")


class ModelPrice(BaseModel):
    provider: str
    model: str
    input_usd_per_million_tokens: float
    output_usd_per_million_tokens: float
    price_checked: str
    price_source: str


@lru_cache
def load_prices(path: Path = PRICING_FILE) -> dict[tuple[str, str], ModelPrice]:
    data = yaml.safe_load(path.read_text()) or {}
    prices = [ModelPrice.model_validate(m) for m in data.get("models") or []]
    return {(p.provider, p.model): p for p in prices}


class GuardRefusal(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class Authorization:
    price: ModelPrice
    estimated_cost_usd: float


def estimate_tokens(text: str) -> int:
    return max(1, -(-len(text) // 3))  # ceil(len/3): conservative for English


def estimate_cost(price: ModelPrice, prompt: str, max_output_tokens: int) -> float:
    return (
        estimate_tokens(prompt) * price.input_usd_per_million_tokens
        + max_output_tokens * price.output_usd_per_million_tokens
    ) / 1_000_000


def key_configured(settings: Settings, provider: str) -> bool:
    key = {
        "anthropic": settings.anthropic_api_key,
        "openai": settings.openai_api_key,
        "gemini": settings.gemini_api_key,
    }[provider]
    return bool(key.get_secret_value().strip())


def spent_today(session: Session, now: datetime) -> float:
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    total = session.exec(
        select(func.sum(AIUsage.estimated_cost_usd)).where(AIUsage.created_at >= start)
    ).one()
    return float(total or 0.0)


def requests_last_hour(session: Session, learner_id: str, now: datetime) -> int:
    return session.exec(
        select(func.count()).select_from(AIUsage).where(
            AIUsage.learner_id == learner_id, AIUsage.created_at >= now - timedelta(hours=1)
        )
    ).one()


def authorize(
    settings: Settings,
    session: Session,
    *,
    learner_id: str,
    provider: str,
    model: str,
    prompt: str,
    max_output_tokens: int,
    confirm_paid: bool,
    prices: dict[tuple[str, str], ModelPrice] | None = None,
    now: datetime | None = None,
) -> Authorization:
    now = now or datetime.now(UTC)
    prices = load_prices() if prices is None else prices
    if settings.ai_emergency_disable:
        raise GuardRefusal("emergency_disabled", "Paid AI features are switched off (kill switch).")
    if not settings.ai_features_enabled:
        raise GuardRefusal("disabled", "Paid AI features are disabled (AI_FEATURES_ENABLED=false).")
    if provider not in PROVIDERS:
        raise GuardRefusal("unknown_provider", f"Unknown provider '{provider}'.")
    if not key_configured(settings, provider):
        raise GuardRefusal("no_key", f"No API key configured for {provider}.")
    price = prices.get((provider, model))
    if price is None:
        raise GuardRefusal(
            "model_not_allowed", f"{provider}/{model} is not allow-listed with prices in pricing.yaml."
        )
    if not confirm_paid:
        raise GuardRefusal("not_confirmed", "This is a paid request; confirm_paid must be true.")
    if max_output_tokens > settings.ai_max_output_tokens:
        raise GuardRefusal(
            "too_many_tokens", f"max_output_tokens exceeds the limit of {settings.ai_max_output_tokens}."
        )
    if requests_last_hour(session, learner_id, now) >= settings.ai_max_requests_per_hour:
        raise GuardRefusal("rate_limited", "Hourly paid-request limit reached. Try again later.")
    cost = estimate_cost(price, prompt, max_output_tokens)
    if spent_today(session, now) + cost > settings.ai_daily_budget_usd:
        raise GuardRefusal("budget_exceeded", "Today's estimated AI budget would be exceeded.")
    return Authorization(price=price, estimated_cost_usd=round(cost, 6))
