from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from app.ai.guard import estimate_cost, load_prices
from app.db import get_session
from app.deps import experiment_limiter, learner_id
from app.routers.ai import _paid_call
from app.tutor import intent as intents
from app.tutor import quiz
from app.tutor.answer import NOT_COVERED, build_answer, chat_reply, overview_reply, plain_reply
from app.tutor.chat import Context, Turn, resolve
from app.tutor.prompt import build_prompt, check_citations
from app.tutor.search import get_index

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


FREE_INTENTS = ("greeting", "thanks", "help", "overview", "lesson_about")


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=300)
    lesson_id: str | None = None
    stage_id: str | None = None
    history: list[Turn] = Field(default_factory=list, max_length=6)

    @field_validator("question")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = " ".join(v.split())
        if len(v) < 3:
            raise ValueError("question is too short")
        return v


def _retrieve(req: AskRequest, k: int = 5):
    index = get_index()
    ctx = resolve(req.question, req.lesson_id, req.stage_id, req.history)
    hits, info = index.search(
        ctx.search_text,
        lesson_id=ctx.lesson_id,
        stage_id=ctx.stage_id,
        k=k,
        prefer=intents.kind_preference(req.question),
    )
    return index, ctx, hits, info


def _free_reply(req: AskRequest, ctx: Context, index, hits, info) -> dict | None:
    """Replies that need no search and no model: small talk, and re-explaining the current stage."""
    if ctx.intent == "greeting":
        return chat_reply(intents.GREETING_REPLY)
    if ctx.intent == "thanks":
        return chat_reply(intents.THANKS_REPLY)
    if ctx.intent == "help":
        return chat_reply(intents.HELP_REPLY)
    if ctx.intent == "overview":
        return overview_reply()
    if ctx.intent == "lesson_about":
        return overview_reply(intents.lesson_number(req.question))
    if ctx.intent in ("simplify", "example", "more", "why"):
        if ctx.lesson_id and ctx.stage_id:
            r = plain_reply(ctx.lesson_id, ctx.stage_id, ctx.intent, info)
            if r:
                return r
        return chat_reply(intents.NEEDS_TOPIC)
    return None


def _answer(req: AskRequest, ctx: Context, index, hits, info) -> dict:
    open_stage = (ctx.lesson_id, ctx.stage_id) if ctx.lesson_id and ctx.stage_id else None
    return build_answer(req.question, hits, info, index, open_stage=open_stage)


@router.post("/ask")
def ask(req: AskRequest, learner: str = Depends(learner_id)):
    """Free and offline: quotes verified lesson content with its claims and sources, leads with the
    stage's plain-words explanation, and remembers the conversation the client sends back."""
    experiment_limiter.check(learner)
    index, ctx, hits, info = _retrieve(req)
    return _free_reply(req, ctx, index, hits, info) or _answer(req, ctx, index, hits, info)


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
    """Worst-case cost of the AI-explained answer. Free: nothing is sent to a provider."""
    price = load_prices().get((req.provider, req.model))
    if price is None:
        raise HTTPException(404, {"code": "model_not_allowed", "message": "Model is not allow-listed."})
    index, ctx, hits, info = _retrieve(req, k=6)
    if ctx.intent in FREE_INTENTS or not hits:
        return {
            "covered": bool(hits),
            "max_cost_usd": 0.0,
            "passages": 0,
            "message": NOT_COVERED if not hits else None,
        }
    prompt, _ = build_prompt(req.question, hits, req.history, ctx.intent)
    return {
        "covered": True,
        "max_cost_usd": round(estimate_cost(price, prompt, req.max_output_tokens), 6),
        "passages": len(hits),
    }


@router.post("/ask/llm")
def ask_llm(req: LlmRequest, learner: str = Depends(learner_id), session: Session = Depends(get_session)):
    """Paid, optional. The server builds the prompt from retrieved lesson passages and the recent
    conversation, so this cannot be used as a general-purpose proxy. Small talk and questions the
    lessons do not cover are answered free, with no provider call."""
    experiment_limiter.check(learner)
    index, ctx, hits, info = _retrieve(req, k=6)
    if ctx.intent in FREE_INTENTS:
        return {**_free_reply(req, ctx, index, hits, info), "is_llm": False, "cost_usd": 0.0}
    if not hits:
        return {**_answer(req, ctx, index, hits, info), "is_llm": False, "cost_usd": 0.0}
    prompt, allowed = build_prompt(req.question, hits, req.history, ctx.intent)
    out = _paid_call(
        session, learner, req.provider, req.model, prompt, req.max_output_tokens, req.confirm_paid
    )
    checked = check_citations(out["text"], allowed)
    base = _answer(req, ctx, index, hits, info)
    return {
        **out,
        **checked,
        "type": "llm",
        "covered": True,
        "claims": [c for c in base["claims"] if c["id"] in checked["cited"]] or base["claims"],
        "sources": base["sources"],
        "related": base["related"],
    }
