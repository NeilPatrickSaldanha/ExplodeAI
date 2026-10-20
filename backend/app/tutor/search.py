"""Find the passages that answer a question: BM25 plus (when installed) the local neural
embedder, fused with reciprocal rank fusion, the same techniques Lesson 01 teaches.

Relevance is gated: a question about something the lessons do not cover returns no
passages at all, so the tutor says so instead of improvising.
"""

import hashlib
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np

from app.config import get_settings
from app.content.loader import content
from app.experiments.embed import model as bge
from app.experiments.rag.retrieval import BM25, rank, rrf
from app.experiments.rag.text import terms
from app.tutor.index import Passage, build_passages

STAGE_BOOST = 0.004  # added to the fused score: a nudge, never an override
LESSON_BOOST = 0.0015
# A vague question ("what can go wrong?") matches the same wording in every stage. Then the open
# stage is the best clue to what is meant, so it counts for more.
KIND_BOOST = 0.004  # the phrasing ("why", "what if removed") points at a kind of passage
VAGUE_STAGE_BOOST = 0.02
VAGUE_LESSON_BOOST = 0.006
VAGUE_IF_TOP8_SPANS = 5
# Gate: a question is "covered" when enough of its meaningful words appear in the lessons,
# or (with the neural model) a passage is clearly close in meaning. Calibrated by
# tests/test_tutor_eval.py on in-scope and out-of-scope questions.
MIN_TERM_COVERAGE = 0.6
MIN_DENSE_COSINE = 0.72  # close in meaning on its own
MIN_DENSE_ALL_WORDS = 0.57  # every meaningful word is in the lessons AND the meaning is roughly close
MIN_DENSE_MOST_WORDS = 0.70  # most words are in the lessons AND the meaning is clearly close


@dataclass(frozen=True)
class Scored:
    passage: Passage
    score: float
    lexical: float
    dense: float | None


class TutorIndex:
    def __init__(self, passages: list[Passage], use_neural: bool | None = None) -> None:
        self.passages = passages
        self.bm25 = BM25([p.search_text for p in passages])
        self.vocab = {t for toks in self.bm25.tokens for t in toks}
        self.neural = bge.neural_ready() if use_neural is None else use_neural
        self.vectors: np.ndarray | None = _vectors(passages) if self.neural else None

    def coverage(self, question: str) -> float:
        q = terms(question)
        return sum(t in self.vocab for t in q) / len(q) if q else 0.0

    def search(
        self,
        question: str,
        *,
        lesson_id: str | None = None,
        stage_id: str | None = None,
        k: int = 5,
        prefer: set[str] | None = None,
    ) -> tuple[list[Scored], dict]:
        n = len(self.passages)
        lex = self.bm25.scores(question)
        rankings = [rank(lex)]
        dense = None
        if self.vectors is not None:
            q = bge.l2_normalize(
                bge.pool(bge.get_encoder().encode([bge.QUERY_INSTRUCTION + question]).hidden[0], "cls")
            )
            dense = self.vectors @ q
            rankings.append(rank(dense))
        fused = rrf(rankings, n)
        top8 = sorted(range(n), key=lambda i: (-fused[i], i))[:8]
        vague = (
            len({(self.passages[i].lesson_id, self.passages[i].stage_id) for i in top8})
            >= VAGUE_IF_TOP8_SPANS
        )
        stage_boost, lesson_boost = (
            (VAGUE_STAGE_BOOST, VAGUE_LESSON_BOOST) if vague else (STAGE_BOOST, LESSON_BOOST)
        )
        for i, p in enumerate(self.passages):
            if lesson_id and p.lesson_id == lesson_id:
                fused[i] += lesson_boost
                if stage_id and p.stage_id == stage_id:
                    fused[i] += stage_boost
        if prefer:
            for i, p in enumerate(self.passages):
                if p.kind in prefer:
                    fused[i] += KIND_BOOST
        coverage = self.coverage(question)
        best_dense = float(dense.max()) if dense is not None else None
        if best_dense is None:  # no neural model: shared words are all there is to go on
            covered = coverage >= MIN_TERM_COVERAGE
        else:
            covered = (
                best_dense >= MIN_DENSE_COSINE
                or (coverage >= 1.0 and best_dense >= MIN_DENSE_ALL_WORDS)
                or (coverage >= MIN_TERM_COVERAGE and best_dense >= MIN_DENSE_MOST_WORDS)
            )
        info = {
            "coverage": round(coverage, 3),
            "best_dense": None if best_dense is None else round(best_dense, 3),
            "covered": covered,
            "method": "hybrid" if dense is not None else "bm25",
        }
        if not covered:
            return [], info
        order = sorted(range(n), key=lambda i: (-fused[i], i))[:k]
        return [
            Scored(
                self.passages[i], float(fused[i]), float(lex[i]), None if dense is None else float(dense[i])
            )
            for i in order
        ], info


def _vectors(passages: list[Passage]) -> np.ndarray:
    """Passage vectors, cached on disk and keyed by content so edits re-embed automatically."""
    key = hashlib.sha256((bge.MODEL_BUILD + "".join(p.search_text for p in passages)).encode()).hexdigest()[
        :16
    ]
    cache = Path(get_settings().database_url.replace("sqlite:///", "")).parent / f"tutor_vectors_{key}.npy"
    if cache.exists():
        return np.load(cache)
    enc = bge.get_encoder()
    vecs = np.stack(
        [bge.l2_normalize(bge.pool(h, "cls")) for h in enc.encode([p.search_text for p in passages]).hidden]
    )
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        np.save(cache, vecs)
    except OSError:  # read-only deploys still work, just slower on first use
        pass
    return vecs


@lru_cache(maxsize=1)
def get_index() -> TutorIndex:
    registry, lessons = content()
    return TutorIndex(build_passages(lessons, registry))


def warm() -> float:
    start = time.perf_counter()
    get_index()
    return round(time.perf_counter() - start, 2)
