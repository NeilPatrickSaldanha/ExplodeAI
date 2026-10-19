from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.ai import providers
from app.ai.guard import (
    PROVIDERS,
    GuardRefusal,
    authorize,
    key_configured,
    load_prices,
    spent_today,
)
from app.config import get_settings
from app.db import AIUsage, get_session, utcnow
from app.deps import learner_id

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status")
def status(session: Session = Depends(get_session)):
    """What the UI needs to label paid features. Exposes key *presence* only."""
    s = get_settings()
    prices = load_prices()
    return {
        "enabled": s.ai_features_enabled and not s.ai_emergency_disable,
        "emergency_disabled": s.ai_emergency_disable,
        "providers": {p: {"key_configured": key_configured(s, p)} for p in PROVIDERS},
        "allowed_models": [{"provider": p, "model": m} for (p, m) in prices],
        "limits": {
            "daily_budget_usd": s.ai_daily_budget_usd,
            "spent_today_estimated_usd": round(spent_today(session, utcnow()), 6),
            "max_requests_per_hour": s.ai_max_requests_per_hour,
            "max_output_tokens": s.ai_max_output_tokens,
            "timeout_seconds": s.ai_request_timeout_seconds,
        },
    }


class GenerateRequest(BaseModel):
    provider: str
    model: str
    prompt: str = Field(min_length=1, max_length=20_000)
    max_output_tokens: int = Field(200, ge=1)
    confirm_paid: bool = False


@router.post("/generate")
def generate(req: GenerateRequest, learner: str = Depends(learner_id),
             session: Session = Depends(get_session)):
    s = get_settings()
    try:
        auth = authorize(s, session, learner_id=learner, provider=req.provider, model=req.model,
                         prompt=req.prompt, max_output_tokens=req.max_output_tokens,
                         confirm_paid=req.confirm_paid)
    except GuardRefusal as refusal:
        raise HTTPException(403, {"code": refusal.code, "message": refusal.message}) from refusal

    usage = AIUsage(learner_id=learner, provider=req.provider, model=req.model,
                    estimated_cost_usd=auth.estimated_cost_usd, status="ok")
    try:
        text = providers.generate(s, req.provider, req.model, req.prompt, req.max_output_tokens)
    except providers.ProviderError as exc:
        usage.status = "error"
        raise HTTPException(502, {"code": "provider_error", "message": str(exc)}) from exc
    except Exception as exc:  # timeouts, network errors
        usage.status = "timeout" if "Timeout" in type(exc).__name__ else "error"
        raise HTTPException(504, {"code": usage.status, "message": "Provider request failed."}) from exc
    finally:
        # Record every attempt that passed the guard: failed calls may still be billed.
        session.add(usage)
        session.commit()
    return {"text": text, "estimated_cost_usd": auth.estimated_cost_usd, "is_llm": True}
