"""Attention experiment: the mechanism, checked against an independent reference."""

import math

import numpy as np
import pytest

from app.experiments.attend import model as m
from app.experiments.attend.pipeline import STAGES, AttendParams, forward, order_gap, run, stats
from tests.conftest import validates

SENTENCES = [
    "the cat sat on the mat",
    "dog bites man",
    "the animal did not cross the street because it was too tired",
    "attention lets every word look at every other word",
    "she poured water into the glass until it was full",
    "tokens become vectors then queries meet keys",
]


def words(text: str) -> list[str]:
    return m.tokenize(text)


def naive(ws: list[str], heads: int, scale: bool, causal: bool, position: bool):
    """The same layer written with plain Python loops, as an independent reference."""
    n, d_k = len(ws), m.D_MODEL // heads
    w = m.weights(heads)
    x = [list(m.word_vector(wd)) for wd in ws]
    if position:
        pe = m.position_encoding(n)
        x = [[(x[i][c] + pe[i][c]) / math.sqrt(1.5) for c in range(m.D_MODEL)] for i in range(n)]

    def proj(mat, i):  # one token, one head
        return [sum(x[i][c] * mat[c][k] for c in range(m.D_MODEL)) for k in range(d_k)]

    outs = [[0.0] * m.D_MODEL for _ in range(n)]
    all_weights = []
    mixed_all = [[[0.0] * d_k for _ in range(n)] for _ in range(heads)]
    for h in range(heads):
        q = [proj(w.wq[h], i) for i in range(n)]
        k = [proj(w.wk[h], i) for i in range(n)]
        v = [proj(w.wv[h], i) for i in range(n)]
        head_w = []
        for i in range(n):
            s = [sum(q[i][c] * k[j][c] for c in range(d_k)) for j in range(n)]
            if scale:
                s = [a / math.sqrt(d_k) for a in s]
            allowed = [j for j in range(n) if not (causal and j > i)]
            mx = max(s[j] for j in allowed)
            e = [math.exp(s[j] - mx) if j in allowed else 0.0 for j in range(n)]
            tot = sum(e)
            row = [a / tot for a in e]
            head_w.append(row)
            mixed_all[h][i] = [sum(row[j] * v[j][c] for j in range(n)) for c in range(d_k)]
        all_weights.append(head_w)
    for i in range(n):
        cat = [c for h in range(heads) for c in mixed_all[h][i]]
        outs[i] = [sum(cat[r] * w.wo[r][c] for r in range(m.D_MODEL)) for c in range(m.D_MODEL)]
    return np.array(all_weights), np.array(outs)


@validates("attn-scaled-dot-product", "attn-weighted-sum", "attn-qkv-projections")
@pytest.mark.parametrize("heads,scale,causal,position", [(1, True, False, True), (2, True, True, True),
                                                         (4, False, False, False), (8, True, True, False)])
def test_layer_matches_an_independent_loop_implementation(heads, scale, causal, position):
    ws = words("the cat sat on the mat")
    f = forward(ws, heads, scale, causal, position)
    ref_w, ref_out = naive(ws, heads, scale, causal, position)
    assert np.allclose(f.weights, ref_w, atol=1e-9)
    assert np.allclose(f.out, ref_out, atol=1e-9)


@validates("attn-softmax-weights")
def test_attention_weights_are_non_negative_and_every_row_sums_to_one():
    for text in SENTENCES:
        for heads in m.HEAD_CHOICES:
            f = forward(words(text), heads, True, False, True)
            assert (f.weights >= 0).all()
            assert np.allclose(f.weights.sum(axis=-1), 1.0)


@validates("attn-softmax-stable")
def test_softmax_survives_huge_scores():
    out = m.softmax(np.array([[1000.0, 1001.0, 999.0]]))
    assert np.isfinite(out).all() and math.isclose(out.sum(), 1.0)


@validates("attn-sqrt-dk-scaling")
def test_unscaled_scores_have_variance_d_k_and_scaling_brings_it_to_about_one():
    """Vaswani et al.'s assumption, checked on this layer: unit-variance inputs give q.k variance d_k."""
    for heads in (1, 4, 8):
        d_k = m.D_MODEL // heads
        raw, scaled = [], []
        for text in SENTENCES:
            f = forward(words(text), heads, True, False, True)
            raw.append(f.raw.ravel())
            scaled.append(f.scaled.ravel())
        raw_var, scaled_var = float(np.concatenate(raw).var()), float(np.concatenate(scaled).var())
        assert 0.6 * d_k < raw_var < 1.5 * d_k
        assert 0.6 < scaled_var < 1.5


@validates("attn-softmax-saturation")
def test_without_scaling_a_wide_head_becomes_nearly_one_hot():
    wide = [stats(forward(words(t), 1, False, False, True), False)["mean_max_weight"] for t in SENTENCES]
    scaled = [stats(forward(words(t), 1, True, False, True), False)["mean_max_weight"] for t in SENTENCES]
    assert np.mean(wide) > 0.85 and min(wide) > 0.75
    assert np.mean(scaled) < 0.6 and max(scaled) < 0.75


@validates("attn-causal-mask")
def test_causal_mask_gives_zero_weight_to_later_words():
    for text in SENTENCES:
        f = forward(words(text), 2, True, True, True)
        assert (f.weights[:, m.causal_mask(len(words(text)))] == 0).all()
        assert np.allclose(f.weights[:, 0, 0], 1.0)  # the first word can only see itself
        assert np.allclose(f.weights.sum(axis=-1), 1.0)


@validates("attn-causal-mask")
def test_without_the_mask_words_attend_to_later_words():
    f = forward(words("the cat sat on the mat"), 2, True, False, True)
    assert stats(f, False)["future_mass"] > 0.1


@validates("attn-position-needed")
def test_without_positions_or_a_mask_word_order_changes_nothing():
    """Self-attention alone is permutation-equivariant; positions (or a causal mask) break the tie."""
    base = dict(text="dog bites man", heads=2, scale=True)
    assert order_gap(AttendParams(**base, causal=False, position=False)) < 1e-9
    assert order_gap(AttendParams(**base, causal=False, position=True)) > 0.05
    assert order_gap(AttendParams(**base, causal=True, position=False)) > 0.05


@validates("attn-position-encoding")
def test_sinusoidal_positions_follow_the_published_formula():
    pe = m.position_encoding(6)
    for pos in range(6):
        for i in range(m.D_MODEL // 2):
            angle = pos / (10000 ** (2 * i / m.D_MODEL))
            assert math.isclose(pe[pos, 2 * i], math.sin(angle), abs_tol=1e-12)
            assert math.isclose(pe[pos, 2 * i + 1], math.cos(angle), abs_tol=1e-12)


@validates("attn-multihead-concat")
def test_heads_split_the_model_width_and_concatenate_back_to_it():
    for heads in m.HEAD_CHOICES:
        f = forward(words("the cat sat"), heads, True, False, True)
        assert f.q.shape == (heads, 3, m.D_MODEL // heads)
        assert f.mixed.shape == (heads, 3, m.D_MODEL // heads)
        assert f.out.shape == (3, m.D_MODEL)


@validates("attn-heads-additive")
def test_concatenating_heads_then_projecting_equals_summing_per_head_slices():
    f = forward(words("the cat sat on the mat"), 4, True, False, True)
    w = m.weights(4)
    d_k = m.D_MODEL // 4
    summed = sum(f.mixed[h] @ w.wo[h * d_k:(h + 1) * d_k] for h in range(4))
    assert np.allclose(f.out, summed)


@validates("attn-kv-cache-valid")
def test_with_a_causal_mask_earlier_words_do_not_change_when_later_words_arrive():
    """The reason a KV cache is valid: outputs (and keys, values) for a prefix are the same with or without the rest."""
    full = forward(words("the cat sat on the mat"), 2, True, True, True)
    prefix = forward(words("the cat sat"), 2, True, True, True)
    assert np.allclose(full.out[:3], prefix.out)
    assert np.allclose(full.k[:, :3], prefix.k) and np.allclose(full.v[:, :3], prefix.v)
    # Without the mask, earlier words do change when later words arrive.
    free_full = forward(words("the cat sat on the mat"), 2, True, False, True)
    free_prefix = forward(words("the cat sat"), 2, True, False, True)
    assert not np.allclose(free_full.out[:3], free_prefix.out)


@validates("attn-quadratic-cost")
def test_the_score_grid_has_n_squared_entries_per_head():
    for n_words in (2, 5, 9, 12):
        f = forward(words(" ".join(["w"] * n_words)), 2, True, False, True)
        assert f.raw.shape == (2, n_words, n_words)
        assert f.raw[0].size == n_words**2


def test_the_same_word_always_gets_the_same_vector_and_runs_are_deterministic():
    assert np.array_equal(m.word_vector("Cat"), m.word_vector("cat"))
    a, b = run(AttendParams()), run(AttendParams())
    assert a["heads"] == b["heads"] and a["output"] == b["output"]


def test_run_reports_every_stage_and_bounded_numbers():
    out = run(AttendParams(text="the cat sat on the mat", heads=4))
    assert out["stages"] == STAGES and set(out["timings_ms"]) == set(STAGES)
    assert len(out["heads"]) == 4 and len(out["tokens"]) == 6
    assert all(len(row) == 6 for row in out["weights_mean"])
    assert out["model"]["kind"] == "toy"


def test_input_is_capped_and_validated():
    assert len(run(AttendParams(text=" ".join(["w"] * 30)))["tokens"]) == m.MAX_TOKENS
    with pytest.raises(ValueError):
        AttendParams(text="!!!   ", heads=3)
    with pytest.raises(ValueError):
        AttendParams(text="hello", heads=3)
