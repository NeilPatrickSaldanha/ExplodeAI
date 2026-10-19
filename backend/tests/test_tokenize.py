"""Tokenization lesson: the educational BPE, its lesson content, and Pass 3 evidence.

Every @validates test here runs ExplodeAI's own educational BPE. It shows the
algorithmic property a claim describes; it says nothing about any provider's
trained tokenizer.
"""

import random
from collections import Counter

import pytest
import yaml

from app.config import REPO_DIR
from app.content.loader import load_lessons, load_registry
from app.content.schema import Lesson, validate_lesson
from app.experiments.tokenize import bpe, pipeline
from app.experiments.tokenize.corpus import SAMPLE_CORPUS
from app.routers.lessons import check_order
from app.routers.tokenize import evaluate_challenge
from tests.conftest import validates

CONTENT = REPO_DIR / "content"
CORPUS = SAMPLE_CORPUS.text
LEARNER = {"X-Learner-Id": "test-learner-0002"}


@pytest.fixture(scope="module")
def lesson() -> Lesson:
    return load_lessons(CONTENT)["tokenization"]


@pytest.fixture(scope="module")
def registry():
    return load_registry(CONTENT)


@pytest.fixture(scope="module")
def full() -> bpe.Tokenizer:
    return bpe.train(CORPUS, pipeline.MAX_MERGES)


def texts(tok: bpe.Tokenizer, ids: list[int]) -> list[str]:
    return [tok.token_bytes(i).decode("utf-8", errors="replace") for i in ids]


def random_text(rng: random.Random, n: int) -> str:
    """Mixed-script text: ASCII, accents, CJK, emoji, combining marks, odd whitespace."""
    pools = [
        "abcdefghijklmnopqrstuvwxyz ABCXYZ .,!?;:'\"-_()[]{}<>|0123456789",
        "éèçñüøåßœÆ", "日本語中文한국어", "😀🚀☕🌊🏳️‍🌈", "́̈", " \t\n\r 　",
        "<|endoftext|>",
    ]
    return "".join(rng.choice(rng.choice(pools)) for _ in range(n))


# ------------------------------------------------------- reference implementation
def reference_train(text: str, n: int, pre_tokenizer: bpe.PreTokenizer = "words"):
    """Independent, naive BPE over byte tuples, written separately from bpe.py.

    Returns the merges as (left bytes, right bytes) and each piece's final
    segmentation, so the real implementation can be checked against it.
    """
    freq = Counter(bpe.pre_tokenize(text, pre_tokenizer))
    segs = {w: [bytes([b]) for b in w.encode()] for w in freq}
    merges = []
    for _ in range(n):
        counts: Counter = Counter()
        for w, seg in segs.items():
            for a, b in zip(seg, seg[1:], strict=False):
                counts[(a, b)] += freq[w]
        if not counts:
            break
        top = max(counts.values())
        a, b = min(p for p, c in counts.items() if c == top)
        merges.append((a, b))
        for w, seg in segs.items():
            out, i = [], 0
            while i < len(seg):
                if i + 1 < len(seg) and seg[i] == a and seg[i + 1] == b:
                    out.append(a + b)
                    i += 2
                else:
                    out.append(seg[i])
                    i += 1
            segs[w] = out
    return merges, segs


# ------------------------------------------------------------ lesson content
def test_lesson_content_is_valid(lesson, registry):
    assert validate_lesson(lesson, registry) == []


def test_lesson_components_match_pipeline_stages(lesson):
    """The 3D model, the reconstruction graph, and the executed pipeline agree."""
    assert [c.id for c in lesson.components] == pipeline.STAGES
    assert lesson.reconstruction.dependencies == pipeline.STAGE_DEPENDENCIES


def test_diagram_edges_are_the_pipeline_dependencies(lesson):
    edges = {(c.source, c.target) for c in lesson.connections}
    deps = {(need, stage) for stage, needs in pipeline.STAGE_DEPENDENCIES.items() for need in needs}
    assert edges == deps


def test_every_visual_declares_its_kind_and_the_tokenizer_is_labelled(lesson):
    kinds = {v.id: v.kind for v in lesson.visuals}
    assert kinds["exploded-view"] == "conceptual"
    assert kinds["experiment"] == kinds["merge-replay"] == kinds["tradeoff"] == "real_execution"
    experiment = next(v for v in lesson.visuals if v.id == "experiment")
    assert "educational" in experiment.label.lower()
    assert "not any provider" in experiment.description
    assert "not any provider" in lesson.experiment["corpus_note"]
    assert "not any provider" in pipeline.LABEL


def test_reconstruction_accepts_any_valid_topological_order(lesson):
    deps = lesson.reconstruction.dependencies
    assert check_order(pipeline.STAGES, deps)["correct"]
    input_first = ["input_text", "corpus", "pre_tokenizer", "base_alphabet", "merge_learner",
                   "vocabulary", "encoder", "decoder"]
    assert check_order(input_first, deps)["correct"]
    encoder_early = ["corpus", "input_text", "encoder", "pre_tokenizer", "base_alphabet",
                     "merge_learner", "vocabulary", "decoder"]
    out = check_order(encoder_early, deps)
    assert not out["correct"] and {"stage": "encoder", "needs": "vocabulary"} in out["violations"]


def test_validator_rejects_a_check_from_another_engine(registry):
    with (CONTENT / "lessons" / "tokenization" / "lesson.yaml").open() as fh:
        raw = yaml.safe_load(fh)
    raw["challenges"][0]["checks"] = [{"type": "gold_in_prompt", "gold": ["x"]}]
    problems = validate_lesson(Lesson.model_validate(raw), registry)
    assert any("not available for engine 'tokenize'" in p for p in problems)


def test_max_tokens_check_needs_a_limit():
    from app.content.schema import Check

    with pytest.raises(ValueError):
        Check(type="max_tokens")
    with pytest.raises(ValueError):
        Check(type="single_token")


# ------------------------------------------------------------------ pipeline
def test_run_reports_every_stage_with_timing():
    result = pipeline.run(pipeline.TokenizeParams())
    assert result["stages"] == pipeline.STAGES
    assert set(result["timings_ms"]) == set(pipeline.STAGES)
    assert result["decoding"]["round_trip"] is True
    assert result["encoding"]["count"] == len(result["encoding"]["ids"])
    assert "not any provider" in result["label"]


def test_trace_steps_end_in_the_final_tokens():
    r = pipeline.run(pipeline.TokenizeParams(text="The keeper trimmed the lantern wick.", merges=200))
    final = [p["steps"][-1]["pieces"] if p["steps"] else p["start"] for p in r["encoding"]["pieces"]]
    assert [t for piece in final for t in piece] == [t["text"] for t in r["encoding"]["tokens"]]
    ranks = [s["rank"] for p in r["encoding"]["pieces"] for s in p["steps"]]
    for p in r["encoding"]["pieces"]:
        assert [s["rank"] for s in p["steps"]] == sorted(s["rank"] for s in p["steps"])
    assert ranks, "some merges were applied"


def test_overlong_input_and_bad_settings_are_rejected():
    with pytest.raises(ValueError):
        pipeline.TokenizeParams(text="x" * 401)
    with pytest.raises(ValueError):
        pipeline.TokenizeParams(merges=pipeline.MAX_MERGES + 1)
    with pytest.raises(ValueError):
        pipeline.TokenizeParams(base="unicode")


# ----------------------------------------------------------- Pass 3 evidence
@validates("bpe-training-loop", "bpe-apply-in-order")
def test_bpe_matches_an_independent_reference_implementation(full):
    ref_merges, ref_segs = reference_train(CORPUS, pipeline.MAX_MERGES)
    got = [(full.vocab[m.pair[0]], full.vocab[m.pair[1]]) for m in full.merges]
    assert got == ref_merges
    # Encoding a training piece by replaying merges in learned order reproduces
    # exactly the segmentation training ended with.
    for piece, seg in ref_segs.items():
        assert [full.token_bytes(i) for i in full.encode_piece(piece)] == seg


@validates("bpe-training-loop")
def test_each_merge_is_the_most_frequent_pair_at_that_step():
    tok = bpe.train(CORPUS, 60)
    freq = Counter(bpe.pre_tokenize(CORPUS, "words"))
    segs = {w: tok.base_ids(w) for w in freq}
    for step in tok.merges:
        counts: Counter = Counter()
        for w, ids in segs.items():
            for pair in zip(ids, ids[1:], strict=False):
                counts[pair] += freq[w]
        assert counts[step.pair] == max(counts.values()) == step.count
        segs = {w: bpe.merge_pair(ids, step.pair, step.new_id) for w, ids in segs.items()}


@validates("bpe-frequency-weighted")
def test_training_on_a_word_frequency_dictionary_equals_training_on_the_text():
    freq = Counter(bpe.pre_tokenize(CORPUS, "words"))
    assert len(freq) < sum(freq.values())  # the dictionary is smaller than the text
    a = bpe.train(CORPUS, 150)
    b = bpe.train_from_counts(freq, 150)
    assert [(m.pair, m.count) for m in a.merges] == [(m.pair, m.count) for m in b.merges]
    # Counts are weighted by frequency: doubling every count doubles each pair count.
    c = bpe.train_from_counts(Counter({w: 2 * n for w, n in freq.items()}), 150)
    assert [m.pair for m in c.merges] == [m.pair for m in a.merges]
    assert [m.count for m in c.merges] == [2 * m.count for m in a.merges]


@validates("bpe-vocab-formula")
@pytest.mark.parametrize("base", ["bytes", "chars"])
@pytest.mark.parametrize("merges", [0, 1, 50, 150])
def test_vocabulary_is_base_plus_merges_plus_special(base, merges):
    tok = bpe.train(CORPUS, merges, base)
    assert len(tok.merges) == merges
    assert tok.vocab_size == tok.base_size + merges + len(bpe.SPECIAL_TOKENS)


@validates("real-merge-counts")
def test_training_stops_when_no_pair_is_left():
    tok = bpe.train(CORPUS, 5000)
    assert len(tok.merges) == 216 < pipeline.MAX_MERGES  # the figure the lesson states
    distinct = set(bpe.pre_tokenize(CORPUS, "words"))
    assert all(len(tok.encode_piece(w)) == 1 for w in distinct)


@validates("bpe-no-cross-word")
def test_word_pre_tokenization_keeps_every_merge_inside_a_word():
    words = bpe.train(CORPUS, 200, pre_tokenizer="words")
    learned = [words.vocab[m.new_id].decode() for m in words.merges]
    pieces = set(bpe.pre_tokenize(CORPUS, "words"))
    assert not [t for t in learned if bpe.crosses_word_boundary(t)]
    assert all(any(t in p for p in pieces) for t in learned)
    # Without pre-tokenization the same learner does merge across spaces.
    none = bpe.train(CORPUS, 200, pre_tokenizer="none")
    assert [t for t in (none.vocab[m.new_id].decode() for m in none.merges) if bpe.crosses_word_boundary(t)]


@validates("bpe-deterministic")
def test_training_and_encoding_are_deterministic_and_merges_are_a_prefix(full):
    a, b = bpe.train(CORPUS, 150), bpe.train(CORPUS, 150)
    assert [(m.pair, m.new_id) for m in a.merges] == [(m.pair, m.new_id) for m in b.merges]
    text = "The lanternkeepers rewound clockwork."
    assert a.encode(text) == b.encode(text)
    # Training greedily for n merges learns exactly the first n of a longer run,
    # which is why the trade-off sweep can slice one long training run.
    assert [(m.pair, m.new_id) for m in a.merges] == [(m.pair, m.new_id) for m in full.merges[:150]]
    assert full.truncated(150).encode(text) == a.encode(text)


@validates("gpt2-byte-level")
def test_byte_level_base_alphabet_has_exactly_256_symbols():
    tok = bpe.train(CORPUS, 0, "bytes")
    assert tok.base_size == 256 and sorted(tok.vocab) == list(range(256))
    assert tok.base_ids("é☕") == list("é☕".encode())
    chars = bpe.train(CORPUS, 0, "chars")
    assert chars.base_size == len(set(CORPUS)) + 1  # characters seen + [UNK]


@validates("byte-level-no-unk", "byte-bpe-lossless")
@pytest.mark.parametrize("merges", [0, 30, 216])
def test_byte_level_bpe_round_trips_arbitrary_text_without_unknowns(merges):
    tok = bpe.train(CORPUS, merges, "bytes")
    rng = random.Random(merges)
    for _ in range(300):
        text = random_text(rng, rng.randint(1, 60))
        ids = tok.encode(text)
        assert tok.unk_id is None and all(i in tok.vocab for i in ids)
        assert tok.decode(ids) == text


@validates("char-bpe-unk")
def test_character_alphabet_turns_unseen_characters_into_unknowns():
    tok = bpe.train(CORPUS, 60, "chars")
    assert "é" not in CORPUS
    ids = tok.encode("café at dusk")
    assert ids.count(tok.unk_id) == 1
    assert tok.decode(ids) == "caf\ufffd at dusk"
    r = pipeline.run(pipeline.TokenizeParams(text="Café crème ☕", base="chars", merges=60))
    assert r["decoding"]["unk_count"] >= 3 and not r["decoding"]["round_trip"]


@validates("gpt2-character-categories")
def test_letters_and_punctuation_are_never_merged_together():
    pieces = bpe.pre_tokenize("dog. dog! dog? The keeper's lantern, at dusk.", "words")
    assert pieces[:6] == ["dog", ".", " dog", "!", " dog", "?"]
    tok = bpe.train(CORPUS, 216)
    for m in tok.merges:
        t = tok.vocab[m.new_id].decode()
        has_letter = any(ch.isalpha() for ch in t)
        has_punct = any(not ch.isalnum() and not ch.isspace() for ch in t)
        assert not (has_letter and has_punct), t
    # Pieces always concatenate back to the input, whatever it contains.
    rng = random.Random(7)
    for _ in range(300):
        text = random_text(rng, 40)
        assert "".join(bpe.pre_tokenize(text, "words")) == text


@validates("leading-space")
def test_a_space_belongs_to_the_next_word():
    tok = bpe.train(CORPUS, 216)
    assert bpe.pre_tokenize("the keeper and the lantern", "words") == ["the", " keeper", " and", " the", " lantern"]
    ids = tok.encode("The the")
    assert texts(tok, ids) == ["The", " the"]
    assert ids[0] != ids[1]


@validates("special-tokens")
def test_special_token_text_in_the_input_is_encoded_as_plain_text():
    tok = bpe.train(CORPUS, 100)
    special_id = tok.special["<|endoftext|>"]
    assert special_id == max(tok.vocab) + 1 and special_id not in tok.vocab
    ids = tok.encode("dusk<|endoftext|>dawn")
    assert special_id not in ids and len(ids) > 3
    assert tok.decode(ids) == "dusk<|endoftext|>dawn"


@validates("vocab-length-tradeoff")
def test_more_merges_grow_the_vocabulary_and_shorten_sequences():
    r = pipeline.run(pipeline.TokenizeParams(text="The keeper lit the lantern before the tide turned.", merges=300))
    sweep = r["sweep"]
    assert [s["merges"] for s in sweep] == sorted(s["merges"] for s in sweep)
    vocab = [s["vocab_size"] for s in sweep]
    tokens = [s["input_tokens"] for s in sweep]
    corpus_tokens = [s["corpus_tokens"] for s in sweep]
    assert vocab == sorted(set(vocab))  # strictly growing
    assert tokens == sorted(tokens, reverse=True) and tokens[0] > tokens[-1]
    assert corpus_tokens == sorted(corpus_tokens, reverse=True)
    assert sweep[0]["merges"] == 0 and sweep[0]["input_tokens"] == r["input"]["bytes"]
    # Character level (no merges) vs this tokenizer's largest vocabulary.
    assert sweep[0]["input_tokens"] >= 4 * sweep[-1]["input_tokens"]


@validates("decode-partial-lossy", "tokens-not-words")
def test_one_character_can_span_tokens_and_a_slice_of_them_is_not_valid_utf8():
    tok = bpe.train(CORPUS, 0)
    ids = tok.encode("é")
    assert len(ids) == 2  # a token shorter than one character
    assert bpe.display(tok.token_bytes(ids[0])) is None
    with pytest.raises(UnicodeDecodeError):
        tok.token_bytes(ids[0]).decode("utf-8")
    assert tok.decode(ids[:1]) == "�"  # lossy: replacement character
    assert tok.decode(ids) == "é"


@validates("tokens-not-words")
def test_without_pre_tokenization_a_token_can_span_several_words():
    tok = bpe.train(CORPUS, 150, pre_tokenizer="none")
    pieces = texts(tok, tok.encode("The keeper lit the lantern at dusk."))
    assert any(len(p.split()) >= 2 for p in pieces), pieces


@validates("counts-tokenizer-specific")
def test_the_same_text_gets_different_counts_under_different_tokenizers():
    text = "The keeper lit the lantern before the tide turned."
    counts = {
        (pre, merges): len(bpe.train(CORPUS, merges, pre_tokenizer=pre).encode(text))
        for pre in ("words", "none") for merges in (0, 50, 200)
    }
    assert len(set(counts.values())) >= 4, counts


@validates("subword-open-vocabulary")
def test_unseen_words_are_spelled_from_known_subwords():
    tok = bpe.train(CORPUS, 216)
    word = " lanternkeepers"
    assert word.strip() not in CORPUS
    pieces = texts(tok, tok.encode_piece(word))
    assert 1 < len(pieces) < len(word.encode())
    assert pieces[0] == " lantern" and "".join(pieces) == word
    learned = {tok.vocab[m.new_id].decode() for m in tok.merges}
    assert " lantern" in learned


# --------------------------------------------------------------- challenges
KNOWN_FIXES = {
    "unknown-characters": {"base": "bytes"},
    "too-many-tokens": {"merges": 150},
    "merges-out-of-order": {"merge_order": "learned"},
    "merging-across-words": {"pre_tokenizer": "words"},
}


@validates("bpe-apply-in-order", "byte-level-no-unk", "bpe-no-cross-word", "vocab-length-tradeoff")
@pytest.mark.parametrize("challenge_id", list(KNOWN_FIXES))
def test_challenge_fails_when_broken_and_passes_when_fixed(lesson, challenge_id):
    ch = next(c for c in lesson.challenges if c.id == challenge_id)
    broken = pipeline.run(pipeline.TokenizeParams(**ch.broken_params))
    assert not evaluate_challenge(ch, broken)["passed"]
    fix = KNOWN_FIXES[challenge_id]
    assert not set(fix) & set(ch.locked_params), "the fix must use an unlocked control"
    fixed = pipeline.run(pipeline.TokenizeParams(**{**ch.broken_params, **fix}))
    assert evaluate_challenge(ch, fixed)["passed"]


def test_challenge_briefs_describe_what_the_broken_settings_do(lesson):
    by_id = {c.id: c for c in lesson.challenges}
    unk = pipeline.run(pipeline.TokenizeParams(**by_id["unknown-characters"].broken_params))
    unknown_chars = [ch for ch in unk["input"]["text"] if ch not in CORPUS]
    assert set(unknown_chars) == {"C", "é", "è", "☕"} and unk["decoding"]["unk_count"] == 4
    cross = pipeline.run(pipeline.TokenizeParams(**by_id["merging-across-words"].broken_params))
    assert {" the ", "d the "} <= set(cross["vocabulary"]["crossing_word_boundary"])
    order = pipeline.run(pipeline.TokenizeParams(**by_id["merges-out-of-order"].broken_params))
    base = bpe.train(CORPUS, 0)
    tok = bpe.train(CORPUS, 200)
    for t in order["encoding"]["tokens"]:
        # In reverse order only merges of two single bytes can fire.
        assert len(tok.token_bytes(t["id"])) <= 2 or t["id"] in base.vocab


def test_every_challenge_has_a_known_fix(lesson):
    assert {c.id for c in lesson.challenges} == set(KNOWN_FIXES)


# --------------------------------------------------------------------- API
def test_tokenize_run_persists_and_config(client, engine):
    from sqlmodel import Session, select

    from app.db import ExperimentRun

    r = client.post("/api/experiments/tokenize/run", json={"text": "Tide at 04:15.", "merges": 40}, headers=LEARNER)
    assert r.status_code == 200 and r.json()["decoding"]["round_trip"]
    with Session(engine) as s:
        runs = s.exec(select(ExperimentRun).where(ExperimentRun.experiment_id == "tokenization")).all()
    assert len(runs) == 1 and runs[0].summary["tokens"] == r.json()["encoding"]["count"]
    cfg = client.get("/api/experiments/tokenize/config").json()
    assert cfg["stages"] == pipeline.STAGES and cfg["max_merges"] == pipeline.MAX_MERGES


def test_tokenize_rejects_bad_params(client):
    assert client.post("/api/experiments/tokenize/run", json={"merges": -1}).status_code == 422
    assert client.post("/api/experiments/tokenize/run", json={"text": ""}).status_code == 422


def test_tokenize_challenge_enforces_locked_params(client):
    url = "/api/experiments/tokenize/challenges/tokenization/merges-out-of-order/check"
    # "Fixing" by changing the locked merge count is forced back to 200 → still broken.
    cheat = client.post(url, json={"merges": 0, "merge_order": "reversed"}, headers=LEARNER).json()
    assert cheat["result"]["params"]["merges"] == 200 and not cheat["passed"]
    fixed = client.post(url, json={"merge_order": "learned"}, headers=LEARNER).json()
    assert fixed["passed"]


def test_challenge_routes_refuse_the_other_engine(client):
    assert client.post("/api/experiments/tokenize/challenges/rag-pipeline/ranking-miss/check",
                       json={}, headers=LEARNER).status_code == 404
    assert client.post("/api/experiments/rag/challenges/tokenization/unknown-characters/check",
                       json={}, headers=LEARNER).status_code == 404


def test_progress_accepts_tokenization_ids(client):
    url = "/api/progress/tokenization"
    out = client.put(url, json={"explored_components": ["merge_learner", "chunker"],
                                "solved_challenges": ["unknown-characters"]}, headers=LEARNER).json()
    assert out["explored_components"] == ["merge_learner"]
    assert out["solved_challenges"] == ["unknown-characters"]
