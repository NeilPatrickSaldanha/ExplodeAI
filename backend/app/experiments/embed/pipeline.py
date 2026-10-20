"""End-to-end embeddings experiment: every stage runs for real and is timed.

The stage ids are the contract between this code, the lesson content
(`content/lessons/embeddings/lesson.yaml` components), and the 3D view.
"""

import time
from functools import lru_cache
from typing import Literal

import numpy as np
from pydantic import BaseModel, Field

from app.experiments.embed import model as bge
from app.experiments.embed.corpus import CATEGORIES, SAMPLE_LIBRARY_ID, SAMPLE_LIBRARY_NOTE, get_library
from app.experiments.rag.embedding import HashingEmbedder
from app.experiments.rag.projection import pca_3d
from app.experiments.rag.text import terms

STAGE_DEPENDENCIES: dict[str, list[str]] = {
    "library": [],
    "your_text": [],
    "tokenizer": ["library", "your_text"],
    "encoder": ["tokenizer"],
    "pooling": ["encoder"],
    "normalizer": ["pooling"],
    "similarity": ["normalizer"],
    "semantic_space": ["normalizer"],
}
STAGES = list(STAGE_DEPENDENCIES)

Embedder = Literal["neural", "lexical"]
TOKEN_PREVIEW_DIMS = 24
VECTOR_PREVIEW_DIMS = 48


class EmbedParams(BaseModel):
    library_id: str = SAMPLE_LIBRARY_ID
    text: str = Field("A puppy playing fetch in the park", min_length=1, max_length=4000)
    library_embedder: Embedder = "neural"
    query_embedder: Embedder = "neural"
    pooling: bge.Pooling = "cls"
    normalize: bool = True
    metric: Literal["cosine", "dot", "euclidean"] = "cosine"
    query_instruction: bool = False
    top_k: int = Field(5, ge=1, le=10)


def _ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


@lru_cache(maxsize=1)
def _lexical() -> HashingEmbedder:
    emb = HashingEmbedder()
    emb.fit([i.text for i in get_library()])
    return emb


@lru_cache(maxsize=8)
def _library_neural(library_id: str, pooling: str) -> tuple[np.ndarray, tuple[int, ...]]:
    """Raw (un-normalized) pooled vectors for the library, and each item's token count."""
    enc = bge.get_encoder().encode([i.text for i in get_library(library_id)])
    return np.array([bge.pool(h, pooling) for h in enc.hidden]), tuple(len(t) for t in enc.tokens)


def score(query: np.ndarray, library: np.ndarray, metric: str) -> np.ndarray:
    """Higher is closer for every metric (Euclidean is returned negated)."""
    if metric == "cosine":
        return bge.l2_normalize(library) @ bge.l2_normalize(query)
    if metric == "dot":
        return library @ query
    return -np.linalg.norm(library - query, axis=1)


def run(params: EmbedParams) -> dict:
    timings: dict[str, float] = {}
    notes: list[str] = []

    t = time.perf_counter()
    library = get_library(params.library_id)
    timings["library"] = _ms(t)

    t = time.perf_counter()
    query_text = (bge.QUERY_INSTRUCTION if params.query_instruction else "") + params.text
    timings["your_text"] = _ms(t)

    # Query side, stage by stage (neural), or the lexical stand-in.
    t = time.perf_counter()
    if params.query_embedder == "neural":
        enc = bge.get_encoder().encode([query_text])
        q_tokens, q_ids, truncated = enc.tokens[0], enc.ids[0], enc.truncated[0]
    else:
        enc = None
        q_tokens, q_ids, truncated = terms(query_text), [], False
    timings["tokenizer"] = _ms(t)

    t = time.perf_counter()
    hidden = enc.hidden[0] if enc else None
    timings["encoder"] = _ms(t)

    t = time.perf_counter()
    q_raw = bge.pool(hidden, params.pooling) if hidden is not None else _lexical().embed([query_text])[0]
    timings["pooling"] = _ms(t)

    t = time.perf_counter()
    q_vec = bge.l2_normalize(q_raw) if params.normalize else q_raw
    if params.library_embedder == "neural":
        lib_raw, lib_tokens = _library_neural(params.library_id, params.pooling)
    else:
        lib_raw = _lexical().embed([i.text for i in library])
        lib_tokens = tuple(len(terms(i.text)) for i in library)
    lib_vecs = bge.l2_normalize(lib_raw) if params.normalize else lib_raw
    timings["normalizer"] = _ms(t)

    t = time.perf_counter()
    comparable = q_vec.shape[0] == lib_vecs.shape[1] and params.query_embedder == params.library_embedder
    if not comparable:
        scores = np.full(len(library), np.nan)
        notes.append(
            f"query vectors ({params.query_embedder}, {q_vec.shape[0]}-D) and library vectors "
            f"({params.library_embedder}, {lib_vecs.shape[1]}-D) come from different models "
            "and cannot be compared"
        )
        ranked: list[int] = []
    else:
        scores = score(q_vec, lib_vecs, params.metric)
        ranked = sorted(range(len(library)), key=lambda i: (-scores[i], i))
    top = ranked[: params.top_k]
    timings["similarity"] = _ms(t)

    t = time.perf_counter()
    if comparable:
        proj = pca_3d(lib_vecs, q_vec)
        points, q_point, variance = proj.chunk_points, proj.query_point, proj.explained_variance
    else:
        proj = pca_3d(lib_vecs, np.zeros(lib_vecs.shape[1]))
        points, q_point, variance = proj.chunk_points, None, proj.explained_variance
    timings["semantic_space"] = _ms(t)

    votes = {c: sum(1 for i in top if library[i].category == c) for c in CATEGORIES}
    rank_of = {i: r + 1 for r, i in enumerate(ranked)}
    return {
        "params": params.model_dump(),
        "model": {"name": bge.MODEL_NAME, "build": bge.MODEL_BUILD, "dim": int(lib_vecs.shape[1]),
                  "max_tokens": bge.MAX_TOKENS} if params.library_embedder == "neural" else
                 {"name": _lexical().name, "build": "ExplodeAI lexical hashing (Lesson 01)",
                  "dim": _lexical().dim, "max_tokens": None},
        "library": {"id": params.library_id, "note": SAMPLE_LIBRARY_NOTE, "categories": list(CATEGORIES),
                    "items": [{"id": it.id, "category": it.category, "text": it.text, "tokens": lib_tokens[k],
                               "score": None if not comparable else round(float(scores[k]), 4),
                               "rank": rank_of.get(k), "point": points[k]}
                              for k, it in enumerate(library)]},
        "query": {
            "text": params.text,
            "model_input": query_text,
            "embedder": params.query_embedder,
            "tokens": [{"text": tok, "id": q_ids[i] if q_ids else None} for i, tok in enumerate(q_tokens)],
            "truncated": truncated,
            "token_vectors": None if hidden is None else
            [[round(float(x), 3) for x in row[:TOKEN_PREVIEW_DIMS]] for row in hidden],
            "pooled_preview": [round(float(x), 4) for x in q_raw[:VECTOR_PREVIEW_DIMS]],
            "norm_before": round(float(np.linalg.norm(q_raw)), 4),
            "norm_after": round(float(np.linalg.norm(q_vec)), 4),
            "dim": int(q_vec.shape[0]),
            "point": q_point,
        },
        "comparable": comparable,
        "neighbours": [{"id": library[i].id, "category": library[i].category, "text": library[i].text,
                        "score": round(float(scores[i]), 4), "rank": r + 1} for r, i in enumerate(top)],
        "votes": votes,
        "projection": {"method": "pca", "explained_variance": variance},
        "notes": notes,
        "timings_ms": timings,
        "stages": STAGES,
    }
