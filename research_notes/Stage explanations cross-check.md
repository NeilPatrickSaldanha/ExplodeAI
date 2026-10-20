# Stage explanations — independent fact-check

Date: 2026-10-19. Files checked: `content/lessons/{rag-pipeline,tokenization,embeddings}/explain.yaml` (24 stages, 8 per lesson), against each `lesson.yaml` claim list, `content/sources.yaml`, and the code in `backend/app/experiments/{rag,tokenize,embed}/`.

## Method

- Every sentence of `what / why / happens / goes_to / misconfigured / learn_more` was matched to (a) a claim id in that stage's `claims` list (claim text and cited excerpts read in `lesson.yaml`), or (b) the implementation, or (c) neither. Category (c) is a NEW fact.
- Every implementation statement was checked against the code, and many were run: default RAG pipeline (11 chunks, top-3 = returns#0, battery#1, returns#1; extractive answer; prompt text), the BPE tokenizer (default corpus, 100 merges, vocab 357, first merges `he`, ` t`, ` the`; `lower` encodes to `l`,`ow`,`er`), and the real bge-small encoder (tokens, query-instruction effect, 512 truncation, PCA variance 27% on the default query). No paid API call was made; the local ONNX model was already cached.
- New facts were checked by downloading the page with curl and extracting plain text with a small script (HTML parser, regex excerpt). No summarising fetch tool was used. Downloads are in `.../scratchpad/explain_check/dl/`, scripts in `.../explain_check/scripts/`.
- The UI check: `frontend/src/lessons/shared/cine/Understand.tsx` labels every analogy "ANALOGY · TEACHING AID" and every example "ILLUSTRATIVE EXAMPLE", so the labelling rule is met by the renderer. The remaining question for examples is whether their content contradicts what the learner sees in the live experiment.

Verdict per stage = the worst finding in that stage.

## Summary

| Verdict | Count | Stages |
|---|---|---|
| confirmed | 5 | tokenization: base_alphabet, vocabulary; embeddings: your_text, similarity, semantic_space |
| confirmed_with_changes | 16 | RAG: corpus, chunker, embedder, query_encoder, retriever, prompt_builder; tokenization: corpus, pre_tokenizer, merge_learner, input_text, encoder; embeddings: library, tokenizer, encoder, pooling, normalizer |
| disputed | 3 | RAG: vector_index, generator; tokenization: decoder |
| unverifiable | 0 | none (every new fact was either sourced below or flagged for rewrite) |

No stage contains a fabricated number. All numeric claims (6 articles, 11 chunks, top-3, 1024 / 384 dims, 24 sentences, 25 points, 357 entries, 5 bytes, 216 merges, 800/400, 100-word, 17–33%, 30,522, 50,257, 8,192, 512, <5%) match a verified claim or the running code.

### Prioritized problems

1. **RAG `vector_index` contradicts the implementation.** The code is `index = vecs` (a bare matrix; no chunk ids stored). "Without an index you would compare the question against every chunk" is exactly what the flat index here does, so the reasoning is backwards.
2. **RAG `generator` describes an LLM, not the extractive baseline.** `extractive_answer(question, chunks)` never receives the prompt, writes nothing, and picks sentences by shared query terms, not "the sentence that answers".
3. **Tokenization `decoder.why` "It proves nothing was lost" is false** for the character alphabet, as the same stage's `misconfigured` says.
4. **Tokenization merge/encoder examples (`lo`, `low`, `lower`) disagree with what the learner will see.** The real tokenizer learns `he`, ` t`, ` the` first and encodes `lower` as `l`,`ow`,`er`. The renderer labels them illustrative, but they are replaceable by real, checkable data.
5. **RAG `prompt_builder.example` says "Trim to the word budget".** The code never trims text; it drops whole chunks that do not fit (and keeps trying later chunks).
6. **Embeddings `pooling.misconfigured` overstates** ("wrong pooling hurts quality") against the claim it cites (choice "mattered little" under NLI training).
7. **Embeddings `normalizer.learn_more` "only models trained for it … shorten well"** adds an "only" the claim does not make.
8. **"Questions and chunks must use the same embedding model" (RAG embedder, query_encoder) is not in any RAG claim.** It is true and verified in the Embeddings lesson (`models-not-comparable`); the RAG lesson needs that claim or a restatement tied to ExplodeAI.
9. **RAG `retriever.misconfigured` "Dense search can miss exact terms"** is a new fact (now sourced) and, for the default lexical embedder, backwards.
10. Smaller items: RAG embedder "once, ahead of time" (the demo re-embeds each run), chunker size units, tokenization corpus example counts `the` as one word while the next stage splits it as `the` / ` the`, "silently" and "syllables" in embeddings tokenizer, unexplained jargon.

---

## New facts found and sources

| Where | New fact | Primary source (verbatim, ≤30 words) | Status |
|---|---|---|---|
| RAG retriever.misconfigured | Embedding (dense) search can miss exact terms | Anthropic, Introducing Contextual Retrieval, https://www.anthropic.com/news/contextual-retrieval: "While embedding models excel at capturing semantic relationships, they can miss crucial exact matches." | confirmed; add as a claim |
| RAG embedder / query_encoder .misconfigured | Query and chunk vectors must come from the same model to be comparable | Google, https://ai.google.dev/gemini-api/docs/embeddings: "you cannot directly compare embeddings generated by one model with embeddings generated by the other." Also Voyage docs: "All embeddings created with the 4 series are compatible with each other." (exception) | confirmed; already verified as `models-not-comparable` in the Embeddings lesson, but absent from the RAG lesson.yaml |
| Tokenization corpus / input_text .misconfigured | Text unlike the training text, e.g. another language, splits into many tokens | Petrov et al. 2023, https://arxiv.org/abs/2305.15425: "The same text translated into different languages can have drastically different tokenization lengths, with differences up to 15 times in some cases." | supports production tokenizers; for ExplodeAI's own BPE it is demonstrated by the code (`lighthouse` is spelled from 10 single letters). Scope the sentence to this lesson (fix below). |
| Embeddings encoder.happens "Each token is updated by looking at the others" | Contextual encoding | Devlin et al., https://arxiv.org/abs/1810.04805: "jointly conditioning on both left and right context in all layers." | confirmed; add to `contextual-vectors` if kept |
| RAG corpus.why "A language model only knows what it was trained on" | absolute wording | Covered only for private documents by `rag-private-knowledge`. "Newer documents" is not covered. | soften (fix below) |
| Embeddings pooling.misconfigured "Using the wrong pooling for a model hurts quality" | general | No source; the cited SBERT claim says the opposite for one setup. | flagged; rewrite |

---

## Per-stage results

### RAG pipeline (`content/lessons/rag-pipeline/explain.yaml`)

#### corpus — confirmed_with_changes
- Supported: "six made-up help-centre articles" (6 documents in `corpus.py`); retrieval avoids retraining (`rag-swap-index`); private docs (`rag-private-knowledge`); 200,000-token note matches `rag-small-kb` and is dated.
- Problem: `why` "A language model only knows what it was trained on" is absolute and "newer" is not in a claim.
- Problem (minor): `misconfigured` "every later stage works perfectly" is hyperbole; stages can still be run, but "perfectly" is not tested.
- Fix `corpus.why`: "A language model has no knowledge of private documents it was never trained on. Retrieval lets it use your documents without retraining it."
- Fix `corpus.misconfigured`: "If the documents are missing, out of date or wrong, the later stages have nothing correct to find, so the answer will be wrong."

#### chunker — confirmed_with_changes
- Supported: chunk definition, overlap (`chunking-overlap`), context loss (`chunking-context-loss`), OpenAI 800/400 (`openai-chunk-defaults`, dated "currently"), 100-word RAG paper chunks. `doc_id` stored per chunk: yes.
- Problem: `happens[0]` "split at a chosen size" omits that size is in WORDS here (text.py: "All counts … are in words, not model tokens"), while the learn_more figures are tokens. A beginner will conflate them. Also the default strategy is "sentence" with overlap 0, so the overlap bullet describes an option, not the default.
- Problem: `why` "fit in the prompt" is not in a claim (it is true of this implementation's word budget).
- Problem: example step "two sentences-sized chunks" is a typo.
- Fix `happens[0]`: "The document text is split at a chosen size, counted in words here (not tokens)."
- Fix `happens[1]`: "Optionally, neighbouring chunks overlap a little so a sentence at the edge is not cut in half. Overlap is 0 by default in this lesson."
- Fix `example.steps[0]`: "Split into two sentence-sized chunks"

#### embedder — confirmed_with_changes
- Supported: lexical default (`rag/embedding.py` docstring; kind `lexical-hashing`), dim 1024 for the default, `embedding-definition`, `bi-encoder`, `anthropic-no-embeddings`. OpenAI dims claim is listed but not used (harmless).
- Problem: `happens[0]` "Each chunk goes in, once, ahead of time". In `pipeline.run` every chunk is re-fitted and re-embedded on each run. True for a real system, not for what the learner's run does.
- Problem: `misconfigured` "must use the same embedding model, or their vectors cannot be compared" is a NEW fact in this lesson (see New facts; verified, but add a claim).
- Problem (minor): "Features are folded into a fixed-length vector". Accurate only loosely: features (lowercased, stemmed words and word pairs) are TF-IDF weighted, hashed to one of 1024 slots with a ± sign, then scaled to length 1. Different features can collide in a slot.
- Fix `happens[0]`: "Each chunk goes in once when the index is built, before any question is asked."
- Fix `example.steps[1]`: "Features are hashed into a fixed-length vector"
- Fix `misconfigured`: "Questions and chunks must be embedded by the same embedding model, or their vectors cannot be compared. A lexical embedder will miss a paraphrase that shares no words with the chunk." AND add claim `models-not-comparable` (or an equivalent RAG-lesson claim) to `claims`.

#### vector_index — disputed
- Code: `index = vecs  # exact (flat) index: the matrix itself`. Chunk i is row i of the matrix; no chunk id is stored in it. A flat index has no lookup structure; search is `chunk_vecs @ query_vec` over every row.
- Problem 1: `happens[0]` "Chunk vectors are stored with their chunk ids" is false for this implementation.
- Problem 2: `why` "Without an index you would compare the question against every chunk by hand each time" is the opposite of what the flat index does (it compares every chunk). It also implies an index normally avoids that, which is only true of approximate indexes (`flat-index-exact`).
- Problem 3: `what` "a structure built for quick lookup" is not true of the flat index used here.
- Problem 4: "HNSW" appears in `misconfigured` before being explained.
- Supported: exactness, HNSW trade-off, log scaling, frozen index in the RAG paper, 11 chunk vectors (confirmed: default run gives 11).
- Fix `what`: "Stores all the chunk vectors so they can be searched. ExplodeAI uses a flat index: the vectors themselves, with no extra structure."
- Fix `why`: "Search needs the chunk vectors in one place. A flat index still compares the question with every vector, which is exact. Faster approximate indexes exist, but this lesson does not use one. The index is where the knowledge lives."
- Fix `happens`: ["Chunk vectors are stored as rows of one matrix, in the same order as the chunk list.", "A flat index adds no extra structure.", "A search compares the query against every stored vector."]
- Fix `misconfigured`: "A flat index is exact but compares every vector, so it gets slow at very large scale. Approximate indexes (for example HNSW, which skips most vectors) are much faster but can occasionally miss the true best match."
- Fix `analogy` (optional, to avoid implying a shortcut): "A numbered shelf. You can read every row, which is slow for a huge shelf but never misses a book."

#### query_encoder — confirmed_with_changes
- Supported: `bi-encoder`, `dpr-dot-product`, `anthropic-no-embeddings`. In the implementation the SAME embedder embeds the query (`embedder.embed([params.query])`), consistent with `happens[2]`'s first half. DPR's separate question encoder is consistent with the claim.
- Problem: `happens[2]` "Some systems use one model for both" has no claim. State it as this lesson's implementation.
- Problem: `misconfigured` same-model fact is new (see embedder).
- Problem (minor): example "Tokenised into terms" – here the step lowercases, drops stop-words and strips plural endings (`text.terms`); "tokenised" will be confused with the Tokenization lesson's model tokens. The example query ("blender") is not in the bike corpus, so a learner cannot reproduce it. It is labelled illustrative, which is acceptable.
- Fix `happens[2]`: "Here the same embedder is used for both. Some real systems, such as Dense Passage Retrieval, train a separate question encoder."
- Fix `example.steps[0]`: "Lowercased and cut into word stems"
- Fix `example.input`: "How long do I have to return a bike?" (the default query, so the learner sees the same text)
- Fix `misconfigured`: "The question must be embedded by the same embedder as the chunks. Vectors from different models cannot be compared, so scores would be meaningless." AND add `models-not-comparable` to claims.

#### retriever — confirmed_with_changes
- Supported: top-k default is 3 (`RagParams.top_k`, matches "Keep the top 3"), dense/BM25/hybrid, rrf k=60 (`retrieval.py`), `bm25-mechanics`, rerank cross-encoder. dpr-beats-bm25 is listed but (correctly) not restated, so the disputed claim does not leak.
- Problem: `misconfigured` "Dense search can miss exact terms" is a NEW fact (sourced above: Anthropic) but is misleading with the default: ExplodeAI's "dense" retrieval uses the lexical embedder, which is built from the words themselves. With the default, dense search misses synonyms (as keyword search does), not exact terms. The Pass-2 note in `research_notes/RAG pipeline primary sources/pass2_cross_check.md` item 3 already raised this.
- Problem: `why` "The model has limited room in its prompt" matches the word budget in the implementation but not a claim.
- Problem (jargon): "dense", "cross-encoder" and "k1" / "b" are used without explanation.
- Fix `misconfigured`: "Keyword search misses synonyms. A neural dense model can miss exact terms (Anthropic reports embedding models 'can miss crucial exact matches'), while this lesson's default 'dense' embedder is lexical and behaves more like keyword search. A k that is too small can drop the chunk that holds the answer; a k that is too large floods the prompt." AND add a claim for the Anthropic excerpt.
- Fix `happens[0]`: "Dense retrieval compares vectors (here, from the lexical embedder). BM25 scores keyword matches. Hybrid blends both rankings."
- Fix `learn_more` jargon: replace "rerank them with a slower, more accurate cross-encoder" with "rerank them with a slower, more accurate model (a cross-encoder, which reads the question and a chunk together)". The "reads together" gloss needs `rerank-cross-encoder`'s excerpt to support it; if it does not, drop the gloss and keep only "a slower, more accurate model".

#### prompt_builder — confirmed_with_changes
- Code check: chunks are wrapped as `<document index="i"><source>{chunk.id}</source><document_content>…`, in rank order, then instructions, then `Question: …`. So "each labelled with its source" is true if "source" means the chunk id (e.g. `returns#0`), not the article title. Budget is in WORDS (default 200), not tokens.
- Problem: `happens[2]` "Anything over the budget is dropped" is ambiguous and the example step "Trim to the word budget" implies text is cut. The code never truncates: a chunk that would push the total over budget is dropped whole, and later (smaller) chunks may still be added.
- Problem: `misconfigured` "makes it more likely to be overlooked" is a present-tense general; the claim is a 2023 finding for long contexts. Here prompts are short.
- Fix `happens[0]`: "Chunks are placed first, in rank order, each wrapped in a tag that carries its chunk id as the source."
- Fix `happens[2]`: "A chunk that would push the prompt over the word budget is dropped whole; nothing is cut in half."
- Fix `example.steps[2]`: "Drop any chunk that would go over the word budget"
- Fix `misconfigured`: "A budget that is too small drops the chunk with the answer. A 2023 study found that in long prompts, information in the middle was used less well than information at the start or end."

#### generator — disputed
- Code: `extractive_answer(question, chunks, max_sentences=2)` takes the question and the chunks that were included in the prompt, NOT the prompt text. It splits sentences, keeps those sharing at least one (stemmed, non-stop-word) term with the question, sorts by number of shared terms and returns the top 2 with their chunk ids. Default run output: "Ridgeline Bikes accepts returns of unused bikes within 30 days of delivery. [returns#0] Returned bikes must include the original packaging. [returns#0]". It is explicitly "NOT a language model".
- Problem 1: `happens[0]` "The assembled prompt goes in." Wrong for this implementation (the prompt is built but not read by the baseline).
- Problem 2: `happens[1]` "writes an answer from the context" and the analogy "A student writing an answer" suggest generation; it copies up to two sentences.
- Problem 3: `example.steps[1]` "Pick the sentence that answers the question". It picks by word overlap; it can pick a sentence that does not answer (the default run's second sentence is about packaging). This is a misleading mental model.
- Supported: offline extractive baseline; citations point at chunks; `rag-sequence-token`, `rag-paper-architecture`, `rag-hallucination`, `grounding-definition`.
- Fix `what`: "Produces the answer. A real RAG system sends the prompt to a language model; offline, ExplodeAI uses a simple extractive baseline that copies the sentences from the retrieved chunks that share the most words with the question."
- Fix `happens`: ["The question and the chunks that fit in the prompt go in.", "Each sentence is scored by how many of the question's words it shares.", "The best two sentences are returned, each cited with the id of its chunk."]
- Fix `analogy`: "A student who answers by copying the sentences from the pages on the desk that use the question's words, and noting which page each came from."
- Fix `example.steps`: ["Read the sentences in the context", "Pick the sentences sharing the most words with the question"]
- Fix `misconfigured` second sentence (clarity): "Even with the right chunk, a generator can still get things wrong; this baseline can also pick a sentence that shares words with the question but does not answer it."
- Jargon: "hallucinated" in `learn_more` is not explained. Suggested: "…commercial RAG legal tools still hallucinated (stated things that were not supported) 17–33% of the time."

---

### Tokenization (`content/lessons/tokenization/explain.yaml`)

#### corpus — confirmed_with_changes
- Supported: `bpe-frequency-weighted`, `real-merge-counts` (this corpus runs out at 216 with default pre-tokenizer; confirmed by running training to 300).
- Problem: `happens` "counted word by word" and example "\"the\" appears three times". The training counts are over PRE-TOKENIZED pieces, so in "the tide was low, the wind came from the west" the pieces are `the` once and ` the` twice (a space belongs to the next word, which the next stage teaches). Not wrong as words, but a learner who checks the Experiment will see two entries.
- Problem: `happens[2]` uses "merges" before it is defined (defined two stages later). `learn_more` uses "BPE" without expanding it.
- Problem: `misconfigured` generalises to "your real text" with no claim. See New facts (Petrov et al. is for production tokenizers).
- Fix `happens[1]`: "The text is cut into word-like pieces and each distinct piece is counted."
- Fix `happens[2]`: "The counts decide which pairs of letters get joined first (a step called a merge, explained later)."
- Fix `example.steps[1]`: "\"the\" appears three times (as \"the\" once and \" the\" twice once the space is attached to the next word)"
- Fix `misconfigured`: "In this lesson's tokenizer, a corpus that looks nothing like the text you encode gives merges that suit the wrong words, so the new text is spelled from many small tokens."
- Fix `learn_more` first sentence: "BPE (byte-pair encoding) began as a data-compression technique."

#### pre_tokenizer — confirmed_with_changes
- Code check: regex `'(?:s|t|re|ve|m|ll|d)| ?[^\W\d_]+| ?\d+| ?(?:[^\s\w]|_)+|\s+(?!\S)|\s+`. Output for "the tide, was 42 low!? it's": `the`, ` tide`, `,`, ` was`, ` 42`, ` low`, `!?`, ` it`, `'s`. Consistent with the claims.
- Problem (minor): "A space stays attached to the front of the next word" holds for a single space; the first word has no space, a newline is its own piece, and extra spaces split off. Add "usually".
- Supported: all `learn_more` sentences map to `leading-space`, `gpt2-character-categories`, `sentencepiece-raw-text`, `hf-pipeline`, `bpe-no-cross-word`.
- Fix `happens[1]`: "A single space usually stays attached to the front of the next word."

#### base_alphabet — confirmed
- All statements match the claims and code (`" tide"` is 5 bytes: 32,116,105,100,101; chars alphabet uses `[UNK]` id 0; 256 base symbols).
- Beginner clarity: "byte" and "[UNK]" are never explained, and "Unicode code points" appears in `learn_more`. Suggested addition to `what`: "…A byte is one of 256 possible values; plain English letters are one byte each, while accented letters and emoji take several. [UNK] is the placeholder used for a character the alphabet does not contain."

#### merge_learner — confirmed_with_changes
- Supported: `bpe-training-loop`, `bpe-frequency-weighted`, `bpe-compression-origin`, `bpe-deterministic`.
- Problem: `happens[2]` "Repeat until the chosen number of merges is reached" – training also stops early when no pair is left (`if not pairs: break`; corpus runs out at 216).
- Problem: the example (`l o w e r` → `lo` → `low`) is not what this lesson learns. With the default corpus the first merges are `he`, ` t`, ` the`. The label "ILLUSTRATIVE EXAMPLE" is shown by the renderer, and the file header says so, but nothing in the text of the example tells a learner their run will differ. Real, reproducible alternative below.
- Fix `happens[2]`: "Repeat until the chosen number of merges is reached, or until no pair is left to merge."
- Fix example (real data, default corpus, bytes, 100 merges, words pre-tokenizer):
  - `input`: "\" the\" spelled as: space  t  h  e  (it is frequent in the corpus)"
  - `steps`: ["Most common pair: h + e → he (merge 1)", "Then space + t → \" t\" (merge 2)", "Then \" t\" + he → \" the\" (merge 3)"]
  - `output`: "Merges in order: he, \" t\", \" the\" (these are the first three this lesson learns)"

#### vocabulary — confirmed
- 256 + 100 + 1 = 357, matches `vocab_size` on the default run. All other sentences match `bpe-vocab-formula`, `gpt2-vocab-size`, `real-merge-counts`, `sentencepiece-vocab-size`, `special-tokens`, `vocab-length-tradeoff`. Special token `<|endoftext|>` exists in code.

#### input_text — confirmed_with_changes
- Supported: `subword-open-vocabulary`, `tokens-not-words`. Example "lighthouse keeper" gives ` keeper` (one token) and `lighthouse` as ten one-letter tokens: "a mix of whole-word and small tokens" is right.
- Problem: `misconfigured` "Text unlike the training corpus, such as another language, tends to break into many small tokens" has no claim. Demonstrably true of this lesson's tokenizer; for production tokenizers see Petrov et al. (above).
- Fix `misconfigured`: "In this lesson's tokenizer, text unlike the training corpus, such as another language, is spelled from many small tokens. Real tokenizers show a similar effect: the same text in different languages can differ in token count by up to 15 times." (and add a claim for the Petrov excerpt before shipping the second sentence).

#### encoder — confirmed_with_changes
- Supported: `bpe-apply-in-order`, `counts-tokenizer-specific`, `tiktoken-model-encodings`, `tokens-meter-usage`, `anthropic-new-tokenizer`.
- Problem: `happens[2]` "…then look up ids". In `bpe.py` symbols already are integer ids; there is no separate lookup step.
- Problem: the example (`lower` → `lo` → `low` → ids for low, e, r) disagrees with the live tokenizer, which encodes `lower` as `l`, `ow`, `er`. Labelled illustrative, but replaceable with a real trace.
- Fix `happens[2]`: "Apply the learned merges in the order they were learned. The resulting symbols are the token ids."
- Fix example (real, default settings): `input`: "\" the\""; `steps`: ["Spell as bytes: space, t, h, e", "Apply merge he", "Apply merge \" t\"", "Apply merge \" the\""]; `output`: "One token: \" the\"". Matching decoder example: `input`: "One token: \" the\""; `steps`: ["Look up its bytes", "Join them"]; `output`: "\" the\"".

#### decoder — disputed
- Problem: `why` "It proves nothing was lost" is false in general. With a character alphabet an unseen character becomes `[UNK]` and decodes to "�" (`round_trip` is False in the code), and the stage's own `misconfigured` says so. It also cannot "prove" anything about a model's output.
- Supported: everything else (`byte-bpe-lossless`, `decode-partial-lossy`, `sentencepiece-lossless`; code uses `errors="replace"`).
- Fix `why`: "It shows whether anything was lost: with a byte alphabet the original text comes back exactly, and it is how model output becomes readable."

---

### Embeddings (`content/lessons/embeddings/explain.yaml`)

#### library — confirmed_with_changes
- Verified: 24 sentences in 4 topics; "The bookshelf is full of old novels." exists (`furniture-3`); the neural library vectors are cached once (`lru_cache`) and 384-dimensional.
- Problem: `happens[0]` "same tokenizer, encoder, pooling and normalizer as your text" is true for the default neural embedder only (the lexical option skips them).
- Problem: `misconfigured` and `learn_more` restate `models-not-comparable`, which is not in this stage's `claims` list.
- Fix `claims`: `[embedding-uses, models-not-comparable]`
- Fix `happens[0]`: "With the neural embedder, every sentence goes through the same tokenizer, encoder, pooling and normalizer as your text."

#### your_text — confirmed
- Instruction is optional (`query_instruction` default False) and prepended to the query only; matches `bge-query-instruction` and `query-document-asymmetry`.

#### tokenizer — confirmed_with_changes
- Verified by running the model: `[CLS]` first, `[SEP]` last, `Embeddings` → `em ##bed ##ding ##s`, `unbelievably` → `un ##bel ##ie ##va ##bly`, 600-word input cut to 512 tokens with `[SEP]` kept last and `truncated=True`.
- Problem: `misconfigured` "silently cut" – `silently` is only documented for Google's gemini-embedding-2; for this lesson the app flags truncation. Remove "silently".
- Problem: analogy "like syllables" – WordPiece pieces are statistically common fragments, not linguistic syllables (`##bel`, `##va`). Could mislead.
- Jargon: `[CLS]` and `[SEP]` are used in `happens` without explanation until the pooling stage.
- Fix `analogy`: "Breaking a sentence into familiar word fragments from a fixed list, and numbering each one."
- Fix `happens[1]`: "Two marker tokens are added: [CLS] first (its vector will later summarise the sentence) and [SEP] last."
- Fix `misconfigured`: "Long text is cut at 512 tokens, so the end never reaches the model. Split long documents into chunks first."

#### encoder — confirmed_with_changes
- Supported: `bge-dims` (12 layers, 384), `contextual-vectors` (<5% appears in the cited excerpt), `word2vec-static`, `word2vec-analogy`, `contrastive-training`. The `learn_more` "<5%" figure is in the claim's excerpt, though the claim text only says "explains little"; consider using the number in the claim text.
- Problem: `happens[1]` "Each token is updated by looking at the others" is not stated by any listed claim. Sourced: Devlin et al. (above).
- Jargon (learn_more only): "contrastively", "static embedding", "variance". Acceptable in an expandable section, but "static embedding" is not defined.
- Fix `happens[1]`: "Each token's vector is updated using the tokens on both sides of it, so it depends on context." and add the Devlin excerpt to the `contextual-vectors` claim.

#### pooling — confirmed_with_changes
- Supported: `bge-cls-normalized` (default pooling is cls), `pooling-strategies`, `raw-bert-poor`.
- Problem 1: `misconfigured` "Using the wrong pooling for a model hurts quality" is an unsourced generalisation that sits awkwardly with `pooling-strategies` ("With NLI classification training the choice mattered little").
- Problem 2: example `steps[1]` "Ignore the rest" may teach that the other tokens do not matter. The [CLS] vector was computed by the encoder from all tokens, which is why it can represent the sentence.
- Problem 3: "NLI", "regression training", "GloVe" in `learn_more` are not explained.
- Fix `misconfigured`: "Pooling should match how the model was trained (BGE uses [CLS]). In Sentence-BERT's experiments the choice mattered little in one training setup and max pooling did much worse in another. Raw BERT without similarity training makes poor sentence embeddings."
- Fix `example.steps`: ["Keep the [CLS] vector (the encoder has already mixed information from all tokens into it)", "The other token vectors are not used further"]
- Fix `learn_more` (jargon): replace "NLI classification training" with "training to classify sentence pairs (NLI)" and "regression training" with "training to predict a similarity score", and "GloVe" with "GloVe (a simple older word-vector method)".

#### normalizer — confirmed_with_changes
- Supported: `unit-vector-metrics`; ablation and code agree that without normalisation dot scores are unbounded and cosine is unaffected.
- Problem: `learn_more` "only models trained for it, such as OpenAI's text-embedding-3 with its dimensions parameter, shorten well". The claim says "Some models are trained so their vectors can be shortened" and cites Matryoshka (MRL) and the OpenAI docs; "only" is an inference no excerpt makes.
- Jargon: "cosine similarity", "Euclidean distance" are used before being defined; `why` says "makes dot product and cosine similarity the same measure" without saying what either is.
- Fix `learn_more` second sentence: "If you shorten vectors yourself you must re-normalize them. Some models, such as OpenAI's text-embedding-3 (with its dimensions parameter), are trained so that shortened vectors still work well."
- Fix `why`: "It makes the dot product (multiply matching numbers and add them up) and cosine similarity (how closely two arrows point the same way) the same measure."

#### similarity — confirmed
- Verified by running the real model: "a place to put my books" ranks `furniture-3` (the bookshelf sentence) first, with and without the instruction (0.6954 / 0.6328). 24 sentences scored; default top-k 5 ("top few" is fine). `scores-uncalibrated`, `lexical-vs-neural`, `models-not-comparable`, `mteb-no-winner` map correctly. With the lexical embedder and no shared words every score is 0.0, consistent with "finds nothing".

#### semantic_space — confirmed
- Code: PCA via SVD on mean-centred vectors, query projected with the same basis; `explained_variance` is returned and shown in the UI ("% kept"). Default query keeps 27% of the variance, which supports the cautionary text. 24 library points + 1 query = 25. Shapes/colours by topic exist (`CATEGORY_SHAPE`).
- Optional clarity improvement: `what` could say "A 3D map … (about a quarter of the spread by default; the UI shows the exact figure)".

---

## Required fixes in priority order

| # | File | Stage | Field | Replacement |
|---|---|---|---|---|
| 1 | rag-pipeline/explain.yaml | vector_index | what | "Stores all the chunk vectors so they can be searched. ExplodeAI uses a flat index: the vectors themselves, with no extra structure." |
| 1 | same | vector_index | why | "Search needs the chunk vectors in one place. A flat index still compares the question with every vector, which is exact. Faster approximate indexes exist, but this lesson does not use one. The index is where the knowledge lives." |
| 1 | same | vector_index | happens | ["Chunk vectors are stored as rows of one matrix, in the same order as the chunk list.", "A flat index adds no extra structure.", "A search compares the query against every stored vector."] |
| 1 | same | vector_index | misconfigured | "A flat index is exact but compares every vector, so it gets slow at very large scale. Approximate indexes (for example HNSW, which skips most vectors) are much faster but can occasionally miss the true best match." |
| 2 | rag-pipeline/explain.yaml | generator | what / happens / analogy / example.steps / misconfigured | see generator section above (five replacements) |
| 3 | tokenization/explain.yaml | decoder | why | "It shows whether anything was lost: with a byte alphabet the original text comes back exactly, and it is how model output becomes readable." |
| 4 | tokenization/explain.yaml | merge_learner | example | input "\" the\" spelled as: space  t  h  e  (it is frequent in the corpus)"; steps ["Most common pair: h + e → he (merge 1)", "Then space + t → \" t\" (merge 2)", "Then \" t\" + he → \" the\" (merge 3)"]; output "Merges in order: he, \" t\", \" the\" (these are the first three this lesson learns)" |
| 4 | same | encoder | example | input "\" the\""; steps ["Spell as bytes: space, t, h, e", "Apply merge he", "Apply merge \" t\"", "Apply merge \" the\""]; output "One token: \" the\"" |
| 4 | same | decoder | example | input "One token: \" the\""; steps ["Look up its bytes", "Join them"]; output "\" the\"" |
| 5 | rag-pipeline/explain.yaml | prompt_builder | example.steps[2], happens[2], happens[0], misconfigured | see prompt_builder section above |
| 6 | embeddings/explain.yaml | pooling | misconfigured, example.steps | see pooling section above |
| 7 | embeddings/explain.yaml | normalizer | learn_more, why | see normalizer section above |
| 8 | rag-pipeline/explain.yaml | embedder, query_encoder | misconfigured (+ claims) | add `models-not-comparable` (or an equivalent verified RAG claim) to `claims`; use the replacement text in each section above |
| 9 | rag-pipeline/explain.yaml | retriever | misconfigured, happens[0] | see retriever section above (add a claim for the Anthropic "can miss crucial exact matches" excerpt) |
| 10 | rag-pipeline/explain.yaml | embedder | happens[0], example.steps[1] | see embedder section above |
| 11 | rag-pipeline/explain.yaml | chunker | happens[0], happens[1], example.steps[0] | see chunker section above |
| 12 | rag-pipeline/explain.yaml | corpus | why, misconfigured | see corpus section above |
| 13 | rag-pipeline/explain.yaml | query_encoder | happens[2], example.input, example.steps[0] | see query_encoder section above |
| 14 | tokenization/explain.yaml | corpus | happens[1], happens[2], example.steps[1], misconfigured, learn_more | see corpus section above |
| 15 | tokenization/explain.yaml | input_text | misconfigured | see input_text section above |
| 16 | tokenization/explain.yaml | encoder | happens[2] | "Apply the learned merges in the order they were learned. The resulting symbols are the token ids." |
| 17 | tokenization/explain.yaml | merge_learner | happens[2] | "Repeat until the chosen number of merges is reached, or until no pair is left to merge." |
| 18 | tokenization/explain.yaml | pre_tokenizer | happens[1] | "A single space usually stays attached to the front of the next word." |
| 19 | embeddings/explain.yaml | tokenizer | analogy, happens[1], misconfigured | see tokenizer section above |
| 20 | embeddings/explain.yaml | library | claims, happens[0] | see library section above |
| 21 | embeddings/explain.yaml | encoder | happens[1] (+ add Devlin excerpt to `contextual-vectors`) | see encoder section above |
| 22 | tokenization/explain.yaml | base_alphabet | what (jargon) | add the byte and [UNK] explanation from the base_alphabet section above |

## Beginner-clarity list (jargon before it is explained)

- RAG: HNSW (vector_index.misconfigured), dense / cross-encoder / k1 / b (retriever), hallucinated (generator.learn_more), "tokenised" (query_encoder example).
- Tokenization: merges (corpus.happens), BPE (corpus.learn_more), byte, [UNK], Unicode code points (base_alphabet), end-of-text (vocabulary).
- Embeddings: [CLS], [SEP] (tokenizer), cosine similarity and dot product (normalizer.why), NLI, regression training, GloVe, contrastively, static embedding (learn_more sections).
