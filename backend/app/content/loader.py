"""Load lessons and the source registry from the repository's content/ folder."""

from functools import lru_cache
from pathlib import Path

import yaml

from app.config import get_settings
from app.content.schema import Lesson, SourceRegistry


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_registry(content_dir: Path) -> SourceRegistry:
    return SourceRegistry.model_validate(_read_yaml(content_dir / "sources.yaml"))


def read_lesson_data(path: Path) -> dict:
    """A lesson's raw data: lesson.yaml, with each stage's explain.yaml entry merged in."""
    data = _read_yaml(path)
    explain_path = path.with_name("explain.yaml")
    if explain_path.exists():
        explain = _read_yaml(explain_path)
        for comp in data["components"]:
            if comp["id"] in explain:
                comp["explain"] = explain[comp["id"]]
    return data


def load_lessons(content_dir: Path) -> dict[str, Lesson]:
    paths = (content_dir / "lessons").glob("*/lesson.yaml")
    loaded = [Lesson.model_validate(read_lesson_data(p)) for p in paths]
    return {lesson.id: lesson for lesson in sorted(loaded, key=lambda lesson: lesson.number)}


@lru_cache
def content() -> tuple[SourceRegistry, dict[str, Lesson]]:
    d = get_settings().content_dir
    return load_registry(d), load_lessons(d)
