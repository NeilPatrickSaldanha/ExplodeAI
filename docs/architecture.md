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
- **Challenges** are data: broken params, locked params, and checks (a gold
  phrase must be in a retrieved chunk or in the prompt). The server forces locked
  params back to their broken values, so the client cannot cheat.
- **Persistence** — SQLite via SQLModel: `LessonProgress` (merge-only, filtered to
  valid ids), `ExperimentRun` (params + summary of every run), `AIUsage` (ledger
  for limits and budgets).

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
