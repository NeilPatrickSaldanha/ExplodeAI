"""Pass 3 evidence for each embeddings component's `breaks_if_removed` statement."""

import pytest

pytest.importorskip("fastembed")

from app.config import REPO_DIR  # noqa: E402
from app.content.loader import load_lessons  # noqa: E402
from app.experiments.embed.ablation import ablate  # noqa: E402
from app.experiments.embed.pipeline import STAGES, EmbedParams  # noqa: E402

P = EmbedParams(text="A puppy playing fetch in the park")


def test_baseline_finds_animals():
    out = ablate(P, None)
    assert out["top_category"] == "animals" and out["has_map"]


@pytest.mark.parametrize("stage", ["library", "your_text", "tokenizer", "encoder"])
def test_without_inputs_tokenizer_or_encoder_there_are_no_neighbours(stage):
    out = ablate(P, stage)
    assert out["neighbours"] == [] and out["library_vectors"] is None


def test_without_pooling_there_are_token_vectors_but_no_text_vector():
    out = ablate(P, "pooling")
    assert out["token_vectors"] and out["token_vectors"].endswith("× 384") and out["neighbours"] == []


def test_without_normalizer_dot_scores_are_unbounded():
    base = ablate(P.model_copy(update={"metric": "dot"}), None)
    out = ablate(P.model_copy(update={"metric": "dot"}), "normalizer")
    assert base["score_range"][1] <= 1.0 + 1e-6
    assert out["score_range"][1] > 1.0


def test_without_similarity_nothing_is_ranked():
    out = ablate(P, "similarity")
    assert [n["id"] for n in out["neighbours"]] == ["animals-1", "animals-2", "animals-3"]
    assert all(n["score"] is None for n in out["neighbours"])


def test_without_semantic_space_neighbours_are_unchanged():
    assert ablate(P, "semantic_space")["neighbours"] == ablate(P, None)["neighbours"]
    assert ablate(P, "semantic_space")["has_map"] is False


def test_unknown_stage_rejected():
    with pytest.raises(ValueError):
        ablate(P, "nope")


def test_every_component_has_a_breaks_statement():
    lessons = load_lessons(REPO_DIR / "content")
    if "embeddings" not in lessons:
        pytest.skip("lesson content not written yet")
    lesson = lessons["embeddings"]
    assert [c.id for c in lesson.components] == STAGES
    assert all(c.breaks_if_removed for c in lesson.components)


def test_ablate_endpoint(client):
    r = client.post("/api/experiments/embed/ablate", json={"text": P.text, "stage": "pooling"})
    assert r.status_code == 200 and r.json()["ablated"]["neighbours"] == []


CHECK = "/api/experiments/embed/challenges/embeddings/{}/check"
LEARNER_H = {"X-Learner-Id": "test-learner-0001"}


def _check(client, cid, **params):
    return client.post(CHECK.format(cid), json=params, headers=LEARNER_H)


def test_challenges_fail_when_broken_and_pass_when_fixed(client, monkeypatch):
    """Each challenge starts broken and has a real fix, so none can be passed by accident."""
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "show_draft_lessons", True)
    broken = {"synonym-blind": {"library_embedder": "lexical", "query_embedder": "lexical"},
              "mixed-models": {"library_embedder": "neural", "query_embedder": "lexical"},
              "short-query": {"query_instruction": False}}
    fixed = {"synonym-blind": {"library_embedder": "neural", "query_embedder": "neural"},
             "mixed-models": {"library_embedder": "neural", "query_embedder": "neural"},
             "short-query": {"query_instruction": True}}
    for cid in broken:
        assert _check(client, cid, **broken[cid]).json()["passed"] is False, cid
        assert _check(client, cid, **fixed[cid]).json()["passed"] is True, cid
