"""Integration of pipeline, lesson content, and the 3D model description."""

import copy

import pytest
import yaml

from app.config import REPO_DIR
from app.content.loader import load_lessons, load_registry
from app.content.schema import Lesson, validate_lesson
from app.experiments.rag import pipeline
from app.experiments.rag.corpus import SAMPLE_CORPUS
from app.routers.experiments import evaluate_challenge
from app.routers.lessons import check_order
from tests.conftest import validates

CONTENT = REPO_DIR / "content"


@pytest.fixture(scope="module")
def lesson() -> Lesson:
    return load_lessons(CONTENT)["rag-pipeline"]


@pytest.fixture(scope="module")
def registry():
    return load_registry(CONTENT)


@pytest.fixture(scope="module")
def lessons() -> dict[str, Lesson]:
    return load_lessons(CONTENT)


def test_lesson_content_is_valid(lesson, registry):
    assert validate_lesson(lesson, registry) == []


def test_lesson_components_match_pipeline_stages(lesson):
    """The 3D model, the reconstruction graph, and the executed pipeline agree."""
    assert [c.id for c in lesson.components] == pipeline.STAGES
    assert lesson.reconstruction.dependencies == pipeline.STAGE_DEPENDENCIES


def test_diagram_edges_are_the_pipeline_dependencies(lesson):
    edges = {(c.source, c.target) for c in lesson.connections}
    deps = {(need, stage) for stage, needs in pipeline.STAGE_DEPENDENCIES.items() for need in needs}
    assert edges == deps


def test_every_visual_declares_its_kind(lesson):
    kinds = {v.id: v.kind for v in lesson.visuals}
    assert kinds["experiment"] == "real_execution"
    assert kinds["exploded-view"] == "conceptual"
    assert "not an LLM" in next(v.label for v in lesson.visuals if v.id == "answer")


def test_run_reports_every_stage_with_timing():
    result = pipeline.run(pipeline.RagParams())
    assert result["stages"] == pipeline.STAGES
    assert set(result["timings_ms"]) == set(pipeline.STAGES)
    assert result["answer"]["is_llm"] is False
    assert len(result["retrieved"]) == 3


@pytest.mark.parametrize("method", ["dense", "bm25", "hybrid"])
def test_each_method_retrieves_the_battery_article(method):
    r = pipeline.run(pipeline.RagParams(query="How should I store the battery?", method=method))
    assert r["retrieved"][0]["chunk_id"].startswith("battery#")


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        pipeline.RagParams(chunk_size=10, overlap=10)


@validates("rag-swap-index")
def test_replacing_the_corpus_changes_the_answer_without_other_changes(monkeypatch):
    params = pipeline.RagParams(query="How long do I have to return a bike?")
    before = pipeline.run(params)["answer"]["text"]
    updated = copy.deepcopy(SAMPLE_CORPUS)
    idx = next(i for i, d in enumerate(updated) if d.id == "returns")
    updated[idx] = type(updated[idx])(
        "returns", "Returns", "Ridgeline Bikes accepts returns of unused bikes within 45 days."
    )
    monkeypatch.setattr(pipeline, "get_corpus", lambda _cid: updated)
    after = pipeline.run(params)["answer"]["text"]
    assert "30 days" in before and "45 days" in after


# --------------------------------------------------------------- challenges
KNOWN_FIXES = {
    "boundary-split": {"chunk_size": 20},
    "too-few-results": {"top_k": 3},
    "ranking-miss": {"method": "hybrid"},
    "budget-overflow": {"context_budget_words": 60},
}


@validates("chunking-affects-retrieval", "rrf", "bm25-mechanics")
@pytest.mark.parametrize("challenge_id", list(KNOWN_FIXES))
def test_challenge_fails_when_broken_and_passes_when_fixed(lesson, challenge_id):
    ch = next(c for c in lesson.challenges if c.id == challenge_id)
    broken = pipeline.run(pipeline.RagParams(**ch.broken_params))
    assert not evaluate_challenge(ch, broken)["passed"]
    fix = KNOWN_FIXES[challenge_id]
    assert not set(fix) & set(ch.locked_params), "the fix must use an unlocked control"
    fixed = pipeline.run(pipeline.RagParams(**{**ch.broken_params, **fix}))
    assert evaluate_challenge(ch, fixed)["passed"]


# ----------------------------------------------------------- reconstruction
def test_reconstruction_accepts_any_valid_topological_order(lesson):
    deps = lesson.reconstruction.dependencies
    assert check_order(pipeline.STAGES, deps)["correct"]
    query_first = ["query_encoder", "corpus", "chunker", "embedder", "vector_index",
                   "retriever", "prompt_builder", "generator"]
    assert check_order(query_first, deps)["correct"]


def test_reconstruction_reports_violations(lesson):
    deps = lesson.reconstruction.dependencies
    wrong = ["retriever", "corpus", "chunker", "embedder", "vector_index", "query_encoder",
             "prompt_builder", "generator"]
    out = check_order(wrong, deps)
    assert not out["correct"]
    assert {"stage": "retriever", "needs": "vector_index"} in out["violations"]
    assert check_order(["corpus"], deps)["correct"] is False


# ------------------------------------------------------- validator negatives
def _raw():
    with (CONTENT / "lessons" / "rag-pipeline" / "lesson.yaml").open() as fh:
        return yaml.safe_load(fh)


def test_validator_rejects_unknown_source(registry):
    raw = _raw()
    raw["claims"][0]["citations"][0]["source"] = "made-up-source"
    problems = validate_lesson(Lesson.model_validate(raw), registry)
    assert any("unknown source 'made-up-source'" in p for p in problems)


def test_validator_blocks_publishing_unverified_claims(registry):
    raw = _raw()
    raw["status"] = "published"
    raw["claims"][0]["verification"]["cross_check"] = {"status": "pending"}
    problems = validate_lesson(Lesson.model_validate(raw), registry)
    assert any("cross_check pass is 'pending' in a published lesson" in p for p in problems)


def test_validator_flags_failed_pass_even_in_draft(registry):
    raw = _raw()
    raw["claims"][0]["verification"]["cross_check"] = {
        "status": "failed", "date": "2026-10-18", "by": "x"}
    problems = validate_lesson(Lesson.model_validate(raw), registry)
    assert any("FAILED" in p for p in problems)


def test_claim_without_citation_is_rejected_by_schema():
    raw = _raw()
    raw["claims"][0]["citations"] = []
    with pytest.raises(ValueError):
        Lesson.model_validate(raw)


def test_long_excerpts_are_rejected():
    raw = _raw()
    raw["claims"][0]["citations"][0]["excerpt"] = "word " * 40
    with pytest.raises(ValueError):
        Lesson.model_validate(raw)


# -------------------------------------------------- stage explanations (explain.yaml)
def test_every_stage_of_every_lesson_has_an_explanation(lessons):
    for lesson in lessons.values():
        for comp in lesson.components:
            assert comp.explain is not None, f"{lesson.id}/{comp.id}"
            assert 1 <= len(comp.explain.happens) <= 5
            assert comp.explain.example.steps


def test_validator_flags_a_stage_without_an_explanation(registry, lessons):
    lesson = next(iter(lessons.values())).model_copy(deep=True)
    lesson.components[0].explain = None
    assert any("no explain section" in p for p in validate_lesson(lesson, registry))


def test_validator_flags_an_explanation_citing_a_claim_the_stage_does_not_own(registry, lessons):
    lesson = next(iter(lessons.values())).model_copy(deep=True)
    other = lesson.components[1].claims[0]
    lesson.components[0].explain.claims = [other]
    assert any("must be among the component's own claims" in p for p in validate_lesson(lesson, registry))
