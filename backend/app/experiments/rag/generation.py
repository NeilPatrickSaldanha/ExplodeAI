"""Prompt assembly and the offline answer step.

`assemble_prompt` builds the exact text a generator model would receive:
retrieved chunks first (wrapped in XML-style tags with their source id), then
the instructions and the question. Chunks are added in rank order until the
context budget (in words) would be exceeded; anything dropped is reported.

`extractive_answer` is NOT a language model. It is a transparent baseline that
picks the retrieved sentences sharing the most query terms and cites them.
It shows what "grounded in retrieved context" means without a paid API call,
and it fails in visible, explainable ways when retrieval fails.
"""

from dataclasses import dataclass, field

from app.experiments.rag.chunking import Chunk
from app.experiments.rag.text import sentence_spans, terms, word_count

INSTRUCTIONS = (
    "Answer the question using only the documents above. "
    "Cite the source id of each fact in square brackets. "
    "If the documents do not contain the answer, say that you cannot find it."
)


@dataclass
class AssembledPrompt:
    text: str
    included: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)
    context_words: int = 0


def assemble_prompt(question: str, ranked: list[Chunk], budget_words: int) -> AssembledPrompt:
    parts: list[str] = []
    out = AssembledPrompt(text="")
    for i, chunk in enumerate(ranked, start=1):
        if out.context_words + chunk.words > budget_words:
            out.dropped.append(chunk.id)
            continue
        out.context_words += chunk.words
        out.included.append(chunk.id)
        parts.append(
            f'<document index="{i}">\n<source>{chunk.id}</source>\n'
            f"<document_content>{chunk.text}</document_content>\n</document>"
        )
    docs = "<documents>\n" + "\n".join(parts) + "\n</documents>"
    out.text = f"{docs}\n\n{INSTRUCTIONS}\n\nQuestion: {question}"
    return out


@dataclass(frozen=True)
class AnswerSentence:
    text: str
    source: str
    overlap: int


NO_ANSWER = "The retrieved context does not contain an answer to this question."


def extractive_answer(
    question: str, chunks: list[Chunk], max_sentences: int = 2
) -> list[AnswerSentence]:
    q = set(terms(question))
    candidates: list[AnswerSentence] = []
    for chunk in chunks:
        for s, e in sentence_spans(chunk.text):
            sent = chunk.text[s:e].strip()
            overlap = len(q & set(terms(sent)))
            if overlap and word_count(sent) >= 3:
                candidates.append(AnswerSentence(sent, chunk.id, overlap))
    candidates.sort(key=lambda a: -a.overlap)
    picked: list[AnswerSentence] = []
    for c in candidates:
        if all(c.text != p.text for p in picked):
            picked.append(c)
        if len(picked) == max_sentences:
            break
    return picked
