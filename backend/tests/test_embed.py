"""Embeddings experiment: stage mechanics. Needs the neural extra (local, free)."""

import numpy as np
import pytest

pytest.importorskip("fastembed")

from app.experiments.embed import model as bge  # noqa: E402
from app.experiments.embed.corpus import CATEGORIES, SAMPLE_LIBRARY  # noqa: E402
from app.experiments.embed.pipeline import STAGES, EmbedParams, run, score  # noqa: E402
from tests.conftest import validates  # noqa: E402

TEXTS = ["A puppy playing fetch", "The oak table seats eight people."]


@pytest.fixture(scope="module")
def enc():
    return bge.get_encoder()


@validates("bge-cls-normalized")
def test_hand_built_stages_reproduce_fastembed(enc):
    """Tokenize → transformer → [CLS] → L2-normalize equals the library's own output."""
    e = enc.encode(TEXTS)
    mine = np.array([bge.l2_normalize(bge.pool(h, "cls")) for h in e.hidden])
    ref = bge.l2_normalize(enc.reference(TEXTS))
    assert np.allclose((mine * ref).sum(axis=1), 1.0, atol=1e-5)


@validates("bge-dims")
def test_vectors_are_384_dimensional(enc):
    e = enc.encode(TEXTS)
    assert enc.dim == 384 and all(h.shape[1] == 384 for h in e.hidden)


@validates("bert-cls-token", "wordpiece-subwords")
def test_tokens_are_wordpieces_wrapped_in_cls_and_sep(enc):
    e = enc.encode(["Embeddings are unbelievably useful"])
    toks = e.tokens[0]
    assert toks[0] == "[CLS]" and toks[-1] == "[SEP]"
    assert any(t.startswith("##") for t in toks), toks  # a rare word split into sub-word pieces


@validates("bge-max-tokens")
def test_long_text_is_truncated_to_512_tokens(enc):
    e = enc.encode(["word " * 900])
    assert len(e.ids[0]) == 512 and e.truncated[0] and e.tokens[0][-1] == "[SEP]"


@validates("contextual-vectors")
def test_the_same_word_gets_different_vectors_in_different_contexts(enc):
    a = enc.encode(["I sat on the river bank."])
    b = enc.encode(["I paid money into the bank."])
    va = a.hidden[0][a.tokens[0].index("bank")]
    vb = b.hidden[0][b.tokens[0].index("bank")]
    assert float(bge.l2_normalize(va) @ bge.l2_normalize(vb)) < 0.95


def test_raw_vectors_are_not_unit_length_until_normalized(enc):
    raw = bge.pool(enc.encode(TEXTS[:1]).hidden[0], "cls")
    assert np.linalg.norm(raw) > 2
    assert np.isclose(np.linalg.norm(bge.l2_normalize(raw)), 1.0)


@validates("unit-vector-metrics")
def test_cosine_dot_and_euclidean_agree_on_unit_vectors():
    rng = np.random.default_rng(3)
    lib = bge.l2_normalize(rng.normal(size=(30, 16)))
    q = bge.l2_normalize(rng.normal(size=16))
    cos, dot, euc = score(q, lib, "cosine"), score(q, lib, "dot"), score(q, lib, "euclidean")
    assert np.allclose(cos, dot)
    assert np.allclose(euc**2, 2 - 2 * cos)  # ||a-b||^2 = 2 - 2cos for unit vectors
    assert (np.argsort(-cos) == np.argsort(-euc)).all()


@validates("semantic-similarity", "lexical-vs-neural")
def test_neural_finds_meaning_without_shared_words_lexical_does_not():
    q = "a place to put my books"
    neural = run(EmbedParams(text=q))
    lexical = run(EmbedParams(text=q, library_embedder="lexical", query_embedder="lexical"))
    assert neural["neighbours"][0]["id"] == "furniture-3"  # the bookshelf
    assert lexical["neighbours"][0]["score"] == 0  # no shared words, nothing to match on


@validates("models-not-comparable")
def test_vectors_from_different_models_cannot_be_compared():
    out = run(EmbedParams(query_embedder="lexical"))
    assert not out["comparable"] and out["neighbours"] == []


@validates("bge-query-instruction")
def test_query_instruction_is_prepended_to_the_model_input():
    out = run(EmbedParams(text="getting to the office", query_instruction=True))
    assert out["query"]["model_input"].startswith(bge.QUERY_INSTRUCTION)
    assert out["query"]["tokens"][1]["text"] == "represent"


def test_run_reports_every_stage_and_a_bounded_projection():
    out = run(EmbedParams())
    assert out["stages"] == STAGES and set(out["timings_ms"]) == set(STAGES)
    pts = np.array([i["point"] for i in out["library"]["items"]] + [out["query"]["point"]])
    assert np.abs(pts).max() <= 1 + 1e-9 and 0 < out["projection"]["explained_variance"] <= 1
    assert set(out["votes"]) == set(CATEGORIES) and len(out["library"]["items"]) == len(SAMPLE_LIBRARY)


@validates("scores-uncalibrated")
def test_unrelated_sentences_still_score_well_above_zero(enc):
    """Anisotropy: cross-topic cosine sits far above the ~0 of random directions."""
    e = enc.encode([it.text for it in SAMPLE_LIBRARY])
    v = np.array([bge.l2_normalize(bge.pool(h, "cls")) for h in e.hidden])
    cats = [it.category for it in SAMPLE_LIBRARY]
    sims = v @ v.T
    cross = [sims[i, j] for i in range(len(cats)) for j in range(i + 1, len(cats)) if cats[i] != cats[j]]
    rng = np.random.default_rng(0)
    r = bge.l2_normalize(rng.standard_normal((len(cats), v.shape[1])))
    rand = (r @ r.T)[np.triu_indices(len(cats), 1)]
    assert np.mean(cross) > 0.25 and min(cross) > 0.0
    assert abs(np.mean(rand)) < 0.05


@validates("projection-lossy")
def test_3d_projection_loses_information():
    out = run(EmbedParams())
    assert out["projection"]["explained_variance"] < 0.9
