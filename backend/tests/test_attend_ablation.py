"""Each 'breaks if removed' statement for the attention lesson, checked by running the layer without it."""

import pytest

from app.config import REPO_DIR
from app.content.loader import load_lessons
from app.experiments.attend.ablation import ablate
from app.experiments.attend.pipeline import STAGES, AttendParams

P = AttendParams(text="the cat sat on the mat", heads=2, scale=True, causal=True, position=True)


def test_baseline_has_weights_and_vectors():
    out = ablate(P, None)
    assert out["has_weights"] and out["has_output"] and out["output_shape"] == "6 × 64"
    assert out["row_sum_min"] == out["row_sum_max"] == 1.0 and out["future_mass"] == 0


def test_without_tokens_there_is_nothing_to_attend_over():
    out = ablate(P, "tokens")
    assert not out["has_weights"] and out["weights"] is None


def test_without_position_vectors_word_order_changes_nothing_when_unmasked():
    free = AttendParams(text="dog bites man", heads=2, causal=False)
    assert ablate(free, None)["order_gap"] > 0.05
    assert ablate(free, "embed_pos")["order_gap"] < 1e-9


def test_without_qkv_projections_each_word_attends_most_to_itself():
    plain = AttendParams(text="the cat sat on the mat", heads=2, causal=False)
    assert ablate(plain, "qkv")["self_weight"] > ablate(plain, None)["self_weight"] + 0.2


def test_without_scoring_every_visible_word_gets_the_same_weight():
    free = AttendParams(text="the cat sat on the mat", heads=2, causal=False)
    out = ablate(free, "scores")
    assert out["uniform"] and out["mean_max_weight"] == pytest.approx(1 / 6, abs=1e-3)


def test_without_the_mask_words_peek_at_the_future():
    assert ablate(P, None)["future_mass"] == 0
    assert ablate(P, "mask")["future_mass"] > 0.1


def test_without_softmax_rows_do_not_sum_to_one_and_can_be_negative():
    out = ablate(P, "softmax")
    assert out["has_negative"] and not (0.99 < out["row_sum_min"] < 1.01 and 0.99 < out["row_sum_max"] < 1.01)


def test_without_the_weighted_sum_there_are_weights_but_no_word_vectors():
    out = ablate(P, "mix")
    assert out["has_weights"] and not out["has_output"] and out["output_shape"] is None


def test_without_the_output_step_heads_stay_separate():
    out = ablate(P, "output")
    assert not out["has_output"] and out["output_shape"] == "2 × 6 × 32"


def test_unknown_stage_rejected():
    with pytest.raises(ValueError):
        ablate(P, "nope")


def test_every_component_has_a_breaks_statement():
    lessons = load_lessons(REPO_DIR / "content")
    if "attention" not in lessons:
        pytest.skip("the attention lesson content does not exist yet")
    lesson = lessons["attention"]
    assert [c.id for c in lesson.components] == STAGES
    assert all(c.breaks_if_removed for c in lesson.components)


def test_ablate_endpoint(client):
    r = client.post("/api/experiments/attend/ablate", json={**P.model_dump(), "stage": "softmax"})
    assert r.status_code == 200 and r.json()["ablated"]["has_negative"]


CHECK = "/api/experiments/attend/challenges/attention/{}/check"
LEARNER_H = {"X-Learner-Id": "test-learner-0001"}


def _check(client, cid, **params):
    return client.post(CHECK.format(cid), json=params, headers=LEARNER_H)


def test_challenges_fail_when_broken_and_pass_when_fixed(client, monkeypatch):
    """Each challenge starts broken and has a real fix, so none can be passed by accident."""
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "show_draft_lessons", True)
    broken = {"peeking": {"causal": False}, "one-word-takes-all": {"scale": False, "heads": 1},
              "bag-of-words": {"position": False}}
    fixed = {"peeking": {"causal": True},
             "one-word-takes-all": {"scale": True, "heads": 1},
             "bag-of-words": {"position": True}}
    for cid in broken:
        assert _check(client, cid, **broken[cid]).json()["passed"] is False, cid
        assert _check(client, cid, **fixed[cid]).json()["passed"] is True, cid


def test_saturation_challenge_also_accepts_more_narrower_heads(client, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "show_draft_lessons", True)
    assert _check(client, "one-word-takes-all", heads=8, scale=False).json()["passed"] is True


def test_locked_challenge_params_cannot_be_overridden(client, monkeypatch):
    from app.config import get_settings

    monkeypatch.setattr(get_settings(), "show_draft_lessons", True)
    out = _check(client, "peeking", causal=True, text="completely different words").json()
    assert out["result"]["params"]["text"] == "the cat sat on the mat"
