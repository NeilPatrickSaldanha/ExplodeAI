"""What breaks if an attention step is removed? Run the real toy layer without it.

- tokens      no words, so there is nothing to attend over.
- embed_pos   no position vectors: with the causal mask off, each word's output is the same
              whatever order the words arrive in.
- qkv         no Q/K/V projections: the words themselves are compared with each other, so each
              word's strongest match is itself.
- scores      no scoring step: every visible word gets the same weight, so each output is
              just an average.
- mask        no mask: every word can attend to the words after it (peeking at the future).
- softmax     no softmax: raw scores are used as weights, so rows do not sum to 1 and can be
              negative.
- mix         no weighted sum: there is a table of weights, but no new word vectors.
- output      no concatenation or output projection: each head's result stays separate, so
              there is no single d_model-wide vector per word.

These statements describe ExplodeAI's own toy layer and are checked by
tests/test_attend_ablation.py.
"""

import numpy as np

from app.experiments.attend import model as m
from app.experiments.attend.pipeline import STAGES, AttendParams, _r

TRIVIAL = {
    "tokens": "no words, so there is nothing to attend over",
}


def _variant(words: list[str], p: AttendParams, stage: str | None):
    """Return (weights (h,n,n), mixed or None, out or None) with one stage removed."""
    n = len(words)
    heads = 1 if stage == "qkv" else p.heads
    d_k = m.D_MODEL // heads
    w = m.weights(heads)
    x = m.inputs(words, p.position and stage != "embed_pos")
    if stage == "qkv":
        q = k = v = x[None]
        d_k = m.D_MODEL
    else:
        q = np.einsum("nd,hdk->hnk", x, w.wq)
        k = np.einsum("nd,hdk->hnk", x, w.wk)
        v = np.einsum("nd,hdk->hnk", x, w.wv)
    scores = np.einsum("hik,hjk->hij", q, k)
    if p.scale:
        scores = scores / np.sqrt(d_k)
    if stage == "scores":
        scores = np.zeros_like(scores)
    hide = m.causal_mask(n) if (p.causal and stage != "mask") else np.zeros((n, n), dtype=bool)
    masked = np.where(hide[None], -np.inf, scores)
    weights = np.where(hide[None], 0.0, scores) if stage == "softmax" else m.softmax(masked, axis=-1)
    if stage == "mix":
        return weights, None, None
    mixed = np.einsum("hij,hjk->hik", weights, v)
    if stage == "output":
        return weights, mixed, None
    return weights, mixed, np.concatenate(list(mixed), axis=-1) @ w.wo


def _order_gap(words: list[str], p: AttendParams, stage: str | None) -> float | None:
    a = _variant(words, p, stage)[2]
    b = _variant(words[::-1], p, stage)[2]
    if a is None or b is None:
        return None
    return round(float(np.abs(a - b[::-1]).max()), 6)


def ablate(params: AttendParams, stage: str | None) -> dict:
    if stage is not None and stage not in STAGES:
        raise ValueError(f"unknown stage '{stage}'")
    words = m.tokenize(params.text)
    n = len(words)
    notes: list[str] = []
    empty = {"removed": stage, "has_weights": False, "has_output": False, "output_shape": None,
             "weights": None,
             "row_sum_min": None, "row_sum_max": None, "has_negative": None, "future_mass": None,
             "self_weight": None, "mean_max_weight": None, "order_gap": None, "uniform": None, "notes": notes}
    if stage == "tokens":
        notes.append("no words, so there is nothing to attend over")
        return empty

    weights, mixed, out = _variant(words, params, stage)
    future = m.causal_mask(n)
    sums = weights.sum(axis=-1)
    h = weights.shape[0]
    gap = _order_gap(words, params, stage)
    first = weights[0]
    uniform = None
    if stage == "scores":
        uniform = bool(np.allclose(weights, weights[:, :1, :]) and not params.causal)
    if stage == "embed_pos":
        extra = "; the causal mask still reveals order" if params.causal else ""
        notes.append("no position vectors" + extra)
    elif stage == "qkv":
        notes.append("words are compared directly: queries, keys and values are all the raw word vectors")
    elif stage == "scores":
        notes.append("no scores, so every visible word gets the same weight")
    elif stage == "mask":
        notes.append("no mask" if params.causal else "the mask was already off, so nothing changes")
    elif stage == "softmax":
        notes.append("raw scores are used as weights, so rows do not sum to 1")
    elif stage == "mix":
        notes.append("a table of weights, but no weighted sum, so no new word vectors")
    elif stage == "output":
        notes.append(f"{h} separate head results of {m.D_MODEL // h} numbers each, never combined")
    shape = None
    if out is not None:
        shape = f"{n} × {out.shape[1]}"
    elif mixed is not None:
        shape = f"{h} × {n} × {mixed.shape[2]}"
    return {
        "removed": stage,
        "has_weights": True,
        "has_output": out is not None,
        "output_shape": shape,
        "weights": _r(first),
        "row_sum_min": round(float(sums.min()), 4),
        "row_sum_max": round(float(sums.max()), 4),
        "has_negative": bool((weights < 0).any()),
        "future_mass": round(float(weights[:, future].sum(axis=-1).mean() / n), 6),
        "self_weight": round(float(np.mean([weights[hd][i, i] for hd in range(h) for i in range(n)])), 4),
        "mean_max_weight": round(float(weights.max(axis=-1).mean()), 4),
        "order_gap": gap,
        "uniform": uniform,
        "notes": notes,
    }
