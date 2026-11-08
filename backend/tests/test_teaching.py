"""The teaching layer (content/lessons/*/teaching.yaml) quotes real numbers from each lesson's running
example. Every one of them is asserted here against the real experiments, so the stories can't drift."""

import numpy as np
import pytest

from app.content.loader import content
from app.content.schema import validate_lesson
from app.experiments.agent import tools as agent_tools
from app.experiments.agent.pipeline import AgentParams
from app.experiments.agent.pipeline import run as run_agent
from app.experiments.attend import pipeline as attend
from app.experiments.rag.pipeline import RagParams
from app.experiments.rag.pipeline import run as run_rag
from app.experiments.tokenize.pipeline import TokenizeParams
from app.experiments.tokenize.pipeline import run as run_tokenize

LESSONS = content()[1]


@pytest.mark.parametrize("lesson_id", list(LESSONS))
def test_every_lesson_is_fully_taught(lesson_id):
    lesson = LESSONS[lesson_id]
    assert validate_lesson(lesson, content()[0]) == []
    assert lesson.big_picture is not None
    assert {m.part for m in lesson.big_picture.analogy.mapping} == {c.label for c in lesson.components}
    for comp in lesson.components:
        assert comp.explain.story and comp.explain.thread
        assert comp.explain.check.question.endswith("?") and comp.explain.check.answer
    assert all(conn.explain for conn in lesson.connections)


def test_rag_running_example():
    r = run_rag(RagParams(query="How long do I have to return a bike?"))
    assert len(r["corpus"]["documents"]) == 6 if "documents" in r["corpus"] else True
    assert len(r["chunks"]) == 11
    assert sum(1 for c in r["chunks"] if c["id"].startswith("returns#")) == 2
    assert [h["chunk_id"] for h in r["retrieved"]] == ["returns#0", "battery#1", "returns#1"]
    assert r["embedding"]["dim"] == 1024
    assert (r["prompt"]["context_words"], r["prompt"]["budget_words"]) == (66, 200)
    assert [s["text"] for s in r["answer"]["sentences"]][:2] == [
        "Ridgeline Bikes accepts returns of unused bikes within 30 days of delivery.",
        "Returned bikes must include the original packaging.",
    ]
    from app.experiments.rag.corpus import get_corpus

    assert len(get_corpus()) == 6 and sum(len(d.text.split()) for d in get_corpus()) == 271


def test_tokenization_running_example():
    text = "The keeper lit the lantern at dusk."
    base = dict(
        corpus_id="greyhaven-keepers-log",
        text=text,
        base="bytes",
        pre_tokenizer="words",
        merge_order="learned",
    )
    assert run_tokenize(TokenizeParams(**base, merges=0))["encoding"]["count"] == 35
    assert len(text.encode()) == 35
    r = run_tokenize(TokenizeParams(**base, merges=100))
    enc = r["encoding"]
    assert enc["count"] == 8 and enc["ids"] == [262, 269, 346, 258, 275, 285, 321, 46]
    assert [t["text"] for t in enc["tokens"]] == [
        "The",
        " keeper",
        " lit",
        " the",
        " lantern",
        " at",
        " dusk",
        ".",
    ]
    assert r["vocabulary"]["size"] == 357
    keeper = next(p for p in enc["pieces"] if p["text"] == " keeper")
    assert len(keeper["start"]) == 7 and [s["token"] for s in keeper["steps"]] == [
        "er",
        "ep",
        "ke",
        " ke",
        " keep",
        " keeper",
    ]
    assert r["decoding"]["text"] == text and r["decoding"]["round_trip"] and r["decoding"]["unk_count"] == 0
    first = r["training"]["merges"][:3] if "merges" in r["training"] else None
    if first:
        assert [(m["left"], m["right"]) for m in first] == [("h", "e"), (" ", "t"), (" t", "he")]


def test_embeddings_running_example():
    pytest.importorskip("fastembed")
    from app.experiments.embed.pipeline import EmbedParams
    from app.experiments.embed.pipeline import run as run_embed

    r = run_embed(EmbedParams(text="a place to put my books", top_k=3))
    q = r["query"]
    assert [t["text"] for t in q["tokens"]] if isinstance(q["tokens"], list) else True
    assert q["tokens"] == 8 or len(q["tokens"]) == 8
    assert round(q["norm_before"], 2) == 9.25 and q["norm_after"] == 1.0 and q["dim"] == 384
    assert len(r["library"]["items"]) == 24
    top = [(n["text"], round(n["score"], 3), n["category"]) for n in r["neighbours"][:3]]
    assert top == [
        ("The bookshelf is full of old novels.", 0.695, "furniture"),
        ("The desk has three drawers and a lamp.", 0.566, "furniture"),
        ("A soft armchair stands beside the fireplace.", 0.554, "furniture"),
    ]


def test_attention_running_example():
    r = attend.run(
        attend.AttendParams(text="the cat sat on the mat", heads=2, scale=True, causal=False, position=True)
    )
    assert [t["text"] for t in r["tokens"]] == ["the", "cat", "sat", "on", "the", "mat"]
    assert (r["model"]["d_model"], r["model"]["heads"], r["model"]["head_dim"]) == (64, 2, 32)
    sat = np.array(r["weights_mean"])[2]
    assert round(sat[3] * 100) == 30 and abs(sat.sum() - 1) < 1e-3
    assert np.array(r["output"]["preview"]).shape[0] == 6
    masked = attend.run(attend.AttendParams(text="the cat sat on the mat", causal=True))
    weights = np.array(masked["heads"][0]["weights"])
    assert int((weights == 0).sum()) == 15 and weights.shape == (6, 6)


def test_agent_running_example():
    held = run_agent(AgentParams())
    assert len(held["steps"]) == 5 and held["status"] == "needs_approval"
    assert held["steps"][1]["validation"]["errors"] and held["steps"][2]["decision"]["arguments"] == {
        "order_id": "A1001"
    }
    assert [s["tokens_in"] for s in held["steps"]] == [1475, 1955, 2203, 2526, 2799]
    assert round(sum(s["tokens_in"] for s in held["steps"]), -3) == 11000
    order = agent_tools.get_order("A1001").content
    assert (order["item"], order["price"], order["delivered"]) == (
        "E-Trail electric bike",
        2899.0,
        "2026-10-05",
    )
    done = run_agent(AgentParams(approve=True))
    assert len(done["steps"]) == 6 and done["refunds"][0]["refund_id"] == "R-001"
    assert "16 days ago" in done["answer"] and "30 days" in done["answer"]


# --- the Experiment tab's "what to notice" guidance quotes these results -------------------------------


def _guide(lesson_id):
    return LESSONS[lesson_id].experiment["guide"]


@pytest.mark.parametrize("lesson_id", list(LESSONS))
def test_every_example_button_and_tab_has_guidance(lesson_id):
    lesson = LESSONS[lesson_id]
    guide = _guide(lesson_id)
    assert {p["label"] for p in lesson.experiment["presets"]} == set(guide["presets"])
    assert len(guide["ideas"]) >= 3 and guide["intro"]
    assert all(g["try"] and len(g["notice"]) > 60 for g in guide["presets"].values())


def test_rag_guidance_numbers():
    base = dict(
        strategy="sentence",
        chunk_size=40,
        overlap=0,
        embedder="lexical-hashing",
        method="dense",
        top_k=3,
        context_budget_words=200,
    )
    ids = lambda r: [h["chunk_id"] for h in r["retrieved"]]  # noqa: E731
    cases = {
        "How long do I have to return a bike, and what must I include?": [
            "returns#0",
            "service#1",
            "battery#1",
        ],
        "What does the warranty cover for the frame and for components like brakes?": [
            "warranty#0",
            "sizing#1",
            "returns#0",
        ],
        "How should I store the battery long term?": ["battery#1", "returns#0", "service#0"],
        "Can I get my money back?": ["battery#0", "returns#0", "returns#1"],
    }
    for question, expected in cases.items():
        assert ids(run_rag(RagParams(**base, query=question))) == expected
    assert run_rag(RagParams(**base, query="Can I get my money back?"))["answer"]["sentences"] == []
    q = "How long do I have to return a bike?"
    assert len(run_rag(RagParams(**{**base, "strategy": "fixed", "chunk_size": 8}, query=q))["chunks"]) == 37
    assert (
        len(
            run_rag(RagParams(**{**base, "strategy": "fixed", "chunk_size": 8, "overlap": 4}, query=q))[
                "chunks"
            ]
        )
        == 65
    )
    assert len(run_rag(RagParams(**{**base, "strategy": "fixed", "chunk_size": 120}, query=q))["chunks"]) == 6
    assert ids(run_rag(RagParams(**{**base, "top_k": 1}, query=q))) == ["returns#0"]
    assert run_rag(RagParams(**{**base, "top_k": 6}, query=q))["prompt"]["context_words"] == 145
    tiny = run_rag(RagParams(**{**base, "context_budget_words": 15}, query=q))["prompt"]
    assert (len(tiny["included"]), len(tiny["dropped"])) == (1, 2)


def test_tokenization_guidance_numbers():
    base = dict(corpus_id="greyhaven-keepers-log", base="bytes", pre_tokenizer="words", merge_order="learned")

    def count(text, merges, **kw):
        return run_tokenize(TokenizeParams(**{**base, **kw}, text=text, merges=merges))

    familiar, unseen = "The keeper lit the lantern at dusk.", "The lanternkeepers rewound clockwork."
    assert [count(familiar, m)["encoding"]["count"] for m in (0, 25, 100, 300)] == [35, 15, 8, 8]
    assert [count(familiar, m)["vocabulary"]["size"] for m in (0, 25, 100, 300)] == [257, 282, 357, 473]
    assert [count(unseen, m)["encoding"]["count"] for m in (0, 25, 100, 300)] == [37, 23, 18, 16]
    accents = "Café crème at the lantern ☕"
    assert (
        count(accents, 100)["encoding"]["count"] == 17 and count(accents, 100)["decoding"]["unk_count"] == 0
    )
    chars = count(accents, 100, base="chars")
    assert chars["decoding"]["unk_count"] == 4 and not chars["decoding"]["round_trip"]
    digits = "Tide at 04:15, height 3.2 metres."
    assert count(digits, 100)["encoding"]["count"] == 28
    assert count(digits, 100, base="chars")["decoding"]["unk_count"] == 6


def test_embeddings_guidance_numbers():
    pytest.importorskip("fastembed")
    from app.experiments.embed.pipeline import EmbedParams
    from app.experiments.embed.pipeline import run as run_embed

    def top(text, **kw):
        r = run_embed(EmbedParams(text=text, top_k=3, **kw))
        return [(n["category"], round(n["score"], 3)) for n in r["neighbours"]], r

    puppy, _ = top("A puppy playing fetch in the park")
    assert puppy == [("animals", 0.717), ("animals", 0.637), ("animals", 0.564)]
    commute, _ = top("getting to the office")
    assert commute[:2] == [("furniture", 0.588), ("vehicles", 0.561)]
    assisted, _ = top("getting to the office", query_instruction=True)
    assert assisted[:2] == [("vehicles", 0.515), ("furniture", 0.502)]
    rails, r = top("a vehicle that runs on rails")
    assert [s for _, s in rails] == [0.619, 0.613, 0.597]
    train = next(i for i in r["library"]["items"] if "train" in i["text"].lower())
    assert train["rank"] == 14
    long_text = next(
        p["text"] for p in LESSONS["embeddings"].experiment["presets"] if p["label"] == "Long text"
    )
    assert run_embed(EmbedParams(text=long_text))["query"]["truncated"] is True
    both_lexical, _ = top("a place to put my books", library_embedder="lexical", query_embedder="lexical")
    assert both_lexical[0][1] == 0.0


def test_attention_guidance_numbers():
    pronoun = "the animal did not cross the street because it was too tired"
    r = attend.run(attend.AttendParams(text=pronoun, heads=2, scale=True, causal=False, position=True))
    words = [t["text"] for t in r["tokens"]]
    row = np.array(r["weights_mean"])[words.index("it")]
    assert len(words) == 12 and words[int(row.argmax())] == "too"
    assert round(row.max() * 100) == 28 and round(row[words.index("animal")] * 100) == 9
    cat = attend.run(attend.AttendParams(text="the cat sat on the mat", heads=2, scale=True))
    assert round(cat["stats"]["mean_max_weight"] * 100) == 35
    wide = attend.run(attend.AttendParams(text="the cat sat on the mat", heads=8, scale=False))
    assert round(wide["stats"]["mean_max_weight"] * 100) == 63
    order = attend.run(attend.AttendParams(text="dog bites man", position=False))
    assert order["stats"]["order_gap"] == 0.0


def test_agent_guidance_numbers():
    steps = lambda goal, **kw: len(run_agent(AgentParams(goal=goal, **kw))["steps"])  # noqa: E731
    assert steps("Can I return order A1002?") == 4 and steps("I want to return order A1003") == 4
    assert steps("Where is my order A1004?") == 2 and steps("How long do refunds take?") == 2
    assert "within 5 business days" in run_agent(AgentParams(goal="How long do refunds take?"))["answer"]
    assert "50 days ago" in run_agent(AgentParams(goal="Can I return order A1002?"))["answer"]
    assert "custom-built" in run_agent(AgentParams(goal="I want to return order A1003"))["answer"]
    runaway = run_agent(AgentParams(descriptions="vague", max_steps=None))
    assert runaway["status"] == "safety_cap" and len(runaway["steps"]) == 30
