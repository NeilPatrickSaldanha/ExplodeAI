"""Pass 3 evidence for each tokenization component's `breaks_if_removed` statement."""

import pytest

from app.config import REPO_DIR
from app.content.loader import load_lessons
from app.experiments.tokenize.ablation import ablate
from app.experiments.tokenize.pipeline import STAGES, TokenizeParams

P = TokenizeParams(text="The keeper lit the lantern at dusk.", merges=100)


def test_baseline_round_trips():
    out = ablate(P, None)
    assert out["round_trip"] and out["tokens"] and out["merges"] == 100


def test_without_corpus_no_merges_and_one_token_per_byte():
    out = ablate(P, "corpus")
    assert out["merges"] == 0
    assert out["tokens"] == len(P.text.encode()) and out["round_trip"]
    chars = ablate(P.model_copy(update={"base": "chars"}), "corpus")
    assert chars["unk_count"] == chars["tokens"] and not chars["round_trip"]


def test_without_pre_tokenizer_merges_cross_words():
    assert ablate(P, None)["crossing_word_boundary"] == 0
    assert ablate(P, "pre_tokenizer")["crossing_word_boundary"] > 0


def test_without_base_alphabet_everything_is_unknown():
    out = ablate(P, "base_alphabet")
    assert out["unk_count"] == out["tokens"] > 0 and not out["round_trip"]


def test_without_merge_learner_sequence_is_longest():
    base = ablate(P, None)
    out = ablate(P, "merge_learner")
    assert out["merges"] == 0 and out["tokens"] > base["tokens"] and out["round_trip"]


@pytest.mark.parametrize("stage", ["vocabulary", "encoder"])
def test_without_vocabulary_or_encoder_no_ids(stage):
    out = ablate(P, stage)
    assert out["tokens"] is None and out["decoded"] == "" and not out["round_trip"]


def test_without_input_nothing_is_encoded():
    out = ablate(P, "input_text")
    assert out["tokens"] == 0 and not out["round_trip"]


def test_without_decoder_ids_but_no_text():
    out = ablate(P, "decoder")
    assert out["tokens"] and out["decoded"] is None and not out["round_trip"]


def test_unknown_stage_rejected():
    with pytest.raises(ValueError):
        ablate(P, "nope")


def test_every_component_has_a_breaks_statement():
    lesson = load_lessons(REPO_DIR / "content")["tokenization"]
    assert [c.id for c in lesson.components] == STAGES
    assert all(c.breaks_if_removed for c in lesson.components)


def test_ablate_endpoint(client):
    r = client.post("/api/experiments/tokenize/ablate", json={"text": P.text, "stage": "merge_learner"})
    assert r.status_code == 200 and r.json()["ablated"]["merges"] == 0
    assert client.post("/api/experiments/tokenize/ablate", json={"stage": "nope"}).status_code == 422
