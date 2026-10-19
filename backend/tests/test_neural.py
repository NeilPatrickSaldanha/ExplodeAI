"""Pass 3 evidence that needs a real neural embedding model (local, free).

Skipped unless the optional extra is installed: `uv sync --extra neural`.
The first run downloads BAAI/bge-small-en-v1.5 from Hugging Face (~130 MB).
"""

import numpy as np
import pytest

from app.experiments.rag import pipeline
from tests.conftest import validates

pytest.importorskip("fastembed")


@pytest.fixture(scope="module")
def embedder():
    from app.experiments.rag.embedding import FastEmbedEmbedder

    return FastEmbedEmbedder()


@validates("embedding-definition", "lexical-misses-synonyms")
def test_neural_embedding_places_a_paraphrase_closer_than_unrelated_text(embedder):
    q, refund, sizing = embedder.embed([
        "Can I get my money back?",
        "Refunds go to the original payment method within 5 business days.",
        "Riders between 160 and 170 cm usually fit a size S.",
    ])
    assert np.allclose(np.linalg.norm([q, refund, sizing], axis=1), 1.0)
    assert q @ refund > q @ sizing + 0.1


@validates("lexical-misses-synonyms", "embedding-definition")
def test_neural_retrieval_finds_refunds_where_lexical_fails():
    query = "Can I get my money back?"
    lexical = pipeline.run(pipeline.RagParams(query=query, top_k=1, embedder="lexical-hashing"))
    neural = pipeline.run(pipeline.RagParams(query=query, top_k=1, embedder="neural-local"))
    texts = {c["id"]: c["text"] for c in neural["chunks"]}
    assert "Refunds" in texts[neural["retrieved"][0]["chunk_id"]]
    lex_texts = {c["id"]: c["text"] for c in lexical["chunks"]}
    assert "Refunds" not in lex_texts[lexical["retrieved"][0]["chunk_id"]]
