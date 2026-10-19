# RAG Foundations: Definition, Original Architecture, and Provider Descriptions (Pass 1, Primary Sources)

All pages were accessed on 2026-10-18. Fetching method: WebFetch. It converts each page to text, and a small model then pulls out the requested passages. The excerpts below are the quotes that tool returned as verbatim. They were not character-checked against the original PDF or HTML. **Pass 2 should spot-check every excerpt against the live page.** Where the tool paraphrased a passage, the note says so and the excerpt is not shown in quotation marks. Lewis et al. and Karpukhin et al. full-text quotes come from the ar5iv HTML rendering (ar5iv.labs.arxiv.org). Abstracts and version histories come from arxiv.org/abs.

---

## Q1. Lewis et al. 2020: what RAG is, components, models, memory, RAG-Sequence vs RAG-Token, latent-document marginalization, frozen vs fine-tuned document encoder

### Takeaway
The original RAG has two parts. A DPR bi-encoder retriever (non-parametric memory) reads from a FAISS index of 21M 100-word Wikipedia passages (Dec 2018 dump). BART-large is the generator (parametric memory). Retrieved passages are treated as a latent variable and marginalized over the top-K. There are two variants: RAG-Sequence uses one document for the whole output, and RAG-Token can use a different document for each token. Training is end-to-end, but only the query encoder and BART are fine-tuned. The document encoder and the index stay frozen.

### Cited Findings
**Source metadata**
- arXiv 2005.11401 has four versions: v1 22 May 2020, v2 7 Dec 2020, v3 29 Mar 2021, v4 12 Apr 2021 (current). The comments field says "Accepted at NeurIPS 2020". — [arXiv abs](https://arxiv.org/abs/2005.11401)
- The ar5iv page shows no version number. It may render the latest version (v4). Not confirmed. — [ar5iv full text](https://ar5iv.labs.arxiv.org/html/2005.11401)

**Definition / two memories**
- Abstract: "the parametric memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of Wikipedia" — [arXiv abs](https://arxiv.org/abs/2005.11401)
- Abstract framing: "Pre-trained models with a differentiable access mechanism to explicit non-parametric memory" — [arXiv abs](https://arxiv.org/abs/2005.11401)
- Motivation (Intro), about parametric-only models: "they cannot easily expand or revise their memory" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Generator conditioning (Intro): "then conditions on these latent documents together with the input to generate the output" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)

**Retriever (DPR)**
- "The retrieval component p_η(z|x) is based on DPR" (Sec 2.2) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- "DPR follows a bi-encoder architecture" (Sec 2.2) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- "We use a pre-trained bi-encoder from DPR to initialize our retriever and to build the document index." — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Initialization supervision: "RAG's retriever is initialized using DPR's retriever, which uses retrieval supervision on Natural Questions and TriviaQA" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Top-K search: "is a Maximum Inner Product Search (MIPS) problem, which can be approximately solved in sub-linear time" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)

**Generator (BART)**
- "We use BART-large … a pre-trained seq2seq transformer … with 400M parameters" (Sec 2.3; the tool elided citation markers) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- DPR query and document encoders are "with 110M parameters each". Total: "making a total of 626M trainable parameters" (App. G) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)

**Non-parametric memory (index)**
- "we use the December 2018 dump" (Sec 3) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- "split into disjoint 100-word chunks, to make a total of 21M documents" (Sec 3) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- "build a single MIPS index using FAISS" with "a Hierarchical Navigable Small World approximation for fast retrieval" (Sec 3) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)

**RAG-Sequence vs RAG-Token**
- RAG-Sequence: "uses the same retrieved document to generate the complete sequence" (Sec 2.1) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- RAG-Sequence: "treats the retrieved document as a single latent variable that is marginalized" "via a top-K approximation" (Sec 2.1) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- RAG-Token: "we can draw a different latent document for each target token" (Sec 2.1) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Abstract wording for RAG-Sequence: "one which conditions on the same retrieved passages across the whole generated sequence" — [arXiv abs](https://arxiv.org/abs/2005.11401)
- Decoding: RAG-Sequence uses "Thorough Decoding" (where "answers are generally short") or "Fast Decoding". RAG-Token test results use "15 retrieved documents" (App. A) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)

**K values**
- "We consider k∈{5,10} for training and set k for test time using dev data." — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)

**Document encoder: frozen**
- "keep the document encoder (and index) fixed, only fine-tuning the query encoder" [and the BART generator] (Sec 2.4) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Reason: "Updating the document encoder … is costly as it requires the document index to be periodically updated" (Sec 2.4; the ellipsis comes from the extraction tool) — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)

**Results / properties**
- Abstract: "set the state-of-the-art on three open domain QA tasks, outperforming parametric seq2seq models" — [arXiv abs](https://arxiv.org/abs/2005.11401)
- Abstract: "RAG models generate more specific, diverse and factual language than a state-of-the-art parametric-only seq2seq baseline" — [arXiv abs](https://arxiv.org/abs/2005.11401)
- Knowledge hot-swapping (Sec 4.5): "we can update RAG's world knowledge by simply replacing its non-parametric memory" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Code note (App. C): "After submission, We have ported our code to HuggingFace Transformers" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2005.11401)

### Inferences
- In the original paper, "RAG" names a specific trained model: retriever and generator are fine-tuned jointly with a marginal-likelihood objective. In most modern provider usage, "RAG" means a looser pattern. An off-the-shelf embedding model plus a vector store retrieves chunks, the chunks are pasted into an LLM prompt, and nothing is trained jointly. Lessons should keep these two meanings separate. See Q3–Q5 for the modern usage.
- Because the document encoder was frozen, the 21M-passage index only needed to be built once. That design choice is what made end-to-end training practical at this scale.
- Passage length is given in words (100 words), not tokens. Modern provider defaults are in tokens (for example, OpenAI's 800). They are not directly comparable.

### Gaps
- I did not character-check the quotes against the NeurIPS proceedings PDF (proceedings.neurips.cc). I did not fetch it.
- The exact HNSW/FAISS parameters and the index memory footprint were not extracted.
- The exact training objective equations (the p_RAG-Sequence and p_RAG-Token formulas) were not quoted. Pass 2 should take them from Sec 2.1 of the PDF if needed.

---

## Q2. Karpukhin et al. 2020: Dense Passage Retrieval (DPR)

### Takeaway
DPR is a dual (bi-)encoder: two independent BERT encoders whose [CLS] vectors are scored by inner (dot) product. It indexes about 21M 100-word Wikipedia passages (Dec 20, 2018 dump) with FAISS. Training uses in-batch negatives. It beats Lucene-BM25 by 9–19% absolute top-20 passage retrieval accuracy.

### Cited Findings
- arXiv 2004.04906 has three versions: v1 10 Apr 2020, v2 2 May 2020, v3 30 Sep 2020 (current). The comments field says "EMNLP 2020". — [arXiv abs](https://arxiv.org/abs/2004.04906)
- Abstract: "embeddings are learned from a small number of questions and passages by a simple dual-encoder framework." — [arXiv abs](https://arxiv.org/abs/2004.04906)
- Design: uses "two independent BERT" networks and takes "the representation at the [CLS] token as the output." — [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.04906)
- Similarity: "we thus choose the simpler inner product function". The paper's reason is that the other similarity functions it tried performed comparably (the reason is paraphrased). — [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.04906)
- Passage size: "split each article into multiple, disjoint text blocks of 100 words" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.04906)
- Corpus: English Wikipedia dump from "Dec. 20, 2018", "which results in 21,015,324 passages in the end." — [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.04906)
- vs BM25 (arXiv abstract, v3): "outperforms a strong Lucene-BM25 system largely by 9%-19% absolute" in top-20 passage retrieval accuracy — [arXiv abs](https://arxiv.org/abs/2004.04906). **Wording conflict:** the ar5iv rendering returned "greatly by 9%-19% absolute in terms of top-20 passage retrieval accuracy" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.04906). The numbers agree. The adverb differs, possibly because the two pages render different versions or the extraction tool slipped. Quote the arxiv.org/abs wording ("largely").
- Indexing: FAISS is "an extremely efficient, open-source library for similarity search and clustering of dense vectors." — [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.04906)
- Training: "in-batch negative training is an easy and memory-efficient way to reuse the negative examples" — [ar5iv](https://ar5iv.labs.arxiv.org/html/2004.04906)

### Inferences
- RAG's index (21M 100-word passages, Dec 2018 Wikipedia) matches DPR's corpus setup, which fits RAG's statement that it uses DPR's pre-trained bi-encoder "to build the document index". This is an inference from both papers. Neither paper states the match in a quote I extracted.
- Dot-product scoring over separately encoded queries and passages is what lets passages be pre-encoded offline and searched with MIPS. This is the same structure modern embedding and vector-store pipelines use.

### Gaps
- The per-dataset top-20/top-100 accuracy table (NQ, TriviaQA, WebQ, CuratedTREC, SQuAD) was not extracted.
- The hard-negative (BM25 negative) details were not extracted.

---

## Q3. Anthropic: how it describes RAG, its steps, and embeddings providers

### Takeaway
Anthropic's "Introducing Contextual Retrieval" (Sep 19, 2024) defines RAG as retrieving from a knowledge base and appending the results to the prompt. It describes a chunk → embed → vector DB (+ BM25) → top-K → prompt pipeline. It names context loss from chunking as the main failure mode. Its fix (Contextual Embeddings plus Contextual BM25, with reranking) cut top-20 retrieval failures by up to 67%. Anthropic's docs state it has no embedding model of its own and point to Voyage AI (by MongoDB). Current Voyage recommendations are the voyage-4 family.

### Cited Findings
**Contextual Retrieval post** (published Sep 19, 2024; fetched at anthropic.com/news/contextual-retrieval, which returned content. Whether it redirects to /engineering/ is not known.)
- Definition: "RAG is a method that retrieves relevant information from a knowledge base and appends it to the user's prompt" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Step 1: "Break down the knowledge base (the “corpus” of documents) into smaller chunks of text", "usually no more than a few hundred tokens" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Step 2: "Use an embedding model to convert these chunks into vector embeddings that encode meaning" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Step 3: "Store these embeddings in a vector database that allows for searching by semantic similarity" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Hybrid step: "Use BM25 to find top chunks based on exact matches" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Final step: "Add the top-K chunks to the prompt to generate the response." — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Failure mode: traditional RAG solutions "remove context when encoding information" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Method: prepend "chunk-specific explanatory context to each chunk before embedding" (also applied to the BM25 index) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Result: "Contextual Embeddings reduced the top-20-chunk retrieval failure rate by 35%" (5.7%→3.7%) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Result: "Combining Contextual Embeddings and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 49%" (5.7%→2.9%) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Result: "Reranked Contextual Embedding and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 67%" (5.7%→1.9%) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- No-RAG alternative for small corpora (under 200,000 tokens): "you can just include the entire knowledge base in the prompt that you give the model" (prompt caching makes this faster and cheaper; paraphrased) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Top-K: "Passing the top-20 chunks to the model is more effective than just the top-10 or top-5" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Embedding models: "We found Gemini and Voyage embeddings to be particularly effective." — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Limits on adding context: "more information can be distracting for models so there's a limit to this"; reranking "inevitably adds a small amount of latency" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- The post's cost example assumes 800-token chunks. Context was generated with Claude 3 Haiku, and only the Cohere reranker was tested (paraphrased by the extraction tool) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)

**Embeddings doc** (docs.claude.com/en/docs/build-with-claude/embeddings returns 302 to platform.claude.com/docs/en/build-with-claude/embeddings; no date shown on the page)
- "Anthropic does not offer its own embedding model." — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- "One embeddings provider with a wide variety of models and capabilities is Voyage AI by MongoDB." — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Hedge: "you should assess a variety of embeddings vendors to find the best fit for your specific use case." — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Recommended general-purpose models: "`voyage-4-large`: Best quality", "`voyage-4-lite`: Lowest latency and cost", "`voyage-4`: Balanced performance". All have 32,000-token context and 1024 dimensions by default. — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Also listed: voyage-code-4, voyage-context-4 ("For chunk-level and document-level retrieval"), voyage-multimodal-3.5, and rerankers rerank-3 / rerank-3-lite — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- RAG usage note: "For all retrieval tasks and use cases (for example, RAG), use the `input_type` parameter to specify whether the input text is a query or document." — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Similarity: "Voyage AI embeddings are normalized to length 1"; "Cosine similarity is equivalent to dot-product similarity" — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Access: API keys are now created in MongoDB Atlas ("AI Model APIs"), endpoint ai.mongodb.com — [Claude Docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)

**Search results content blocks** (platform.claude.com; no date shown)
- "Use them in RAG (Retrieval-Augmented Generation) applications where Claude needs to attribute answers to your documents." — [Claude Docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)
- Two input paths: "From tool calls: Your custom tools return search results, enabling dynamic RAG applications", or "As top-level content" — [Claude Docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)
- Status: "No beta header is required: search results are part of the standard Messages API." Claude Haiku 3 is the exception. — [Claude Docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)

### Inferences
- **Outdated/provider-specific flags.** The Contextual Retrieval post is from 2024 and its experiments used Claude 3 Haiku and older Voyage/Gemini embeddings. The method still holds, but the specific numbers belong to that setup. Voyage model names change quickly: the 2024 voyage-2/3 generations have been replaced by voyage-4 (Jan 2026 per the linked blog URLs). Voyage is now presented as "Voyage AI by MongoDB" with Atlas keys. Older tutorials that use dash.voyageai.com keys may be stale.
- Anthropic's docs present RAG as something the developer builds, with the developer's own retrieval passed in through tools or search_result blocks. Claude docs did not describe a hosted vector store comparable to OpenAI's.

### Gaps
- I did not fetch a dedicated Claude Docs page explaining "RAG" as a concept, if one exists (for example, prompt-engineering or "reduce hallucinations" pages). The Claude Cookbook RAG recipe (linked from the embeddings page) was not fetched.
- I did not confirm whether anthropic.com/engineering/contextual-retrieval is now the canonical URL.

---

## Q4. OpenAI: retrieval pipeline, file search, vector stores, and default chunking

### Takeaway
OpenAI documents a hosted pipeline: upload files to a vector store, where they are automatically chunked, embedded, and indexed. Retrieval is hybrid semantic plus keyword search (reciprocal rank fusion) with optional query rewriting, used by the `file_search` tool and the Retrieval API. **The default chunking is `max_chunk_size_tokens` = 800 and `chunk_overlap_tokens` = 400**, documented on the Retrieval guide, not on the File Search tool page.

### Cited Findings
- URL migration: platform.openai.com/docs/guides/tools-file-search returns 301 to developers.openai.com/api/docs/guides/tools-file-search. — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- File search: lets models "retrieve information in a knowledge base of previously uploaded files through semantic and keyword search." — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- Steps (paraphrased by the tool): upload a file to the Files API → create a vector store → add the file → poll until status "completed" → pass the `file_search` tool and vector_store_ids to the Responses API — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- `max_num_results`: you can "customize the number of results you want to retrieve from the vector stores". Fewer results "may come at the cost of reduced answer quality." — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- Citations: output text contains "annotations (references to files)" of type `file_citation`. Raw results are only returned if you include `file_search_call.results`. — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- The File search page shows no chunk-size defaults and no date. — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- Retrieval API: "allows you to perform semantic search over your data." — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- "Vector stores are the containers that power semantic search for the Retrieval API and the file search tool." — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- **Defaults:** "`max_chunk_size_tokens` is set to `800` and `chunk_overlap_tokens` is set to `400`." — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- Bounds: "`max_chunk_size_tokens` must be between 100 and 4096 inclusive"; "`chunk_overlap_tokens` must be non-negative and should not exceed `max_chunk_size_tokens / 2`." — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- Limits: "The maximum file size is 512 MB"; "no more than 5,000,000 tokens per file" — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- Query rewriting: "we've provided a setting to automatically rewrite your queries for optimal performance" (`rewrite_query=true`) — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- Hybrid ranking: you can "control how reciprocal rank fusion balances semantic embedding matches vs. sparse keyword matches." Ranker ID `default-2024-08-21` appears on the page. — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- Embeddings: "An embedding is a vector (list) of floating point numbers." Default dimension is 1536 for text-embedding-3-small (3072 for -large), with a max input of 8192 tokens. — [OpenAI Embeddings](https://developers.openai.com/api/docs/guides/embeddings)
- Similarity: "We recommend cosine similarity"; "OpenAI embeddings are normalized to length 1" — [OpenAI Embeddings](https://developers.openai.com/api/docs/guides/embeddings)
- Scale: "For searching over many vectors quickly, we recommend using a vector database." The page has a section "Question answering using embeddings-based search" but does not use the term "RAG." — [OpenAI Embeddings](https://developers.openai.com/api/docs/guides/embeddings)

### Inferences
- The 800/400 default means 50% overlap, the maximum the docs allow (overlap ≤ max/2). This is my arithmetic, not a doc statement.
- **Provider-specific/outdated flags.** Older Assistants-API (v2) file search docs also listed 800/400. The Assistants API path is legacy. The current pages are under developers.openai.com/api/docs and the Responses API. Older platform.openai.com links now redirect.
- OpenAI's embeddings page still says the v3 models lack knowledge of events "after September 2021". That is a statement about the models' training data, not the page date.

### Gaps
- None of the OpenAI pages showed a "last updated" date. Pass 2 should record a snapshot (for example, the Wayback Machine) if a date is needed.
- The default `max_num_results` for file_search (often cited as 10 or 20 elsewhere) was **not** confirmed on the fetched pages. The example only shows 2.

---

## Q5. Google: Gemini API (ai.google.dev) and Vertex AI / "RAG Engine" descriptions of RAG and grounding

### Takeaway
Google describes RAG in two places. The Gemini API's hosted File Search tool ("enables Retrieval Augmented Generation") auto-chunks, embeds, and indexes files and returns citation annotations. Cloud RAG Engine documents a six-step pipeline: ingestion → transformation/chunking → embedding → indexing → retrieval → generation. Google uses "grounding" for basing answers on retrieved content, including web results via Grounding with Google Search.

### Cited Findings
**Gemini API File Search** (page shows "Last updated 2026-10-13 UTC")
- "The Gemini API enables Retrieval Augmented Generation ("RAG") through the File Search tool." — [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)
- On import, a file is "automatically broken down into chunks, embedded, indexed, and uploaded" — [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)
- `chunking_config` accepts `max_tokens_per_chunk` and `max_overlap_tokens`. The examples use 200 and 20, which are **sample values, not stated defaults** (paraphrased by the tool). — [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)
- Embedding model in examples: `models/gemini-embedding-2`. gemini-embedding-001 is also mentioned for text. — [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)
- Limits (paraphrased): not supported in the Live API; "File Search cannot be used simultaneously with Grounding with Google Search"; 100 MB maximum per document; stores recommended under 20 GB — [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)
- Pricing (paraphrased): indexing embeddings are charged; storage and query-time embeddings are free; retrieved tokens are billed as context — [Gemini File Search](https://ai.google.dev/gemini-api/docs/file-search)

**Grounding with Google Search** (page shows "Last updated 2026-10-13 UTC")
- It "connects the Gemini model to real-time web content" — [Gemini Google Search grounding](https://ai.google.dev/gemini-api/docs/google-search)
- "Reduce model hallucinations by basing responses on real-world information." — [Gemini Google Search grounding](https://ai.google.dev/gemini-api/docs/google-search)
- "cite verifiable sources beyond its knowledge cutoff" — [Gemini Google Search grounding](https://ai.google.dev/gemini-api/docs/google-search)
- The model "automatically generates one or multiple search queries and executes them". The API returns a response "grounded in the search results." — [Gemini Google Search grounding](https://ai.google.dev/gemini-api/docs/google-search)
- "Older models use a `google_search_retrieval` tool." Current responses expose `annotations` with `url_citation` (start_index/end_index/url/title), not the older `groundingMetadata` naming. — [Gemini Google Search grounding](https://ai.google.dev/gemini-api/docs/google-search)

**Google Cloud RAG Engine** (cloud.google.com/... returns 301 to docs.cloud.google.com/...; page shows "Last updated 2026-10-16 UTC")
- **Naming flag:** the page now says "RAG Engine, a component of Gemini Enterprise Agent Platform, facilitates Retrieval-Augmented Generation (RAG)." It does not say "Vertex AI RAG Engine." — [Google Cloud RAG Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- "RAG Engine is also a data framework for developing context-augmented large language model (LLM) applications." — [Google Cloud RAG Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- Steps: ingestion ("Ingest data from different data sources"); transformation ("data is split into chunks"); embedding ("Numerical representations of words or pieces of text"); indexing ("structures the knowledge base so it's optimized for searching"); retrieval ("find information that is relevant to the query"); generation ("The retrieved information becomes the context added to the original user query.") — [Google Cloud RAG Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- Motivation: "A common problem with LLMs is that they don't understand private knowledge, that is, your organization's data." — [Google Cloud RAG Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- Benefit: "the model can reduce hallucinations and answer questions more accurately." — [Google Cloud RAG Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- Restrictions: "You must be added to the allowlist to access RAG Engine in" [some contexts; sentence cut off by the tool]; "Data residency and AXT security controls aren't supported." — [Google Cloud RAG Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- No default chunk size or overlap is stated on the overview page. — [Google Cloud RAG Engine overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)

### Inferences
- Google's six-step list is the clearest "modern pipeline" statement among the three providers and works well as the canonical lesson diagram. Anthropic's post gives nearly the same steps plus BM25 hybrid search.
- In Google's docs, "grounding" is the broader idea (basing answers on external sources, web or private), and RAG is one way to do it. This is my inference from how the pages use the terms.
- **Naming/outdated flag.** Materials that say "Vertex AI RAG Engine" or use cloud.google.com URLs may now be out of date because of the rebrand and domain move. Confirm before publishing.

### Gaps
- The RAG Engine default chunking values (if any) are probably on a separate "chunking/transformation" page, which I did not fetch.
- The allowlist sentence was truncated by the extraction tool. Its exact scope (which projects or regions need allowlisting) is unknown.

---

## Q6. What sources say RAG is good for, and its known limitations

### Takeaway
Across sources, RAG helps with four things: factuality and specificity (Lewis et al.), updating knowledge without retraining, access to private or post-cutoff data, and citable answers (providers). Documented limitations: retrieval can fail (Anthropic measured a 5.7% top-20 failure rate for a baseline setup), chunking loses context, extra context can distract the model, reranking adds latency, smaller K lowers answer quality, sources can be wrong, and the original paper does not claim RAG removes hallucination.

### Cited Findings
**Good for**
- Fewer hallucinations: "RAG models hallucinate less and generate factually correct text more often than BART" (Sec 4.2) — [ar5iv RAG](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Updatable knowledge: "we can update RAG's world knowledge by simply replacing its non-parametric memory" — [ar5iv RAG](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Private data: "they don't understand private knowledge, that is, your organization's data." — [Google Cloud RAG Engine](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview)
- Post-cutoff knowledge and citations: "cite verifiable sources beyond its knowledge cutoff" — [Gemini grounding](https://ai.google.dev/gemini-api/docs/google-search)
- Attribution: search result blocks let Claude "attribute answers to your documents" — [Claude Docs: Search results](https://platform.claude.com/docs/en/build-with-claude/search-results)

**Limitations**
- Hallucination is reduced, not eliminated. Broader Impact says RAG makes the model "'hallucinate' less", and generation grounded in Wikipedia "will probably never be entirely factual" — [ar5iv RAG](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Misuse: "it might be used to generate abuse, faked or misleading content in the news or on social media" — [ar5iv RAG](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Retriever training failure: the retrieval component can "collapse" and "learn to retrieve the same documents regardless of the input" (seen on some tasks in the paper) — [ar5iv RAG](https://ar5iv.labs.arxiv.org/html/2005.11401)
- Retrieval failures in practice: baseline top-20 retrieval failure rate of 5.7% (Anthropic's eval) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Context loss from chunking: traditional RAG "remove[s] context when encoding information" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Too much context: "more information can be distracting for models so there's a limit to this" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Latency: reranking "inevitably adds a small amount of latency" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Recall vs cost: lowering max_num_results "may come at the cost of reduced answer quality." — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- RAG may be unnecessary: for knowledge bases under 200k tokens, "you can just include the entire knowledge base in the prompt" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)

### Inferences
- Lessons should say "RAG reduces but does not eliminate hallucination". No primary source here claims elimination.
- A retrieval miss is a separate failure from a generation error. The generator cannot cite or use a passage it never received. Anthropic's metric (retrieval failure rate at top-20) measures only the retrieval stage.

### Gaps
- No provider page fetched here gives a quantitative end-to-end hallucination rate for its RAG product.
- I did not fetch independent evaluations (for example, papers on "lost in the middle" or RAG faithfulness). They are outside this primary-source pass.

---

## Claims table

| # | Claim | Source URL | Excerpt (<25 words) | Confidence |
|---|---|---|---|---|
| 1 | RAG paper: arXiv v1 22 May 2020, latest v4 12 Apr 2021; accepted at NeurIPS 2020 | https://arxiv.org/abs/2005.11401 | "Accepted at NeurIPS 2020" | high |
| 2 | Parametric memory = pre-trained seq2seq; non-parametric = dense vector index of Wikipedia | https://arxiv.org/abs/2005.11401 | "the parametric memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of Wikipedia" | high |
| 3 | Retriever is DPR (bi-encoder) | https://ar5iv.labs.arxiv.org/html/2005.11401 | "The retrieval component p_η(z|x) is based on DPR" | high |
| 4 | Generator is BART-large, 400M params | https://ar5iv.labs.arxiv.org/html/2005.11401 | "We use BART-large … a pre-trained seq2seq transformer … with 400M parameters" | high |
| 5 | 626M trainable params total; DPR encoders 110M each | https://ar5iv.labs.arxiv.org/html/2005.11401 | "making a total of 626M trainable parameters" | medium (appendix, not cross-checked with PDF) |
| 6 | Index: Dec 2018 Wikipedia, 100-word chunks, 21M docs | https://ar5iv.labs.arxiv.org/html/2005.11401 | "split into disjoint 100-word chunks, to make a total of 21M documents" | high |
| 7 | Index built with FAISS MIPS + HNSW | https://ar5iv.labs.arxiv.org/html/2005.11401 | "build a single MIPS index using FAISS" | high |
| 8 | RAG-Sequence uses one document for the whole output | https://ar5iv.labs.arxiv.org/html/2005.11401 | "uses the same retrieved document to generate the complete sequence" | high |
| 9 | RAG-Token can use a different document per token | https://ar5iv.labs.arxiv.org/html/2005.11401 | "we can draw a different latent document for each target token" | high |
| 10 | Retrieved document is a latent variable, marginalized via top-K | https://ar5iv.labs.arxiv.org/html/2005.11401 | "treats the retrieved document as a single latent variable that is marginalized" | high |
| 11 | Training k ∈ {5,10}; test k tuned on dev | https://ar5iv.labs.arxiv.org/html/2005.11401 | "We consider k∈{5,10} for training and set k for test time using dev data." | high |
| 12 | Document encoder and index frozen; only query encoder (and BART) fine-tuned | https://ar5iv.labs.arxiv.org/html/2005.11401 | "keep the document encoder (and index) fixed, only fine-tuning the query encoder" | high |
| 13 | Reason: updating doc encoder requires costly index rebuilds | https://ar5iv.labs.arxiv.org/html/2005.11401 | "is costly as it requires the document index to be periodically updated" | high |
| 14 | Knowledge can be updated by swapping the index | https://ar5iv.labs.arxiv.org/html/2005.11401 | "we can update RAG's world knowledge by simply replacing its non-parametric memory" | high |
| 15 | RAG hallucinates less than BART, not zero | https://ar5iv.labs.arxiv.org/html/2005.11401 | "RAG models hallucinate less and generate factually correct text more often than BART" | high |
| 16 | DPR: v3 30 Sep 2020; EMNLP 2020 | https://arxiv.org/abs/2004.04906 | "EMNLP 2020" | high |
| 17 | DPR uses two independent BERT encoders ([CLS] output) | https://ar5iv.labs.arxiv.org/html/2004.04906 | "two independent BERT" … "representation at the [CLS] token as the output" | high |
| 18 | DPR similarity = inner (dot) product | https://ar5iv.labs.arxiv.org/html/2004.04906 | "we thus choose the simpler inner product function" | high |
| 19 | DPR passages are 100 words; 21,015,324 passages from Dec 20, 2018 dump | https://ar5iv.labs.arxiv.org/html/2004.04906 | "which results in 21,015,324 passages in the end." | high |
| 20 | DPR beats BM25 by 9–19% absolute top-20 accuracy | https://arxiv.org/abs/2004.04906 | "outperforms a strong Lucene-BM25 system largely by 9%-19% absolute" | high (ar5iv returned "greatly"; use abs wording) |
| 21 | DPR trained with in-batch negatives | https://ar5iv.labs.arxiv.org/html/2004.04906 | "in-batch negative training is an easy and memory-efficient way to reuse the negative examples" | high |
| 22 | Anthropic defines RAG as retrieval appended to the prompt | https://www.anthropic.com/news/contextual-retrieval | "RAG is a method that retrieves relevant information from a knowledge base and appends it to the user's prompt" | high |
| 23 | Anthropic's traditional RAG pipeline: chunk, embed, vector DB, BM25, top-K into prompt | https://www.anthropic.com/news/contextual-retrieval | "Add the top-K chunks to the prompt to generate the response." | high |
| 24 | Contextual Embeddings + BM25 + reranking cut top-20 failure rate 67% (5.7%→1.9%) | https://www.anthropic.com/news/contextual-retrieval | "reduced the top-20-chunk retrieval failure rate by 67%" | high (2024 setup-specific) |
| 25 | Under 200k tokens, Anthropic suggests skipping RAG | https://www.anthropic.com/news/contextual-retrieval | "you can just include the entire knowledge base in the prompt that you give the model" | high |
| 26 | Anthropic has no embedding model and points to Voyage AI by MongoDB | https://platform.claude.com/docs/en/build-with-claude/embeddings | "Anthropic does not offer its own embedding model." | high |
| 27 | Current Voyage recommendations: voyage-4-large / voyage-4 / voyage-4-lite | https://platform.claude.com/docs/en/build-with-claude/embeddings | "`voyage-4-large`: Best quality" | high (fast-changing) |
| 28 | Claude search_result blocks are for RAG citations; GA (no beta header) | https://platform.claude.com/docs/en/build-with-claude/search-results | "No beta header is required: search results are part of the standard Messages API." | high |
| 29 | OpenAI file search = semantic + keyword search over uploaded files | https://developers.openai.com/api/docs/guides/tools-file-search | "retrieve information in a knowledge base of previously uploaded files through semantic and keyword search." | high |
| 30 | OpenAI default chunking: 800 max tokens, 400 overlap | https://developers.openai.com/api/docs/guides/retrieval | "`max_chunk_size_tokens` is set to `800` and `chunk_overlap_tokens` is set to `400`." | high |
| 31 | OpenAI chunk bounds: 100–4096; overlap ≤ max/2 | https://developers.openai.com/api/docs/guides/retrieval | "`max_chunk_size_tokens` must be between 100 and 4096 inclusive" | high |
| 32 | OpenAI hybrid ranking via reciprocal rank fusion | https://developers.openai.com/api/docs/guides/retrieval | "reciprocal rank fusion balances semantic embedding matches vs. sparse keyword matches" | medium (single extraction) |
| 33 | OpenAI embeddings normalized; cosine recommended | https://developers.openai.com/api/docs/guides/embeddings | "OpenAI embeddings are normalized to length 1" | high |
| 34 | Gemini API: File Search tool enables RAG (auto chunk/embed/index) | https://ai.google.dev/gemini-api/docs/file-search | "The Gemini API enables Retrieval Augmented Generation ("RAG") through the File Search tool." | high |
| 35 | Gemini File Search can't be combined with Google Search grounding | https://ai.google.dev/gemini-api/docs/file-search | "File Search cannot be used simultaneously with Grounding with Google Search" | medium |
| 36 | Google Search grounding reduces hallucinations and cites post-cutoff sources | https://ai.google.dev/gemini-api/docs/google-search | "Reduce model hallucinations by basing responses on real-world information." | high |
| 37 | Google Cloud RAG Engine now branded as part of "Gemini Enterprise Agent Platform" | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview | "RAG Engine, a component of Gemini Enterprise Agent Platform, facilitates Retrieval-Augmented Generation (RAG)." | medium (rebrand; verify) |
| 38 | RAG Engine pipeline: ingest, transform/chunk, embed, index, retrieve, generate | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview | "The retrieved information becomes the context added to the original user query." | high |
| 39 | Google: RAG addresses LLMs' lack of private knowledge | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview | "A common problem with LLMs is that they don't understand private knowledge" | high |
| 40 | OpenAI file_search default max_num_results | (not confirmed) | not found on fetched pages | low / unverified |
| 41 | Gemini File Search default chunk size/overlap | https://ai.google.dev/gemini-api/docs/file-search | not stated (200/20 are example values) | low / unverified |
