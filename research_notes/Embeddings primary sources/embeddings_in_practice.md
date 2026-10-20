# Embeddings in Practice: Primary-Source Notes (Pass 1)

Access date for all sources: 2026-10-19. Excerpts were extracted with a fetch tool that summarizes pages using a small model. Each quoted excerpt was returned as verbatim text, but Pass 2 should re-check every one against the live page, especially any marked "medium". "Provider-specific" means the behaviour applies only to that vendor or model and should not be presented as universal.

Version and date stamps found:
- Gemini embeddings page: "Last updated 2026-10-09 UTC."
- OpenAI embeddings guide and API reference: no last-updated date or version shown.
- Anthropic embeddings page: no date shown. Model blog links on the page are dated up to 2026-09-30 (rerank-3).
- BGE model card: news entry dated 09/12/2023 announcing v1.5. License MIT.
- sbert.net: no docs version shown on the pages fetched. The homepage banner says "Sentence Transformers v6.0 recently released". Footer © 2026.
- Qdrant migration tutorial: footer © 2026 only.

## Use cases (OpenAI, Gemini, sentence-transformers, Anthropic/Voyage)

### Takeaway
All three main sources list retrieval or search first. OpenAI gives the broadest list (search, clustering, recommendations, anomaly detection, diversity measurement, classification). Gemini also names RAG and search reranking. The sbert.net homepage leads with semantic search, STS and paraphrase mining.

### Cited Findings
- OpenAI lists: Search, Clustering, Recommendations, Anomaly detection, Diversity measurement, Classification. Lead-in: "Embeddings are commonly used for:". Classification is described as "where text strings are classified by their most similar label". — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Gemini: "Text embeddings are crucial for a variety of common AI use cases, such as:" Listed items: information retrieval, search reranking, anomaly detection, classification, clustering. (The list items were paraphrased by the fetch tool. Pass 2 should confirm the exact wording.) — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Gemini: "Building Retrieval Augmented Generation (RAG) systems is a common use case for AI products." — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- sentence-transformers: "This unlocks a wide range of applications, including semantic search, semantic textual similarity, and paraphrase mining." The Usage sidebar also lists Semantic Search, Retrieve & Re-Rank, Clustering, Paraphrase Mining, Translated Sentence Mining, Image Search and Embedding Quantization. The homepage does not name classification. — [sbert.net](https://sbert.net/)
- Anthropic page description: embeddings are for "tasks like search, recommendations, and anomaly detection". — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)

### Inferences
- "Search/retrieval, clustering, classification, anomaly detection" is common ground across OpenAI and Gemini, and safe to teach as canonical. Recommendations and diversity measurement are OpenAI's framing.

### Gaps
- I did not fetch a dedicated sbert.net classification page, so there is no sbert citation for classification.

## Query vs document asymmetry

### Takeaway
Asymmetric retrieval is handled differently by each provider:
- Gemini: a `task_type` enum, on gemini-embedding-001 only.
- Voyage: an `input_type` that prepends fixed prompts.
- BGE: a manual query-only instruction prefix.
- sentence-transformers: `encode_query` / `encode_document` plus prompts.

All of this is provider-specific.

### Cited Findings
- **Gemini task types (gemini-embedding-001):** SEMANTIC_SIMILARITY, CLASSIFICATION, CLUSTERING, RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, CODE_RETRIEVAL_QUERY, QUESTION_ANSWERING, FACT_VERIFICATION. — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Gemini: "For `gemini-embedding-001`, you can specify the `task_type` in the `embedContent` method." — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Gemini: "You cannot use the `task_type` field for the `gemini-embedding-2` model." — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Gemini descriptions: RETRIEVAL_DOCUMENT is "Embeddings optimized for document search." SEMANTIC_SIMILARITY is "Embeddings optimized to assess text similarity." — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- **Anthropic does not make an embedding model:** "Anthropic does not offer its own embedding model." The page names Voyage AI by MongoDB as one provider. — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- **Voyage `input_type`:** "Do not omit `input_type` or set `input_type=None`." It applies "For all retrieval tasks and use cases (for example, RAG)". — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Voyage: "special prompts are prepended to the input text prior to embedding." The query prompt is "Represent the query for retrieving supporting documents: ". The document prompt is "Represent the document for retrieval: ". — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Voyage rationale: specifying query or document "can create better dense vector representations for retrieval, which can lead to better retrieval quality." — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- **BGE query instruction (English):** `Represent this sentence for searching relevant passages: ` — [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- BGE recommends the instruction for short queries: "it is recommended to add instructions for these short queries." Passages do not need it: "In all cases, the documents/passages do not need to add the instruction." — [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- BGE says the instruction is optional in v1.5: "So you can generate embedding without instruction in all cases for convenience." — [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- **sentence-transformers:** `encode_query` "Computes embeddings specifically optimized for query representation." `encode_document` "Computes embeddings specifically optimized for document/passage representation." — [SentenceTransformer API](https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)
- sentence-transformers prompts: "The prompt text will be prepended before any text during inference." — [SentenceTransformer API](https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)

### Inferences
- In each case, the asymmetry is applied as a text prefix or prompt before encoding. Voyage and sentence-transformers document this explicitly. For Gemini this is an assumption: the docs only show the parameter.
- The prefix applied at query time must match the convention used for the corpus.
- The OpenAI embeddings guide and API reference fetched here show no query/document parameter. Absence is not proof, so verify in Pass 2.

### Gaps
- Gemini's alternative for gemini-embedding-2 (for example, in-text task prompts) was not captured. Pass 2 should check the page for any replacement guidance.

## Input limits and truncation

### Takeaway
Limits by provider:
- OpenAI: 8192 tokens per input, 2048 inputs per array, 300,000 tokens per request.
- Gemini: 8192 input tokens, and overflow is silently truncated.
- Voyage: 32,000-token context on current models.
- BGE-small: 512 tokens.
- sentence-transformers: truncates anything beyond `max_seq_length`.

Silent truncation is the key pitfall.

### Cited Findings
- OpenAI per-input limit: "The input must not exceed the max input tokens for the model (8192 tokens for all embedding models)". — [OpenAI API reference: create embeddings](https://developers.openai.com/api/reference/resources/embeddings/methods/create)
- OpenAI request limits: "any array must be 2048 dimensions or less". Also, "all embedding models enforce a maximum of 300,000 tokens summed across all inputs in a single request." "2048 dimensions" is OpenAI's wording for array length. — [OpenAI API reference](https://developers.openai.com/api/reference/resources/embeddings/methods/create)
- OpenAI guide table, text-embedding-3-small row: "| text-embedding-3-small | 62,500 | 62.3% | 8192 |". The large model shows the same 8192. — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Gemini: "The overall maximum input tokens limit is 8192 tokens." Also, "The system silently truncates inputs that exceed this limit." — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Voyage: voyage-4 family context length is 32,000; voyage-law-2 is 16,000. voyage-context-4 accepts 120,000 tokens only "when you set `enable_auto_chunking` to `true`". — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- BGE-small-en-v1.5: the model card's table lists dimension 384 and sequence length 512. This comes from a table, so there is no sentence to quote. — [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- sentence-transformers truncation: "Longer texts will be truncated to the first `model.max_seq_length` tokens". — [sbert computing embeddings](https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html)
- sentence-transformers, the `max_seq_length` property: "Returns the maximal input sequence length for the model. Longer inputs will be truncated." — [SentenceTransformer API](https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)
- sentence-transformers, hard ceiling: "You cannot increase the length higher than what is maximally supported by the respective transformer model." — [sbert computing embeddings](https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html)
- sentence-transformers, rough conversion: "A common value for BERT-based models are 512 tokens, which corresponds to about 300-400 words (for English)." — [sbert computing embeddings](https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html)
- sentence-transformers, quality caveat: "if a model was trained on short texts, the representations for long texts might not be that good." — [sbert computing embeddings](https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html)
- sentence-transformers example: all-MiniLM-L6-v2 shows "Max Sequence Length: 256". — [sbert computing embeddings](https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html)

### Inferences
- Truncation behaviour differs by provider. Gemini and sentence-transformers truncate silently, while OpenAI states a hard "must not exceed" limit. OpenAI's error behaviour on overflow was not confirmed.
- Chunking text below the model limit is therefore an operational requirement.

### Gaps
- I did not confirm whether OpenAI returns an error or truncates when input exceeds 8192 tokens.
- I did not fetch Voyage's `truncation` parameter, which is documented on MongoDB docs rather than the Anthropic page.

## Model compatibility and re-embedding

### Takeaway
Google gives the clearest official statement: gemini-embedding-001 and gemini-embedding-2 spaces are "incompatible" and upgrading requires re-embedding all data. Qdrant (vendor doc) states that switching models requires re-embedding all vectors. The OpenAI guide fetched has no such statement.

### Cited Findings
- Google: "The embedding spaces between `gemini-embedding-001` and `gemini-embedding-2` are **incompatible**." — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Google: "If you are upgrading to `gemini-embedding-2`, you must re-embed all of your existing data." — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Qdrant (VENDOR DOC): "Switching models requires re-embedding all vectors in your collection, which can take time." — [Qdrant: Migrate to a New Embedding Model](https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/)
- Qdrant (VENDOR DOC): the new collection must be "compatible with the new model in terms of vector size and similarity function". — [Qdrant migration tutorial](https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/)
- Qdrant (VENDOR DOC), from search-result summary only and not quoted verbatim: the tutorial describes keeping the old collection serving while re-embedding into a new one, with dual writes during migration. — [Qdrant migration tutorial](https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/)
- OpenAI guide: the fetch found no statement on mixing models or re-embedding. — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)

### Inferences
- The incompatibility principle generalizes beyond Google. Teach it as a general rule, citing Google as the official example and Qdrant as vendor corroboration.

### Gaps
- No official Pinecone or Weaviate page was fetched. The Pinecone search hits were community forum posts and third-party pages, which I excluded as non-primary. Pinecone's "Bring your own vectors" quickstart (https://docs.pinecone.io/guides/get-started/quickstart/bring-your-own-vectors) was surfaced in search but NOT fetched. Its search-summary content (index dimension must match the model's output) is unverified.
- No OpenAI statement on cross-model compatibility was found.

## Multilingual and multimodal (gemini-embedding-2): provider-specific and fast-changing

### Takeaway
Google describes gemini-embedding-2 as its first multimodal embedding model. It uses one space for text, images, video, audio and documents, and supports 100+ languages. Voyage offers separate multimodal models.

### Cited Findings
- "The latest model, `gemini-embedding-2`, is the first multimodal embedding model in the Gemini API." — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings) (Last updated 2026-10-09)
- "It maps text, images, video, audio, and documents into a unified embedding space". — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Supports "over 100 languages". The fetch tool returned only this phrase verbatim. — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Voyage: `voyage-multimodal-3.5` "can vectorize interleaved text, images, and videos". It is called via `multimodal_embed()` instead of `embed()`. — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Voyage: voyage-4-large is described as "The best general-purpose and multilingual retrieval quality." — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)

### Inferences
- Model names and capabilities changed during 2026. Lesson content should name the date, or describe multimodality generically.

### Gaps
- Per-modality limits for gemini-embedding-2 (image count, audio or video length, PDF pages) were not extracted.

## Cost, dimensions and normalization trade-offs

### Takeaway
OpenAI recommends using the `dimensions` parameter to shorten embeddings, which saves storage and compute at some cost in accuracy. If you truncate vectors manually, you must re-normalize them. Gemini and Voyage offer the same kind of control:
- Gemini: `output_dimensionality`. gemini-embedding-001 needs manual re-normalization; gemini-embedding-2 renormalizes automatically.
- Voyage: `output_dimension`, plus quantization via `output_dtype`.

### Cited Findings
- OpenAI: larger embeddings "generally costs more and consumes more compute, memory and storage than using smaller embeddings." This is a fragment of a longer sentence; the fetch tool returned only this part verbatim (medium confidence). — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- OpenAI: "developers can shorten embeddings (i.e. remove some numbers from the end of the sequence)". — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- OpenAI: "In general, using the `dimensions` parameter when creating the embedding is the suggested approach." — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- OpenAI: "When you change the dimension manually, you need to be sure to normalize the dimensions of the embedding". — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- OpenAI default sizes: 1536 for small and 3072 for large. A 256-dimension large embedding can still outperform unshortened ada-002 on MTEB (paraphrased by the fetch tool). — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- OpenAI API reference: `dimensions` is "Only supported in `text-embedding-3` and later models." — [OpenAI API reference](https://developers.openai.com/api/reference/resources/embeddings/methods/create)
- OpenAI similarity metric: "OpenAI embeddings are normalized to length 1". Cosine similarity "can be computed slightly faster using just a dot product". Also, "The choice of distance function typically doesn't matter much." — [OpenAI embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Gemini: "We recommend using 768, 1536, or 3072 output dimensions." Also, "`gemini-embedding-2` introduces automatic renormalization for non-default dimensions." For gemini-embedding-001, the docs say non-3072 dimensions must be normalized manually (paraphrased). — [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- Voyage quantization: int8 and binary reduce "storage, memory, and costs by 4x and 32x, respectively". — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- Voyage manual truncation: "truncate them by keeping the leading subset of dimensions, then normalize them again." — [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- sentence-transformers: `normalize_embeddings` means "Whether to normalize returned vectors to have length 1." `truncate_dim` is "The dimension to truncate sentence embeddings to." — [SentenceTransformer API](https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)
- BGE score calibration pitfall: "the similarity distribution of the current BGE model is about in the interval [0.6, 1]". Also, "a similarity score greater than 0.5 does not indicate that the two sentences are similar." These lines refer to the pre-v1.5 issue that v1.5 "alleviates". — [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5)

### Inferences
- Re-normalizing after manual truncation is a recurring pitfall, documented by OpenAI, Voyage and Google (for gemini-embedding-001).
- Absolute similarity thresholds are model-specific, as the BGE card shows. Teach ranking over fixed cutoffs.

### Gaps
- No OpenAI per-token price was captured. The table column "62,500" is labelled pages-per-dollar on the OpenAI page, but this was not confirmed and should be verified before use.

## Claims table

| Claim | Source URL | Excerpt (≤25 words) | Confidence |
|---|---|---|---|
| OpenAI lists search, clustering, recommendations, anomaly detection, diversity measurement, classification as uses | https://developers.openai.com/api/docs/guides/embeddings | "Embeddings are commonly used for:" | high |
| Gemini lists retrieval, reranking, anomaly detection, classification, clustering | https://ai.google.dev/gemini-api/docs/embeddings | "Text embeddings are crucial for a variety of common AI use cases, such as:" | medium (list items paraphrased) |
| sentence-transformers enables semantic search, STS, paraphrase mining | https://sbert.net/ | "including semantic search, semantic textual similarity, and paraphrase mining." | high |
| Anthropic has no embedding model of its own | https://platform.claude.com/docs/en/build-with-claude/embeddings | "Anthropic does not offer its own embedding model." | high |
| Voyage input_type should always be set for retrieval | https://platform.claude.com/docs/en/build-with-claude/embeddings | "Do not omit `input_type` or set `input_type=None`." | high |
| Voyage input_type prepends prompts | https://platform.claude.com/docs/en/build-with-claude/embeddings | "special prompts are prepended to the input text prior to embedding." | high |
| Voyage query prompt text | https://platform.claude.com/docs/en/build-with-claude/embeddings | "Represent the query for retrieving supporting documents: " | high |
| Gemini task_type is supported on gemini-embedding-001 | https://ai.google.dev/gemini-api/docs/embeddings | "For `gemini-embedding-001`, you can specify the `task_type` in the `embedContent` method." | high |
| Gemini task_type is not supported on gemini-embedding-2 | https://ai.google.dev/gemini-api/docs/embeddings | "You cannot use the `task_type` field for the `gemini-embedding-2` model." | high |
| BGE English query instruction | https://huggingface.co/BAAI/bge-small-en-v1.5 | "Represent this sentence for searching relevant passages:" | high |
| BGE passages need no instruction | https://huggingface.co/BAAI/bge-small-en-v1.5 | "In all cases, the documents/passages do not need to add the instruction." | high |
| BGE-small-en-v1.5: 384 dims, 512 max sequence length | https://huggingface.co/BAAI/bge-small-en-v1.5 | (table values: 384 / 512) | medium (table, not sentence) |
| OpenAI 8192-token per-input limit | https://developers.openai.com/api/reference/resources/embeddings/methods/create | "The input must not exceed the max input tokens for the model (8192 tokens for all embedding models)" | high |
| OpenAI 300k tokens per request | https://developers.openai.com/api/reference/resources/embeddings/methods/create | "maximum of 300,000 tokens summed across all inputs in a single request." | high |
| Gemini 8192-token limit with silent truncation | https://ai.google.dev/gemini-api/docs/embeddings | "The system silently truncates inputs that exceed this limit." | high |
| sentence-transformers truncates beyond max_seq_length | https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html | "Longer texts will be truncated to the first `model.max_seq_length` tokens" | high |
| max_seq_length cannot exceed the underlying model's maximum | https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html | "You cannot increase the length higher than what is maximally supported by the respective transformer model." | high |
| Gemini 001 and 2 embedding spaces are incompatible | https://ai.google.dev/gemini-api/docs/embeddings | "The embedding spaces between `gemini-embedding-001` and `gemini-embedding-2` are **incompatible**." | high |
| Upgrading Gemini model requires re-embedding all data | https://ai.google.dev/gemini-api/docs/embeddings | "you must re-embed all of your existing data." | high |
| Switching models requires re-embedding (VENDOR: Qdrant) | https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/ | "Switching models requires re-embedding all vectors in your collection, which can take time." | high |
| gemini-embedding-2 is multimodal (provider-specific, fast-changing) | https://ai.google.dev/gemini-api/docs/embeddings | "the first multimodal embedding model in the Gemini API." | high (as of 2026-10-09) |
| gemini-embedding-2 maps multiple modalities to one space | https://ai.google.dev/gemini-api/docs/embeddings | "maps text, images, video, audio, and documents into a unified embedding space" | high |
| OpenAI recommends the dimensions parameter for shortening | https://developers.openai.com/api/docs/guides/embeddings | "In general, using the `dimensions` parameter when creating the embedding is the suggested approach." | high |
| Larger embeddings cost more compute/memory/storage | https://developers.openai.com/api/docs/guides/embeddings | "generally costs more and consumes more compute, memory and storage than using smaller embeddings." | medium (fragment) |
| Manual truncation requires re-normalization (OpenAI) | https://developers.openai.com/api/docs/guides/embeddings | "When you change the dimension manually, you need to be sure to normalize the dimensions of the embedding" | high |
| dimensions only on text-embedding-3 and later | https://developers.openai.com/api/reference/resources/embeddings/methods/create | "Only supported in `text-embedding-3` and later models." | high |
| OpenAI embeddings are unit-normalized | https://developers.openai.com/api/docs/guides/embeddings | "OpenAI embeddings are normalized to length 1" | high |
| Gemini-embedding-2 auto-renormalizes reduced dimensions | https://ai.google.dev/gemini-api/docs/embeddings | "`gemini-embedding-2` introduces automatic renormalization for non-default dimensions." | high |
| Voyage quantization cuts storage 4x (int8) / 32x (binary) | https://platform.claude.com/docs/en/build-with-claude/embeddings | "reducing storage, memory, and costs by 4x and 32x, respectively." | high |
| BGE similarity scores are not calibrated to 0.5 | https://huggingface.co/BAAI/bge-small-en-v1.5 | "a similarity score greater than 0.5 does not indicate that the two sentences are similar." | high |
