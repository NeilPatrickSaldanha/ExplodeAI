# RAG pipeline — Pass 2 independent factual cross-check

Date: 2026-10-18. Inputs: `content/lessons/rag-pipeline/lesson.yaml` (32 claims, plus component, challenge and tour text) and `content/sources.yaml`.

## Method

- Every cited URL was downloaded directly (curl) and turned into plain text: HTML through BeautifulSoup, PDFs through pypdf, and arXiv abstracts through the arXiv export API and abs pages. Each excerpt was then matched as a string against that text, once strictly and once loosely (loose = ignoring Markdown backticks, PDF hyphenation and ligatures). No summarising fetch tool was used to confirm any excerpt. The one exception is the OpenAI embeddings blog, which returned 403 and so was not used.
- When a strict match failed, the passage around it was pulled out and compared by eye. The results are reported below.
- Independent sources are ones not cited for that claim. They were fetched and their excerpts confirmed the same way.

## Summary

| Verdict | Count |
|---|---|
| confirmed | 18 |
| confirmed_with_changes | 13 |
| disputed | 1 |
| unverifiable | 0 |

All 51 excerpts were found in their cited sources. Only formatting differs: Markdown backticks, math notation in PDFs, and in one case a period added where the source sentence carries on. **No excerpt is fabricated.**

### Most important problems, in priority order

1. **`dpr-beats-bm25` is disputed.** The claim says DPR beat BM25 "on the open-domain QA benchmarks it was tested on". That is false for SQuAD. In the DPR paper's own Table 2, BM25 scores 68.8 top-20 against 63.2 for single-dataset DPR, and §5.1 says "With the exception of SQuAD, DPR performs consistently better". The "9%–19%" figure in the abstract covers only the other four datasets. The abstract wording also differs by version: the arXiv abs page says "largely by", while the v3 PDF says "greatly by".
2. **`rag-small-kb` is out of date.** The 200,000-token figure comes from the September 2024 post and matched Claude's context window at that time. Anthropic's current context-windows page says most current Claude models have a 1M-token window and that "Other Claude models … have a 200k-token context window." The claim reads as standing, current guidance, so it needs a date.
3. **Implementation mismatch (not a claim, but serious).** The backend's default "dense" embedder is `tfidf-hashing-1024`, a *lexical* hashing embedder (`backend/app/experiments/rag/embedding.py`, default `"lexical-hashing"` in `pipeline.py`). Its own docstring says texts "that mean the same thing in different words do NOT" land close together. The lesson.yaml never says so. Yet the embedder component says "Nearby vectors should mean related text", the claim `lexical-misses-synonyms` says embedding models "are trained to catch" synonyms, and there is a "Synonym test" preset. With the default embedder, dense retrieval will *also* miss "money back" ↔ "refund". The docstring says "The lesson labels it as a stand-in", but no such label exists in lesson.yaml. Pass 3 should check this, and the lesson text should disclose it.
4. **`query_encoder.short` contradicts a claim.** "Encodes the question with the same model" conflicts with `dpr-dot-product`, which says "separate question and passage encodings". DPR and RAG use two separate BERT encoders (BERT_q and BERT_d) that map into one shared space.
5. **`ranking-miss` explanation overstates RRF.** "RRF keeps chunks that either ranker places highly" is not guaranteed. With k = 60, a chunk ranked 1st and 20th scores 1/61 + 1/80 ≈ 0.0289, which loses to a chunk ranked 5th in both lists (2/65 ≈ 0.0308). RRF favours agreement between rankers.
6. **`openai-chunk-defaults` names the wrong product surface.** The 800/400 defaults are for vector-store file chunking, documented in the Retrieval guide and API reference. The file search tool uses vector stores, but the cited page is not the file-search page. The API reference also says the auto strategy "currently" uses 800/400, so the default may change.
7. **Some excerpts don't support the half of the claim they are cited for.** This affects `flat-index-exact` (the HNSW excerpt does not mention approximation or speed), `rag-paper-architecture` (no excerpt mentions BART-large), `bm25-defaults` (the k1 default has no excerpt), `hybrid-contextual-results` (the 49% figure has no excerpt) and `lexical-misses-synonyms` (nothing covers the claim that embeddings catch synonyms). Verbatim excerpts that do support them are given below.

---

## Per-claim results

### rag-definition — confirmed_with_changes
- **Excerpt check.** anthropic_contextual_retrieval: verbatim. The sentence goes on with ", significantly enhancing the model's response." google_rag_engine: the words are verbatim, but **the excerpt adds a period in mid-sentence**. The source reads: "The retrieved information becomes the context added to the original user query as a guide for the generative AI model to generate factually grounded and relevant responses."
- **Independent source.** AWS, *What is RAG?* https://aws.amazon.com/what-is/retrieval-augmented-generation/ — "references an authoritative knowledge base outside of its training data sources before generating a response."
- **Notes.** The claim itself is supported. Only the excerpt needs fixing.
- **Fix.** Replace the Google excerpt with: "The retrieved information becomes the context added to the original user query as a guide for the generative AI model"

### rag-private-knowledge — confirmed
- **Excerpt check.** Verbatim. The source goes on: ", that is, your organization's data."
- **Independent source.** Microsoft Learn, *RAG in Azure AI Search* https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview — "RAG … extends LLM capabilities by grounding responses in your proprietary content."
- **Currency.** The Google page now calls RAG Engine "a component of Gemini Enterprise Agent Platform" (no longer "Vertex AI"). sources.yaml already records this.

### rag-small-kb — confirmed_with_changes (currency)
- **Excerpt check.** Verbatim. Full sentence: "If your knowledge base is smaller than 200,000 tokens (about 500 pages of material), you can just include the entire knowledge base in the prompt that you give the model, with no need for RAG or similar methods."
- **Independent source.** Anthropic *Context windows* https://platform.claude.com/docs/en/build-with-claude/context-windows lists many current models that "have a 1M-token context window", and says "Other Claude models, including Claude Sonnet 4.5 (deprecated), have a 200k-token context window."
- **Notes.** The number is accurate for 2024, but it was tied to Claude's 200k window at the time. As written in the present tense, it now reads as current guidance, which it is not. The post also links the advice to prompt caching.
- **Fix.** "In a September 2024 post, Anthropic suggested that a knowledge base under about 200,000 tokens (roughly 500 pages) could simply be placed in the prompt instead of retrieved. That figure matched Claude's context window at the time, and many current Claude models accept up to 1M tokens."

### rag-paper-architecture — confirmed_with_changes (excerpt)
- **Excerpt check.** The abstract excerpt is verbatim, confirmed through the arXiv export API. The §2.2 excerpt is verbatim except for notation: the PDF reads "The retrieval component pη(z|x) is based on DPR [26]." ("p_η" is an ASCII rendering of this.)
- **Missing support.** Neither excerpt mentions **BART-large**. §2.3 says it verbatim: "We use BART-large [32], a pre-trained seq2seq transformer [58] with 400M parameters."
- **Independent source.** HF model card https://huggingface.co/facebook/rag-token-nq — "based on `facebook/dpr-question_encoder-single-nq-base` and `facebook/bart-large`".
- **Notes.** §3 shows the "dense vector index" was a FAISS MIPS index "with a Hierarchical Navigable Small World approximation". In other words, the original RAG used an approximate index. That is useful context for the vector_index component.
- **Excerpt fix.** Add a lewis2020rag §2.3 excerpt: "We use BART-large [32], a pre-trained seq2seq transformer [58] with 400M parameters." Optionally write the §2.2 excerpt as "pη(z|x)".

### rag-paper-chunks — confirmed
- **Excerpt check.** Verbatim, §3: "we use the December 2018 dump. Each Wikipedia article is split into disjoint 100-word chunks, to make a total of 21M documents."
- **Independent source.** DPR paper §4.1 https://arxiv.org/abs/2004.04906 — "we use the English Wikipedia dump from Dec. 20, 2018" … "which results in 21,015,324 passages in the end."

### rag-paper-frozen-index — confirmed_with_changes (causal wording)
- **Excerpt check.** Both excerpts are verbatim (§2.4). The full sentences: "Updating the document encoder BERTd during training is costly as it requires the document index to be periodically updated as REALM does during pre-training [20]. We do not find this step necessary for strong performance, and keep the document encoder (and index) fixed, only fine-tuning the query encoder BERTq and the BART generator."
- **Claim vs source.** The paper gives *two* reasons: updating is costly, and it was not necessary for strong performance. The claim's single "because" leaves out the second.
- **Independent source.** REALM https://arxiv.org/abs/2002.08909 (full text, §3.4) — "the search index goes 'stale' after every gradient update … 'refresh' the index by asynchronously re-embedding and re-indexing all documents".
- **Fix.** "In the RAG paper the document encoder and index stayed fixed; only the query encoder and generator were fine-tuned. Updating the document encoder would mean periodically rebuilding the index, which the authors called costly and found unnecessary for strong performance."

### rag-swap-index — confirmed
- **Excerpt check.** Verbatim (§4.5, "Index hot-swapping"). Context: 70% / 68% accuracy with matched indexes against 12% / 4% with mismatched ones, tested on 82 world leaders.
- **Independent sources.** HF Transformers RAG docs https://huggingface.co/docs/transformers/model_doc/rag — "lets you update knowledge by changing the index instead of retraining the whole model." Atlas https://arxiv.org/abs/2208.03299 — "study the impact of the content of the document index, showing that it can easily be updated."

### rag-sequence-token — confirmed
- **Excerpt check.** Both verbatim (§2.1).
- **Independent source.** The paper's own abstract (not cited for this claim) https://arxiv.org/abs/2005.11401 — "one which conditions on the same retrieved passages across the whole generated sequence, the other can use different passages per token." The HF checkpoints `facebook/rag-sequence-nq` and `facebook/rag-token-nq` confirm both variants were released, but their cards do not describe the difference.
- **Notes.** No fully external description was found. The abstract is the best cross-check available.

### chunking-affects-retrieval — confirmed
- **Excerpt check.** Verbatim, followed by footnote marker "1".
- **Independent source.** Chroma Research, *Evaluating Chunking Strategies for Retrieval* https://research.trychroma.com/evaluating-chunking — "the choice of chunking strategy can have a significant impact on retrieval performance, with some strategies outperforming others by up to 9% in recall."

### chunking-overlap — confirmed
- **Excerpt check.** Verbatim. LangChain describes `chunk_overlap` as "Target overlap between chunks."
- **Independent source.** Chroma (above): "suggesting that for smaller context, overlapping chunks are necessary for high recall". It also says "reducing chunk overlap improves IoU scores, as this metric penalizes redundant information."
- **Notes.** The claim is accurate as worded. A teaching note could add the cost: overlap means redundant tokens, so the same evidence takes up more of the context budget.

### chunking-context-loss — confirmed
- **Excerpt check.** Both verbatim.
- **Independent source.** Late Chunking (Jina AI) https://arxiv.org/abs/2409.04701 — "chunk embeddings created in this way can lose contextual information from surrounding chunks, resulting in sub-optimal representations."

### openai-chunk-defaults — confirmed_with_changes (product scope, currency)
- **Excerpt check.** Verbatim apart from Markdown backticks. These appear in the Retrieval guide's "Chunking" section on **vector stores**. The guide then says: "chunk_overlap_tokens must be non-negative and should not exceed max_chunk_size_tokens / 2."
- **Claim vs source.** The cited page covers vector-store file chunking, not the file-search tool page (`openai_file_search` has no chunking text). The file search tool runs on vector stores, so the substance holds, but "file search's default" is an inference. The 100–4096 range applies to the **static** strategy, which the claim already says.
- **Independent sources.** OpenAI API reference, *Create vector store file* https://developers.openai.com/api/reference/resources/vector_stores/subresources/files/methods/create — "The default strategy. This strategy currently uses a max_chunk_size_tokens of 800 and chunk_overlap_tokens of 400." Chroma Research also independently cites OpenAI's "chunk size of 800 tokens with an overlap of 400 tokens".
- **Fix.** "OpenAI vector stores (which back the file search tool) currently default to 800-token chunks with a 400-token overlap. A custom static strategy allows 100–4096-token chunks, with overlap at most half the chunk size."

### embedding-definition — confirmed
- **Excerpt check.** Both verbatim.
- **Independent source.** Google ML Crash Course https://developers.google.com/machine-learning/crash-course/embeddings/embedding-space — "The distance between points in an embedding space represents the relative similarity between the corresponding items."

### cosine-dot-normalized — confirmed
- **Excerpt check.** Both verbatim. OpenAI's context: "OpenAI embeddings are normalized to length 1, which means that: Cosine similarity can be computed slightly faster using just a dot product".
- **Independent sources.** Manning et al., *IR book* §6.3.1 https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html — cosine similarity's "numerator represents the dot product … while the denominator is the product of their Euclidean lengths". The Faiss index table (not cited for this claim) says of IndexFlatIP: "also for cosine (normalize vectors beforehand)".
- **Notes.** Consistent with the backend docstring: "Because every vector is L2-normalised, the dot product equals cosine similarity."

### openai-embedding-dims — confirmed
- **Excerpt check.** Verbatim apart from backticks. The sentence starts "By default, the length of the embedding vector is 1536 for text-embedding-3-small or 3072 for text-embedding-3-large." The second excerpt is verbatim.
- **Independent source.** Microsoft Azure OpenAI models https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models table: "text-embedding-3-large 8,192 3,072 … text-embedding-3-small 8,192 1,536".
- **Currency.** The OpenAI guide still lists text-embedding-3 as its current generation as of the access date. The OpenAI launch blog returned 403 and was not used.

### anthropic-no-embeddings — confirmed_with_changes (nuance, currency)
- **Excerpt check.** Both verbatim (backticks aside). The context: "One embeddings provider with a wide variety of models and capabilities is Voyage AI by MongoDB … you should assess a variety of embeddings vendors". It also says: "For all retrieval tasks and use cases (for example, RAG), use the input_type parameter to specify whether the input text is a query or document."
- **Claim vs source.** "Its docs point to Voyage AI" is fair, but Anthropic presents Voyage as *one* provider and tells readers to assess others. `input_type` is an optional parameter (default None) that is *recommended* for retrieval. It is not a fixed property of the models.
- **Independent source.** Voyage AI docs https://docs.voyageai.com/docs/embeddings — "input_type (str, optional, defaults to None) - Type of the input text. Options: None, query, document."
- **Currency.** Voyage is now branded "Voyage AI by MongoDB", and the current models are the voyage-4 family.
- **Fix.** "Anthropic does not offer its own embedding model. Its docs use Voyage AI (now part of MongoDB) as an example provider and recommend setting input_type to query or document for retrieval."

### bi-encoder — confirmed
- **Excerpt check.** The SBERT docs excerpt is verbatim. The reimers2019sbert excerpt is verbatim in the arXiv abstract (confirmed through the export API): "…to derive semantically meaningful sentence embeddings that can be compared using cosine-similarity."
- **Independent source.** DPR §3.1 https://arxiv.org/abs/2004.04906 — "we apply the passage encoder EP to all the passages and index them using FAISS … offline."

### dpr-dot-product — confirmed
- **Excerpt check.** Verbatim (§3.1). The preceding clause adds a qualifier: "As our ablation study finds other similarity functions perform comparably … we thus choose the simpler inner product function".
- **Independent source.** RAG paper §2.2 https://arxiv.org/abs/2005.11401 — "DPR follows a bi-encoder architecture: pη(z|x) ∝ exp(d(z)⊤q(x))".

### flat-index-exact — confirmed_with_changes (excerpt)
- **Excerpt check.** "Exact Search for Inner Product" is verbatim, but it is a table-row label. The same row marks the index "Exhaustive: yes". The HNSW excerpt is verbatim from the abstract, but it describes the graph structure only. **It does not support "trade some accuracy for much faster search."**
- **Independent source.** Faiss wiki, *Guidelines to choose an index* https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index — "The only index that can guarantee exact results is the IndexFlatL2 or IndexFlatIP."
- **Excerpt fixes.** For faiss_indexes, replace "Exact Search for Inner Product" with the guidelines sentence above. That requires adding a source `faiss_guidelines`, or else keep the row label and add "Exhaustive: yes" as context. For malkov2016hnsw, replace the excerpt with: "We present a new approach for the approximate K-nearest neighbor search based on navigable small world graphs with controllable hierarchy".

### hnsw-log-scaling — confirmed_with_changes (qualifier)
- **Excerpt check.** Verbatim in the abstract ("…and allows a logarithmic complexity scaling.").
- **Full text (read this pass).** §4.2.1: "The complexity scaling of a single search can be strictly analyzed under the assumption that we build exact Delaunay graphs…", then "the overall complexity scaling is O(log(N)), in agreement with the simulations on low dimensional datasets." The paper adds that this assumption "violates in Hierarchical NSW due to usage of approximate edge selection heuristic".
- **Notes.** Attributing this to "the authors report" is right, but the log scaling rests on an idealised analysis and on low-dimensional experiments. The sources.yaml note "full text not read" can now be updated.
- **Independent source.** The paper's own full text, §4.2.1 (arXiv PDF https://arxiv.org/pdf/1603.09320v4), quoted above.
- **Fix.** "HNSW's authors report search cost that scales logarithmically with the number of stored vectors. Their analysis assumes idealised graphs and matches their experiments on low-dimensional data."

### bm25-mechanics — confirmed
- **Excerpt check.** Both verbatim, ignoring the "oﬀ" ligature. Saturation is in §3.4.2, and the b sentence is in §3.4.5 ("Thus setting b = 1 will perform full document-length normalisation, while b = 0 will switch normalisation off."). The locator "§3.4" is acceptable.
- **Independent source.** IR book §11.4.3 https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html — "b = 1 corresponds to fully scaling the term weight by the document length, while b = 0 corresponds to no length normalization."

### bm25-defaults — confirmed_with_changes (excerpt)
- **Excerpt check.** The Elasticsearch excerpt is verbatim apart from backticks and covers **only b**. The k1 default has no excerpt; the same page says: "k1 Controls non-linear term frequency normalization (saturation). The default value is 1.2." The Robertson excerpt is verbatim apart from PDF spacing (§3.5), and the source qualifies it straight away: "However, there is also evidence that optimal values do depend on other factors (such as the type of documents or queries)."
- **Independent sources.** Lucene BM25Similarity javadoc https://lucene.apache.org/core/9_11_0/core/org/apache/lucene/search/similarities/BM25Similarity.html — "BM25 with these default values: k1 = 1.2 b = 0.75". IR book §11.4.3: reasonable values set k1 "to a value between 1.2 and 2 and b = 0.75".
- **Notes.** The claim is accurate. It might help to note that the DPR paper's BM25 baseline was tuned to b = 0.4, k1 = 0.9, which shows the defaults are not universal.
- **Excerpt fix.** Add an elasticsearch_similarity excerpt: "Controls non-linear term frequency normalization (saturation). The default value is `1.2`."

### lexical-misses-synonyms — confirmed_with_changes (absolute wording, missing support)
- **Excerpt check.** Verbatim. Nothing supports the second sentence, but the same page says: "Semantic search overcomes the shortcomings of lexical search and can recognize synonym and acronyms."
- **Claim vs source.** "Only matches the words used" holds for plain keyword matching. Real lexical engines often add stemming, synonym filters or query expansion. "Trained to catch them" overstates it: embeddings *often* catch synonyms but not always. See also the default lexical-hashing embedder issue in the summary.
- **Independent source.** IR book ch. 9 https://nlp.stanford.edu/IR-book/html/htmledition/relevance-feedback-and-query-expansion-1.html — "This issue, known as synonymy, has an impact on the recall of most information retrieval systems." The same page lists thesaurus-based query expansion as a fix.
- **Fix.** "Plain keyword search only matches the words used, so it misses synonyms and rephrasings unless synonyms or query expansion are added. Neural embedding models are trained to place such paraphrases close together, so they often catch them."
- **Excerpt fix.** Add an sbert_retrieve_rerank excerpt: "Semantic search overcomes the shortcomings of lexical search and can recognize synonym and acronyms."

### rrf — confirmed
- **Excerpt check.** Both verbatim. The second ("combines ranks without regard to the arbitrary scores returned by particular ranking methods") is split by a PDF hyphen. Formula: "RRFscore(d ∈ D) = Σ_{r∈R} 1/(k + r(d))". The paper adds that k = 60 "was near-optimal, but that the choice was not critical."
- **Independent source.** Elasticsearch RRF reference https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion — `rank_constant` "Defaults to 60."

### hybrid-contextual-results — confirmed_with_changes (excerpt, setup qualifier)
- **Excerpt check.** Both verbatim. The full figures are 5.7% → 3.7% (35%), 5.7% → 2.9% (49%) and 5.7% → 1.9% (67%). **The 49% step has no excerpt.** Verbatim: "Combining Contextual Embeddings and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 49%".
- **Claim vs source.** These are averages across Anthropic's knowledge domains, using the "top-performing embedding configuration (Gemini Text 004)" and the Cohere reranker, with metric 1 − recall@20. The claim says "Anthropic's 2024 tests", which is fair, but it leaves out that these are best-configuration averages.
- **Independent source.** No third-party replication was found (web search). The closest cross-check is Anthropic's own cookbook on a different dataset (codebases): https://github.com/anthropics/claude-cookbooks/blob/main/capabilities/contextual-embeddings/guide.ipynb — "we've reduced retrieval failures by ~30-40% across all k values". It points the same way but is the same vendor, not independent.
- **Fix.** "In Anthropic's 2024 tests (averaged across its datasets with the best embedding setup), top-20 retrieval failure fell 35% with contextual embeddings, 49% when contextual BM25 was added, and 67% with reranking on top."
- **Excerpt fix.** Add the 49% sentence above.

### rerank-cross-encoder — confirmed
- **Excerpt check.** Both verbatim on the Cross-Encoders page. The page also says Cross-Encoders "do not scale well for large datasets".
- **Independent source.** Nogueira & Cho, *Passage Re-ranking with BERT* https://arxiv.org/abs/1901.04085 — "a simple re-implementation of BERT for query-based passage re-ranking … the top entry in the leaderboard of the MS MARCO passage retrieval task".

### dpr-beats-bm25 — disputed
- **Excerpt check.** "outperforms a strong Lucene-BM25 system largely by 9%-19% absolute" is verbatim on the **arXiv abs page**. The v3 PDF (the version sources.yaml records) says "greatly by 9%-19% absolute". The text continues "in terms of top-20 passage retrieval accuracy".
- **Contradiction.** The paper's own §5.1 says: "With the exception of SQuAD, DPR performs consistently better than BM25 on all datasets." Top-20 figures from Table 2, BM25 vs single-dataset DPR: NQ 59.1 vs 78.4 (+19.3), TriviaQA 66.9 vs 79.4 (+12.5), WQ 55.0 vs 73.2 (+18.2), TREC 70.9 vs 79.8 (+8.9), **SQuAD 68.8 vs 63.2 (−5.6)**. So "on the open-domain QA benchmarks it was tested on" is wrong for one of the five.
- **Independent source.** DPR full text, §5.1 and Table 2 (https://arxiv.org/pdf/2004.04906v3), quoted above. Note too that the BM25 baseline was tuned to b = 0.4 and k1 = 0.9.
- **Fix.** "On four of the five open-domain QA benchmarks it was tested on (all except SQuAD), DPR beat a tuned Lucene BM25 baseline by about 9–19 points of top-20 passage retrieval accuracy."
- **Excerpt fix.** Keep "largely" only if the citation names the abs page. To match the v3 PDF in sources.yaml, use "outperforms a strong Lucene-BM25 system greatly by 9%-19% absolute". Add a §5.1 excerpt: "With the exception of SQuAD, DPR performs consistently better than BM25 on all datasets."

### prompt-docs-first — confirmed_with_changes (qualifiers)
- **Excerpt check.** The first excerpt is verbatim. The second is verbatim apart from backticks. Context: the section opens "When working with large documents or data-rich inputs (20k+ tokens)", and the tag advice is prefaced "When using multiple documents". The page adds: "Queries at the end can improve response quality by up to 30 percent in tests".
- **Independent sources.** Gemini prompting strategies https://ai.google.dev/gemini-api/docs/prompting-strategies — "supply all the context first. Place your specific instructions or questions at the very end of the prompt." (This agrees.) OpenAI GPT-4.1 prompting guide https://cookbook.openai.com/examples/gpt4-1_prompting_guide — "ideally place your instructions at both the beginning and end of the provided context". (This qualifies it: vendors differ on where *instructions* go.)
- **Fix.** "For long inputs (20k+ tokens), Anthropic recommends putting documents at the top of the prompt, above the instructions and the question. With several documents, each goes in its own <document> tag with <source> and <document_content> subtags."

### lost-in-middle — confirmed
- **Excerpt check.** Verbatim (§1). The abstract hedges: performance "is often highest when relevant information occurs at the beginning or end".
- **Independent source.** *Found in the Middle* (2024) https://arxiv.org/abs/2406.16008 — "LLMs exhibit a U-shaped attention bias where the tokens at the beginning and at the end of its input receive higher attention".
- **Notes.** The Pass 1 note "2023-era models; newer models may differ" is appropriate.

### rag-hallucination — confirmed_with_changes (excerpt scope)
- **Excerpt check.** The Lewis excerpt is verbatim (§4.2, no locator given) and qualitative. The Anthropic excerpt is verbatim, but the full sentence is: "Remember, while these techniques significantly reduce hallucinations, they don't eliminate them entirely." "These techniques" are the page's prompting strategies, not retrieval specifically.
- **Independent sources.** Magesh et al. 2024, *Hallucination-Free?* https://arxiv.org/abs/2405.20362 — RAG-based legal tools "each hallucinate between 17% and 33% of the time". Shuster et al. 2021 https://arxiv.org/abs/2104.07567 — retrieval "substantially reduce[s] the well-known problem of knowledge hallucination".
- **Notes.** The claim is well supported overall. Magesh et al. supports the exact point (RAG reduces hallucination but does not remove it) more directly than either current citation.
- **Excerpt fix.** Lengthen the Anthropic excerpt to "while these techniques significantly reduce hallucinations, they don't eliminate them entirely". Add a locator "§4.2" to the Lewis excerpt. Consider adding Magesh et al. 2024 to sources.yaml and citing it.

### citations-feature — confirmed
- **Excerpt check.** Both verbatim. The first continues: "If you need more control over citation granularity … use custom content documents instead." For custom content documents, "no further chunking is done."
- **Independent source.** Anthropic launch post https://www.anthropic.com/news/introducing-citations-api — "the API processes user-provided source documents (PDF documents and plain text files) by chunking them into sentences."
- **Notes.** "Valid pointers" guarantees the location exists. It does not guarantee the cited text supports the claim. The tour line "Citations let you check them" is consistent with that.

### grounding-definition — confirmed
- **Excerpt check.** Verbatim. The page now carries the "Gemini Enterprise Agent Platform" branding.
- **Independent source.** Gemini API, *Grounding with Google Search* https://ai.google.dev/gemini-api/docs/google-search — grounding lets Gemini "provide more accurate answers and cite verifiable sources beyond its knowledge cutoff."

---

## Uncovered statements (component / challenge / tour / visual text)

1. **`query_encoder.short`: "Encodes the question with the same model."** This is inaccurate in general and contradicts the `dpr-dot-product` claim attached to the same component. DPR uses "two independent BERT … networks", and RAG uses BERT_q and BERT_d. Suggested: "Encodes the question into the same vector space as the chunks (often with the same model)." The detail text ("into the same vector space") and the tour body are fine.
2. **`embedder.detail` and the lexical-misses-synonyms framing versus the default embedder.** The default backend embedder is lexical TF-IDF hashing (`embedding.py`, default in `pipeline.py`), and it explicitly does not place paraphrases together. lesson.yaml never tells the learner. The "Synonym test" preset will show dense retrieval failing too, unless `neural-local` is enabled. Suggested: add to the `experiment` visual description something like "Offline, 'dense' uses a lexical hashing embedder as a stand-in for a neural model; it does not catch synonyms." Pass 3 should confirm what the frontend shows.
3. **`challenges.ranking-miss.explanation`: "Reciprocal rank fusion keeps chunks that either ranker places highly."** This overstates it (worked example in the summary). Suggested: "Reciprocal rank fusion rewards chunks that rank well in either list, and most of all chunks both rankers agree on."
4. **`challenges.boundary-split.explanation`: "Larger chunks fix both problems."** This is true for this corpus, but stated as a general rule. Larger chunks make splits less likely without ruling them out, and they can dilute relevance. Late Chunking abstract: "dense vector-based retrieval systems often perform better with shorter text segments". Chroma found 200-token chunks without overlap did well. Suggested: "Here, larger chunks fix both problems, though very large chunks can bury a fact among unrelated text."
5. **`challenges.too-few-results.explanation`: "Top-k sets how much evidence reaches the model."** This conflicts with the lesson's own `budget-overflow` challenge, where the context budget drops retrieved chunks. Suggested: "Top-k sets how much evidence is retrieved." The linked claim (`rag-definition`) does not support the top-k trade-off. The "too many … noise" half has support in Liu et al. 2023, whose experiments vary the number of retrieved documents, so consider linking `lost-in-middle`.
6. **`challenges.budget-overflow` claim link.** `prompt-docs-first` does not support "a context budget that is too small silently drops evidence". That describes ExplodeAI's own assembler, so mark it as an implementation statement for Pass 3 instead of linking a provider claim.
7. **`retriever.detail`: "hybrid retrieval fuses both rankings."** This is accurate for this lesson, which uses RRF. In general, hybrid can also fuse *scores*: the DPR paper used "BM25(q,p) + λ·sim(q,p)" with λ = 1.1, and Anthropic's cookbook used weighted RRF. Optional: "…hybrid retrieval fuses both (here with reciprocal rank fusion)."
8. **`prompt_builder.detail` and tour body: "Documents go first, then the instructions and the question."** This matches Anthropic and Gemini guidance. OpenAI's GPT-4.1 guide prefers instructions both before and after long context. Fine as ExplodeAI's layout; just avoid calling it universal.
9. **`vector_index.detail`: "Approximate indexes like HNSW scale to millions of vectors."** Supported: the RAG paper itself used FAISS HNSW over 21M passages. No change needed. You could add that Faiss HNSW "does not support removing vectors from the index" (Faiss wiki) if index updates come up.
10. **`corpus.detail`: "six fictional help-centre articles."** Matches `corpus.py`, which has 6 `Document(` entries.
11. **`backend/app/experiments/rag/retrieval.py` docstring.** Consistent with the claims: k1 = 1.2, b = 0.75, RRF k = 60, Lucene-style non-negative IDF.
12. **sources.yaml housekeeping.** No claim in this lesson cites `johnson2017faiss`, `openai_file_search` or `gemini_embeddings`. Either cite them (e.g. `openai_file_search` for "file search uses vector stores") or note that they are unused. Update `malkov2016hnsw.version` ("full text not read"); the full text was read in this pass. For `karpukhin2020dpr`, note that the abs page and the v3 PDF word the abstract differently ("largely" vs "greatly").

---

## Machine-readable results

```yaml
pass2:
  date: 2026-10-18
  results:
    - claim: rag-definition
      verdict: confirmed_with_changes
      independent_sources: [https://aws.amazon.com/what-is/retrieval-augmented-generation/]
      fix: null
      excerpt_fixes:
        - {source: google_rag_engine, old: "The retrieved information becomes the context added to the original user query.", new: "The retrieved information becomes the context added to the original user query as a guide for the generative AI model"}
    - claim: rag-private-knowledge
      verdict: confirmed
      independent_sources: [https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview]
      fix: null
      excerpt_fixes: []
    - claim: rag-small-kb
      verdict: confirmed_with_changes
      independent_sources: [https://platform.claude.com/docs/en/build-with-claude/context-windows]
      fix: "In a September 2024 post, Anthropic suggested that a knowledge base under about 200,000 tokens (roughly 500 pages) could simply be placed in the prompt instead of retrieved. That figure matched Claude's context window at the time, and many current Claude models accept up to 1M tokens."
      excerpt_fixes: []
    - claim: rag-paper-architecture
      verdict: confirmed_with_changes
      independent_sources: [https://huggingface.co/facebook/rag-token-nq]
      fix: null
      excerpt_fixes:
        - {source: lewis2020rag, old: null, new: "We use BART-large [32], a pre-trained seq2seq transformer [58] with 400M parameters."}
        - {source: lewis2020rag, old: "The retrieval component p_η(z|x) is based on DPR", new: "The retrieval component pη(z|x) is based on DPR"}
    - claim: rag-paper-chunks
      verdict: confirmed
      independent_sources: [https://arxiv.org/abs/2004.04906]
      fix: null
      excerpt_fixes: []
    - claim: rag-paper-frozen-index
      verdict: confirmed_with_changes
      independent_sources: [https://arxiv.org/abs/2002.08909]
      fix: "In the RAG paper the document encoder and index stayed fixed; only the query encoder and generator were fine-tuned. Updating the document encoder would mean periodically rebuilding the index, which the authors called costly and found unnecessary for strong performance."
      excerpt_fixes:
        - {source: lewis2020rag, old: null, new: "We do not find this step necessary for strong performance"}
    - claim: rag-swap-index
      verdict: confirmed
      independent_sources: [https://huggingface.co/docs/transformers/model_doc/rag, https://arxiv.org/abs/2208.03299]
      fix: null
      excerpt_fixes: []
    - claim: rag-sequence-token
      verdict: confirmed
      independent_sources: [https://arxiv.org/abs/2005.11401]
      fix: null
      excerpt_fixes: []
    - claim: chunking-affects-retrieval
      verdict: confirmed
      independent_sources: [https://research.trychroma.com/evaluating-chunking]
      fix: null
      excerpt_fixes: []
    - claim: chunking-overlap
      verdict: confirmed
      independent_sources: [https://research.trychroma.com/evaluating-chunking]
      fix: null
      excerpt_fixes: []
    - claim: chunking-context-loss
      verdict: confirmed
      independent_sources: [https://arxiv.org/abs/2409.04701]
      fix: null
      excerpt_fixes: []
    - claim: openai-chunk-defaults
      verdict: confirmed_with_changes
      independent_sources: [https://developers.openai.com/api/reference/resources/vector_stores/subresources/files/methods/create, https://research.trychroma.com/evaluating-chunking]
      fix: "OpenAI vector stores (which back the file search tool) currently default to 800-token chunks with a 400-token overlap. A custom static strategy allows 100–4096-token chunks, with overlap at most half the chunk size."
      excerpt_fixes: []
    - claim: embedding-definition
      verdict: confirmed
      independent_sources: [https://developers.google.com/machine-learning/crash-course/embeddings/embedding-space]
      fix: null
      excerpt_fixes: []
    - claim: cosine-dot-normalized
      verdict: confirmed
      independent_sources: [https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html]
      fix: null
      excerpt_fixes: []
    - claim: openai-embedding-dims
      verdict: confirmed
      independent_sources: [https://learn.microsoft.com/en-us/azure/ai-foundry/openai/concepts/models]
      fix: null
      excerpt_fixes:
        - {source: openai_embeddings, old: "the length of the embedding vector is `1536` for `text-embedding-3-small` or `3072` for `text-embedding-3-large`", new: "By default, the length of the embedding vector is `1536` for `text-embedding-3-small` or `3072` for `text-embedding-3-large`"}
    - claim: anthropic-no-embeddings
      verdict: confirmed_with_changes
      independent_sources: [https://docs.voyageai.com/docs/embeddings]
      fix: "Anthropic does not offer its own embedding model. Its docs use Voyage AI (now part of MongoDB) as an example provider and recommend setting input_type to query or document for retrieval."
      excerpt_fixes:
        - {source: anthropic_embeddings, old: null, new: "One embeddings provider with a wide variety of models and capabilities is Voyage AI by MongoDB."}
    - claim: bi-encoder
      verdict: confirmed
      independent_sources: [https://arxiv.org/abs/2004.04906]
      fix: null
      excerpt_fixes: []
    - claim: dpr-dot-product
      verdict: confirmed
      independent_sources: [https://arxiv.org/abs/2005.11401]
      fix: null
      excerpt_fixes: []
    - claim: flat-index-exact
      verdict: confirmed_with_changes
      independent_sources: [https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index]
      fix: null
      excerpt_fixes:
        - {source: malkov2016hnsw, old: "builds a multi-layer structure consisting from hierarchical set of proximity graphs (layers)", new: "We present a new approach for the approximate K-nearest neighbor search based on navigable small world graphs with controllable hierarchy"}
        - {source: faiss_indexes, old: "Exact Search for Inner Product", new: "Exact Search for Inner Product IndexFlatIP \"Flat\" d 4*d yes also for cosine (normalize vectors beforehand)"}
    - claim: hnsw-log-scaling
      verdict: confirmed_with_changes
      independent_sources: [https://arxiv.org/pdf/1603.09320v4]
      fix: "HNSW's authors report search cost that scales logarithmically with the number of stored vectors. Their analysis assumes idealised graphs and matches their experiments on low-dimensional data."
      excerpt_fixes:
        - {source: malkov2016hnsw, old: null, new: "the overall complexity scaling is O(log(N)), in agreement with the simulations on low dimensional datasets"}
    - claim: bm25-mechanics
      verdict: confirmed
      independent_sources: [https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html]
      fix: null
      excerpt_fixes: []
    - claim: bm25-defaults
      verdict: confirmed_with_changes
      independent_sources: [https://lucene.apache.org/core/9_11_0/core/org/apache/lucene/search/similarities/BM25Similarity.html, https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html]
      fix: null
      excerpt_fixes:
        - {source: elasticsearch_similarity, old: null, new: "Controls non-linear term frequency normalization (saturation). The default value is `1.2`."}
    - claim: lexical-misses-synonyms
      verdict: confirmed_with_changes
      independent_sources: [https://nlp.stanford.edu/IR-book/html/htmledition/relevance-feedback-and-query-expansion-1.html]
      fix: "Plain keyword search only matches the words used, so it misses synonyms and rephrasings unless synonyms or query expansion are added. Neural embedding models are trained to place such paraphrases close together, so they often catch them."
      excerpt_fixes:
        - {source: sbert_retrieve_rerank, old: null, new: "Semantic search overcomes the shortcomings of lexical search and can recognize synonym and acronyms."}
    - claim: rrf
      verdict: confirmed
      independent_sources: [https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion]
      fix: null
      excerpt_fixes: []
    - claim: hybrid-contextual-results
      verdict: confirmed_with_changes
      independent_sources: [https://github.com/anthropics/claude-cookbooks/blob/main/capabilities/contextual-embeddings/guide.ipynb]
      fix: "In Anthropic's 2024 tests (averaged across its datasets with the best embedding setup), top-20 retrieval failure fell 35% with contextual embeddings, 49% when contextual BM25 was added, and 67% with reranking on top."
      excerpt_fixes:
        - {source: anthropic_contextual_retrieval, old: null, new: "Combining Contextual Embeddings and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 49%"}
    - claim: rerank-cross-encoder
      verdict: confirmed
      independent_sources: [https://arxiv.org/abs/1901.04085]
      fix: null
      excerpt_fixes: []
    - claim: dpr-beats-bm25
      verdict: disputed
      independent_sources: [https://arxiv.org/pdf/2004.04906v3]
      fix: "On four of the five open-domain QA benchmarks it was tested on (all except SQuAD), DPR beat a tuned Lucene BM25 baseline by about 9–19 points of top-20 passage retrieval accuracy."
      excerpt_fixes:
        - {source: karpukhin2020dpr, old: "outperforms a strong Lucene-BM25 system largely by 9%-19% absolute", new: "outperforms a strong Lucene-BM25 system greatly by 9%-19% absolute"}
        - {source: karpukhin2020dpr, old: null, new: "With the exception of SQuAD, DPR performs consistently better than BM25 on all datasets."}
    - claim: prompt-docs-first
      verdict: confirmed_with_changes
      independent_sources: [https://ai.google.dev/gemini-api/docs/prompting-strategies, https://cookbook.openai.com/examples/gpt4-1_prompting_guide]
      fix: "For long inputs (20k+ tokens), Anthropic recommends putting documents at the top of the prompt, above the instructions and the question. With several documents, each goes in its own <document> tag with <source> and <document_content> subtags."
      excerpt_fixes: []
    - claim: lost-in-middle
      verdict: confirmed
      independent_sources: [https://arxiv.org/abs/2406.16008]
      fix: null
      excerpt_fixes: []
    - claim: rag-hallucination
      verdict: confirmed_with_changes
      independent_sources: [https://arxiv.org/abs/2405.20362, https://arxiv.org/abs/2104.07567]
      fix: null
      excerpt_fixes:
        - {source: anthropic_hallucinations, old: "they don't eliminate them entirely. Always validate critical information", new: "while these techniques significantly reduce hallucinations, they don't eliminate them entirely. Always validate critical information"}
    - claim: citations-feature
      verdict: confirmed
      independent_sources: [https://www.anthropic.com/news/introducing-citations-api]
      fix: null
      excerpt_fixes: []
    - claim: grounding-definition
      verdict: confirmed
      independent_sources: [https://ai.google.dev/gemini-api/docs/google-search]
      fix: null
      excerpt_fixes: []
```

Notes on the YAML: `old: null` in an excerpt fix means "add this excerpt". The openai-embedding-dims excerpt fix is optional: it only adds the "By default," prefix. In the flat-index-exact Faiss fix, the `new` value is a flattened table row; using the guidelines-page sentence needs a new source id, e.g. `faiss_guidelines` → https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index.
