"""The paid "polish" path: the server builds the prompt from retrieved lesson passages only."""

import re

from app.tutor.search import Scored

INSTRUCTIONS = (
    "You are the ExplodeAI tutor. Answer the learner's question using ONLY the numbered passages below. "
    "If the passages do not answer it, say that the lessons do not cover it. Do not use outside knowledge. "
    "Write at most four short sentences in plain language for a beginner. After each fact, cite the claim "
    "ids that support it in square brackets, like [attn-causal-mask]. Passages marked ANALOGY are teaching "
    'aids, not facts: say "think of it like..." if you use one.'
)


def build_prompt(question: str, hits: list[Scored]) -> tuple[str, list[str]]:
    """Return the prompt and the claim ids the model is allowed to cite."""
    allowed: list[str] = []
    lines = []
    for i, h in enumerate(hits, 1):
        for c in h.passage.claim_ids:
            if c not in allowed:
                allowed.append(c)
        tag = "ANALOGY" if h.passage.teaching_aid else h.passage.kind.upper()
        ids = ", ".join(h.passage.claim_ids) or "none"
        lines.append(f"[{i}] ({tag}; claims: {ids}) {h.passage.text}")
    prompt = f"{INSTRUCTIONS}\n\nPassages:\n" + "\n".join(lines) + f"\n\nQuestion: {question}\nAnswer:"
    return prompt, allowed


_CITE = re.compile(r"\[([a-z0-9][a-z0-9-]*)\]")


def check_citations(text: str, allowed: list[str]) -> dict:
    """Keep only citations to claims that were actually in the prompt."""
    cited = _CITE.findall(text)
    ok = [c for c in dict.fromkeys(cited) if c in allowed]
    bad = [c for c in dict.fromkeys(cited) if c not in allowed]
    cleaned = _CITE.sub(lambda m: m.group(0) if m.group(1) in allowed else "", text)
    return {
        "text": re.sub(r"\s{2,}", " ", cleaned).strip(),
        "cited": ok,
        "removed_citations": bad,
        "grounded": bool(ok) and not bad,
    }
