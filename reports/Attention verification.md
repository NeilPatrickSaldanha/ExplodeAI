# Attention verification

Research and verification report for **Lesson 04 · Attention, exploded**
(`content/lessons/attention/lesson.yaml`, version 1.0.0, status **published**).
Completed 2026-10-20.

> Three verification passes give each claim recorded, inspectable evidence. They do not
> guarantee absolute correctness. Documentation changes often; every source records the
> date or version it was read.

## Summary

| | |
|---|---|
| Claims | 31 (5 provider-specific: Hugging Face ×3, PyTorch, BERT/OpenAI/BAAI) |
| Citations | 66 verbatim excerpts (each ≤ 30 words) from 17 new sources: 11 papers, PyTorch and Hugging Face docs, a pinned model card and a research publication |
| Pass 1 (primary-source research) | 31/31 passed |
| Pass 2 (independent cross-check) | 16 confirmed · 13 confirmed with changes · 2 disputed · 0 unverifiable. All 66 excerpts were found in the raw sources; none fabricated. All fixes applied |
| Pass 3 (technical validation) | 14 executed and passing · 17 not applicable, each with a reason |
| Automated gates | content validator ✓ · claim-coverage gate ✓ · ruff ✓ · backend tests ✓ · unit tests ✓ · end-to-end tests ✓ |

**What this lesson's attention layer is.** Every "real execution" runs a **toy** self-attention
layer written from scratch in numpy (`backend/app/experiments/attend/`): each word gets a fixed
random vector, and the Q/K/V and output projections are fixed random matrices. It runs the real
mechanism, but nothing is trained, so its patterns say nothing about what a trained model attends
to. The UI, the API (`model.kind = "toy"`) and the lesson text say so wherever numbers are shown.
No paid API and no key was used at any stage.

## Pass 1 — primary-source research

Two researchers followed the `deep-research` skill, one on foundations (Vaswani, Bahdanau, the
interpretability papers, Elhage et al., PyTorch) and one on practice (FlashAttention, KV cache,
masking, head sizes, positions, MQA/GQA, softmax numerics). Excerpts were copied from raw downloads
(curl; PDFs through pypdf) and machine-checked as substrings.

- Notes: `research_notes/Attention primary sources/foundations.md` (40 claims) and `practice.md` (45 claims)

Caveats Pass 1 recorded before any lesson text was written:
- The √d_k argument is hedged by the authors ("We suspect"). Footnote 4 gives mean 0 and variance d_k only under an independence assumption.
- Jain & Wallace and Wiegreffe & Pinter studied recurrent models with attention, not Transformer self-attention.
- Elhage et al. analyse small attention-only models and call their work a research thread, not a peer-reviewed paper.
- "Attention Is All You Need" does not mean attention only: embeddings, positions, feed-forward layers, residuals and layer norm remain.
- pypdf drops superscripts in equations, so no equation is shown from an extracted excerpt.

## Pass 2 — independent cross-check

A separate agent re-downloaded every source, string-matched all 66 excerpts, found an independent
source for every claim, and ran the layer locally to check every behavioural statement, each
"breaks if removed" statement and both states of every challenge. Full report:
`research_notes/Attention primary sources/pass2_cross_check.md`.

Changes applied:
- **Bug:** the "attention on later words" figure was a sum over rows, not a fraction (the UI showed 261%). It is now divided by the number of words (43.5% for the default sentence).
- `attn-origin` (disputed): "first used" was not supported by the paper; rewritten as what Bahdanau et al. introduced and found.
- `attn-explanation-contested` (disputed): "RNN models" corrected to "mainly recurrent (LSTM) models".
- `attn-scaling-reason`, `attn-softmax-saturation`: the excerpt now includes the words the claim relies on. The saturation claim is labelled as a property of the formula, not stated by a source, and the irrelevant PyTorch excerpt was dropped.
- `attn-sqrt-dk-scaling`: the step "dividing brings it back to about 1" is labelled as simple arithmetic, not a sentence in the paper.
- The "Cat" preset note said repeated words attend to each other strongly. That is false for random weights, so it was replaced.
- Input vectors are now rescaled so that their components keep unit variance with positions added; the displayed expected spread now matches the measured one.
- Smaller: "positive" → "non-negative" weights; scope added to the Elhage claim; KV-cache formula scoped to one sequence and plain multi-head attention; RoPE excerpt corrected; FlashAttention O(N) excerpt added; self-attention-includes-itself citation added; challenge explanations corrected (four or more narrower heads; causal mask is locked in the order challenge); analogies reworded; tokenizer limitation (a–z only) disclosed.

## Pass 3 — technical validation

Executed against the real layer (`backend/tests/test_attend.py`, `test_attend_ablation.py`):

| Claim | Test |
|---|---|
| attn-weighted-sum, attn-qkv-projections, attn-scaled-dot-product | Output matches an independent plain-Python loop implementation across head counts, masks and settings |
| attn-softmax-weights | Every row of every head sums to 1 and no weight is negative |
| attn-softmax-stable | Softmax stays finite and sums to 1 for scores around 1000 |
| attn-sqrt-dk-scaling | Unscaled score variance is close to d_k, scaled variance close to 1 |
| attn-softmax-saturation | Unscaled 64-wide head: strongest weight averages over 85%; scaled: under 60% |
| attn-multihead-concat | d_k = d_model/h, and the heads concatenate back to d_model |
| attn-heads-additive | Concatenate-then-project equals the sum of per-head slices |
| attn-causal-mask | All weights on later words are exactly 0; the first word attends only to itself |
| attn-position-needed | Reversing the sentence only reverses the outputs when positions and mask are off |
| attn-position-encoding | Positions equal the published sin/cos formula |
| attn-quadratic-cost | The score grid has n² entries per head |
| attn-kv-cache-valid | With the mask on, a prefix's outputs, keys and values do not change when later words arrive; with it off they do |
| (8 stages) | Ablation tests back every "breaks if removed" statement |
| (3 challenges) | Each fails when broken and passes when fixed; locked parameters cannot be overridden |

Not applicable (each with a reason in the lesson file): benchmark and motivation statements from
papers, provider and library behaviour, design history, and interpretive framings.

## Visual honesty

| Visual | Kind |
|---|---|
| Exploded view, data flow | Conceptual |
| Experiment, ablation, attention grid | Real execution of a **toy** layer with fixed random weights |

The grid encodes weights by fill height and a printed number, hatches masked cells and prints "–",
and is a real table with row and column headers, so colour is never the only cue.
