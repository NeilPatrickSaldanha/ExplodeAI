# Embeddings verification

Research and verification report for **Lesson 03 · Embeddings, exploded**
(`content/lessons/embeddings/lesson.yaml`, version 1.0.0, status **published**).
Completed 2026-10-19.

> Three verification passes give each claim recorded, inspectable evidence. They do
> not guarantee absolute correctness. Provider documentation changes often; every
> source records the date it was read.

## Summary

| | |
|---|---|
| Claims | 24 (7 provider-specific: BAAI ×4, Voyage/Google, OpenAI ×2 or OpenAI/Google) |
| Citations | 53 excerpts (each ≤ 30 words) from the registered sources: 9 papers, the BGE model card and pinned config files, fastembed code, and OpenAI, Google, Anthropic/Voyage and Qdrant docs |
| Pass 1 (primary-source research) | 24/24 passed |
| Pass 2 (independent cross-check) | 11 confirmed · 11 confirmed with changes · 2 disputed · 0 unverifiable. All 47 original excerpts were found in the raw sources; none was fabricated. All fixes applied |
| Pass 3 (technical validation) | 13 executed and passing · 11 not applicable, each with a reason |
| Automated gates | content validator ✓ · claim-coverage gate ✓ · 185 backend tests passing |

**What this lesson's model is.** Every "real execution" runs **bge-small-en-v1.5
as served by Qdrant's ONNX export through fastembed** (`Qdrant/bge-small-en-v1.5-onnx-Q`),
locally, on CPU. Qdrant's card calls it a "Quantized ONNX port" while its config
suggests fp16; it has not been measured against BAAI's original weights, and the
lesson says "reduced-precision ONNX port". No paid API, hosted embedding service or key
was used at any stage. The "lexical" embedder is ExplodeAI's own hashing embedder from
Lesson 01.

## Pass 1 — primary-source research

Done with the `deep-research` skill: three parallel researchers, then a report writer.

- Notes: `research_notes/Embeddings primary sources/` (`embedding_foundations.md`, `similarity_geometry.md`, `embeddings_in_practice.md`)
- Synthesis: `reports/Embeddings primary sources.md` (source register, ~150-row claims table, 11 conflicts, 20 gaps)

Caveats Pass 1 caught before any lesson text was written:
- Qdrant's export is labelled "quantized" but its config indicates fp16, not int8. The lesson never says int8.
- BGE's "scores fall in [0.6, 1]" describes v1, not v1.5. The lesson teaches no score range.
- fastembed adds no query prefix; the BGE instruction must be prepended by the caller, which is what the experiment does.
- The "24M" parameter figure in the C-Pack paper is the Chinese small model, so it is not used.
- OpenAI's blog returned HTTP 403 and was not cited.

## Pass 2 — independent cross-check

A separate agent re-downloaded every cited source, string-matched the excerpts, found
independent sources, and checked all lesson text against the implementation. Full
report: `research_notes/Embeddings primary sources/pass2_cross_check.md`.

Changes applied:
- `pooling-strategies` (disputed): "pooling matters little" held only for NLI classification training. With regression training, max pooling scored far below mean. Claim and excerpts rewritten.
- `word2vec-analogy` (disputed): the king/queen example is §1.1, credited to earlier RNN work, and needs the input words excluded. Claim rewritten around the paper's own Paris − France + Italy example.
- `models-not-comparable`: Voyage documents that its 4-series models share one space. Claim now says "generally" and names the exception; Voyage docs added as a source.
- `scores-uncalibrated`: the BGE ">0.5" quote describes v1. Replaced with the card's v1.5 note; the anisotropy locator fixed.
- `bge-query-instruction`: "never" softened to "passages don't need it", plus "test both". The `short-query` challenge explanation no longer claims the model card says the model was trained with an instruction.
- `input-limits`: the silent-truncation statement is documented only for gemini-embedding-2.
- `raw-bert-poor`: true on average only (averaged BERT beats GloVe on one benchmark); now says so.
- `query-document-asymmetry`: added the Gemini excerpt that actually shows the asymmetry.
- Smaller: MTEB dated to the 2022 paper; "always loses information" → "generally"; "one of the most common uses" → "a common use"; four locators fixed; SBERT source pinned to v1; Voyage docs registered.
- Implementation text: experiment visual relabelled "reduced-precision ONNX port"; `synonym-blind` brief now says "content word"; the "Where it goes wrong" preset explains why the train ranks only 14th of 24.
- Experiment: the text box was capped at 300 characters, so truncation could never be seen. The limit is now 4,000 and a "Long text" preset demonstrates the 512-token cut-off (verified: 512 tokens, `truncated: true`).
- Two challenge definitions were missing locked parameters in `broken_params`; fixed and now covered by a regression test.

Known thin margin: the `short-query` fix wins narrowly (bus 0.5146 vs desk 0.5017 in Pass 2). It is regression-tested, and the lesson text calls it a tendency, not a guarantee.

## Pass 3 — technical validation

Executed against the real model (`backend/tests/test_embed.py`, `test_embed_ablation.py`):

| Claim | Test |
|---|---|
| bge-cls-normalized | Hand-built tokenizer → encoder → [CLS] → L2 matches fastembed (cosine ≈ 1) |
| bge-dims | Output is 384-dimensional |
| bert-cls-token, wordpiece-subwords | Input is wrapped in [CLS] … [SEP]; a rare word splits into ## pieces |
| bge-max-tokens | A 900-word input is cut to 512 tokens with [SEP] last |
| contextual-vectors | "bank" gets different vectors in two contexts |
| unit-vector-metrics | cos = dot, ‖a−b‖² = 2 − 2cos, identical rankings |
| semantic-similarity, lexical-vs-neural | Neural finds the bookshelf for "a place to put my books"; lexical scores 0 |
| models-not-comparable | Lexical (1024-D) vs neural (384-D) is refused |
| bge-query-instruction | The instruction is prepended to the model input |
| scores-uncalibrated | Cross-topic cosine averages well above 0.25 (measured ≈ 0.41); random directions ≈ 0 |
| projection-lossy | The 3D PCA keeps under 90% of the variance |
| (all 8 stages) | Ablation tests back every `breaks_if_removed` statement |
| (3 challenges) | Each fails when broken and passes when fixed |

Not applicable (each with a reason in the lesson file): historical or benchmark results from
papers (word2vec, SBERT, MTEB, t-SNE cautions, contrastive training), provider behaviour
that would need paid calls (query/document asymmetry, input limits, Matryoshka
dimensions), and the use-case list.

## Visual honesty

| Visual | Kind |
|---|---|
| Exploded view, data flow | Conceptual |
| Experiment, ablation | Real execution |
| Semantic space | Real data, **approximate** projection (PCA; the UI states the variance kept and offers a table view) |

## Gates at publication

- Content validator ✓, claim-coverage gate ✓, ruff ✓, 185 backend tests ✓, 25 frontend unit tests ✓, 29 end-to-end tests across all lessons ✓.
- 8 end-to-end tests for this lesson (3D render, real experiment, table view, 512-token cut-off, ablation, break & fix, tour) ✓.
- Visual check on desktop (dark and light) and phone: no horizontal scroll, labels inside the canvas.
- Docker image includes the `neural` extra; CI e2e job installs it and caches the model.
