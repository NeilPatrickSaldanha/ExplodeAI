from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from app.ai.guard import estimate_cost, load_prices
from app.db import get_session
from app.deps import experiment_limiter, learner_id
from app.routers.ai import _paid_call
from app.tutor import quiz
from app.tutor.answer import NOT_COVERED, build_answer
from app.tutor.prompt import build_prompt, check_citations
from app.tutor.search import get_index

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=300)
    lesson_id: str | None = None
    stage_id: str | None = None

    @field_validator("question")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = " ".join(v.split())
        if len(v) < 3:
            raise ValueError("question is too short")
        return v


def _retrieve(req: AskRequest, k: int = 5):
    index = get_index()
    hits, info = index.search(req.question, lesson_id=req.lesson_id, stage_id=req.stage_id, k=k)
    return index, hits, info


@router.post("/ask")
def ask(req: AskRequest, learner: str = Depends(learner_id)):
    """Free and offline: quotes verified lesson content with its claims and sources."""
    experiment_limiter.check(learner)
    index, hits, info = _retrieve(req)
    return build_answer(req.question, hits, info, index)


@router.get("/suggestions")
def get_suggestions(lesson_id: str | None = None, stage_id: str | None = None):
    return {"suggestions": quiz.suggestions(lesson_id, stage_id)}


@router.get("/check")
def get_check(
    lesson_id: str, stage_id: str, n: int = Query(0, ge=0, le=1000), learner: str = Depends(learner_id)
):
    experiment_limiter.check(learner)
    return quiz.check(lesson_id, stage_id, n)


class LlmRequest(AskRequest):
    provider: str
    model: str
    max_output_tokens: int = Field(250, ge=1)
    confirm_paid: bool = False


@router.post("/ask/estimate")
def estimate(req: LlmRequest):
    """Worst-case cost of the AI-polished answer. Free: nothing is sent to a provider."""
    price = load_prices().get((req.provider, req.model))
    if price is None:
        raise HTTPException(404, {"code": "model_not_allowed", "message": "Model is not allow-listed."})
    _, hits, info = _retrieve(req)
    if not hits:
        return {"covered": False, "max_cost_usd": 0.0, "passages": 0, "message": NOT_COVERED}
    prompt, _ = build_prompt(req.question, hits)
    return {
        "covered": True,
        "max_cost_usd": round(estimate_cost(price, prompt, req.max_output_tokens), 6),
        "passages": len(hits),
    }


@router.post("/ask/llm")
def ask_llm(req: LlmRequest, learner: str = Depends(learner_id), session: Session = Depends(get_session)):
    """Paid, optional. The server builds the prompt from retrieved lesson passages only, so this
    cannot be used as a general-purpose proxy, and a question the lessons do not cover costs nothing."""
    experiment_limiter.check(learner)
    index, hits, info = _retrieve(req)
    if not hits:
        return {**build_answer(req.question, hits, info, index), "is_llm": False, "cost_usd": 0.0}
    prompt, allowed = build_prompt(req.question, hits)
    out = _paid_call(
        session, learner, req.provider, req.model, prompt, req.max_output_tokens, req.confirm_paid
    )
    checked = check_citations(out["text"], allowed)
    base = build_answer(req.question, hits, info, index)
    return {
        **out,
        **checked,
        "covered": True,
        "claims": [c for c in base["claims"] if c["id"] in checked["cited"]],
        "sources": base["sources"],
        "related": base["related"],
    }
