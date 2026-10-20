# Lesson 04 foundations: how one self-attention head works

Primary-source research notes for ExplodeAI Lesson 04 "Attention, exploded". Accessed 2026-10-19. All excerpts were copied from the downloaded raw files (PDFs extracted with pypdf, HTML stripped with html.parser) and machine-checked to appear in the extracted text (whitespace and ligature-normalised, each at most 25 words). No paid API calls, no summarising fetch tools.

Reading notes: pypdf drops super/subscripts and mangles equations (e.g. 'dk', 'O(n2 · d)', 'QK T√dk'); excerpts keep the extracted spelling, so check the PDF image before quoting an equation on screen. Excerpts are mid-sentence fragments where needed; some are cut where a line or page break split a word. Page numbers are PDF page numbers (they equal the printed numbers in these arXiv files).

## 1. Source register

| id | title | authors | URL | version | accessed | sha256 (first 12) of downloaded file |
|---|---|---|---|---|---|---|
| V | Attention Is All You Need | Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser, Polosukhin | https://arxiv.org/abs/1706.03762 (PDF https://arxiv.org/pdf/1706.03762v7) | arXiv v7 (2 Aug 2023); NIPS 2017 | 2026-10-19 | bdfaa68d8984 |
| B | Neural Machine Translation by Jointly Learning to Align and Translate | Bahdanau, Cho, Bengio | https://arxiv.org/abs/1409.0473 (PDF https://arxiv.org/pdf/1409.0473v7) | arXiv v7 (19 May 2016); ICLR 2015 | 2026-10-19 | 84801c8410da |
| J | Attention is not Explanation | Jain, Wallace | https://arxiv.org/abs/1902.10186 (PDF https://arxiv.org/pdf/1902.10186v3) | arXiv v3 (8 May 2019); NAACL 2019 | 2026-10-19 | ffc666e7e27d |
| W | Attention is not not Explanation | Wiegreffe, Pinter | https://arxiv.org/abs/1908.04626 (PDF https://arxiv.org/pdf/1908.04626v2) | arXiv v2 (5 Sep 2019); EMNLP 2019 | 2026-10-19 | d9e507dfa544 |
| E | A Mathematical Framework for Transformer Circuits | Elhage, Nanda, Olsson, Henighan, Joseph, Mann, Askell, Bai, Chen, Conerly, et al. (Anthropic) | https://transformer-circuits.pub/2021/framework/index.html | Published Dec 22, 2021 (page shows no version number or commit; fetched page hash recorded) | 2026-10-19 | 5b072df765d9 |
| P | torch.nn.functional.scaled_dot_product_attention (PyTorch docs) | PyTorch contributors | https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html (the /stable/ URL redirects to 2.14) | PyTorch 2.14 documentation (page title); no per-page date | 2026-10-19 | afbae6dd9c16 |

Notes on versions: arXiv listing probed with curl; latest existing versions are Vaswani v7, Bahdanau v7, Jain & Wallace v3, Wiegreffe & Pinter v2 (vN+1 returned HTTP 404). Hugging Face Transformers docs were optional and NOT used. Raw files: scratchpad `attn_research/raw`, text in `attn_research/txt`.

## 2. Claim types

- definition: how the source defines or specifies something.
- mathematical: exact, testable by code (lesson can run a check).
- empirical: depends on experiments in a stated setting; do not generalise beyond it.
- hypothesis/motivation: the authors' stated reason, hedged in the source.

## 3. Claims

### A01. Attention takes a query and a set of key-value pairs and returns a weighted sum of the values; each weight comes from how well the query matches the corresponding key.

- Excerpt [V, §3.2 (pp.3-4)]: "The output is computed as a weighted sum"
- Excerpt [V, §3.2 (p.4)]: "the weight assigned to each value is computed by a compatibility function of the query with the corresponding key"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition
- Confidence: high
- Notes / caveats: Quotes span a page break (p.3 to p.4); the first excerpt is a line fragment ending p.3.

### A02. One head computes softmax(QK^T / sqrt(d_k)) V: dot each query with every key, divide by sqrt(d_k), softmax into weights, then use the weights to mix the values.

- Excerpt [V, §3.2.1, Eq. (1) (p.4)]: "We compute the dot products of the query with all keys, divide each by √dk, and apply a softmax function"
- Excerpt [V, §3.2.1, Eq. (1) (p.4)]: "Attention(Q, K, V) = softmax(QK T√dk )V (1)"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: mathematical (exact, testable by code)
- Confidence: high
- Notes / caveats: The second excerpt is the pypdf extraction of Eq. (1) (typesetting lost: read as softmax(QK^T/sqrt(d_k))V). Verify against the PDF image before any on-screen rendering. Cross-check with the PyTorch reference code (claim A33).

### A03. Queries, keys and values for all tokens are packed into matrices Q, K, V so one matrix product scores every query against every key at once.

- Excerpt [V, §3.2.1 (p.4)]: "In practice, we compute the attention function on a set of queries simultaneously, packed together into a matrix Q."
- Excerpt [V, §3.2.1 (p.4)]: "The keys and values are also packed together into matrices K and V ."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition
- Confidence: high
- Notes / caveats: Efficiency framing; for beginners the per-token (vector) view and the matrix view are the same computation.

### A04. Q, K and V are not given; they are produced from the token vectors by learned linear projections (weight matrices W^Q, W^K, W^V).

- Excerpt [V, §3.2.2 (p.4)]: "linearly project the queries, keys and values h times with different, learned linear projections to dk, dk and dv dimensions, respectively."
- Excerpt [V, §3.2.2 (p.5)]: "the projections are parameter matricesW Qi ∈ Rdmodel×dk, W Ki ∈ Rdmodel×dk, W Vi ∈ Rdmodel×dv"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition
- Confidence: high
- Notes / caveats: Vaswani describes the projections in the multi-head context (per head i). A single head is the h=1 special case (Table 3 row A, h=1). Elhage writes the same thing per token: v_i = W_V x_i, k_i = W_K x_i, q_i = W_Q x_i (claim A28).

### A05. In self-attention the queries, keys and values all come from the same sequence (the previous layer's output), so every token attends to tokens of its own sequence.

- Excerpt [V, §3.2.3 (p.5)]: "In a self-attention layer all of the keys, values and queries come from the same place"
- Excerpt [V, §2 (p.2)]: "Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition
- Confidence: high
- Notes / caveats: none

### A06. Why divide by sqrt(d_k): for large d_k the raw dot products become large, which pushes softmax into regions with extremely small gradients; scaling counteracts this.

- Excerpt [V, §3.2.1 (p.4)]: "We suspect that for large values of dk, the dot products grow large in magnitude, pushing the softmax function into regions"
- Excerpt [V, §3.2.1 (p.4)]: "To counteract this effect, we scale the dot products by 1√dk ."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: empirical/hypothesis (the paper says 'We suspect'); the supporting variance statement is mathematical (A07)
- Confidence: medium
- Notes / caveats: The paper hedges: 'We suspect'. It cites [3] (Britz et al.) for additive attention beating UNSCALED dot-product at larger d_k, but gives no experiment of its own isolating the scaling. Do not teach it as a proven result; teach it as the authors' stated reason, then show it with a code demo (softmax saturation with large-variance scores) that the lesson itself runs.

### A07. The variance argument: if the components of q and k are independent with mean 0 and variance 1, then q.k has mean 0 and variance d_k, so its typical size grows like sqrt(d_k).

- Excerpt [V, footnote 4 (page 4; marker in §3.2.1)]: "assume that the components of q and k are independent random variables with mean 0 and variance 1."
- Excerpt [V, footnote 4 (page 4; marker in §3.2.1)]: "Then their dot product, q · k = Pdki=1 qiki, has mean 0 and variance dk."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: mathematical (exact under the stated assumption; testable by Monte Carlo)
- Confidence: high for the arithmetic; the assumption is NOT guaranteed for trained models
- Notes / caveats: Footnote text says 'assume'. It is an ASSUMPTION about q and k, not a measured property of trained models (learned projections need not give unit-variance, independent components). The footnote gives only mean 0 and variance d_k; that dividing by sqrt(d_k) restores unit variance (std of the sum = sqrt(d_k)) is a one-line consequence NOT written in the footnote. The footnote is attached (superscript 4) to the sentence about dot products pushing softmax into small-gradient regions (A06). Extraction places the marker as '4' after 'gradients'; confirm placement in the PDF image.

### A08. Softmax turns the raw scores into positive weights that sum to 1, so each query gets a probability-like distribution over positions.

- Excerpt [B, §3.1, Eq. (6) (p.3)]: "αij = exp (eij)∑Tx k=1 exp (eik) , (6)"
- Excerpt [B, §3.1 (p.4)]: "Let αij be a probability that the target wordyi is aligned to, or translated from, a source word xj."
- Source id(s): B; URL: https://arxiv.org/abs/1409.0473
- Version / accessed: B: arXiv v7 (19 May 2016); accessed 2026-10-19
- Type: mathematical (property of softmax: outputs are positive and sum to 1; testable by code)
- Confidence: high
- Notes / caveats: The sources show the softmax formula but do not state 'sums to 1' in a sentence; that follows from the formula (denominator = sum of numerators). Vaswani only says 'apply a softmax function to obtain the weights on the values' (A02). Bahdanau's excerpt has a typo-style spacing from extraction ('wordyi').

### A09. The output for a query is the weighted sum of the value vectors: an 'expected' value under the attention distribution.

- Excerpt [B, §3.1, Eq. (5) (p.3)]: "The context vectorci is, then, computed as a weighted sum of these annotationshi"
- Excerpt [B, §3.1 (p.4)]: "the i-th context vector ci is the expected annotation over all the annotations with probabilities αij."
- Source id(s): B; URL: https://arxiv.org/abs/1409.0473
- Version / accessed: B: arXiv v7 (19 May 2016); accessed 2026-10-19
- Type: mathematical + definition
- Confidence: high
- Notes / caveats: Bahdanau's 'annotations h_j' play the role of values (and keys); 'context vector' = attention output. Terminology differs from Vaswani's Q/K/V; the Q/K/V naming appears in Vaswani, not in Bahdanau.

### A10. Multi-head attention runs h attention heads in parallel on different learned projections, concatenates their outputs, and applies one more learned output projection W^O.

- Excerpt [V, §3.2.2 (pp.4-5)]: "On each of these projected versions of queries, keys and values we then perform the attention function in parallel"
- Excerpt [V, §3.2.2 (p.5)]: "MultiHead(Q, K, V) = Concat(head1, ...,headh)W O"
- Excerpt [V, §3.2.2 (p.5)]: "we employ h = 8 parallel attention layers, or heads. For each of these we use dk = dv = dmodel/h = 64."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition + mathematical
- Confidence: high
- Notes / caveats: Base model: h=8, d_model=512, d_k=d_v=64. 'These are concatenated and once again projected' is the sentence on p.5.

### A11. The stated reason for multiple heads: they can jointly attend to information from different representation subspaces at different positions, which a single averaged head cannot.

- Excerpt [V, §3.2.2 (p.5)]: "Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this."
- Excerpt [V, §6.2 (p.9)]: "While single-head attention is 0.9 BLEU worse than the best setting, quality also drops off with too many heads."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: claim = authors' motivation; ablation = empirical (EN-DE dev set newstest2013, BLEU)
- Confidence: medium
- Notes / caveats: Motivation is asserted, not proven. Table 3 row (A) shows h=1 at 24.9 BLEU vs 25.8 for base (h=8), and 25.4 at h=32 (compute held constant). Single dev-set translation task, one run per cell; not evidence about what individual heads 'mean'.

### A12. Splitting into heads does not add compute: each head works in a smaller dimension (d_model/h), so total cost is similar to one full-width head.

- Excerpt [V, §3.2.2 (p.5)]: "Due to the reduced dimension of each head, the total computational cost is similar to that of single-head attention with full dimensionality."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: mathematical-ish claim (asymptotic/parameter-count argument, stated without proof)
- Confidence: medium-high
- Notes / caveats: Stated, not derived, in the paper. Testable by counting FLOPs/parameters in a code demo. W^O adds d_model x d_model parameters.

### A13. Heads are independent of each other within a layer; 'concatenate then multiply by W^O' is mathematically the same as each head multiplying by its own slice of W^O and adding results.

- Excerpt [E, 'Attention Heads are Independent and Additive']: "Attention heads can be understood as independent operations, each outputting a result which is added into the residual stream."
- Excerpt [E, same section]: "Attention heads are often described in an alternate “concatenate and multiply” formulation for computational efficiency, but this is mathematically equivalent."
- Source id(s): E; URL: https://transformer-circuits.pub/2021/framework/index.html
- Version / accessed: E: Published Dec 22, 2021 (page shows no version number or commit; accessed 2026-10-19
- Type: mathematical (exact; testable by code)
- Confidence: high
- Notes / caveats: Elhage's derivation: W_O^H [r^h1; r^h2;...] = sum_i W_O^{h_i} r^{h_i}. Equivalence is exact; the 'independent' claim is about the computation inside a layer (heads read the same input, do not see each other's output within the layer).

### A14. Self-attention alone has no sense of order (it treats the sequence as a set), so position information must be injected.

- Excerpt [V, §3.5 (p.6)]: "in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition/design argument (the permutation-invariance of attention without positions is a mathematical fact, testable by code, but the paper states it only implicitly)
- Confidence: high
- Notes / caveats: The paper states the need but never writes 'attention is permutation-equivariant'. A lesson demo can show shuffling tokens (without positional info) merely shuffles the outputs. Do not attribute that exact sentence to Vaswani.

### A15. Original positional encodings: fixed sine/cosine waves of different frequencies, same size as the embedding, added to the input embeddings.

- Excerpt [V, §3.5 (p.6)]: "we add "positional encodings" to the input embeddings at the bottoms of the encoder and decoder stacks."
- Excerpt [V, §3.5 (p.6)]: "P E(pos,2i) = sin(pos/100002i/dmodel)"
- Excerpt [V, §3.5 (p.6)]: "The wavelengths form a geometric progression from 2π to 10000 · 2π."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition (exact formula; testable by code)
- Confidence: high
- Notes / caveats: Extraction mangled the formula (10000^(2i/d_model) printed as 100002i/dmodel); check against the PDF. Modern LLMs often use other schemes (e.g. learned or rotary); no source in this register covers those.

### A16. Why sinusoids: the authors hypothesized they make relative positions easy to learn, and they performed about as well as learned position embeddings.

- Excerpt [V, §3.5 (p.6)]: "we hypothesized it would allow the model to easily learn to attend by relative positions"
- Excerpt [V, §3.5 (p.6)]: "found that the two versions produced nearly identical results (see Table 3 row (E))."
- Excerpt [V, §3.5 (p.6)]: "because it may allow the model to extrapolate to sequence lengths longer than the ones encountered during training."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: hypothesis (rationale) + empirical (Table 3 row E: 25.7 vs 25.8 BLEU dev)
- Confidence: medium
- Notes / caveats: Both rationales are hedged ('hypothesized', 'may'). Row (E) is one task, one run. Do not teach sinusoids as uniquely necessary.

### A17. Around each sub-layer (attention, feed-forward) the original Transformer adds the input back (residual connection) and then applies layer normalization: LayerNorm(x + Sublayer(x)).

- Excerpt [V, §3.1 (p.3)]: "We employ a residual connection [11] around each of the two sub-layers, followed by layer normalization [ 1]."
- Excerpt [V, §3.1 (p.3)]: "the output of each sub-layer is LayerNorm(x + Sublayer(x))"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition (exact; testable by code)
- Confidence: high
- Notes / caveats: This is the original 'post-norm' placement. Many later models normalise before the sub-layer instead; none of the registered sources covers that, so do not claim it from these sources. Elhage et al. deliberately IGNORE layer norm in their analysis (see A31 notes).

### A18. The residual connection means each layer reads from and adds to a shared running vector (the 'residual stream') instead of replacing it.

- Excerpt [E, 'Virtual Weights and the Residual Stream as a Communication Channel']: "The residual stream is simply the sum of the output of all the previous layers and the original embedding."
- Excerpt [E, 'High-Level Architecture']: "Both the attention and MLP layers each “read” their input from the residual stream (by performing a linear projection), and then “write” their result"
- Source id(s): E; URL: https://transformer-circuits.pub/2021/framework/index.html
- Version / accessed: E: Published Dec 22, 2021 (page shows no version number or commit; accessed 2026-10-19
- Type: definition/framing (mathematically exact for the residual architecture; the 'stream' vocabulary is Elhage's framing)
- Confidence: medium-high
- Notes / caveats: Elhage works in a simplified setting: attention-only, no biases, layer norm ignored. 'Residual stream' is their terminology, not Vaswani's.

### A19. Original motivation: older encoder-decoder translators squeezed the whole source sentence into one fixed-length vector, which is a bottleneck; attention lets the decoder look back at all source positions instead.

- Excerpt [B, Abstract (p.1)]: "we conjecture that the use of a fixed-length vector is a bottleneck in improving the performance of this basic"
- Excerpt [B, §1 (p.2)]: "it does not attempt to encode a whole input sentence into a single fixed-length vector."
- Source id(s): B; URL: https://arxiv.org/abs/1409.0473
- Version / accessed: B: arXiv v7 (19 May 2016); accessed 2026-10-19
- Type: motivation (authors' conjecture) supported by empirical result (A20)
- Confidence: high
- Notes / caveats: The paper calls it a 'conjecture' in the abstract; Fig. 2 provides supporting evidence (A20). Note: the word 'attention' appears in the paper only in §3.1 ('this implements a mechanism of attention in the decoder'); the model is named RNNsearch.

### A20. Evidence for the bottleneck: the plain encoder-decoder's translation score drops sharply as sentences get longer, while the attention model (RNNsearch-50) shows no deterioration even at length 50+.

- Excerpt [B, §5.1 (p.6), Fig. 2]: "of RNNencdec dramatically drops as the length of the sentences increases."
- Excerpt [B, §5.1 (p.6)]: "RNNsearch-50, especially, shows no performance deterioration even with sentences of length 50 or more."
- Source id(s): B; URL: https://arxiv.org/abs/1409.0473
- Version / accessed: B: arXiv v7 (19 May 2016); accessed 2026-10-19
- Type: empirical (English-French, WMT'14, BLEU)
- Confidence: high for this setup
- Notes / caveats: Single language pair, RNN-based models, one training run per model. Table 1: RNNsearch-50 26.75 vs RNNencdec-50 17.82 BLEU (all sentences).

### A21. Bahdanau attention scores each source position with a small neural network (additive attention), then softmaxes the scores and takes a weighted sum; the score depends on the decoder's previous hidden state and the source annotation.

- Excerpt [B, §3.1 (p.3)]: "eij =a(si−1,h j) is an alignment model which scores how well the inputs around positionj and the output at position i match."
- Excerpt [B, Appendix A.1.2, Alignment Model (p.12)]: "a(si−1,h j) = v⊤a tanh (Wasi−1 +Uahj),"
- Source id(s): B; URL: https://arxiv.org/abs/1409.0473
- Version / accessed: B: arXiv v7 (19 May 2016); accessed 2026-10-19
- Type: definition (exact formula)
- Confidence: high
- Notes / caveats: This is 'additive' attention. The transformer's QK^T/sqrt(d_k) is 'dot-product' attention (A22). The appendix gives the single-layer MLP form of the alignment model a.

### A22. Vaswani chose dot-product scoring over additive scoring because it is faster and uses less memory in practice (it maps to optimized matrix multiplication), while being similar in theoretical complexity.

- Excerpt [V, §3.2.1 (p.4)]: "dot-product attention is much faster and more space-efficient in practice, since it can be implemented using highly optimized"
- Excerpt [V, §3.2.1 (p.4)]: "additive attention outperforms dot product attention without scaling for larger values of dk [3]."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: empirical/engineering claim (second excerpt cites another paper)
- Confidence: medium-high
- Notes / caveats: Performance claims are the authors' general statement, not benchmarked in this paper. The second excerpt shows scaling was introduced to close the gap with additive attention at large d_k.

### A23. Cost: a self-attention layer costs O(n^2 * d) per layer for sequence length n and representation size d (every token is compared with every other token); it is cheaper than a recurrent layer when n < d.

- Excerpt [V, Table 1 (p.6)]: "Self-Attention O(n2 · d) O(1) O(1)"
- Excerpt [V, §4 (p.7; the sentence begins on p.6)]: "length n is smaller than the representation dimensionality d"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: mathematical (asymptotic complexity)
- Confidence: high
- Notes / caveats: Extraction lost the superscript (n2 = n^2). The same table gives Recurrent O(n·d^2) with O(n) sequential operations. This is asymptotic per-layer complexity, not wall-clock speed. The n<d condition is the paper's, for sentence-length inputs; for very long sequences the quadratic term dominates (the paper proposes restricted self-attention, O(r·n·d), as future work).

### A24. Self-attention connects every pair of positions in a constant number of sequential steps, whereas a recurrent layer needs a number of steps proportional to length; this helps parallelism and learning long-range dependencies.

- Excerpt [V, §4 (p.6)]: "a self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires O(n) sequential operations."
- Excerpt [V, §4 (p.6)]: "The shorter these paths between any combination of positions in the input and output sequences, the easier it is to learn long-range dependencies"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: mathematical (path length/sequential ops) + hypothesis (shorter paths -> easier learning, citing [12])
- Confidence: medium-high
- Notes / caveats: Second excerpt is a general claim supported by a citation, not tested here.

### A25. Averaging over attended positions loses resolution; multi-head attention is the authors' remedy.

- Excerpt [V, §2 (p.2)]: "albeit at the cost of reduced effective resolution due to averaging attention-weighted positions, an effect we counteract with Multi-Head Attention"
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: motivation (authors' claim)
- Confidence: medium
- Notes / caveats: Qualitative; ties A11 to the weighted-sum view. Stated without a dedicated experiment.

### A26. Causal (masked) attention: in the decoder, scores for future positions are set to minus infinity before the softmax, so after softmax those positions get weight 0 and a token cannot see later tokens.

- Excerpt [V, §3.2.3 (p.5)]: "We need to prevent leftward information flow in the decoder to preserve the auto-regressive property."
- Excerpt [V, §3.2.3 (p.5)]: "masking out (setting to −∞) all values in the input of the softmax which correspond to illegal connections."
- Excerpt [V, §3.1 (p.3)]: "prevent positions from attending to subsequent positions."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: mathematical (exact; testable by code: exp(-inf)=0)
- Confidence: high
- Notes / caveats: Vaswani says 'leftward information flow' where 'leftward' is the paper's orientation (tokens to be generated); the plain-English meaning is 'no looking at later tokens'. exp(-inf)=0 and weight-0 are consequences of softmax, not quoted. A position may attend to itself: 'all positions in the decoder up to and including that position' (§3.2.3).

### A27. Implementation of the causal mask in code: a lower-triangular boolean matrix (diagonal included) marks allowed positions; disallowed scores are filled with -inf before softmax.

- Excerpt [P, pseudo-code in doc 'scaled_dot_product_attention' (torch 2.14)]: "temp_mask = torch.ones(L, S, dtype=torch.bool, device=query.device).tril(diagonal=0)"
- Excerpt [P, pseudo-code]: "attn_bias.masked_fill_(temp_mask.logical_not(), float("-inf"))"
- Excerpt [P, Parameter docs, is_causal]: "If set to true, the attention masking is a lower triangular matrix when the mask is a square matrix."
- Source id(s): P; URL: https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html
- Version / accessed: P: PyTorch 2.14 documentation (page title); accessed 2026-10-19
- Type: mathematical/API definition (testable by code)
- Confidence: high
- Notes / caveats: API reference, not a paper. The doc says its code is 'equivalent' to the efficient kernel; floating-point results may differ across backends: 'the output of this function may be different depending on what backend kernel is chosen.' Doc is for PyTorch 2.14 (accessed 2026-10-19).

### A28. Reference pseudo-code for one head (PyTorch): scores = Q K^T times scale (default 1/sqrt(E), E = last dimension of the query), add mask bias, softmax over the last dimension, multiply by V.

- Excerpt [P, pseudo-code]: "scale_factor = 1 / math.sqrt(query.size(-1)) if scale is None else scale"
- Excerpt [P, pseudo-code]: "attn_weight = query @ key.transpose(-2, -1) * scale_factor"
- Excerpt [P, pseudo-code]: "attn_weight = torch.softmax(attn_weight, dim=-1)"
- Excerpt [P, pseudo-code]: "return attn_weight @ value"
- Source id(s): P; URL: https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html
- Version / accessed: P: PyTorch 2.14 documentation (page title); accessed 2026-10-19
- Type: mathematical (exact reference implementation; testable by code)
- Confidence: high
- Notes / caveats: Matches Vaswani Eq. (1). The doc header says 'Efficient implementation equivalent to the following:'. Dropout on the weights is also in the pseudo-code (attn_weight = torch.dropout(attn_weight, dropout_p, train=True)); the doc WARNS dropout is always applied unless dropout_p=0.0. Note scale is on the last dim of the query, which equals d_k per head.

### A29. Gotcha: in PyTorch's scaled_dot_product_attention a True entry in a boolean mask means 'may attend'; this is the opposite of MultiheadAttention's key_padding_mask where True means 'masked out'.

- Excerpt [P, 'Note' on boolean mask semantics]: "The boolean mask semantics for attn_mask are the inverse of MultiheadAttention’s key_padding_mask."
- Excerpt [P, same note]: "In scaled_dot_product_attention(), True indicates values to participate in attention."
- Source id(s): P; URL: https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html
- Version / accessed: P: PyTorch 2.14 documentation (page title); accessed 2026-10-19
- Type: definition (API semantics)
- Confidence: high
- Notes / caveats: Version-specific API behaviour (PyTorch 2.14 docs); the doc also marks the function 'beta and subject to change'. Useful warning for any lesson code that builds masks.

### A30. The first instance of attention in neural translation produced a readable soft-alignment between target and source words, which the authors presented as intuitive evidence for what the model attended to.

- Excerpt [B, §5.2.1 (p.7)]: "The proposed approach provides an intuitive way to inspect the (soft-)alignment between the words in a generated translation and those in a source sentence."
- Excerpt [B, §5.2.1 (p.7)]: "From this we see which positions in the source sentence were considered more important when generating the target word."
- Source id(s): B; URL: https://arxiv.org/abs/1409.0473
- Version / accessed: B: arXiv v7 (19 May 2016); accessed 2026-10-19
- Type: empirical/qualitative
- Confidence: medium
- Notes / caveats: Qualitative inspection on a few sentences (Fig. 3). Read together with J&W/W&P (A35-A37): the later literature questions how far such heatmaps explain model decisions. Bahdanau's claim is also modest: 'considered more important', for a translation model, not a classification model.

### A31. A head can be split into two independent parts: a QK circuit that decides WHERE to attend (the attention pattern) and an OV circuit that decides WHAT is moved from the attended token.

- Excerpt [E, Summary, 'Conceptual Take-Aways']: "a QK (“query-key”) circuit which computes the attention pattern, and an OV (“output-value”) circuit which computes how each token affects the output if attended to."
- Excerpt [E, 'Observations about Attention Heads']: "A governs which token's information is moved from and to."
- Excerpt [E, 'Observations about Attention Heads']: "W_O W_V governs which information is read from the source token and how it is written to the destination token."
- Source id(s): E; URL: https://transformer-circuits.pub/2021/framework/index.html
- Version / accessed: E: Published Dec 22, 2021 (page shows no version number or commit; accessed 2026-10-19
- Type: mathematical reformulation (exact algebra; testable by code) + interpretive framing
- Confidence: high for the algebra; the interpretive value is the authors' framing
- Notes / caveats: Elhage et al. study toy models: 'transformers with two layers or less which have only attention blocks', no MLPs, biases omitted, and 'We also ignore layer normalization'. Applying the QK/OV picture to full models is an extension they hedge ('partially relevant for much larger'). Paper is a blog-style publication (Transformer Circuits Thread), not peer-reviewed; published Dec 22, 2021. They name the pieces W_QK = W_Q^T W_K and W_OV = W_O W_V.

### A32. Keys, queries and values are intermediate by-products: only the products W_Q^T W_K and W_O W_V matter for the head's function, so q/k/v vectors can be re-parameterized without changing the function.

- Excerpt [E, 'Observations about Attention Heads']: "Keys, queries and value vectors are, in some sense, superficial."
- Excerpt [E, 'Observations about Attention Heads']: "They’re intermediary by-products of computing these low-rank matrices."
- Excerpt [E, 'Observations about Attention Heads']: "One could easily reparametrize both factors of the low-rank matrices to create different vectors, but still function identically."
- Source id(s): E; URL: https://transformer-circuits.pub/2021/framework/index.html
- Version / accessed: E: Published Dec 22, 2021 (page shows no version number or commit; accessed 2026-10-19
- Type: mathematical (exact)
- Confidence: high
- Notes / caveats: This is a framing that deliberately cuts against the standard Q/K/V teaching. Keep Q/K/V for the lesson (it matches Vaswani, PyTorch) but note the head's behaviour only depends on the products. Hedged by the words 'in some sense'.

### A33. Attention heads move information between token positions: each head reads from one token's residual-stream vector and writes into another's; with a FIXED attention pattern a head is linear, so the only nonlinearity inside a head is the softmax.

- Excerpt [E, 'Observations about Attention Heads']: "Attention heads move information from the residual stream of one token to another."
- Excerpt [E, 'Observations about Attention Heads']: "A is the only non-linear part of this equation (being computed from a softmax)."
- Excerpt [E, 'Observations about Attention Heads']: "This also means that, without fixing A, attention heads are “half-linear” in some sense"
- Source id(s): E; URL: https://transformer-circuits.pub/2021/framework/index.html
- Version / accessed: E: Published Dec 22, 2021 (page shows no version number or commit; accessed 2026-10-19
- Type: mathematical (exact)
- Confidence: high
- Notes / caveats: 'A' = softmax(x^T W_Q^T W_K x) (with the autoregressive mask in their notation, softmax*). Their 'result vector' step r_i = sum_j A_ij v_j is the weighted sum of values (A09).

### A34. Attention is not the whole Transformer: the original architecture also uses word embeddings, positional encodings, position-wise feed-forward networks, residual connections and layer norm.

- Excerpt [V, Abstract (p.1)]: "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
- Excerpt [V, §3.3 (p.5)]: "each of the layers in our encoder and decoder contains a fully connected feed-forward network, which is applied to each position separately and identically."
- Excerpt [V, §3.1 (p.3)]: "Each layer has two sub-layers. The first is a multi-head self-attention mechanism, and the second is a simple, position-wise fully connected feed-forward network."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: definition (architecture fact)
- Confidence: high
- Notes / caveats: Contradicts the folklore reading of the title 'Attention Is All You Need' as 'nothing but attention'. The abstract's 'solely on attention' is relative to the removal of recurrence and convolutions, not of feed-forward layers, embeddings, residuals, layer norm, positional encodings, or the output softmax layer. Elhage et al. also stress that real models alternate attention with MLP blocks ('alternates attention blocks with MLP blocks') and say they understand MLP layers much less well.

### A35. Attention weights are not necessarily explanations of a model's prediction: learned attention weights correlate only weakly with gradient-based importance, and very different attention weights can give the same prediction.

- Excerpt [J, Abstract (p.1)]: "We find that they largely do not."
- Excerpt [J, Abstract (p.1)]: "nonetheless yield equivalent predictions."
- Excerpt [J, Abstract (p.1)]: "do not provide meaningful explanations and should not be treated as though they do."
- Excerpt [J, Fig. 1 caption (p.1)]: "Despite being quite dissimilar, these both yield effectively the same prediction (0.01)."
- Source id(s): J; URL: https://arxiv.org/abs/1902.10186
- Version / accessed: J: arXiv v3 (8 May 2019); accessed 2026-10-19
- Type: empirical
- Confidence: medium-high within scope
- Notes / caveats: SCOPE: BiLSTM encoders + additive or scaled dot-product attention on one query, for text classification, NLI and QA. NOT multi-head Transformer self-attention. Authors themselves note the limits: 'it remains a possibility that agreement is strong between attention weights and feature importance scores for the top-k features only', 'at least for RNN-based models', 'Alternative attention specifications may yield different conclusions', and for simple feed-forward (average) encoders 'attention weights ... exhibit stronger correlations'. Using v3 (8 May 2019), the post-conference version. Numbers quoted in the paper's introduction (p.2, not excerpted above): Kendall tau between attention and gradient importance = 0.29 for the Fig. 1 example; randomly permuting attention gives a median output difference of 0.006. Fig. 1 (p.1) shows the original vs adversarial attention heatmaps giving the same 0.01 prediction.

### A36. Jain & Wallace warn against telling just-so stories from attention heatmaps: highlighting attended tokens as 'responsible for' the output can be misleading.

- Excerpt [J, §1 (p.2)]: "We thus caution against using attention weights to highlight input tokens “responsible for” model outputs and constructing just-so stories on this basis."
- Excerpt [J, §6 (pp.10-11)]: "their ability to provide transparency or meaningful explanations for model predictions is, at best, questionable"
- Source id(s): J; URL: https://arxiv.org/abs/1902.10186
- Version / accessed: J: arXiv v3 (8 May 2019); accessed 2026-10-19
- Type: empirical conclusion + authors' recommendation
- Confidence: medium-high
- Notes / caveats: The words 'at best, questionable' are the authors' hedged conclusion; same scope limits as A35.

### A37. The rebuttal: whether attention is an explanation depends on what you mean by 'explanation' (plausible vs. faithful); the existence of an alternative attention distribution does not make the original one meaningless.

- Excerpt [W, §6 (p.9)]: "Whether or not attention is explanation depends on the definition of explainability one is looking for: plausible or faithful explanations (or both)."
- Excerpt [W, §5 (p.8; sentence continues 'or meaningless' on p.9)]: "does not mean that the one provided is false"
- Excerpt [W, §6 (p.9)]: "adversarial distributions can be found for LSTM models in some classification tasks, as originally hypothesized by Jain and Wallace."
- Source id(s): W; URL: https://arxiv.org/abs/1908.04626
- Version / accessed: W: arXiv v2 (5 Sep 2019); accessed 2026-10-19
- Type: empirical + conceptual argument
- Confidence: medium-high
- Notes / caveats: W&P do NOT overturn J&W: they confirm adversarial distributions can be found for LSTM models in some tasks, but argue (a) the setup left too much freedom ('an implausibly large amount of freedom'), (b) a uniform-attention baseline shows attention is unnecessary on some datasets, and (c) frozen-weights diagnostic suggests trained attention is coherent. Same RNN scope. v2 (5 Sep 2019). The two papers disagree on interpretation, not primarily on the raw facts.

### A38. On some tasks attention does little: freezing attention weights to uniform barely hurts accuracy, so there attention carries little 'explanation' to extract.

- Excerpt [W, §3.2 (p.4)]: "three of the classification tasks the attention layer appears to offer little to no improvement"
- Excerpt [W, §3.2 (p.4)]: "We conclude that these datasets, notably AG NEWS and 20 NEWSGROUPS, are not useful test cases for the debated question"
- Source id(s): W; URL: https://arxiv.org/abs/1908.04626
- Version / accessed: W: arXiv v2 (5 Sep 2019); accessed 2026-10-19
- Type: empirical
- Confidence: medium-high (tasks: AG News, 20 Newsgroups, SST borderline)
- Notes / caveats: RNN-with-attention classifiers, English datasets. A caution that 'the model attends to X' is only informative if attention was needed for the task.

### A39. The original authors themselves claimed some interpretability benefit but hedged it: attention distributions inspected in the appendix 'appear' to relate to sentence structure.

- Excerpt [V, §4 (p.7)]: "As side benefit, self-attention could yield more interpretable models."
- Excerpt [V, Fig. 4 caption (p.14)]: "Two attention heads, also in layer 5 of 6, apparently involved in anaphora resolution."
- Excerpt [V, §4 (p.7)]: "many appear to exhibit behavior related to the syntactic and semantic structure of the sentences."
- Source id(s): V; URL: https://arxiv.org/abs/1706.03762
- Version / accessed: V: arXiv v7 (2 Aug 2023); accessed 2026-10-19
- Type: empirical/qualitative (hand-picked examples) with hedged wording
- Confidence: low-medium as evidence
- Notes / caveats: Words used: 'could', 'apparently', 'appear'. Examples are chosen visualizations of a few heads in layer 5 of 6; no quantitative test. This is the source folklore draws on ('attention shows what the model is thinking'); compare A35-A38.

### A40. Context: the original Transformer had an encoder-decoder shape (needed for translation) with three kinds of attention; many modern language models keep only the masked self-attention decoder stack.

- Excerpt [V, §3.2.3 (p.5)]: "In "encoder-decoder attention" layers, the queries come from the previous decoder layer, and the memory keys and values come from the output of the encoder."
- Excerpt [E, 'High-Level Architecture']: "The original transformer paper had a special encoder-decoder structure to support translation, but many modern language models don't include this."
- Source id(s): V, E; URL: https://arxiv.org/abs/1706.03762; https://transformer-circuits.pub/2021/framework/index.html
- Version / accessed: V: arXiv v7 (2 Aug 2023); E: Published Dec 22, 2021 (page shows no version number or commit; accessed 2026-10-19
- Type: definition + framing
- Confidence: high for Vaswani; medium-high for Elhage's characterization
- Notes / caveats: Elhage's statement about 'many modern language models' is a 2021 characterization, not a survey. Cross-attention (queries from decoder, keys/values from encoder) is a different wiring of Q, K and V from self-attention.

## 4. Conflicts, caveats and folklore contradicted

1. 'Attention is all you need' does not mean attention only (A34). The Transformer keeps embeddings, positional encodings, position-wise feed-forward layers, residual connections and layer norm. Its claim is dropping recurrence and convolutions.
2. 'Attention weights explain the model' is contested (A35-A39). Jain & Wallace (RNN/BiLSTM text classification, NLI, QA) find weak correlation with gradient/LOO importance and equivalent predictions under very different weights; Wiegreffe & Pinter argue the verdict depends on whether 'explanation' means plausible or faithful, and that J&W's setup is too permissive, while confirming adversarial distributions exist for LSTMs on some tasks. Neither paper tested multi-head Transformer self-attention. Vaswani itself hedges ('could', 'apparently', 'appear'). Safe lesson wording: attention weights show where a head reads from; they are not by themselves a proof of why the model predicted something.
3. The sqrt(d_k) story (A06, A07): the variance computation is exact only under the assumption of independent, zero-mean, unit-variance components; the claim that large dot products saturate softmax is described by the authors as a suspicion ('We suspect'), and the empirical support they cite is another paper ([3], additive vs unscaled dot-product). Do not present it as measured on trained weights. The lesson can demonstrate it numerically with random Q, K.
4. Q/K/V are not sacred (A32): Elhage et al. call keys, queries and values 'superficial' by-products of W_QK and W_OV. This is an algebraic restatement, compatible with the standard picture, but changes emphasis. Their analysis is restricted to toy attention-only models and ignores layer norm and biases.
5. Multi-head (A11, A12, A13): the 'different subspaces' rationale is a motivation; the only direct evidence is Table 3 row (A) (BLEU on one task). 'Concatenate then W^O' is exactly equivalent to a sum of per-head outputs (Elhage).
6. Positional encodings (A14-A16): the need is argued from the absence of recurrence/convolution; sinusoids were chosen on hypotheses; learned positions were nearly identical in BLEU (25.7 vs 25.8, dev). Modern models often use other schemes; no source here covers them.
7. Causal mask nuance (A26, A27): a token may attend to itself (diagonal included); masked scores are -inf before softmax. Vaswani's decoder additionally offsets output embeddings by one position so predictions for position i depend only on positions less than i.
8. Residual + layer norm (A17): original paper is post-norm LayerNorm(x + Sublayer(x)). No registered source covers pre-norm; do not assert that modern models differ based on these sources.
9. Cost (A23): O(n^2 · d) is the paper's asymptotic per-layer count; its 'faster than recurrent when n < d' condition is specific to the regime it considers. Not a wall-clock claim. PyTorch docs note fused kernels may produce slightly different outputs.
10. Terminology drift: Bahdanau uses annotations/alignment/context vector and an additive score; Vaswani introduces dot-product Q/K/V terminology. 'Attention' in Bahdanau §3.1 is a mechanism in the decoder; Vaswani's self-attention relates positions within one sequence.
11. PyTorch version/doc caveat (A27-A29): API docs for 2.14 mark the function as beta; boolean mask polarity is opposite to MultiheadAttention's key_padding_mask.
12. Unverified items not claimed: the exact PDF rendering of equations; Hugging Face docs on masking; any claim about GQA/KV-cache/FlashAttention beyond the one line in the PyTorch doc.
