# Tokenization verification

Research and verification report for **Lesson 02 · Tokenization, exploded**
(`content/lessons/tokenization/lesson.yaml`, version 1.0.0, status **published**).
Completed 2026-10-19.

> Three verification passes give each claim recorded, inspectable evidence. They
> do not guarantee absolute correctness. Provider documentation changes often;
> every source records the date it was read.

## Summary

| | |
|---|---|
| Claims | 32 (7 provider-specific: OpenAI/tiktoken ×4, Anthropic ×2, Google ×1) |
| Citations | 70 excerpts (each ≤ 25 words) from 18 sources: 5 papers, Hugging Face and tiktoken docs and source pinned to a version, Anthropic, Google and OpenAI docs |
| Pass 1 (primary-source research) | 32/32 passed |
| Pass 2 (independent cross-check) | 22 confirmed · 10 confirmed with changes · 0 disputed · 0 unverifiable. 64 of 65 excerpts found in the raw sources; the missing one was replaced |
| Pass 3 (technical validation) | 19 executed and passing · 13 not applicable, each with a reason |
| Automated gates | content validator ✓ · claim-coverage gate ✓ (per lesson) · 138 backend tests · 25 frontend unit tests · 19 end-to-end tests (9 for Lesson 02, plus a phone-layout test) |

**What this lesson's tokenizer is.** Every "real execution" in the lesson runs
ExplodeAI's own **educational BPE** (`backend/app/experiments/tokenize/`) on a 1 KB
fictional corpus. It follows the published algorithm, but it is **not any
provider's tokenizer**. The UI, the API (`label`) and the lesson's corpus note all
say so. No provider tokenizer, token-counting endpoint or paid API was called at
any stage, and no key was used.

## Pass 1 — primary-source research

Done with the `deep-research` skill: three parallel researchers (algorithm papers;
tokenizer libraries; provider token-counting docs), then a report writer.
Every excerpt came from raw downloads (curl, PDF text extraction, raw GitHub files
pinned to a tag or commit), checked by script. None came through a summarising fetch.

- Notes: `research_notes/Tokenization primary sources/` (`tokenizer_papers.md`, `tokenizer_libraries.md`, `provider_token_counting.md`)
- Synthesis: `reports/Tokenization primary sources.md` (source register, ~200-row claims table, 20 conflicts, 20 gaps)

Corrections and caveats Pass 1 caught before any lesson text was written:
- Sennrich et al. only *imply* that merges are applied in learned order; the Hugging Face course states it. Both are cited.
- GPT-2's paper gives the 50,257 total but not its breakdown; the Transformers docs give 256 + 50,000 + 1 (also matched by tiktoken's source).
- tiktoken calls BPE "reversible and lossless", but its own `decode` docstring warns decoding is lossy when a slice of tokens splits a UTF-8 character. The lesson teaches both.
- Anthropic gives "approximately 30%" more tokens for its newer tokenizer on three pages and "1x to 1.35x" in a migration guide. The claim is dated and cites both.
- OpenAI's help article and Tokenizer page returned HTTP 403 and were not cited. No OpenAI platform doc names `o200k_base`, so that claim cites tiktoken's `model.py` at tag 0.14.0.
- No provider says outright "don't compare token counts across providers". The lesson presents that as an inference from each provider's tokenizer-specific statements, and the Pass 1 note says so.

## Pass 2 — independent cross-check

A separate agent, which did not write the lesson, re-downloaded every cited source,
string-matched all 65 excerpts (24 exact, 16 after whitespace collapse, 23 loose,
1 letters-and-digits only) and found at least one independent source per claim.
These included GPT-2's released `vocab.bpe` / `encoder.json`, whose hashes match
tiktoken's, as well as `subword-nmt` and the SentencePiece docs. It also reviewed all
non-claim text against the code. Full report:
`research_notes/Tokenization primary sources/pass2_cross_check.md`.

Changes applied:
- `bpe-vocab-formula`: Added "(plus any special tokens)", because the app's own vocabulary counts one.
- `bpe-deterministic`: Scoped to standard BPE, with BPE-dropout (Provilkov et al.) added as the randomised variant.
- `sentencepiece-lossless`: Reworded: decoding returns the normalised text, which is not necessarily the original.
- `real-merge-counts`: Scoped Sennrich's figures to English→German, and corrected the corpus limit to 216 merges.
- `special-tokens`: Added a tiktoken excerpt for the first sentence, and noted that ExplodeAI does not copy tiktoken's refusal.
- `hf-pipeline`: Dropped "only", and replaced an excerpt that did not support the four-stage list.
- `vocab-length-tradeoff`: Added the plateau: once words are single tokens, more merges stop helping.
- `anthropic-count-tokens`: Narrowed "the same inputs", because the endpoint rejects a few (server tools, URL-sourced files).
- `anthropic-new-tokenizer`: Dated it, and added the Opus 5.5 migration guide's 1x–1.35x range.
- `tokens-meter-usage`: The Gemini excerpt was **not on the page**, and the current page contradicts it for newer models. It was replaced with two verbatim excerpts.

The three excerpts added on Pass 2's advice (BPE-dropout abstract, Anthropic
migration guide, Anthropic token-counting exceptions) were re-fetched and
string-matched by the author before use. The migration guide differs only by a
Markdown escape (`\~`).

Non-claim text corrected after Pass 2:
- The `unknown-characters` brief omitted the capital "C" of "Café", which is also [UNK] because the corpus has no capital C. Brief and hint fixed; a test now pins the four unknown characters.
- The `merging-across-words` brief named "the " as a learned token, but at 150 merges the learned tokens are " the " and "d the ". Fixed and tested.
- The `merges-out-of-order` explanation said "only the earliest merges" fire. The precise statement is that only merges joining two single bytes can fire. Fixed and tested.
- `decoder.detail` said the round trip is exact "when the alphabet is bytes". It is exact whenever no token is [UNK]. Fixed.
- `vocabulary.detail` now notes that [UNK] counts as part of the base alphabet in character mode.
- The trade-off visual said "retraining". The sweep replays the first *n* learned merges of one run, which is identical to retraining (tested). Its bytes-per-token figures are in-sample, and both the description and the table header now say so.
- The Numbers preset is labelled "(none in the corpus)", since digits stay one byte each.
- In sources.yaml, `tiktoken_readme` is pinned to the 0.14.0 tag, the Cookbook to its commit, and `provilkov2020bpedropout` (arXiv v2) and `anthropic_opus55_migration` are added.

## Pass 3 — technical validation

Executable evidence lives in the backend `pytest` suite (`backend/tests/test_tokenize.py`).
Every test runs ExplodeAI's educational BPE, so it demonstrates the property a
claim describes, not the behaviour of any provider's trained tokenizer.

Highlights:
- **Independent reference implementation.** A naive BPE written separately inside the test learns exactly the same merge list as `bpe.py` over the full corpus. Replaying merges in learned order reproduces every training word's final segmentation.
- **Merge-order properties.** Each learned merge is the most frequent pair at its step (recomputed independently). Training with *n* merges equals the first *n* of a longer run (prefix property). Reversed replay leaves frequent words fragmented, and only two-byte merges fire.
- **Round-trip properties.** At 0, 30 and 216 merges, 300 random mixed-script strings each (ASCII, accents, CJK, emoji with ZWJ, combining marks, odd whitespace, `<|endoftext|>`) encode with no unknown token and decode exactly. Pre-tokenized pieces always concatenate back to the input.

Per claim:
- `subword-open-vocabulary`: Evidence: test_unseen_words_are_spelled_from_known_subwords.
- `bpe-training-loop`: Evidence: test_bpe_matches_an_independent_reference_implementation; test_each_merge_is_the_most_frequent_pair_at_that_step.
- `bpe-frequency-weighted`: Evidence: test_training_on_a_word_frequency_dictionary_equals_training_on_the_text.
- `bpe-vocab-formula`: Evidence: test_vocabulary_is_base_plus_merges_plus_special.
- `bpe-no-cross-word`: Evidence: test_word_pre_tokenization_keeps_every_merge_inside_a_word; test_challenge_fails_when_broken_and_passes_when_fixed.
- `bpe-apply-in-order`: Evidence: test_bpe_matches_an_independent_reference_implementation; test_challenge_fails_when_broken_and_passes_when_fixed.
- `bpe-deterministic`: BPE half only; the unigram half rests on the source. Evidence: test_training_and_encoding_are_deterministic_and_merges_are_a_prefix.
- `gpt2-byte-level`: Consistency of ExplodeAI's byte alphabet; the 130,000 figure rests on the paper. Evidence: test_byte_level_base_alphabet_has_exactly_256_symbols.
- `byte-level-no-unk`: Property test on random mixed-script text. Evidence: test_byte_level_bpe_round_trips_arbitrary_text_without_unknowns; test_challenge_fails_when_broken_and_passes_when_fixed.
- `char-bpe-unk`: Evidence: test_character_alphabet_turns_unseen_characters_into_unknowns.
- `gpt2-character-categories`: ExplodeAI's simplified GPT-2-style pattern, not GPT-2's own regex. Evidence: test_letters_and_punctuation_are_never_merged_together.
- `leading-space`: Evidence: test_a_space_belongs_to_the_next_word.
- `real-merge-counts`: Only the sentence about ExplodeAI's corpus is executable. Evidence: test_training_stops_when_no_pair_is_left.
- `special-tokens`: Only ExplodeAI's own behaviour is executable; tiktoken's refusal rests on its source. Evidence: test_special_token_text_in_the_input_is_encoded_as_plain_text.
- `vocab-length-tradeoff`: Evidence: test_more_merges_grow_the_vocabulary_and_shorten_sequences; test_challenge_fails_when_broken_and_passes_when_fixed.
- `byte-bpe-lossless`: On ExplodeAI's educational BPE, not tiktoken. Evidence: test_byte_level_bpe_round_trips_arbitrary_text_without_unknowns.
- `decode-partial-lossy`: Evidence: test_one_character_can_span_tokens_and_a_slice_of_them_is_not_valid_utf8.
- `tokens-not-words`: Evidence: test_one_character_can_span_tokens_and_a_slice_of_them_is_not_valid_utf8; test_without_pre_tokenization_a_token_can_span_several_words.
- `counts-tokenizer-specific`: Shown across ExplodeAI tokenizer settings, not provider tokenizers. Evidence: test_the_same_text_gets_different_counts_under_different_tokenizers.

Diagram, animation and challenge consistency (also in `test_tokenize.py`):
- The 3D components equal the executed stages, in order. The diagram edges equal `STAGE_DEPENDENCIES`, which is also the rebuild graph. Any topological order is accepted, and an encoder placed before the vocabulary is rejected.
- Each of the four break/fix challenges fails in its broken state and passes with a known fix that uses only unlocked controls. The server forces locked params back to their broken values (API test). Each challenge brief matches what its broken settings actually do.
- The challenge check types are validated per engine (`ENGINE_CHECKS`). A RAG check in the tokenization lesson is a validation error, and each engine's challenge route refuses the other engine's lessons.
- Every visual declares its kind, and the experiment visual, the corpus note and the API label all say "not any provider's tokenizer".

Not executable (`not_applicable`):
- `bpe-compression-origin`: Historical fact about the algorithm's origin.
- `sentencepiece-raw-text`: ExplodeAI's educational tokenizer does not implement SentencePiece.
- `sentencepiece-vocab-size`: Describes SentencePiece's configuration; ExplodeAI's slider sets merges, as in Sennrich et al.
- `sentencepiece-lossless`: ExplodeAI does not implement SentencePiece or NFKC normalisation. The byte-level round trip is tested under byte-bpe-lossless.
- `gpt2-vocab-size`: Fact about a released model. ExplodeAI mirrors the same formula (base + merges + 1 special), tested under bpe-vocab-formula.
- `hf-pipeline`: Describes a library's architecture.
- `tiktoken-model-encodings`: Needs OpenAI's trained encodings; ExplodeAI ships no provider tokenizer.
- `bytes-per-token`: An average over OpenAI's trained encodings and real text. ExplodeAI's toy vocabulary shows the trend, not this value.
- `openai-rule-of-thumb`: Provider rule of thumb; checking it would need OpenAI's tokenizer and a representative corpus.
- `gemini-tokens`: Provider documentation; ExplodeAI never calls provider APIs.
- `anthropic-count-tokens`: Provider feature; ExplodeAI never calls provider APIs or uses keys.
- `anthropic-new-tokenizer`: Needs Claude's tokenizer, which is not public; ExplodeAI never calls provider APIs.
- `tokens-meter-usage`: Provider pricing and limits; not executable offline.

## Test results

Run on 2026-10-19 against the working tree, with both lessons published. Every gate in `make test` passed:

| Gate | Result |
|---|---|
| `make validate` | rag-pipeline 32/32 · tokenization 32/32 claims fully verified · content validation ok |
| `make test-backend` | 138 passed (48 in `test_tokenize.py`; the coverage gate runs for each lesson and checks claim ids are unique across lessons) |
| `make test-frontend` | typecheck clean · 25 unit tests passed (9 for Lesson 02, using a real backend run as fixture) |
| `make e2e` | 19 passed: 9 in `tokenization.spec.ts`, 1 tokenization phone-layout test in `mobile.spec.ts`, and the Lesson 01 suite |
| lint | ruff ✓ · oxlint ✓ |

The e2e suite ran on alternate ports (`E2E_API_PORT=8300 E2E_WEB_PORT=5374`) because another session was using the defaults at the same time. Default ports behave the same.

## Browser check

The lesson was opened in the built-in browser against a local backend
(desktop 1360×900 and phone 375×812; dark and light themes). Checked by eye:
- the 3D scene with live readouts on every part;
- the experiment's Tokens view (partial-byte and [UNK] tokens are labelled);
- the Replay stepper;
- the Merges table;
- the trade-off chart and its data table;
- no horizontal scroll at phone width.

Two issues found and fixed:
- a truncated pre-tokenizer readout;
- token chips that were too wide on phones.

A third issue came from the mobile e2e test: example chips were 36px on touch screens, below the UI's 44px target. They now reach 44px on coarse pointers, which also benefits Lesson 01.

## Clearly labelled non-claims

- **Conceptual:** the exploded layout and shapes, and the moving data-flow packets.
- **Real execution · educational BPE:** pre-tokenization, the base alphabet, merge training, encoding, decoding and stage timings.
- **Real execution, replayed:** the merge replay. It steps through the backend's recorded trace and recomputes nothing.
- **Real data, tiny corpus:** the trade-off chart. Its bytes-per-token figures are in-sample.
- **Fictional sample data:** the lighthouse keeper's log (12 entries, 1,045 ASCII characters).

## Residual risks

- **Provider docs move.** Anthropic's tokenizer change, Gemini's rules of thumb, OpenAI's concepts page and tiktoken's model map are dated 2026-10-18/19 and will go stale. The Anthropic 30% figure already conflicts with the migration guide's 1.35x. Both are shown.
- **Simplified pre-tokenizer.** ExplodeAI's pattern approximates GPT-2's with Python `re` (`[^\W\d_]` for `\p{L}`). A few characters are categorised differently, such as "²" grouping with letters. The lesson calls it "simplified" and never says it equals GPT-2's.
- **Toy scale.** With 216 merges on 1 KB of text, the trade-off curve has the right shape but production magnitudes are absent. Bytes per token (about 4.4 at the limit) is in-sample and must not be compared with tiktoken's "about 4 bytes"; the UI labels it in-sample.
- **Inference, not quotation.** "Don't reuse token counts across providers" is inferred from provider statements that counts are tokenizer- and model-specific. No source states it in those words.
- **Gage 1994** was read only on a third-party mirror in Pass 1 and is not cited directly. The lesson cites Sennrich's description of it.
