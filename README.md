# ExplodeAI

Learn AI engineering by taking systems apart. Each lesson is an interactive 3D
exploded view of a real system: rotate it, pull it apart, isolate a part, run it
for real with your own parameters, break it on purpose, and rebuild it. Every
technical claim links to its sources and records three verification passes.

**Status:** foundation plus three lessons, each with every claim through all three passes:
[Retrieval-Augmented Generation, exploded](content/lessons/rag-pipeline/lesson.yaml),
[Tokenization, exploded](content/lessons/tokenization/lesson.yaml) and
[Embeddings, exploded](content/lessons/embeddings/lesson.yaml). See
[Limitations](#limitations).

## Learning experience

Every stage has an "Understand this stage" panel (plain-language explanation, analogy, a
playable example, expandable depth, links to neighbouring stages), the Tour mode can play
itself with a visible countdown, and first-time visitors get an optional interactive
walkthrough that is remembered and can be replayed from "How to use".

## Quick start

Requirements: [uv](https://docs.astral.sh/uv/) ≥ 0.13, Node ≥ 22.

```bash
make setup   # backend deps (incl. local neural embedder) + frontend deps + Playwright Chromium
make dev     # API on :8000, web on http://127.0.0.1:5173
```

Or with Docker (no local Python/Node needed):

```bash
docker compose up --build   # same ports
```

No API keys are needed. Everything in the lesson runs locally and costs nothing.

## API keys and paid AI (optional)

Everything works with no keys. Paid answers are an optional extra in the RAG
lesson's **Experiment → Answer** tab ("Ask a real LLM"). The server builds the
prompt from the lesson's pipeline, so the endpoint can't be used as a
general-purpose paid proxy.

To turn it on, add **one** key to `backend/.env` (git-ignored) and restart the
backend: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` or `GEMINI_API_KEY`. Already
configured:

- `AI_FEATURES_ENABLED=true`, with `AI_EMERGENCY_DISABLE=true` as the kill switch.
- **`AI_TOTAL_BUDGET_USD=4.00`**: a lifetime cap enforced server-side before
  every call. There is also a $1/day cap, 10 requests/hour, a 300-token output
  cap, and a 20 s timeout.
- An allow-list with prices copied from the official pricing pages on 2026-10-19
  (`backend/app/ai/pricing.yaml`): `claude-haiku-5-5`, `gemini-3.1-flash-lite`,
  `gpt-4.1-nano`. One lesson answer costs well under $0.001 (live tests on 2026-10-19: $0.00003–$0.00011).
- The worst-case cost is shown before each click, and each click is one confirmed
  request. The ledger records the actual cost from the provider's reported token
  counts, so the $4 cap tracks real spend.

Keys stay in the backend. The API only ever reports whether a key is *present*,
and the test suite blanks all keys so tests can never make a paid call.

## Repository layout

| Path | What it is |
|---|---|
| `frontend/src/engine/` | Reusable exploded-view engine (3D, 2D fallback, keyboard, labels, camera fit) |
| `frontend/src/lessons/rag/` | The RAG lesson: explore, tour, experiment, break & fix, rebuild |
| `backend/app/experiments/rag/` | Real pipeline: chunking, embedding, BM25, RRF, PCA, prompt assembly |
| `frontend/src/lessons/tokenization/` | The tokenization lesson: token strip, merge replay, trade-off chart, plus the shared modes |
| `frontend/src/lessons/embeddings/` | The embeddings lesson: semantic-space map, neighbours, token and vector views |
| `backend/app/experiments/embed/` | bge-small-en-v1.5 opened into its stages: tokenize, encode, pool, normalize, rank, PCA (needs `--extra neural`) |
| `backend/app/experiments/tokenize/` | Educational byte-pair-encoding tokenizer: pre-tokenize, byte/char alphabet, merge training, encode, decode |
| `backend/app/content/` | Content schema + publishing rules |
| `backend/app/ai/` | Paid-AI guard and provider clients |
| `content/` | Lessons (`lessons/*/lesson.yaml`) and the source registry (`sources.yaml`) |
| `research_notes/`, `reports/` | Pass 1 and Pass 2 research evidence and verification reports |
| `docs/` | Architecture, content schema, verification workflow, testing, design system, scaling |

## Tests

```bash
make test        # content validation + backend + frontend unit + end-to-end
make validate    # just the content gate (citations, sources, verification passes)
```

CI (`.github/workflows/ci.yml`) runs the same four jobs on every push and PR. See
[docs/testing.md](docs/testing.md).

## How lessons are verified

Every claim passes **primary-source research → independent cross-check →
technical validation** before a lesson can be published. The validator refuses to
publish otherwise. Passing three checks does not guarantee a claim is correct; it
means each claim has recorded, inspectable evidence. See
[docs/verification-workflow.md](docs/verification-workflow.md) and the
[RAG](reports/RAG%20pipeline%20verification.md) and
[tokenization](reports/Tokenization%20verification.md) and
[embeddings](reports/Embeddings%20verification.md) verification reports.

## Limitations

- **Three lessons so far.** The engine and content pipeline are lesson-agnostic; RAG, tokenization and embeddings are built.
- **Lesson 03 needs the local model.** It runs BAAI/bge-small-en-v1.5 via Qdrant's reduced-precision ONNX port (fastembed), downloaded once and cached. It is free and needs no key; without `uv sync --extra neural` its endpoints return 503. The Docker image includes it. Results are for that build, not measured against BAAI's original weights.
- **The tokenizer is educational.** Lesson 02 trains a small BPE on a 1 KB fictional corpus. It shows how BPE works, but its token counts say nothing about GPT, Claude or Gemini tokenizers, and no provider tokenizer or token-counting API is ever called.
- **The default embedder is lexical** (TF-IDF features folded into 1024 dims by hashing). The lesson says so everywhere it matters. The optional local neural model (`uv sync --extra neural`, BAAI/bge-small-en-v1.5) shows semantic matching.
- **No LLM in the default answer step.** The offline answer is a labelled extractive baseline. The paid-provider clients are tested only against mocked HTTP; they have never been called live.
- **Word counts, not tokens.** Chunk sizes and context budgets are counted in words, so they don't imply any specific tokenizer.
- **Anonymous progress.** Progress is keyed to a random id stored in the browser; there are no accounts.
- **Single-node SQLite.** This is fine for local use and small deployments; see [docs/scaling.md](docs/scaling.md).
