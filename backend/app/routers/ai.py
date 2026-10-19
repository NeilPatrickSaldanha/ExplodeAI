from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.ai import providers
from app.ai.guard import (
    PROVIDERS,
    GuardRefusal,
    actual_cost,
    authorize,
    estimate_cost,
    key_configured,
    load_prices,
    spent_today,
    spent_total,
)
from app.config import get_settings
from app.db import AIUsage, get_session, utcnow
from app.deps import learner_id
from app.experiments.rag import pipeline

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
        "allowed_models": [
            {
                "provider": p,
                "model": m,
                "usable": key_configured(s, p),
                "input_usd_per_million_tokens": price.input_usd_per_million_tokens,
                "output_usd_per_million_tokens": price.output_usd_per_million_tokens,
                "price_checked": price.price_checked,
            }
            for (p, m), price in prices.items()
        ],
        "limits": {
            "daily_budget_usd": s.ai_daily_budget_usd,
            "total_budget_usd": s.ai_total_budget_usd,
            "spent_today_usd": round(spent_today(session, utcnow()), 6),
            "spent_total_usd": round(spent_total(session), 6),
            "max_requests_per_hour": s.ai_max_requests_per_hour,
            "max_output_tokens": s.ai_max_output_tokens,
            "timeout_seconds": s.ai_request_timeout_seconds,
        },
    }


def _paid_call(session: Session, learner: str, provider: str, model: str, prompt: str,
               max_output_tokens: int, confirm_paid: bool) -> dict:
    """Guard → call → ledger. Every attempt that passes the guard is recorded,
    first at its worst-case estimate, then at its actual cost when the provider
    reports token usage."""
    s = get_settings()
    try:
        auth = authorize(s, session, learner_id=learner, provider=provider, model=model,
                         prompt=prompt, max_output_tokens=max_output_tokens, confirm_paid=confirm_paid)
    except GuardRefusal as refusal:
        raise HTTPException(403, {"code": refusal.code, "message": refusal.message}) from refusal

    usage = AIUsage(learner_id=learner, provider=provider, model=model,
                    estimated_cost_usd=auth.estimated_cost_usd, status="ok")
    try:
        gen = providers.generate_with_usage(s, provider, model, prompt, max_output_tokens)
        if gen.input_tokens is not None and gen.output_tokens is not None:
            usage.estimated_cost_usd = round(actual_cost(auth.price, gen.input_tokens, gen.output_tokens), 8)
    except providers.ProviderError as exc:
        usage.status = "error"
        raise HTTPException(502, {"code": "provider_error", "message": str(exc)}) from exc
    except Exception as exc:  # timeouts, network errors
        usage.status = "timeout" if "Timeout" in type(exc).__name__ else "error"
        raise HTTPException(504, {"code": usage.status, "message": "Provider request failed."}) from exc
    finally:
        session.add(usage)
        session.commit()
    return {
        "text": gen.text,
        "provider": provider,
        "model": model,
        "input_tokens": gen.input_tokens,
        "output_tokens": gen.output_tokens,
        "cost_usd": usage.estimated_cost_usd,
        "max_cost_usd": auth.estimated_cost_usd,
        "spent_total_usd": round(spent_total(session), 6),
        "is_llm": True,
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
    return _paid_call(session, learner, req.provider, req.model, req.prompt,
                      req.max_output_tokens, req.confirm_paid)


class RagAnswerRequest(pipeline.RagParams):
    provider: str
    model: str
    max_output_tokens: int = Field(200, ge=1)
    confirm_paid: bool = False


def _rag_prompt(req: RagAnswerRequest) -> tuple[str, dict]:
    params = pipeline.RagParams.model_validate(req.model_dump(include=set(pipeline.RagParams.model_fields)))
    result = pipeline.run(params)
    return result["prompt"]["text"], result["prompt"]


@router.post("/rag-answer/estimate")
def rag_answer_estimate(req: RagAnswerRequest):
    """Worst-case cost of answering this lesson question with the chosen model. Free: no call."""
    price = load_prices().get((req.provider, req.model))
    if price is None:
        raise HTTPException(404, {"code": "model_not_allowed", "message": "Model is not allow-listed."})
    prompt, meta = _rag_prompt(req)
    return {"max_cost_usd": round(estimate_cost(price, prompt, req.max_output_tokens), 6),
            "prompt_words": len(prompt.split()), "included": meta["included"]}


@router.post("/rag-answer")
def rag_answer(req: RagAnswerRequest, learner: str = Depends(learner_id),
               session: Session = Depends(get_session)):
    """Answer the lesson's question with a real LLM. The server builds the prompt from
    the RAG pipeline, so this endpoint cannot be used as a general-purpose paid proxy."""
    prompt, meta = _rag_prompt(req)
    out = _paid_call(session, learner, req.provider, req.model, prompt,
                     req.max_output_tokens, req.confirm_paid)
    return {**out, "included": meta["included"], "prompt_words": len(prompt.split())}
