"""Pass 3 evidence for every component's `breaks_if_removed` statement.

Each statement in content/lessons/rag-pipeline/lesson.yaml describes what the
executable pipeline does without that stage; these tests run it and check.
"""

import pytest

from app.config import REPO_DIR
from app.content.loader import load_lessons
from app.experiments.rag.ablation import ablate
from app.experiments.rag.pipeline import STAGES, RagParams

Q = RagParams(query="How should I store the battery long term?", top_k=3)
GOLD = "between 40 and 60 percent"


def test_baseline_answers_the_question():
    out = ablate(Q, None)
    assert out["answer"]["has_answer"] and GOLD in out["answer"]["text"]


def test_without_corpus_there_is_nothing_to_search():
    out = ablate(Q, "corpus")
    assert out["chunks"] == 0 and out["retrieved"] == [] and not out["answer"]["has_answer"]


def test_without_chunker_whole_documents_become_chunks():
    out = ablate(Q, "chunker")
    assert out["chunks"] == 6
    assert all(r["chunk_id"].endswith("#0") for r in out["retrieved"])
    # Whole documents are bigger, so the same budget fits fewer of them.
    assert out["prompt"]["context_words"] >= ablate(Q, None)["prompt"]["context_words"] or out["prompt"]["dropped"]


@pytest.mark.parametrize("stage", ["embedder", "query_encoder"])
def test_without_vectors_dense_fails_but_bm25_still_works(stage):
    assert ablate(Q, stage)["retrieved"] == []
    bm25 = ablate(Q.model_copy(update={"method": "bm25"}), stage)
    assert bm25["retrieved"] and GOLD in bm25["answer"]["text"]


def test_without_vector_index_nothing_is_retrieved_by_any_method():
    for method in ("dense", "bm25", "hybrid"):
        out = ablate(Q.model_copy(update={"method": method}), "vector_index")
        assert out["retrieved"] == [] and not out["answer"]["has_answer"]


def test_without_retriever_chunks_arrive_unranked_and_the_budget_drops_the_answer():
    tight = Q.model_copy(update={"context_budget_words": 60})
    out = ablate(tight, "retriever")
    assert out["retrieved"][0]["chunk_id"] == "returns#0"  # corpus order, not relevance
    assert out["prompt"]["dropped"]
    assert GOLD not in (out["answer"]["text"] or "")
    assert GOLD in ablate(tight, None)["answer"]["text"]


def test_without_prompt_builder_the_generator_sees_only_the_question():
    out = ablate(Q, "prompt_builder")
    assert out["prompt"]["included"] == [] and not out["answer"]["has_answer"]


def test_without_generator_no_answer_is_written():
    out = ablate(Q, "generator")
    assert out["prompt"]["included"] and out["answer"]["text"] is None


def test_unknown_stage_is_rejected():
    with pytest.raises(ValueError):
        ablate(Q, "nope")


def test_every_component_has_a_breaks_statement_and_an_ablation_test():
    lesson = load_lessons(REPO_DIR / "content")["rag-pipeline"]
    assert [c.id for c in lesson.components] == STAGES
    assert all(c.breaks_if_removed for c in lesson.components)


def test_ablate_endpoint(client):
    r = client.post("/api/experiments/rag/ablate", json={"query": Q.query, "stage": "retriever",
                                                         "context_budget_words": 60})
    assert r.status_code == 200
    body = r.json()
    assert body["baseline"]["answer"]["has_answer"] and body["ablated"]["removed"] == "retriever"
    assert client.post("/api/experiments/rag/ablate", json={"stage": "nope"}).status_code == 422
