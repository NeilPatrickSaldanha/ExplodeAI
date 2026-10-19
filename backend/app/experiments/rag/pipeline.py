"""End-to-end RAG experiment: every stage runs for real and is timed.

The stage ids below are the contract between this code, the lesson content
(`content/lessons/rag-pipeline/lesson.yaml` components), and the 3D view. A
test asserts the three stay in sync.
"""

import time
from dataclasses import asdict
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.experiments.rag.chunking import chunk_corpus
from app.experiments.rag.corpus import SAMPLE_CORPUS_ID, SAMPLE_CORPUS_NOTE, get_corpus
from app.experiments.rag.embedding import make_embedder
from app.experiments.rag.generation import NO_ANSWER, assemble_prompt, extractive_answer
from app.experiments.rag.projection import pca_3d
from app.experiments.rag.retrieval import BM25, dense_scores, rank, rrf

# Stage id -> stages it depends on. Ingestion runs before any query; the query
# path needs both the index and the query embedding before retrieval.
STAGE_DEPENDENCIES: dict[str, list[str]] = {
    "corpus": [],
    "chunker": ["corpus"],
    "embedder": ["chunker"],
    "vector_index": ["embedder"],
    "query_encoder": [],
    "retriever": ["vector_index", "query_encoder"],
    "prompt_builder": ["retriever"],
    "generator": ["prompt_builder"],
}
STAGES = list(STAGE_DEPENDENCIES)


class RagParams(BaseModel):
    corpus_id: str = SAMPLE_CORPUS_ID
    query: str = Field("How long do I have to return a bike?", min_length=3, max_length=300)
    strategy: Literal["fixed", "sentence"] = "sentence"
    chunk_size: int = Field(40, ge=4, le=200)
    overlap: int = Field(0, ge=0, le=100)
    embedder: Literal["lexical-hashing", "neural-local"] = "lexical-hashing"
    method: Literal["dense", "bm25", "hybrid"] = "dense"
    top_k: int = Field(3, ge=1, le=10)
    context_budget_words: int = Field(200, ge=10, le=1000)

    @model_validator(mode="after")
    def _overlap_below_size(self):
        if self.overlap >= self.chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        return self


def _ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


def run(params: RagParams) -> dict:
    timings: dict[str, float] = {}

    t = time.perf_counter()
    docs = get_corpus(params.corpus_id)
    timings["corpus"] = _ms(t)

    t = time.perf_counter()
    chunks = chunk_corpus(docs, params.strategy, params.chunk_size, params.overlap)
    timings["chunker"] = _ms(t)

    t = time.perf_counter()
    embedder = make_embedder(params.embedder)
    texts = [c.text for c in chunks]
    embedder.fit(texts)
    vecs = embedder.embed(texts)
    timings["embedder"] = _ms(t)

    t = time.perf_counter()
    index = vecs  # exact (flat) index: the matrix itself
    bm25 = BM25(texts) if params.method in ("bm25", "hybrid") else None
    timings["vector_index"] = _ms(t)

    t = time.perf_counter()
    qvec = embedder.embed([params.query])[0]
    timings["query_encoder"] = _ms(t)

    t = time.perf_counter()
    dense = rank(dense_scores(index, qvec))
    lexical = rank(bm25.scores(params.query)) if bm25 else None
    if params.method == "dense":
        final = dense
    elif params.method == "bm25":
        final = lexical
    else:
        final = rank(rrf([dense, lexical], len(chunks)))
    top = final[: params.top_k]
    timings["retriever"] = _ms(t)

    t = time.perf_counter()
    ranked_chunks = [chunks[h.index] for h in top]
    prompt = assemble_prompt(params.query, ranked_chunks, params.context_budget_words)
    timings["prompt_builder"] = _ms(t)

    t = time.perf_counter()
    in_context = [c for c in ranked_chunks if c.id in prompt.included]
    sentences = extractive_answer(params.query, in_context)
    timings["generator"] = _ms(t)

    dense_rank = {h.index: h for h in dense}
    lexical_rank = {h.index: h for h in lexical} if lexical else {}
    projection = pca_3d(vecs, qvec)

    return {
        "params": params.model_dump(),
        "corpus": {
            "id": params.corpus_id,
            "note": SAMPLE_CORPUS_NOTE,
            "documents": [asdict(d) for d in docs],
        },
        "chunks": [
            {
                **asdict(c),
                "words": c.words,
                "point": projection.chunk_points[i],
                "dense_score": round(dense_rank[i].score, 4),
                "dense_rank": dense_rank[i].rank,
                "bm25_score": round(lexical_rank[i].score, 4) if lexical else None,
                "bm25_rank": lexical_rank[i].rank if lexical else None,
            }
            for i, c in enumerate(chunks)
        ],
        "embedding": {"name": embedder.name, "kind": embedder.kind, "dim": embedder.dim},
        "query": {"text": params.query, "point": projection.query_point},
        "projection": {"method": "pca", "explained_variance": projection.explained_variance},
        "retrieved": [
            {"chunk_id": chunks[h.index].id, "score": round(h.score, 6), "rank": h.rank}
            for h in top
        ],
        "prompt": {
            "text": prompt.text,
            "included": prompt.included,
            "dropped": prompt.dropped,
            "context_words": prompt.context_words,
            "budget_words": params.context_budget_words,
        },
        "answer": {
            "mode": "extractive-baseline",
            "is_llm": False,
            "sentences": [asdict(s) for s in sentences],
            "text": " ".join(f"{s.text} [{s.source}]" for s in sentences) or NO_ANSWER,
        },
        "timings_ms": timings,
        "stages": STAGES,
    }
