"""An educational byte-pair-encoding (BPE) tokenizer.

This is NOT any provider's tokenizer. It is a small, readable BPE written for
ExplodeAI so every stage can be inspected. It follows the published algorithm
(Sennrich et al., 2016; byte-level variant from the GPT-2 paper):

- pre-tokenize:  split text into word-like pieces. "words" uses a simplified
                 GPT-2-style pattern (an optional leading space, then letters,
                 digits or other symbols); "none" keeps the text as one piece, so
                 merges may cross word boundaries.
- base alphabet: "bytes" = the 256 possible byte values (any text can be encoded);
                 "chars" = only the characters seen in training, plus [UNK].
- train:         count adjacent symbol pairs (weighted by how often each piece
                 occurs), merge the most frequent pair into a new symbol, repeat.
                 Ties break on the pair's bytes, so training is deterministic.
- encode:        pre-tokenize, map to base symbols, then replay the learned
                 merges in the order they were learned.
- decode:        concatenate each token's bytes and decode as UTF-8.

Symbols are integer ids; every id maps to the exact bytes it stands for.
"""

import re
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Literal

Base = Literal["bytes", "chars"]
PreTokenizer = Literal["words", "none"]
MergeOrder = Literal["learned", "reversed"]

UNK = "[UNK]"
SPECIAL_TOKENS = ["<|endoftext|>"]

# GPT-2's pattern uses \p{L} and \p{N}; Python's `re` has no Unicode property
# classes, so letters are [^\W\d_] and digits are \d. The last alternatives make
# sure every character (including "_") lands in some piece: the pieces always
# concatenate back to the input.
_WORDS = re.compile(r"'(?:s|t|re|ve|m|ll|d)| ?[^\W\d_]+| ?\d+| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+")


def pre_tokenize(text: str, mode: PreTokenizer) -> list[str]:
    if mode == "none":
        return [text] if text else []
    return _WORDS.findall(text)


Pair = tuple[int, int]


@dataclass
class MergeStep:
    rank: int
    pair: Pair
    new_id: int
    count: int


@dataclass
class Tokenizer:
    base: Base
    pre_tokenizer: PreTokenizer
    # id -> bytes the symbol stands for. For base="chars", id 0 is [UNK] (no bytes).
    vocab: dict[int, bytes]
    base_size: int
    merges: list[MergeStep] = field(default_factory=list)
    char_to_id: dict[str, int] = field(default_factory=dict)
    special: dict[str, int] = field(default_factory=dict)

    @property
    def unk_id(self) -> int | None:
        return 0 if self.base == "chars" else None

    @property
    def vocab_size(self) -> int:
        return len(self.vocab) + len(self.special)

    def truncated(self, n_merges: int) -> "Tokenizer":
        """The tokenizer that training would have produced with only the first n merges."""
        merges = self.merges[:n_merges]
        keep = set(range(self.base_size)) | {m.new_id for m in merges}
        vocab = {i: b for i, b in self.vocab.items() if i in keep}
        return _with_special(Tokenizer(self.base, self.pre_tokenizer, vocab, self.base_size,
                                       merges, self.char_to_id))

    # ------------------------------------------------------------ encoding
    def base_ids(self, piece: str) -> list[int]:
        if self.base == "bytes":
            return list(piece.encode("utf-8"))
        return [self.char_to_id.get(ch, 0) for ch in piece]

    def encode_piece(self, piece: str, order: MergeOrder = "learned",
                     trace: list[tuple[MergeStep, list[int]]] | None = None) -> list[int]:
        ids = self.base_ids(piece)
        steps = self.merges if order == "learned" else list(reversed(self.merges))
        for step in steps:
            if len(ids) < 2:
                break
            merged = merge_pair(ids, step.pair, step.new_id)
            if len(merged) != len(ids):
                ids = merged
                if trace is not None:
                    trace.append((step, ids))
        return ids

    def encode(self, text: str, order: MergeOrder = "learned") -> list[int]:
        pieces = pre_tokenize(text, self.pre_tokenizer)
        return [i for piece in pieces for i in self.encode_piece(piece, order)]

    # ------------------------------------------------------------ decoding
    def token_bytes(self, token_id: int) -> bytes:
        if token_id == self.unk_id:
            return "�".encode()
        for name, sid in self.special.items():
            if sid == token_id:
                return name.encode()
        return self.vocab[token_id]

    def decode(self, ids: Iterable[int]) -> str:
        return b"".join(self.token_bytes(i) for i in ids).decode("utf-8", errors="replace")


def merge_pair(ids: list[int], pair: Pair, new_id: int) -> list[int]:
    """Replace every non-overlapping occurrence of `pair`, scanning left to right."""
    out: list[int] = []
    i = 0
    a, b = pair
    while i < len(ids):
        if i + 1 < len(ids) and ids[i] == a and ids[i + 1] == b:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


def _with_special(tok: Tokenizer) -> Tokenizer:
    next_id = max(tok.vocab) + 1
    tok.special = {name: next_id + i for i, name in enumerate(SPECIAL_TOKENS)}
    return tok


def train(text: str, n_merges: int, base: Base = "bytes",
          pre_tokenizer: PreTokenizer = "words") -> Tokenizer:
    """Learn up to `n_merges` merges. Stops early if no pair is left to merge."""
    return train_from_counts(Counter(pre_tokenize(text, pre_tokenizer)), n_merges, base, pre_tokenizer)


def train_from_counts(freq: Counter[str], n_merges: int, base: Base = "bytes",
                      pre_tokenizer: PreTokenizer = "words") -> Tokenizer:
    """Train on a dictionary of distinct pieces and how often each occurs (Sennrich §3.2)."""
    if base == "bytes":
        vocab = {i: bytes([i]) for i in range(256)}
        char_to_id: dict[str, int] = {}
    else:
        alphabet = sorted({ch for piece in freq for ch in piece})
        vocab = {0: b""}  # [UNK]
        char_to_id = {ch: i + 1 for i, ch in enumerate(alphabet)}
        vocab.update({i: ch.encode("utf-8") for ch, i in char_to_id.items()})
    tok = Tokenizer(base, pre_tokenizer, vocab, len(vocab), char_to_id=char_to_id)

    # Each distinct piece once, weighted by how often it occurs.
    words = {piece: tok.base_ids(piece) for piece in freq}
    next_id = len(vocab)
    for rank in range(n_merges):
        pairs: Counter[Pair] = Counter()
        for piece, ids in words.items():
            for pair in zip(ids, ids[1:], strict=False):
                pairs[pair] += freq[piece]
        if not pairs:
            break
        # Most frequent pair; ties go to the pair whose bytes sort first.
        best = min(pairs, key=lambda p: (-pairs[p], tok.vocab[p[0]], tok.vocab[p[1]]))
        tok.vocab[next_id] = tok.vocab[best[0]] + tok.vocab[best[1]]
        tok.merges.append(MergeStep(rank, best, next_id, pairs[best]))
        for piece, ids in words.items():
            if len(ids) > 1:
                words[piece] = merge_pair(ids, best, next_id)
        next_id += 1
    return _with_special(tok)


def display(b: bytes) -> str | None:
    """Readable text for a token's bytes, or None if they are not valid UTF-8 on their own."""
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return None


def crosses_word_boundary(piece: str) -> bool:
    """True if a token spans more than one word: it has visible characters and
    whitespace somewhere after its first character (a leading space is allowed)."""
    return not piece.isspace() and any(ch.isspace() for ch in piece[1:])
