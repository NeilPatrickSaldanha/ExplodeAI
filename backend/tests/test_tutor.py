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
        "ONLY the passages below" in seen["prompt"] and "Question: What is the causal mask?" in seen["prompt"]
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


# ----------------------------------------------- conversation: small talk, memory, plain words
def _turn(q, stage="embed_pos", lesson="attention", text="Each word becomes a vector."):
    return {"question": q, "answer_text": text, "lesson_id": lesson, "stage_id": stage}


def test_small_talk_is_friendly_free_and_not_a_refusal(client):
    for q in ("hi there", "Hello!", "hey", "good morning"):
        r = ask(client, q).json()
        assert (
            r["type"] == "chat"
            and "tutor" in r["message"].lower()
            and r["sources"] == []
            and r["claims"] == []
        )
    thanks = ask(client, "thanks!").json()
    assert thanks["type"] == "chat" and "quiz" in thanks["message"].lower()


def test_answers_lead_with_the_stages_plain_words_taken_from_its_explanation(client):
    _, lessons = content()
    comp = next(c for c in lessons["attention"].components if c.id == "embed_pos")
    r = ask(
        client, "wait so what does vectors + position do?", lesson_id="attention", stage_id="embed_pos"
    ).json()
    assert r["type"] == "answer" and r["plain"]["stage_id"] == "embed_pos"
    e = comp.explain
    assert r["plain"]["what"] == e.what and r["plain"]["analogy"] == e.analogy
    assert r["plain"]["example"] == e.example.model_dump()
    assert r["sentences"] and r["claims"] and r["sources"], "the verified quotes follow the plain words"


def test_follow_ups_use_the_conversation_and_stay_on_the_stage(client):
    _, lessons = content()
    e = next(c for c in lessons["attention"].components if c.id == "embed_pos").explain
    hist = [_turn("what does vectors + position do?")]
    # An open stage elsewhere must not hijack the follow-up.
    r = ask(
        client, "can you frame it in easier words", lesson_id="attention", stage_id="softmax", history=hist
    ).json()
    assert r["type"] == "plain" and r["plain"]["stage_id"] == "embed_pos" and r["plain"]["mode"] == "simplify"
    assert r["plain"]["what"] == e.what and r["plain"]["example"] and r["plain"]["analogy"] == e.analogy
    ex = ask(client, "give me an example", lesson_id="attention", history=hist).json()
    assert ex["plain"]["mode"] == "example" and ex["plain"]["example"]["steps"] == e.example.steps
    more = ask(client, "tell me more", lesson_id="attention", history=hist).json()
    assert more["plain"]["mode"] == "more" and more["plain"]["misconfigured"] == e.misconfigured
    why = ask(client, "why does that matter?", lesson_id="attention", history=hist).json()
    assert why["plain"]["mode"] == "why" and why["plain"]["why"] == e.why
    assert all(c["id"] in {c.id for c in lessons["attention"].claims} for c in r["claims"])


def test_a_follow_up_with_nothing_to_refer_to_asks_which_part(client):
    r = ask(client, "can you explain it simpler").json()
    assert r["type"] == "chat" and "Which part" in r["message"]
    # With a stage open and no history, the open stage is what "it" means.
    r = ask(client, "explain it simpler", lesson_id="attention", stage_id="softmax").json()
    assert r["type"] == "plain" and r["plain"]["stage_id"] == "softmax"


def test_a_short_pronoun_question_is_searched_together_with_the_previous_one(client):
    hist = [_turn("what is the causal mask?", stage="mask", text="It hides later words.")]
    # "how does it work?" has no topic of its own; with the history it is about the mask.
    r = ask(client, "how does it work?", lesson_id="attention", history=hist).json()
    assert r["covered"] and any(s["stage_id"] == "mask" for s in r["sentences"])
    alone = ask(client, "how does it work?", lesson_id="attention").json()
    assert (
        not any(s["stage_id"] == "mask" for s in alone["sentences"] or [{"stage_id": None}])
        or not alone["covered"]
    )
    # And "why is it needed?" is a plain-words follow-up about the same stage.
    why = ask(client, "why is it needed?", lesson_id="attention", history=hist).json()
    assert why["type"] == "plain" and why["plain"]["stage_id"] == "mask"


def test_history_is_bounded(client):
    too_many = [_turn(f"q{i}") for i in range(7)]
    assert ask(client, "what is attention?", history=too_many).status_code == 422
    assert (
        ask(client, "what is attention?", history=[{**_turn("q"), "answer_text": "x" * 901}]).status_code
        == 422
    )


def test_phrasing_points_at_the_kind_of_passage_that_answers_it():
    from app.tutor import intent

    assert intent.kind_preference("what happens if the mask is removed?") == {"breaks"}
    assert intent.kind_preference("why is the softmax needed") == {"why"}
    assert "misconfigured" in intent.kind_preference("what can go wrong here")
    assert intent.kind_preference("what does vectors + position do?") == {"what", "claim"}
    assert (
        intent.classify("hi there") == "greeting" and intent.classify("explain it like I'm 5") == "simplify"
    )
    assert intent.classify("what is the causal mask?") is None


def test_ai_mode_prompt_carries_the_conversation_and_asks_for_plain_language(client, monkeypatch):
    _enable(monkeypatch)
    seen = {}

    def fake(settings_, provider, model, prompt, max_tokens):
        seen["prompt"] = prompt
        return providers.Generation("Think of it like a seat number [attn-position-needed].", 120, 15)

    monkeypatch.setattr(providers, "generate_with_usage", fake)
    body = {
        "question": "can you explain that in easier words?",
        "lesson_id": "attention",
        "history": [_turn("what does vectors + position do?", text="It adds a position pattern.")],
        **LLM,
    }
    r = client.post("/api/tutor/ask/llm", json=body, headers=H)
    assert r.status_code == 200, r.text
    p = seen["prompt"]
    assert "friendly teacher" in p and "everyday sentences" in p and "plain words first" in p
    assert "Earlier in this conversation" in p and "Learner: what does vectors + position do?" in p
    assert "Tutor: It adds a position pattern." in p
    assert "more simply" in p, "the intent is passed on"
    assert "Position information has to be added" in p or "position" in p.lower()
    assert r.json()["cited"] == ["attn-position-needed"]


def test_ai_mode_small_talk_is_free_and_makes_no_provider_call(client, engine, monkeypatch):
    _enable(monkeypatch)
    called = []
    monkeypatch.setattr(providers, "generate_with_usage", lambda *a, **k: called.append(1))
    out = client.post("/api/tutor/ask/llm", json={"question": "hi there", **LLM}, headers=H).json()
    assert out["type"] == "chat" and out["cost_usd"] == 0.0 and out["is_llm"] is False and not called
    with Session(engine) as session:
        assert session.exec(select(AIUsage)).all() == []


def test_passage_numbers_are_not_citations_and_are_removed_from_the_text():
    """Seen in a real call: the model wrote "[3, 4]" meaning passages 3 and 4."""
    out = tprompt.check_citations("It adds a pattern to each word [3, 4]. That keeps order [a-1].", ["a-1"])
    assert "[3, 4]" not in out["text"] and "[a-1]" in out["text"]
    assert out["cited"] == ["a-1"] and out["removed_citations"] == ["[3, 4]"] and out["grounded"] is False
    assert " ." not in out["text"], "no stray space left before punctuation"
    none = tprompt.check_citations("Think of it like a card with a stamp.", ["a-1"])
    assert none["has_citations"] is False and none["cited"] == [] and none["grounded"] is False


def test_the_prompt_labels_passages_so_they_cannot_be_mistaken_for_citations():
    from app.tutor.prompt import INSTRUCTIONS, build_prompt

    registry, lessons = content()
    hits = TutorIndex(build_passages(lessons, registry)).search("what is the causal mask?")[0]
    prompt, allowed = build_prompt("what is the causal mask?", hits)
    assert "Passage 1 (" in prompt and "\n[1]" not in prompt
    assert "claim ids only, never passage numbers" in INSTRUCTIONS.lower().replace("cite ", "")
    assert "attn-causal-mask" in allowed


# ------------------------------------------------------------- questions about the course itself
def test_questions_about_the_course_are_answered_not_refused(client):
    _, lessons = content()
    for q in (
        "What are all four lessons?",
        "what can you teach me?",
        "list the topics",
        "what is explodeai?",
    ):
        r = ask(client, q).json()
        assert r["type"] == "overview", q
        assert [x["number"] for x in r["lessons"]] == [1, 2, 3, 4]
        for card in r["lessons"]:
            lesson = lessons[card["lesson_id"]]
            assert card["summary"] == lesson.summary and card["title"] == lesson.title
            assert card["stages"] == [c.label for c in lesson.components]
        assert "don't cover" not in str(r["message"])


def test_asking_about_one_lesson_shows_its_objectives(client):
    _, lessons = content()
    for n, lesson_id in ((1, "rag-pipeline"), (3, "embeddings"), (4, "attention")):
        r = ask(client, f"what's in lesson {n}?").json()
        assert r["type"] == "overview" and r["focus_number"] == n and len(r["lessons"]) == 1
        assert r["lessons"][0]["objectives"] == lessons[lesson_id].objectives
    two = ask(client, "lesson two summary").json()
    assert two["lessons"][0]["lesson_id"] == "tokenization"


def test_how_do_i_use_this_explains_the_modes(client):
    r = ask(client, "how do I use this?").json()
    assert r["type"] == "chat" and all(
        w in r["message"] for w in ("Explore", "Tour", "Experiment", "Break & fix", "Rebuild")
    )
    assert "How to use" in r["message"]


def test_topic_questions_are_not_mistaken_for_course_questions():
    from app.tutor import intent

    for q in (
        "What is the causal mask?",
        "what is attention?",
        "why do we split documents into chunks?",
        "What does an embedding model do?",
        "what is BM25?",
    ):
        assert intent.classify(q) is None, q
    assert (
        intent.lesson_number("what's in lesson three?") == 3
        and intent.lesson_number("no number here") is None
    )


def test_course_questions_are_free_in_ai_mode_too(client, engine, monkeypatch):
    _enable(monkeypatch)
    called = []
    monkeypatch.setattr(providers, "generate_with_usage", lambda *a, **k: called.append(1))
    for q in ("What are all four lessons?", "how do I use this?", "what's in lesson 4?"):
        out = client.post("/api/tutor/ask/llm", json={"question": q, **LLM}, headers=H).json()
        assert out["is_llm"] is False and out["cost_usd"] == 0.0 and out["covered"], q
    assert not called
    with Session(engine) as session:
        assert session.exec(select(AIUsage)).all() == []
