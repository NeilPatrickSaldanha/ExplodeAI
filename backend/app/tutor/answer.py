"""Turn retrieved passages into a grounded answer.

The default answer is extractive: it quotes the best-matching sentences from verified lesson
content and attaches the claims and sources behind each one. Nothing is generated, so nothing
can be invented. If the lessons do not cover the question, it says so.
"""

from dataclasses import dataclass

from app.content.loader import content
from app.experiments.rag.text import sentence_spans, terms
from app.tutor.index import Passage
from app.tutor.search import Scored, TutorIndex

MAX_SENTENCES = 3
NOT_COVERED = "ExplodeAI's lessons don't cover that, so I won't guess."


@dataclass(frozen=True)
class Sentence:
    text: str
    passage: Passage


def _claim_texts() -> dict[str, str]:
    _, lessons = content()
    return {c.id: c.text for lesson in lessons.values() for c in lesson.claims}


def narrow_claims(sentence: str, claim_ids: tuple[str, ...], keep: int = 2) -> list[str]:
    """A stage cites all its claims. For one sentence, cite only the ones that match it."""
    if len(claim_ids) <= keep:
        return list(claim_ids)
    texts = _claim_texts()
    q = set(terms(sentence))
    ranked = sorted(claim_ids, key=lambda c: (-len(q & set(terms(texts.get(c, "")))), claim_ids.index(c)))
    return ranked[:keep]


def _near_duplicate(text: str, chosen: list[str]) -> bool:
    a = set(terms(text))
    return any(a and len(a & set(terms(c))) / len(a | set(terms(c))) > 0.5 for c in chosen)


def best_sentences(question: str, passage: Passage, limit: int) -> list[str]:
    spans = [passage.text[s:e].strip() for s, e in sentence_spans(passage.text)]
    q = set(terms(question))
    scored = sorted(spans, key=lambda s: (-len(q & set(terms(s))), spans.index(s)))
    keep = [s for s in scored if len(q & set(terms(s))) > 0][:limit] or spans[:1]
    return [s for s in spans if s in keep]  # restore original order


def _source_cards(source_ids: list[str]) -> list[dict]:
    registry, _ = content()
    by_id = registry.by_id()
    return [
        {
            "id": s,
            "title": by_id[s].title,
            "publisher": by_id[s].publisher,
            "url": str(by_id[s].url),
            "version": by_id[s].version,
        }
        for s in source_ids
        if s in by_id
    ]


def _claim_cards(claim_ids: list[str]) -> list[dict]:
    _, lessons = content()
    texts = {c.id: (lesson.id, c.text) for lesson in lessons.values() for c in lesson.claims}
    return [{"id": c, "lesson_id": texts[c][0], "text": texts[c][1]} for c in claim_ids if c in texts]


def _stage_ref(lesson_id: str, stage_id: str):
    _, lessons = content()
    lesson = lessons.get(lesson_id)
    comp = next((c for c in lesson.components if c.id == stage_id), None) if lesson else None
    return lesson, comp


def plain_block(lesson_id: str, stage_id: str, mode: str = "simplify") -> dict | None:
    """The stage's beginner-friendly explanation (hand-written for the lesson, tied to verified claims)."""
    lesson, comp = _stage_ref(lesson_id, stage_id)
    if comp is None or comp.explain is None:
        return None
    e = comp.explain
    block = {
        "lesson_id": lesson_id,
        "stage_id": stage_id,
        "stage_label": comp.label,
        "mode": mode,
        "what": None,
        "why": None,
        "analogy": None,
        "example": None,
        "happens": [],
        "misconfigured": None,
        "more": None,
    }
    if mode == "brief":
        block.update(what=e.what)
    elif mode in ("simplify", "answer"):
        block.update(
            what=e.what,
            analogy=e.analogy,
            example=e.example.model_dump(),
            happens=list(e.happens) if mode == "simplify" else [],
        )
    elif mode == "example":
        block.update(example=e.example.model_dump(), happens=list(e.happens), analogy=e.analogy)
    elif mode == "why":
        block.update(why=e.why, analogy=e.analogy)
    elif mode == "more":
        spans = [e.learn_more[a:b].strip() for a, b in sentence_spans(e.learn_more)][:3]
        block.update(why=e.why, misconfigured=e.misconfigured, more=" ".join(spans))
    return block


def _empty(kind: str, message: str | None, info: dict, **extra) -> dict:
    base = {
        "type": kind,
        "covered": True,
        "message": message,
        "sentences": [],
        "analogy": None,
        "plain": None,
        "claims": [],
        "sources": [],
        "related": [],
        "topics": [],
        "meta": info,
    }
    base.update(extra)
    return base


def overview_reply(number: int | None = None) -> dict:
    """The course itself: what each lesson covers. Built from the lessons' own summaries and objectives."""
    _, lessons = content()
    items = [
        {
            "number": lesson.number,
            "lesson_id": lesson.id,
            "title": lesson.title,
            "summary": lesson.summary,
            "objectives": list(lesson.objectives),
            "minutes": lesson.estimated_minutes,
            "stages": [c.label for c in lesson.components],
        }
        for lesson in sorted(lessons.values(), key=lambda lesson: lesson.number)
        if number is None or lesson.number == number
    ]
    if not items:
        return chat_reply(
            "There are four lessons, numbered 1 to 4. Ask “what are all four lessons?” to see them."
        )
    info = {"method": "course", "covered": True, "coverage": 1.0, "best_dense": None}
    return _empty("overview", None, info, lessons=items, focus_number=number)


def chat_reply(message: str, info: dict | None = None) -> dict:
    return _empty(
        "chat", message, info or {"method": "chat", "covered": True, "coverage": 1.0, "best_dense": None}
    )


def plain_reply(lesson_id: str, stage_id: str, mode: str, info: dict) -> dict | None:
    block = plain_block(lesson_id, stage_id, mode)
    if block is None:
        return None
    lesson, comp = _stage_ref(lesson_id, stage_id)
    claim_ids = list(comp.explain.claims)[:3]
    by_claim = {c.id: c for c in lesson.claims}
    sources: list[str] = []
    for cid in claim_ids:
        for cit in by_claim[cid].citations if cid in by_claim else []:
            if cit.source not in sources:
                sources.append(cit.source)
    return _empty(
        "plain",
        None,
        info,
        plain=block,
        claims=_claim_cards(claim_ids),
        sources=_source_cards(sources[:6]),
        related=[
            {
                "lesson_id": lesson_id,
                "lesson_title": lesson.title,
                "stage_id": stage_id,
                "stage_label": comp.label,
            }
        ],
    )


def build_answer(
    question: str,
    hits: list[Scored],
    info: dict,
    index: TutorIndex,
    open_stage: tuple[str, str] | None = None,
    brief: bool = False,
) -> dict:
    if not hits:
        registry_lessons = sorted({(p.lesson_number, p.lesson_id, p.lesson_title) for p in index.passages})
        return {
            "type": "none",
            "covered": False,
            "message": NOT_COVERED,
            "plain": None,
            "sentences": [],
            "analogy": None,
            "claims": [],
            "sources": [],
            "related": [],
            "topics": [{"lesson_id": i, "title": t, "number": n} for n, i, t in registry_lessons],
            "meta": info,
        }
    facts = [h for h in hits if not h.passage.teaching_aid]
    sentences: list[dict] = []
    used_claims: list[str] = []
    seen_text: set[str] = set()
    for h in facts:
        for text in best_sentences(question, h.passage, 2 if not sentences else 1):
            if (
                text in seen_text
                or len(sentences) >= (1 if brief else MAX_SENTENCES)
                or _near_duplicate(text, list(seen_text))
            ):
                continue
            seen_text.add(text)
            cites = narrow_claims(text, h.passage.claim_ids)
            sentences.append(
                {
                    "text": text,
                    "passage_id": h.passage.id,
                    "kind": h.passage.kind,
                    "claim_ids": cites,
                    "lesson_id": h.passage.lesson_id,
                    "lesson_title": h.passage.lesson_title,
                    "stage_id": h.passage.stage_id,
                    "stage_label": h.passage.stage_label,
                }
            )
            for c in cites:
                if c not in used_claims:
                    used_claims.append(c)
    # Plain words go first. They explain the stage the answer is about: the open stage if the answer
    # touches it, otherwise the best-matching stage.
    stages = [(h.passage.lesson_id, h.passage.stage_id) for h in facts[:3] if h.passage.stage_id]
    chosen = open_stage if open_stage in stages else (stages[0] if stages else None)
    plain = plain_block(chosen[0], chosen[1], "brief" if brief else "answer") if chosen else None
    top_stage = chosen[1] if chosen else None
    analogy = (
        None
        if plain
        else next(
            (h.passage for h in hits if h.passage.teaching_aid and h.passage.stage_id == top_stage), None
        )
    )
    source_ids: list[str] = []
    _, lessons = content()
    by_claim = {c.id: c for lesson in lessons.values() for c in lesson.claims}
    for cid in used_claims:
        for cit in by_claim[cid].citations if cid in by_claim else []:
            if cit.source not in source_ids:
                source_ids.append(cit.source)
    related, seen = [], set()
    for h in hits:
        key = (h.passage.lesson_id, h.passage.stage_id)
        if h.passage.stage_id and key not in seen and len(related) < 3:
            seen.add(key)
            related.append(
                {
                    "lesson_id": h.passage.lesson_id,
                    "lesson_title": h.passage.lesson_title,
                    "stage_id": h.passage.stage_id,
                    "stage_label": h.passage.stage_label,
                }
            )
    return {
        "type": "answer",
        "covered": True,
        "message": None,
        "plain": plain,
        "sentences": sentences,
        "analogy": None
        if analogy is None
        else {
            "text": analogy.text,
            "stage_label": analogy.stage_label,
            "note": "A teaching analogy, not a verified fact.",
        },
        "claims": _claim_cards(used_claims),
        "sources": _source_cards(source_ids[:6]),
        "related": related,
        "topics": [],
        "meta": info,
    }
