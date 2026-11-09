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


Voice = str  # "technical" (the standard names) or "plain" (everyday words first, plain.yaml laid over)


def read_lesson_data(path: Path, voice: Voice = "technical") -> dict:
    """A lesson's raw data: lesson.yaml, with each stage's explain.yaml entry merged in.

    The plain voice then lays plain.yaml over the text: the same lesson, the same verified claims, told in
    everyday words with the standard names kept beside them as "technical names"."""
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
    plain_path = path.with_name("plain.yaml")
    if voice == "plain" and plain_path.exists():
        _apply_plain(data, _read_yaml(plain_path))
    return data


def _apply_plain(data: dict, plain: dict) -> None:
    """Replace technical wording with everyday wording. Keeps ids, numbers and claims untouched."""
    for key in ("title", "summary"):
        if key in plain:
            data[key] = plain[key]
    if "objectives" in plain:
        data["objectives"] = plain["objectives"]
    data["ui"] = {**data.get("ui", {}), **plain.get("ui", {})}
    renamed: dict[str, str] = {}
    for comp in data["components"]:
        over = plain.get("components", {}).get(comp["id"])
        if not over:
            continue
        explain_over = over.get("explain", {})
        if "label" in over and over["label"] != comp["label"]:
            renamed[comp["label"]] = over["label"]
            comp["technical_name"] = comp["label"]
        for field, value in over.items():
            if field != "explain":
                comp[field] = value
        if explain_over and comp.get("explain") is not None:
            comp["explain"].update(explain_over)
    big = data.get("big_picture")
    if big and "big_picture" in plain:
        over = plain["big_picture"]
        for key in ("story",):
            if key in over:
                big[key] = over[key]
        big["analogy"].update(over.get("analogy", {}))
        big["example"].update(over.get("example", {}))
    if big:
        for item in big["analogy"]["mapping"]:
            item["part"] = renamed.get(item["part"], item["part"])
    for conn in data["connections"]:
        over = plain.get("connections", {}).get(f"{conn['source']}->{conn['target']}")
        if over:
            conn.update(over)
    for visual in data["visuals"]:
        if visual["id"] in plain.get("visuals", {}):
            visual.update(plain["visuals"][visual["id"]])
    experiment = plain.get("experiment", {})
    for field in ("corpus_note", "labels"):
        if field in experiment:
            data["experiment"][field] = experiment[field]
    for preset in data["experiment"].get("presets", []):
        over = experiment.get("presets", {}).get(preset.get("label"))
        if over:
            preset.update(over)
    if "guide" in experiment:
        data["experiment"]["guide"] = experiment["guide"]
    for ch in data["challenges"]:
        if ch["id"] in plain.get("challenges", {}):
            ch.update(plain["challenges"][ch["id"]])
    for step in data["tour"]:
        over = plain.get("tour", {}).get(step["component"])
        if over:
            step.update(over)
    if "reconstruction" in plain:
        data["reconstruction"].update(plain["reconstruction"])


def _merge_teaching(data: dict, teaching: dict) -> None:
    """Add the teaching layer: the big picture, each hand-off's explanation, each stage's story."""
    if "big_picture" in teaching:
        data["big_picture"] = teaching["big_picture"]
    if "experiment" in teaching:
        data["experiment"]["guide"] = teaching["experiment"]
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


def load_lessons(content_dir: Path, voice: Voice = "technical") -> dict[str, Lesson]:
    paths = (content_dir / "lessons").glob("*/lesson.yaml")
    loaded = [Lesson.model_validate(read_lesson_data(p, voice)) for p in paths]
    return {lesson.id: lesson for lesson in sorted(loaded, key=lambda lesson: lesson.number)}


@lru_cache
def content(voice: Voice = "technical") -> tuple[SourceRegistry, dict[str, Lesson]]:
    d = get_settings().content_dir
    return load_registry(d), load_lessons(d, voice)
