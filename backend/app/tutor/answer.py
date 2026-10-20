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
    return any(a and len(a & set(terms(c))) / len(a | set(terms(c))) > 0.6 for c in chosen)


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


def build_answer(question: str, hits: list[Scored], info: dict, index: TutorIndex) -> dict:
    if not hits:
        registry_lessons = sorted({(p.lesson_number, p.lesson_id, p.lesson_title) for p in index.passages})
        return {
            "covered": False,
            "message": NOT_COVERED,
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
            if text in seen_text or len(sentences) >= MAX_SENTENCES or _near_duplicate(text, list(seen_text)):
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
    top_stage = facts[0].passage.stage_id if facts else None
    analogy = next(
        (h.passage for h in hits if h.passage.teaching_aid and h.passage.stage_id == top_stage), None
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
        "covered": True,
        "message": None,
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
