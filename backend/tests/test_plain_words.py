"""The plain-words voice must stay a faithful, beginner-safe retelling of the technical lesson.

* it keeps the same stages, claims and numbers as the technical voice;
* no technical word is used before the stage that introduces it ("Words you will hear");
* every number it quotes also appears in the technical text.
"""

import re

import pytest

from app.content.loader import content
from app.content.schema import validate_lesson

# Technical words a beginner has not met yet, per lesson. Each must be introduced (as a term, in a stage's
# "Words you will hear") before any plain text uses it. Everyday words are not listed here.
JARGON: dict[str, list[str]] = {
    "agents": [
        r"schema",
        r"\bJSON\b",
        r"\btokens?\b",
        r"\bcontext\b",
        r"\bAPI\b",
        r"prompt injection",
        r"language model",
        r"\bLLM\b",
        r"validat",
        r"tool calls?",
        r"human in the loop",
        r"step limit",
    ],
    "rag-pipeline": [
        r"\bchunk",
        r"\bvectors?\b",
        r"embedd?",
        r"\bindex\b(?! cards?)",
        r"retriev(?!al-augmented)",
        r"\bprompt",
        r"top-k",
        r"BM25",
        r"\bdense\b",
        r"hybrid",
        r"language model",
        r"\bLLM\b",
        r"hallucinat",
        r"cosine",
        r"TF-IDF",
        r"hash",
        r"lexical",
        r"neural",
        r"\bgenerator\b",
        r"context budget",
        r"\btokens?\b",
        r"\boverlap",
    ],
    "attention": [
        r"\bvectors?\b",
        r"\bquer(?:y|ies)\b",
        r"\bkeys?\b",
        r"\bvalues?\b",
        r"\bheads?\b",
        r"softmax",
        r"\bmask\b",
        r"\bcausal\b",
        r"matri(?:x|ces)",
        r"dot product",
        r"\btokens?\b",
        r"residual",
        r"feed-forward",
        r"normalis",
        r"embedding",
        r"transformer",
        r"self-attention",
        r"position pattern",
        r"weighted sum",
    ],
    "tokenization": [
        r"corpus",
        r"\bBPE\b",
        r"\bbytes?\b",
        r"\bmerges?\b",
        r"vocabulary",
        r"alphabet",
        r"pre-tokenizer",
        r"(?<!pair )\bencod(?:er|ing|e)\b",
        r"\bdecod(?:er|ing|e)\b",
        r"\[UNK\]",
        r"\bASCII\b",
        r"round trip",
    ],
    "embeddings": [
        r"embedding",
        r"vector",
        r"token",
        r"cosine",
        r"dot product",
        r"euclidean",
        r"pooling",
        r"normali[sz]",
        r"\bPCA\b",
        r"\[CLS\]",
        r"\[SEP\]",
        r"encoder",
        r"\blayers?\b",
        r"lexical",
        r"neural",
        r"\bBGE\b",
        r"dimension",
        r"semantic",
        r"transformer",
        r"\bquery\b",
        r"cluster",
    ],
}


def _lessons():
    registry, plain = content("plain")
    _, technical = content("technical")
    return registry, plain, technical


def _plain_ids():
    _, plain, technical = _lessons()
    return [lid for lid in plain if plain[lid].components[0].technical_name or plain[lid].ui]


def _stage_text(component) -> str:
    ex = component.explain
    parts = [
        component.label,
        component.subtitle or "",
        component.short,
        component.detail,
        component.breaks_if_removed or "",
        " ".join(component.inputs),
        " ".join(component.outputs),
    ]
    if ex:
        parts += [
            ex.what,
            ex.why,
            ex.analogy,
            " ".join(ex.happens),
            ex.goes_to,
            ex.misconfigured,
            ex.story or "",
            ex.thread or "",
            ex.example.input,
            " ".join(ex.example.steps),
            ex.example.output,
        ]
        if ex.check:
            parts += [ex.check.question, ex.check.answer]
        parts += [t.meaning for t in ex.terms]
    return " ".join(parts)


def _strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            yield from _strings(v)
    elif isinstance(obj, str):
        yield obj


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?", text.replace(",", "")))


@pytest.mark.parametrize("lid", _plain_ids())
def test_plain_voice_keeps_the_lesson_intact(lid):
    registry, plain, technical = _lessons()
    p, t = plain[lid], technical[lid]
    assert validate_lesson(p, registry) == []
    assert [c.id for c in p.components] == [c.id for c in t.components]
    assert [c.claims for c in p.components] == [c.claims for c in t.components]
    assert p.claims == t.claims
    assert [(c.source, c.target) for c in p.connections] == [(c.source, c.target) for c in t.connections]
    assert [ch.id for ch in p.challenges] == [ch.id for ch in t.challenges]
    assert [ch.checks for ch in p.challenges] == [ch.checks for ch in t.challenges]
    assert all(
        c.technical_name == tc.label
        for c, tc in zip(p.components, t.components, strict=True)
        if c.label != tc.label
    )
    assert all(c.explain and c.explain.terms for c in p.components), (
        "every stage lists the words it introduces"
    )


@pytest.mark.parametrize("lid", _plain_ids())
def test_plain_voice_uses_no_word_before_it_is_introduced(lid):
    assert lid in JARGON, f"list the technical words for {lid} in JARGON"
    _, plain, _ = _lessons()
    p = plain[lid]
    introduced_at: dict[str, int] = {}
    for i, comp in enumerate(p.components):
        for term in comp.explain.terms:
            introduced_at.setdefault(term.word.lower(), i)

    def known_by(index: int, pattern: str) -> bool:
        return any(i <= index and re.search(pattern, w, re.IGNORECASE) for w, i in introduced_at.items())

    problems: list[str] = []

    def check(where: str, text: str, index: int):
        for pattern in JARGON[lid]:
            if re.search(pattern, text, re.IGNORECASE) and not known_by(index, pattern):
                problems.append(f"{where} uses '{pattern}' before it is introduced")

    last = len(p.components) - 1
    check("summary", p.summary, -1)
    check("objectives", " ".join(p.objectives), last)  # objectives are what you will be able to do by the end
    check(
        "big picture", f"{p.big_picture.story} {p.big_picture.example.note} {p.big_picture.analogy.title}", -1
    )
    mapping = " ".join(f"{m.part} {m.becomes}" for m in p.big_picture.analogy.mapping)
    check("analogy", mapping, -1)
    for i, comp in enumerate(p.components):
        check(f"stage '{comp.label}'", _stage_text(comp), i)
    ids = [c.id for c in p.components]
    for conn in p.connections:
        check(
            f"hand-off {conn.source}->{conn.target}",
            conn.explain or "",
            min(ids.index(conn.source), ids.index(conn.target)),
        )
    for step in p.tour:
        check(f"tour '{step.title}'", f"{step.title} {step.body}", ids.index(step.component))
    assert not problems, f"{lid}:\n" + "\n".join(problems)


@pytest.mark.parametrize("lid", _plain_ids())
def test_plain_voice_quotes_only_numbers_the_technical_text_has(lid):
    _, plain, technical = _lessons()
    known = _numbers(" ".join(_strings(technical[lid].model_dump(mode="json"))))
    seen = _numbers(" ".join(_strings(plain[lid].model_dump(mode="json"))))
    unknown = {n for n in seen - known if not (n.isdigit() and int(n) <= 12)}
    assert not unknown, (
        f"{lid}: numbers in the plain text that the technical text never mentions: {sorted(unknown)}"
    )


@pytest.mark.parametrize("lid", _plain_ids())
def test_plain_sentences_are_short(lid):
    _, plain, _ = _lessons()
    p = plain[lid]
    texts = [p.big_picture.story] + [
        s for c in p.components if c.explain for s in (c.explain.story or "", c.explain.thread or "")
    ]
    long = [s for t in texts for s in re.split(r"(?<=[.!?])\s+", t) if len(s.split()) > 45]
    assert not long, f"{lid}: sentences over 45 words: {[s[:60] for s in long]}"
