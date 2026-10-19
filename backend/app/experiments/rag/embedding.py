"""Embedders.

`HashingEmbedder` is the always-available default. It is a *lexical* embedding:
TF-IDF weights over word unigrams and bigrams, folded into a fixed number of
dimensions with the signed hashing trick, then L2-normalised. Texts that share
words land close together; texts that mean the same thing in different words
do NOT. The lesson labels it as a stand-in for a neural embedding model.

`FastEmbedEmbedder` (optional extra: `uv sync --extra neural`) runs a small
neural embedding model locally on CPU. It needs a one-time model download and
costs nothing per call.

Paid provider embeddings are intentionally not wired in here: they would go
through `app.ai.guard` like every other paid call.
"""

import hashlib
import math
from collections import Counter
from typing import Protocol

import numpy as np

from app.experiments.rag.text import terms


class Embedder(Protocol):
    name: str
    kind: str  # "lexical-hashing" | "neural-local"
    dim: int

    def fit(self, texts: list[str]) -> None: ...
    def embed(self, texts: list[str]) -> np.ndarray: ...


def _features(text: str) -> list[str]:
    toks = terms(text)
    return toks + [f"{a} {b}" for a, b in zip(toks, toks[1:], strict=False)]


def _bucket(feature: str, dim: int) -> tuple[int, float]:
    """Deterministic (process-independent) hash → (index, sign)."""
    digest = hashlib.blake2b(feature.encode(), digest_size=8).digest()
    value = int.from_bytes(digest, "little")
    return value % dim, (1.0 if (value >> 63) & 1 else -1.0)


class HashingEmbedder:
    name = "tfidf-hashing-1024"
    kind = "lexical-hashing"

    def __init__(self, dim: int = 1024) -> None:
        self.dim = dim
        self._idf: dict[str, float] = {}

    def fit(self, texts: list[str]) -> None:
        n = len(texts)
        df: Counter[str] = Counter()
        for t in texts:
            df.update(set(_features(t)))
        # Smoothed IDF (as in scikit-learn's TfidfVectorizer with smooth_idf=True).
        self._idf = {f: math.log((1 + n) / (1 + c)) + 1 for f, c in df.items()}
        self._default_idf = math.log(1 + n) + 1

    def embed(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float64)
        for row, text in enumerate(texts):
            for feature, tf in Counter(_features(text)).items():
                idx, sign = _bucket(feature, self.dim)
                weight = (1 + math.log(tf)) * self._idf.get(feature, self._default_idf)
                out[row, idx] += sign * weight
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return out / norms


class FastEmbedEmbedder:  # pragma: no cover - exercised only when the extra is installed
    kind = "neural-local"

    def __init__(self, model: str = "BAAI/bge-small-en-v1.5") -> None:
        from fastembed import TextEmbedding

        self._model = TextEmbedding(model_name=model)
        self.name = model
        self.dim = len(next(iter(self._model.embed(["probe"]))))

    def fit(self, texts: list[str]) -> None:
        return None

    def embed(self, texts: list[str]) -> np.ndarray:
        vecs = np.array(list(self._model.embed(texts)), dtype=np.float64)
        return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


def neural_available() -> bool:
    try:
        import fastembed  # noqa: F401
    except ImportError:
        return False
    return True


def make_embedder(kind: str) -> Embedder:
    if kind == "neural-local":
        if not neural_available():
            raise ValueError("neural-local embedder needs the optional 'neural' extra")
        return FastEmbedEmbedder()
    if kind == "lexical-hashing":
        return HashingEmbedder()
    raise ValueError(f"unknown embedder: {kind}")
