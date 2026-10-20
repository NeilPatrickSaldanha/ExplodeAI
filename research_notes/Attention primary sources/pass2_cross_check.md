# Attention (Lesson 04) - Pass 2 independent factual cross-check

Date: 2026-10-20. Inputs: `content/lessons/attention/lesson.yaml` (31 claims, 66 excerpts, plus component, challenge, preset, tour and visual text), `explain.yaml` (8 stages), `content/sources.yaml`, and `backend/app/experiments/attend/` (model, pipeline, ablation), `backend/app/routers/attend.py`, `backend/tests/test_attend*.py`. Files were last modified 00:06 on 2026-10-20 (the author was editing during the check: the saturation threshold changed 90% to 85% and `model.inputs()` was added). Everything below was re-run against the 00:06 state. The Pass 1 notes were not relied on.

## Method

- Every cited URL was downloaded with curl into `scratchpad/pass2_attn/dl/` and converted with pypdf or BeautifulSoup by scripts kept in `scratchpad/pass2_attn_scripts/`, run with `python3 -I`. arXiv PDFs are the versions named in sources.yaml (Vaswani v7, Bahdanau v7, Jain v3, Wiegreffe v2, FlashAttention v2, RoFormer v5, Shazeer v1, GQA v3, GPT-3 v4, Milakov v2, BERT v2). HTML sources: Elhage, PyTorch 2.14 SDPA and softmax docs, Hugging Face Transformers v5.20.2 cache_explanation, glossary and llm_tutorial_optimization. `config.json` came from the raw URL at pinned commit 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a. No summarising fetch tool was used.
- Each excerpt was matched strict (raw substring), loose (NFKC, markdown, quotes, dashes, hyphenation, whitespace, case) and squash (alphanumerics only). Failed matches were read in context.
- Independent sources (not cited for that claim) were downloaded the same way into `dl_ind/` and each quoted fragment was re-matched by script (`ind.py`).
- Implementation: the layer was run locally (`PYTHONPATH=. uv run python`) for every preset, every challenge broken and fixed state through `evaluate_challenge`, every `breaks_if_removed` through `ablate`, the saturation and variance numbers, and the existing tests (`tests/test_attend.py`, `tests/test_attend_ablation.py`: 34 passed). No network use beyond downloads, no paid calls.

## Summary

| Verdict | Count |
|---|---|
| confirmed | 16 |
| confirmed_with_changes | 13 |
| disputed | 2 |
| unverifiable | 0 |

All 66 excerpts were found in their cited sources; none is fabricated. 28 strict, 30 loose (ligatures, quotes, hyphenation), 8 squash only (PDF or HTML code spacing, e.g. `Ther e is a safe form`, `float ( "-inf" )`). Locators are right except where noted. No excerpt is wrong, but several are cut before the words the claim relies on.

### Prioritised problems

1. **Implementation bug: `future_mass` is a sum over rows, not a fraction.** `stats()` and `ablate()` compute `weights[:, future].sum(axis=-1).mean()`, which sums the future weights of all n rows. Default sentence, causal off: 2.6128, shown in the UI as "Attention on later words 261%" (`AttendViews.tsx`), in the ablation panel as "Looks at later words", and in the peeking challenge as "Words still put 261% of their attention on later words." With softmax removed on "dog bites man" it prints -92%. Fix in `pipeline.py` line 132 and `ablation.py` line 117: divide by n, e.g. `round(float(f.weights[:, future].sum(axis=-1).mean() / n), 6)`. Then the default is 43.5% and the tests (`> 0.1`, `== 0`, `<= 1e-9`) still hold.
2. **Cat preset note is false.** "Repeated words ("the") get the same vector, so they match each other strongly." Random projections do not make equal words match. Default weights for the two "the"s (positions 0 and 4): 0.15 and 0.12 against a uniform 0.167. Over 300 random seeds, the repeated pair averages 0.154 against 0.168 for other pairs (repeat pair higher in only 38 to 41% of seeds), with or without positions. Replacement note: `Repeated words ("the") start from the same vector, but with random weights that does not make them attend to each other. A trained model learns which words to match.`
3. **`attn-softmax-saturation` and `attn-scaling-reason` excerpts do not contain the key words.** The excerpt ends at "pushing the softmax function into regions"; "where it has extremely small gradients" is cut off. Replace with `We suspect that for large values of dk, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients` (the text is on p.4 and ends with footnote marker 4). Saturation's other excerpt (PyTorch "[0, 1] and sum to 1") says nothing about saturation; see per-claim.
4. **`attn-origin` overstates.** "first used" is not in the paper, and "the attention model did not [drop]" is true only for RNNsearch-50. See per-claim fix.
5. **`attn-explanation-contested` and `attn-interpretability-hedged`**: "Both studied RNN models" is almost right (Jain and Wallace: "predominantly" BiRNN, plus average-embedding and CNN encoders; Wiegreffe and Pinter: LSTM only). "Hand-picked heads" is not stated by Vaswani.
6. **`attn-softmax-weights` says "positive"**; PyTorch says [0, 1], and masked entries are exactly 0.
7. **`attn-qk-ov` scope**: Elhage et al. work on "toy, attention-only" transformers without layer norm or biases. Say so in the claim.
8. **Pronoun preset hedge** is acceptable ("might") but can be sourced and tightened (Clark et al.).
9. **Smaller**: `attn-sqrt-dk-scaling` "back to about 1" is arithmetic, not in the paper; `attn-kv-cache-size` is per sequence, multi-head only; `attn-position-alternatives` RoPE excerpt lacks "queries and keys"; `attn-quadratic-memory` excerpt lacks "O(N)"; `model.inputs()` divides by sqrt(1.5) undisclosed; Elhage locators.

---

## Per-claim results

Excerpt match key: S strict, L loose, Q squash.

| Claim | Excerpts | Verdict |
|---|---|---|
| attn-weighted-sum | L, L | confirmed |
| attn-qkv-projections | L, L | confirmed |
| attn-scaled-dot-product | L, Q, Q | confirmed |
| attn-softmax-weights | L, L | confirmed_with_changes |
| attn-softmax-stable | Q, L, S | confirmed_with_changes |
| attn-scaling-reason | L, S | confirmed_with_changes |
| attn-sqrt-dk-scaling | L, S | confirmed_with_changes |
| attn-softmax-saturation | L, L | confirmed_with_changes |
| attn-multihead-concat | L, S, L | confirmed |
| attn-heads-additive | S | confirmed_with_changes |
| attn-multihead-motivation | L, L | confirmed_with_changes |
| attn-causal-mask | L, S, Q | confirmed |
| attn-padding-vs-causal | L, L | confirmed |
| attn-mask-polarity | Q, Q | confirmed |
| attn-position-needed | L | confirmed |
| attn-position-encoding | L, S | confirmed |
| attn-position-alternatives | L, L, L, L | confirmed_with_changes |
| attn-quadratic-cost | S, S | confirmed |
| attn-quadratic-memory | L, L | confirmed_with_changes |
| attn-kv-cache | S, S | confirmed |
| attn-kv-cache-valid | S | confirmed |
| attn-kv-cache-size | S | confirmed_with_changes |
| attn-mqa-gqa | Q, L, L | confirmed |
| attn-head-sizes | S, S, S, S | confirmed |
| attn-not-all-you-need | L, L | confirmed |
| attn-residual | L, L | confirmed |
| attn-origin | L, S, Q | disputed |
| attn-additive-vs-dot | S, L | confirmed_with_changes |
| attn-qk-ov | S, S | confirmed_with_changes |
| attn-explanation-contested | L, L | disputed (as worded) |
| attn-interpretability-hedged | S, L | confirmed_with_changes |

(Counts: 16 confirmed, 13 confirmed_with_changes, 2 disputed = 31.)

### Claim notes, independents and fixes

**attn-weighted-sum** (confirmed). Vaswani §3.2 p.3-4: "An attention function can be described as mapping a query and a set of key-value pairs to an output ... The output is computed as a weighted sum of the values" (the sentence breaks across a page; the excerpts are split correctly). Independent: Bahdanau §3.1 eq. 5 "ci is then, computed as a weighted sum of these annotations hi"; Jurafsky and Martin SLP3 ch.7 (Aug 2026 draft) "attention is really just a weighted sum of context vectors".

**attn-qkv-projections** (confirmed). Independent: SLP3 ch.7 "The attention head allows us to distinctly represent three different roles that each input embedding plays". Both Vaswani excerpts also fit; note §3.2.3 is the locator for the self-attention sentence and is correct.

**attn-scaled-dot-product** (confirmed). Eq. 1 on p.4. PyTorch pseudo-code excerpts match only after squash (the HTML has spaces around dots and parentheses); cosmetic. Independent: d2l.ai "we rescale the dot product by 1/sqrt(d)" (attention-scoring-functions).

**attn-softmax-weights** (confirmed_with_changes). PyTorch: "will re-scale them so that the elements lie in the range [0, 1] and sum to 1". The claim says "positive weights", and the lesson itself sets masked weights to exactly 0, which is not positive. Also "a share of attention that is a fraction of its total" is confusing. Fix text: `Softmax turns each row of scores into non-negative weights that add up to 1, so each word's attention is split into shares.` Also fix `softmax` component detail ("positive weights that sum to 1" to "non-negative weights that sum to 1"). Independent: SLP3 "normalizing them by a softmax, and using the resulting probabilities as weights".

**attn-softmax-stable** (confirmed_with_changes, minor). Milakov §2: "There is a safe form of (1), which is immune to this problem" and eq. 2 subtracts the max; "All major DL frameworks are using this safe version". The FlashAttention excerpt "For numerical stability, the softmax of vector" stops before the formula, so alone it shows nothing; extend to `For numerical stability, the softmax of vector x in R^B is computed as: m(x) := max_i x_i` (pypdf garbles the maths symbols, so quote the prose only, or drop this excerpt). Locators fine. Independent (strict): Wikipedia "Softmax function": "subtracting the maximum value from the input tuple is common. This approach, while not altering the output or the derivative theoretically". Test `test_softmax_survives_huge_scores` confirms.

**attn-scaling-reason** (confirmed_with_changes). The paper does say "We suspect"; the claim keeps the hedge, which is correct. Two points. (a) Excerpt 1 is cut before "extremely small gradients" (fix above). (b) The paper adds, in the same passage, "additive attention outperforms dot product attention without scaling for larger values of dk [3]"; this is context, not a problem. Independent: SLP3 ch.7 "exponentiating large values can lead to numerical issues and loss of gradients during training" (a hedge-free restatement; it frames the cause as large dot products).

**attn-sqrt-dk-scaling** (confirmed_with_changes). Footnote 4 (p.4) gives only mean 0 and variance dk under independence with mean 0 and variance 1. It does not state that dividing by sqrt(dk) restores unit spread; that is one line of arithmetic (Var(X/c) = Var(X)/c^2) and holds only under the same assumption, which does not describe trained weights. "Fairly stated as a consequence": yes, if labelled as the follow-on arithmetic. The footnote 4 excerpt reproduces pypdf garbling ("Pdki=1 qiki") which will look odd if shown. Independent that states the consequence: d2l.ai "To ensure that the variance of the dot product still remains 1 regardless of vector length, we use the scaled dot product attention scoring function." Fix text: `If the components of a query and a key are independent with mean 0 and variance 1, their dot product has mean 0 and variance d_k, so the spread of scores grows like sqrt(d_k). Dividing by sqrt(d_k) then gives variance 1 (simple arithmetic under the same assumption). Trained models need not satisfy it.` Toy check (position off): raw variance 55.8 / 29.3 / 16.1 / 8.25 for d_k 64 / 32 / 16 / 8, scaled 0.87 / 0.92 / 1.01 / 1.03. With positions on, `inputs()` divides by sqrt(1.5) to keep components near unit variance.

**attn-softmax-saturation** (confirmed_with_changes). Labelled `kind: simplification` and scoped to "this lesson's toy layer", which is honest. But neither cited source states that a large score takes nearly all the weight; that is a property of exp. Cite an independent source for it and make the sources' roles clear. Independent (strict): Wikipedia "Softmax function": "if one input is much larger than the others relative to the temperature, T = 1 / beta, the output is approximately the arg max", with sigma(0, 10) approx (0.00005, 0.99995). Replace the PyTorch excerpt (which is about range and sum, irrelevant to saturation) with that. Measured: 64-wide head, positions on, six test sentences, strongest weight averages 88.8% (min 79.3%, max 97.2%); scaled 35.3% (max 51.2%). So "over 85%" and "under 60%" are true; "near one-hot" is a fair gloss only as "about nine tenths of the weight". Suggested text: `... In this lesson's toy layer a 64-wide head without scaling puts about 90% of a word's attention on one word on average (89% over six sample sentences), and scaling spreads it out (about 35%).` Also state it is the forward effect only; gradients are not measured.

**attn-multihead-concat** (confirmed). §3.2.2 p.5. Table 3 supports h = 8, dk = 64. Independent: SLP3 "concatenated to produce a single output with dimensionality [1 x A dv]. Then we use yet another linear projection W^O"; d2l.ai "concatenated and transformed with another learned linear projection".

**attn-heads-additive** (confirmed_with_changes). Locator "same section" is vague; use `Summary of Results, Conceptual Take-Aways; section "Attention Heads are Independent and Additive"`. Mathematically it is block-matrix multiplication; verified numerically by `test_concatenating_heads_then_projecting_equals_summing_per_head_slices` (atol default). No second prose source found; computed equivalence is the independent check. Elhage's setting is attention-only and bias-free, but the identity is general.

**attn-multihead-motivation** (confirmed_with_changes). Table 3 rows (A): h = 1 gives BLEU 24.9; best is 25.8 (h = 8 and h = 16); h = 32 gives 25.4. So "0.9 BLEU worse than the best setting" is exact. Qualifiers the claim omits: this is English-German dev set (newstest2013) with computation held constant (dk shrinks as h grows), and the paper's "reason" is a motivation, not a result (it says "allows ... With a single attention head, averaging inhibits this."). Fix: `... In their English-German tests (computation held constant) one head scored 0.9 BLEU below the best setting (24.9 against 25.8), and 32 heads also did worse (25.4).` Independent: Michel et al. 2019 abstract: "a large percentage of attention heads can be removed at test time without significantly impacting performance" (so more heads is not automatically better or necessary).

**attn-causal-mask** (confirmed). All three match. Missing excerpt for "a word can still attend to itself": Vaswani §3.2.3 p.5 "allow each position in the decoder to attend to all positions in the decoder up to and including that position" (add it); PyTorch pseudo-code uses `tril(diagonal=0)`, which includes the diagonal. Independent: SLP3 "the elements in the upper-triangular portion of the matrix are set to -inf, which the softmax will turn to zero".

**attn-padding-vs-causal** (confirmed). HF glossary v5.20.2: "For the BertTokenizer, 1 indicates a value that should be attended to, while 0 indicates a padded value." The claim says "In Hugging Face tokenizers": the glossary says BertTokenizer; other tokenizers follow the same convention in practice, so say "In Hugging Face Transformers" to stay within the source. Independent: PyTorch MultiheadAttention docs `key_padding_mask`: "indicating which elements within key to ignore for the purpose of attention (i.e. treat as 'padding')". Also note the HF cache page prints the formula as `softmax(QK^T/sqrt(d_head) x mask)` (a multiplicative mask); that is HF's own sketch and differs from the -inf addition the lesson teaches; the lesson does not quote it.

**attn-mask-polarity** (confirmed). Exact on the 2.14 page, both excerpts. Independent: PyTorch MHA docs "a True value indicates that the corresponding key value will be ignored"; Keras MultiHeadAttention `attention_mask`: "1 indicates attention and 0 indicates no attention". Implementation note: `model.causal_mask` returns True where a position may NOT be attended to (the MHA convention, opposite to SDPA); never shown to learners but worth a comment.

**attn-position-needed** (confirmed). Independent: Shaw et al. 2018 "the model is otherwise entirely invariant to sequence ordering"; d2l.ai "self-attention by itself does not preserve the order of the sequence". Toy statement verified: with position and causal off, `order_gap` = 0.0; position on 0.455; causal on 3.35. Wording nuance: "no sense of order" means the outputs are permutation-equivariant (each word's output is unchanged, only the list order changes), not that all outputs are equal. Several texts (component `embed_pos`, `breaks_if_removed`, challenge brief "same output") are ambiguous on this; suggested replacement below.

**attn-position-encoding** (confirmed). §3.5 p.6. Independent: d2l.ai "a simple scheme for fixed positional encodings based on sine and cosine functions". Toy `position_encoding` matches the formula (tested). Disclosure: `model.inputs()` now returns `(word + position) / sqrt(1.5)`, which the explain text does not mention.

**attn-position-alternatives** (confirmed_with_changes). Vaswani hypothesis and "nearly identical" (Table 3 row E: 25.7 against 25.8 BLEU, PPL 4.92 against 4.92 on the dev set) are right; the paper also gives a second reason (extrapolation to longer sequences). BERT: "constructed by summing the corresponding token, segment, and position embeddings" is correct (BERT's are learned). RoPE: the abstract excerpt says "rotation matrix" and "relative position dependency" but never mentions queries and keys, which the claim states. Eq. 14 (§3.2.2) f{q,k}(x_m, m) = R_{Theta,m} W{q,k} x_m supports it. Replace the RoPE excerpt with `simply rotate the affine-transformed word embedding vector by amount of angle multiples of its position index` (RoFormer §3.2.1, p.4). Independent: SLP3 "these positional embeddings are learned along with other parameters during training".

**attn-quadratic-cost** (confirmed). Table 1 p.6. Independent: SLP3 "attention is quadratic in the length of the input"; Longformer abstract "self-attention operation, which scales quadratically with the sequence length". Caveat the paper itself states: self-attention is cheaper than recurrence when n is smaller than d.

**attn-quadratic-memory** (confirmed_with_changes). Abstract: "time and memory complexity of self-attention are quadratic in sequence length" (about standard attention); Theorem 1 (v2, §3.1 p.5): "returns O = softmax(QK^T)V with O(N^2 d) FLOPs and requires O(N) additional memory beyond inputs and output". The second excerpt as written omits "O(N)", and "arithmetic still quadratic" rests on the unquoted "O(N^2 d) FLOPs". Add that clause (pypdf renders it as `𝑂„𝑁 2𝑑” FLOPs`; quote it as prose from a cleaner copy or note the garble). Independent (strict): Rabe and Staats 2021 "requires O(1) memory with respect to sequence length ... While the time complexity is still O(n2)". Note FlashAttention's O(N) is "additional memory"; the attention matrix is never stored in full.

**attn-kv-cache** (confirmed). HF "How caching works" v5.20.2. Independent: SLP3 "it would be a waste of computation time to recompute the key and value vectors for all the prior tokens". HF adds: "Caching should only be used for inference".

**attn-kv-cache-valid** (confirmed). HF: "Once a token is processed, its representation never changes with respect to future tokens, which means K_past and V_past can be cached". Wording check: "a word that has been processed never changes" is the HF sentence; precise statement is that its keys and values (and per-layer hidden state) do not change under a causal mask. Toy check: first 3 outputs, keys and values identical with the mask on and not with it off (tested).

**attn-kv-cache-size** (confirmed_with_changes). HF llm_tutorial_optimization §3.2: "The number of float values amounts to two times the sequence length times the number of attention heads times the attention head dimension and times the number of layers." That is per sequence (batch 1) and for plain multi-head attention; MQA and GQA replace "attention heads" with the number of key-value heads (same page, 3.2.2 and 3.2.3), which matters because the lesson mentions MQA and GQA beside it. Fix text: `For plain multi-head attention, the KV cache for one sequence holds two times the sequence length times the number of heads times the head dimension times the number of layers numbers (multi-query and grouped-query attention use fewer key-value heads).` Independent (strict): vLLM paper (Kwon et al.) "2 (key and value vectors) x 5120 (hidden state size) x 40 (number of layers) x 2 (bytes per FP16)" = 800 KB per token for OPT-13B.

**attn-mqa-gqa** (confirmed). Shazeer abstract and GQA §2.2 match; also the GQA text "Going from MHA to MQA reduces H key and value heads to a single key and value head, reducing the size of the key-value cache ... by a factor of H". Independent: PaLM §2 "the key/value projections are shared for each head". The word "between" is justified by GQA: "interpolating between multi-head and multi-query attention".

**attn-head-sizes** (confirmed). Re-fetched: bge `config.json` at 5c38ec7: `hidden_size 384`, `num_attention_heads 12`, so 32 per head. BERT-base (L=12, H=768, A=12) gives 64 per head; GPT-3 175B Table 2.1: n_layers 96, d_model 12288, n_heads 96, d_head 128 (96 x 128 = 12288). The BERT excerpt ends mid-word ("Param-"); cosmetic. Independent: BERT-base `config.json` on HF (768 / 12); OPT paper Table 1 "175B 96 96 12288" (#L, #H, d_model) with the text that OPT follows GPT-3 settings, so 12288 / 96 = 128. Note the 64-per-head, 32-per-head, 128-per-head numbers are divisions, flagged as such in the claim notes.

**attn-not-all-you-need** (confirmed). Abstract and §3.3 match. The claim says the title "means it dropped recurrence and convolutions": the abstract says this, but the title is not explained in the paper; phrase as "Its abstract says it dropped...". Independent: Dong et al. 2021 "without skip connections or multi-layer perceptrons (MLPs), the output converges doubly exponentially to a rank-1 matrix".

**attn-residual** (confirmed). §3.1 p.3 exact. Independent: Xiong et al. 2020 "the original-designed Post-LN Transformer, which places the layer normalization between the residual blocks". SLP3 shows a pre-norm layout, so "original" is the right qualifier (already used).

**attn-origin** (disputed as worded). (a) "Attention was first used in neural translation" is a priority claim that no excerpt supports. Bahdanau §6.1 cites Graves (2013) for a similar alignment idea in handwriting synthesis, and the paper never claims to be first. (b) "the attention model did not [drop]": Bahdanau says "both RNNsearch-30 and RNNsearch-50 are more robust to the length of the sentences. RNNsearch-50, especially, shows no performance deterioration even with sentences of length 50 or more", so only RNNsearch-50 shows none. Independent for the encoder-decoder drop: Cho et al. 2014, "the performance of the neural machine translation model degrades quickly as the length of a source sentence increases". Fix text: `Bahdanau et al. (2014) introduced attention to neural translation so that a whole source sentence need not be squeezed into one fixed-length vector. In their test the plain encoder-decoder dropped sharply on long sentences, while the attention model trained on longer sentences (RNNsearch-50) showed no deterioration even at 50+ words.` Same change in `tokens` explain (`why`: "Attention was invented for translation" is fine; "learn_more" is fine).

**attn-additive-vs-dot** (confirmed_with_changes). Bahdanau A.1.2 eq: `a(s_{i-1}, h_j) = v_a^T tanh(W_a s_{i-1} + U_a h_j)`, "a single-layer multilayer perceptron" (the main text also says "feedforward neural network jointly trained"). "Additive" is Vaswani's name, not Bahdanau's. The Vaswani excerpt is cut at "highly optimized" (fine). Missing nuance from the same page: "additive attention outperforms dot product attention without scaling for larger values of dk [3]"; this strengthens the lesson's scaling story and could be added. Independent: Britz et al. 2017 §4.5 "the computationally less expensive multiplicative variant"; Luong et al. 2015 compare dot, general, concat and note "dot works well for the global attention". Note "much faster" in practice is Vaswani's own statement; the lesson attributes it ("the authors say"), correct.

**attn-qk-ov** (confirmed_with_changes). Both excerpts exact ("Keys, queries and value vectors are, in some sense, superficial. They're intermediary by-products of computing these low-rank matrices."). Scope: the paper focuses on "toy, attention-only models", ignores biases and layer norm, is not peer reviewed (sources.yaml notes this). The claim text has no scope. Fix text: `In Elhage et al.'s analysis of small attention-only transformers (not peer reviewed), a head is seen as two largely independent parts: one that computes where to attend and one that computes what to move from the attended word. They call queries, keys and values "in some sense, superficial" intermediate results of computing two low-rank matrices.` Independent: Olsson et al. 2022 use the same QK and OV circuit vocabulary ("Prefix matching is implemented ... in the QK ("Query-Key") Circuit").

**attn-explanation-contested** (disputed as worded; one-word fix). Jain and Wallace: "Our findings for attention weights in recurrent (BiLSTM) encoders", "We predominantly consider a Bi-RNN as the encoder", plus "unordered 'average' embedding variants" and ConvNets (supplement). They also report that in "simple, feedforward (weighted average) encoders" attention "enjoy[s] better behaviors". Wiegreffe and Pinter: "models with an LSTM architecture", "the only one the authors make firm conclusions on". Neither paper tests Transformer self-attention. So "Both studied RNN models" is accurate for Wiegreffe and Pinter, and for Jain and Wallace only for the main results. Fix text: `Both mainly studied recurrent (LSTM) models with attention, not Transformer self-attention.` Jain and Wallace's finding "frequently uncorrelated with gradient-based measures of feature importance" is quoted fairly. Independent: Serrano and Smith 2019, "attention noisily predicts input components' overall importance to a model, it is by no means a fail-safe indicator" (they also analyse trained text classifiers). The explain `mix.misconfigured` ("Studies of RNN models with attention found...") is fine.

**attn-interpretability-hedged** (confirmed_with_changes). Quotes exact (§4 p.7: "many appear to exhibit behavior related to the syntactic and semantic structure"). "Hand-picked" is not stated; the appendix shows a few specific heads ("Full attention for head 5 ...") without saying how they were chosen. Fix text: `The Transformer authors suggested self-attention could yield more interpretable models, but they only showed a few example heads, which "appear" related to sentence structure.` Also in `explain.yaml` `mix.learn_more`. Independent: Clark et al. 2019 abstract "certain attention heads correspond well to linguistic notions of syntax and coreference" (BERT, not the Transformer paper).

---

## Non-claim text against code and tests

### Verified true (ran locally)
- softmax of 2.0, 1.0, 0.0 = 0.6652, 0.2447, 0.0900, i.e. 67%, 24%, 9% (explain example). Weights 70%/30% example is plain arithmetic.
- "At most 12 tokens" (`MAX_TOKENS`; 30 words give 12; a note is shown when truncated). "Up to 12" in the `tokens` component.
- "Fixed random vector per word, same word same vector": true, and case-insensitive (`Cat` equals `cat`). 64 numbers (`D_MODEL`).
- "Sine and cosine added": true; see disclosure on `inputs()` below.
- Six tokens for "the cat sat on the mat", 36 dot products, 6 x 6 grid, "2 heads of 32 joined into 64", W^O: all match.
- Causal mask: later scores -inf, exact zero weight, first word weight 1 on itself, rows sum to 1, self attention allowed.
- Dog bites man order claim: position off and causal off, order_gap 0.0; position on 0.455; causal on 3.35 (so the component and the Order preset note are right). The preset note says "turn Position vectors off and the Causal mask off": correct.
- Saturation numbers (6 sentences, positions on, causal off): 1 head unscaled 88.8% (min 79.3%); 2 heads 79.2%; 4 heads 75.5%; 8 heads 62.1%; all scaled 35 to 37%. Tests assert > 85% and < 60%.
- Score variance numbers listed above support "about sqrt(d_k)" in the explain text (std 7.5 for d_k = 64, expected 8).
- `breaks_if_removed` for all eight stages (default config, causal on, and "dog bites man"): tokens (no weights), embed_pos (order_gap 0.0 with causal off; with causal on order still matters, and the tool says so), qkv (self weight 0.86 against 0.20, 0.94 against 0.44 causal; argmax is self in every row of three test sentences with positions on), scores (all weights 1/6, uniform True; with causal on rows uniform over visible words), mask (future mass appears), softmax (row sums -7.9 to 15.3, negative weights), mix (weights but no output), output (separate 2 x 6 x 32 results).

### Challenges (via `evaluate_challenge`)
| Challenge | Broken | Fixed |
|---|---|---|
| peeking | fails (future mass 2.61, message "261%") | passes with causal on |
| one-word-takes-all | fails: strongest 93.5% | passes with scale on (29.7%), 8 heads unscaled (56.2%), 4 heads unscaled (75.7%); 2 heads unscaled (86.5%) still fails |
| bag-of-words | fails: gap 0.0 | passes with position on (0.455) |

Challenge text issues:
- `peeking`: the failure message shows the bug above.
- `one-word-takes-all` explanation "Dividing by sqrt(d_k), or splitting into more narrower heads" is right but 2 heads are not enough; say "four or more narrower heads". "Unscaled dot products have a spread of about sqrt(d_k)" carries the Vaswani footnote assumption; add "for random vectors like these".
- `bag-of-words` brief "gives the same output for 'dog bites man' and 'man bites dog'" should say each word's output is the same, and its explanation offers the causal mask as an alternative although `causal` is locked in this challenge.

### Component and explain.yaml mismatches
- **embed_pos.happens / what**: "A sine and cosine pattern ... is added" but the code now also divides the sum by sqrt(1.5). Add "(the sum is then rescaled by 1/sqrt(1.5) to keep numbers a steady size)" or remove the rescaling.
- **embed_pos.misconfigured and breaks_if_removed**: "every word's output is the same whatever order the words come in" invites the reading "all words get the same output". Replace: `Each word's output stays the same wherever it sits, so "dog bites man" and "man bites dog" give each word the same output; only the order of the list changes.`
- **qkv.breaks_if_removed**: true; note the ablation also changes the toy layer to one 64-wide head, so the self-weight gain mixes two effects. Add "and one head" to the ablation note, or keep the head count.
- **scores.breaks_if_removed**: "Every visible word gets the same weight" is true per row; with the mask on, weights are 1/(i+1) for word i.
- **output.breaks_if_removed**: with 1 head the output step removal still yields one vector per word (without W^O); the text is correct for 2, 4, 8 heads.
- **tokens.what**: "words and punctuation marks": the regex splits non-ASCII letters, so "cafe with accent" becomes `caf`, `é`; "naive with umlaut" becomes `na`, `ï`, `ve`. Say "English words" or fix the regex (`[^\W\d_]+`).
- **tokens.misconfigured**: fine; "long or rare word is just one token" is correct for this toy.
- **softmax.misconfigured**: "near one-hot" see saturation note; fine with the numbers.
- **mask.misconfigured**: "Turn the mask off in a text-generating model and each word can see the future, which would not exist when generating" is correct. The default `causal` is False, which is worth one line: the lesson's default demo is a non-causal (encoder-style) layer.
- **mix.misconfigured**: "also needs a table that grows with the square of the sentence length" is true for standard attention (FlashAttention avoids storing it); say "standard attention".
- **output.misconfigured**: "in the original tests too many heads also hurt" correct (32 heads 25.4). "More heads is not automatically better" is supported by Michel et al.
- **output.learn_more**: BERT-base 12 on 768 and bge-small 12 on 384 verified.

### Presets and visual labels
- **Cat preset note**: false; fix in the Problems list.
- **Pronoun preset**: "A trained model might link 'it' to 'animal'." It is hedged. The sentence is the well known illustration from Google's 2017 Transformer post, not from the paper. Sourced hedge: `Some trained models do have heads that often link a pronoun to its earlier noun (in BERT, one head linked coreferent mentions to their antecedents 65.1% of the time in Clark et al. 2019), but this toy layer has random weights, so it will not. Do not read meaning into its grid.` Note that "animal" is also the only noun candidate.
- **Order preset**: correct.
- **Visuals**: `ablation` and `experiment` are labelled "Real execution" and are real; `exploded-view` and `data-flow` are labelled conceptual and the data-flow wording ("dotted lines carry scores and weights") matches the edges in `connections`. Toy honesty: `corpus_note`, NOTE, preset notes and the tour all say "toy", "random", "not what a trained model attends to". The `tokens` and `scores` sections are honest; only the Cat note contradicts it.
- **Tour**: "Scores are divided by sqrt(d_k) so they do not grow too large" is a plain statement of the hedged claim; add "the authors suspect" or soften to "so large scores do not push softmax into near one-hot".

### Jargon before explanation and analogies
- `tokens.why`: "squeezed into one vector" before "vector" is explained (the `embed_pos` step). `goes_to` and `what` use "tokenizer (Lesson 02)" fine.
- `scores.what` uses "dot", "d_k" and "grid" before defining d_k (width of one head); the first mention should say "(d_k is the number of numbers in one head's query)".
- `softmax.happens`: "exponentiate" and "overflow" unexplained.
- `qkv` library analogy: it implies a lookup that returns one book. Attention returns a blend of all values weighted by match, and in the toy the matrices are random. The explain text partially fixes this (`mix` stage). Suggested label addition: `Unlike a library, you get a blend of every book, weighted by how well its label matches.`
- `tokens.analogy` "seating words around a table": suggests neighbours-only or symmetric attention. In causal layers a word sees only earlier words, and attention is not symmetric (weights from i to j differ from j to i). Suggested: `Giving every word a turn to look back over the sentence and decide whom to listen to.`
- `mask.analogy` (card covering the page) and `mix.analogy` (mixing paints) are fine; `output.analogy` ("pool their notes") is fine.

### Other implementation notes
- `model.weights()` draws four 64 x 64 matrices from one RNG, so heads of different counts are column slices of the same matrices; consistent with the "split" description.
- `tests/test_attend.py` thresholds were tightened from 0.9 to 0.85 while I worked; `lesson.yaml` was updated to match (85%). The tests assert on the 6-sentence mean, so any new sentence set should be re-measured.
- `AttendViews.tsx` prints `pct(s.future_mass)`; after the divide-by-n fix the values are fractions in [0, 1].

## Fix list (file, id, field, replacement)

1. `backend/app/experiments/attend/pipeline.py:132` and `ablation.py:117`: `"future_mass": round(float(<...>.sum(axis=-1).mean() / n), 6)`.
2. `lesson.yaml` experiment.presets[Cat].note: `Repeated words ("the") start from the same vector, but with random weights that does not make them attend to each other. A trained model learns which words to match.`
3. `lesson.yaml` attn-scaling-reason and attn-softmax-saturation citation 1 excerpt: `We suspect that for large values of dk, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients`.
4. `lesson.yaml` attn-softmax-saturation: replace the PyTorch citation with Wikipedia "Softmax function": `if one input is much larger than the others relative to the temperature, T = 1/beta, the output is approximately the arg max`.
5. `lesson.yaml` attn-origin text: see claim note above (introduced, RNNsearch-50).
6. `lesson.yaml` attn-explanation-contested text: `Both mainly studied recurrent (LSTM) models with attention, not Transformer self-attention.` Same in `explain.yaml` `mix.learn_more` ("Both studied RNN models with attention").
7. `lesson.yaml` attn-interpretability-hedged text and `explain.yaml` `mix.learn_more`: "hand-picked heads" to "a few example heads".
8. `lesson.yaml` attn-softmax-weights text and the `softmax` component detail: "positive" to "non-negative".
9. `lesson.yaml` attn-sqrt-dk-scaling text: see claim note (label the "back to 1" as arithmetic).
10. `lesson.yaml` attn-qk-ov text: add the attention-only, small-model, not-peer-reviewed scope.
11. `lesson.yaml` attn-kv-cache-size text: add "for one sequence, plain multi-head attention".
12. `lesson.yaml` attn-position-alternatives RoPE excerpt: `simply rotate the affine-transformed word embedding vector by amount of angle multiples of its position index`; attn-quadratic-memory excerpt 2: add `requires O(N) additional memory beyond inputs and output`; attn-heads-additive locator: `Summary, Conceptual Take-Aways`.
13. `lesson.yaml` attn-multihead-motivation text: add "English-German, computation held constant" and the 24.9 against 25.8 figures.
14. `lesson.yaml` challenges one-word-takes-all explanation (4 or more heads) and bag-of-words brief/explanation (per-word outputs; causal locked); embed_pos `breaks_if_removed` and `misconfigured`; Pronoun preset note (Clark hedge).
15. `explain.yaml` embed_pos.happens: mention the 1/sqrt(1.5) rescaling or remove it in `model.inputs()`; tokens.analogy replacement; qkv.analogy qualifier; mix.misconfigured "standard attention".
