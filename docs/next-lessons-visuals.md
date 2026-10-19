# Next lessons: visual proposals

Same design language as the Lesson 01 redesign: the exploded machine is the hero,
the stage panel shows first and explains second, an 8-stage-style bar sits below,
three flows are told apart by line style as well as colour, and every number on
screen comes from a real run. Each lesson still needs all three verification
passes (deep-research → independent cross-check → executable tests) before it
publishes. Nothing below is a verified claim yet.

## Lesson 02 · Tokenization, exploded (in progress in its own session)

The engine, experiment and verified content are being built now. Visual upgrade to
match Lesson 01 once that session finishes:

| Stage | Part in the machine | Goes in → comes out (real data) | Breaks if removed (ablation to test) |
|---|---|---|---|
| Text input | tilted glass card with your text | text → UTF-8 bytes (hex strip) | nothing to tokenize |
| Normalizer | stacked filter plates | raw → normalized text (diff highlight) | variants of the same character split into different tokens |
| Pre-tokenizer | slicer with word-shaped slots | text → pre-tokens (chips) | merges can cross word boundaries |
| BPE merge table | press with numbered dies | pieces → merged tokens (replay with step slider) | text stays as single bytes, so sequences get long |
| Token IDs | numbered drawer rack | tokens → integer IDs (badges) | the model has nothing numeric to read |
| To model | connector block | IDs → sequence length vs. budget gauge | none (output stage) |

- **Flows:** text (solid), bytes and IDs (dashed), your input (dotted).
- **Signature visual:** a merge replay where the active merge pair lights up in the press and the token strip re-segments in step.
- **Mini 2D chart:** vocabulary size vs. tokens per input (the lesson's existing trade-off chart), with the current setting marked.

## Lesson 03 · Embeddings, exploded

Based on the Embeddings concept image. It builds directly on Lessons 01 and 02.

| Stage | Part | Goes in → comes out | Breaks if removed |
|---|---|---|---|
| Text input | glass card | sentence → text | — |
| Tokenizer | reuses Lesson 02's machine, collapsed | text → tokens | the model can't read raw text |
| Embedding model | lens stack with a pooling plate | tokens → vector (strip of real values) | no vectors, so no similarity search |
| Vector | a column of number cells | vector → normalised vector (length shown) | cosine ≠ dot product (Lesson 01 claim reused) |
| Semantic space | 3D scatter with labelled clusters | vectors → nearest neighbours | nothing to compare |
| Applications | three hooks: search · cluster · classify | neighbours → result | — |

- **Hero interaction:** type a sentence and watch a new point fly into the 3D semantic space and land near its neighbours. This uses the local neural model (`--extra neural`), so it's a real execution, free, and needs no API keys.
- **Break & fix:** the lexical embedder places "money back" far from "refunds" while the neural model places them close. Fix it by switching embedders or adding synonyms.
- **Honesty label:** a PCA "variance kept" badge on every 3D projection, as in Lesson 01.

## Later candidates (ordered by how well they fit the exploded-machine metaphor)

1. **Attention, exploded:** Q/K/V projection plates, a score grid, softmax, a weighted sum. A real tiny attention computation runs on the backend; the heat-grid is the 2D precision view.
2. **Tool-using agent, exploded:** planner → tool router → tools → observation → memory loop. The loop is the hero animation; it runs offline with deterministic stub tools, clearly labelled as simulation.
3. **Evaluation harness, exploded:** dataset → runner → grader → metrics, reusing Lesson 01's challenges as test cases.
