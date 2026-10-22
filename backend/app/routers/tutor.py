import re
from dataclasses import dataclass

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
from app.tutor.search import TutorIndex, get_index, looks_like_code

router = APIRouter(prefix="/api/tutor", tags=["tutor"])


FREE_INTENTS = ("recall", "greeting", "thanks", "help", "overview", "lesson_about", "about_me")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=300)
    lesson_id: str | None = None
    stage_id: str | None = None
    history: list[Turn] = Field(default_factory=list, max_length=6)

    @field_validator("question")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = " ".join(v.split())
        if not v:
            raise ValueError("question is empty")
        return v


HOW_ARE_YOU = re.compile(
    r"\bhow\s+(?:are|r)\s+(?:you|u|ya)|how'?s\s+it\s+going|how\s+(?:you|u)\s+doing", re.I
)


@dataclass
class Understood:
    index: TutorIndex
    ctx: Context
    hits: list
    info: dict
    lead: str | None  # a friendly opener when the message started with a greeting
    greeting_only: bool
    brief: bool
    cleaned: str


def _understand(req: AskRequest, k: int = 5) -> Understood:
    """Peel off greetings and filler, work out what is being asked, then search the lessons for it."""
    index = get_index()
    greeted, rest = intents.split_greeting(req.question)
    core = rest or req.question
    cleaned = intents.clean(core)
    ctx = resolve(core, req.lesson_id, req.stage_id, req.history, cleaned=cleaned, vocabulary=index.vocab)
    hits, info = index.search(
        ctx.search_text,
        lesson_id=ctx.lesson_id,
        stage_id=ctx.stage_id,
        k=k,
        prefer=intents.kind_preference(cleaned),
        # A message that names a topic ("what is rag") is not vague: the open lesson must not outrank it.
        vague=not intents.has_topic(ctx.search_text, index.vocab),
    )
    if looks_like_code(req.question):  # checked on the original text: cleaning strips the telltale symbols
        hits, info = [], {**info, "covered": False}
    lead = None
    if greeted and rest:
        lead = "Doing well, thanks for asking!" if HOW_ARE_YOU.search(req.question) else intents.GREETING_LEAD
    return Understood(index, ctx, hits, info, lead, greeted and not rest, intents.is_brief(core), cleaned)


def _greeting(question: str) -> str:
    if HOW_ARE_YOU.search(question):
        return "Doing well, thanks for asking! " + intents.GREETING_REPLY.removeprefix("Hi! ")
    return intents.GREETING_REPLY


def _where(lesson_id: str | None, stage_id: str | None) -> str | None:
    """ "Knowledge source, in Lesson 01 (Retrieval-Augmented Generation, exploded)"."""
    from app.content.loader import content

    lesson = content()[1].get(lesson_id) if lesson_id else None
    if not lesson:
        return None
    stage = next((c.label for c in lesson.components if c.id == stage_id), None)
    place = f"Lesson {lesson.number:02d} ({lesson.title})"
    return f"{stage}, in {place}" if stage else place


def _recall(history: list[Turn]) -> str:
    """Answer "what did I just ask?" from the turns the client sent back."""
    turns = [t for t in history if not intents.RECALL.search(t.question)]
    if not turns:
        return intents.RECALL_EMPTY
    last = turns[-1]
    where = _where(last.lesson_id, last.stage_id)
    reply = f"You just asked: “{last.question.rstrip('?.! ')}”." + (
        f" That was about {where}." if where else ""
    )
    earlier = []
    for t in reversed(turns[:-1]):
        w = _where(t.lesson_id, t.stage_id)
        if w and w != where and w not in earlier:
            earlier.append(w)
    if earlier:
        reply += " Before that we covered " + "; ".join(earlier) + "."
    return reply + " Want me to go on from there?"


def _free_reply(req: AskRequest, u: Understood) -> dict | None:
    """Replies that need no search and no model: small talk, the course itself, re-explaining a stage."""
    ctx = u.ctx
    if ctx.intent == "recall":
        return chat_reply(_recall(req.history))
    if u.greeting_only or ctx.intent == "greeting":
        return chat_reply(_greeting(req.question))
    if ctx.intent == "thanks":
        return chat_reply(intents.THANKS_REPLY)
    if ctx.intent == "about_me":
        return chat_reply(intents.ABOUT_ME_REPLY)
    if ctx.intent == "help":
        return chat_reply(intents.HELP_REPLY)
    if ctx.intent == "overview":
        return overview_reply()
    if ctx.intent == "lesson_about":
        return overview_reply(intents.lesson_number(req.question))
    if ctx.intent in ("simplify", "example", "more", "why"):
        if ctx.lesson_id and ctx.stage_id:
            r = plain_reply(ctx.lesson_id, ctx.stage_id, ctx.intent, u.info)
            if r:
                return r
        return chat_reply(intents.NEEDS_TOPIC)
    return None


def _answer(req: AskRequest, u: Understood) -> dict:
    if (
        not u.hits
        and not looks_like_code(req.question)
        and not intents.looks_like_question(u.cleaned)
        and len(req.question.split()) <= 3
    ):
        # Chatter rather than a question: point the way instead of refusing.
        return chat_reply(intents.SMALLTALK_FALLBACK)
    ctx = u.ctx
    open_stage = (ctx.lesson_id, ctx.stage_id) if ctx.lesson_id and ctx.stage_id else None
    return build_answer(u.cleaned, u.hits, u.info, u.index, open_stage=open_stage, brief=u.brief)


def _with_lead(reply: dict, u: Understood) -> dict:
    return {**reply, "lead": u.lead}


@router.post("/ask")
def ask(req: AskRequest, learner: str = Depends(learner_id)):
    """Free and offline: quotes verified lesson content with its claims and sources, leads with the
    stage's plain-words explanation, and remembers the conversation the client sends back."""
    experiment_limiter.check(learner)
    u = _understand(req)
    return _with_lead(_free_reply(req, u) or _answer(req, u), u)


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


def _is_free(u: Understood) -> bool:
    return u.greeting_only or u.ctx.intent in FREE_INTENTS


def _llm_intent(u: Understood) -> str | None:
    return u.ctx.intent or ("brief" if u.brief else None)


@router.post("/ask/estimate")
def estimate(req: LlmRequest):
    """Worst-case cost of the AI-explained answer. Free: nothing is sent to a provider."""
    price = load_prices().get((req.provider, req.model))
    if price is None:
        raise HTTPException(404, {"code": "model_not_allowed", "message": "Model is not allow-listed."})
    u = _understand(req, k=6)
    if _is_free(u) or not u.hits:
        return {
            "covered": bool(u.hits),
            "max_cost_usd": 0.0,
            "passages": 0,
            "message": None if u.hits else NOT_COVERED,
        }
    prompt, _ = build_prompt(req.question, u.hits, req.history, _llm_intent(u))
    return {
        "covered": True,
        "max_cost_usd": round(estimate_cost(price, prompt, req.max_output_tokens), 6),
        "passages": len(u.hits),
    }


@router.post("/ask/llm")
def ask_llm(req: LlmRequest, learner: str = Depends(learner_id), session: Session = Depends(get_session)):
    """Paid, optional. The server builds the prompt from retrieved lesson passages and the recent
    conversation, so this cannot be used as a general-purpose proxy. Small talk and questions the
    lessons do not cover are answered free, with no provider call."""
    experiment_limiter.check(learner)
    u = _understand(req, k=6)
    if _is_free(u):
        return {**_with_lead(_free_reply(req, u), u), "is_llm": False, "cost_usd": 0.0}
    if not u.hits:
        return {**_with_lead(_answer(req, u), u), "is_llm": False, "cost_usd": 0.0}
    prompt, allowed = build_prompt(req.question, u.hits, req.history, _llm_intent(u))
    out = _paid_call(
        session, learner, req.provider, req.model, prompt, req.max_output_tokens, req.confirm_paid
    )
    checked = check_citations(out["text"], allowed)
    base = _answer(req, u)
    return {
        **out,
        **checked,
        "type": "llm",
        "covered": True,
        "lead": u.lead,
        "claims": [c for c in base["claims"] if c["id"] in checked["cited"]] or base["claims"],
        "sources": base["sources"],
        "related": base["related"],
    }
