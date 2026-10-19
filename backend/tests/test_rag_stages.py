"""Unit tests for each RAG stage, including Pass 3 evidence for lesson claims."""

import math

import numpy as np
import pytest

from app.experiments.rag.chunking import chunk_fixed, chunk_sentences
from app.experiments.rag.corpus import SAMPLE_CORPUS, Document
from app.experiments.rag.embedding import HashingEmbedder
from app.experiments.rag.generation import NO_ANSWER, assemble_prompt, extractive_answer
from app.experiments.rag.projection import pca_3d
from app.experiments.rag.retrieval import BM25, dense_scores, rank, rrf
from app.experiments.rag.text import s_stem, terms
from tests.conftest import validates

DOC = Document("d", "t", "one two three four five six seven eight nine ten")


# ------------------------------------------------------------------ chunking
def test_fixed_chunks_cover_document_and_respect_size():
    chunks = chunk_fixed(DOC, size=4, overlap=0)
    assert [c.text for c in chunks] == ["one two three four", "five six seven eight", "nine ten"]
    assert all(DOC.text[c.start : c.end] == c.text for c in chunks)


def test_fixed_overlap_repeats_trailing_words():
    chunks = chunk_fixed(DOC, size=4, overlap=2)
    assert chunks[0].text.split()[-2:] == chunks[1].text.split()[:2]


@validates("chunking-overlap", "chunking-affects-retrieval")
def test_overlap_keeps_a_boundary_fact_intact():
    fact = "within 30 days of delivery"
    doc = next(d for d in SAMPLE_CORPUS if d.id == "returns")
    no_overlap = chunk_fixed(doc, size=8, overlap=0)
    with_overlap = chunk_fixed(doc, size=8, overlap=4)
    assert fact in doc.text
    assert not any(fact in c.text for c in no_overlap), "fact should be split at overlap 0"
    assert any(fact in c.text for c in with_overlap), "overlap should keep it whole"


@pytest.mark.parametrize("size,overlap", [(0, 0), (4, 4), (4, -1)])
def test_invalid_chunk_params_raise(size, overlap):
    with pytest.raises(ValueError):
        chunk_fixed(DOC, size, overlap)


def test_sentence_chunks_never_cut_mid_sentence():
    for doc in SAMPLE_CORPUS:
        for c in chunk_sentences(doc, size=20, overlap=0):
            assert c.text.rstrip().endswith((".", "!", "?", "C")), c.text  # "0 °C." ends a doc


def test_sentence_overlap_carries_previous_sentence():
    doc = Document("d", "t", "Alpha beta. Gamma delta. Epsilon zeta.")
    chunks = chunk_sentences(doc, size=4, overlap=2)
    assert chunks[0].text == "Alpha beta. Gamma delta."
    assert chunks[1].text.startswith("Gamma delta.")


def test_s_stemmer_only_strips_plurals():
    assert [s_stem(w) for w in ["bikes", "batteries", "boxes", "glass", "status", "gas"]] == [
        "bike", "battery", "boxe", "glass", "status", "gas"]
    assert terms("The Bikes are returned") == ["bike", "returned"]


# ---------------------------------------------------------------- embedding
def test_hashing_embedder_is_unit_length_and_deterministic():
    emb = HashingEmbedder()
    texts = [d.text for d in SAMPLE_CORPUS]
    emb.fit(texts)
    a, b = emb.embed(texts), emb.embed(texts)
    assert np.allclose(np.linalg.norm(a, axis=1), 1.0)
    assert np.array_equal(a, b)


def test_lexical_embedder_ranks_word_sharing_text_first():
    emb = HashingEmbedder()
    texts = [d.text for d in SAMPLE_CORPUS]
    emb.fit(texts)
    vecs = emb.embed(texts)
    q = emb.embed(["battery charge storage"])[0]
    scores = dict(zip([d.id for d in SAMPLE_CORPUS], dense_scores(vecs, q), strict=True))
    assert max(scores, key=scores.get) == "battery"
    assert scores["battery"] > scores["sizing"]


@validates("cosine-dot-normalized")
def test_dot_product_equals_cosine_for_unit_vectors():
    rng = np.random.default_rng(0)
    x, y = rng.normal(size=(50, 64)), rng.normal(size=(50, 64))
    cosine = (x * y).sum(1) / (np.linalg.norm(x, axis=1) * np.linalg.norm(y, axis=1))
    xn = x / np.linalg.norm(x, axis=1, keepdims=True)
    yn = y / np.linalg.norm(y, axis=1, keepdims=True)
    assert np.allclose((xn * yn).sum(1), cosine)
    # ...and without normalisation the two differ, so the step matters.
    assert not np.allclose((x * y).sum(1), cosine)


@validates("bi-encoder")
def test_chunk_vectors_do_not_depend_on_the_query():
    emb = HashingEmbedder()
    texts = [d.text for d in SAMPLE_CORPUS]
    emb.fit(texts)
    before = emb.embed(texts)
    emb.embed(["a completely different question about frames"])
    assert np.array_equal(before, emb.embed(texts))


# ---------------------------------------------------------------- retrieval
@validates("flat-index-exact")
def test_flat_index_matches_brute_force_ordering():
    rng = np.random.default_rng(1)
    vecs = rng.normal(size=(200, 32))
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    q = vecs[17] + 0.01 * rng.normal(size=32)
    hits = rank(dense_scores(vecs, q))
    brute = sorted(range(200), key=lambda i: -float(vecs[i] @ q))
    assert [h.index for h in hits] == brute
    assert hits[0].index == 17


@validates("bm25-mechanics")
def test_bm25_term_frequency_saturates():
    docs = ["bike " * n + "filler words here" for n in (1, 2, 5, 50, 500)]
    bm = BM25(docs)
    s = bm.scores("bike")
    assert all(a < b for a, b in zip(s, s[1:], strict=False)), "more matches still help..."
    bound = bm.idf["bike"] * (bm.k1 + 1)
    assert s.max() < bound, "...but never past idf·(k1+1)"


@validates("bm25-mechanics")
def test_bm25_b_zero_ignores_document_length():
    docs = ["bike", "bike " + "padding " * 40]
    s0 = BM25(docs, b=0.0).scores("bike")
    s1 = BM25(docs, b=0.75).scores("bike")
    assert math.isclose(s0[0], s0[1])
    assert s1[0] > s1[1]


@validates("bm25-defaults")
def test_bm25_uses_elasticsearch_defaults():
    bm = BM25(["x"])
    assert (bm.k1, bm.b) == (1.2, 0.75)


@validates("lexical-misses-synonyms")
def test_lexical_retrieval_misses_a_synonym_only_query():
    texts = [d.text for d in SAMPLE_CORPUS]
    returns = [d.id for d in SAMPLE_CORPUS].index("returns")
    # "money back" means refund, but shares no terms with the returns article.
    assert BM25(texts).scores("money back")[returns] == 0
    emb = HashingEmbedder()
    emb.fit(texts)
    q = emb.embed(["money back"])[0]
    assert float(emb.embed(texts)[returns] @ q) == pytest.approx(0, abs=0.05)


@validates("rrf")
def test_rrf_matches_formula_and_ignores_raw_scores():
    a = rank(np.array([0.9, 0.1, 0.5]))
    b = rank(np.array([3.0, 9.0, 1.0]))
    fused = rrf([a, b], 3, k=60)
    expected = [1 / 61 + 1 / 62, 1 / 63 + 1 / 61, 1 / 62 + 1 / 63]
    assert np.allclose(fused, expected)
    # Rescaling one ranker's scores leaves its ranks — and the fusion — unchanged.
    b2 = rank(np.array([3000.0, 9000.0, 1000.0]))
    assert np.allclose(rrf([a, b2], 3, k=60), fused)


# --------------------------------------------------------------- generation
def _chunks(*texts):
    from app.experiments.rag.chunking import Chunk

    return [Chunk(f"c#{i}", "c", i, t, 0, len(t)) for i, t in enumerate(texts)]


@validates("prompt-docs-first")
def test_prompt_puts_documents_first_and_question_last():
    p = assemble_prompt("What is x?", _chunks("x is one.", "y is two."), budget_words=100)
    assert p.text.startswith("<documents>")
    assert p.text.rstrip().endswith("Question: What is x?")
    assert p.text.index("<source>c#0</source>") < p.text.index("<document_content>x is one.")


def test_prompt_budget_drops_chunks_in_rank_order():
    p = assemble_prompt("q", _chunks("a b c d e", "f g h", "i j"), budget_words=7)
    assert p.included == ["c#0", "c#2"]
    assert p.dropped == ["c#1"]
    assert p.context_words == 7


def test_extractive_answer_cites_and_admits_ignorance():
    ans = extractive_answer("battery storage charge", _chunks("Keep the battery at half charge."))
    assert ans and ans[0].source == "c#0"
    assert extractive_answer("frame size", _chunks("Keep the battery cool.")) == []
    assert NO_ANSWER.startswith("The retrieved context does not contain")


def test_projection_is_bounded_and_reports_variance():
    rng = np.random.default_rng(2)
    vecs = rng.normal(size=(12, 40))
    proj = pca_3d(vecs, vecs[0])
    pts = np.array(proj.chunk_points + [proj.query_point])
    assert pts.shape == (13, 3)
    assert np.abs(pts).max() <= 1.0 + 1e-9
    assert 0 < proj.explained_variance <= 1
