# Tokenization — Pass 2 independent factual cross-check

Date: 2026-10-19. Inputs: `content/lessons/tokenization/lesson.yaml` (32 claims, 65 excerpts, plus component, challenge, tour, visual and corpus-note text), the "Lesson 02: tokenization" section of `content/sources.yaml`, and the implementation in `backend/app/experiments/tokenize/` (`bpe.py`, `pipeline.py`, `corpus.py`) and `backend/app/routers/tokenize.py`.

## Method

- Every cited source was downloaded with curl into an empty scratch directory and converted to plain text: PDFs with pypdf, HTML with BeautifulSoup (scripts and styles removed), the Cookbook notebook by joining its cell sources, and everything else read as raw text. Sources fetched:
  - arXiv PDFs: Sennrich v5 (1508.07909v5), Kudo SentencePiece v1 (1808.06226v1), Kudo subword regularization v1 (1804.10959v1). The ACL Anthology PDFs P16-1162 and D18-2012 were also fetched.
  - The GPT-2 PDF from cdn.openai.com.
  - tiktoken `README.md`, `tiktoken/core.py`, `tiktoken/model.py` and `tiktoken_ext/openai_public.py` from raw.githubusercontent.com at tag `0.14.0`. `git ls-remote` confirms the tag points to commit `4e71bbe0c078468e00fefbf94b39849389f346e5`, as sources.yaml records.
  - The Cookbook notebook at commit `db3144982aa2` and at `main`. The two are byte-identical.
  - The Hugging Face pages, both rendered HTML (tags stripped) and the pinned sources: `tokenizers@3fe1b852de47` `pipeline.mdx` and `components.mdx`, `course@e05c3b637f0a` `chapter6/5.mdx`, and `transformers@83eb94c1febf` `tokenizer_summary.md`.
  - The `.md` variants of the Anthropic platform.claude.com pages.
  - The rendered HTML of ai.google.dev and developers.openai.com.
- Each excerpt was matched against that text in four steps:
  1. **strict**: exact substring;
  2. **strict-ws**: exact after collapsing whitespace and line breaks;
  3. **loose**: NFKC (which unfolds PDF ligatures such as "ﬁ"), PDF hyphenation re-joined, curly quotes made straight, Markdown backticks, bold and link syntax removed, case ignored;
  4. **loose-alnum**: letters and digits only, used for HTML where inline `<code>` or `<em>` adds stray spaces.

  When a match was only loose, the surrounding passage was read by eye. No summarising fetch tool was used to confirm any excerpt.
- Independent sources are sources not cited for that claim. They were downloaded and their excerpts confirmed the same way. All of the 69 proposed replacement and independent excerpts in this report matched (strict or loose). Extra files checked:
  - GPT-2's released `vocab.bpe` and `encoder.json` from openaipublic.blob.core.windows.net. Their SHA-256 hashes match the `expected_hash` values in tiktoken's `openai_public.py`.
  - `openai/gpt-2` `src/encoder.py`, `rsennrich/subword-nmt` `apply_bpe.py`/`learn_bpe.py`, and the `google/sentencepiece` README and docs. Pinned HEAD commits are listed under Independent sources below.
  - The BPE-dropout abstract, via the arXiv export API.
  - RFC 3629.
  - Anthropic's pricing, context-windows, models-overview, Opus 5.5 migration-guide and count_tokens API reference pages.
  - The Gemini API `countTokens` reference and the Vertex AI token-count page.
- The implementation was checked by importing the backend modules into a read-only script and running them on the sample corpus, the four presets and the four challenges' `broken_params`. No code was modified. No provider API was called, no token-counting endpoint was used, and no keys were used. Two pages returned 403 and were not used: help.openai.com and platform.openai.com/tokenizer.

## Summary

| Verdict | Count |
|---|---|
| confirmed | 22 |
| confirmed_with_changes | 10 |
| disputed | 0 |
| unverifiable | 0 |

**64 of 65 excerpts were found in their cited source.** Taking the best match in any of a source's files, 24 matched strictly, 16 after collapsing whitespace, 23 loosely and 1 on letters and digits only (the Gemini `count_tokens` sentence). The loose matches differ from the source only in PDF ligatures and hyphenation, Markdown backticks, bold or link markup, and HTML inline-code spacing. **One excerpt failed:** the `gemini_tokens` excerpt for `tokens-meter-usage` ("The context window defines the combined limit of input and output tokens.") is not on the page. That is true of the HTML, the `?hl=en` variant and the Gemini long-context page alike, and the page carries the same "Last updated 2026-10-13" that sources.yaml records. No other excerpt looks fabricated.

### Most important problems, in priority order

1. **`tokens-meter-usage`: the Gemini excerpt does not exist, and the current page contradicts it for some models.** The page's "Context window" section now reads: "Each Gemini model has a maximum number of tokens it can handle." It also says Gemini 4 models "Share a single 1M-token context window … across input, thinking, and output tokens", while "Gemini 3 and 2.5 models: Use separate input (1,048,576 tokens) and output (65,536 tokens) budgets." A "combined limit of input and output tokens" is therefore wrong for Gemini 3 and 2.5. The claim text itself ("Providers measure prices and context windows in tokens") is fine. Replace the excerpt (see below).
2. **Challenge `unknown-characters`: the brief misdescribes what the learner will see.** It says "The accented letters and the emoji come out as [UNK]." Running the broken params gives **4** unknowns: `[UNK] a f [UNK] ␠c r [UNK] me …`. The capital **"C"** of "Café" is unknown too, because the corpus has no capital C (its 32 distinct characters include only the capitals A, F, R and T). The fix (switching to bytes) still passes, but the brief and hint should mention it.
3. **Challenge `merging-across-words`: the brief names a token that is not learned.** With `pre_tokenizer: none` and 150 merges, the learner produces 84 boundary-crossing tokens, including "d the ", " the ", "The " and "he ", but **not "the "**. The brief's example should be " the " (or "The "), not "the ".
4. **`real-merge-counts`: "runs out after a few hundred" overstates it.** With the default `words` pre-tokenizer, training stops at **216 merges** (vocab 473 with bytes, 250 with chars). With `none` it stops at 406, which is beyond the slider's `MAX_MERGES = 300`, so a learner never sees that run out. The Sennrich figures are also specific to English→German (Table 1 gives German-side statistics; the systems are named BPE-60k and BPE-J90k).
5. **`bpe-deterministic` needs "standard".** BPE-dropout (Provilkov et al.) "stochastically corrupts the segmentation procedure of BPE". Both subword-nmt (`# get list of symbol pairs; optionally apply dropout`) and SentencePiece ("BPE-Dropout for BPE") ship that option. Plain BPE inference is deterministic, but BPE as a family is not always.
6. **`anthropic-new-tokenizer` is dated and gives one figure where Anthropic gives a range.** The token-counting, pricing and glossary pages say "approximately 30 percent more". The Opus 5.5 migration guide says "roughly 1x to 1.35x … (up to ~35% more, varying by content)". The claim should give the range and say the increase depends on content.
7. **`anthropic-count-tokens` says "the same inputs as a message", but the page lists exceptions.** "This endpoint returns an `invalid_request_error` for a few inputs that the Messages API accepts": server tools, the MCP connector, and `image`/`document` blocks with a `url` or `file` source.
8. **`sentencepiece-lossless` is worded misleadingly.** "The original text comes back only after normalisation" can be read as "you get the original text back". The paper says what comes back is *the normalised text*. The current docs also say the default rule is `nmt_nfkc`, a "custom variant" of NFKC that also normalises spaces, not plain NFKC.
9. **The excerpts for `hf-pipeline` and `special-tokens` don't cover parts of their claims.** For `hf-pipeline`, the pre-tokenization excerpt does not support the four-stage list, and "Only the model is trained" is an inference. For `special-tokens`, nothing supports "sit outside the merge rules". Verbatim support is given below.
10. **Consistency between the claims and what the code shows.** `bpe-vocab-formula` ("starting alphabet plus one new symbol per merge") leaves out the special token, but the experiment reports `vocab_size` 257 at 0 merges (256 + 0 + `<|endoftext|>`). `vocab-length-tradeoff` says more merges mean "fewer tokens per text", but the sweep for the default sentence stays at 8 tokens from 100 merges onward. Both claims should allow for this.

---

## Per-claim results

### bpe-compression-origin — confirmed
- **Excerpt check.** §1 excerpt: strict-ws in both v5 and ACL. §3.2 excerpt: loose (hyphenation). The source sentence begins "Byte Pair Encoding (BPE) (Gage, 1994) is a simple data compression technique that iteratively replaces…".
- **Independent source.** HF LLM Course ch. 6.5 https://huggingface.co/learn/llm-course/chapter6/5 — "Byte-Pair Encoding (BPE) was initially developed as an algorithm to compress texts". It is not cited for this claim. Gage (1994) itself could not be downloaded (the mirror timed out), so the original paper was not checked directly.
- **Notes.** Gage replaces a pair with "a single, unused byte", which the claim's "a new symbol" covers. "Adapted it in 2016" is fine for the ACL paper; the preprint is from August 2015, and GPT-2 cites it as "Sennrich et al., 2015". Optional: "(arXiv 2015, ACL 2016)".

### subword-open-vocabulary — confirmed
- **Excerpt check.** Abstract excerpt: loose (hyphenation). "In our example, the OOV ‘lower’ would be segmented into ‘low er·’." is strict-ws.
- **Independent sources.** HF Transformers *Tokenization algorithms* — "Subword splitting lets the model represent unseen words from known subwords." HF Tokenizers *Components* — "BPE is able to build words it has never seen by using multiple subword tokens".
- **Notes.** Sennrich's footnote 3 limits this: "The only symbols that will be unknown at test time are unknown characters" (and fully merged-away symbols). The lesson already covers that case under `char-bpe-unk`.

### bpe-training-loop — confirmed
- **Excerpt check.** Sennrich: loose (hyphenation). HF course: strict.
- **Independent source.** HF Transformers *Tokenization algorithms* — "BPE starts with individual characters and iteratively merges the most frequent adjacent pair."
- **Code.** `bpe.train` does exactly this, weighting by piece frequency. Ties are broken by `(-count, left bytes, right bytes)`. Sennrich's Algorithm 1 uses `max(pairs, key=pairs.get)` and has no explicit tie rule.

### bpe-frequency-weighted — confirmed
- **Excerpt check.** strict-ws.
- **Independent source.** HF Transformers — "A pre-tokenizer splits text on whitespace or other rules, producing a set of unique words and their frequencies."
- **Code.** Matches `train()`: `words` holds each distinct piece once, and `freq` weights its pairs.

### bpe-vocab-formula — confirmed_with_changes (special tokens)
- **Excerpt check.** Both Sennrich excerpts: loose (ligature "ﬁnal", hyphenation; the source reads "…merge operations – the latter is the only hyperparameter…"). HF Transformers: strict.
- **Independent source.** GPT-2's released files: `vocab.bpe` has 50,000 merges after the `#version: 0.2` header, and `encoder.json` has 50,257 entries with `<|endoftext|>` = 50256. tiktoken `openai_public.py@0.14.0`: `"explicit_n_vocab": 50257,` and `"special_tokens": {ENDOFTEXT: 50256},`. So 256 + 50,000 merges, plus one special token.
- **Notes.** As a statement about Sennrich's algorithm, the claim is right. Real tokenizers add special tokens on top, and ExplodeAI counts one: `vocab_size` = 257 at 0 merges with bytes, and 33 + merges + 1 with chars, where the 33 includes [UNK]. Sennrich also notes that the network vocabularies were "typically slightly smaller" than the symbol counts.
- **Fix.** "The final vocabulary is the starting alphabet plus one new symbol per merge (plus any special tokens), so the number of merges is what sets the vocabulary size."

### bpe-no-cross-word — confirmed
- **Excerpt check.** loose (ligature "efﬁciency").
- **Independent source.** HF Tokenizers *The tokenization pipeline* — "the pre-tokenizer will split your text into "words" and then, your final tokens will be parts of those words." This sentence is cited under `hf-pipeline` but not here.
- **Notes.** Sennrich gives efficiency as the reason. The rule holds for Sennrich's BPE and for regex-pre-tokenized BPE. SentencePiece's `split_by_whitespace` (default `true`) can be turned off, which allows cross-word pieces. The claim is scoped to Sennrich, so it is fine.
- **Code.** With `words`, 150 merges give 0 crossing tokens. With `none`, they give 84.

### bpe-apply-in-order — confirmed
- **Excerpt check.** Sennrich: loose (ligature "ﬁrst", hyphenation). HF course: strict.
- **Independent sources.** openai/gpt-2 `src/encoder.py` — `bigram = min(pairs, key = lambda pair: self.bpe_ranks.get(pair, float('inf')))`. subword-nmt `apply_bpe.py` — "#get first merge operation in list of BPE codes".
- **Notes.** Reference implementations repeatedly merge the lowest-ranked pair that is present. ExplodeAI instead walks the whole merge list in rank order. The two give the same result, because each symbol is created by exactly one merge, so a pair that contains a new symbol always ranks later. The Pass 1 note "Sennrich implies the order" is fair.

### bpe-deterministic — confirmed_with_changes (scope: standard BPE)
- **Excerpt check.** Both Kudo excerpts: loose (hyphenation, ligature "ﬂexible"). Locators §3.1 and §3.4 are correct.
- **Independent sources.** HF Transformers — "Unlike BPE, which is deterministic and based on merge rules, Unigram is probabilistic and can sample different tokenizations during training." HF Tokenizers *Components*, Unigram row — "Unigram will be able to compute multiple ways of tokenizing, while choosing the most probable one."
- **Qualifier.** Provilkov et al., *BPE-Dropout* https://arxiv.org/abs/1910.13267 describes BPE's deterministic nature as an "imperfection" and adds randomness: "It stochastically corrupts the segmentation procedure of BPE, which leads to producing multiple segmentations within the same fixed BPE framework." subword-nmt and SentencePiece both ship the option.
- **Fix.** "Standard BPE is deterministic, so the same text always gets the same tokens. The unigram language model, an alternative, can produce several segmentations of the same text, each with a probability. (Variants such as BPE-dropout add randomness on purpose during training.)"

### sentencepiece-raw-text — confirmed
- **Excerpt check.** Abstract: strict-ws (v1 and ACL). §3.1: loose (ligature "ﬁrst"). The PDF text layer renders "▁" as "_", as the locator already says.
- **Independent sources.** SentencePiece README (`google/sentencepiece@d6b191ec50dc`) — "It does **not** require language-specific pre-tokenizers (such as Moses, MeCab, or KyTea)." and "It escapes whitespaces with a meta-symbol `▁` (U+2581) and includes it in the tokenization." HF Course ch. 6.4 — "it doesn't even require a pre-tokenization step, which is very useful for languages where the space character is not used".
- **Notes.** The current default `split_by_whitespace: true` still uses spaces as piece boundaries during training, but that is not language-specific word splitting. Fine as worded.

### sentencepiece-vocab-size — confirmed
- **Excerpt check.** Both: loose (ligatures "speciﬁes", "ﬁnal", hyphenation). §3.3 is correct.
- **Independent sources.** SentencePiece README — "where the vocabulary size is fixed prior to training." `doc/options.md` — "**`vocab_size`** (int32, default: `8000`)".

### sentencepiece-lossless — confirmed_with_changes (wording, default rule)
- **Excerpt check.** The §3.1 excerpt is strict-ws in arXiv v1. **The ACL D18-2012 PDF ends "= Normalize(text):" with a colon, not a full stop**, so it matches only on letters and digits. sources.yaml lists v1 first, so the excerpt is correct for v1. The §3.4 excerpt is loose (hyphenation).
- **Claim vs source.** The paper says "all the information to reproduce the normalized text is preserved". Decoding returns *Normalize(text)*, not the original text. "The original text comes back only after normalisation" can be misread.
- **Independent sources.** SentencePiece `doc/normalization.md` — "By default, SentencePiece normalizes input sentences using a custom variant of Unicode **NFKC** normalization". `nmt_nfkc` is "NFKC normalization with additional space-related normalization … This is the **default** rule." HF Course ch. 6.4 — decoding "results in the normalized text".
- **Fix.** "SentencePiece's decoder is the exact inverse of its encoder on normalised text, which its authors call lossless tokenization. What comes back is the normalised text (by default a variant of NFKC), which matches the original only if normalisation left it unchanged."

### gpt2-byte-level — confirmed
- **Excerpt check.** Both: strict-ws. Context: "reference BPE implementations often operate on Unicode code points and not byte sequences."
- **Independent sources.** HF Tokenizers *Components* (ByteLevel row, not cited for this claim) — "only requires **256** characters as initial alphabet (the number of values a byte can have), as opposed to the 130,000+ Unicode characters." openai/gpt-2 `encoder.py` — "This means you need a large # of unicode characters in your vocab if you want to avoid UNKs."
- **Currency.** Unicode now assigns well over 130,000 characters, so "over 130,000" is still true.

### byte-level-no-unk — confirmed
- **Excerpt check.** All three strict.
- **Independent sources.** GPT-2 §2.2 — "Since our approach can assign a probability to any Unicode string". HF Transformers — "Byte-level BPE uses 256 byte values as the base vocabulary instead, ensuring every word can be tokenized without the "<unk>" token."
- **Notes.** One API edge case: by default tiktoken's `encode` *raises an error* on text that matches a special token (see `special-tokens`). That is an API policy, not an alphabet limit, so the claim stands.

### char-bpe-unk — confirmed
- **Excerpt check.** Loose (backticks in the source; inline-code spacing in the HTML).
- **Independent sources.** HF Transformers — "Any character not in the base vocabulary maps to an unknown token like "<unk>"." Sennrich footnote 3 — "The only symbols that will be unknown at test time are unknown characters".
- **Notes.** "The original text cannot be recovered" is not stated in either source, but it follows from [UNK] carrying no information. ExplodeAI shows it: the broken challenge decodes to "�af� cr�me at the lantern �". SentencePiece's `byte_fallback` (default `false`) is the usual production workaround.

### gpt2-character-categories — confirmed
- **Excerpt check.** First: strict-ws. Second and third: loose (hyphenation, ligatures).
- **Independent sources.** openai/gpt-2 `encoder.py` implements the categories as a regex: `'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+`. tiktoken `openai_public.py` — "# The pattern in the original GPT-2 release is:" followed by the same pattern.
- **Notes.** The paper never defines "character categories". In the code they are letters, numbers, other, and whitespace, with English contractions split off. The Pass 1 note is right.

### leading-space — confirmed
- **Excerpt check.** Loose (backticks).
- **Independent sources.** OpenAI *Key concepts* (cited elsewhere, not here) — "Note that in a sentence, the first token of each word typically starts with a space character." GPT-2 `encoder.json` gives "the" = 1169 and "Ġthe" (i.e. " the") = 262, so the two are different tokens.

### gpt2-vocab-size — confirmed
- **Excerpt check.** HF Transformers: strict. GPT-2 §2.3: strict.
- **Independent sources.** GPT-2 released `vocab.bpe` (50,000 merges) and `encoder.json` (50,257 entries, `<|endoftext|>` = 50256), with hashes matching tiktoken's. tiktoken `openai_public.py@0.14.0` `gpt2()`: `"explicit_n_vocab": 50257,`. HF `openai-community/gpt2` config.json: `"vocab_size": 50257`.

### real-merge-counts — confirmed_with_changes (ExplodeAI figure, language pair)
- **Excerpt check.** Sennrich: strict-ws. HF: strict.
- **Code.** `bpe.train(corpus, 100000)` stops at **216** merges with `words` (both alphabets), and at 406 with `none`. The slider cap is 300.
- **Independent sources.** Sennrich Table 2 system names "BPE-60k" and "BPE-J90k" (verbatim row: "BPE-J90k BPE (joint) - 90 000 90 000"). GPT-2 `vocab.bpe` has 50,000 merges.
- **Fix.** "Real systems learn tens of thousands of merges. For English→German, Sennrich et al. used 59,500 (89,500 for joint BPE over both languages), and GPT-2 has 50,000. This lesson's tiny corpus runs out after about 200 (216 with the default pre-tokenizer)."

### special-tokens — confirmed_with_changes (excerpt for first sentence)
- **Excerpt check.** Both: strict / strict-ws in `core.py@0.14.0`. Context: "Special tokens are artificial tokens used to unlock capabilities from a model, such as fill-in-the-middle." `disallowed_special` defaults to `"all"`.
- **Missing support.** Nothing supports "sit outside the merge rules". tiktoken defines `special_tokens` separately from `mergeable_ranks` (`"special_tokens": {ENDOFTEXT: 50256},`). HF Tokenizers *pipeline*, Post-Processing, cited under `hf-pipeline`, adds them "like adding potential special tokens".
- **Independent source.** HF Course ch. 6.5 — "In the case of GPT-2, the only special token is "<|endoftext|>"". Refusing special-token text by default is specific to tiktoken; no other library was found to document it.
- **Code.** ExplodeAI does *not* copy tiktoken's refusal. `encode("<|endoftext|>")` returns 13 ordinary byte tokens, and `test_special_token_text_in_the_input_is_encoded_as_plain_text` asserts this. That is fine, but the lesson text should not imply ExplodeAI refuses.
- **Excerpt fix.** Add a tiktoken_core excerpt such as "Special tokens are artificial tokens used to unlock capabilities from a model, such as fill-in-the-middle." Better, add a source for `tiktoken_ext/openai_public.py@0.14.0` and cite `"special_tokens": {ENDOFTEXT: 50256},` next to its `mergeable_ranks`.

### hf-pipeline — confirmed_with_changes ("only", excerpt)
- **Excerpt check.** All three in both the HTML and `pipeline.mdx@3fe1b852`: two strict-ws, one loose (backticks around `Encoding`).
- **Claim vs source.** The page lists the stages after "When calling `Tokenizer.encode` or `Tokenizer.encode_batch`, the input text(s) go through the following pipeline:". The pre-tokenization excerpt does not support that list. The page says the model "needs training"; it does not say *only* the model does. It does say changing the normaliser or pre-tokenizer calls for retraining, while "you don't need to retrain a tokenizer after changing its post-processor".
- **Independent source.** HF Course ch. 6.4 — "Here's a high-level overview of the steps in the tokenization pipeline:"; the steps are normalization and pre-tokenization, then the model, then post-processing.
- **Fix.** "Hugging Face Tokenizers describes encoding as a pipeline: normalization, pre-tokenization, a model such as BPE, and post-processing. The model is the part trained on a corpus, and post-processing adds any special tokens."
- **Excerpt fix.** Replace the pre-tokenization excerpt with "the input text(s) go through the following pipeline:".

### vocab-length-tradeoff — confirmed_with_changes (monotonic, not strict)
- **Excerpt check.** Sennrich excerpts: loose (hyphenation; the ACL PDF needs letters-and-digits matching for "# tokens"/"# types"). GPT-2 and Kudo: strict-ws.
- **Independent source.** HF Transformers — "They split text into units between words and characters, keeping the vocabulary compact while still capturing meaningful pieces." Sennrich's Table 1 (same paper, uncited passage) gives the extremes for German: characters "550 m" tokens / "3000" types against unsegmented "100 m" / "1 750 000".
- **Code.** For the default sentence, the sweep gives 35, 24, 15, 13, 9, then 8 tokens at 100 merges and 8 thereafter. Corpus tokens fall from 1,045 to 237. More merges never increase a count, but they stop reducing it once each word is a single token.
- **Fix.** Replace the last sentence with: "More merges mean a bigger vocabulary and fewer tokens per text, until the text's words are already single tokens."

### byte-bpe-lossless — confirmed
- **Excerpt check.** strict.
- **Independent sources.** openai/gpt-2 `encoder.py` `decode` joins token bytes and decodes UTF-8 (`.decode('utf-8', errors=self.errors)`). OpenAI Cookbook (cited elsewhere) — "`.decode()` converts a list of token integers to a string."
- **Notes.** This holds when the pipeline applies no normaliser. ExplodeAI applies none: the `words` pattern's pieces always concatenate back to the input, and the presets with emoji and accents round-trip. Pass 3 already tests this (`test_byte_level_bpe_round_trips_arbitrary_text_without_unknowns`).

### decode-partial-lossy — confirmed
- **Excerpt check.** strict-ws ("WARNING: the default behaviour…").
- **Independent sources.** OpenAI Cookbook (not cited for this claim) — "Warning: although `.decode()` can be applied to single tokens, beware that it can be lossy for tokens that aren't on utf-8 boundaries." RFC 3629 §3 — "In UTF-8, characters from the U+0000..U+10FFFF range (the UTF-16 accessible range) are encoded using sequences of 1 to 4 octets."
- **Code.** With 100 merges, `decode(encode("Café ☕")[:-1])` gives "Café �".

### tokens-not-words — confirmed
- **Excerpt check.** Both strict.
- **Independent source.** Gemini *Understand and count tokens* — "Tokens can be single characters like z or whole words like cat. Long words are broken up into several tokens." Note that this sentence covers only the "a token can be a whole word" half; ExplodeAI's own split of "é" into two byte tokens shows the "shorter than one character" half.

### counts-tokenizer-specific — confirmed
- **Excerpt check.** Cookbook: strict. Glossary: strict. Token counting: loose (the source puts `model` in backticks).
- **Independent sources.** Anthropic *Pricing* — "How many tokens the same text produces depends on the model's tokenizer, the language, and the type of content." Gemini API reference `models.countTokens` — "Runs a model's tokenizer on input Content and returns the token count."
- **Notes.** The Pass 1 note is right: "should not be reused for another" is stated outright only by Anthropic ("rather than reusing counts measured against earlier models").

### tiktoken-model-encodings — confirmed (version-pinned)
- **Excerpt check.** Both strict in `model.py@0.14.0`.
- **Independent source.** OpenAI Cookbook encodings table: "| `o200k_base` | `gpt-4o`, `gpt-4o-mini`", with `cl100k_base` listed for `gpt-4-turbo`, `gpt-4`, ….
- **Currency.** `model.py@0.14.0` also maps `gpt-5`, `gpt-4.1`, `gpt-4.5-`, `o1`, `o3` and `o4-mini` to `o200k_base`, and `gpt-oss-` to `o200k_harmony`. The Cookbook table (2024) predates these. Keep "In tiktoken 0.14.0".

### bytes-per-token — confirmed (provider-specific)
- **Excerpt check.** strict.
- **Independent source.** OpenAI *Key concepts* — "1 token is approximately 4 characters" (English). For English text, characters and bytes are close.
- **Notes.** The README names no encoding or corpus. **ExplodeAI caution:** at 216 merges the sweep reports `corpus_bytes_per_token` 4.409, and 4.13 at 200. That is close to tiktoken's "about 4", but it is measured *on the training corpus itself*, so it is in-sample and flattering. Say this next to the trade-off chart so learners do not equate the two.

### openai-rule-of-thumb — confirmed (provider-specific, dated)
- **Excerpt check.** strict.
- **Independent sources.** tiktoken README — "On average, in practice, each token corresponds to about 4 bytes." Gemini says about 4 characters. As a contrast that shows the rule does not transfer: Anthropic's glossary says earlier Claude tokens average "approximately 3.5 English characters", and its models overview says "1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7)".

### gemini-tokens — confirmed (dated)
- **Excerpt check.** First: strict-ws. Second: loose-alnum (the source has inline-code and bold markup around `count_tokens` and "the input only"). The page says "Last updated 2026-10-13 UTC" and names current models such as `gemini-4-argon`.
- **Independent sources.** Gemini API reference `models.countTokens` https://ai.google.dev/api/tokens — "Runs a model's tokenizer on input Content and returns the token count." Vertex AI *Get token count* https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/get-token-count — "the result from the countTokens API call may not match the final consumed tokens." That remark is about multimodal inputs.

### anthropic-count-tokens — confirmed_with_changes (exceptions)
- **Excerpt check.** First: loose (Markdown links). Second: loose (bold "**free to use**", link). Third: strict.
- **Claim vs source.** The page goes straight on to list inputs the endpoint rejects. It also says "Token counts may include tokens added automatically by Anthropic for system optimizations. **You are not billed for system-added tokens**."
- **Independent source.** Anthropic API reference *Count tokens in a Message* https://platform.claude.com/docs/en/api/messages/count_tokens — "The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it."
- **Fix.** "Anthropic's token counting endpoint takes the same structured inputs as a message, including system prompts, tools, images and PDFs, with a few exceptions such as server tools and URL-sourced files. It is free but rate-limited, and its count is an estimate that can differ slightly from actual usage."
- **Excerpt fix.** Add: "This endpoint returns an `invalid_request_error` for a few inputs that the Messages API accepts".

### anthropic-new-tokenizer — confirmed_with_changes (range, dated)
- **Excerpt check.** All three strict (Supported models note).
- **Independent sources.** Anthropic *Pricing* https://platform.claude.com/docs/en/about-claude/pricing — "This tokenizer produces approximately 30% more tokens for the same text." and "Claude Sonnet 4.6 and earlier models use the previous tokenizer." Anthropic *Opus 5.5 migration guide* https://platform.claude.com/docs/en/models/opus-5-5/migration-guide — "it may use roughly 1x to 1.35x as many tokens when processing text compared to models before Claude Opus 4.7".
- **Notes.** The same page says "The exact increase depends on the content and workload shape". Both this claim and `counts-tokenizer-specific` depend on Anthropic's current model line-up (Fable 5.1, Mythos 5.1 and so on), so they will date.
- **Fix.** "Anthropic's docs say Claude 4.7 and later models use a newer tokenizer that produces roughly 30% more tokens for the same text (its Opus 5.5 migration guide gives about 1x–1.35x, depending on content), and advise recounting prompts for the model you plan to use."

### tokens-meter-usage — confirmed_with_changes (excerpt not found)
- **Excerpt check.** Cookbook: strict. **Gemini: NO MATCH.** See problem 1.
- **Independent sources.** Anthropic *Context windows* — "The "context window" refers to all the text a language model can reference when generating a response, including the response itself." Anthropic *Pricing* lists prices per MTok (e.g. "$10 / MTok"). OpenAI *Key concepts* — "the prompt and the generated output combined must be no more than the model’s maximum context length."
- **Excerpt fix.** Replace the Gemini excerpt with "Each Gemini model has a maximum number of tokens it can handle." Add "the cost of a call to the Gemini API is determined in part by the number of input and output tokens" for the pricing half.

---

## Uncovered statements (components, challenges, tour, visuals, corpus note)

These describe ExplodeAI's own implementation. They belong to Pass 3 tests, not citations, unless noted.

1. **`challenges.unknown-characters.brief`.** "The accented letters and the emoji come out as [UNK]" leaves out the capital "C" (problem 2). Suggested: "The capital C, the accented letters and the emoji come out as [UNK], so the text cannot be decoded back." The hint could add "or a capital C?".
2. **`challenges.merging-across-words.brief`.** "tokens like “the ” and “d the ”" — "the " is not learned at 150 merges (problem 3). Suggested: "tokens like “ the ” and “d the ”".
3. **`challenges.merges-out-of-order.explanation`.** "only the earliest merges end up applied" is close but loose. In reverse order, a merge whose inputs are themselves merged symbols always runs before the merge that would create them, so **only merges that join two base bytes can fire**. Run output: `T he ␠ ke ep er ␠t r im me d …`. Suggested: "…only merges that join two single bytes can fire." Learned order gives " keeper" and " lantern" as single tokens, as the brief says.
4. **`challenges.too-many-tokens`.** The text is accurate. 0 merges give 50 tokens. The first merge count that reaches ≤ 12 is 123. From 150 merges on the count is 10 (one token per piece). At 216 merges every corpus piece is a single symbol, so "nothing left to merge" is literally true.
5. **`decoder.detail` "gives back the input exactly when the alphabet is bytes".** With the character alphabet the round trip is also exact whenever no [UNK] appears (e.g. the familiar sentence with `base: chars` round-trips). Suggested: "…gives back the input exactly unless a token is [UNK]. With a byte alphabet that never happens." The tour decoder body is fine in the context of a byte alphabet.
6. **`vocabulary.detail`.** In `chars` mode, [UNK] is id 0 and is counted in `base_size` (33 = 32 corpus characters + [UNK]). Readers might expect it among the special tokens. Optional: "(With the character alphabet, [UNK] counts as part of the base alphabet.)"
7. **`visuals.tradeoff.description` "measured by retraining on the sample corpus".** The code trains once to `MAX_MERGES` and slices with `Tokenizer.truncated(n)`. I checked that this equals a fresh `train(n)` (merges, vocab and vocab_size) for n ∈ {0, 10, 50, 123, 299}, and a test covers it, so the numbers are right. Only the word "retraining" is loose. Also consider saying the bytes-per-token figures are in-sample (see `bytes-per-token`).
8. **`merge_learner.detail` "Ties go to the pair whose bytes sort first".** The code compares `(left symbol's bytes, right symbol's bytes)`, which is lexicographic on the pair. The wording is acceptable.
9. **`pre_tokenizer.detail`.** Accurate. The regex is GPT-2's pattern with `[^\W\d_]` in place of `\p{L}`. Python's `\w` treats a few non-letter symbols as word characters (e.g. "²" is grouped with letters, not digits), and "simplified" covers this. I checked that pieces concatenate back to the input for mixed whitespace, underscores, tabs, NBSP, digits, accents and emoji.
10. **`corpus.detail` and `experiment.corpus_note`.** Confirmed: 12 fictional entries, 1,045 characters, `isascii()` is true, 32 distinct characters. The note in `corpus.py` matches.
11. **`base_alphabet.detail`, tour `base_alphabet`.** Accurate. The byte base is always 256. With chars, unseen characters become [UNK] (4 in the challenge).
12. **`encoder.short`/`detail`, tour `encoder`.** These match `encode_piece`: the same pre-tokenizer, base symbols, then merges in learned order (equivalent to GPT-2 and subword-nmt). "The number of ids it outputs is the token count" matches `encoding.count`.
13. **`input_text.detail`, "Unseen words" preset.** "The lanternkeepers rewound clockwork." becomes `The ␠lantern ke ep er s ␠ r e w o un d ␠clock w or k .`, i.e. spelled from smaller pieces, as stated. Note that " keeper" is not reused, because "keepers" here lacks the leading space.
14. **"Numbers" preset.** The corpus has no digits, so digits stay one byte each (28 tokens at 100 merges). This is consistent with the "corpus decides" message, and the lesson text could point it out.
15. **`experiment.endpoint` and `reconstruction.dependencies`.** These match the router prefix `/api/experiments/tokenize` + `/run` and `pipeline.STAGE_DEPENDENCIES` exactly.
16. **`objectives` and `summary`.** These are consistent with the claims. "they do not transfer between models or providers" is backed by `counts-tokenizer-specific`.
17. **sources.yaml housekeeping.**
    - `tiktoken_readme.url` points at the repository root. Pin it as `https://github.com/openai/tiktoken/blob/0.14.0/README.md`, which matches its `version`.
    - `openai_cookbook_count_tokens.url` uses `blob/main`. Pinning to `db3144982aa2` would match its `version`; it is identical to `main` today.
    - `kudo2018sentencepiece`: note that ACL D18-2012 writes "Normalize(text):" with a colon.
    - `gemini_tokens`: the page now names Gemini 4 / 3 / 2.5 context rules.
    - If the fixes above are adopted, add sources for:
      - `provilkov2020bpedropout` (arXiv 1910.13267);
      - `anthropic_pricing` and `anthropic_opus55_migration`;
      - `tiktoken_openai_public` (`tiktoken_ext/openai_public.py@0.14.0`);
      - `gpt2_encoder` (`openai/gpt-2@9b63575ef427` `src/encoder.py`);
      - `sentencepiece_docs` (`google/sentencepiece@d6b191ec50dc` README / `doc/normalization.md`).
    - All 16 Lesson 02 source ids are cited at least once.

### Independent sources fetched (pinned where possible)
- openai/gpt-2 `src/encoder.py` @ `9b63575ef42771a015060c964af2c3da4cf7c8ab`. GPT-2 `vocab.bpe` and `encoder.json` from `openaipublic.blob.core.windows.net/gpt-2/encodings/main/` (SHA-256 `1ce16647…` / `19613966…`, matching tiktoken's expected hashes).
- rsennrich/subword-nmt `apply_bpe.py` @ `92d6139d07d30e12735a0af9e7f7f925ebe62c54`.
- google/sentencepiece README, `doc/normalization.md` and `doc/options.md` @ `d6b191ec50dc4302b262688f0250b9b677bb15d2`.
- huggingface/course `chapters/en/chapter6/4.mdx` @ `8b893f0ede6c781045692a7f892f25a0c92b4805`.
- tiktoken `tiktoken_ext/openai_public.py` @ `0.14.0`.
- HF `openai-community/gpt2` `config.json` (main).
- arXiv 1910.13267 abstract (export API).
- RFC 3629.
- Anthropic: `/about-claude/pricing.md`, `/build-with-claude/context-windows.md`, `/models/overview.md`, `/models/opus-5-5/migration-guide.md`, `/api/messages/count_tokens.md`.
- Google: ai.google.dev `/api/tokens`; cloud.google.com Vertex AI `get-token-count`.

---

## Machine-readable results

```yaml
pass2:
  date: 2026-10-19
  results:
    - claim: bpe-compression-origin
      verdict: confirmed
      independent_sources: [https://huggingface.co/learn/llm-course/chapter6/5]
      fix: null
      excerpt_fixes: []
    - claim: subword-open-vocabulary
      verdict: confirmed
      independent_sources: [https://huggingface.co/docs/transformers/tokenizer_summary, https://huggingface.co/docs/tokenizers/components]
      fix: null
      excerpt_fixes: []
    - claim: bpe-training-loop
      verdict: confirmed
      independent_sources: [https://huggingface.co/docs/transformers/tokenizer_summary]
      fix: null
      excerpt_fixes: []
    - claim: bpe-frequency-weighted
      verdict: confirmed
      independent_sources: [https://huggingface.co/docs/transformers/tokenizer_summary]
      fix: null
      excerpt_fixes: []
    - claim: bpe-vocab-formula
      verdict: confirmed_with_changes
      independent_sources: [https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/vocab.bpe, https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py]
      fix: "The final vocabulary is the starting alphabet plus one new symbol per merge (plus any special tokens), so the number of merges is what sets the vocabulary size."
      excerpt_fixes: []
    - claim: bpe-no-cross-word
      verdict: confirmed
      independent_sources: [https://huggingface.co/docs/tokenizers/pipeline]
      fix: null
      excerpt_fixes: []
    - claim: bpe-apply-in-order
      verdict: confirmed
      independent_sources: [https://github.com/openai/gpt-2/blob/9b63575ef42771a015060c964af2c3da4cf7c8ab/src/encoder.py, https://github.com/rsennrich/subword-nmt/blob/92d6139d07d30e12735a0af9e7f7f925ebe62c54/subword_nmt/apply_bpe.py]
      fix: null
      excerpt_fixes: []
    - claim: bpe-deterministic
      verdict: confirmed_with_changes
      independent_sources: [https://huggingface.co/docs/transformers/tokenizer_summary, https://huggingface.co/docs/tokenizers/components, https://arxiv.org/abs/1910.13267]
      fix: "Standard BPE is deterministic, so the same text always gets the same tokens. The unigram language model, an alternative, can produce several segmentations of the same text, each with a probability. (Variants such as BPE-dropout add randomness on purpose during training.)"
      excerpt_fixes: []
    - claim: sentencepiece-raw-text
      verdict: confirmed
      independent_sources: [https://github.com/google/sentencepiece/blob/d6b191ec50dc4302b262688f0250b9b677bb15d2/README.md, https://huggingface.co/learn/llm-course/chapter6/4]
      fix: null
      excerpt_fixes: []
    - claim: sentencepiece-vocab-size
      verdict: confirmed
      independent_sources: [https://github.com/google/sentencepiece/blob/d6b191ec50dc4302b262688f0250b9b677bb15d2/doc/options.md]
      fix: null
      excerpt_fixes: []
    - claim: sentencepiece-lossless
      verdict: confirmed_with_changes
      independent_sources: [https://github.com/google/sentencepiece/blob/d6b191ec50dc4302b262688f0250b9b677bb15d2/doc/normalization.md, https://huggingface.co/learn/llm-course/chapter6/4]
      fix: "SentencePiece's decoder is the exact inverse of its encoder on normalised text, which its authors call lossless tokenization. What comes back is the normalised text (by default a variant of NFKC), which matches the original only if normalisation left it unchanged."
      excerpt_fixes: []
    - claim: gpt2-byte-level
      verdict: confirmed
      independent_sources: [https://huggingface.co/docs/tokenizers/components, https://github.com/openai/gpt-2/blob/9b63575ef42771a015060c964af2c3da4cf7c8ab/src/encoder.py]
      fix: null
      excerpt_fixes: []
    - claim: byte-level-no-unk
      verdict: confirmed
      independent_sources: [https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf, https://huggingface.co/docs/transformers/tokenizer_summary]
      fix: null
      excerpt_fixes: []
    - claim: char-bpe-unk
      verdict: confirmed
      independent_sources: [https://huggingface.co/docs/transformers/tokenizer_summary, https://arxiv.org/abs/1508.07909]
      fix: null
      excerpt_fixes: []
    - claim: gpt2-character-categories
      verdict: confirmed
      independent_sources: [https://github.com/openai/gpt-2/blob/9b63575ef42771a015060c964af2c3da4cf7c8ab/src/encoder.py, https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py]
      fix: null
      excerpt_fixes: []
    - claim: leading-space
      verdict: confirmed
      independent_sources: [https://developers.openai.com/api/docs/concepts, https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/encoder.json]
      fix: null
      excerpt_fixes: []
    - claim: gpt2-vocab-size
      verdict: confirmed
      independent_sources: [https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/vocab.bpe, https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/encoder.json, https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py, https://huggingface.co/openai-community/gpt2/blob/main/config.json]
      fix: null
      excerpt_fixes: []
    - claim: real-merge-counts
      verdict: confirmed_with_changes
      independent_sources: [https://openaipublic.blob.core.windows.net/gpt-2/encodings/main/vocab.bpe]
      fix: "Real systems learn tens of thousands of merges. For English→German, Sennrich et al. used 59,500 (89,500 for joint BPE over both languages), and GPT-2 has 50,000. This lesson's tiny corpus runs out after about 200 (216 with the default pre-tokenizer)."
      excerpt_fixes: []
    - claim: special-tokens
      verdict: confirmed_with_changes
      independent_sources: [https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py, https://huggingface.co/learn/llm-course/chapter6/5]
      fix: null
      excerpt_fixes:
        - {source: tiktoken_core, old: null, new: "Special tokens are artificial tokens used to unlock capabilities from a model, such as fill-in-the-middle."}
    - claim: hf-pipeline
      verdict: confirmed_with_changes
      independent_sources: [https://huggingface.co/learn/llm-course/chapter6/4]
      fix: "Hugging Face Tokenizers describes encoding as a pipeline: normalization, pre-tokenization, a model such as BPE, and post-processing. The model is the part trained on a corpus, and post-processing adds any special tokens."
      excerpt_fixes:
        - {source: hf_tokenizers_pipeline, old: "your final tokens will be parts of those words.", new: "the input text(s) go through the following pipeline:"}
    - claim: vocab-length-tradeoff
      verdict: confirmed_with_changes
      independent_sources: [https://huggingface.co/docs/transformers/tokenizer_summary]
      fix: "Vocabulary size trades against sequence length. Characters give a tiny vocabulary but long sequences, whole words a huge vocabulary, and BPE sits in between. More merges mean a bigger vocabulary and fewer tokens per text, until the text's words are already single tokens."
      excerpt_fixes: []
    - claim: byte-bpe-lossless
      verdict: confirmed
      independent_sources: [https://github.com/openai/gpt-2/blob/9b63575ef42771a015060c964af2c3da4cf7c8ab/src/encoder.py, https://github.com/openai/openai-cookbook/blob/db3144982aa2/examples/How_to_count_tokens_with_tiktoken.ipynb]
      fix: null
      excerpt_fixes: []
    - claim: decode-partial-lossy
      verdict: confirmed
      independent_sources: [https://github.com/openai/openai-cookbook/blob/db3144982aa2/examples/How_to_count_tokens_with_tiktoken.ipynb, https://www.rfc-editor.org/rfc/rfc3629]
      fix: null
      excerpt_fixes: []
    - claim: tokens-not-words
      verdict: confirmed
      independent_sources: [https://ai.google.dev/gemini-api/docs/tokens]
      fix: null
      excerpt_fixes: []
    - claim: counts-tokenizer-specific
      verdict: confirmed
      independent_sources: [https://platform.claude.com/docs/en/about-claude/pricing, https://ai.google.dev/api/tokens]
      fix: null
      excerpt_fixes: []
    - claim: tiktoken-model-encodings
      verdict: confirmed
      independent_sources: [https://github.com/openai/openai-cookbook/blob/db3144982aa2/examples/How_to_count_tokens_with_tiktoken.ipynb]
      fix: null
      excerpt_fixes: []
    - claim: bytes-per-token
      verdict: confirmed
      independent_sources: [https://developers.openai.com/api/docs/concepts]
      fix: null
      excerpt_fixes: []
    - claim: openai-rule-of-thumb
      verdict: confirmed
      independent_sources: [https://github.com/openai/tiktoken/blob/0.14.0/README.md, https://ai.google.dev/gemini-api/docs/tokens, https://platform.claude.com/docs/en/models/overview]
      fix: null
      excerpt_fixes: []
    - claim: gemini-tokens
      verdict: confirmed
      independent_sources: [https://ai.google.dev/api/tokens, https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/get-token-count]
      fix: null
      excerpt_fixes: []
    - claim: anthropic-count-tokens
      verdict: confirmed_with_changes
      independent_sources: [https://platform.claude.com/docs/en/api/messages/count_tokens]
      fix: "Anthropic's token counting endpoint takes the same structured inputs as a message, including system prompts, tools, images and PDFs, with a few exceptions such as server tools and URL-sourced files. It is free but rate-limited, and its count is an estimate that can differ slightly from actual usage."
      excerpt_fixes:
        - {source: anthropic_token_counting, old: null, new: "This endpoint returns an `invalid_request_error` for a few inputs that the Messages API accepts"}
    - claim: anthropic-new-tokenizer
      verdict: confirmed_with_changes
      independent_sources: [https://platform.claude.com/docs/en/about-claude/pricing, https://platform.claude.com/docs/en/models/opus-5-5/migration-guide]
      fix: "Anthropic's docs say Claude 4.7 and later models use a newer tokenizer that produces roughly 30% more tokens for the same text (its Opus 5.5 migration guide gives about 1x–1.35x, depending on content), and advise recounting prompts for the model you plan to use."
      excerpt_fixes:
        - {source: anthropic_token_counting, old: null, new: "The exact increase depends on the content and workload shape."}
    - claim: tokens-meter-usage
      verdict: confirmed_with_changes
      independent_sources: [https://platform.claude.com/docs/en/build-with-claude/context-windows, https://platform.claude.com/docs/en/about-claude/pricing, https://developers.openai.com/api/docs/concepts]
      fix: null
      excerpt_fixes:
        - {source: gemini_tokens, old: "The context window defines the combined limit of input and output tokens.", new: "Each Gemini model has a maximum number of tokens it can handle."}
        - {source: gemini_tokens, old: null, new: "the cost of a call to the Gemini API is determined in part by the number of input and output tokens"}
```

Notes on the YAML:
- `old: null` in an excerpt fix means "add this excerpt".
- Proposed excerpts from sources that sources.yaml does not yet list are not in `excerpt_fixes`. They need a new source id first: BPE-dropout, Anthropic pricing and migration guide, tiktoken `openai_public.py`, gpt-2 `encoder.py`, and the SentencePiece docs. Their verbatim text is in the per-claim sections above.
- The second `gemini_tokens` excerpt is verbatim apart from whitespace (the page wraps it across lines and links "cost of a call to the Gemini API").
- The `anthropic_token_counting` excerpt for `anthropic-count-tokens` is verbatim with the source's backticks around `invalid_request_error`.
