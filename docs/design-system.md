# Design system

Built with the **Hallmark**, **ui-ux-pro-max** and **ui-styling** skills.

**Hallmark · v1.1.0**

- **Genre** · atmospheric (AI tool, dark canvas)
- **Macrostructure** · Map / Diagram: a single spatial system organises the page
- **Theme** · custom, tuned from Lumen. Night palette by default: `oklch(13% 0.014 265)` paper, molten-brass accent `oklch(76% 0.17 50)`. Day palette in light mode: cool bone paper, indigo accent `oklch(46% 0.24 268)`.
- **Type** · Instrument Serif (roman, lowercase display heads) · Geist (body, sentence case) · JetBrains Mono (UPPERCASE machine readouts, code, prompts)
- **Enrichment** · the 3D exploded view is the page's single apparatus. It's interactive, so three.js earns its place.
- **Nav / footer** · N9 edge-aligned minimal · Ft2 inline single line
- **Motion** · one load-time explosion · flow packets (pausable) · camera glide to the selected part
- **Slop test** · checked at handoff. Fixed: card-in-card panel border, off-scale paddings, missing hover/active states, hero padding balance, off-token axis colours.

Tokens live in [`frontend/src/styles/tokens.css`](../frontend/src/styles/tokens.css),
which starts with the Hallmark stamp. The run is recorded in `.hallmark/log.json`.

## Deliberate deviations from the Lumen catalog theme

- **Body text stays sentence case.** Lumen lowercases all prose. Lesson content
  depends on acronyms (BM25, HNSW, DPR, RRF) that must read correctly, so only
  display headings are lowercase.
- **Mono labels appear in many places.** Lumen's mono register *is* its label
  system: eyebrows, callouts, meter labels. Here it also marks live readouts,
  which are real values from the last run, never invented.
- **The meter strip is real.** Its bars are per-stage timings from the last real
  execution, not decoration.

## Lesson 02 additions (tokenization)

Component-scope Hallmark run: no new theme, macrostructure, nav or footer.
`frontend/src/lessons/tokenization/tokenization.css` adds only components, all
on existing tokens: the token strip (unknown and partial tokens are dashed *and*
labelled "UNKNOWN" / "PARTIAL", never colour alone), the merge replay (Previous /
Next / slider always; autoplay only when motion is allowed), and a single-series
trade-off line chart (one y-axis, current setting marked, hover readout, and the
same data as a table). Example chips now reach 44px on coarse pointers.

## Learning aids (all lessons)

- **Understand this stage** (`shared/cine/Understand.tsx`): short version always visible
  (what it does, a labelled analogy, connected-stage chips, a step-through example),
  everything else in native `<details>` sections (why, what happens to the data, where it
  goes, if set up wrong, learn more). Keyboard and screen-reader friendly, 44px rows.
- **First-run tutorial** (`shared/cine/Tutorial.tsx`): a spotlight dims everything but one
  control, a card explains it, and some steps ask the learner to do it (drag, zoom, move the
  slider, pick a stage, press Play). Next, Back, Skip, Finish, Esc to skip; a bottom sheet on
  phones. Remembered in `localStorage` (`explodeai.tutorial`), replayable from "How to use".
- **Tour Play/Pause**: a labelled Play/Pause button, a "PLAYING · NEXT STAGE IN 8s" state with
  a countdown bar, restart on the last step. Calm/reduced motion removes the animation.
- **Exploded layout**: each lesson adapter sets a per-axis `SPREAD` for its explode offsets;
  the camera frames the stretched layout with room for the toolbar, and labels are clamped
  inside the canvas, so parts separate widely without clipping.

## Lesson 01 redesign: cinematic exploded view

Hallmark `redesign`, single page, inside the existing boundaries (new components
plus a scoped stylesheet, now `lessons/shared/cine/cine.css`; nothing deleted). Mood: cinematic, technical.

- **Structure:** the exploded machine is the hero (about 75% of the width, 74dvh
  tall), with a slim stage panel on the right and a full-width 8-stage bar below.
  Mode tabs move into the header. The old part list and inspector are replaced by
  the stage bar and stage panel.
- **Show first, explain second:** each stage shows a close-up of its part (its
  sub-explosion opening and closing), what goes in and what comes out (real data
  from the last run: vector strips, top-k scores, the prompt budget bar), and a
  red "what breaks if removed?" card that runs the pipeline without the stage.
  Facts are collapsed to one line each and expand to their full citations.
- **Three flows, told apart by more than colour:** text (solid line, cube
  packets), vectors (dashed, spheres), and your question (dotted, diamonds,
  starting from a dashed "Your question" card). Tokens: `--scene-flow`,
  `--scene-flow-vector`, `--scene-flow-query`, defined for both themes.
- **Active stage:** emissive glow plus an accent bracket in the scene, a filled
  number badge and leader line on its callout, a raised card in the stage bar,
  brighter and faster packets on its links, and its data cards shown on those links.
- **Removed:** the separate part list (its job moved to the stage bar) and the
  long-text inspector as the default view.
- **Engine styles** (callouts, link data cards, 2D flow styles) live in
  `engine/engine.css`, so every lesson that uses the engine gets them.

## Shared cinematic shell (both lessons)

Lesson 02 now uses the same cinematic layout as Lesson 01, through a shared shell
in `frontend/src/lessons/shared/cine/`:

- `CineLesson` owns the layout, stage navigation (`goToStage` is the single source
  of truth: scene click, stage bar, panel arrows, keyboard, tour, auto-play), tour
  sync, auto-play, progress and the toolbar.
- `StagePanel`, `StageBar`, `StageIcon`, `PartCloseup`, `FlowLegend` (labels per
  lesson) and a generic `BreaksCard` (the caller supplies the ablation runner and
  the outcome renderer).
- Each lesson supplies only its own pieces: scene readouts, the in/out views
  (`rag/StageIO`, `tokenization/TokStageIO`), the outcome renderers (`ragOutcome`,
  `tokOutcome`) and its Experiment / Break & fix / Rebuild tabs.
- Lesson 02 flows: text (solid), symbols & ids (dashed), your text (dotted).
  Token chips in stage cards mark `[UNK]` with a dashed border *and* the text "[UNK]".

## Lesson 03 additions (embeddings)

- Categorical palette `--cat-1..4` (blue, yellow, magenta, green; dark and light
  sets) validated with the dataviz validator using `--pairs all`. Colour is never
  the only encoding: each topic also has a shape (sphere, box, cylinder, cone), the
  legend names them, and the semantic space has a table view.
- The semantic-space map is labelled "Real data, approximate projection" and states
  the share of variance PCA kept.
- Flows: text (solid), vectors (dashed), your text (dotted).

## From ui-ux-pro-max

- Pattern match: "Interactive 3D Configurator" (scene + minimal overlay UI).
- Three.js guidelines applied: canvas `role="img"` + label, live reduced-motion
  listener, aspect-aware camera, explicit framing.
- Its suggested Inter/Inter pairing was rejected under Hallmark's banned-defaults
  rule. The icon set is Phosphor (its default) and only Phosphor.

## From ui-styling

Radix UI primitives (Slider, Tabs, ToggleGroup) supply accessible keyboard and
ARIA behaviour. Styling is token-driven plain CSS rather than Tailwind, so every
value traces to one token file (Hallmark's locked-tokens rule).
