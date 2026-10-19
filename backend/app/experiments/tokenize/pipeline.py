"""End-to-end tokenization experiment: every stage runs for real and is timed.

An educational BPE (see `bpe.py`), not any provider's tokenizer. The stage ids
below are the contract between this code, the lesson content
(`content/lessons/tokenization/lesson.yaml` components), and the 3D view. A test
asserts the three stay in sync.
"""

import time
from functools import lru_cache

from pydantic import BaseModel, Field

from app.experiments.tokenize import bpe
from app.experiments.tokenize.corpus import SAMPLE_CORPUS_ID, get_corpus

# Stage id -> stages it depends on. Training (left) builds the vocabulary; the
# encoder needs both the vocabulary and the input text; the decoder inverts it.
STAGE_DEPENDENCIES: dict[str, list[str]] = {
    "corpus": [],
    "pre_tokenizer": ["corpus"],
    "base_alphabet": ["pre_tokenizer"],
    "merge_learner": ["base_alphabet"],
    "vocabulary": ["merge_learner"],
    "input_text": [],
    "encoder": ["vocabulary", "input_text"],
    "decoder": ["encoder"],
}
STAGES = list(STAGE_DEPENDENCIES)

MAX_MERGES = 300
SWEEP_POINTS = [0, 10, 25, 50, 75, 100, 150, 200, 250, 300]
LABEL = "Educational BPE (ExplodeAI), not any provider's tokenizer"


class TokenizeParams(BaseModel):
    corpus_id: str = SAMPLE_CORPUS_ID
    text: str = Field("The keeper lit the lantern at dusk.", min_length=1, max_length=400)
    merges: int = Field(100, ge=0, le=MAX_MERGES)
    base: bpe.Base = "bytes"
    pre_tokenizer: bpe.PreTokenizer = "words"
    merge_order: bpe.MergeOrder = "learned"


def _ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 3)


@lru_cache(maxsize=16)
def _full_training(corpus_id: str, base: bpe.Base, pre_tokenizer: bpe.PreTokenizer) -> bpe.Tokenizer:
    """Training to MAX_MERGES once, for the trade-off sweep. Because training is
    greedy and deterministic, the first n merges of this run are exactly what a
    run with n merges learns (tested), so the sweep can slice it."""
    return bpe.train(get_corpus(corpus_id).text, MAX_MERGES, base, pre_tokenizer)


def _token_out(tok: bpe.Tokenizer, token_id: int) -> dict:
    raw = tok.token_bytes(token_id)
    is_unk = token_id == tok.unk_id
    return {
        "id": token_id,
        "text": bpe.UNK if is_unk else bpe.display(raw),
        "bytes_hex": raw.hex(" ") if not is_unk else "",
        "is_unk": is_unk,
    }


def _pieces(tok: bpe.Tokenizer, ids: list[int]) -> list[str]:
    return [bpe.UNK if i == tok.unk_id else (bpe.display(tok.vocab[i]) or tok.vocab[i].hex(" ")) for i in ids]


def run(params: TokenizeParams) -> dict:
    timings: dict[str, float] = {}

    t = time.perf_counter()
    corpus = get_corpus(params.corpus_id)
    timings["corpus"] = _ms(t)

    t = time.perf_counter()
    train_pieces = bpe.pre_tokenize(corpus.text, params.pre_tokenizer)
    timings["pre_tokenizer"] = _ms(t)

    t = time.perf_counter()
    base_tok = bpe.train(corpus.text, 0, params.base, params.pre_tokenizer)
    timings["base_alphabet"] = _ms(t)

    t = time.perf_counter()
    tok = bpe.train(corpus.text, params.merges, params.base, params.pre_tokenizer)
    timings["merge_learner"] = _ms(t)

    t = time.perf_counter()
    learned_tokens = [bpe.display(tok.vocab[m.new_id]) or tok.vocab[m.new_id].hex(" ") for m in tok.merges]
    crossing = [s for s in learned_tokens if bpe.crosses_word_boundary(s)]
    timings["vocabulary"] = _ms(t)

    t = time.perf_counter()
    input_pieces = bpe.pre_tokenize(params.text, params.pre_tokenizer)
    timings["input_text"] = _ms(t)

    t = time.perf_counter()
    piece_traces = []
    ids: list[int] = []
    for piece in input_pieces:
        trace: list[tuple[bpe.MergeStep, list[int]]] = []
        start_ids = tok.base_ids(piece)
        piece_ids = tok.encode_piece(piece, params.merge_order, trace)
        ids.extend(piece_ids)
        piece_traces.append({
            "text": piece,
            "start": _pieces(tok, start_ids),
            "steps": [{"rank": s.rank, "token": _pieces(tok, [s.new_id])[0], "pieces": _pieces(tok, after)}
                      for s, after in trace],
        })
    timings["encoder"] = _ms(t)

    t = time.perf_counter()
    decoded = tok.decode(ids)
    timings["decoder"] = _ms(t)

    # Vocabulary size vs sequence length, across merge counts (same corpus and settings).
    full = _full_training(params.corpus_id, params.base, params.pre_tokenizer)
    corpus_bytes = len(corpus.text.encode())
    sweep = []
    # Fixed points, the learner's setting, and the point where training runs out of pairs.
    learned = len(full.merges)
    points = {p for p in SWEEP_POINTS if p <= learned} | {min(params.merges, learned), learned}
    for n in sorted(points):
        sub = full.truncated(n)
        corpus_tokens = len(sub.encode(corpus.text))
        sweep.append({
            "merges": n,
            "vocab_size": sub.vocab_size,
            "input_tokens": len(sub.encode(params.text, params.merge_order)),
            "corpus_tokens": corpus_tokens,
            "corpus_bytes_per_token": round(corpus_bytes / max(1, corpus_tokens), 3),
        })

    freq: dict[str, int] = {}
    for p in train_pieces:
        freq[p] = freq.get(p, 0) + 1
    top_words = sorted(freq, key=lambda w: (-freq[w], w))[:4] if params.pre_tokenizer == "words" else []
    history = []
    for w in top_words:
        trace = []
        tok.encode_piece(w, "learned", trace)
        history.append({
            "word": w, "count": freq[w], "start": _pieces(tok, tok.base_ids(w)),
            "steps": [{"after_merges": s.rank + 1, "pieces": _pieces(tok, after)} for s, after in trace],
        })

    unk_count = sum(1 for i in ids if i == tok.unk_id)
    return {
        "params": params.model_dump(),
        "label": LABEL,
        "corpus": {
            "id": corpus.id,
            "title": corpus.title,
            "note": corpus.note,
            "text": corpus.text,
            "characters": len(corpus.text),
            "bytes": corpus_bytes,
        },
        "pre_tokens": {
            "mode": params.pre_tokenizer,
            "count": len(train_pieces),
            "unique": len(freq),
            "sample": [{"text": w, "count": freq[w]} for w in sorted(freq, key=lambda w: (-freq[w], w))[:12]],
        },
        "base": {
            "mode": params.base,
            "size": base_tok.base_size,
            "has_unk": tok.unk_id is not None,
        },
        "training": {
            "merges_requested": params.merges,
            "merges_learned": len(tok.merges),
            "steps": [
                {"rank": m.rank, "left": _pieces(tok, [m.pair[0]])[0], "right": _pieces(tok, [m.pair[1]])[0],
                 "token": learned_tokens[m.rank], "token_id": m.new_id, "count": m.count}
                for m in tok.merges
            ],
            "word_history": history,
        },
        "vocabulary": {
            "size": tok.vocab_size,
            "base_size": tok.base_size,
            "merges": len(tok.merges),
            "special": [{"text": name, "id": sid} for name, sid in tok.special.items()],
            "crossing_word_boundary": crossing,
        },
        "input": {
            "text": params.text,
            "characters": len(params.text),
            "bytes": len(params.text.encode()),
            "pieces": len(input_pieces),
        },
        "encoding": {
            "order": params.merge_order,
            "ids": ids,
            "tokens": [_token_out(tok, i) for i in ids],
            "count": len(ids),
            "pieces": piece_traces,
        },
        "decoding": {
            "text": decoded,
            "round_trip": decoded == params.text,
            "unk_count": unk_count,
        },
        "sweep": sweep,
        "timings_ms": timings,
        "stages": STAGES,
    }
