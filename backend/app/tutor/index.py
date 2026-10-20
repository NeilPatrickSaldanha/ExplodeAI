"""The tutor's knowledge: ExplodeAI's own lessons, split into small citable passages.

Nothing else is ever indexed, so an answer can only come from verified lesson content.
Each passage records where it came from (lesson, stage), which verified claims stand behind
it, and the sources those claims cite. Analogies are kept but flagged, so they are never
presented as facts.
"""

import re
from dataclasses import dataclass, field

from app.content.schema import Lesson, SourceRegistry
from app.experiments.rag.text import sentence_spans


@dataclass(frozen=True)
class Passage:
    id: str
    lesson_id: str
    lesson_number: int
    lesson_title: str
    stage_id: str | None
    stage_label: str | None
    # claim | what | why | misconfigured | learn_more | analogy | breaks | tour | challenge | objective
    kind: str
    text: str
    claim_ids: tuple[str, ...] = ()
    source_ids: tuple[str, ...] = ()
    teaching_aid: bool = False
    # What retrieval matches on: the text plus its place in the lessons, so "softmax" finds the Softmax stage.
    search_text: str = field(default="", compare=False)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _lesson_passages(lesson: Lesson) -> list[Passage]:
    out: list[Passage] = []
    claims = {c.id: c for c in lesson.claims}
    labels = {c.id: c.label for c in lesson.components}
    stage_of: dict[str, str] = {}
    for comp in lesson.components:
        for cid in comp.claims:
            stage_of.setdefault(cid, comp.id)

    def sources(ids) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for cid in ids:
            if cid in claims:
                for cit in claims[cid].citations:
                    seen.setdefault(cit.source)
        return tuple(seen)

    def add(pid, stage, kind, text, claim_ids=(), aid=False):
        text = _clean(text)
        if not text:
            return
        label = labels.get(stage) if stage else None
        out.append(
            Passage(
                id=f"{lesson.id}/{pid}",
                lesson_id=lesson.id,
                lesson_number=lesson.number,
                lesson_title=lesson.title,
                stage_id=stage,
                stage_label=label,
                kind=kind,
                text=text,
                claim_ids=tuple(claim_ids),
                source_ids=sources(claim_ids),
                teaching_aid=aid,
                search_text=f"{lesson.title} {label or ''}. {text}",
            )
        )

    for cid, claim in claims.items():
        add(f"claim/{cid}", stage_of.get(cid), "claim", claim.text, (cid,))
    for comp in lesson.components:
        if comp.breaks_if_removed:
            add(
                f"{comp.id}/breaks",
                comp.id,
                "breaks",
                f"If the {comp.label} is removed: {comp.breaks_if_removed}",
                comp.claims,
            )
        e = comp.explain
        if not e:
            continue
        add(f"{comp.id}/what", comp.id, "what", f"{comp.label}: {e.what}", e.claims)
        add(f"{comp.id}/why", comp.id, "why", f"Why {comp.label} is needed: {e.why}", e.claims)
        add(
            f"{comp.id}/analogy",
            comp.id,
            "analogy",
            f"Analogy for {comp.label}: {e.analogy}",
            e.claims,
            aid=True,
        )
        add(
            f"{comp.id}/happens",
            comp.id,
            "what",
            f"What happens in {comp.label}: " + " ".join(e.happens),
            e.claims,
        )
        add(
            f"{comp.id}/wrong",
            comp.id,
            "misconfigured",
            f"If {comp.label} is set up wrong: {e.misconfigured}",
            e.claims,
        )
        for k, (start, end) in enumerate(sentence_spans(e.learn_more)):
            add(f"{comp.id}/more/{k}", comp.id, "learn_more", e.learn_more[start:end], e.claims)
    for k, step in enumerate(lesson.tour):
        add(f"tour/{k}", step.component, "tour", f"{step.title}. {step.body}", step.claims)
    for ch in lesson.challenges:
        add(f"challenge/{ch.id}", None, "challenge", f"{ch.title}: {ch.explanation}", ch.claims)
    for k, obj in enumerate(lesson.objectives):
        add(f"objective/{k}", None, "objective", obj)
    return out


def build_passages(lessons: dict[str, Lesson], registry: SourceRegistry | None = None) -> list[Passage]:
    return [p for lesson in lessons.values() for p in _lesson_passages(lesson)]
