# Embeddings — Pass 2 independent factual cross-check

Date: 2026-10-19. Inputs: `content/lessons/embeddings/lesson.yaml` (24 claims, 47 excerpts, plus component, challenge, tour, visual and experiment text), `content/sources.yaml`, and the implementation in `backend/app/experiments/embed/` (`model.py`, `pipeline.py`, `ablation.py`, `corpus.py`) and `backend/app/routers/embed.py`. The Pass 1 report was read only for context and was not relied on.

## Method

- Every cited URL was downloaded directly with curl into an empty scratch directory, and the conversion scripts were kept in a separate directory and run with `python3 -I`. Plain text was produced with BeautifulSoup for HTML and pypdf for PDFs. arXiv papers were taken from the abs page and from the versioned PDF named in sources.yaml: word2vec v3, BERT v2, Ethayarajh v1, SimCSE v4, MRL v4 and MTEB v3. SBERT has only v1, so the v1 PDF was used. The BGE files came from the raw URLs at the pinned commit `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`: README.md, config.json, sentence_bert_config.json, 1_Pooling/config.json, modules.json and tokenizer_config.json. fastembed's `onnx_embedding.py` came from raw.githubusercontent.com at commit `de502ca83baa2b81922cb5a46acf689f5e2c72a1`. No summarising fetch tool was used to confirm any excerpt.
- Each excerpt was matched against that text three ways. **Strict** is a raw substring match. **Loose** applies NFKC normalisation, which removes ligatures, then removes Markdown backticks and `**`, unescapes `\"`, normalises quotes and dashes, removes line-break hyphenation, collapses whitespace and lowercases. **Squash** compares alphanumerics only, to catch PDF spacing artefacts. Excerpts containing `...` were matched part by part. Whenever a strict match failed, the surrounding passage was extracted and compared by eye.
- An independent source is one not cited for that claim. Each was downloaded and confirmed the same way.
- **Implementation check.** The lesson's own backend was run locally with the cached `Qdrant/bge-small-en-v1.5-onnx-Q` build. The run used `HF_HUB_OFFLINE=1` and made no network or paid calls. It covered all four presets, all three challenges in their broken and fixed states, the anisotropy statistics, and the existing tests (`tests/test_embed.py` and `tests/test_embed_ablation.py`: 25 passed).

## Summary

| Verdict | Count |
|---|---|
| confirmed | 11 |
| confirmed_with_changes | 11 |
| disputed | 2 |
| unverifiable | 0 |

All 47 excerpts were found in their cited sources. **No excerpt is fabricated.** The match results were:

- **31 strict.**
- **11 loose.** The differences were ligatures, PDF hyphenation and Markdown.
- **4 squash only.** These were PDF spacing ("wordQueen", "( MEAN- strategy)", "Av- eraging") and Markdown bold with a stray space ("are **incompatible** .").
- **1 matched only on rendered text.** The BGE "retromae" excerpt matches once the Markdown link `[retromae](https://github.com/staoxiao/RetroMAE)` is rendered.

The only real wording difference is in the BERT excerpt. It reads "(Wu et al. 2016)" where the source has "(Wu et al., 2016)". **Four locators are wrong**:

- word2vec-analogy says §5; the passage is in §1.1.
- scores-uncalibrated (Ethayarajh) says abstract; the passage is in §1.
- projection-lossy (second excerpt) says §2; the passage is in §1.
- contrastive-training (SimCSE) says §1; the passage is in §2.

### Most important problems, in priority order

1. **`pooling-strategies` is disputed.** The claim says Sentence-BERT "found the choice mattered little once the model was trained for it". That holds only for the NLI classification objective. In the same §6 the paper says: "When trained with the regression objective function, we observe that the pooling strategy has a large impact." Table 6 has MAX at 69.92 against MEAN at 87.44 on STSb. The excerpt "the pooling strategy has a rather minor impact" is cut from a sentence that begins "When trained with the classification objective function on NLI data,".
2. **`word2vec-analogy` is disputed as cited.**
   - The locator is wrong (§1.1, not §5).
   - The word2vec paper does not report King − Man + Woman ≈ Queen as its own result. It writes "it was shown for example that … [20]", which cites Mikolov, Yih & Zweig 2013. That paper used vectors "learned by a recurrent neural network language model", not word2vec. The word2vec paper's own §5 example is "Paris - France + Italy = Rome".
   - The claim also leaves out a necessary condition: the input words are excluded from the search. word2vec §4.1 says "we discard the input question words during this search", and Jurafsky & Martin (SLP3 ch. 5) say the nearest vector "is usually not in fact b* but one of the 3 input words".
3. **`models-not-comparable` is stated too absolutely.** Voyage's own docs say "All embeddings created with the 4 series are compatible with each other." Some providers deliberately ship model families that share one space, so the claim needs a qualifier.
4. **`scores-uncalibrated` cites a BGE v1 statement as if it applied to v1.5.** The quote "a similarity score greater than 0.5 does not indicate…" comes from a FAQ entry that opens "Suggest to use bge v1.5, which alleviates the issue of the similarity distribution". It explains that "the current BGE model" (v1) sits in "[0.6, 1]". The Ethayarajh excerpt is about contextual **word** representations, not sentence embeddings, and it comes from §1, not the abstract. The claim text itself still holds: on this lesson's v1.5 build, cross-topic cosine averages 0.411 (min 0.221). The excerpts need re-scoping.
5. **BGE query-instruction wording.**
   - The claim says the instruction goes "never to the passages", and the tour says "Passages never do." The card says "the documents/passages do not need to add the instruction" and "In all cases, **no instruction** needs to be added to passages." "Do not need" is softer than "never".
   - The `short-query` challenge explanation says "BGE was trained with an instruction on the query side for retrieval". The BGE model card does not say this. The C-Pack paper does: "a task specific instruction … is attached to the query side". Cite C-Pack (arXiv 2309.07597) or rephrase.
6. **`input-limits`: the Gemini half is over-generalised.** The sentence "The system silently truncates inputs that exceed this limit" sits in the **PDF-input section for gemini-embedding-2** ("Your inputs must fit within the model's 8,192 token limit (shared across all modalities)."). gemini-embedding-001 has a 2,048-token limit, and the page says nothing about truncation for it.
7. **`raw-bert-poor` is true only on average.** In SBERT Table 1, averaged BERT beats averaged GloVe on SICK-R (58.40 vs 53.76). The claim's "on the sentence-similarity benchmarks … both scored below" needs "on average". The sentence that actually supports the GloVe comparison ("Both are worse than computing average GloVe embeddings.") is not excerpted.
8. **`query-document-asymmetry`: the Gemini excerpt shows no asymmetry.** It only says `task_type` is unavailable on gemini-embedding-2. The asymmetry is in "Use RETRIEVAL_QUERY for queries; RETRIEVAL_DOCUMENT for documents to be retrieved." gemini-embedding-2 does it with different prefixes for queries and documents.
9. **Implementation disclosure.** The lesson calls the build "Qdrant's ONNX export". Qdrant's own model card calls it a "Quantized ONNX port", and its `ort_config.json` shows `"fp16": true` with GELU approximation. The `short-query` challenge passes by a thin margin on this build: bus 0.5146 against desk 0.5017. It has not been measured against BAAI's original weights.
10. **Smaller fixes.**
    - `mteb-no-winner`: the figures describe the 2022 paper; MTEB has since expanded to MMTEB, with over 500 tasks.
    - `projection-lossy`: "always loses information" is too strong, and one locator is wrong.
    - `embedding-uses`: both excerpts are list headers only.
    - `wordpiece-subwords`: missing comma in the excerpt, and no support for the claim that rare words get split.
    - `synonym-blind` brief: "Nothing in the library shares a word" is literally false for "a" and "to". It is true after stopword removal.

---

## Per-claim results

### semantic-similarity — confirmed
- **Excerpt check.** openai_embeddings: strict. Preceded by "The distance between two vectors measures their relatedness." mikolov2013word2vec: loose (PDF hyphenation). In §1.1 the sentence is framed as an expectation, citing [20]: "with the expectation that not only will similar words tend to be close to each other, but that words can have multiple degrees of similarity [20]".
- **Independent source.** Google ML Crash Course, *Embedding space* https://developers.google.com/machine-learning/crash-course/embeddings/embedding-space — "The distance between points in an embedding space represents the relative similarity between the corresponding items."
- **Implementation.** Confirmed. "a place to put my books" ranks the bookshelf first (0.6954) with the neural model.

### word2vec-static — confirmed
- **Excerpt check.** The Mikolov abstract excerpt is strict on the abs page. The Ethayarajh §1 excerpt is loose (PDF spacing). Full sentence: "Traditionally, these word embeddings were static: each word had a single vector, regardless of context (Mikolov et al., 2013a; Pennington et al., 2014)." It goes on: "all senses of a polysemous word had to share the same representation."
- **Independent source.** Jurafsky & Martin, SLP3 ch. 5 (draft of Aug 19, 2026) https://web.stanford.edu/~jurafsky/slp3/5.pdf — "Word2vec embeddings are static embeddings, meaning that the method learns one fixed embedding for each word in the vocabulary." In the PDF text a margin note interrupts this sentence.

### word2vec-analogy — disputed (attribution, locator, missing condition)
- **Excerpt check.** Squash match only, because the PDF reads "wordQueen". The passage is in **§1.1 "Goals of the Paper"**, not §5. The full sentence is: 'Using a word offset technique where simple algebraic operations are performed on the word vectors, it was shown for example that vector("King") - vector("Man") + vector("Woman") results in a vector that is closest to the vector representation of the word Queen [20].' (In the source the quotes are curly.)
- **Claim vs source.**
  - [20] is Mikolov, Yih & Zweig (NAACL 2013), and its vectors came from an RNN language model. The word2vec paper presents this as earlier work that it set out to improve on ("In this paper, we try to maximize accuracy of these vector operations by developing new model architectures").
  - The word2vec paper's own §5 example is "Paris - France + Italy = Rome". Table 8 also shows misses, such as "big - bigger small: larger" and "Einstein - scientist … Mozart: violinist", which supports "captured some relationships".
  - The method only works if the input words are excluded. §4.1 says "(we discard the input question words during this search)".
- **Independent sources.**
  - Mikolov, Yih & Zweig 2013 https://aclanthology.org/N13-1090.pdf — '"King - Man + Woman" results in a vector very close to "Queen."' and "The word representations we study are learned by a recurrent neural network language model".
  - SLP3 ch. 5 https://web.stanford.edu/~jurafsky/slp3/5.pdf — "the closest value returned by the parallelogram algorithm in word2vec or GloVe embedding spaces is usually not in fact b* but one of the 3 input words". In the PDF, "paral-lelogram" is hyphenated and a page header interrupts the passage.
- **Fix.** "Word vectors of this era captured some relationships through arithmetic: king − man + woman lands nearest to queen, provided the three input words are excluded from the search. The word2vec paper's own example is Paris − France + Italy ≈ Rome."
- **Excerpt fixes.** Change the locator to §1.1. Add a §5 excerpt: "Thus for example, Paris - France + Italy = Rome". Add a §4.1 excerpt: "we discard the input question words during this search".

### contextual-vectors — confirmed
- **Excerpt check.** Strict on the abs page. The full sentence includes a qualifier: "In all layers of ELMo, BERT, and GPT-2, on average, less than 5% of the variance in a word's contextualized representations can be explained by a static embedding for that word".
- **Independent source.** Peters et al., ELMo https://arxiv.org/abs/1802.05365 — "how these uses vary across linguistic contexts (i.e., to model polysemy)". SLP3 ch. 5: "contextual embeddings like the popular family of BERT representations, in which the vector for each word is different in different contexts."
- **Implementation.** `test_the_same_word_gets_different_vectors_in_different_contexts` passes.

### wordpiece-subwords — confirmed_with_changes (excerpt)
- **Excerpt check.** Devlin is a squash match only. **The excerpt drops a comma**: the source reads "We use WordPiece embeddings (Wu et al., 2016) with a 30,000 token vocabulary." The BGE `config.json` excerpt is strict. `tokenizer_config.json` confirms `"tokenizer_class": "BertTokenizer"` and `"do_lower_case": true`.
- **Missing support.** No excerpt supports "Rare words are split into smaller pieces". BERT's Figure 2 input example has "[CLS] he likes play ##ing [SEP]".
- **Independent source.** HF `google-bert/bert-base-uncased` config.json — `"vocab_size": 30522`. This shows that the paper's "30,000" is a rounded figure. The Qdrant ONNX build's config.json (commit aa8f8b0) also lists `"vocab_size": 30522`, and the running tokenizer reports 30,522.
- **Implementation.** "Embeddings are unbelievably useful" tokenizes as `em ##bed ##ding ##s are un ##bel ##ie ##va ##bly useful`.
- **Excerpt fix.** "We use WordPiece embeddings (Wu et al., 2016) with a 30,000 token vocabulary". Optionally add the Figure 2 example "he likes play ##ing".

### bert-cls-token — confirmed
- **Excerpt check.** Both loose (ligatures). The first is in §3. The second is **footnote 6**: "The vector C is not a meaningful sentence representation without fine-tuning, since it was trained with NSP."
- **Independent source.** SBERT §4.1 (not cited for this claim) https://arxiv.org/pdf/1908.10084v1 — "using the CLS-token output only achieves an average correlation of 29.19".

### raw-bert-poor — confirmed_with_changes (average only)
- **Excerpt check.** Squash only (PDF hyphenation "Av- eraging"). §4.1 is correct. The next sentence, which carries the GloVe comparison, is not excerpted: "Both are worse than computing average GloVe embeddings."
- **Claim vs source.** Table 1 averages over 7 datasets are GloVe 61.32, averaged BERT 54.81 and [CLS] 29.19. Per dataset, **averaged BERT beats GloVe on SICK-R (58.40 vs 53.76)**, so "on the sentence-similarity benchmarks … both scored below" holds only on average.
- **Independent source.** SimCSE Table 1 (not cited for this claim) https://arxiv.org/pdf/2104.08821v4 — "GloVe embeddings (avg.)" 61.32 against "BERTbase (first-last avg.)" 56.70.
- **Fix.** "Without training for similarity, averaged BERT outputs and the [CLS] vector made poor sentence embeddings. Averaged over the seven sentence-similarity benchmarks in the SBERT paper, both scored below simple averaged GloVe word vectors."
- **Excerpt fix.** Add "Both are worse than computing average GloVe embeddings."

### pooling-strategies — disputed
- **Excerpt check.** The §3 excerpt is squash only: the source has "( MEAN- strategy)", and the sentence goes on "(MAX-strategy). The default configuration is MEAN." The §6 excerpt is loose, but it is **cut from a qualified sentence**: "When trained with the classification objective function on NLI data, the pooling strategy has a rather minor impact."
- **Contradiction.** The same section goes on: "When trained with the regression objective function, we observe that the pooling strategy has a large impact. There, the MAX strategy perform significantly worse than MEAN or CLS-token strategy." Table 6 (STSb): MEAN 87.44, MAX 69.92, CLS 86.62. On NLI: 80.78, 79.07 and 79.80.
- **Independent source.** SimCSE Table 6, "Ablation studies of different pooling methods in unsupervised and supervised SimCSE". [CLS] variants and first-last average fall within 80.9–82.5 (unsupervised) and 85.8–86.2 (supervised). For contrastive training this supports "little difference between CLS and mean".
- **Fix.** "Sentence-BERT compared three ways to pool token vectors into one sentence vector: the [CLS] token, the mean, and the max. With NLI classification training the choice mattered little. With regression training, max pooling did much worse than mean or [CLS]."
- **Excerpt fix.** Lengthen the §6 excerpt to "When trained with the classification objective function on NLI data, the pooling strategy has a rather minor impact." Add "When trained with the regression objective function, we observe that the pooling strategy has a large impact."

### contrastive-training — confirmed_with_changes (locator, excerpt form)
- **Excerpt check.** The SimCSE excerpt is loose, but it sits in **§2 "Background: Contrastive Learning"**, not §1. The full sentence: "Contrastive learning aims to learn effective representation by pulling semantically close neighbors together and pushing apart non-neighbors (Hadsell et al., 2006)." The BGE excerpt matches the rendered README. The raw Markdown is "using [retromae](https://github.com/staoxiao/RetroMAE) and train them", which is why the raw string match fails.
- **Independent source.** C-Pack (the BGE paper) https://arxiv.org/abs/2309.07597, PDF v5 — "Our training recipe has three main components: 1) pre-training with plain texts, 2) contrastive learning with C-MTP (unlabeled), and 3) multi-task learning with C-MTP (labeled)."
- **Notes.** "Typically" is fair. C-Pack shows BGE also used instruction-based multi-task fine-tuning (see bge-query-instruction).
- **Excerpt fix.** Change the gao2021simcse locator to §2.

### bge-dims — confirmed
- **Excerpt check.** Strict (pinned config.json). `"architectures": ["BertModel"]`, `"num_attention_heads": 12`.
- **Independent source.** fastembed registry (not cited for this claim), `onnx_embedding.py` @ de502ca — `model="BAAI/bge-small-en-v1.5", dim=384`. The Qdrant ONNX build's config.json has `"hidden_size": 384` and `"num_hidden_layers": 12`.
- **Implementation.** `test_vectors_are_384_dimensional` passes.

### bge-max-tokens — confirmed
- **Excerpt check.** The sentence_bert_config excerpt is strict. The sbert_computing excerpt is loose (backticks). Context: "A common value for BERT-based models are 512 tokens, which corresponds to about 300-400 words (for English)."
- **Independent source.** fastembed registry entry for bge-small-en-v1.5 — "Text embeddings, Unimodal (text), English, 512 input tokens truncation". The pinned config.json has `"max_position_embeddings": 512`.
- **Implementation.** The unit test truncates 900 words to 512 ids, with [SEP] last. **Note, however:** the API caps `text` at 300 characters (`EmbedParams.text max_length=300`), so a learner can never trigger truncation from the UI. See the implementation section.

### bge-cls-normalized — confirmed
- **Excerpt check.** All three match: the pooling config (loose, because of JSON whitespace), modules.json (strict) and fastembed (strict, both parts). fastembed: `processed_embeddings = embeddings[:, 0]` … `return normalize(processed_embeddings)`, and the registry maps bge-small-en-v1.5 to `sources=ModelSource(hf="Qdrant/bge-small-en-v1.5-onnx-Q")`.
- **Independent source.** The BGE README usage code (same publisher, different section): "# Perform pooling. In this case, cls pooling. sentence_embeddings = model_output[0][:, 0]" followed by an L2 normalize. Locally, `test_hand_built_stages_reproduce_fastembed` passes (cosine ≈ 1 to 1e-5).
- **Notes.** The claim is accurate. The build-disclosure issue ("quantized"/fp16) is covered under implementation mismatches.

### bge-query-instruction — confirmed_with_changes ("never" overstated)
- **Excerpt check.** Both strict. Full FAQ passage: "For the `bge-*-v1.5`, we improve its retrieval ability when not using instruction. No instruction only has a slight degradation in retrieval performance compared with using instruction. … For a retrieval task that uses short queries to find long related documents, it is recommended to add instructions for these short queries. **The best method to decide whether to add instructions for queries is choosing the setting that achieves better performance on your task.** In all cases, the documents/passages do not need to add the instruction."
- **Claim vs source.** "Slight cost" accurately reflects "slight degradation", and the statement is specific to v1.5. "Never to the passages" is stronger than "do not need". The card also tells readers to decide by testing on their own task.
- **Independent source.** C-Pack §3 (PDF v5) https://arxiv.org/abs/2309.07597 — "we leverage instruction-based fine-tuning [7, 50], where the input is differentiated to help the model accommodate different tasks." It adds that a task-specific instruction "is attached to the query side". This describes the BGE (v1) recipe.
- **Implementation.** The instruction is prepended (test passes). For "getting to the office" it changes the top-1 result from the desk (0.5876) to the bus (0.5146). It does not change the top-1 for the other three presets.
- **Fix.** "For short retrieval queries, BGE recommends adding an instruction to the query ('Represent this sentence for searching relevant passages:'); passages don't need it. For v1.5, leaving it out costs only slightly, so test both on your own task."

### query-document-asymmetry — confirmed_with_changes (Gemini excerpt)
- **Excerpt check.** anthropic_embeddings: strict. Context: "When using the input_type parameter, special prompts are prepended to the input text prior to embedding." For a query: "Represent the query for retrieving supporting documents: ". gemini_embeddings: loose (backticks). It continues: "Instead, include the task as an instruction in your prompt".
- **Claim vs source.** The Gemini excerpt only says that `task_type` is unavailable on gemini-embedding-2. **It does not show** that Gemini embeds queries and documents differently. The same page does: "Use RETRIEVAL_QUERY for queries; RETRIEVAL_DOCUMENT for documents to be retrieved." For gemini-embedding-2 it says: "In asymmetric use cases, add the task prefix to the query and apply the document structure for the content you want to embed and retrieve." Query and document use different formats, "task: search result | query: {content}" against "title: {title} | text: {content}". The Voyage half rests on Anthropic's page, which is a secondary source.
- **Independent source.** Voyage docs https://docs.voyageai.com/docs/embeddings — 'For query, the prompt is " Represent the query for retrieving supporting documents: ".' The same page notes: "Embeddings generated with and without the input_type argument are compatible."
- **Fix.** "Some providers embed queries and documents differently. Voyage prepends different prompts depending on input_type. Gemini's gemini-embedding-001 takes a task_type (RETRIEVAL_QUERY or RETRIEVAL_DOCUMENT); gemini-embedding-2 drops task_type and uses different prefixes for queries and documents instead."
- **Excerpt fix.** Add the gemini_embeddings excerpt "Use RETRIEVAL_QUERY for queries; RETRIEVAL_DOCUMENT for documents to be retrieved."

### unit-vector-metrics — confirmed
- **Excerpt check.** Both strict. The IR-book sentence goes on: "This measure is the cosine of the angle between the two vectors". The OpenAI passage is prefaced "OpenAI embeddings are normalized to length 1, which means that:".
- **Independent source.** Anthropic *Embeddings* page (not cited for this claim) — "Cosine similarity and Euclidean distance result in identical rankings."
- **Implementation.** `test_cosine_dot_and_euclidean_agree_on_unit_vectors` passes. Euclidean distance is returned negated, so higher means closer.

### scores-uncalibrated — confirmed_with_changes (excerpt scope, locator)
- **Excerpt check.**
  - **Ethayarajh.** Loose, but the passage is in **§1** (the list of findings), not the abstract. The abstract has only "not isotropic in any layer". The full §1 sentence is about **contextualized word representations** of ELMo, BERT and GPT-2: "In all layers of all three models, the contextualized word representations of all words are not isotropic: … Instead, they are anisotropic, occupying a narrow cone in the vector space."
  - **BGE.** Both quotes are strict, but they come from FAQ item 2, "The similarity score between two dissimilar sentences is higher than 0.5". That item opens "**Suggest to use bge v1.5, which alleviates the issue of the similarity distribution.** Since we finetune the models by contrastive learning with a temperature of 0.01, the similarity distribution of the current BGE model is about in the interval [0.6, 1]. So a similarity score greater than 0.5 does not indicate…" In other words, the ">0.5" sentence describes the **v1** distribution. The "relative order" sentence and the advice to set thresholds on your own data apply generally.
- **Independent source.** SimCSE §5 https://arxiv.org/pdf/2104.08821v4 — "the learned embeddings occupy a narrow cone in the vector space, which severely limits their expressiveness". SimCSE also shows that contrastive training reduces anisotropy, so for contrastively trained models the effect is weaker but not gone.
- **Implementation.** Measured on this build with CLS pooling: the 216 cross-topic pairs have mean cosine 0.411, min 0.221 and max 0.584; same-topic pairs average 0.490. Random 384-D directions average about 0. This supports "well above zero" and the technical note's "~0.41".
- **Excerpt fixes.** Change the Ethayarajh locator to §1. Replace the BGE ">0.5" excerpt with, or precede it by, "Suggest to use bge v1.5, which alleviates the issue of the similarity distribution." Keep "what matters is the relative order of the scores, not the absolute value." Optionally add the SimCSE §5 excerpt for sentence-level anisotropy.
- **Claim text.** It can stay. Optionally replace "Embeddings tend to occupy" with "Transformer representations tend to occupy".

### lexical-vs-neural — confirmed
- **Excerpt check.** Both strict.
- **Independent source.** IR book ch. 9 https://nlp.stanford.edu/IR-book/html/htmledition/relevance-feedback-and-query-expansion-1.html — "This issue, known as synonymy , has an impact on the recall of most information retrieval systems."
- **Notes.** "Keyword matching only finds shared words" ignores stemming and synonym expansion. The lesson's own lexical embedder applies an S-stemmer, so "books" becomes "book". The claim's "can match" is suitably hedged.
- **Implementation.** The lexical/lexical run on "a place to put my books" scores every item 0.0. Neural ranks the bookshelf first.

### models-not-comparable — confirmed_with_changes (absolute wording)
- **Excerpt check.** Gemini "incompatible" is a squash match (Markdown bold, and the rendered text is "are incompatible ."). The other two match (loose and strict). The Gemini page continues: "This means you cannot directly compare embeddings generated by one model with embeddings generated by the other."
- **Counterexample.** Voyage docs https://docs.voyageai.com/docs/embeddings — "All embeddings created with the 4 series are compatible with each other." So "cannot be compared" is not universal. Some providers deliberately train a model family into one shared space.
- **Independent source.** Microsoft Azure OpenAI models https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models — "You can't upgrade between embedding models. To move from text-embedding-ada-002 to text-embedding-3-large , you need to generate new embeddings."
- **Implementation.** The lexical/neural mix is refused: `comparable=False`, 1024-D against 384-D.
- **Fix.** "Vectors from different embedding models generally live in different spaces and cannot be compared, unless the provider says a model family shares one space (Voyage's 4 series does). Switching to an incompatible model means re-embedding everything."

### projection-lossy — confirmed_with_changes (wording, locator)
- **Excerpt check.** Both loose. The §6.2 excerpt is right. **The second excerpt is in §1 (Introduction), not §2.** Full sentence: "Traditional dimensionality reduction techniques such as Principal Components Analysis (PCA; Hotelling, 1933) and classical multidimensional scaling (MDS; Torgerson, 1952) are linear techniques that focus on keeping the low-dimensional representations of dissimilar datapoints far apart."
- **Claim vs source.** "Always loses information" is stronger than "impossible to fully represent the structure of **intrinsically** high-dimensional data". Data lying in a low-dimensional subspace loses nothing. Neither excerpt says PCA "keeps the directions of greatest spread".
- **Independent source.** scikit-learn PCA docs https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html — "Principal axes in feature space, representing the directions of maximum variance in the data."
- **Implementation.** The PCA via SVD keeps 27.07% of the library variance (CLS). `test_3d_projection_loses_information` passes.
- **Fix.** "Drawing high-dimensional vectors in 2D or 3D generally loses information. PCA keeps the directions of greatest spread, so nearby points in the picture are only a hint."
- **Excerpt fix.** Change the second locator to §1.

### tsne-cautions — confirmed
- **Excerpt check.** Both strict. They are the conclusions of sections "2. Cluster sizes in a t-SNE plot mean nothing" and "3. Distances between clusters might not mean anything".
- **Independent source.** scikit-learn manifold guide https://scikit-learn.org/stable/modules/manifold.html — "Global structure is not explicitly preserved."

### shorter-dimensions — confirmed
- **Excerpt check.** Both strict. MRL is at v4 (abs and PDF).
- **Supporting excerpt (optional).** OpenAI guide: "Both of our new embedding models were trained with a technique that allows developers to trade-off performance and cost of using embeddings." The OpenAI API reference says `dimensions` is "Only supported in text-embedding-3 and later models."
- **Independent source.** Gemini embeddings page (not cited for this claim) — "If you are using gemini-embedding-001 , you must manually normalize non-3072 dimensions". Sentence Transformers Matryoshka docs: "proposes a solution to train embedding models whose embeddings are still useful after truncation to much smaller sizes."

### mteb-no-winner — confirmed_with_changes (currency)
- **Excerpt check.** Both strict on the abs page, and loose in the v3 PDF. The abstract adds: "Through the benchmarking of 33 models on MTEB".
- **Currency.** These figures describe the 2022 paper. MTEB has since grown. MMTEB https://arxiv.org/abs/2502.13595 — "covering over 500 quality-controlled evaluation tasks across 250+ languages". The present-tense label "On the MTEB benchmark (8 task types, 58 datasets, 112 languages)" now reads as describing the current benchmark.
- **Independent source.** MMTEB (above). Separately, the OpenAI guide's table shows models with different MTEB averages (62.3% / 64.6% / 61.0%). That is consistent with the claim but not a direct confirmation.
- **Fix.** "In the original MTEB paper (2022: 8 task types, 58 datasets, 112 languages, 33 models), no single embedding model was best at every task, so choose by your own task."

### embedding-uses — confirmed_with_changes (excerpts are headers only)
- **Excerpt check.** Both strict, but both are only lead-ins to lists ("Embeddings are commonly used for:"). The OpenAI list is: Search, Clustering, Recommendations, Anomaly detection, Diversity measurement, Classification. The Gemini list puts first: "Retrieval-Augmented Generation (RAG): Embeddings enhance the quality of generated text by retrieving and incorporating relevant information into the context of a model."
- **Claim vs source.** "One of the most common uses" is a mild overstatement. Gemini lists RAG as a "common AI use case", but neither source ranks the uses.
- **Independent source.** Google ML Crash Course, embedding-space page (not cited for this claim) — "Embeddings place similar items closer together in the embedding space, allowing for efficient machine learning on large datasets."
- **Fix.** "Embeddings are used for search, clustering, recommendations, anomaly detection and classification. Retrieval for RAG (Lesson 01) is a common use."
- **Excerpt fixes.** Replace the openai_embeddings excerpt with "Search (where results are ranked by relevance to a query string)". Replace the gemini_embeddings excerpt with "Retrieval-Augmented Generation (RAG): Embeddings enhance the quality of generated text by retrieving and incorporating relevant information".

### input-limits — confirmed_with_changes (Gemini scope)
- **Excerpt check.** Both strict.
  - OpenAI context: "…(8192 tokens for all embedding models), cannot be an empty string, and any array must be 2048 dimensions or less." It adds: "all embedding models enforce a maximum of 300,000 tokens summed across all inputs in a single request."
  - Gemini context (the **PDF** section for gemini-embedding-2): "Your inputs must fit within the model's 8,192 token limit (shared across all modalities). The system silently truncates inputs that exceed this limit."
- **Claim vs source.** The Gemini statement is documented for gemini-embedding-2. gemini-embedding-001 has "Input token limit 2,048", and the page says nothing about its truncation behaviour.
- **Independent sources.**
  - Vertex AI text-embeddings API https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api — autoTruncate: "When set to false, an error is returned if the input text is longer than the maximum length supported by the model. Defaults to true." This covers Vertex rather than the Gemini Developer API.
  - Voyage docs — "truncation (bool, optional, defaults to True )".
  - Azure OpenAI models table — "text-embedding-3-large 8,192 3,072 … text-embedding-3-small 8,192 1,536".
- **Fix.** "Hosted models have input limits too. OpenAI's embedding models take up to 8,192 tokens per input. Google documents that gemini-embedding-2 (8,192 tokens) silently truncates longer inputs."

---

## Implementation / lesson-text mismatches

Every run below used the local cached build `Qdrant/bge-small-en-v1.5-onnx-Q` (snapshot aa8f8b0) with fastembed 0.9.0.

1. **The build is not plainly "Qdrant's ONNX export".**
   - **Where.** The `experiment` visual reads "bge-small-en-v1.5 (Qdrant's ONNX export, via fastembed)", and `bge-cls-normalized` says "Qdrant's ONNX export of the model". `MODEL_BUILD` uses the same wording.
   - **What Qdrant says.** Its model card (https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q) says "Quantized ONNX port of BAAI/bge-small-en-v1.5". Its `ort_config.json` shows `"fp16": true`, `"enable_gelu_approximation": true` and `"quantization": {}`.
   - **Inconsistency.** The `model.py` docstring already makes this caveat, but the learner-facing text does not.
   - **Suggested visual description.** "bge-small-en-v1.5 (Qdrant's reduced-precision ONNX port, via fastembed) runs locally, stage by stage, on your text. Scores may differ slightly from BAAI's original weights."
2. **The `short-query` challenge passes by a thin margin.**
   - **Results.** Broken: desk (furniture-5) 0.5876, then bus 0.5611. Fixed with the instruction: bus (vehicles-5) 0.5146, desk 0.5017. The margin is 0.013.
   - **Brief and explanation.** The brief ("the top match is a desk") is accurate, and the explanation's "tendency, not a guarantee" is appropriately hedged.
   - **Lock-down.** No unlocked parameter (`normalize`, `top_k`) can pass it any other way. Mean pooling is locked, and it would still rank the desk first.
   - **Risk.** Given the margin and the reduced-precision build, a model or runtime change could flip the result. Add a regression test that asserts this challenge passes, since none exists today.
   - **Attribution.** "BGE was trained with an instruction on the query side for retrieval" is not in the model card. Cite C-Pack ("a task specific instruction … is attached to the query side"), or rephrase as "BGE recommends an instruction on the query side for short retrieval queries."
3. **The `synonym-blind` brief is literally false.** "Nothing in the library shares a word with this question" does not hold for "a" and "to", which appear in many sentences, for example "He rides his bicycle to work". It is true only after the lexical embedder drops stopwords (`STOPWORDS` in `rag/text.py`) and S-stems "books" to "book".
   - Suggested: "No library sentence shares a content word with this question, so the search finds nothing useful."
   - The run confirms all lexical scores are 0.0, so the check (`score > 0`) correctly fails.
4. **Learners can never see truncation.** `tokenizer.detail` ("anything past 512 tokens is cut off") and the tour ("a 512-token limit") are true of the model. However, `EmbedParams.text` has `max_length=300` characters, so the UI can never trigger truncation, and `query.truncated` is always false. The `bge-max-tokens` technical note ("A 900-word input is cut to 512 tokens") is verified only by the unit test. Either say "(not reachable in this experiment's 300-character box)", or show the unit-test result.
5. **The "Where it goes wrong" preset has no explanation.** For "a vehicle that runs on rails", the train sentence ranks **14th of 24** (0.4882). The top hits are the truck (0.6191) and the horse (0.6125). With the instruction the train ranks 10th; with mean pooling the top-1 becomes the horse (animals-5). Nothing in lesson.yaml says what goes wrong, so the frontend should explain it, for example: "embeddings match the topic of vehicles but miss that only trains run on rails."
6. **The normalizer ablation silently changes the metric.** `ablation.py` uses `metric = "dot" if params.metric != "cosine" else "cosine"`. With Euclidean selected and the normalizer removed, the ablated side shows dot scores, not distances. `breaks_if_removed` talks only about dot-product scores, so this is acceptable. Pass 3 should check that the UI labels the metric actually used.
7. **The component and tour text below matches the implementation.**
   - library: 24 sentences in 4 topics (`corpus.py`).
   - encoder: 12 layers, 384-D.
   - pooling: CLS by default; mean averages every token, including [CLS] and [SEP], as Sentence Transformers does.
   - normalizer: cosine is unaffected because `score()` normalises for cosine.
   - similarity: removing it returns stored order.
   - semantic_space: removing it leaves the neighbours unchanged, and PCA explains 27% of the variance.
   - mixed-models: 1024-D lexical against 384-D neural, matching "don't even have the same number of dimensions".
   - The `breaks_if_removed` statements all match `ablation.py`, and their tests pass.
8. **Tour wording.**
   - `your_text`: "Passages never do." should read "Passages don't need one." (see bge-query-instruction).
   - `normalizer`: "After this, dot product and cosine are the same thing" is fine.
   - `pooling.detail`: "Averaging every token is the other common choice" is supported, since SBERT's "default configuration is MEAN".
9. **sources.yaml housekeeping.**
   - `reimers2019sbert.version` says "arXiv abstract page", but the excerpts come from the body (§3, §4.1, §6). It should name the v1 PDF.
   - Add `cpack2023` (https://arxiv.org/abs/2309.07597) for the query-side instruction training.
   - Consider adding `voyage_embeddings` (https://docs.voyageai.com/docs/embeddings) so the Voyage claims rest on Voyage's own docs.
   - Consider adding `slp3_ch5` for the analogy caveat.

---

## Machine-readable results

```yaml
pass2:
  date: 2026-10-19
  results:
    - claim: semantic-similarity
      verdict: confirmed
      independent_sources: [https://developers.google.com/machine-learning/crash-course/embeddings/embedding-space]
      fix: null
      excerpt_fixes: []
    - claim: word2vec-static
      verdict: confirmed
      independent_sources: [https://web.stanford.edu/~jurafsky/slp3/5.pdf]
      fix: null
      excerpt_fixes: []
    - claim: word2vec-analogy
      verdict: disputed
      independent_sources: [https://aclanthology.org/N13-1090.pdf, https://web.stanford.edu/~jurafsky/slp3/5.pdf]
      fix: "Word vectors of this era captured some relationships through arithmetic: king − man + woman lands nearest to queen, provided the three input words are excluded from the search. The word2vec paper's own example is Paris − France + Italy ≈ Rome."
      excerpt_fixes:
        - {source: mikolov2013word2vec, old_locator: "§5", new_locator: "§1.1"}
        - {source: mikolov2013word2vec, old: null, new: "Thus for example, Paris - France + Italy = Rome", locator: "§5"}
        - {source: mikolov2013word2vec, old: null, new: "we discard the input question words during this search", locator: "§4.1"}
    - claim: contextual-vectors
      verdict: confirmed
      independent_sources: [https://arxiv.org/abs/1802.05365, https://web.stanford.edu/~jurafsky/slp3/5.pdf]
      fix: null
      excerpt_fixes: []
    - claim: wordpiece-subwords
      verdict: confirmed_with_changes
      independent_sources: [https://huggingface.co/google-bert/bert-base-uncased/raw/main/config.json]
      fix: null
      excerpt_fixes:
        - {source: devlin2018bert, old: "We use WordPiece embeddings (Wu et al. 2016) with a 30,000 token vocabulary", new: "We use WordPiece embeddings (Wu et al., 2016) with a 30,000 token vocabulary"}
    - claim: bert-cls-token
      verdict: confirmed
      independent_sources: [https://arxiv.org/pdf/1908.10084v1]
      fix: null
      excerpt_fixes:
        - {source: devlin2018bert, old_locator: "footnote", new_locator: "§3.1, footnote 6"}
    - claim: raw-bert-poor
      verdict: confirmed_with_changes
      independent_sources: [https://arxiv.org/pdf/2104.08821v4]
      fix: "Without training for similarity, averaged BERT outputs and the [CLS] vector made poor sentence embeddings. Averaged over the seven sentence-similarity benchmarks in the SBERT paper, both scored below simple averaged GloVe word vectors."
      excerpt_fixes:
        - {source: reimers2019sbert, old: null, new: "Both are worse than computing average GloVe embeddings.", locator: "§4.1"}
    - claim: pooling-strategies
      verdict: disputed
      independent_sources: [https://arxiv.org/pdf/2104.08821v4]
      fix: "Sentence-BERT compared three ways to pool token vectors into one sentence vector: the [CLS] token, the mean, and the max. With NLI classification training the choice mattered little. With regression training, max pooling did much worse than mean or [CLS]."
      excerpt_fixes:
        - {source: reimers2019sbert, old: "the pooling strategy has a rather minor impact", new: "When trained with the classification objective function on NLI data, the pooling strategy has a rather minor impact."}
        - {source: reimers2019sbert, old: null, new: "When trained with the regression objective function, we observe that the pooling strategy has a large impact.", locator: "§6"}
    - claim: contrastive-training
      verdict: confirmed_with_changes
      independent_sources: [https://arxiv.org/abs/2309.07597]
      fix: null
      excerpt_fixes:
        - {source: gao2021simcse, old_locator: "§1", new_locator: "§2"}
    - claim: bge-dims
      verdict: confirmed
      independent_sources: [https://github.com/qdrant/fastembed/blob/de502ca83baa2b81922cb5a46acf689f5e2c72a1/fastembed/text/onnx_embedding.py]
      fix: null
      excerpt_fixes: []
    - claim: bge-max-tokens
      verdict: confirmed
      independent_sources: [https://github.com/qdrant/fastembed/blob/de502ca83baa2b81922cb5a46acf689f5e2c72a1/fastembed/text/onnx_embedding.py]
      fix: null
      excerpt_fixes: []
    - claim: bge-cls-normalized
      verdict: confirmed
      independent_sources: [local reproduction tests/test_embed.py (hand-built CLS+L2 equals fastembed output)]
      fix: null
      excerpt_fixes: []
    - claim: bge-query-instruction
      verdict: confirmed_with_changes
      independent_sources: [https://arxiv.org/abs/2309.07597]
      fix: "For short retrieval queries, BGE recommends adding an instruction to the query ('Represent this sentence for searching relevant passages:'); passages don't need it. For v1.5, leaving it out costs only slightly, so test both on your own task."
      excerpt_fixes:
        - {source: bge_model_card, old: null, new: "In all cases, the documents/passages do not need to add the instruction."}
    - claim: query-document-asymmetry
      verdict: confirmed_with_changes
      independent_sources: [https://docs.voyageai.com/docs/embeddings]
      fix: "Some providers embed queries and documents differently. Voyage prepends different prompts depending on input_type. Gemini's gemini-embedding-001 takes a task_type (RETRIEVAL_QUERY or RETRIEVAL_DOCUMENT); gemini-embedding-2 drops task_type and uses different prefixes for queries and documents instead."
      excerpt_fixes:
        - {source: gemini_embeddings, old: null, new: "Use RETRIEVAL_QUERY for queries; RETRIEVAL_DOCUMENT for documents to be retrieved."}
    - claim: unit-vector-metrics
      verdict: confirmed
      independent_sources: [https://platform.claude.com/docs/en/build-with-claude/embeddings]
      fix: null
      excerpt_fixes: []
    - claim: scores-uncalibrated
      verdict: confirmed_with_changes
      independent_sources: [https://arxiv.org/pdf/2104.08821v4]
      fix: null
      excerpt_fixes:
        - {source: ethayarajh2019, old_locator: "abstract", new_locator: "§1"}
        - {source: bge_model_card, old: "a similarity score greater than 0.5 does not indicate that the two sentences are similar.", new: "Suggest to use bge v1.5, which alleviates the issue of the similarity distribution."}
    - claim: lexical-vs-neural
      verdict: confirmed
      independent_sources: [https://nlp.stanford.edu/IR-book/html/htmledition/relevance-feedback-and-query-expansion-1.html]
      fix: null
      excerpt_fixes: []
    - claim: models-not-comparable
      verdict: confirmed_with_changes
      independent_sources: [https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models, https://docs.voyageai.com/docs/embeddings]
      fix: "Vectors from different embedding models generally live in different spaces and cannot be compared, unless the provider says a model family shares one space (Voyage's 4 series does). Switching to an incompatible model means re-embedding everything."
      excerpt_fixes: []
    - claim: projection-lossy
      verdict: confirmed_with_changes
      independent_sources: [https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html]
      fix: "Drawing high-dimensional vectors in 2D or 3D generally loses information. PCA keeps the directions of greatest spread, so nearby points in the picture are only a hint."
      excerpt_fixes:
        - {source: vandermaaten2008tsne, excerpt: "linear techniques that focus on keeping the low-dimensional representations of dissimilar datapoints far apart", old_locator: "§2", new_locator: "§1"}
    - claim: tsne-cautions
      verdict: confirmed
      independent_sources: [https://scikit-learn.org/stable/modules/manifold.html]
      fix: null
      excerpt_fixes: []
    - claim: shorter-dimensions
      verdict: confirmed
      independent_sources: [https://ai.google.dev/gemini-api/docs/embeddings, https://sbert.net/examples/sentence_transformer/training/matryoshka/README.html]
      fix: null
      excerpt_fixes:
        - {source: openai_embeddings, old: null, new: "Both of our new embedding models were trained with a technique that allows developers to trade-off performance and cost of using embeddings.", optional: true}
    - claim: mteb-no-winner
      verdict: confirmed_with_changes
      independent_sources: [https://arxiv.org/abs/2502.13595]
      fix: "In the original MTEB paper (2022: 8 task types, 58 datasets, 112 languages, 33 models), no single embedding model was best at every task, so choose by your own task."
      excerpt_fixes: []
    - claim: embedding-uses
      verdict: confirmed_with_changes
      independent_sources: [https://developers.google.com/machine-learning/crash-course/embeddings/embedding-space]
      fix: "Embeddings are used for search, clustering, recommendations, anomaly detection and classification. Retrieval for RAG (Lesson 01) is a common use."
      excerpt_fixes:
        - {source: openai_embeddings, old: "Embeddings are commonly used for:", new: "Search (where results are ranked by relevance to a query string)"}
        - {source: gemini_embeddings, old: "Text embeddings are crucial for a variety of common AI use cases, such as:", new: "Retrieval-Augmented Generation (RAG): Embeddings enhance the quality of generated text by retrieving and incorporating relevant information"}
    - claim: input-limits
      verdict: confirmed_with_changes
      independent_sources: [https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api, https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models]
      fix: "Hosted models have input limits too. OpenAI's embedding models take up to 8,192 tokens per input. Google documents that gemini-embedding-2 (8,192 tokens) silently truncates longer inputs."
      excerpt_fixes:
        - {source: gemini_embeddings, old: null, new: "Your inputs must fit within the model's 8,192 token limit (shared across all modalities)."}
  text_fixes:
    - {where: "challenges.synonym-blind.brief", old: "Nothing in the library shares a word with this question", new: "No library sentence shares a content word with this question"}
    - {where: "challenges.short-query.explanation", old: "BGE was trained with an instruction on the query side for retrieval.", new: "BGE recommends an instruction on the query side for short retrieval queries (its training attached one to queries)."}
    - {where: "tour.your_text.body", old: "Passages never do.", new: "Passages don't need one."}
    - {where: "visuals.experiment.description", old: "bge-small-en-v1.5 (Qdrant's ONNX export, via fastembed)", new: "bge-small-en-v1.5 (Qdrant's reduced-precision ONNX port, via fastembed)"}
```

Notes on the YAML. `old: null` means "add this excerpt". `old_locator`/`new_locator` means "change only the locator". Excerpt text is copied from the downloaded source text. Curly quotes and PDF hyphenation are normalised, and nothing else is changed.
