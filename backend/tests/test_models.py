"""Every 3D model a lesson names must exist as a file the frontend can serve."""

from pathlib import Path

from app.content.loader import content

MODELS = Path(__file__).resolve().parents[2] / "frontend" / "public" / "models"


def test_every_named_model_exists():
    _, lessons = content()
    named = [(lesson.id, c.id, c.geometry.model) for lesson in lessons.values() for c in lesson.components if c.geometry.model]
    assert named, "at least one lesson uses a 3D model"
    missing = [(lid, cid, m) for lid, cid, m in named if not (MODELS / f"{m}.glb").is_file()]
    assert not missing, f"model files missing: {missing}"
