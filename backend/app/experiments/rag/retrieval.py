"""Retrieval: dense similarity, BM25, and hybrid reciprocal rank fusion.

- dense:  exact (brute-force) nearest-neighbour search. Because every vector is
          L2-normalised, the dot product equals cosine similarity.
- bm25:   Okapi BM25 over the same chunks. IDF uses the non-negative form
          ln(1 + (N - n + 0.5) / (n + 0.5)) used by Lucene, so a term appearing
          in most chunks never gets a negative weight. k1 = 1.2 and b = 0.75 are
          the Elasticsearch/Lucene defaults; Robertson & Zaragoza (2009) give
          0.5 < b < 0.8 and 1.2 < k1 < 2 as reasonable ranges, not fixed values.
- hybrid: reciprocal rank fusion, score(d) = Σ 1 / (k + rank_i(d)), k = 60.
"""

import math
from collections import Counter
from dataclasses import dataclass
from typing import Literal

import numpy as np

from app.experiments.rag.text import terms

Method = Literal["dense", "bm25", "hybrid"]
RRF_K = 60


@dataclass(frozen=True)
class Hit:
    index: int
    score: float
    rank: int  # 1-based


def rank(scores: np.ndarray) -> list[Hit]:
    order = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
    return [Hit(i, float(scores[i]), r + 1) for r, i in enumerate(order)]


def dense_scores(chunk_vecs: np.ndarray, query_vec: np.ndarray) -> np.ndarray:
    return chunk_vecs @ query_vec


class BM25:
    def __init__(self, docs: list[str], k1: float = 1.2, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.tokens = [terms(d) for d in docs]
        self.n = len(docs)
        self.avgdl = sum(len(t) for t in self.tokens) / max(self.n, 1)
        df: Counter[str] = Counter()
        for t in self.tokens:
            df.update(set(t))
        self.idf = {w: math.log(1 + (self.n - c + 0.5) / (c + 0.5)) for w, c in df.items()}

    def scores(self, query: str) -> np.ndarray:
        q = terms(query)
        out = np.zeros(self.n)
        for i, toks in enumerate(self.tokens):
            tf = Counter(toks)
            norm = self.k1 * (1 - self.b + self.b * len(toks) / self.avgdl)
            for w in q:
                f = tf.get(w, 0)
                if f:
                    out[i] += self.idf[w] * f * (self.k1 + 1) / (f + norm)
        return out


def rrf(rankings: list[list[Hit]], n: int, k: int = RRF_K) -> np.ndarray:
    fused = np.zeros(n)
    for hits in rankings:
        for h in hits:
            fused[h.index] += 1.0 / (k + h.rank)
    return fused
