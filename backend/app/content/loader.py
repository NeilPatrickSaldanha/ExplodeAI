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


def load_lessons(content_dir: Path) -> dict[str, Lesson]:
    loaded = [Lesson.model_validate(_read_yaml(p)) for p in (content_dir / "lessons").glob("*/lesson.yaml")]
    return {lesson.id: lesson for lesson in sorted(loaded, key=lambda lesson: lesson.number)}


@lru_cache
def content() -> tuple[SourceRegistry, dict[str, Lesson]]:
    d = get_settings().content_dir
    return load_registry(d), load_lessons(d)
