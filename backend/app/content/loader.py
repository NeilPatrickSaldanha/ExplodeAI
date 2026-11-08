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
    teaching_path = path.with_name("teaching.yaml")
    if teaching_path.exists():
        _merge_teaching(data, _read_yaml(teaching_path))
    return data


def _merge_teaching(data: dict, teaching: dict) -> None:
    """Add the teaching layer: the big picture, each hand-off's explanation, each stage's story."""
    if "big_picture" in teaching:
        data["big_picture"] = teaching["big_picture"]
    handoffs = teaching.get("connections", {})
    for conn in data["connections"]:
        text = handoffs.get(f"{conn['source']}->{conn['target']}")
        if text:
            conn["explain"] = text
    stages = teaching.get("stages", {})
    for comp in data["components"]:
        extra = stages.get(comp["id"])
        if extra and comp.get("explain") is not None:
            comp["explain"].update(extra)


def load_lessons(content_dir: Path) -> dict[str, Lesson]:
    paths = (content_dir / "lessons").glob("*/lesson.yaml")
    loaded = [Lesson.model_validate(read_lesson_data(p)) for p in paths]
    return {lesson.id: lesson for lesson in sorted(loaded, key=lambda lesson: lesson.number)}


@lru_cache
def content() -> tuple[SourceRegistry, dict[str, Lesson]]:
    d = get_settings().content_dir
    return load_registry(d), load_lessons(d)
