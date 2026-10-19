# RAG Retrieval, Reranking, and Prompt Grounding: Primary-Source Notes (Pass 1)

All sources accessed 2026-10-18. Excerpts are verbatim, and each is under 25 words. Where a page redirected, the final URL is given. "Version/date" is whatever the page or paper shows. A few excerpts came through a fetch tool that summarises pages; those are marked "(fetch-tool quote)" and should be checked against the live page in Pass 2. Excerpts from the RRF paper, the Lost in the Middle PDF, and the Anthropic docs pages were read from the full source text.

## Q1. Nearest-neighbour search: exact (flat / brute-force) k-NN vs ANN; HNSW; FAISS flat indexes; inner product vs cosine

### Takeaway
Exact k-NN compares the query with every stored vector. FAISS calls its flat indexes "Exact Search" and marks them "brute-force". ANN indexes such as HNSW give up exhaustiveness for speed: HNSW builds a hierarchy of proximity-graph layers and starts its search at the top layer. Its authors claim this gives "logarithmic complexity scaling". Cosine similarity in FAISS means inner-product search over L2-normalized vectors, with both the stored vectors and the queries normalized.

### Cited Findings
**HNSW paper (Malkov & Yashunin), arXiv:1603.09320. v1 30 Mar 2016; current v4 14 Aug 2018. The arXiv page lists no journal ref.**
- Title: "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs". So HNSW is explicitly an *approximate* NN method. — [arXiv 1603.09320](https://arxiv.org/abs/1603.09320)
- Structure: "Hierarchical NSW incrementally builds a multi-layer structure consisting from hierarchical set of proximity graphs (layers)" (fetch-tool quote) — [arXiv 1603.09320](https://arxiv.org/abs/1603.09320)
- It is related to the earlier NSW: "This allows producing graphs similar to the previously studied Navigable Small World (NSW) structures" (fetch-tool quote) — [arXiv 1603.09320](https://arxiv.org/abs/1603.09320)
- Search procedure and complexity claim: "Starting search from the upper layer together with utilizing the scale separation boosts the performance compared to NSW" and "allows a logarithmic complexity scaling" (fetch-tool quote) — [arXiv 1603.09320](https://arxiv.org/abs/1603.09320)

**FAISS paper (Johnson, Douze, Jégou), "Billion-scale similarity search with GPUs", arXiv:1702.08734. v1 28 Feb 2017. No journal ref shown on the arXiv page.**
- Scope: the abstract says the paper proposes optimized designs for brute-force, approximate, and compressed-domain (product quantization) search on GPUs, with k-selection at up to 55% of theoretical peak and an 8.5x speed-up over the prior GPU state of the art. (Paraphrase of fetch-tool output; the verbatim quote was not captured.) — [arXiv 1702.08734](https://arxiv.org/abs/1702.08734)
- Scale: k-NN graph built on "95 million images from the Yfcc100M dataset" in 35 minutes. A graph over 1 billion vectors took under 12 hours on 4 Maxwell Titan X GPUs. (Partly paraphrased.) — [arXiv 1702.08734](https://arxiv.org/abs/1702.08734)

**FAISS wiki (github.com/facebookresearch/faiss/wiki)**
- Getting started (last edited 28 Jun 2020): IndexFlatL2 is "the simplest version that just performs brute-force L2 distance search on them"; for training, "For `IndexFlatL2`, we can skip this operation." — [FAISS wiki: Getting started](https://github.com/facebookresearch/faiss/wiki/Getting-started)
- Faiss indexes summary table (last edited 28 Jul 2025): IndexFlatL2 is "Exact Search for L2" (comment "brute-force"); IndexFlatIP is "Exact Search for Inner Product", "also for cosine (normalize vectors beforehand)"; IndexHNSWFlat is "Hierarchical Navigable Small World graph exploration", Exhaustive: "no". (Fetch-tool output of a flattened table.) — [FAISS wiki: Faiss indexes](https://github.com/facebookresearch/faiss/wiki/Faiss-indexes)
- MetricType and distances (last edited 3 Dec 2024): METRIC_INNER_PRODUCT "is not by itself cosine similarity, unless the vectors are normalized". For cosine, "build an index with `METRIC_INNER_PRODUCT`", "normalize the vectors prior to adding them to the index (with `faiss.normalize_L2` in Python)", and "normalize the vectors prior to searching them". (fetch-tool quotes) — [FAISS wiki: MetricType and distances](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)
- The same page gives the identity for normalized vectors: |x − y|² = 2 − 2⟨x, y⟩, so L2 and inner-product rankings agree on normalized data. (Paraphrase of fetch-tool output.) — [FAISS wiki: MetricType and distances](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)
- METRIC_INNER_PRODUCT "is typically used for maximum inner product search in recommendation systems." (fetch-tool quote) — [FAISS wiki: MetricType and distances](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)

### Inferences
- "Top-k" retrieval in RAG means returning the k vectors with the highest similarity (or smallest distance). A flat index returns the true top-k because it scores every vector, which the FAISS table labels exhaustive. An ANN index such as HNSW may miss some of the true neighbours in exchange for speed. The trade-off is recall vs latency, which the "Exhaustive: no" label for HNSW implies.
- The "logarithmic" claim is the authors' own abstract-level claim. These notes have not checked whether the paper presents it as an empirical or average-case result rather than a worst-case guarantee, so a lesson should attribute it ("the authors report...") and not state it as a proven bound.
- If you use IndexFlatIP for cosine and forget to normalize either the stored vectors or the queries, results are no longer cosine-ranked. This is an easy failure mode to teach.

### Gaps
- I did not fetch the full HNSW paper body, so its exact complexity analysis (e.g., the assumptions behind the logarithmic scaling, or the parameters M and efConstruction/efSearch) is not verified.
- The FAISS arXiv abstract was not captured as one verbatim block (the fetch tool would only return fragments). The newer "The Faiss library" paper (Douze et al., 2024, arXiv 2401.08281) was not consulted.
- The FAISS Getting-started page does not itself use the word "exact". The word "exact" comes from the Faiss-indexes summary table.

## Q2. Hybrid lexical + dense search, rank fusion, and reranking (Anthropic Contextual Retrieval; RRF)

### Takeaway
Anthropic's Contextual Retrieval post (19 Sep 2024) runs BM25 and embedding search separately, merges and deduplicates the results "using rank fusion techniques", retrieves the top 150 chunks, reranks them with a Cohere reranker, and keeps the top 20. Measured as 1 − recall@20, the reported failure-rate reductions are 35%, 49%, and 67% (5.7% → 3.7% → 2.9% → 1.9%). RRF (Cormack, Clarke & Büttcher, SIGIR 2009) scores each document as the sum of 1/(k + rank) across rankings, with k = 60.

### Cited Findings
**Anthropic, "Introducing Contextual Retrieval", "Published Sep 19, 2024"** — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Hybrid steps: "Use BM25 to find top chunks based on exact matches;" and "Use embeddings to find top chunks based on semantic similarity;" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Fusion: "Combine and deduplicate results from (3) and (4) using rank fusion techniques;" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Reranking: "Using a reranking model, give each chunk a score based on its relevance and importance to the prompt"; "We ran our tests with the Cohere reranker" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- K values: initial retrieval of "the top potentially relevant chunks (we used the top 150)", then rerank and keep "(we used the top 20)". — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Metric: "We use 1 minus recall@20 as our evaluation metric" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Results: "Contextual Embeddings reduced the top-20-chunk retrieval failure rate by 35%" (5.7% → 3.7%) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- "Combining Contextual Embeddings and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 49%" (5.7% → 2.9%) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- "Reranked Contextual Embedding and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 67%" (5.7% → 1.9%) — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Contextualization: Claude 3 Haiku prepends chunk-specific context; "The resulting contextual text, usually 50-100 tokens". Prompt: "Please give a short succinct context to situate this chunk within the overall document" — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)
- Small-corpus caveat: "If your knowledge base is smaller than 200,000 tokens (about 500 pages of material)," the post says you can put the whole knowledge base in the prompt instead of using RAG. — [Anthropic](https://www.anthropic.com/news/contextual-retrieval)

**Cormack, Clarke, Büttcher, "Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods", SIGIR'09, 19–23 Jul 2009, Boston, pp. 758–759, DOI 10.1145/1571941.1572114.** Read from the authors' PDF. The DOI and page numbers come from search results (ir.webis.de / dblp), not from the PDF.
- Abstract: RRF is "a simple method for combining the document rankings from multiple IR systems" that "consistently yields better results than any individual system". — [Cormack et al. 2009 PDF](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
- Formula: RRFscore(d ∈ D) = Σ_{r∈R} 1/(k + r(d)), "where k = 60 was fixed during a pilot investigation and not altered during subsequent validation." — [Cormack et al. 2009 PDF](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
- Why k: "The constant k mitigates the impact of high rankings by outlier systems." The pilot "indicated that k = 60 was near-optimal, but that the choice was not critical." — [Cormack et al. 2009 PDF](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
- Why reciprocal: lower-ranked documents' importance "does not vanish as it would were, say, an exponential function used." — [Cormack et al. 2009 PDF](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
- Score-agnostic: RRF "combines ranks without regard to the arbitrary scores returned by particular ranking methods". — [Cormack et al. 2009 PDF](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
- Effect size: "RRF outperforms Condorcet, CombMNZ and the best system by 4% to 5% on average" (MAP, TREC experiments). — [Cormack et al. 2009 PDF](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)
- Caveat inside the paper: on LETOR 3, "CombMNZ edges RRF by a small margin (p ≈ .2)". On TREC 9, the best individual (human-in-the-loop) run beat RRF. — [Cormack et al. 2009 PDF](http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)

**OpenAI file search exposes RRF-style hybrid weights**
- OpenAI's retrieval guide says that with `ranking_options.hybrid_search` you can tune "`hybrid_search.embedding_weight` (`rrf_embedding_weight`)" and "`hybrid_search.text_weight` (`rrf_text_weight`)". (fetch-tool quote; no page date shown) — [OpenAI Retrieval guide](https://developers.openai.com/api/docs/guides/retrieval)

### Inferences
- Rank fusion is needed because BM25 scores and cosine similarities are on different scales. RRF avoids calibrating them by using only ranks, which is the paper's "without regard to the arbitrary scores" property.
- The Anthropic post says "rank fusion techniques" and does not name RRF specifically. Do not claim Anthropic used RRF.
- The 35%/49%/67% figures are relative reductions on Anthropic's own evaluation sets with particular embedding models, the Cohere reranker, and Claude 3 Haiku for contextualization. They are vendor-reported and depend on that setup. Present them as "Anthropic reports..."

### Gaps
- I did not verify which datasets and embedding models the Contextual Retrieval post evaluated (the post mentions several; they were not captured), nor its statements about reranking latency or cost.
- I did not open the ACM DL page (dl.acm.org) directly. The DOI and pages come from search results.

## Q3. Cross-encoders vs bi-encoders for reranking (Sentence-Transformers docs)

### Takeaway
A bi-encoder embeds the query and each document separately, so document embeddings can be precomputed and searched at scale. A cross-encoder reads the query and the document together and outputs a relevance score, with no embedding. It is more accurate but too slow to run over a whole corpus. The documented pattern is: retrieve the top ~100 with a bi-encoder, then rerank them with a cross-encoder.

### Cited Findings
Page footer reads "© Copyright 2026". No software version is shown on the page.
- "Bi-Encoders produce for a given sentence a sentence embedding." "We pass to a BERT independently the sentences A and B, which result in the sentence embeddings u and v." (fetch-tool quote) — [SBERT Cross-Encoder docs](https://sbert.net/examples/cross_encoder/applications/README.html)
- "A Cross-Encoder does not produce a sentence embedding". It outputs "an output value between 0 and 1 indicating the similarity of the input sentence pair." (fetch-tool quote) — [SBERT Cross-Encoder docs](https://sbert.net/examples/cross_encoder/applications/README.html)
- "Cross-Encoder achieve better performances than Bi-Encoders." (fetch-tool quote) — [SBERT Cross-Encoder docs](https://sbert.net/examples/cross_encoder/applications/README.html)
- Scaling: clustering 10,000 sentences with cross-encoders needs scores for about 50 million pairs, "which takes about 65 hours". With a bi-encoder, the embeddings take "only 5 seconds". (fetch-tool quote) — [SBERT Cross-Encoder docs](https://sbert.net/examples/cross_encoder/applications/README.html)
- Retrieve-then-rerank: "First, you use an efficient Bi-Encoder to retrieve e.g. the top-100 most similar sentences for a query." Then the cross-encoder re-ranks those 100 hits by scoring every (query, hit) pair. (fetch-tool quote) — [SBERT Cross-Encoder docs](https://sbert.net/examples/cross_encoder/applications/README.html)

### Inferences
- Anthropic's 150 → 20 rerank step (Q2) is an instance of this two-stage pattern.
- The "between 0 and 1" output describes the classic SBERT cross-encoder example. Some rerankers output unbounded logits, so do not generalize that range to all rerankers.

### Gaps
- I did not confirm the exact sentence-transformers library version that this docs page corresponds to.

## Q4. Prompt assembly, grounding and citations (Anthropic, OpenAI, Google)

### Takeaway
Anthropic's docs say to put long documents at the top of the prompt, above the query, and report that queries at the end improve quality "by up to 30 percent" in tests. They recommend wrapping each document in `<document>` tags with `<source>` and `<document_content>` subtags, and asking Claude to extract quotes first. Anthropic's Citations API chunks documents into sentences and returns `cited_text` with location pointers that are "guaranteed" to be valid; it cannot be combined with structured outputs. OpenAI file search is a hosted tool that runs semantic plus keyword search over vector stores and returns `file_citation` annotations. Google defines grounding as connecting output to verifiable sources and returns `url_citation` annotations with character indices.

### Cited Findings
**Anthropic, long-context prompting.** The old URL docs.claude.com/.../long-context-tips redirects (302) to platform.claude.com; the content now sits in the "Prompting best practices" page under "Long context prompting". The page has no date, and it lists current models including Claude Opus 5.5, Sonnet 5.5, Haiku 5.5, and Fable 5.1.
- Scope: "When working with large documents or data-rich inputs (20k+ tokens), structure your prompt carefully" — [Anthropic Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- "Place your long documents and inputs near the top of your prompt, above your query, instructions, and examples." — [Anthropic Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- "Queries at the end can improve response quality by up to 30 percent in tests, especially with complex, multidocument inputs." — [Anthropic Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- "wrap each document in `<document>` tags with `<document_content>` and `<source>` (and other metadata) subtags for clarity." The example wraps everything in `<documents>` and uses `index` attributes. — [Anthropic Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- "ask Claude to quote relevant parts of the documents first before carrying out its task." The example asks for quotes "in <quotes> tags". — [Anthropic Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)

**Anthropic Citations API.** Status GA. Platforms: Claude API, Claude Platform on AWS, Bedrock, Google Cloud, Microsoft Foundry. "All active models support citations." No date shown.
- Purpose: "Citations return the exact passages that support each claim, so you can verify answers and surface sources to your users." — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Enabled per document block with `"citations": {"enabled": true}`; a document can carry `title` and `context` fields (from the code example). — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Chunking: "Document contents are 'chunked' to define the minimum granularity of possible citations." Plain text and PDFs "are automatically chunked into sentences". Custom content blocks "are used as-is and no further chunking is done." — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- RAG guidance: "if you want Claude to be able to cite specific sentences from your RAG chunks, you should put each RAG chunk into a plain text document." — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Location types: `char_location` (plain text), `page_location` (PDF), and `content_block_location` (custom content, 0-indexed block indices). — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Reliability vs prompt-based approaches: "citations are guaranteed to contain valid pointers to the provided documents." Also, "significantly more likely to cite the most relevant quotes from documents than purely prompt-based approaches" (Anthropic's own evaluations; no number given). — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Tokens: "The `cited_text` field is provided for convenience and does not count toward output tokens." Enabling citations causes "a slight increase in input tokens". — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- Limitation: "Citations cannot be used together with structured outputs". Combining them returns a 400 error. Citations also apply to `search_result` blocks. — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- PDF limitation: "Citing images from PDFs is not currently supported." — [Anthropic Citations](https://platform.claude.com/docs/en/build-with-claude/citations)

**OpenAI file search / retrieval.** platform.openai.com/docs/guides/tools-file-search redirects (301) to developers.openai.com. No page date shown.
- File search "enables models to retrieve information in a knowledge base of previously uploaded files" using "semantic and keyword search." (fetch-tool quote) — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- Output: a `file_search_call` item plus a `message` whose annotations include `"type": "file_citation"` entries with `file_id` and `filename`. Results are hidden unless requested: "the file search call will not return search results by default" (use `include: ["file_search_call.results"]`). (fetch-tool output) — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- `max_num_results`: "This can help reduce both token usage and latency, but may come at the cost of reduced answer quality." (fetch-tool quote) — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- Metadata filtering: "You can filter the search results based on the metadata of the files." (fetch-tool quote) — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search)
- Default chunking: "`max_chunk_size_tokens` is set to `800` and `chunk_overlap_tokens` is set to `400`." (fetch-tool quote) — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- Ranking: a `ranker` "such as `auto` or `default-2024-08-21`" and a `score_threshold` "between 0.0 and 1.0". (fetch-tool quote) — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- Semantic search "is a technique that leverages vector embeddings to surface semantically relevant results." After retrieval you may "synthesize a response" by supplying the results and query "to get back a grounded response." (fetch-tool quote) — [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)

**Google grounding**
- Vertex AI / Gemini Enterprise Agent Platform. cloud.google.com redirects to docs.cloud.google.com; the page says "Last updated 2026-10-15 UTC". Definition: "In generative AI, grounding is the ability to connect model output to verifiable sources of information." (fetch-tool quote) — [Google Cloud Grounding overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview)
- Benefits listed: "Reduces model hallucinations, which are instances where the model generates content that isn't factual"; "Anchors model responses to your data sources"; "Provides auditability by providing grounding support, which are links to sources." (fetch-tool quotes) — [Google Cloud Grounding overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview)
- Sources listed include Google Search, Google Maps, Agent Search, RAG Engine, Elasticsearch, "your search API", Web Grounding for Enterprise, and Parallel web search. — [Google Cloud Grounding overview](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview)
- Gemini API (ai.google.dev, last updated 2026-10-13 UTC): "Grounding with Google Search connects the Gemini model to real-time web content and works with all available languages." The current page documents the Interactions API: `url_citation` annotations with `url`, `title`, `start_index`, `end_index`. "Each annotation includes `start_index` and `end_index` to identify which part of the text it cites." (fetch-tool quotes) — [Gemini API Google Search grounding](https://ai.google.dev/gemini-api/docs/google-search)

### Inferences
- Across providers, grounding has two parts: (1) put the retrieved text in the context, clearly delimited and with source metadata; (2) get machine-checkable pointers from the answer back to the source spans. These are Anthropic's char/page/block locations, OpenAI's `file_citation`, and Google's `url_citation` start/end indices.
- Anthropic's "documents at top, query at end" advice fits Lost in the Middle's finding of recency bias (Q5). Anthropic does not cite that paper, so present this as a connection, not as Anthropic's stated rationale.
- Provider-specific and change-prone: the Gemini page now describes the Interactions API, while older material describes `groundingMetadata` / `groundingSupports`. The OpenAI docs moved domains. The Anthropic long-context page was folded into the best-practices page. A lesson should not hard-code field names without a date.

### Gaps
- I did not confirm the older Gemini `groundingMetadata` / `groundingChunks` / `groundingSupports` fields on the current page; they are not on it. I did not check whether `generateContent` still returns them.
- The OpenAI file search page as fetched showed no ranking or chunking details; those came from the separate Retrieval guide. I did not capture any OpenAI statement that file search does not eliminate hallucination.

## Q5. Failure modes: Lost in the Middle; hallucination despite RAG; irrelevant chunks

### Takeaway
Liu et al. (TACL 2024) found a U-shaped curve: accuracy is highest when the relevant passage comes at the start or end of the context and drops when it sits in the middle. For GPT-3.5-Turbo, a relevant passage in the middle gave lower accuracy than giving no documents at all (closed-book 56.1%). Going from 20 to 50 retrieved documents improved accuracy only marginally (about 1.5% for GPT-3.5-Turbo). Anthropic states that grounding techniques "don't eliminate" hallucinations. OpenAI warns that lowering `max_num_results` may reduce answer quality.

### Cited Findings
**Liu et al., "Lost in the Middle: How Language Models Use Long Contexts". arXiv:2307.03172 v1 6 Jul 2023; v3 20 Nov 2023. TACL Vol. 12, pp. 157–173, 2024, DOI 10.1162/tacl_a_00638.** Quotes below are from the v3 PDF text; TACL metadata is from the ACL Anthology.
- Abstract: "performance is often highest when relevant information occurs at the beginning or end of the input context" — [arXiv 2307.03172](https://arxiv.org/abs/2307.03172)
- "we observe a distinctive U-shaped performance curve"; performance is highest at the very beginning "(primacy bias) or end of its input context (recency bias)". — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)
- Tasks: "multi-document question answering and key-value retrieval". The QA task uses NaturalQuestions-Open with "10, 20, and 30 total documents". — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)
- Worse than no retrieval: "GPT-3.5-Turbo's performance on the multidocument question task is lower than its performance when predicting without any documents (i.e., the closed-book setting; 56.1%)." (24 words) — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)
- Magnitude: "GPT-3.5-Turbo's multi-document QA performance can drop by more than 20%" — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)
- Long-context variants don't help: "extended-context models are not necessarily better at using their input context". — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)
- More retrieval saturates: "using 50 documents instead of 20 retrieved documents only marginally improves performance (∼1.5% for GPT-3.5-Turbo and∼1% for claude-1.3)." — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)
- "model performance saturates long before retriever recall saturates". — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)
- Query-aware contextualization (query before and after the data) "enables near-perfect performance on the synthetic key-value task, but minimally changes trends in multi-document QA". — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)
- Models tested (Table 1 closed-book/oracle): LongChat-13B (16K), MPT-30B-Instruct, GPT-3.5-Turbo (and 16K), Claude-1.3 (and 100K). Claude-1.3 did nearly perfectly on key-value retrieval. — [arXiv 2307.03172 v3 PDF](https://arxiv.org/pdf/2307.03172v3)

**Provider warnings**
- Anthropic, Reduce hallucinations: "while these techniques significantly reduce hallucinations, they don't eliminate them entirely. Always validate critical information" — [Anthropic Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- Anthropic: models "can sometimes generate text that is factually incorrect or inconsistent with the given context." So hallucination can contradict even supplied context. — [Anthropic Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- Anthropic mitigations: "Allow Claude to say 'I don't know'"; extract "word-for-word quotes first" for documents over 20k tokens; for unsupported claims, "If it can't find a quote, it must retract the claim"; "only use information from provided documents". — [Anthropic Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- OpenAI: limiting `max_num_results` "may come at the cost of reduced answer quality". A higher `score_threshold` restricts results to more relevant chunks but may exclude useful ones (fetch-tool paraphrase). — [OpenAI File search](https://developers.openai.com/api/docs/guides/tools-file-search); [OpenAI Retrieval](https://developers.openai.com/api/docs/guides/retrieval)
- Anthropic: retrieval itself fails some of the time. Even the best configuration had a 1.9% top-20 retrieval failure rate (1 − recall@20), so the right chunk is sometimes not in context at all. — [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)

### Inferences
- RAG failures fall into two layers: retrieval failures (the right chunk is not in the top-k, measured by recall@k) and reading failures (the chunk is present but ignored or misused, as in Lost in the Middle). Rerankers address the first. Ordering, fewer but better chunks, and quote-first prompting address the second.
- Liu et al. tested 2023-era models. Current frontier models may behave differently, so teach the finding as a documented phenomenon to check for, not a fixed property of today's models.
- Irrelevant retrieved chunks act as "distractors" (the paper's term for the non-answer passages). Their cost is position-dependent dilution, which argues for tight top-k after reranking rather than very large k.

### Gaps
- I did not find primary-source statements from OpenAI or Google that explicitly say "RAG/grounding does not eliminate hallucination". Google says grounding "reduces" hallucinations, which implicitly is not elimination.
- I did not fetch newer replication studies of Lost in the Middle on current long-context models (out of scope for primary-source Pass 1).

---

### Claims table

| # | Claim | Source URL | Excerpt (verbatim, <25 words) | Confidence |
|---|---|---|---|---|
| 1 | HNSW is an approximate NN method using a multi-layer hierarchy of proximity graphs | https://arxiv.org/abs/1603.09320 | "builds a multi-layer structure consisting from hierarchical set of proximity graphs (layers)" | high |
| 2 | HNSW search starts at the upper layer; authors claim logarithmic complexity scaling | https://arxiv.org/abs/1603.09320 | "allows a logarithmic complexity scaling" | high (as authors' claim); medium as a general guarantee |
| 3 | HNSW paper current version v4, 14 Aug 2018 (v1 30 Mar 2016) | https://arxiv.org/abs/1603.09320 | (version history on abstract page) | high |
| 4 | FAISS IndexFlatL2 is brute-force L2 search and needs no training | https://github.com/facebookresearch/faiss/wiki/Getting-started | "the simplest version that just performs brute-force L2 distance search on them" | high |
| 5 | FAISS labels IndexFlatL2 / IndexFlatIP as exact search | https://github.com/facebookresearch/faiss/wiki/Faiss-indexes | "Exact Search for L2" / "Exact Search for Inner Product" | high |
| 6 | IndexFlatIP can do cosine if vectors are normalized beforehand | https://github.com/facebookresearch/faiss/wiki/Faiss-indexes | "also for cosine (normalize vectors beforehand)" | high |
| 7 | Inner product is not cosine unless vectors are normalized; normalize both stored vectors and queries | https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances | "This is not by itself cosine similarity, unless the vectors are normalized" | high |
| 8 | IndexHNSWFlat is non-exhaustive | https://github.com/facebookresearch/faiss/wiki/Faiss-indexes | Exhaustive: "no" | medium (flattened-table read) |
| 9 | FAISS paper: GPU brute-force, approximate and PQ search; 1B-vector k-NN graph < 12 h on 4 GPUs | https://arxiv.org/abs/1702.08734 | "95 million images from the Yfcc100M dataset" | medium (abstract only partially quoted) |
| 10 | Contextual Retrieval published 19 Sep 2024 | https://www.anthropic.com/news/contextual-retrieval | "Published Sep 19, 2024" | high |
| 11 | Anthropic hybrid: BM25 for exact matches + embeddings for semantic similarity, merged via rank fusion | https://www.anthropic.com/news/contextual-retrieval | "Combine and deduplicate results from (3) and (4) using rank fusion techniques;" | high |
| 12 | Anthropic retrieved top 150, reranked with Cohere, kept top 20 | https://www.anthropic.com/news/contextual-retrieval | "(we used the top 150)" ... "(we used the top 20)" | high |
| 13 | Metric is 1 − recall@20 | https://www.anthropic.com/news/contextual-retrieval | "We use 1 minus recall@20 as our evaluation metric" | high |
| 14 | Contextual Embeddings: −35% failure (5.7%→3.7%) | https://www.anthropic.com/news/contextual-retrieval | "Contextual Embeddings reduced the top-20-chunk retrieval failure rate by 35%" | high |
| 15 | + Contextual BM25: −49% (→2.9%) | https://www.anthropic.com/news/contextual-retrieval | "Combining Contextual Embeddings and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 49%" | high |
| 16 | + reranking: −67% (→1.9%) | https://www.anthropic.com/news/contextual-retrieval | "Reranked Contextual Embedding and Contextual BM25 reduced the top-20-chunk retrieval failure rate by 67%" | high |
| 17 | Below ~200k tokens, put the whole knowledge base in the prompt instead of RAG | https://www.anthropic.com/news/contextual-retrieval | "If your knowledge base is smaller than 200,000 tokens (about 500 pages of material)," | high |
| 18 | RRF formula Σ 1/(k + r(d)) with k = 60 fixed in a pilot | http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf | "where k = 60 was fixed during a pilot investigation and not altered during subsequent validation" | high |
| 19 | k mitigates outlier systems; choice of k not critical | http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf | "The constant k mitigates the impact of high rankings by outlier systems." | high |
| 20 | RRF beats Condorcet, CombMNZ and best system by 4–5% on average (TREC) | http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf | "RRF outperforms Condorcet, CombMNZ and the best system by 4% to 5% on average" | high |
| 21 | RRF uses ranks only, ignoring raw scores | http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf | "combines ranks without regard to the arbitrary scores returned by particular ranking methods" | high |
| 22 | OpenAI hybrid search exposes RRF embedding/text weights | https://developers.openai.com/api/docs/guides/retrieval | "`hybrid_search.embedding_weight` (`rrf_embedding_weight`)" | medium (fetch-tool quote) |
| 23 | Cross-encoders produce no embedding and are more accurate than bi-encoders | https://sbert.net/examples/cross_encoder/applications/README.html | "Cross-Encoder achieve better performances than Bi-Encoders." | high |
| 24 | Cross-encoder clustering of 10k sentences ≈ 65 h vs 5 s for bi-encoder | https://sbert.net/examples/cross_encoder/applications/README.html | "which takes about 65 hours" | medium (fetch-tool quote) |
| 25 | Retrieve top-100 with bi-encoder, rerank with cross-encoder | https://sbert.net/examples/cross_encoder/applications/README.html | "use an efficient Bi-Encoder to retrieve e.g. the top-100 most similar sentences for a query" | high |
| 26 | Anthropic: put long documents at the top, above query/instructions | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | "Place your long documents and inputs near the top of your prompt, above your query, instructions, and examples." | high |
| 27 | Anthropic: queries at end improve quality up to 30% in tests | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | "Queries at the end can improve response quality by up to 30 percent in tests" | high (vendor-reported) |
| 28 | Anthropic: use `<document>` with `<document_content>` and `<source>` subtags | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | "wrap each document in `<document>` tags with `<document_content>` and `<source>` (and other metadata) subtags" | high |
| 29 | Anthropic: ask Claude to quote relevant parts first | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | "ask Claude to quote relevant parts of the documents first before carrying out its task." | high |
| 30 | Claude Citations: text/PDF chunked into sentences; custom content used as-is | https://platform.claude.com/docs/en/build-with-claude/citations | "By default, plain text and PDF documents are automatically chunked into sentences." | high |
| 31 | Citations pointers guaranteed valid; cited_text not billed as output | https://platform.claude.com/docs/en/build-with-claude/citations | "citations are guaranteed to contain valid pointers to the provided documents." | high |
| 32 | Citations incompatible with structured outputs (400 error) | https://platform.claude.com/docs/en/build-with-claude/citations | "Citations cannot be used together with structured outputs" | high |
| 33 | OpenAI file search uses semantic + keyword search over uploaded files | https://developers.openai.com/api/docs/guides/tools-file-search | "semantic and keyword search" | medium (fetch-tool quote) |
| 34 | OpenAI file search returns `file_citation` annotations; results only with include param | https://developers.openai.com/api/docs/guides/tools-file-search | "the file search call will not return search results by default" | medium |
| 35 | OpenAI default chunking 800 tokens with 400 overlap | https://developers.openai.com/api/docs/guides/retrieval | "`max_chunk_size_tokens` is set to `800` and `chunk_overlap_tokens` is set to `400`" | medium |
| 36 | Google: grounding connects output to verifiable sources and reduces hallucinations | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview | "grounding is the ability to connect model output to verifiable sources of information." | medium (fetch-tool quote) |
| 37 | Gemini Search grounding returns `url_citation` annotations with start/end indices | https://ai.google.dev/gemini-api/docs/google-search | "Each annotation includes `start_index` and `end_index` to identify which part of the text it cites." | medium (API surface changes often) |
| 38 | Lost in the Middle: U-shaped curve, primacy and recency bias | https://arxiv.org/pdf/2307.03172v3 | "we observe a distinctive U-shaped performance curve" | high |
| 39 | GPT-3.5-Turbo with mid-context answer scored below closed-book (56.1%) | https://arxiv.org/pdf/2307.03172v3 | "lower than its performance when predicting without any documents (i.e., the closed-book setting; 56.1%)" | high |
| 40 | Extended-context models not necessarily better at using context | https://arxiv.org/pdf/2307.03172v3 | "extended-context models are not necessarily better at using their input context" | high |
| 41 | 50 vs 20 retrieved docs gives ~1.5% (GPT-3.5) / ~1% (Claude-1.3) gain | https://arxiv.org/pdf/2307.03172v3 | "using 50 documents instead of 20 retrieved documents only marginally improves performance" | high |
| 42 | Published in TACL vol. 12, pp. 157–173, 2024 | https://aclanthology.org/2024.tacl-1.9/ | (bibliographic metadata) | high |
| 43 | Anthropic: hallucination-reduction techniques don't eliminate hallucinations | https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations | "they don't eliminate them entirely. Always validate critical information" | high |
| 44 | Anthropic: retract claims lacking a supporting quote; restrict to provided documents | https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations | "If it can't find a quote, it must retract the claim." | high |
| 45 | OpenAI: lowering max_num_results may reduce answer quality | https://developers.openai.com/api/docs/guides/tools-file-search | "may come at the cost of reduced answer quality" | medium |
