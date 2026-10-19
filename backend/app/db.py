"""SQLite persistence via SQLModel.

Tables:
- LessonProgress: which components a learner explored, which challenges they solved.
- ExperimentRun: parameters + summary metrics of every real experiment execution.
- AIUsage: ledger of paid-provider requests, used to enforce rate limits and budgets.
"""

from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import JSON, Column
from sqlmodel import Field, Session, SQLModel, create_engine

from app.config import get_settings


def utcnow() -> datetime:
    return datetime.now(UTC)


class LessonProgress(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    learner_id: str = Field(index=True, max_length=64)
    lesson_id: str = Field(index=True, max_length=64)
    explored_components: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    solved_challenges: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    reconstruction_solved: bool = False
    updated_at: datetime = Field(default_factory=utcnow)


class ExperimentRun(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    learner_id: str = Field(index=True, max_length=64)
    experiment_id: str = Field(index=True, max_length=64)
    params: dict = Field(default_factory=dict, sa_column=Column(JSON))
    summary: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=utcnow)


class AIUsage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    learner_id: str = Field(index=True, max_length=64)
    provider: str = Field(max_length=32)
    model: str = Field(max_length=128)
    estimated_cost_usd: float
    status: str = Field(max_length=32)  # "ok" | "error" | "timeout"
    created_at: datetime = Field(default_factory=utcnow, index=True)


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = get_settings().database_url
        if url.startswith("sqlite:///"):
            Path(url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(url, connect_args={"check_same_thread": False})
    return _engine


def set_engine(engine) -> None:
    """Test hook: swap in an isolated engine."""
    global _engine
    _engine = engine


def init_db() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session
