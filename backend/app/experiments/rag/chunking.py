"""Chunking strategies.

- fixed:    sliding window of `size` words, stepping by `size - overlap` words.
- sentence: packs whole sentences into chunks of at most `size` words; the next
            chunk re-includes trailing words of the previous one up to `overlap`
            words (rounded to whole sentences). A single sentence longer than
            `size` becomes its own chunk rather than being cut mid-sentence.

Every chunk keeps character offsets into its source document so the UI can
highlight exactly which text was embedded.
"""

from dataclasses import dataclass
from typing import Literal

from app.experiments.rag.corpus import Document
from app.experiments.rag.text import sentence_spans, word_count, word_spans

Strategy = Literal["fixed", "sentence"]


@dataclass(frozen=True)
class Chunk:
    id: str
    doc_id: str
    index: int
    text: str
    start: int
    end: int

    @property
    def words(self) -> int:
        return word_count(self.text)


def validate_params(size: int, overlap: int) -> None:
    if size < 1:
        raise ValueError("chunk size must be at least 1 word")
    if overlap < 0:
        raise ValueError("overlap cannot be negative")
    if overlap >= size:
        raise ValueError("overlap must be smaller than chunk size, or chunking never advances")


def chunk_fixed(doc: Document, size: int, overlap: int) -> list[Chunk]:
    validate_params(size, overlap)
    words = word_spans(doc.text)
    step = size - overlap
    chunks: list[Chunk] = []
    i = 0
    while i < len(words):
        window = words[i : i + size]
        start, end = window[0].start, window[-1].end
        chunks.append(
            Chunk(f"{doc.id}#{len(chunks)}", doc.id, len(chunks), doc.text[start:end], start, end)
        )
        if i + size >= len(words):
            break
        i += step
    return chunks


def chunk_sentences(doc: Document, size: int, overlap: int) -> list[Chunk]:
    validate_params(size, overlap)
    sents = sentence_spans(doc.text)
    counts = [word_count(doc.text[s:e]) for s, e in sents]
    chunks: list[Chunk] = []
    i = 0
    while i < len(sents):
        j, total = i, 0
        while j < len(sents) and (total + counts[j] <= size or j == i):
            total += counts[j]
            j += 1
        start, end = sents[i][0], sents[j - 1][1]
        chunks.append(
            Chunk(f"{doc.id}#{len(chunks)}", doc.id, len(chunks), doc.text[start:end], start, end)
        )
        if j >= len(sents):
            break
        # Step back over trailing sentences that fit inside the overlap budget.
        back, carried = j, 0
        while back - 1 > i and carried + counts[back - 1] <= overlap:
            back -= 1
            carried += counts[back]
        i = back
    return chunks


def chunk_corpus(docs: list[Document], strategy: Strategy, size: int, overlap: int) -> list[Chunk]:
    fn = chunk_fixed if strategy == "fixed" else chunk_sentences
    return [c for d in docs for c in fn(d, size, overlap)]
