# Document Chunking and Text Embeddings in RAG Pipelines: Primary-Source Notes (Pass 1)

Access date for all sources: 2026-10-18. Notes on method:
- "Verbatim" excerpts come from one of two places. (a) Raw text I downloaded myself: the OpenAI embeddings guide as markdown, the arXiv API abstract, the Robertson & Zaragoza PDF (text extracted with a custom script), and the sentence-transformers source code. (b) WebFetch, where a small model summarizes the page and quotes from it. Excerpts from (b) are marked [WF]. They were requested verbatim but were not checked character by character, so Pass 2 should re-check them.
- OpenAI docs now live at developers.openai.com. platform.openai.com/docs/guides/embeddings returned "301 Moved Permanently" to https://developers.openai.com/api/docs/guides/embeddings. Anthropic docs moved from docs.claude.com (302) to platform.claude.com.
- The OpenAI launch blog (openai.com/index/new-embedding-models-and-api-updates/) returned HTTP 403 to both WebFetch and curl, so I could not fetch it. Claims attributed to it are only confirmed second-hand through the OpenAI guide.

## Q1. Chunking: what official sources say about chunk size and overlap (OpenAI file search defaults; Anthropic Contextual Retrieval; framework docs)

### Takeaway
OpenAI file search defaults to an `auto` strategy, which currently means 800-token chunks with 400-token overlap. A `static` strategy lets you set the chunk size to anything from 100 to 4096 tokens, with overlap no more than half the chunk size. Anthropic's Contextual Retrieval post (Sep 19, 2024) says splitting loses context. Its fix is to prepend 50–100 tokens of LLM-generated, chunk-specific context to each chunk before embedding and BM25 indexing. That cut the top-20-chunk retrieval failure rate (1 − recall@20) by 35%, then 49% with contextual BM25 added, then 67% with reranking added.

### Cited Findings

**OpenAI file search / vector stores (provider docs; no date or version shown on the pages)**
- Default chunking: "By default, `max_chunk_size_tokens` is set to `800` and `chunk_overlap_tokens` is set to `400`" [WF]. The guide goes on: "every file is indexed by being split up into 800-token chunks, with 400-token overlap between consecutive chunks" [WF] — [OpenAI Retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)
- Allowed range: "`max_chunk_size_tokens` must be between 100 and 4096 inclusive." [WF] — [OpenAI Retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)
- Overlap constraint: "`chunk_overlap_tokens` must be non-negative and should not exceed `max_chunk_size_tokens / 2`." [WF] — [OpenAI Retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)
- The API reference names the default strategy: "If not set, will use the `auto` strategy." It also says auto "currently uses a `max_chunk_size_tokens` of `800` and `chunk_overlap_tokens` of `400`." Static is described as "Customize your own chunking strategy by setting chunk size and chunk overlap." Constraint: "the overlap must not exceed half of `max_chunk_size_tokens`" [WF] — [OpenAI API reference: create vector store file](https://developers.openai.com/api/reference/resources/vector_stores/subresources/files/methods/create)
- File limits: "The maximum file size is 512 MB." and "no more than 5,000,000 tokens per file" [WF] — [OpenAI Retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)
- Search defaults and options: results default to "10 results maximum by default, but you can set up to 50 using the `max_num_results` parameter" [WF]. Optional `rewrite_query=true`. A `ranker` option (e.g. `auto`, `default-2024-08-21`). A `score_threshold`. And `hybrid_search` weights that "control how reciprocal rank fusion balances semantic embedding matches vs. sparse keyword matches" [WF] — [OpenAI Retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)
- The file-search tool guide covers retrieval only at a high level: retrieval "through semantic and keyword search" [WF]. It contains no chunking parameters — [OpenAI File search guide](https://developers.openai.com/api/docs/guides/tools-file-search)

**Anthropic, "Introducing Contextual Retrieval" (provider blog/research post, "Published Sep 19, 2024")**
- Problem statement: "The problem is that traditional RAG solutions remove context when encoding information," [WF]. Its example is a chunk like "The company's revenue grew by 3%..." that names neither the company nor the period — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Typical chunk size in traditional RAG: "usually no more than a few hundred tokens" [WF] — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Method: "prepending chunk-specific explanatory context to each chunk before embedding" (Contextual Embeddings) and before "creating the BM25 index ("Contextual BM25")" [WF]. The generated context is "usually 50-100 tokens" [WF] — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Metric: "We use 1 minus recall@20 as our evaluation metric" [WF] — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Results, all measured as top-20-chunk retrieval failure rate [WF] — [Anthropic](https://www.anthropic.com/news/contextual-retrieval):
  - "Contextual Embeddings reduced the top-20-chunk retrieval failure rate by 35%" (5.7% → 3.7%)
  - "Combining Contextual Embeddings and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 49%" (5.7% → 2.9%)
  - "Reranked Contextual Embedding and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 67%" (5.7% → 1.9%)
- On chunking trade-offs: "The choice of chunk size, chunk boundary, and chunk overlap can affect retrieval performance" [WF]. The post gives no specific overlap recommendation (per the WebFetch summary). It also found that retrieving 20 chunks beat retrieving 10 or 5 — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Embedding models: Gemini and Voyage embeddings were "particularly effective" in its tests [WF] — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Cost: "$1.02 per million document tokens" (one-time, with prompt caching). This assumes "800 token chunks, 8k token documents, 50 token context instructions, and 100 tokens of context per chunk" [WF] — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- When to skip RAG: "If your knowledge base is smaller than 200,000 tokens (about 500 pages of material)," the whole knowledge base can go in the prompt [WF] — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)

**Framework docs (secondary; widely used; no version or date on the pages)**
- LangChain RecursiveCharacterTextSplitter: it "tries to split on them in order until the chunks are small enough"; default separators `["\n\n", "\n", " ", ""]`; this "has the effect of trying to keep all paragraphs (and then sentences, and then words) together as long as possible" [WF]. `chunk_overlap` is described as: "Overlapping chunks helps to mitigate loss of information when context is divided between chunks." Chunk size is measured in characters by default, through `length_function` [WF] — [LangChain docs](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)
- LlamaIndex SentenceSplitter: it "attempts to split text while respecting the boundaries of sentences" [WF]. The example uses `chunk_size=1024, chunk_overlap=20`, but the page does not call these the class defaults. SemanticSplitterNodeParser "adaptively picks the breakpoint in-between sentences using embedding similarity" [WF] — [LlamaIndex node parsers](https://developers.llamaindex.ai/python/framework/module_guides/loading/node_parsers/modules/)
- Hugging Face cookbook (Aymeric Roucher, undated; a community cookbook, not official API docs): chunk size "too small will truncate ideas, and too large will dilute them" [WF]. Overlap "lets adjacent chunks get a bit of overlap on each other", set to one tenth of the chunk size in the notebook. Chunks longer than the embedding model's max sequence length (512 for `thenlper/gte-small`) are "truncated before processing, thus losing relevancy" [WF] — [HF Cookbook: Advanced RAG](https://huggingface.co/learn/cookbook/advanced_rag)

### Inferences
- OpenAI's default overlap is 50% of the chunk (400 of 800), the maximum the API allows. That is a generous default. Every token outside the first and last chunk of a file is indexed in about two chunks.
- Every source agrees that chunk size, boundaries, and overlap affect retrieval. No primary source gives a universally optimal value. The numbers that exist are product defaults (OpenAI 800/400) or illustrative examples (LangChain 100/20, LlamaIndex 1024/20).
- Overlap and contextual prepending fix the same problem in different ways. Overlap keeps text that crosses a boundary. Contextual Retrieval adds document-level information that no nearby chunk contains (e.g. the company name).
- Units differ: OpenAI measures tokens, LangChain characters by default. A lesson should not compare these numbers directly.

### Gaps
- I could not confirm when OpenAI's 800/400 auto defaults were introduced. The docs show no date, and "currently" implies they may change.
- The Anthropic quotes came through WebFetch [WF]. The before/after figures (5.7% → 3.7% / 2.9% / 1.9%) were reported in the fetch output but not as one verbatim sentence. I did not fetch the alternate URL anthropic.com/engineering/contextual-retrieval.
- I did not confirm the LlamaIndex SentenceSplitter class defaults (often cited as chunk_size=1024, chunk_overlap=200) from source.
- I found no primary academic paper that systematically measures chunk size vs. overlap.

## Q2. Embeddings: provider docs (OpenAI, Google Gemini, Anthropic/Voyage, sentence-transformers)

### Takeaway
OpenAI's text-embedding-3-small and -large default to 1536 and 3072 dimensions. They can be shortened with the `dimensions` parameter, come normalized to length 1, and OpenAI recommends cosine similarity, which equals the dot product for unit vectors. Gemini's current models are `gemini-embedding-2` (April 2026, multimodal, no `task_type`) and `gemini-embedding-001` (task types such as RETRIEVAL_DOCUMENT and RETRIEVAL_QUERY). Both default to 3072 dimensions. Anthropic says it "does not offer its own embedding model" and points to Voyage AI. sentence-transformers defaults to cosine similarity and has `normalize_embeddings` (default False).

### Cited Findings

**OpenAI (developers.openai.com/api/docs/guides/embeddings; no date/version on page; verbatim from raw .md)**
- Definition: "An embedding is a vector (list) of floating point numbers." Also "The distance between two vectors measures their relatedness." — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Dimensions: "By default, the length of the embedding vector is `1536` for `text-embedding-3-small` or `3072` for `text-embedding-3-large`." — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- `dimensions` parameter: shortening works "without the embedding losing its concept-representing properties". Also "a `text-embedding-3-large` embedding can be shortened to a size of 256 while still outperforming" an unshortened 1536-dim ada-002 embedding on MTEB — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- "In general, using the `dimensions` parameter when creating the embedding is the suggested approach." If you shorten vectors yourself, "you need to be sure to normalize the dimensions of the embedding". The training technique links to arXiv 2205.13147 (Matryoshka Representation Learning) — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Distance FAQ: "We recommend cosine similarity. The choice of distance function typically doesn't matter much." Also "OpenAI embeddings are normalized to length 1". With unit vectors, "Cosine similarity can be computed slightly faster using just a dot product" and "Cosine similarity and Euclidean distance will result in the identical rankings" — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Model table: text-embedding-3-small has MTEB 62.3% and max input 8192. text-embedding-3-large has 64.6% and 8192. text-embedding-ada-002 has 61.0% and 8192 — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Knowledge cutoff caveat: the v3 models "lack knowledge of events that occurred after September 2021." — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Launch date: third-party pages give January 25, 2024 ([Vercel AI Gateway](https://vercel.com/ai-gateway/models/text-embedding-3-large/about); [Pinecone](https://www.pinecone.io/learn/openai-embeddings-v3/)). I could not fetch the OpenAI launch post itself (HTTP 403): [OpenAI blog](https://openai.com/index/new-embedding-models-and-api-updates/)

**Google Gemini (ai.google.dev/gemini-api/docs/embeddings; "Last updated 2026-10-09 UTC") [WF]**
- Models: "Stable: `gemini-embedding-2`" (latest update April 2026), the "first multimodal embedding model in the Gemini API". "Stable: `gemini-embedding-001`" (June 2025) "remains available" for text-only use — [Gemini Embeddings docs](https://ai.google.dev/gemini-api/docs/embeddings)
- Task types (gemini-embedding-001): `SEMANTIC_SIMILARITY`, `CLASSIFICATION`, `CLUSTERING`, `RETRIEVAL_DOCUMENT` ("Embeddings optimized for document search."), `RETRIEVAL_QUERY` ("Embeddings optimized for general search queries."), `CODE_RETRIEVAL_QUERY`, `QUESTION_ANSWERING`, `FACT_VERIFICATION` — [Gemini Embeddings docs](https://ai.google.dev/gemini-api/docs/embeddings)
- gemini-embedding-2 drops task_type: "You cannot use the `task_type` field for the `gemini-embedding-2` model". Task instructions go in the prompt instead, e.g. `task: search result | query: {content}` — [Gemini Embeddings docs](https://ai.google.dev/gemini-api/docs/embeddings)
- Dimensionality: "By default, both models output a 3072-dimensional embedding." "We recommend using 768, 1536, or 3072 output dimensions." gemini-embedding-2 supports 128–3072. Both models are trained with Matryoshka Representation Learning — [Gemini Embeddings docs](https://ai.google.dev/gemini-api/docs/embeddings)
- Normalization: "Gemini Embedding 2 also auto-normalizes truncated dimensions (e.g., 768, 1536)". For gemini-embedding-001, "you must manually normalize non-3072 dimensions" — [Gemini Embeddings docs](https://ai.google.dev/gemini-api/docs/embeddings)
- Input limits: 8,192 tokens for gemini-embedding-2 and 2,048 tokens for gemini-embedding-001 — [Gemini Embeddings docs](https://ai.google.dev/gemini-api/docs/embeddings)

**Anthropic (platform.claude.com/docs/en/build-with-claude/embeddings; no date shown; full page text retrieved)**
- "Anthropic does not offer its own embedding model." and "One embeddings provider with a wide variety of models and capabilities is Voyage AI by MongoDB." The page also says to "assess a variety of embeddings vendors" — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Page description: "Text embeddings are numerical representations of text that enable measuring semantic similarity." — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Current Voyage models listed: voyage-4-large, voyage-4, voyage-4-lite, and voyage-code-4, each with 32,000-token context and 1024 dimensions by default (256/512/2048 optional). voyage-4-nano is open-weight with 2048 by default. voyage-context-4 does contextualized chunk embeddings with 120,000 tokens when auto-chunking is on. voyage-3.x, voyage-law-2, and voyage-finance-2 are listed as previous generation or domain-specific — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Similarity: "Voyage AI embeddings are normalized to length 1". So "Cosine similarity is equivalent to dot-product similarity, while the latter can be computed more quickly" — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Asymmetric retrieval: "Do not omit `input_type` or set `input_type=None`." Voyage prepends the prompt "Represent the query for retrieving supporting documents: " to queries and "Represent the document for retrieval: " to documents — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)

**Hugging Face sentence-transformers (sbert.net; library v6.1.0 on PyPI as of access date; docs show no version)**
- Bi-encoder: "The bi-encoder produces embeddings independently for your paragraphs and for your search queries." [WF]. A cross-encoder receives the query and document "simultaneously"; it scores better because it performs "attention across the query and the document" [WF]. Scoring millions of pairs "would be rather slow" [WF], so the usual pattern is to retrieve with the bi-encoder and rerank with the cross-encoder — [SBERT Retrieve & Re-Rank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)
- Similarity functions: cosine is the default. Options are "cosine", "dot", "euclidean", "manhattan" [WF]. "Dot product on normalized embeddings is equivalent to cosine similarity." [WF] — [SBERT STS docs](https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html); [SentenceTransformer API](https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)
- `normalize_embeddings`: the `encode()` docstring says "Whether to normalize returned vectors to have length 1." The signature default is `normalize_embeddings: bool = False` (verbatim from source) — [sentence-transformers source, model.py](https://raw.githubusercontent.com/huggingface/sentence-transformers/main/sentence_transformers/sentence_transformer/model.py)

### Inferences
- OpenAI and Voyage vectors come normalized, so dot product, cosine, and Euclidean distance all give the same ranking. Normalization becomes the user's job when vectors are truncated by hand (OpenAI; Voyage; gemini-embedding-001 below 3072). It also applies to many open sentence-transformers models, since `normalize_embeddings` defaults to False.
- Gemini task types, Voyage `input_type`, and the gemini-embedding-2 prompt prefixes all mean query and document embeddings can be produced differently (asymmetric). A lesson should not suggest that every provider embeds queries and documents the same way.

### Gaps
- I could not fetch the OpenAI v3 launch post (403). The OpenAI guide shows no models newer than text-embedding-3-*, and I could not confirm whether OpenAI has released newer embedding models or deprecated ada-002 as of 2026-10-18.
- The Gemini figures came through WebFetch [WF]. I did not verify the Gemini deprecations page.

## Q3. Sentence-BERT (Reimers & Gurevych 2019, arXiv:1908.10084): problem and bi-encoder idea

### Takeaway
SBERT solves a cost problem. Cross-encoding BERT has to process every sentence pair jointly, so finding the most similar pair among 10,000 sentences takes about 65 hours. SBERT uses siamese and triplet networks to produce a separate embedding for each sentence. Those embeddings are compared with cosine similarity, and the same search takes about 5 seconds.

### Cited Findings
- "it requires that both sentences are fed into the network, which causes a massive computational overhead" (verbatim abstract) — [arXiv 1908.10084](https://arxiv.org/abs/1908.10084)
- "Finding the most similar pair in a collection of 10,000 sentences requires about 50 million inference computations (~65 hours) with BERT." — [arXiv 1908.10084](https://arxiv.org/abs/1908.10084)
- "The construction of BERT makes it unsuitable for semantic similarity search as well as for unsupervised tasks like clustering." — [arXiv 1908.10084](https://arxiv.org/abs/1908.10084)
- SBERT uses "siamese and triplet network structures to derive semantically meaningful sentence embeddings that can be compared using cosine-similarity." — [arXiv 1908.10084](https://arxiv.org/abs/1908.10084)
- "from 65 hours with BERT / RoBERTa to about 5 seconds with SBERT, while maintaining the accuracy from BERT." — [arXiv 1908.10084](https://arxiv.org/abs/1908.10084)
- Submitted August 27, 2019; published at EMNLP 2019 [WF] — [arXiv 1908.10084](https://arxiv.org/abs/1908.10084)

### Inferences
- "Bi-encoder" is the sentence-transformers docs' term for this architecture. The abstract itself says "siamese". The term matters for RAG because document embeddings can be computed once, offline. Only the query is embedded at search time.

### Gaps
- I read only the abstract, not the full paper (pooling strategies, training objectives).

## Q4. Is it accurate to say "semantically similar texts have embeddings that are close"? How sources phrase it

### Takeaway
Yes, broadly, and the sources say it in slightly different ways. OpenAI says "relatedness": small distance means high relatedness. Anthropic/Voyage says embeddings "enable measuring semantic similarity". SBERT says "semantically meaningful sentence embeddings" compared with cosine. A precise lesson should say "related or similar, as the model has learned it, measured by a chosen similarity function." It should not present closeness as a guaranteed property of meaning.

### Cited Findings
- "Small distances suggest high relatedness and large distances suggest low relatedness." — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- "OpenAI's text embeddings measure the relatedness of text strings." — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- "Text embeddings are numerical representations of text that enable measuring semantic similarity." — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- "derive semantically meaningful sentence embeddings that can be compared using cosine-similarity" — [arXiv 1908.10084](https://arxiv.org/abs/1908.10084)
- "The text pairs with the highest similarity score are most semantically similar." [WF] — [SBERT STS docs](https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)
- Gemini sells task-specific embeddings ("optimized to assess text similarity" vs. "optimized for document search") [WF]. So what counts as "close" depends on the task — [Gemini Embeddings docs](https://ai.google.dev/gemini-api/docs/embeddings)

### Inferences
- The claim is fair if hedged with "suggest" or "tend to", as OpenAI does. Closeness depends on the model and the task. Query–document retrieval is often asymmetric (Voyage `input_type`, Gemini RETRIEVAL_QUERY/RETRIEVAL_DOCUMENT), so "relevant" and "semantically similar" are not identical.

### Gaps
- None of the fetched sources gave a formal guarantee or a failure analysis, such as negation or numbers.

## Q5. Lexical baselines: TF-IDF and BM25 (Robertson & Zaragoza 2009)

### Takeaway
BM25 scores a document by summing, over the query terms, a term weight. Each term weight multiplies an IDF-like component (the RSJ weight) by a saturating term-frequency component. The TF part is length-normalised by b and saturates under k1. Robertson & Zaragoza say the model "provides no guidance" on these parameters. They report experiments suggesting 0.5 < b < 0.8 and 1.2 < k1 < 2. The often-quoted defaults k1 = 1.2, b = 0.75 come from Lucene/Elasticsearch, not from that paper.

### Cited Findings
- Citation: S. Robertson and H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," Foundations and Trends in Information Retrieval, Vol. 3, No. 4 (2009) 333–389, DOI 10.1561/1500000019 (from the PDF title page) — [Robertson & Zaragoza 2009 PDF](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- Saturation: "any one term's contribution to the document score cannot exceed a saturation point (the asymptotic limit), however frequently it occurs in the document" (§3.4.2) — [Robertson & Zaragoza 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- Length normalisation: B := ((1 − b) + b·dl/avdl), 0 ≤ b ≤ 1. "setting b = 1 will perform full document-length normalisation, while b = 0 will switch normalisation off" (Eq. 3.12) — [Robertson & Zaragoza 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- Formula: w_i^BM25(tf) = tf / (k1((1 − b) + b·dl/avdl) + tf) · w_i^RSJ (Eq. 3.15). The paper calls this "the classic BM25 term-weighting and document-scoring function" and says "the full document score is obtained by summing these term-weights over the ... set of query terms" — [Robertson & Zaragoza 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- Relation to TF-IDF: without relevance information, RSJ "reduces as before to a form of idf", and "the BM25 weight looks very much like a traditional tf*idf weight" except for the saturating tf (§3.5) — [Robertson & Zaragoza 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- Parameter guidance: "the model provides no guidance on how these should be set". Experiments "suggest that in general values such as 0.5 < b < 0.8 and 1.2 < k1 < 2 are reasonably good in many circumstances". Optimal values "depend on other factors (such as the type of documents or queries)" (§3.5) — [Robertson & Zaragoza 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- Published variants: "A common combination would be b = 0.5 and k1 = 2." But "many experiments suggest a somewhat lower value of k1 and a somewhat higher value of b" (§3.5.1) — [Robertson & Zaragoza 2009](https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf)
- Engineering defaults: BM25 is Elasticsearch's default similarity. k1 "Controls non-linear term frequency normalization (saturation). The default value is `1.2`." b "Controls to what degree document length normalizes tf values. The default value is `0.75`." [WF] — [Elasticsearch similarity docs](https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity)
- Anthropic's framing in a RAG context: "BM25 works by building upon the TF-IDF (Term Frequency-Inverse Document Frequency) concept." [WF] — [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- Lexical limitation, as framework docs put it: "It will not recognize synonyms, acronyms or spelling variations." [WF] — [SBERT Retrieve & Re-Rank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)

### Inferences
- "k1 in 1.2–2.0, b = 0.75" blends two sources. The k1 range comes from R&Z 2009. b = 0.75 (with k1 = 1.2) is the Lucene/Elasticsearch default, and it sits inside R&Z's 0.5–0.8 range. The lesson should cite each number to its own source.
- Excerpts from the PDF went through a custom text extraction, which drops ligatures (e.g. "signicant"). The excerpts above were lightly re-assembled (ligatures restored, spacing fixed). Pass 2 should check them against the rendered PDF.

### Gaps
- I did not fetch a primary source for TF-IDF itself (e.g. Spärck Jones 1972 on IDF).
- I did not check the Lucene BM25Similarity javadoc directly. The Elasticsearch page links to Lucene 10.0.0 javadocs, but the version is not stated.

---

### Claims table

| Claim | Source URL | Excerpt (<25 words) | Confidence |
|---|---|---|---|
| OpenAI file search default chunk = 800 tokens, overlap = 400 | https://developers.openai.com/api/docs/guides/retrieval | "By default, `max_chunk_size_tokens` is set to `800` and `chunk_overlap_tokens` is set to `400`" | High |
| Default strategy is `auto` when chunking_strategy is unset | https://developers.openai.com/api/reference/resources/vector_stores/subresources/files/methods/create | "If not set, will use the `auto` strategy." | High |
| max_chunk_size_tokens range 100–4096 | https://developers.openai.com/api/docs/guides/retrieval | "`max_chunk_size_tokens` must be between 100 and 4096 inclusive." | High |
| Overlap ≤ half of max chunk size | https://developers.openai.com/api/docs/guides/retrieval | "should not exceed `max_chunk_size_tokens / 2`." | High |
| Traditional RAG chunking loses context | https://www.anthropic.com/news/contextual-retrieval | "traditional RAG solutions remove context when encoding information" | High |
| Contextual Retrieval prepends chunk-specific context before embedding/BM25 indexing | https://www.anthropic.com/news/contextual-retrieval | "prepending chunk-specific explanatory context to each chunk before embedding" | High |
| Contextual Embeddings: −35% top-20 failure rate (5.7%→3.7%) | https://www.anthropic.com/news/contextual-retrieval | "Contextual Embeddings reduced the top-20-chunk retrieval failure rate by 35%" | High |
| + Contextual BM25: −49% (5.7%→2.9%) | https://www.anthropic.com/news/contextual-retrieval | "Combining Contextual Embeddings and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 49%" | High |
| + Reranking: −67% (5.7%→1.9%) | https://www.anthropic.com/news/contextual-retrieval | "reduced the top-20-chunk retrieval failure rate by 67%" | High |
| Metric is 1 − recall@20 | https://www.anthropic.com/news/contextual-retrieval | "We use 1 minus recall@20 as our evaluation metric" | High |
| Generated context is ~50–100 tokens per chunk | https://www.anthropic.com/news/contextual-retrieval | "usually 50-100 tokens" | Medium (WF only) |
| Chunk size/boundary/overlap affect retrieval | https://www.anthropic.com/news/contextual-retrieval | "The choice of chunk size, chunk boundary, and chunk overlap can affect retrieval performance" | High |
| Knowledge bases under 200k tokens can skip RAG | https://www.anthropic.com/news/contextual-retrieval | "smaller than 200,000 tokens (about 500 pages of material)" | High |
| LangChain recursive splitter default separators keep paragraphs/sentences together | https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter | "trying to keep all paragraphs (and then sentences, and then words) together as long as possible" | High (framework doc) |
| Overlap mitigates info loss at chunk boundaries (framework) | https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter | "Overlapping chunks helps to mitigate loss of information when context is divided between chunks." | High (framework doc) |
| Chunks too small truncate ideas, too large dilute them | https://huggingface.co/learn/cookbook/advanced_rag | "too small will truncate ideas, and too large will dilute them" | Medium (community cookbook, WF) |
| An embedding is a vector of floats; distance measures relatedness | https://developers.openai.com/api/docs/guides/embeddings | "An embedding is a vector (list) of floating point numbers." | High |
| text-embedding-3-small/large default dims 1536/3072 | https://developers.openai.com/api/docs/guides/embeddings | "the length of the embedding vector is `1536` for `text-embedding-3-small` or `3072` for `text-embedding-3-large`" | High |
| `dimensions` parameter shortens embeddings; 256-dim large beats 1536-dim ada-002 on MTEB | https://developers.openai.com/api/docs/guides/embeddings | "can be shortened to a size of 256 while still outperforming an unshortened `text-embedding-ada-002`" | High |
| OpenAI embeddings normalized to length 1 | https://developers.openai.com/api/docs/guides/embeddings | "OpenAI embeddings are normalized to length 1" | High |
| OpenAI recommends cosine similarity; dot product suffices for unit vectors | https://developers.openai.com/api/docs/guides/embeddings | "Cosine similarity can be computed slightly faster using just a dot product" | High |
| v3 models' knowledge ends Sept 2021 | https://developers.openai.com/api/docs/guides/embeddings | "lack knowledge of events that occurred after September 2021" | High |
| text-embedding-3 launched Jan 25, 2024 | https://vercel.com/ai-gateway/models/text-embedding-3-large/about | (third-party; OpenAI blog returned 403) | Medium |
| Gemini current models: gemini-embedding-2 (Apr 2026, multimodal) and gemini-embedding-001 | https://ai.google.dev/gemini-api/docs/embeddings | "first multimodal embedding model in the Gemini API" | Medium-High (WF) |
| Gemini task types incl. RETRIEVAL_DOCUMENT / RETRIEVAL_QUERY (gemini-embedding-001 only) | https://ai.google.dev/gemini-api/docs/embeddings | "You cannot use the `task_type` field for the `gemini-embedding-2` model" | Medium-High (WF) |
| Gemini default 3072 dims; recommends 768/1536/3072 | https://ai.google.dev/gemini-api/docs/embeddings | "We recommend using 768, 1536, or 3072 output dimensions." | Medium-High (WF) |
| gemini-embedding-001 needs manual normalization below 3072; -2 auto-normalizes | https://ai.google.dev/gemini-api/docs/embeddings | "you must manually normalize non-3072 dimensions" | Medium-High (WF) |
| Anthropic has no embedding model; points to Voyage AI | https://platform.claude.com/docs/en/build-with-claude/embeddings | "Anthropic does not offer its own embedding model." | High |
| Voyage embeddings normalized; cosine = dot product | https://platform.claude.com/docs/en/build-with-claude/embeddings | "Cosine similarity is equivalent to dot-product similarity, while the latter can be computed more quickly." | High |
| Voyage retrieval requires input_type query/document | https://platform.claude.com/docs/en/build-with-claude/embeddings | "Do not omit `input_type` or set `input_type=None`." | High |
| Bi-encoder embeds queries and passages independently | https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html | "The bi-encoder produces embeddings independently for your paragraphs and for your search queries." | High (WF) |
| sentence-transformers: dot on normalized embeddings = cosine; cosine default | https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html | "Dot product on normalized embeddings is equivalent to cosine similarity." | High (WF) |
| normalize_embeddings normalizes to length 1; default False | https://raw.githubusercontent.com/huggingface/sentence-transformers/main/sentence_transformers/sentence_transformer/model.py | "Whether to normalize returned vectors to have length 1." | High |
| SBERT problem: BERT needs ~50M inferences (~65 h) for 10k sentences | https://arxiv.org/abs/1908.10084 | "requires about 50 million inference computations (~65 hours) with BERT" | High |
| SBERT: siamese/triplet nets yield cosine-comparable embeddings; ~5 s | https://arxiv.org/abs/1908.10084 | "derive semantically meaningful sentence embeddings that can be compared using cosine-similarity" | High |
| "Similar texts → close embeddings" (as relatedness) | https://developers.openai.com/api/docs/guides/embeddings | "Small distances suggest high relatedness and large distances suggest low relatedness." | High (hedged phrasing) |
| BM25 tf component saturates | https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf | "any one term's contribution to the document score cannot exceed a saturation point" | High |
| b controls length normalisation (b=1 full, b=0 off) | https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf | "setting b = 1 will perform full document-length normalisation, while b = 0 will switch normalisation off" | High |
| R&Z: good ranges 0.5<b<0.8, 1.2<k1<2 | https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf | "values such as 0.5 < b < 0.8 and 1.2 < k1 < 2 are reasonably good in many circumstances" | High |
| k1=1.2, b=0.75 are Elasticsearch/Lucene defaults (not from R&Z) | https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity | "Controls to what degree document length normalizes tf values. The default value is `0.75`." | High (WF) |
| BM25 builds on TF-IDF | https://www.anthropic.com/news/contextual-retrieval | "BM25 works by building upon the TF-IDF (Term Frequency-Inverse Document Frequency) concept." | High |
| Lexical search misses synonyms/acronyms | https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html | "It will not recognize synonyms, acronyms or spelling variations." | High (WF, framework doc) |
