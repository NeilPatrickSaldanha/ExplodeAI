from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.db import LessonProgress, get_session, utcnow
from app.deps import learner_id
from app.routers.lessons import get_lesson_or_404

router = APIRouter(prefix="/api/progress", tags=["progress"])


class ProgressUpdate(BaseModel):
    explored_components: list[str] = Field(default_factory=list)
    solved_challenges: list[str] = Field(default_factory=list)
    reconstruction_solved: bool = False


def _get(session: Session, learner: str, lesson_id: str) -> LessonProgress | None:
    return session.exec(
        select(LessonProgress).where(
            LessonProgress.learner_id == learner, LessonProgress.lesson_id == lesson_id
        )
    ).first()


def _out(p: LessonProgress | None, lesson_id: str) -> dict:
    if p is None:
        return {"lesson_id": lesson_id, "explored_components": [], "solved_challenges": [],
                "reconstruction_solved": False}
    return {"lesson_id": lesson_id, "explored_components": p.explored_components,
            "solved_challenges": p.solved_challenges,
            "reconstruction_solved": p.reconstruction_solved}


@router.get("/{lesson_id}")
def get_progress(lesson_id: str, learner: str = Depends(learner_id),
                 session: Session = Depends(get_session)):
    get_lesson_or_404(lesson_id)
    return _out(_get(session, learner, lesson_id), lesson_id)


@router.put("/{lesson_id}")
def merge_progress(lesson_id: str, update: ProgressUpdate, learner: str = Depends(learner_id),
                   session: Session = Depends(get_session)):
    """Merge (never erase) progress, keeping only ids that exist in the lesson."""
    lesson = get_lesson_or_404(lesson_id)
    valid_components = {c.id for c in lesson.components}
    valid_challenges = {c.id for c in lesson.challenges}
    p = _get(session, learner, lesson_id) or LessonProgress(learner_id=learner, lesson_id=lesson_id)
    p.explored_components = sorted(
        (set(p.explored_components) | set(update.explored_components)) & valid_components
    )
    p.solved_challenges = sorted(
        (set(p.solved_challenges) | set(update.solved_challenges)) & valid_challenges
    )
    p.reconstruction_solved = p.reconstruction_solved or update.reconstruction_solved
    p.updated_at = utcnow()
    session.add(p)
    session.commit()
    session.refresh(p)
    return _out(p, lesson_id)
