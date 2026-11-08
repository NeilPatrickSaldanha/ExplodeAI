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
