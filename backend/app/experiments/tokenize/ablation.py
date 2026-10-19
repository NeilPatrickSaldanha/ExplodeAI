"""What breaks if a tokenizer stage is removed? Run the real tokenizer without it.

`ablate(params, stage)` executes every remaining stage for real:

- corpus          nothing to learn from: zero merges, so text is spelled in base
                  symbols only (bytes) or entirely as [UNK] (characters).
- pre_tokenizer   text is not cut into word pieces, so merges can join across
                  words (same as the "none" pre-tokenizer setting).
- base_alphabet   there are no starting symbols, so every character of the input
                  is [UNK] and the text cannot be recovered.
- merge_learner   no merges are learned: every token is a single base symbol,
                  so the sequence is as long as it can be.
- vocabulary      no symbol-to-id table exists, so the encoder cannot emit ids.
- input_text      there is nothing to encode.
- encoder         no ids are produced, so the decoder has nothing to decode.
- decoder         ids are produced but never turned back into text.

These statements describe ExplodeAI's own educational tokenizer and are checked
by tests/test_tokenize_ablation.py, not by external citations.
"""

from app.experiments.tokenize import bpe
from app.experiments.tokenize.corpus import get_corpus
from app.experiments.tokenize.pipeline import STAGES, TokenizeParams

PREVIEW = 16


def _show(tok: bpe.Tokenizer, ids: list[int]) -> list[str]:
    return [bpe.UNK if i == tok.unk_id else (bpe.display(tok.vocab[i]) or tok.vocab[i].hex(" ")) for i in ids]


def ablate(params: TokenizeParams, stage: str | None) -> dict:
    if stage is not None and stage not in STAGES:
        raise ValueError(f"unknown stage '{stage}'")
    notes: list[str] = []

    training_text = "" if stage == "corpus" else get_corpus(params.corpus_id).text
    pre = "none" if stage == "pre_tokenizer" else params.pre_tokenizer
    merges = 0 if stage == "merge_learner" else params.merges

    if stage == "base_alphabet":
        # No starting symbols at all: an empty character alphabet, nothing learned.
        tok = bpe.train("", 0, "chars", pre)
        notes.append("no base symbols, so every character is [UNK]")
    else:
        tok = bpe.train(training_text, merges, params.base, pre)
    if stage == "corpus":
        notes.append("no training text, so no merges are learned")
    if stage == "merge_learner":
        notes.append("no merges: one token per base symbol")

    crossing = [t for t in (_show(tok, [m.new_id])[0] for m in tok.merges) if bpe.crosses_word_boundary(t)]
    if stage == "pre_tokenizer" and crossing:
        notes.append(f"{len(crossing)} learned tokens span more than one word")

    text = "" if stage == "input_text" else params.text
    if stage == "input_text":
        notes.append("no input, so nothing is encoded")

    if stage in ("vocabulary", "encoder"):
        ids: list[int] | None = None
        notes.append("no vocabulary to look ids up in" if stage == "vocabulary"
                     else "the encoder never runs, so no ids exist")
    else:
        ids = tok.encode(text, params.merge_order) if text else []

    if stage == "decoder":
        decoded = None
        notes.append("ids are produced but never turned back into text")
    else:
        decoded = tok.decode(ids) if ids else ""

    return {
        "removed": stage,
        "vocab_size": tok.vocab_size,
        "merges": len(tok.merges),
        "crossing_word_boundary": len(crossing),
        "tokens": None if ids is None else len(ids),
        "preview": [] if not ids else _show(tok, ids[:PREVIEW]),
        "unk_count": 0 if not ids else sum(1 for i in ids if i == tok.unk_id),
        "decoded": decoded,
        "round_trip": decoded == params.text,
        "notes": notes,
    }
