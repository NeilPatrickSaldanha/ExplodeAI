"""Text utilities shared by the RAG experiment stages.

All counts in the experiment are in *words* (whitespace-delimited), not model
tokens. Real tokenizers split text differently per model; the lesson labels
every budget as "words" so it never implies a specific tokenizer.
"""

import re
from dataclasses import dataclass

_WORD = re.compile(r"\S+")
_TERM = re.compile(r"[a-z0-9]+(?:[.'][a-z0-9]+)*")
_SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

# A tiny stopword list. Kept short and explicit so learners can read it.
STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does", "for", "from",
    "has", "have", "how", "i", "if", "in", "is", "it", "its", "like", "my", "of", "on",
    "or", "should", "the", "this", "to", "was", "what", "when", "where", "which", "who",
    "will", "with", "you", "your",
})


def s_stem(word: str) -> str:
    """Harman's (1991) "S" stemmer: strips common English plural endings only."""
    if len(word) <= 3:
        return word
    if word.endswith("ies") and not word.endswith(("eies", "aies")):
        return word[:-3] + "y"
    if word.endswith("es") and not word.endswith(("aes", "ees", "oes")):
        return word[:-1]
    if word.endswith("s") and not word.endswith(("us", "ss")):
        return word[:-1]
    return word


@dataclass(frozen=True)
class Span:
    """A word with its character offsets in the source document."""

    text: str
    start: int
    end: int


def word_spans(text: str) -> list[Span]:
    return [Span(m.group(), m.start(), m.end()) for m in _WORD.finditer(text)]


def terms(text: str, *, drop_stopwords: bool = True) -> list[str]:
    """Lowercased, plural-stripped terms used by BM25 and the hashing embedder."""
    found = _TERM.findall(text.lower())
    if drop_stopwords:
        found = [t for t in found if t not in STOPWORDS]
    return [s_stem(t) for t in found]


def sentence_spans(text: str) -> list[tuple[int, int]]:
    """Character ranges of sentences (split after . ! ? followed by whitespace)."""
    spans: list[tuple[int, int]] = []
    start = 0
    for m in _SENTENCE_END.finditer(text):
        spans.append((start, m.start()))
        start = m.end()
    if start < len(text):
        spans.append((start, len(text)))
    return [(s, e) for s, e in spans if text[s:e].strip()]


def word_count(text: str) -> int:
    return len(_WORD.findall(text))
