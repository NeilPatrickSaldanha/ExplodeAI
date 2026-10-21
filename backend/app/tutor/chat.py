"""Conversation context: what the learner is really asking, given what was said before."""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from app.tutor import intent as intents


class Turn(BaseModel):
    """One earlier exchange, sent back by the client (the server keeps no conversation state)."""

    question: str = Field(max_length=300)
    answer_text: str | None = Field(None, max_length=900)
    lesson_id: str | None = None
    stage_id: str | None = None


@dataclass(frozen=True)
class Context:
    intent: str | None
    search_text: str
    lesson_id: str | None
    stage_id: str | None
    focus: Turn | None  # the last earlier exchange that was about a stage


FOLLOWUPS = ("simplify", "example", "more", "why")


def resolve(
    question: str,
    lesson_id: str | None,
    stage_id: str | None,
    history: list[Turn],
    cleaned: str | None = None,
    vocabulary: set[str] | None = None,
) -> Context:
    """`question` is the message without greetings; `cleaned` also drops filler ("tell me in one line")."""
    cleaned = cleaned or question
    focus = next((t for t in reversed(history) if t.stage_id and t.lesson_id), None)
    kind = intents.classify(question)
    # "Explain the causal mask simply" names a topic: it is a question, just asked simply, not a follow-up.
    if kind in FOLLOWUPS and vocabulary is not None and intents.has_topic(cleaned, vocabulary):
        kind = None
    follow = kind in FOLLOWUPS or intents.is_followup(cleaned)
    search = cleaned
    if follow and focus:
        search = f"{focus.question} {cleaned}" if kind is None else focus.question
    # A follow-up stays on the stage the conversation was about, not the stage that happens to be open.
    if follow and focus:
        return Context(kind, search, focus.lesson_id, focus.stage_id, focus)
    if kind in FOLLOWUPS and not focus and lesson_id and stage_id:
        return Context(kind, search, lesson_id, stage_id, None)
    return Context(kind, search, lesson_id, stage_id, focus)
