from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import get_settings
from app.content.loader import content
from app.content.schema import Lesson, validate_lesson

router = APIRouter(prefix="/api/lessons", tags=["lessons"])


def _visible(lesson: Lesson) -> bool:
    return lesson.status == "published" or get_settings().show_draft_lessons


def get_lesson_or_404(lesson_id: str) -> Lesson:
    _, lessons = content()
    lesson = lessons.get(lesson_id)
    if lesson is None or not _visible(lesson):
        raise HTTPException(404, "lesson not found")
    return lesson


@router.get("")
def list_lessons():
    _, lessons = content()
    return [
        {
            "id": lesson.id,
            "title": lesson.title,
            "summary": lesson.summary,
            "status": lesson.status,
            "estimated_minutes": lesson.estimated_minutes,
            "component_count": len(lesson.components),
        }
        for lesson in lessons.values()
        if _visible(lesson)
    ]


@router.get("/{lesson_id}")
def get_lesson(lesson_id: str):
    lesson = get_lesson_or_404(lesson_id)
    registry, _ = content()
    by_id = registry.by_id()
    cited = sorted({c.source for claim in lesson.claims for c in claim.citations})
    return {
        **lesson.model_dump(mode="json"),
        "sources": [by_id[s].model_dump(mode="json") for s in cited if s in by_id],
        "validation_problems": validate_lesson(lesson, registry),
    }


class ReconstructionAttempt(BaseModel):
    order: list[str]


def check_order(order: list[str], deps: dict[str, list[str]]) -> dict:
    """An order is correct iff it is a topological order of the stage dependency graph.

    Several orders are valid (e.g. the query can be embedded before or after
    the corpus is indexed); only dependency violations are mistakes.
    """
    if sorted(order) != sorted(deps):
        return {"correct": False, "violations": [], "message": "Place every stage exactly once."}
    position = {stage: i for i, stage in enumerate(order)}
    violations = [
        {"stage": stage, "needs": need}
        for stage, needs in deps.items()
        for need in needs
        if position[need] > position[stage]
    ]
    return {
        "correct": not violations,
        "violations": violations,
        "message": "Every stage runs after what it depends on." if not violations
        else f"{len(violations)} stage(s) run before something they need.",
    }


@router.post("/{lesson_id}/reconstruction/check")
def check_reconstruction(lesson_id: str, attempt: ReconstructionAttempt):
    lesson = get_lesson_or_404(lesson_id)
    return check_order(attempt.order, lesson.reconstruction.dependencies)
