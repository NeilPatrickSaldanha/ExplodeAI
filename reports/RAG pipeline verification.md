# RAG pipeline verification

Research and verification report for **Lesson 01 · Retrieval-Augmented Generation, exploded**
(`content/lessons/rag-pipeline/lesson.yaml`, version 1.0.0, status **published**).
Completed 2026-10-18.

> Three verification passes give each claim recorded, inspectable evidence. They
> do not guarantee absolute correctness. Provider documentation changes often;
> every source records the date it was read.

## Summary

| | |
|---|---|
| Claims | 32 (7 provider-specific) |
| Sources cited | 23 (papers, official docs from Anthropic, OpenAI, Google, FAISS, Sentence Transformers, Elastic) |
| Pass 1 (primary-source research) | 32/32 passed |
| Pass 2 (independent cross-check) | 18 confirmed · 13 confirmed with changes · 1 disputed → rewritten from the paper · 0 unverifiable |
| Pass 3 (technical validation) | 12 executed and passing · 20 not applicable, each with a reason |
| Automated gates | content validator ✓ · claim-coverage gate ✓ · 75 backend tests · 16 frontend unit tests · 8 end-to-end tests |

## Pass 1 — primary-source research

Done with the `deep-research` skill: three parallel researchers (RAG foundations;
chunking & embeddings; retrieval & grounding), then a report writer.

- Notes: `research_notes/RAG pipeline primary sources/` (`rag_foundations.md`, `chunking_embeddings.md`, `retrieval_grounding.md`)
- Synthesis: `reports/RAG pipeline primary sources.md` (source register and 141-row claims table with confidence and re-check flags)

Corrections Pass 1 caught before any lesson text was written:
- The common BM25 defaults (k1 = 1.2, b = 0.75) come from Elasticsearch/Lucene, not Robertson & Zaragoza, who give ranges.
- Anthropic's Contextual Retrieval post says "rank fusion techniques"; it never names RRF.
- HNSW's logarithmic scaling is the authors' claim.

## Pass 2 — independent cross-check

A separate agent downloaded every cited source and string-matched all 51
excerpts against the raw text. All of them are present in their sources; the only
mismatches were formatting (Markdown backticks, PDF math notation). It also found
at least one independent source per claim and reviewed non-claim lesson text.
Full report: `research_notes/RAG pipeline primary sources/pass2_cross_check.md`.

Changes applied:
- `rag-definition`: Excerpt completed to the full source sentence.
- `rag-small-kb`: Dated: 200k figure is from Sep 2024; current context windows noted.
- `rag-paper-architecture`: Added BART-large excerpt (§2.3).
- `rag-paper-frozen-index`: Added the paper's second reason (not needed for strong performance).
- `openai-chunk-defaults`: Scoped to vector stores; "currently" qualifier added.
- `openai-embedding-dims`: Excerpt now includes "By default".
- `anthropic-no-embeddings`: Voyage is one example provider; input_type is recommended, not required.
- `flat-index-exact`: Replaced HNSW excerpt with one that states approximation; Faiss guidelines excerpt added.
- `hnsw-log-scaling`: Qualified: idealised graphs, low-dimensional experiments (full text §4.2).
- `bm25-defaults`: Added the k1 = 1.2 excerpt.
- `lexical-misses-synonyms`: Softened: synonym expansion exists; neural models "often" catch paraphrases.
- `hybrid-contextual-results`: Added 49% excerpt; results are averages under the best embedding setup.
- `dpr-beats-bm25`: DISPUTED as first written (SQuAD exception, §5.1 / Table 2); rewritten from the paper and re-checked.
- `prompt-docs-first`: Added the 20k+ token and multi-document qualifiers. Vendors differ (OpenAI GPT-4.1 guide).
- `rag-hallucination`: Added Magesh et al. 2024 (17–33% in RAG legal tools); Anthropic excerpt lengthened.

Non-claim text corrected after Pass 2:
- The lesson said nearby vectors "should mean related text" without noting that the built-in embedder is lexical. The embedder detail, tour step, and experiment notice now say so, and the synonym preset is labelled as failing with it.
- The query embedder description wrongly said "the same model"; DPR trains a separate question encoder.
- Challenge explanations overstated RRF ("keeps chunks either ranker places highly"), generalised "larger chunks fix both", and contradicted the context-budget stage. All three were reworded.
- A challenge linked a claim that didn't support it; the link was removed.
- Sources no longer cited were removed from the registry; two sources were added (Faiss index guidelines, Magesh et al. 2024).

## Pass 3 — technical validation

Executable evidence (backend `pytest`; neural tests use BAAI/bge-small-en-v1.5
locally, which is free and needs no API key):
- `rag-swap-index`: test_replacing_the_corpus_changes_the_answer_without_other_changes.
- `chunking-affects-retrieval`: test_overlap_keeps_a_boundary_fact_intact; test_challenge_fails_when_broken_and_passes_when_fixed.
- `chunking-overlap`: test_overlap_keeps_a_boundary_fact_intact.
- `embedding-definition`: test_neural_embedding_places_a_paraphrase_closer_than_unrelated_text (bge-small-en-v1.5, local).
- `cosine-dot-normalized`: test_dot_product_equals_cosine_for_unit_vectors.
- `bi-encoder`: test_chunk_vectors_do_not_depend_on_the_query (consistency of ExplodeAI pipeline).
- `flat-index-exact`: test_flat_index_matches_brute_force_ordering. Exactness only; HNSW speed/accuracy trade-off rests on sources..
- `bm25-mechanics`: test_bm25_term_frequency_saturates; test_bm25_b_zero_ignores_document_length.
- `bm25-defaults`: test_bm25_uses_elasticsearch_defaults (consistency).
- `lexical-misses-synonyms`: test_lexical_retrieval_misses_a_synonym_only_query; test_neural_retrieval_finds_refunds_where_lexical_fails.
- `rrf`: test_rrf_matches_formula_and_ignores_raw_scores.
- `prompt-docs-first`: test_prompt_puts_documents_first_and_question_last (template consistency, not model behaviour).

Diagram and animation consistency (in `test_pipeline_and_content.py`):
- The 3D components equal the executed pipeline stages, in order.
- The diagram edges equal the stage dependency graph used by the rebuild puzzle, and any topological order is accepted.
- Each of the four break/fix challenges fails in its broken state and passes with a known fix that uses only unlocked controls. The server enforces locked params.
- The vector-space plot uses a real PCA projection of the real vectors, and the UI states the variance kept.

Not executable (`not_applicable`):
- `rag-definition`: Definition; the experiment demonstrates it but cannot prove a definition.
- `rag-private-knowledge`: Motivation statement; not executable.
- `rag-small-kb`: Vendor guidance tied to Claude context windows; would need paid calls to test.
- `rag-paper-architecture`: Historical fact about a paper.
- `rag-paper-chunks`: Historical fact about a paper.
- `rag-paper-frozen-index`: Historical fact about a paper.
- `rag-sequence-token`: Describes the paper's model; ExplodeAI does not train generators.
- `chunking-context-loss`: Generating context per chunk needs a paid model call.
- `openai-chunk-defaults`: Provider default; verifying it would need the paid API.
- `openai-embedding-dims`: Provider behaviour; verifying it would need the paid API.
- `anthropic-no-embeddings`: Provider documentation fact.
- `dpr-dot-product`: Describes the paper's model.
- `hnsw-log-scaling`: No HNSW implementation in this lesson.
- `hybrid-contextual-results`: Reproducing needs the vendor's dataset and paid model calls.
- `rerank-cross-encoder`: No cross-encoder model in the offline lesson.
- `dpr-beats-bm25`: Benchmark result from the paper.
- `lost-in-middle`: Needs many paid LLM calls to reproduce.
- `rag-hallucination`: Requires LLM evaluation.
- `citations-feature`: Provider feature; needs paid calls.
- `grounding-definition`: Definition.

## Implementation statements (added 2026-10-19)

The redesign added a "what breaks if removed?" statement for each of the 8
stages. They describe ExplodeAI's own executable pipeline, not the world, so they
are validated by execution instead of citation: `backend/tests/test_ablation.py`
removes each stage, runs the pipeline, and checks the stated effect (12 tests).
The UI shows the same real run side by side, labelled "Real execution, stage
removed". No new external claims were added, so no new research pass was needed.

## Clearly labelled non-claims

- **Conceptual:** the exploded layout and shapes, and the moving data-flow packets.
- **Real execution:** chunking, embedding, retrieval, prompt assembly, and stage timings.
- **Real execution, not an LLM:** the offline answer step, an extractive baseline.
- **Fictional sample data:** the six help-centre articles of a made-up bike shop.

## Residual risks

- Provider defaults and model names (OpenAI chunking 800/400, embedding dimensions, Voyage models, Claude context windows) are dated to 2026-10-18 and can change without notice.
- Vendor-reported results (Anthropic's 35/49/67% reductions) are from the vendor's own 2024 evaluation and have not been independently replicated.
- Pass 2 was one independent agent. A human subject-matter review would add a further check.
- The paid-provider HTTP clients have never been called live (that needs your keys and permission); their request shapes are tested against mocks only.

## Claim register

| Claim | Kind | Sources | P1 | P2 | P3 |
|---|---|---|---|---|---|
| `rag-definition` | definition | anthropic_contextual_retrieval, google_rag_engine | ✓ | ✓ | n/a |
| `rag-private-knowledge` | fact | google_rag_engine | ✓ | ✓ | n/a |
| `rag-small-kb` | provider specific (Anthropic) | anthropic_contextual_retrieval | ✓ | ✓ | n/a |
| `rag-paper-architecture` | fact | lewis2020rag | ✓ | ✓ | n/a |
| `rag-paper-chunks` | fact | lewis2020rag | ✓ | ✓ | n/a |
| `rag-paper-frozen-index` | fact | lewis2020rag | ✓ | ✓ | n/a |
| `rag-swap-index` | fact | lewis2020rag | ✓ | ✓ | ✓ |
| `rag-sequence-token` | fact | lewis2020rag | ✓ | ✓ | n/a |
| `chunking-affects-retrieval` | fact | anthropic_contextual_retrieval | ✓ | ✓ | ✓ |
| `chunking-overlap` | fact | langchain_recursive_splitter | ✓ | ✓ | ✓ |
| `chunking-context-loss` | fact | anthropic_contextual_retrieval | ✓ | ✓ | n/a |
| `openai-chunk-defaults` | provider specific (OpenAI) | openai_retrieval | ✓ | ✓ | n/a |
| `embedding-definition` | definition | openai_embeddings | ✓ | ✓ | ✓ |
| `cosine-dot-normalized` | fact | faiss_metrics, openai_embeddings | ✓ | ✓ | ✓ |
| `openai-embedding-dims` | provider specific (OpenAI) | openai_embeddings | ✓ | ✓ | n/a |
| `anthropic-no-embeddings` | provider specific (Anthropic) | anthropic_embeddings | ✓ | ✓ | n/a |
| `bi-encoder` | fact | reimers2019sbert, sbert_retrieve_rerank | ✓ | ✓ | ✓ |
| `dpr-dot-product` | fact | karpukhin2020dpr | ✓ | ✓ | n/a |
| `flat-index-exact` | fact | faiss_guidelines, malkov2016hnsw | ✓ | ✓ | ✓ |
| `hnsw-log-scaling` | fact | malkov2016hnsw | ✓ | ✓ | n/a |
| `bm25-mechanics` | fact | robertson2009bm25 | ✓ | ✓ | ✓ |
| `bm25-defaults` | fact | elasticsearch_similarity, robertson2009bm25 | ✓ | ✓ | ✓ |
| `lexical-misses-synonyms` | fact | sbert_retrieve_rerank | ✓ | ✓ | ✓ |
| `rrf` | fact | cormack2009rrf | ✓ | ✓ | ✓ |
| `hybrid-contextual-results` | provider specific (Anthropic) | anthropic_contextual_retrieval | ✓ | ✓ | n/a |
| `rerank-cross-encoder` | fact | sbert_cross_encoder | ✓ | ✓ | n/a |
| `dpr-beats-bm25` | fact | karpukhin2020dpr | ✓ | ✓ | n/a |
| `prompt-docs-first` | provider specific (Anthropic) | anthropic_prompting | ✓ | ✓ | ✓ |
| `lost-in-middle` | fact | liu2023lost | ✓ | ✓ | n/a |
| `rag-hallucination` | fact | anthropic_hallucinations, lewis2020rag, magesh2024legal | ✓ | ✓ | n/a |
| `citations-feature` | provider specific (Anthropic) | anthropic_citations | ✓ | ✓ | n/a |
| `grounding-definition` | definition | google_grounding | ✓ | ✓ | n/a |

## Sources

| id | Publisher | Type | Version read | Accessed |
|---|---|---|---|---|
| `anthropic_citations` | Anthropic (Claude Platform docs) | official docs | live page at access date | 2026-10-18 |
| `anthropic_contextual_retrieval` | Anthropic | official blog | published 19 Sep 2024 | 2026-10-18 |
| `anthropic_embeddings` | Anthropic (Claude Platform docs) | official docs | live page at access date (docs.claude.com redirects here) | 2026-10-18 |
| `anthropic_hallucinations` | Anthropic (Claude Platform docs) | official docs | live page at access date | 2026-10-18 |
| `anthropic_prompting` | Anthropic (Claude Platform docs) | official docs | live page at access date (older long-context tips page redirects here) | 2026-10-18 |
| `cormack2009rrf` | SIGIR 2009 (pp. 758–759, DOI 10.1145/1571941.1572114) | paper | author PDF of the SIGIR '09 short paper | 2026-10-18 |
| `elasticsearch_similarity` | Elastic documentation | reference | live page at access date | 2026-10-18 |
| `faiss_guidelines` | Meta AI Research — facebookresearch/faiss | official docs | GitHub wiki page at access date | 2026-10-18 |
| `faiss_metrics` | Meta AI Research — facebookresearch/faiss | official docs | GitHub wiki page at access date | 2026-10-18 |
| `google_grounding` | Google Cloud | official docs | last updated 2026-10-15 | 2026-10-18 |
| `google_rag_engine` | Google Cloud | official docs | last updated 2026-10-16 (page brands it part of Gemini Enterprise Agent Platform) | 2026-10-18 |
| `karpukhin2020dpr` | arXiv / EMNLP 2020 | paper | arXiv v3 (30 Sep 2020) | 2026-10-18 |
| `langchain_recursive_splitter` | LangChain documentation | framework docs | live page at access date | 2026-10-18 |
| `lewis2020rag` | arXiv / NeurIPS 2020 | paper | arXiv v4 (12 Apr 2021); full text read via ar5iv rendering | 2026-10-18 |
| `liu2023lost` | arXiv / TACL vol. 12 (2024), pp. 157–173 | paper | arXiv v3 (20 Nov 2023) PDF | 2026-10-18 |
| `magesh2024legal` | arXiv | paper | arXiv v1 (30 May 2024); abstract | 2026-10-18 |
| `malkov2016hnsw` | arXiv | paper | arXiv v4 (14 Aug 2018); abstract in Pass 1, full text read in Pass 2 | 2026-10-18 |
| `openai_embeddings` | OpenAI (API docs) | official docs | live page at access date (no date shown; platform.openai.com redirects here) | 2026-10-18 |
| `openai_retrieval` | OpenAI (API docs) | official docs | live page at access date (no date shown) | 2026-10-18 |
| `reimers2019sbert` | arXiv / EMNLP 2019 | paper | arXiv abstract page as of access date (submitted 27 Aug 2019) | 2026-10-18 |
| `robertson2009bm25` | Foundations and Trends in Information Retrieval 3(4), 333–389 (DOI 10.1561/1500000019) | paper | author-hosted PDF of the 2009 FnTIR monograph | 2026-10-18 |
| `sbert_cross_encoder` | Sentence Transformers documentation (Hugging Face) | framework docs | docs for sentence-transformers v6.1.0 | 2026-10-18 |
| `sbert_retrieve_rerank` | Sentence Transformers documentation (Hugging Face) | framework docs | docs for sentence-transformers v6.1.0 | 2026-10-18 |

## Re-running the checks

```bash
cd backend && uv sync --extra neural
uv run python scripts/validate_content.py
uv run pytest
cd ../frontend && npm test && npm run test:e2e
```
