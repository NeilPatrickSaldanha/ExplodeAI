"""A toy self-attention layer, built from scratch with numpy.

It is deliberately NOT a trained model. Every word gets a fixed random vector, the
projection matrices are fixed random matrices, and nothing is learned. That is enough to
run the real mechanism (Q/K/V projections, scaled dot-product scores, a mask, softmax, a
weighted sum, several heads, an output projection) and to see what each step does. What
it cannot show is what a trained model attends to.

Scales follow the assumption in Vaswani et al. (2017): input components with zero mean and
unit variance, so that q and k components are also unit variance and the dot product of two
d_k-dimensional vectors has variance d_k. `tests/test_attend.py` checks that numerically.
"""

import hashlib
import re
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

D_MODEL = 64
SEED = 20261019
MAX_TOKENS = 12
HEAD_CHOICES = (1, 2, 4, 8)
PREVIEW_DIMS = 6

_TOKEN = re.compile(r"[A-Za-z']+|\d+|[^\sA-Za-z\d]")


def tokenize(text: str) -> list[str]:
    """Words, numbers and punctuation marks. Capped so the attention grid stays readable."""
    return _TOKEN.findall(text)[:MAX_TOKENS]


def word_vector(word: str) -> np.ndarray:
    """A fixed random vector per (lowercased) word: the same word always gets the same one."""
    seed = int.from_bytes(hashlib.sha256(word.lower().encode()).digest()[:8], "big")
    return np.random.default_rng(seed).standard_normal(D_MODEL)


def position_encoding(n: int, d: int = D_MODEL) -> np.ndarray:
    """Sinusoidal positions, Vaswani et al. 2017 §3.5: sin on even dims, cos on odd dims."""
    pos = np.arange(n)[:, None]
    i = np.arange(d // 2)[None, :]
    angle = pos / np.power(10000.0, 2 * i / d)
    pe = np.zeros((n, d))
    pe[:, 0::2] = np.sin(angle)
    pe[:, 1::2] = np.cos(angle)
    return pe


@dataclass(frozen=True)
class Weights:
    wq: np.ndarray  # (heads, D_MODEL, d_k)
    wk: np.ndarray
    wv: np.ndarray
    wo: np.ndarray  # (D_MODEL, D_MODEL)


@lru_cache(maxsize=len(HEAD_CHOICES))
def weights(heads: int) -> Weights:
    """Fixed random projections. Heads split the same d_model-wide matrices column-wise,
    so d_k = d_model / heads, as in the original multi-head layout."""
    if D_MODEL % heads:
        raise ValueError(f"heads must divide {D_MODEL}")
    rng = np.random.default_rng(SEED)
    scale = 1.0 / np.sqrt(D_MODEL)
    full = [rng.standard_normal((D_MODEL, D_MODEL)) * scale for _ in range(4)]
    d_k = D_MODEL // heads

    def split(m: np.ndarray) -> np.ndarray:
        return np.stack([m[:, h * d_k:(h + 1) * d_k] for h in range(heads)])

    return Weights(split(full[0]), split(full[1]), split(full[2]), full[3])


def inputs(words: list[str], position: bool) -> np.ndarray:
    """Attention's input: word vectors, plus positions when asked. Sums are divided by sqrt(1.5), the
    spread of (unit-variance word + sinusoid), so components stay near unit variance either way."""
    x = np.stack([word_vector(w) for w in words])
    if position:
        x = (x + position_encoding(len(words))) / np.sqrt(1.5)
    return x


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Softmax with the maximum subtracted first, so large scores cannot overflow."""
    shifted = x - np.max(x, axis=axis, keepdims=True)
    e = np.exp(shifted)
    return e / np.sum(e, axis=axis, keepdims=True)


def causal_mask(n: int) -> np.ndarray:
    """True where a position may NOT be attended to: every later position."""
    return np.triu(np.ones((n, n), dtype=bool), k=1)


def entropy(weights_row: np.ndarray) -> float:
    p = weights_row[weights_row > 0]
    return float(-(p * np.log(p)).sum())
