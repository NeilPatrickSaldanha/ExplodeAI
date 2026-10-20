"""End-to-end attention experiment: every stage runs for real and is timed.

The stage ids are the contract between this code, the lesson content
(`content/lessons/attention/lesson.yaml` components) and the 3D view.
"""

import time
from dataclasses import dataclass

import numpy as np
from pydantic import BaseModel, Field, field_validator

from app.experiments.attend import model as m

STAGE_DEPENDENCIES: dict[str, list[str]] = {
    "tokens": [],
    "embed_pos": ["tokens"],
    "qkv": ["embed_pos"],
    "scores": ["qkv"],
    "mask": ["scores"],
    "softmax": ["mask"],
    "mix": ["softmax", "qkv"],
    "output": ["mix"],
}
STAGES = list(STAGE_DEPENDENCIES)

NOTE = ("A toy attention layer with fixed random weights. It runs the real mechanism, but it is not a "
        "trained model, so the patterns show how attention works, not what a trained model attends to.")


class AttendParams(BaseModel):
    text: str = Field("the cat sat on the mat", min_length=1, max_length=120)
    heads: int = 2
    scale: bool = True
    causal: bool = False
    position: bool = True
    head: int = Field(0, ge=0, le=7)

    @field_validator("heads")
    @classmethod
    def _heads(cls, v: int) -> int:
        if v not in m.HEAD_CHOICES:
            raise ValueError(f"heads must be one of {list(m.HEAD_CHOICES)}")
        return v

    @field_validator("text")
    @classmethod
    def _text(cls, v: str) -> str:
        if not m.tokenize(v):
            raise ValueError("text needs at least one word")
        return v


def _ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


def _r(a: np.ndarray, nd: int = 4) -> list:
    return np.round(a, nd).tolist()


@dataclass
class Forward:
    words: list[str]
    x: np.ndarray  # (n, D_MODEL) input to attention
    q: np.ndarray  # (heads, n, d_k)
    k: np.ndarray
    v: np.ndarray
    raw: np.ndarray  # (heads, n, n) Q Kᵀ
    scaled: np.ndarray  # after the optional 1/sqrt(d_k)
    masked: np.ndarray  # scaled, with -inf where the mask hides a position
    weights: np.ndarray  # softmax of masked
    mixed: np.ndarray  # (heads, n, d_k) weights · V
    out: np.ndarray  # (n, D_MODEL) concat heads · W_o
    timings: dict[str, float]


def forward(words: list[str], heads: int, scale: bool, causal: bool, position: bool) -> Forward:
    n = len(words)
    w = m.weights(heads)
    d_k = m.D_MODEL // heads
    t = time.perf_counter()
    timings: dict[str, float] = {"tokens": _ms(t)}

    t = time.perf_counter()
    x = m.inputs(words, position)
    timings["embed_pos"] = _ms(t)

    t = time.perf_counter()
    q = np.einsum("nd,hdk->hnk", x, w.wq)
    k = np.einsum("nd,hdk->hnk", x, w.wk)
    v = np.einsum("nd,hdk->hnk", x, w.wv)
    timings["qkv"] = _ms(t)

    t = time.perf_counter()
    raw = np.einsum("hik,hjk->hij", q, k)
    scaled = raw / np.sqrt(d_k) if scale else raw
    timings["scores"] = _ms(t)

    t = time.perf_counter()
    masked = scaled.copy()
    if causal:
        masked[:, m.causal_mask(n)] = -np.inf
    timings["mask"] = _ms(t)

    t = time.perf_counter()
    weights = m.softmax(masked, axis=-1)
    timings["softmax"] = _ms(t)

    t = time.perf_counter()
    mixed = np.einsum("hij,hjk->hik", weights, v)
    timings["mix"] = _ms(t)

    t = time.perf_counter()
    out = np.concatenate(list(mixed), axis=-1) @ w.wo
    timings["output"] = _ms(t)
    return Forward(words, x, q, k, v, raw, scaled, masked, weights, mixed, out, timings)


def stats(f: Forward, causal: bool) -> dict:
    h, n, _ = f.weights.shape
    d_k = m.D_MODEL // h
    visible = ~m.causal_mask(n) if causal else np.ones((n, n), dtype=bool)
    future = m.causal_mask(n)
    return {
        "head_dim": d_k,
        "score_std_raw": round(float(f.raw[:, visible].std()), 3),
        "score_std_used": round(float(f.scaled[:, visible].std()), 3),
        "expected_raw_std": round(float(np.sqrt(d_k)), 3),
        "mean_max_weight": round(float(f.weights.max(axis=-1).mean()), 4),
        "mean_entropy": round(float(np.mean([m.entropy(r) for hd in f.weights for r in hd])), 4),
        "future_mass": round(float(f.weights[:, future].sum(axis=-1).mean() / n), 6),
        "self_weight": round(float(np.mean([f.weights[hd][i, i] for hd in range(h) for i in range(n)])), 4),
        "row_sum_min": round(float(f.weights.sum(axis=-1).min()), 6),
        "row_sum_max": round(float(f.weights.sum(axis=-1).max()), 6),
    }


def order_gap(params: AttendParams) -> float:
    """How much each word's output changes when the SAME words come in reverse order.

    Compared word by word (output of word i in the original vs. the same word in the reversed
    sentence). Exactly zero means the output ignores word order."""
    words = m.tokenize(params.text)
    a = forward(words, params.heads, params.scale, params.causal, params.position)
    b = forward(words[::-1], params.heads, params.scale, params.causal, params.position)
    return round(float(np.abs(a.out - b.out[::-1]).max()), 6)


def run(params: AttendParams) -> dict:
    words = m.tokenize(params.text)
    f = forward(words, params.heads, params.scale, params.causal, params.position)
    n = len(words)
    h = params.heads
    head = min(params.head, h - 1)
    st = stats(f, params.causal)
    gap = order_gap(params)
    pe = m.position_encoding(n)
    notes: list[str] = []
    if len(m.tokenize(params.text)) == m.MAX_TOKENS and len(m._TOKEN.findall(params.text)) > m.MAX_TOKENS:
        notes.append(f"Only the first {m.MAX_TOKENS} tokens are used so the grid stays readable.")
    return {
        "params": params.model_dump(),
        "model": {"kind": "toy", "note": NOTE, "d_model": m.D_MODEL, "heads": h, "head_dim": m.D_MODEL // h,
                  "seed": m.SEED},
        "tokens": [{"index": i, "text": wd} for i, wd in enumerate(words)],
        "embedding": {
            "word_preview": _r(np.stack([m.word_vector(wd) for wd in words])[:, :m.PREVIEW_DIMS]),
            "position_preview": _r(pe[:, :m.PREVIEW_DIMS]) if params.position else None,
            "input_preview": _r(f.x[:, :m.PREVIEW_DIMS]),
        },
        "heads": [
            {"index": i, "q": _r(f.q[i][:, :m.PREVIEW_DIMS]), "k": _r(f.k[i][:, :m.PREVIEW_DIMS]),
             "v": _r(f.v[i][:, :m.PREVIEW_DIMS]), "scores_raw": _r(f.raw[i], 3), "scores": _r(f.scaled[i], 3),
             "weights": _r(f.weights[i])}
            for i in range(h)
        ],
        "selected_head": head,
        "weights_mean": _r(f.weights.mean(axis=0)),
        "output": {"preview": _r(f.out[:, :m.PREVIEW_DIMS]), "norms": _r(np.linalg.norm(f.out, axis=1), 3)},
        "stats": {**st, "order_gap": gap},
        "notes": notes,
        "timings_ms": f.timings,
        "stages": STAGES,
    }
