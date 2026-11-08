# Teaching layer accuracy review

Scope: `content/lessons/{rag-pipeline,tokenization,embeddings,attention,agents}/teaching.yaml`.
Checked against: `lesson.yaml` claims, `explain.yaml`, the experiment code in `backend/app/experiments/`, the UI in `frontend/src/`, and `backend/tests/test_teaching.py`.
No repository file was edited. Commands were run with `cd backend && PYTHONPATH=. uv run python ...`.

Severity key:
- ERROR: false, or misleading enough to teach a wrong idea or send the learner to something that is not there.
- RISK: uncited general claim, or loose wording a beginner could misread.
- NIT: optional.

Field paths are relative to the lesson's `teaching.yaml`. `ideas[n]` is zero-based.

## 1. Summary

| Lesson | ERROR | RISK | NIT |
|---|---|---|---|
| rag-pipeline | 6 | 10 | 5 |
| tokenization | 3 | 6 | 3 |
| embeddings | 2 | 5 | 4 |
| attention | 4 | 5 | 6 |
| agents | 2 | 9 | 6 |
| Total | 17 | 35 | 24 |

Most important findings:
1. Several tab hints and ideas describe UI that does not exist (RAG Chunks "boxes", RAG Ranking "three ways", Tokenization Replay "pick a word", Embeddings Vector tab "numbers being compared", Attention Order "difference is 0 / 0.45", Attention Pronoun "numbers in each row").
2. RAG prompt builder: "the last ones are dropped" is false. Code skips a chunk that does not fit and keeps later, smaller ones. With budget 15 the best chunk is dropped and a 5-word chunk is kept.
3. Attention: "each head works on 32 of the 64 numbers" is false. Each head reads all 64 and makes 32.
4. Agents: the Custom preset says the stand-in reads the policy. It never does. The refusal is hard-coded from the order's `custom_built` flag.
5. Agents: token counts come from the lesson's own tiny tokenizer and are presented with no caveat. The fixed part alone is 1,392 "tokens" for 1,674 characters.

---

## 2. Issues

### 2.1 rag-pipeline (`content/lessons/rag-pipeline/teaching.yaml`)

**R-E1 (ERROR) `experiment.tabs.chunks`**
Quote: "Each box is one chunk, named after its article (returns#0 is the first chunk of “Returns and refunds”)."
Problem: Each box is one article, not one chunk. Evidence: `frontend/src/lessons/rag/ResultViews.tsx` `ChunkDocView` renders one `<article>` per document, headed `{doc.id} · N chunks`, with the document text as shaded runs. Chunk ids exist only as a hover `title` and hidden text on the start marker. The article title "Returns and refunds" is never shown.
Fix: "Each box is one article, headed by its id and its number of chunks. Inside it the text is shaded: a ▏ marks where a chunk starts, overlapping words get their own shade, and chunks the retriever picked are highlighted. Hover a ▏ to see the chunk's name, such as returns#0."

**R-E2 (ERROR) `experiment.tabs.ranking`**
Quote: "Every chunk is ranked three ways: by meaning (dense), by keywords (BM25) and combined (hybrid). If a chunk you expected is low in one column, that is why it was missed."
Problem: The table has two rank columns, not three. Evidence: `RankingTable` columns are Kept, Chunk, "Dense rank · cosine", "BM25 rank · score", Text. The BM25 column appears only when Retrieval is BM25 or Hybrid (`showBm25`). There is no hybrid column. The hybrid result shows only in "Kept". Also "dense" is not "by meaning" under the default embedder (see R-R1).
Fix: "Every chunk with its dense rank and cosine score. When Retrieval is BM25 or Hybrid, a BM25 rank and score column is added. The Kept column shows the final order for the method you chose. With the default embedder, dense ranking is word-matching, so it often agrees with BM25."

**R-E3 (ERROR) `experiment.ideas[3].see`**
Quote: "The Ranking tab shows where the three methods disagree about the remaining chunks."
Problem: Same cause as R-E2. The tab shows dense and BM25 only. The first sentence ("all three pick the same three chunks") is correct. I ran dense, bm25 and hybrid on the default question and all gave returns#0, battery#1, returns#1.
Evidence for a real disagreement: service#1 is dense rank 4 but BM25 rank 11 (my run).
Fix: "Switch to BM25 or Hybrid and a BM25 column appears next to the Dense one. Compare the two columns for the chunks that were not kept: service#1 is 4th by dense rank but 11th by BM25."

**R-E4 (ERROR) `stages.prompt_builder.story`**
Quote: "If the chunks don't all fit, the last ones are dropped, and a chunk that was found but dropped never reaches the model."
Problem: Wrong rule. Evidence: `generation.py assemble_prompt` does `if context_words + chunk.words > budget: dropped.append(...); continue`. It skips the one chunk and carries on, so a smaller, lower-ranked chunk can still be included.
Run (default question, budget 15): included `['returns#1']` (5 words), dropped `['returns#0','battery#1']`. The best chunk is dropped and the Answer tab quotes only "Custom-built bikes cannot be returned."
`ideas[2].see` ("1 chunk included and 2 dropped") is numerically right but hides this.
Fix (story): "Chunks are added in rank order. A chunk that would push the total over the budget is skipped, and a smaller, lower-ranked chunk can still squeeze in after it. A skipped chunk never reaches the model."
Fix (`ideas[2].see`): add "Here the short returns#1 fits but returns#0, the chunk that holds the answer, is dropped."

**R-E5 (ERROR) `connections.prompt_builder->generator`**
Quote: "The assembled prompt is the only thing the generator sees. A fact that isn't in the prompt can't appear in the answer."
Problem: True for this lesson's baseline. False for the "real system" the same file describes, where the generator is a language model. The `big_picture.story` says models know things from training. `rag-hallucination` says RAG reduces but does not remove hallucination.
Fix: "The assembled prompt is the only place your documents reach the generator. If a fact is not in the prompt, the generator has nothing from your documents to use. A real language model may still add things from its training, right or wrong. This lesson's baseline can only quote the prompt."

**R-E6 (ERROR) `big_picture.example.note`**
Quote: "One question travels through all eight stages."
Problem: The question does not enter until stage 5. Evidence: `pipeline.py STAGE_DEPENDENCIES["query_encoder"] == []`. Stages corpus, chunker, embedder and vector_index never see it. The teaching's own `stages.query_encoder.story` says "This is where the question enters the machine". The threads for corpus, chunker and vector_index do not mention the question.
Fix: "The question joins at the fifth stage, the Query embedder. The first four stages prepare the documents it will be matched against. Look for it in the “In our example” box from stage 5 on."

**R-R1 (RISK) `stages.retriever.story`**
Quote: "This lesson can rank by meaning (dense), by keywords (BM25), or by both combined (hybrid)."
Problem: With the default embedder, dense ranking is word-matching. `explain.yaml retriever.misconfigured` says so, and so does the UI notice under the controls.
Fix: "This lesson can rank by vector similarity (dense), by keywords (BM25), or by both combined (hybrid). With the default embedder, dense ranking is itself word-based. Switch to the local neural embedder to get meaning-based dense ranking."

**R-R2 (RISK) `stages.chunker.story` and `connections.corpus->chunker`**
Quote: "Whole articles are too big to search precisely and too big to fit in a prompt" / "A big document can't be searched precisely or fitted into a prompt."
Problem: Uncited and not generally true. `rag-small-kb` says a knowledge base under about 200,000 tokens can go in the prompt. In this demo each article is about 40 words against a 200-word budget, so they would fit. `explain.yaml` says "too big and too mixed to be a good answer".
Fix: "A whole article mixes several topics, so it matches a question only vaguely, and a prompt has limited room, so you want to send only the most relevant pieces."

**R-R3 (RISK) `stages.chunker.story`**
Quote: "Think of cutting a page into index cards, one idea per card."
Problem: The chunker cuts by sentence packing or fixed word count (`chunking.py`). It does not detect ideas, and the lesson's whole point is that cuts can land mid-fact.
Fix: "...index cards. This lesson cuts by sentence or by a set number of words, not by idea, so a card can hold half a topic."

**R-R4 (RISK) `stages.corpus.story` and `stages.corpus.check.answer`**
Quote: "you can change what the system knows just by changing the documents" / "you can replace or update the documents at any time without retraining anything".
Problem: Documents must be re-chunked and re-embedded (the index rebuilt). `rag-swap-index` says "replacing the index". The demo recomputes everything each run.
Fix: "...by changing the documents and rebuilding the index (re-cutting and re-embedding them). Nothing needs retraining."

**R-R5 (RISK) `stages.chunker.check.answer`**
Quote: "Make the chunks bigger, or let neighbouring chunks overlap, so a whole fact sits inside at least one chunk."
Problem: Over-guarantees. `chunking-overlap` says overlap "reduces the chance". Bigger chunks help but blur topics (`explain.yaml chunker.misconfigured`). "Two ways" is not the only answer: cutting at sentence boundaries is a third.
Fix: "Let neighbouring chunks overlap, make the chunks bigger, or cut at sentence boundaries. Each makes it more likely that a whole fact sits inside one chunk. Bigger chunks cost precision."

**R-R6 (RISK) `stages.embedder.story` and `big_picture.analogy`**
Quote: "it builds the fingerprint from the words used, 1024 numbers per chunk".
Problem: Incomplete. `embedding.py` lowercases, drops about 40 stopwords, trims plural endings, adds pairs of neighbouring words, weights by TF-IDF, then hashes into 1024 slots with a sign. Different words can collide, which creates false matches (see R-R7).
The "fingerprint" analogy suggests exact identity. Here it is a closeness score. The `breaks` sentence does not say so.
Fix: "it builds the fingerprint from the words used (and pairs of neighbouring words), weighted by how rare they are and folded into 1024 numbers. Unrelated words can occasionally land in the same slot." Add to `breaks`: "Unlike a real fingerprint, these are compared by how close they are, not for an exact match."

**R-R7 (RISK) `experiment.presets.Synonym test (lexical embedder fails it).notice`, lexical half**
Quote: "With the simple embedder the first result is battery#0, a battery chunk, and the Answer tab finds nothing to quote, because “money back” shares no words with “refund”."
Problem: It leaves out why battery#0 is first. My run: scores battery#0 0.075, returns#0 0.0, returns#1 0.0. No chunk shares a word with the question. battery#0 leads through a hash collision. returns#0 and returns#1 are 2nd and 3rd only because tied scores are broken by chunk order (`rank()` sorts by `(-score, i)`). A learner who reads the Chunks tab may think the embedder half-found the returns chunks.
Fix: "With the simple embedder no chunk shares a word with the question, so every score is about zero. battery#0 comes first by a hash collision, and returns#0 and returns#1 follow only because ties are listed in chunk order. The Answer tab finds nothing to quote."

**R-R8 (RISK) same preset, neural half**
Quote: "...the first result is returns#0, the returns policy. Keyword-style matching needs shared words; embeddings match meaning."
Problem: (a) This number is not in `test_teaching.py`. I ran it: returns#0 0.643, warranty#1 0.641, returns#1 0.608. The margin over a claim-filing sentence is 0.002. (b) The Answer tab still shows "The retrieved context does not contain an answer", because the extractive baseline needs shared words (`sentences: []`). A learner will expect it to now answer. (c) "embeddings match meaning" is stated flatly. `lexical-misses-synonyms` says neural models "often catch them".
Fix: "With the Local neural embedder (if installed) returns#0 comes first, though only just ahead of a warranty chunk. Embeddings can match paraphrases that keyword matching cannot. The Answer tab still finds nothing to quote, because the baseline picks sentences by shared words. A real language model would read returns#0 and answer."

**R-R9 (RISK) `experiment.tabs.answer`, `stages.generator.story`**
Problem: Not wrong for the default, but incomplete. `ResultViews.tsx AnswerView` also renders `LLMAnswerPanel` ("Real LLM answer: off" unless the backend has a key and budget). A learner who sees that panel may be confused by "it is not a language model".
Fix: add "Below it, an optional real-model answer panel appears; it is off unless the site owner has switched it on."

**R-R10 (RISK) `stages.prompt_builder.thread`**
Quote: "Our three chunks use 66 of the 200 words allowed".
Problem: Correct (`context_words`). But the budget counts chunk words only, not the instructions, the question or the tags, and it counts words, not tokens (`text.py` docstring).
Fix: "Our three chunks use 66 of the 200 words of context allowed (the budget counts chunk words, not tokens)."

NITs:
- **R-N1 `experiment.tabs.prompt`**: "The exact text the generator will read". The baseline does not read the prompt text. `pipeline.py` passes `in_context` chunks to `extractive_answer`. It is exact only for a real model.
- **R-N2 `experiment.presets.Battery storage.notice`**: with a 15-word budget all three chunks are dropped (0 included, battery#1 is 25 words). "the useful chunk can be dropped" is true but understated.
- **R-N3 `big_picture.story`**: "Getting the documents ready happens once". True for real systems. This demo recomputes the first four stages every run (`explain.yaml embedder.happens`).
- **R-N4 `connections.chunker->embedder`**: "Each chunk is fingerprinted on its own". TF-IDF is fitted across all chunks (`embedder.fit(texts)`), so a vector depends on the others.
- **R-N5 `stages.embedder.thread`**: "their fingerprints look alike". The best cosine for the default question is only 0.117 (Ranking tab). Say "score highest".

---

### 2.2 tokenization (`content/lessons/tokenization/teaching.yaml`)

**T-E1 (ERROR) `experiment.tabs.replay`**
Quote: "Pick a word and step through the merges that built it, from single symbols to the final token."
Problem: No word picker. Evidence: `TokenViews.tsx MergeReplay` has Previous, Play and Next buttons and a "Merges applied" slider. `adapter.ts replayEvents` interleaves every merge applied to every piece of your input text, in rank order.
Fix: "Step through the merges applied to your text, one at a time, with the Previous and Next buttons or the “Merges applied” slider. The piece that just changed is highlighted."

**T-E2 (ERROR) `experiment.ideas[0]`**
Quote: "Open the Replay tab and pick “ keeper”."
Problem: Same cause. The place that follows one word is the Merges tab, "How the most frequent words were built". It lists the corpus's top four pieces: " the" (28), "." (22), "\n" (11), " keeper" (11). My run confirmed.
The six merges are right: er (rank 4), ep (10), ke (11), " ke" (12), " keep" (13), " keeper" (14).
Fix: "Open the Merges tab and find “ keeper” under “How the most frequent words were built”. Seven starting symbols become one token in six merges (er, ep, ke, “ ke”, “ keep”, “ keeper”). In the Replay tab you can watch the same six steps, mixed in with the other words' merges."

**T-E3 (ERROR) `experiment.presets.Unseen words.notice`**
Quote: "Words the tokenizer learned stay whole (“ lantern”, “ clock”) while words it never saw fall into pieces (“ke”, “ep”, “er”, “s” for “keepers”)."
Problem: The input has no words “lantern”, “clock” or “keepers”. The pre-tokenizer pieces are " lanternkeepers", " rewound", " clockwork". My run (100 merges) gave 18 tokens: `The | lantern | ke ep er s | ' ' r e w o un d | clock | w or k | .`. “ lantern” and “ clock” are only the front of compounds. The unseen word “rewound” takes 7 tokens, which is the most striking fragmentation and is not mentioned.
Fix: "18 tokens. Parts the tokenizer learned come out as single tokens (“ lantern”, “ clock”), and the rest of each unseen word is spelled out in small pieces: “ke”, “ep”, “er”, “s” finish “lanternkeepers”, “w”, “or”, “k” finish “clockwork”, and “rewound” breaks into 7 tokens (a space, r, e, w, o, un, d). At 0 merges it is 37 tokens, at 25 it is 23 and at 300 it is 16."

**T-R1 (RISK) `stages.base_alphabet.check.question`**
Quote: "Why can a byte alphabet spell any text when a character alphabet can't?"
Problem: Only the "Training characters" alphabet can't. A full Unicode character alphabet could spell any text, with over 130,000 symbols (`gpt2-byte-level`). The answer's own wording ("only holds characters seen in training") shows what was meant.
Fix: "...when an alphabet of only the characters seen in training can't?"

**T-R2 (RISK) `stages.input_text.story` and `stages.input_text.check.answer`**
Quote: "because it can always fall back on single bytes" / "split into smaller known pieces, down to single bytes if necessary, so nothing is lost".
Problem: True only with the 256-bytes base. With Training characters an unseen character becomes [UNK] and the text is lost (`char-bpe-unk`; the same file's Accents preset shows it).
Fix: "...because, with the 256-byte alphabet, it can always fall back on single bytes."

**T-R3 (RISK) `big_picture.analogy.breaks`**
Quote: "Real tokenizers (the ones inside GPT, Claude or Gemini) have their own much bigger vocabularies."
Problem: Only GPT-2's size is cited (`gpt2-vocab-size`, 50,257). No claim gives Claude's or Gemini's vocabulary size. (The UI notice says the same.) Very likely true but uncited.
Fix: "Real tokenizers, such as GPT-2's with 50,257 tokens, have much bigger vocabularies. This one is tiny..."

**T-R4 (RISK) `experiment.presets.Accents and emoji.notice`**
Quote: "With Training characters, 4 tokens become [UNK]...; With 256 bytes, there are no unknown tokens (17 tokens)".
Problem: Numbers are tested. The preset name says "Accents and emoji", but the 4 unknowns are C, é, è and ☕ (capital C is not in the lowercase-heavy log). A learner looking for four accents/emoji finds three. In bytes mode é, è and ☕ show as PARTIAL byte tokens (2, 2 and 3 tokens), not as characters. I ran both.
Fix: "With Training characters, 4 tokens become [UNK]: the capital C (the log has none), é, è and ☕. ... With 256 bytes there are no unknown tokens (17 tokens); é, è and ☕ appear as PARTIAL tokens because each is spelled out as 2 or 3 bytes."

**T-R5 (RISK) `connections.encoder->decoder`**
Quote: "...turns them back into text to prove nothing was lost."
Problem: The decoder's job is to turn ids into text. The comparison with the original is this demo's check.
Fix: "The token numbers go to the decoder, which turns them back into text. Here we also compare that text with the original to check nothing was lost."

**T-R6 (RISK) `stages.decoder.story`**
Quote: "That round trip is a good test that the whole pipeline is working."
Problem: A round trip shows only that the tokenizer is lossless. The 0-merge, 35-token version round-trips too. It says nothing about whether the merges are good.
Fix: "A passing round trip shows the tokenizer is lossless. It does not show the tokens are good ones: the 35-token version at 0 merges round-trips too."

NITs:
- **T-N1 `big_picture.analogy.mapping[Decoder]`**: "taking the bricks apart". The decoder does not un-merge. It looks up each token's bytes and joins them.
- **T-N2 `connections.input_text->encoder`**: "the one input that changes from run to run". The settings also change.
- **T-N3 `experiment.presets.Familiar sentence.notice`**: at "300" only 216 merges are learned (the UI shows "Training ran out of pairs after 216 merges"). Vocabulary 473 = 257 + 216 is correct. A sentence telling the learner this would help.

---

### 2.3 embeddings (`content/lessons/embeddings/teaching.yaml`)

**E-E1 (ERROR) `experiment.tabs.vector`**
Quote: "The real numbers for your text: a small slice of each vector... These are the numbers being compared."
Problem: The tab shows one vector, not "each". It is your sentence's vector, first 48 of 384 values. And it is the vector before normalising. Evidence: `pipeline.py "pooled_preview": q_raw[:48]` (pre-normalisation). The label reads "LENGTH 9.249 → 1.000". The compared numbers are those divided by 9.25. Per-token vectors (first 24 numbers each) are on the Tokens tab (`TokenHeat`). Bars are scaled to the largest of the 48, so height is relative.
Fix: "The first 48 of the 384 numbers in your sentence's vector, as pooled from the [CLS] token before it is scaled to length 1 (the line under it shows the length going from about 9.25 to 1.00). Bar height is relative size and fill shows positive or negative. Scaling divides every number by that length, so the compared vector has the same shape. Per-token vectors are on the Tokens tab."

**E-E2 (ERROR) `stages.your_text.check.answer`**
Quote: "...so only a method that understands meaning can connect them."
Problem: "only" contradicts `lexical-misses-synonyms` ("unless synonyms or query expansion are added"). "understands" is the idea the lesson should avoid: an embedding is a trained numeric similarity, not understanding.
Fix: "It shares no words with the bookshelf sentence yet is related, so a method that only matches shared words (the Lexical option) cannot connect them, while a neural embedding trained on text pairs often can."

**E-R1 (RISK) `experiment.ideas[0].see`**
Quote: "A red notice says the two sets of vectors can't be compared..."
Problem: The default tab is Semantic space. There the library shows without your text's ring and with no notice. The notice is in the Neighbours tab (`Neighbours` returns the `notice--error` paragraph when `!result.comparable`). The header also shows "NOT COMPARABLE".
Fix: "Open the Neighbours tab: a red notice says the two sets of vectors can't be compared, because they come from different models."

**E-R2 (RISK) `experiment.presets.Bookshelf.notice`**
Quote: "With Lexical the neighbours are animal sentences at score 0.0: no shared words, nothing to match." and "shares no words with them".
Problem: Every score is tied at 0.0, so the list is the first sentences of the library in library order: dog, kitten, wolves, parrot (`ranked = sorted(..., key=(-score, i))`). It is not a match with animals. Also the desk and armchair sentences contain the word "a", which the lexical embedder ignores as a stopword. Say "no content words".
Fix: "With Lexical every score is 0.0, so the list just shows the first sentences in the library (the animal ones). That is a tie, not a match: no shared words, nothing to match."

**E-R3 (RISK) `big_picture.analogy.mapping[Encoder]` and `connections.tokenizer->encoder`**
Quote: "a reader who understands each piece in the context of the whole sentence" / "can be understood in the context of the others".
Problem: Anthropomorphic. In a lesson about embeddings, "understands" invites "embedding = meaning". `breaks` does not address it.
Fix: "a reader whose vector for each piece is computed from the whole sentence around it".

**E-R4 (RISK) `experiment.ideas[3]` (pooling)**
Quote: "Both turn the token vectors into one sentence vector, in different ways, so the scores change."
Problem: Omits that bge-small was trained with [CLS] pooling (`explain.yaml` pooling: "Pooling should match how the model was trained"). Mean is a mismatch. My runs: books top score 0.695 → 0.645. For "a vehicle that runs on rails" the order changes (horse first at 0.584, then truck 0.556).
Fix: add "This model was trained to use [CLS], so Mean of tokens is off its training. Try “a vehicle that runs on rails”: the order of the top two changes."

**E-R5 (RISK) `big_picture.story`**
Quote: "...a point on a map where its nearest neighbours are the sentences that mean something similar."
Problem: Stated as fact, then the Where-it-goes-wrong preset shows a miss. `semantic-similarity` says "suggest".
Fix: "...whose nearest neighbours are usually sentences that mean something similar."

NITs:
- **E-N1 `stages.semantic_space.story`**: "a picture, not a calculation". PCA is a calculation. It is a view, not part of the search (`explain.yaml`).
- **E-N2 `experiment.intro`**: "Every run here uses a real small model". Not when both embedders are Lexical. The model is Qdrant's reduced-precision ONNX port, "not measured against BAAI's original weights" (`model.py`).
- **E-N3 `experiment.presets.Where it goes wrong.notice`**: "this is a real miss". True for this build. Consider "for this small model".
- **E-N4 `experiment.presets.Puppy.notice`**: "the match is by meaning, not just words". The top match shares "puppy" and "fetch(es)". The 2nd and 3rd (dog, horse) share nothing. Say so.

---

### 2.4 attention (`content/lessons/attention/teaching.yaml`)

**A-E1 (ERROR) `big_picture.example.note` and `stages.qkv.story`**
Quote: "two heads each work with 32 of them" / "With 2 heads, each head works on 32 of the 64 numbers."
Problem: Each head reads all 64 numbers and produces a 32-number query, key and value. Evidence: `model.py weights()` splits the (64,64) matrices column-wise into (heads, 64, d_k). `pipeline.py q = einsum("nd,hdk->hnk", x, w.wq)` uses all 64 input dimensions. Claims `attn-qkv-projections` and `attn-multihead-concat` ("different learned projections").
Fix: "Each word is 64 numbers. Each of the two heads reads all 64 and makes its own 32-number query, key and value for the word."

**A-E2 (ERROR) `experiment.ideas[0]`**
Quote: "Set Heads to 8 and Scale scores to Off. The strongest weight rises to about 63% ...: with big scores, softmax piles almost everything onto one word."
Problem: 63% is the tested number (heads 8, scale off), but "almost everything" is not 63%. With 8 heads d_k is 8 and the scores are not very large (raw spread 3.6). My runs, mean strongest weight, "the cat sat on the mat": 1 head off 93.7%, 2 heads off 79.3%, 4 heads off 72.6%, 8 heads off 62.9%, 8 heads on 37.4%, 1 head on 42.4%. `attn-softmax-saturation` cites about 90% for a 64-wide head (heads = 1).
Fix: "Set Heads to 1 and Scale scores to Off. The strongest weight averages about 94%: with big scores softmax piles almost everything onto one word. Turn scaling on and it falls to about 42%." (Add these two numbers to `test_teaching.py` if used. With 8 heads the effect is 63% vs 37%.)

**A-E3 (ERROR) `experiment.presets.Order.notice`**
Quote: "...the order difference is exactly 0. With position on it is about 0.45. This shows up in the Break & fix check and in the “What breaks if removed?” card".
Problem: No number is displayed. `attendOutcome.tsx` shows "Order matters: yes/no" (threshold 0.05). The Break & fix message is a sentence (`routers/attend.py`: "Reordering the words changes nothing..."). The experiment's `StatsStrip` has no order item (the `lesson.yaml` preset note, "The Order matters check in the stats", has the same problem).
Numbers: 0.0 is asserted by the test. 0.4548 is correct from my run, but it is not asserted.
Fix: "With position off (and the mask off) the layer can't tell “dog bites man” from “man bites dog”, and the check shows “Order matters: no”. With position on it shows “yes”. (The size of the difference is exactly 0 versus about 0.45.)" Also add the 0.45 case to `test_teaching.py`.

**A-E4 (ERROR) `experiment.presets.Pronoun.try` and `experiment.tabs.grid`**
Quote: "Click it and look at the row for “it”." / "The numbers in each row add up to about 100%."
Problem: Cell numbers are printed only for sentences of 8 words or fewer. Evidence: `AttendViews.tsx` `n <= 8 || compact ? (w*100).toFixed(0) : ''`. The Pronoun sentence has 12. The learner sees bars only. The percentages appear on hover (the caption under the grid) and in the One word tab.
Fix (try): "Click it, open the One word tab and pick “it”." Fix (grid hint): add "(For sentences longer than 8 words the cells show bars only; hover a cell to read its number.)"

**A-R1 (RISK) `stages.mix.story`**
Quote: "A word that pays most attention to “on” ends up with a vector that is mostly “on”'s value."
Problem: "most attention" in this lesson is 30%. The blend is 30% “on” and 70% others.
Fix: "A word that pays the biggest share of its attention to “on” gets the biggest share of its new vector from “on”'s value."

**A-R2 (RISK) `stages.mix.check.answer`**
Quote: "...by blending the other words' values using the attention weights."
Problem: Includes the word's own value. Self-weight averages about 20% in the Cat run, and `attn-causal-mask` says a word can still attend to itself.
Fix: "...by blending the words' values (its own included) using the attention weights."

**A-R3 (RISK) `stages.embed_pos.story` and `stages.embed_pos.check.answer`**
Quote: "Without it, “dog bites man” and “man bites dog” would look identical to the layer." / "...rearranging the words gives the same result."
Problem: True only with the mask off (`attn-position-needed`: "no position vectors and no mask"). My run: position off + causal on gives an order difference of 3.97, so order matters even without positions. Also "the same result" means each word gets the same output vector, only listed in a different order.
Fix: "Without it, and with no mask, each word gets exactly the same output vector whatever order the words arrive in, so “dog bites man” and “man bites dog” cannot be told apart."

**A-R4 (RISK) `experiment.ideas[1].see`**
Quote: "In a real model each head learns a different job."
Problem: Uncited and too strong. `attn-multihead-motivation` gives only the authors' reason, and says too many heads also hurt.
Fix: "In a trained model, heads can end up doing different jobs, though not every head is equally useful."

**A-R5 (RISK) `stages.output.story` and `experiment.tabs.out`**
Quote: "In a real model this is handed to the next layer." / "These would go to the next layer in a real model."
Problem: `attn-residual`, `attn-not-all-you-need`: the real block adds the input back, normalises, and applies a feed-forward layer first.
Fix: "In a real model this is added back to the input, normalised and passed through a feed-forward layer before the next layer."

NITs:
- **A-N1 `stages.tokens.check`**: the answer is circular ("later steps need to know where each word sits"). Better: "The next step adds a position pattern to each word's vector, so it needs each word's place."
- **A-N2 `experiment.presets.Cat.notice`**: "The strongest weight averages about 35%" is the mean over rows AND heads of each row's largest weight (the "Strongest weight (average)" box). The Average grid's row maxima average 33%.
- **A-N3 `experiment.presets.Pronoun.notice`**: the 28% for “too” comes mostly from head 2 (51%). In head 1 “it” looks most at “tired” (22%). Mention the Head to show control.
- **A-N4 `experiment.ideas[3]` and `tabs.word`**: the One word tab shows the weights, not the blended vector.
- **A-N5 `stages.scores.check.answer`**: "scores grow with the vector size". Spread grows like √(head size) (`attn-sqrt-dk-scaling`).
- **A-N6 `stages.output.check.answer`**: "Each head can look for a different kind of relationship". Say "the authors' reason; in this toy the heads are random".

---

### 2.5 agents (`content/lessons/agents/teaching.yaml`)

**G-E1 (ERROR) `experiment.presets.Custom.notice`**
Quote: "The order data says the bike is custom-built, and the policy says custom-built bikes can't be returned, so the agent refuses."
Problem: The stand-in never reads that policy sentence. Evidence: `policy.py _eligible` returns False when `order.get("custom_built")` is true. `compose_answer` returns the hard-coded string "…is custom-built, and custom-built bikes cannot be returned." Only the window (`within N days of delivery`) is parsed from the policy text. The policy search still runs (step count 4 is right).
Fix: "The order data says the bike is custom-built, so the stand-in's rule refuses. (The help-centre article says the same, but this simple rule reads only the order's custom-built flag. A language model would be reading the policy text.)"

**G-E2 (ERROR) `stages.tools.check.answer` and `stages.tools.story`**
Quote: "The model only sees each tool's name and description, so that is all it has to pick the right tool with." / "...only this description, so the description is what it uses to choose."
Problem: Contradicts the same story ("rules for its inputs"), `tool-definition` (name, description and parameter schema) and `tabs.tools` (name, description, rules). The stand-in does compare descriptions only (`policy.py` docstring: "real models also read names and schemas"). Anthropic's guidance (`tool-descriptions-matter`) calls detailed descriptions the most important factor, not the only input.
Fix: "The model sees each tool's name, description and input rules, and the description is the most important part for choosing the right tool. The stand-in here compares descriptions only."

**G-R1 (RISK) `stages.context.thread`, `experiment.ideas[3].see`, `experiment.tabs.context`**
Quote: "Step 1 reads about 1,475 tokens. By step 5 it reads 2,799. Across the first five steps the model reads about 11,000 tokens in total."
Problem: Numbers are tested. They come from the lesson's own teaching tokenizer (`pipeline.py count_tokens` uses a 300-merge byte BPE trained on the lighthouse log). `TOKEN_LABEL` says "not any provider's, so real counts differ". The Token cost and What the model reads tabs print that caveat. The teaching text and the Loop tab do not. Scale: the fixed part (system prompt plus tool definitions) is 1,674 characters and counts as 1,392 tokens here. By the 4-characters-per-token rule of thumb (`openai-rule-of-thumb`) a real tokenizer would give roughly a third of that. The growth pattern is real, the magnitude is not.
Fix: "Step 1 reads about 1,475 tokens (counted with this site's small teaching tokenizer, so a real model's count would be lower, but each step still adds to the one before)."

**G-R2 (RISK) `big_picture.story`, `stages.execute.story`, `stages.execute.check`**
Quote: "The model only asks. Your code runs the tools" / "Who actually runs a tool, the model or the application? The application."
Problem: True for tools you define yourself. `tools-run-in-application` notes that Anthropic also offers server tools that Anthropic runs. Not covered by a qualifier.
Fix: "For tools you define yourself, the model only asks and your application runs them."

**G-R3 (RISK) `big_picture.analogy.mapping[Check]`**
Quote: "a supervisor glancing over a form before it goes anywhere".
Problem: Check is an automatic format test (`tools.validate`: type, pattern, length). A "supervisor" suggests judgement or approval, which is the separate human-approval step at Run (`pipeline.py` holds the refund with "waiting for a person to approve").
Fix: "a clerk who checks that every box on the form is filled in the right format, without judging whether the request is a good idea".

**G-R4 (RISK) `connections.tools->decide`**
Quote: "It can only choose from what it has been shown."
Problem: True of the stand-in. Real models can emit a tool name that was not offered. `tool-errors-are-results` treats unknown tools as protocol errors, and the demo's `execute` has an "unknown tool" branch.
Fix: "It is meant to choose only from what it has been shown, and the application should reject any other name."

**G-R5 (RISK) `stages.decide.story` and `stages.decide.check`**
Quote: "either asks for one tool (with its inputs) or gives the final answer" / "What are the two things the model can do at each step?"
Problem: In this lesson, yes. Real tool-calling APIs let a model request several tools in one reply; not covered by a claim. The check question reads as general.
Fix: "In this lesson, at each step it either asks for one tool or gives the final answer (real systems may allow several calls at once)."

**G-R6 (RISK) `stages.tools.thread`**
Quote: "The refund tool changes something real, so it needs a person's approval."
Problem: In the demo nothing real changes. `tools.py issue_refund` writes to a ledger only. The corpus note says "no money moves". Approval is also a setting (Person approves refunds).
Fix: "The refund tool changes something in the world (here it only adds a line to a pretend ledger), so by default it needs a person's approval."

**G-R7 (RISK) `experiment.ideas[2].see`**
Quote: "Turn approval on, or switch the refund tool off, and it can't."
Problem: True, but incomplete. My run with the refund tool off: the stand-in calls get_order A1001 seven more times and stops at the 8-step limit with no answer. With approval on it stops and waits; you can still press Approve this refund.
Fix: "With approval on, the refund waits for you. With the refund tool off, no refund can be issued, but the stand-in gets stuck calling the order lookup until the step limit."

**G-R8 (RISK) `experiment.tabs.tools`**
Quote: "The four tools exactly as the model sees them".
Problem: The tab adds a "CHANGES THINGS · NEEDS APPROVAL" label, driven by the app-side `side_effects` flag (`AgentViews.tsx ToolsView`), which is not part of what a model is sent. It shows "needs approval" even when Person approves refunds is Off. Only three tools show when the refund tool is off.
Fix: "The tools as the model is given them: a name, a description and rules for the inputs. The orange label is added by this site to mark tools that change things."

**G-R9 (RISK) `experiment.tabs.conversation`**
Quote: "Everything the model reads on its last step."
Problem: The tab lists the tool definitions by name only (`ConversationView` "Tools" bubble). The full definitions are on the Tools tab, though they are counted in the tokens.
Fix: "The conversation the model reads on its last step. Tool definitions are shown here by name only (full text on the Tools tab) but they are included in the token count."

NITs:
- **G-N1 `experiment.presets.Return.notice`**: the list omits step 1 (the policy search), so the five steps listed do not add up to the five shown.
- **G-N2 `stages.decide.story`**: the bars are shared words between what it wants and a description (`score_tools`), shown relative to the best bar. Not a semantic match.
- **G-N3 `big_picture.story`**: "An agent is a language model that can take actions" vs "The model only asks". Prefer "can ask for actions to be taken".
- **G-N4 `stages.observe.thread`**: "2,899 CAD" is the Loop tab's readable summary. The raw result has `price: 2899.0` and no currency field.
- **G-N5 `experiment.ideas[1].see`**: "confidently tells the customer there is none". The answer is "I couldn't find an order called 1001." Accurate but plain.
- **G-N6 `stages.context.story`**: "why each step costs more". Uncited for real billing (provider caching, `tool-tokens-billed` only says billed as input).

---

## 3. Checked and found correct (most at risk of being wrong)

RAG:
- Retriever.thread "battery#1 sneaks in because the simple embedder is only matching words": the shared word is "long" (from "long-term"). BM25 also ranks it 2nd.
- All three methods return the same three chunks for the default question (not covered by the test; I ran it).
- Return policy and Warranty answer sentences match the run. Battery storage at budget 15 drops the useful chunk (matches the `budget-overflow` challenge).
- The fixed-word chunk counts (37, 65, 6) and top-k 6 = 145 words are test-backed.
- Local neural returns returns#0 first for "Can I get my money back?" (0.643). Neural is installed here.
- "Own dotted line" for the question exists (`rag/adapter.ts` adds a `kind: 'query'` link into the query embedder).
- Vector space legend: ◆ query (octahedron), ● retrieved (filled), ○ others (wireframe).

Tokenization:
- First three merges h+e, " "+t, " t"+he. Not covered by `test_teaching.py`: its check reads `r["training"]["merges"]` but the key is `steps`, so that assertion never runs. I verified by hand.
- 257 = 256 bytes + 1 special; the special token's id is 356 (placed last), so "257 to start with" counts, it does not order.
- 84 boundary-crossing tokens at 150 merges with no pre-tokenizer, including "e ". Reversed order on "The keeper trimmed the lantern wick." (200 merges) gives ke|ep|er and l|an|t|er|n.
- Corpus has no digits. "keeper" occurs 11 times and "lantern" 10.
- Control labels and options (Merges learned, Base alphabet 256 bytes/Training characters, Pre-tokenizer, Merge order when encoding Learned order/Reversed) match the UI.

Embeddings:
- Sentence-to-score mapping for Puppy (puppy .717, dog .637, horse .564), Bookshelf, Commute (desk .588, bus .561; with instruction bus .515 vs desk .502) and Rails (truck .619, horse .613, plane .597). The test asserts categories and scores only.
- "Tendency, not a guarantee" is the lesson's own wording (`lesson.yaml`, short-query challenge). "ranks 14th of 24" is rank within all 24.
- Dot product with Normalize off gives 58.1 etc., outside −1..1; cosine is unaffected (`score()` normalises both).
- Ring, "Show as table", hover, colours and shapes by topic, and the control names (Library embedder, Your-text embedder, Pooling, Similarity, Normalize to length 1, BGE query instruction) match the UI.

Attention:
- "sat" gives 30% to "on": head 1 28%, head 2 32%, mean 30%. All other weights are smaller.
- 15 of 36 cells masked (strict upper triangle). Future mass 0% with the mask on.
- "it": too 27.6%, animal 8.5%. The sentence has exactly 12 words, the cap.
- Order gap: 0.0 with position off, 0.4548 with position on (the latter untested).
- "Head to show", Average/Head 1/Head 2, "Attention on later words" and the tab names match.

Agents:
- Step counts, token series, refund R-001 and the 16/30/50-day wording are test-backed.
- The "1001" → "A1001" retry is real. "waiting for a person to approve" is the exact string.
- Vague + no limit runs to the 30-step safety cap with about 134k "tokens". Limit 8 stops at 8 with no answer.
- Check off: "I couldn't find an order called 1001."
- Forum post on + approval off: refund R-001 issued for A1001, which the customer never mentioned (poisoned page retrieved first).
- Policy: "refunds go to the original payment method within 5 business days". Status: 2 steps.
- Control and tab names (The loop, What the model reads, Tools, Token cost; Approve this refund) match.

---

## 4. Not verified, and why

- I did not render the UI. All statements about tabs, labels and colours come from reading the React source. I did not check CSS visuals (hatch pattern, "red" for `notice--error`, which is `var(--color-error)`).
- I did not read every citation excerpt behind every claim. I used the claim text, and excerpts where a point was in doubt.
- Claude and Gemini vocabulary sizes (T-R3) cannot be verified from the repo. No claim covers them.
- G-R1: the "roughly a third" real-tokenizer estimate is from the 4-characters-per-token claim, not from running a real tokenizer.
- A-E2's 93.7% and 42.4% and A-E3's 0.4548 are my own runs. They are not in `test_teaching.py`.
- Whether models can issue parallel tool calls (G-R5) and whether provider prompt caching changes step cost (G-N6) are not covered by any claim in the lessons, and I did not research them.
- R-R8's neural numbers depend on the locally downloaded bge-small model. They matched the test environment but may differ on other builds.
- `test_teaching.py` has two weak spots: the tokenization merge assertion never runs (wrong key), and the embeddings `q["tokens"]` check is `... if isinstance(...) else True`.
