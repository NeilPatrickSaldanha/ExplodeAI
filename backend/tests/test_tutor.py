"""The tutor answers only from verified lesson content, and says so when it cannot."""

import re

import pytest
from pydantic import SecretStr
from sqlmodel import Session, select

from app.ai import providers
from app.config import get_settings
from app.content.loader import content
from app.db import AIUsage
from app.tutor import prompt as tprompt
from app.tutor.index import build_passages
from app.tutor.search import TutorIndex
from tests.test_ai_guard import FAKE_KEY, PRICES

H = {"X-Learner-Id": "tutor-test-learner"}


@pytest.fixture(scope="module")
def passages():
    registry, lessons = content()
    return build_passages(lessons, registry)


@pytest.fixture(scope="module")
def index(passages):
    return TutorIndex(passages)


def ask(client, question, **kw):
    return client.post("/api/tutor/ask", json={"question": question, **kw}, headers=H)


def test_index_only_contains_lesson_content_with_real_claims_and_sources(passages):
    registry, lessons = content()
    claim_ids = {c.id for lesson in lessons.values() for c in lesson.claims}
    sources = registry.by_id()
    assert len(passages) > 400 and {p.lesson_id for p in passages} == set(lessons)
    for p in passages:
        assert p.id.split("/")[0] == p.lesson_id
        assert set(p.claim_ids) <= claim_ids and set(p.source_ids) <= set(sources)
    analogies = [p for p in passages if p.kind == "analogy"]
    assert analogies and all(p.teaching_aid for p in analogies)
    assert not any(p.teaching_aid for p in passages if p.kind != "analogy")


def test_answers_quote_lesson_text_and_cite_real_claims_and_sources(client, passages):
    r = ask(client, "Why do we divide the scores by the square root of d_k?", lesson_id="attention").json()
    assert r["covered"] and r["sentences"] and r["sources"]
    texts = [p.text for p in passages]
    for s in r["sentences"]:
        assert any(s["text"] in t for t in texts), "every sentence is quoted from lesson content"
        assert s["claim_ids"], "every sentence carries the claims behind it"
    assert {c["id"] for c in r["claims"]} == {c for s in r["sentences"] for c in s["claim_ids"]}
    assert all(s["url"].startswith("http") for s in r["sources"])
    assert r["related"] and r["related"][0]["lesson_id"] == "attention"


def test_a_question_the_lessons_do_not_cover_gets_no_answer_and_no_sources(client):
    for q in ("What is the capital of France?", "How do I bake bread?", "Tell me a joke"):
        r = ask(client, q).json()
        assert r["covered"] is False and r["sentences"] == [] and r["sources"] == [] and r["claims"] == []
        assert "don't cover that" in r["message"]
        assert {t["lesson_id"] for t in r["topics"]} >= {"attention", "embeddings"}


def test_analogies_are_labelled_as_teaching_aids(client):
    r = ask(client, "What are queries, keys and values?", lesson_id="attention").json()
    if r["analogy"]:
        assert "not a verified fact" in r["analogy"]["note"]
    assert all(s["kind"] != "analogy" for s in r["sentences"])


def test_the_open_stage_nudges_but_does_not_override_the_question(index):
    plain, _ = index.search("what can go wrong?", k=3)
    boosted, _ = index.search("what can go wrong?", lesson_id="attention", stage_id="softmax", k=3)
    assert boosted[0].passage.stage_id == "softmax"
    assert plain[0].passage.stage_id != "softmax" or plain[0].passage.lesson_id != "attention"
    # A clear question about another topic still wins over the open stage.
    off, _ = index.search("what is the causal mask?", lesson_id="attention", stage_id="softmax", k=3)
    assert off[0].passage.stage_id == "mask"


def test_input_is_validated(client):
    assert ask(client, "ok").status_code == 422
    assert ask(client, "x" * 301).status_code == 422
    assert ask(client, "   hello   ").status_code in (200,)


def test_suggestions_follow_the_stage(client):
    out = client.get(
        "/api/tutor/suggestions", params={"lesson_id": "attention", "stage_id": "softmax"}
    ).json()
    assert len(out["suggestions"]) == 3 and "Softmax" in out["suggestions"][0]
    assert client.get("/api/tutor/suggestions").json()["suggestions"]


def test_tutor_mode_asks_about_every_stage_and_answers_from_its_explanation():
    from app.tutor import quiz

    _, lessons = content()
    claim_ids = {c.id for lesson in lessons.values() for c in lesson.claims}
    for lesson in lessons.values():
        for comp in lesson.components:
            seen = set()
            for n in range(6):
                q = quiz.check(lesson.id, comp.id, n)
                assert q["question"] and q["answer"] and set(q["claim_ids"]) <= claim_ids
                assert q["stage_label"] == comp.label and q["total"] == 5
                seen.add(q["index"])
            assert seen == {0, 1, 2, 3, 4}


def test_tutor_mode_endpoint_and_unknown_stages(client):
    q = client.get(
        "/api/tutor/check", params={"lesson_id": "attention", "stage_id": "softmax", "n": 2}, headers=H
    )
    assert q.status_code == 200 and "Softmax" in q.json()["question"]
    assert (
        client.get(
            "/api/tutor/check", params={"lesson_id": "attention", "stage_id": "nope"}, headers=H
        ).status_code
        == 404
    )
    assert (
        client.get("/api/tutor/check", params={"lesson_id": "nope", "stage_id": "x"}, headers=H).status_code
        == 404
    )


# ------------------------------------------------------------- the optional paid path (mocked)
def _enable(monkeypatch):
    import app.routers.tutor as tutor_router
    from app.ai import guard

    s = get_settings()
    monkeypatch.setattr(s, "ai_features_enabled", True)
    monkeypatch.setattr(s, "anthropic_api_key", SecretStr(FAKE_KEY))
    monkeypatch.setattr(guard, "load_prices", lambda: PRICES)
    monkeypatch.setattr(tutor_router, "load_prices", lambda: PRICES)


LLM = {"provider": "anthropic", "model": "test-model", "confirm_paid": True}


def test_paid_path_is_refused_by_default(client):
    r = client.post("/api/tutor/ask/llm", json={"question": "What is the causal mask?", **LLM}, headers=H)
    assert r.status_code == 403


def test_paid_answer_builds_the_prompt_from_lessons_and_strips_unknown_citations(client, engine, monkeypatch):
    _enable(monkeypatch)
    seen = {}

    def fake(settings_, provider, model, prompt, max_tokens):
        seen["prompt"] = prompt
        return providers.Generation("The mask hides later words [attn-causal-mask] [made-up-claim].", 200, 20)

    monkeypatch.setattr(providers, "generate_with_usage", fake)
    r = client.post("/api/tutor/ask/llm", json={"question": "What is the causal mask?", **LLM}, headers=H)
    assert r.status_code == 200, r.text
    out = r.json()
    assert (
        "ONLY the numbered passages" in seen["prompt"]
        and "Question: What is the causal mask?" in seen["prompt"]
    )
    assert "[made-up-claim]" not in out["text"] and "[attn-causal-mask]" in out["text"]
    assert out["cited"] == ["attn-causal-mask"] and out["removed_citations"] == ["made-up-claim"]
    assert out["grounded"] is False  # an invented citation was removed, so it is flagged
    assert [c["id"] for c in out["claims"]] == ["attn-causal-mask"]
    assert (
        out["cost_usd"] == pytest.approx((200 * 1.0 + 20 * 5.0) / 1e6)
        and out["cost_usd"] <= out["max_cost_usd"]
    )
    with Session(engine) as session:
        assert len(session.exec(select(AIUsage)).all()) == 1


def test_paid_path_needs_confirmation_and_costs_nothing_off_topic(client, engine, monkeypatch):
    _enable(monkeypatch)
    called = []
    monkeypatch.setattr(providers, "generate_with_usage", lambda *a, **k: called.append(1))
    no_confirm = {**LLM, "confirm_paid": False}
    r = client.post(
        "/api/tutor/ask/llm", json={"question": "What is the causal mask?", **no_confirm}, headers=H
    )
    assert r.status_code == 403 and r.json()["detail"]["code"] == "not_confirmed"
    off = client.post(
        "/api/tutor/ask/llm", json={"question": "Who won the world cup?", **LLM}, headers=H
    ).json()
    assert off["covered"] is False and off["cost_usd"] == 0.0 and not called
    with Session(engine) as session:
        assert session.exec(select(AIUsage)).all() == []


def test_estimate_is_free_and_off_topic_estimates_zero(client, engine, monkeypatch):
    _enable(monkeypatch)
    called = []
    monkeypatch.setattr(providers, "generate_with_usage", lambda *a, **k: called.append(1))
    ok = client.post("/api/tutor/ask/estimate", json={"question": "What is the causal mask?", **LLM}).json()
    assert ok["covered"] and 0 < ok["max_cost_usd"] < 0.01
    off = client.post("/api/tutor/ask/estimate", json={"question": "Tell me a joke", **LLM}).json()
    assert off["covered"] is False and off["max_cost_usd"] == 0.0
    assert not called
    bad = client.post(
        "/api/tutor/ask/estimate", json={"question": "hello there", "provider": "x", "model": "y"}
    )
    assert bad.status_code == 404


def test_citation_checker_keeps_only_claims_that_were_in_the_prompt():
    out = tprompt.check_citations("A [a-1] and B [zz-9].", ["a-1"])
    assert out["cited"] == ["a-1"] and out["removed_citations"] == ["zz-9"] and "[zz-9]" not in out["text"]
    assert re.search(r"\[a-1\]", out["text"])
