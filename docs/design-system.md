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
