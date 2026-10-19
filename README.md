# ExplodeAI

Learn AI engineering by taking systems apart. Each lesson is an interactive 3D
exploded view of a real system: rotate it, pull it apart, isolate a part, run it
for real with your own parameters, break it on purpose, and rebuild it. Every
technical claim links to its sources and records three verification passes.

**Status:** foundation plus one complete lesson,
[Retrieval-Augmented Generation, exploded](content/lessons/rag-pipeline/lesson.yaml)
(published, 32/32 claims through all three passes). See
[Limitations](#limitations).

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

## API keys and paid AI (optional, off by default)

`backend/.env` (git-ignored) holds empty `OPENAI_API_KEY`, `GEMINI_API_KEY` and
`ANTHROPIC_API_KEY` placeholders; `backend/.env.example` documents every setting.
Paid calls are **impossible** until you deliberately:

1. add a key to `backend/.env`,
2. set `AI_FEATURES_ENABLED=true`,
3. allow-list the model with prices you copied from the provider's pricing page in
   [`backend/app/ai/pricing.yaml`](backend/app/ai/pricing.yaml) (ships empty), and
4. send `confirm_paid: true` with each request.

The backend also enforces a per-learner hourly request limit, a daily estimated
budget, a max-output-token cap, a request timeout, and an emergency kill switch
(`AI_EMERGENCY_DISABLE=true` blocks everything). Keys never leave the backend; the
API only reports whether a key is *present*. See
[docs/architecture.md § Paid AI guard](docs/architecture.md#paid-ai-guard).

## Repository layout

| Path | What it is |
|---|---|
| `frontend/src/engine/` | Reusable exploded-view engine (3D, 2D fallback, keyboard, labels, camera fit) |
| `frontend/src/lessons/rag/` | The RAG lesson: explore, tour, experiment, break & fix, rebuild |
| `backend/app/experiments/rag/` | Real pipeline: chunking, embedding, BM25, RRF, PCA, prompt assembly |
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
[RAG verification report](reports/RAG%20pipeline%20verification.md).

## Limitations

- **One lesson so far.** The engine and content pipeline are lesson-agnostic, but only RAG is built.
- **The default embedder is lexical** (TF-IDF features folded into 1024 dims by hashing). The lesson says so everywhere it matters. The optional local neural model (`uv sync --extra neural`, BAAI/bge-small-en-v1.5) shows semantic matching.
- **No LLM in the default answer step.** The offline answer is a labelled extractive baseline. The paid-provider clients are tested only against mocked HTTP; they have never been called live.
- **Word counts, not tokens.** Chunk sizes and context budgets are counted in words, so they don't imply any specific tokenizer.
- **Anonymous progress.** Progress is keyed to a random id stored in the browser; there are no accounts.
- **Single-node SQLite.** This is fine for local use and small deployments; see [docs/scaling.md](docs/scaling.md).
