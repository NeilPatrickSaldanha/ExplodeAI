# Architecture

```
browser ──► Vite/React app ──/api──► FastAPI ──► content/ (YAML lessons + sources)
              │                         ├──► experiments (real pipeline, numpy)
              │ three.js (lazy chunk)   ├──► SQLite (progress, runs, AI ledger)
              └ exploded-view engine    └──► paid-AI guard ──► provider HTTP (off by default)
```

## Frontend

- **Engine (`frontend/src/engine/`)** — lesson-agnostic. A lesson describes its
  system as an `AssemblySpec`: parts (shape, size, assembled position, explode
  offset, group) and links (source → target, payload label). The engine provides:
  - `ExplodedCanvas`: react-three-fiber scene with an explode factor (eased, with
    a mid-flight lift), per-shape *sub-explosions* (slices separate, disks stack,
    lens elements part), isolation (non-neighbours fade), animated packets along
    links, and a camera rig that binary-searches the distance at which every part
    fits the viewport. Portrait screens orbit 90° so long pipelines run vertically.
  - Labels are plain DOM elements projected from 3D each frame by `LabelProjector`
    (no nested React roots, no per-frame React renders).
  - `FlatDiagram`: SVG top-down fallback using the same spec. It's used without
    WebGL, on request, and in tests. Every part is a focusable button.
  - `ExplodedView`: picks 3D or 2D. Arrow keys cycle parts, Enter isolates,
    Esc clears, and an `aria-live` region announces the selection.
  - Colours come from CSS tokens (`resolveTokenColor` rasterises `oklch()` to sRGB)
    and re-resolve on theme change. Reduced motion is live (follows OS changes)
    and can be overridden in the UI ("Calm").
- **Lessons (`frontend/src/lessons/<id>/`)** — the interactive module for one
  lesson: an adapter from lesson YAML to the engine spec, live readouts from the
  last real run, and the five modes (Explore, Tour, Experiment, Break & fix,
  Rebuild).
- three.js and drei are lazy-loaded. The first paint ships only the React shell.

## Backend

- **FastAPI** (`backend/app/main.py`) with routers for lessons, experiments,
  progress, and AI. Settings come from `backend/.env` via pydantic-settings, and
  keys are `SecretStr`.
- **Content** (`backend/app/content/`) — YAML loaded into pydantic models;
  `validate_lesson` enforces publishing rules. Only `published` lessons are served
  unless `SHOW_DRAFT_LESSONS=true`. See [content-schema.md](content-schema.md).
- **Experiments** (`backend/app/experiments/rag/`) — every stage runs for real and
  is timed: chunking (fixed / sentence, with overlap and character offsets),
  embedding (lexical hashing by default; optional local neural model), exact flat
  index, BM25 (k1 = 1.2, b = 0.75), reciprocal rank fusion (k = 60), PCA to 3D,
  prompt assembly under a word budget, and an extractive answer baseline.
  `STAGE_DEPENDENCIES` is the contract shared with the lesson's 3D model and the
  rebuild puzzle; tests keep the three in sync.
- **Tokenization experiment** (`backend/app/experiments/tokenize/`) — an
  *educational* byte-pair-encoding tokenizer (not any provider's): simplified
  GPT-2-style pre-tokenization (or none), a 256-byte or training-character base
  alphabet, deterministic merge training on a fictional corpus, encoding that
  replays merges in learned (or, for a challenge, reversed) order with a per-merge
  trace, byte-exact decoding, and a vocabulary-size vs sequence-length sweep.
  Same `STAGE_DEPENDENCIES` contract as RAG.
- **Embeddings experiment** (`backend/app/experiments/embed/`) — bge-small-en-v1.5
  (Qdrant's ONNX port via fastembed, local CPU) opened into its stages so each
  intermediate is real: WordPiece tokens and ids, per-token vectors, [CLS] or mean
  pooling, L2 normalisation, cosine/dot/Euclidean ranking, and a PCA projection.
  `tests/test_embed.py` shows the hand-built stages reproduce fastembed's own output.
  The RAG lexical embedder is available as the contrast. Ablation lives in
  `embed/ablation.py` and `POST /api/experiments/embed/ablate`.
- **Attention experiment** (`backend/app/experiments/attend/`) — a *toy* self-attention layer
  built from scratch in numpy (fixed random word vectors and projections, sinusoidal
  positions, d_model 64, 1–8 heads): Q/K/V projections, n×n scores with optional 1/√d_k,
  an optional causal mask, a max-subtracted softmax, a weighted sum, concatenated heads and
  an output projection. Every statement is checked against an independent plain-Python loop
  implementation. Ablation lives in `attend/ablation.py`; checks are `no_future_attention`,
  `not_saturated` and `order_matters`.
- **Tutor** (`backend/app/tutor/`, `routers/tutor.py`) — a RAG system over the lessons
  themselves. `index.py` splits every lesson into ~470 passages (claims, stage explanations,
  tours, challenges), each linked to its verified claims and sources; analogies are flagged as
  teaching aids. `search.py` fuses BM25 and the local bge embedder with reciprocal rank fusion,
  nudges towards the open lesson and stage (more when the question is vague), and gates relevance:
  a question the lessons do not cover returns nothing. `answer.py` quotes the best sentences and
  attaches the claims and sources behind each, led by the stage's plain-words block (`plain_block`,
  taken verbatim from `explain.yaml`). `intent.py` and `chat.py` handle small talk and follow-ups: the
  client sends the last few turns back (the server keeps no conversation state), and "simpler",
  "example", "more" and "why does that matter" are answered about the stage the conversation was on.
  `quiz.py` builds tutor-mode questions from stage explanations. `prompt.py` builds the paid prompt on the server from retrieved passages only and
  strips any citation to a claim that was not in it. Retrieval quality is measured by
  `tests/test_tutor_eval.py` on 30 in-scope and 13 out-of-scope questions.
- **Challenges** are data: broken params, locked params, and checks. Each
  experiment engine declares the check types it can evaluate (`ENGINE_CHECKS` in
  the schema): RAG checks gold phrases in retrieved chunks or the prompt;
  tokenization checks round trip, unknown tokens, a token budget, single-token
  words, and merges that cross word boundaries; embeddings checks the top
  match's topic and whether query and library vectors are comparable. The server forces locked params
  back to their broken values, so the client cannot cheat.
- **Persistence** — SQLite via SQLModel: `LessonProgress` (merge-only, filtered to
  valid ids), `ExperimentRun` (params + summary of every run), `AIUsage` (ledger
  for limits and budgets).

## Ablation ("what breaks if removed?")

`backend/app/experiments/rag/ablation.py` runs the real pipeline with one stage
removed and returns a compact outcome; `POST /api/experiments/rag/ablate` returns
it next to the full-pipeline outcome. Each component's `breaks_if_removed` text
in the lesson YAML describes this executable behaviour and is checked by
`tests/test_ablation.py` (Pass 3 evidence for implementation statements, which
need no external citation).

Lesson 02 has the same mechanism for its tokenizer:
`backend/app/experiments/tokenize/ablation.py` and
`POST /api/experiments/tokenize/ablate` (checked by
`tests/test_tokenize_ablation.py`). Removing the corpus leaves zero merges, removing
the pre-tokenizer lets merges cross words, removing the base alphabet turns every
character into `[UNK]`, removing the merge learner leaves one token per base symbol,
and removing the vocabulary or encoder leaves no ids to decode.

## Paid AI guard

`backend/app/ai/guard.py` fails closed. In order, a request needs: kill switch off →
features enabled → key present → model allow-listed with prices in `pricing.yaml`
→ `confirm_paid: true` → output tokens ≤ cap → under the hourly limit → today's
estimated spend + this request's worst case ≤ budget. Estimates are conservative
(≈ 1 token per 3 characters, plus the full output allowance). Every attempt that
passes the guard is recorded, including failures, because failed calls may still be
billed. Provider errors never echo response bodies. The frontend never sees keys;
`/api/ai/status` reports presence only.

## Accessibility and responsiveness

- Keyboard: every action in the 3D scene has a list/button equivalent, sliders are
  Radix (arrow keys), and drag-and-drop rebuild has Move up/down buttons.
- Screen readers: the canvas has `role="img"` and a label, selection changes are
  announced, and every visual carries a text badge (real execution / simulation /
  conceptual).
- Motion: one orchestrated entrance. Flow packets can be paused, and reduced motion
  snaps all transitions and replaces moving packets with static direction markers.
- Mobile: container queries for the panel, numbered markers on phone-width
  scenes, no horizontal scroll (checked in e2e), 44px touch targets.
