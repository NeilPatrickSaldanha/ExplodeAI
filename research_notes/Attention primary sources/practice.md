# Attention in practice: primary-source research notes (Lesson 04)

Researcher output for ExplodeAI Lesson 04 "Attention, exploded". Accessed 2026-10-19/20. All excerpts were machine-checked as verbatim substrings (whitespace, ligature, hyphenation-at-line-break and curly-quote normalised) against text extracted from the raw downloads (curl; PDFs via pypdf 6.21.1). No paid API calls. Excerpts are <=25 words. Complementary file: foundations.md (other researcher).

Raw downloads and extraction scripts: `/private/tmp/claude-501/-Users-neilpatricksaldanha/f38d2988-21ba-480c-87af-48cdd1fde197/scratchpad/attn_research2/{raw,txt,scripts,bge}`.

## Source register

| ID | Source | URL | Version / date / commit | Kind | Integrity |
|---|---|---|---|---|---|
| S1 | Vaswani et al., "Attention Is All You Need" | https://arxiv.org/abs/1706.03762 (PDF /pdf/1706.03762) | arXiv v7 (v1 2017-06-12) | paper | raw/1706.03762.pdf sha256 bdfaa68d8984 |
| S2 | Dao et al., "FlashAttention" | https://arxiv.org/abs/2205.14135 ; HTML https://arxiv.org/html/2205.14135v2 | arXiv v2 (PDF dated 2022-06-24) | paper | pdf ca7f9fda10b9 |
| S3 | Devlin et al., "BERT" | https://arxiv.org/abs/1810.04805 | arXiv v2 (v1 2018-10-11) | paper | pdf 5692a5514787 |
| S4 | Su et al., "RoFormer" | https://arxiv.org/abs/2104.09864 | arXiv v5 (PDF dated 2023-11-09) | paper | pdf e9a481fbe1c8 |
| S5 | Shazeer, "Fast Transformer Decoding: One Write-Head is All You Need" (MQA) | https://arxiv.org/abs/1911.02150 | arXiv v1 (2019-11-06) | paper | pdf 3250947d7be3 |
| S6 | Ainslie et al., "GQA" | https://arxiv.org/abs/2305.13245 | arXiv v3 (v1 2023-05-22) | paper | pdf ba9094fe73db |
| S7 | Jain & Wallace, "Attention is not Explanation" | https://arxiv.org/abs/1902.10186 | arXiv v3 (v1 2019-02-26) | paper | pdf ffc666e7e27d |
| S8 | Wiegreffe & Pinter, "Attention is not not Explanation" | https://arxiv.org/abs/1908.04626 | arXiv v2 (v1 2019-08-13) | paper | pdf d9e507dfa544 |
| S9 | Brown et al., "Language Models are Few-Shot Learners" (GPT-3) | https://arxiv.org/abs/2005.14165 | arXiv v4 (latest at access) | paper | pdf 97fd272f1fdf |
| S10 | Radford et al., "Language Models are Unsupervised Multitask Learners" (GPT-2) | https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf | OpenAI-hosted PDF, 2019, no version label | paper (non-arXiv) | pdf d9d852e28945 |
| S11 | Milakov & Gimelshein, "Online normalizer calculation for softmax" | https://arxiv.org/abs/1805.02867 | arXiv v2 | paper | pdf 722747b3a32e |
| S12 | Hugging Face Transformers docs, "Cache strategies" (kv_cache) | https://huggingface.co/docs/transformers/v5.20.2/en/kv_cache | Transformers v5.20.2 docs; no page date; accessed 2026-10-19 | official docs | html f713f0fd0326 |
| S13 | Hugging Face Transformers docs, "How caching works" (cache_explanation) | https://huggingface.co/docs/transformers/v5.20.2/en/cache_explanation | v5.20.2; no page date; accessed 2026-10-19 | official docs | html 24a02b1e2aaf |
| S14 | Hugging Face Transformers docs, "Glossary" | https://huggingface.co/docs/transformers/v5.20.2/en/glossary | v5.20.2; no page date; accessed 2026-10-19 | official docs | html fd28f670d5d7 |
| S15 | Hugging Face Transformers docs, "Optimizing LLMs for Speed and Memory" | https://huggingface.co/docs/transformers/v5.20.2/en/llm_tutorial_optimization | v5.20.2; no page date; accessed 2026-10-19 | official docs (tutorial) | html 492467b8e25c |
| S16 | Hugging Face Transformers docs, "Causal language modeling" (tasks/language_modeling) | https://huggingface.co/docs/transformers/v5.20.2/en/tasks/language_modeling | v5.20.2; no page date; accessed 2026-10-19 | official docs | html 21e6eb5be133 |
| S17 | PyTorch docs, torch.nn.functional.scaled_dot_product_attention | https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html | PyTorch 2.14; accessed 2026-10-19 | official docs | saved raw/pt_sdpa.html |
| S18 | PyTorch docs, torch.nn.functional.softmax | https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.softmax.html | PyTorch 2.14; accessed 2026-10-19 | official docs | saved raw/pt_softmax.html |
| S19 | BAAI/bge-small-en-v1.5 config.json (HF Hub) | https://huggingface.co/BAAI/bge-small-en-v1.5/raw/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a/config.json | commit 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a (lastModified 2024-02-22T03:36:23Z, repo head at access 2026-10-19) | model config | sha 094f8e891b93 |
| S20 | BAAI/bge-small-en-v1.5 sentence_bert_config.json + README | https://huggingface.co/BAAI/bge-small-en-v1.5/raw/5c38ec7c405ec4b44b94cc5a9bb96e735b38267a/sentence_bert_config.json | same commit 5c38ec7 | model config | sha 84e39fda68cc |

Not cited but downloaded: GShard arXiv 2006.16668 v1 (checked as a possible MQA-use source; not needed).

Notes on source handling: (a) "Type" labels: mathematical = follows from definitions; empirical = measured/observed; provider- or model-specific = true of a named model, library or doc version at a date; definition = naming/convention. (b) HF docs pages show no "last updated" date; the URL is pinned to the v5.20.2 docs build and dated by access time. A parallel fetch of the unversioned /en/ URLs returned the same text for kv_cache and cache_explanation. (c) PyTorch pages redirect from /stable/ to /2.14/; 2.14 was stable on 2026-10-19.

## Conflicts and cross-source tensions (summary)

1. "Attention memory is quadratic" (C03, C07) vs FlashAttention giving O(N) extra memory with O(N^2 d) FLOPs (C04): both true; the first describes standard materialised attention. Teach: compute stays quadratic; the big score table need not be stored.
2. Per-step KV-cache cost: HF says "linear" with cache vs "quadratic" without (C11); total cost over a reply is still quadratic either way (sum of steps), and the cache itself costs memory growing linearly with length (C12).
3. Attention as explanation: Jain & Wallace (C36) vs Wiegreffe & Pinter (C37) disagree; both studied RNN+attention models, not Transformer self-attention.
4. Mask polarity differs between APIs (C18 vs C19).
5. Vaswani head-count (8 heads x 64, d_model 512) differs from BERT-base (12 x 64, 768) and bge-small (12 x 32, 384); head width is not constant at 64 (C21, C23-C25).
6. "Near one-hot" softmax saturation has no verbatim primary source in this set (C45); only the "extremely small gradients" wording does (C39).

## Claims

### C01. Self-attention compares every token with every other token, so its per-layer cost grows with the square of the sequence length n (times the vector width d).

- **Source:** S1 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "n is the sequence length, d is the representation dimension" — Table 1 caption, p.6
  - "Self-Attention O(n2 · d) O(1) O(1)" — Table 1 row 1, p.6 (superscript flattened to "n2" by text extraction; PDF shows n squared)
- **Caveats:** Table 1 is per-layer compute for the full (unrestricted) self-attention; Vaswani also lists restricted self-attention O(r·n·d). Compares layer types, not whole-model cost.

### C02. Self-attention is cheaper than a recurrent layer only while the sequence is shorter than the vector width; the quadratic term is what hurts for long inputs.

- **Source:** S1 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "length n is smaller than the representation dimensionality d, which is most often the case" — p.7 (continues from p.6: "self-attention layers are faster than recurrent layers when the sequence")
- **Caveats:** 2017 translation setting (word-piece/BPE sentences); modern contexts of 100k+ tokens exceed d, reversing the comparison.

### C03. Long inputs are costly because attention time AND memory both grow quadratically with sequence length.

- **Source:** S2 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "time and memory complexity of self-attention are quadratic in sequence length" — Abstract
  - "has time and memory complexity quadratic in sequence length" — §1 Introduction, para 1
- **Caveats:** Stated for standard (dense, exact) attention. FlashAttention itself keeps the quadratic compute but not quadratic memory (see C04).

### C04. A standard implementation builds an N-by-N score table (O(N^2) memory); FlashAttention computes the same exact result in tiles with only O(N) extra memory, but still O(N^2 d) arithmetic.

- **Source:** S2 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "Standard attention implementations materialize the matrices" — §2.2 (sentence continues "S and P to HBM, which takes O(N^2) memory")
  - "additional memory beyond inputs and output" — §3.1 Theorem 1 (full text: "returns O = softmax(QK^T)V with O(N^2 d) FLOPs and requires O(N) additional memory beyond inputs and output")
- **Caveats:** Complexity symbols (O(N^2), O(N^2 d), O(N)) read from the arXiv HTML v2 / PDF p.5 text; excerpts above are cut at the math to stay verbatim. CONFLICT/NUANCE: "memory quadratic" (C03) is true of standard attention only; FlashAttention paper says compute stays quadratic (O(N^2 d)) while extra memory is linear. Model weights and KV cache are separate costs.

### C05. Wall-clock runtime of exact attention still grows quadratically with sequence length, even with the faster FlashAttention kernel.

- **Source:** S2 (see register)
- **Type:** empirical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "Runtime grows quadratically with sequence length" — §4.3 Fig. 3 discussion
- **Caveats:** Measured on specific GPUs (A100) in a benchmark; the paper reports FlashAttention up to 3x faster than the PyTorch implementation there, not a change in asymptotics.

### C06. Practitioners avoid long sequences during training because attention cost is quadratic: BERT was mostly trained on 128-token sequences and only briefly on 512.

- **Source:** S3 (see register)
- **Type:** empirical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "Longer sequences are disproportionately expensive because attention is quadratic to the sequence length." — Appendix A.2 Pre-training Procedure
  - "we pre-train the model with sequence length of 128 for 90% of the steps" — Appendix A.2
- **Caveats:** BERT-specific 2018 training recipe on 16 Cloud TPUs; a design choice, not a law.

### C07. Hugging Face states that attention memory and compute grow quadratically with the number of input tokens and become a serious problem around 16,000 tokens.

- **Source:** S15 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** Medium
- **Excerpts (verbatim):**
  - "grows quadratically both in compute and memory complexity with number of input tokens" — §3 Architectural innovations section intro / "Flash Attention" section
  - "it becomes a serious problem for longer input sequences (at around 16000 input tokens)" — same paragraph
- **Caveats:** Docs tutorial (v5.20.2 build, accessed 2026-10-19); the 16k figure is the tutorial authors' rule of thumb tied to its example GPU/model, not a universal threshold. Wording says peak GPU memory of the naive implementation.

### C08. During generation the model stores the keys and values of tokens already processed (the KV cache) and reuses them instead of recomputing them for every new token.

- **Source:** S13 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "A key-value (KV) cache eliminates this inefficiency by storing kv pairs derived from the attention layers of previously processed tokens." — "How caching works", para 1
  - "The stored kv pairs are retrieved from the cache and reused for subsequent tokens, avoiding the need to recompute." — same
- **Caveats:** Docs page has no visible date; version v5.20.2 build, accessed 2026-10-19. Applies to decoder-style autoregressive generation, not to encoder models like bge/BERT embedding.

### C09. Why the cache is valid: with a causal mask, a processed token never changes in response to later tokens, so its past keys and values can be kept.

- **Source:** S13 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "Once a token is processed, its representation never changes with respect to future tokens" — "How caching works", Attention matrices
  - "At inference time, you only need the last token’s query to compute the representation" — same section
- **Caveats:** Only holds for causal (left-to-right) attention; bidirectional encoders recompute everything.

### C10. Only one new query/key/value is computed per step, and the new key and value are appended to the cache; the cache is kept per layer with shape [batch, heads, seq_len, head_dim].

- **Source:** S13 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "At each step, the new key and value vectors are stored in the cache and appended to the past keys and values." — "How caching works"
  - "The key and value caches are tensors with the shape [batch_size, num_heads, seq_len, head_dim]." — "Cache storage implementation"
- **Caveats:** Transformers library implementation (DynamicCache); other runtimes may lay memory out differently.

### C11. Per generation step, cached attention cost grows linearly with the length so far, versus quadratically without a cache; memory for the cache grows linearly.

- **Source:** S13 (see register)
- **Type:** mathematical  |  **Confidence:** Medium
- **Excerpts (verbatim):**
  - "attention cost per step is quadratic with sequence length" — Table "without caching / with caching", left column
  - "attention cost per step is linear with sequence length" — same table, right column
- **Caveats:** "Per step" figures. Over a whole reply of L tokens the total is still O(L^2) with cache (sum of linear steps). HF table cell also notes "(memory grows linearly, but compute/token remains low)". Teach as "each new token no longer redoes the old work".

### C12. The KV cache trades compute for memory: it can be large for long inputs because it stores keys and values for every past token, every layer and every head.

- **Source:** S15 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "two times the sequence length times the number of attention heads times the attention head dimension and times the number of layers" — §3.2 key-value cache
  - "Roughly 8 billion float values! Storing 8 billion float values in float16 precision requires around 15 GB of RAM" — same
- **Caveats:** Formula (2 x seq x heads x head_dim x layers) is general for standard multi-head attention; the 8 billion / 15 GB number is for bigcode/octocoder (16B-class) at a hypothetical 16,000 tokens, float16. GQA/MQA models store fewer heads (C25-C26). Doc date: v5.20.2 build, accessed 2026-10-19.

### C13. Caching is for inference only; the Transformers docs warn it can cause errors if enabled during training.

- **Source:** S13, S12 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "Caching should only be used for inference" — "How caching works", para 1
  - "Disable the cache by configuring use_cache=False in generate()." — "Cache strategies", Default cache
- **Caveats:** Hugging Face Transformers behaviour, v5.20.2 docs. The second excerpt text appears in the docs as use_cache=False in generate() with code formatting; extracted text matches.

### C14. A decoder-only language model uses a causal mask: when predicting position i it may look only at positions up to i; future positions are blocked by setting their scores to minus infinity before softmax.

- **Source:** S1 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "masking out (setting to −∞) all values in the input of the softmax which correspond to illegal connections" — §3.2.3, decoder self-attention bullet
  - "all positions in the decoder up to and including that position" — §3.2.3
- **Caveats:** Vaswani describes the encoder-decoder Transformer decoder; GPT-style models use the same mechanism with no encoder.

### C15. Causal language modeling: the model predicts the next token and can only attend to the left, so it cannot see the future.

- **Source:** S16, S14 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "Causal language modeling predicts the next token in a sequence of tokens, and the model can only attend to tokens on the left." — "Causal language modeling" task guide, intro
  - "using a mask inside the model to hide the future tokens at a certain timestep" — Glossary, "causal language modeling"
- **Caveats:** HF docs v5.20.2 build, accessed 2026-10-19. Also confirmed for GPT in BERT paper (C16).

### C16. GPT-style models use "constrained" self-attention where each token sees only its left context; BERT uses bidirectional self-attention.

- **Source:** S3 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "the BERT Transformer uses bidirectional self-attention, while the GPT Transformer uses constrained self-attention where every token can only attend to context to its left" — §3 Model Architecture, p.3
- **Caveats:** The GPT-2 paper itself (S10) describes autoregressive factorisation p(sn|s1..sn-1) but does not spell out the mask; GPT-3 (S9) says "autoregressive language model" and "same model and architecture as GPT-2".

### C17. In PyTorch the causal mask is a lower-triangular matrix: allowed positions are kept, disallowed positions get -inf, then softmax gives them zero weight.

- **Source:** S17 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "temp_mask = torch.ones(L, S, dtype=torch.bool, device=query.device).tril(diagonal=0)" — scaled_dot_product_attention reference code
  - "attn_bias.masked_fill_(temp_mask.logical_not(), float("-inf"))" — same
- **Caveats:** PyTorch 2.14 docs, accessed 2026-10-19; function page carries a "beta and subject to change" warning. This is the documented reference equivalent; fused kernels compute the same result differently. Verification below matches after whitespace removal (docs render code with extra spaces).

### C18. attention_mask (padding mask) and the causal mask are different things: attention_mask says which tokens are real versus padding added to batch sequences; the causal mask hides future tokens.

- **Source:** S14 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "The attention mask is a binary tensor indicating the position of the padded indices so that the model does not attend to them." — Glossary, "attention mask"
  - "1 indicates a value that should be attended to, while 0 indicates a padded value" — same
- **Caveats:** Glossary entry is for BertTokenizer conventions; "attention_mask" semantics (1 = attend, 0 = ignore) hold across HF tokenizers, but PyTorch's raw API differs (C19). In causal LMs both masks combine; the docs do not state this combination in one sentence, so it is an inference from C15 + C18.

### C19. Be careful: the same word "mask" has opposite polarity in different APIs. In PyTorch scaled_dot_product_attention True means participate; in MultiheadAttention key_padding_mask True means ignore.

- **Source:** S17 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "In scaled_dot_product_attention(), True indicates values to participate in attention." — Note box under function signature
  - "In MultiheadAttention, True indicates values to be masked out (padding)." — same note
- **Caveats:** PyTorch 2.14 docs, accessed 2026-10-19. Good beginner gotcha, but may be too deep for the lesson.

### C20. When generating with a KV cache, the attention_mask must cover cached tokens plus the new one, so its width is past length + new tokens.

- **Source:** S13 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "The attention mask should have the shape (batch_size, past_kv_length + new_tokens_length)." — "How caching works", Cache class
- **Caveats:** Transformers library convention, v5.20.2, accessed 2026-10-19.

### C21. Multi-head attention splits the model width into h parallel heads; in the original Transformer base model h = 8 heads of 64 dimensions each, at about the same total cost as one full-width head.

- **Source:** S1 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "we employ h = 8 parallel attention layers, or heads. For each of these we use dk = dv = dmodel/h = 64" — §3.2.2 Multi-Head Attention
  - "the total computational cost is similar to that of single-head attention with full dimensionality" — §3.2.2
- **Caveats:** Original base model has d_model = 512 (stated in §3 / Table 3, not in this excerpt).

### C22. Heads let the model look at different kinds of information at once; a single head would average them together.

- **Source:** S1 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "Multi-head attention allows the model to jointly attend to information from different representation subspaces at different positions. With a single attention head, averaging inhibits this." — §3.2.2
- **Caveats:** This is the authors' motivation, not proof every head specialises (see C31).

### C23. BERT-base has 12 layers, hidden size 768 and 12 attention heads, i.e. 768/12 = 64 dimensions per head.

- **Source:** S3 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "BERTBASE (L=12, H=768, A=12, Total Param-" — §3 Model Architecture, p.3 (hyphenated line break in PDF)
  - "we set the feed-forward/filter size to be 4H" — footnote 3
- **Caveats:** The 64-per-head figure is derived (H/A), not printed in the BERT paper. Per-head width = hidden size / heads follows Vaswani C21. Paper v2 (arXiv).

### C24. bge-small-en-v1.5 is a BERT model with 12 layers, 12 attention heads and hidden size 384, so each head has 384/12 = 32 dimensions; it accepts up to 512 positions and uses absolute position embeddings.

- **Source:** S19 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - ""hidden_size": 384" — config.json @ 5c38ec7
  - ""num_attention_heads": 12" — config.json
  - ""num_hidden_layers": 12" — config.json
  - ""max_position_embeddings": 512" — config.json
  - ""position_embedding_type": "absolute"" — config.json
- **Caveats:** Pinned commit 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a (HF Hub lastModified 2024-02-22T03:36:23Z; accessed 2026-10-19; this was the repo head at access time). Head size 32 is derived (384/12). config also gives intermediate_size 1536 and model_type "bert". sentence_bert_config.json at same commit: max_seq_length 512.

### C25. Real models differ in head count and head width: GPT-3 Small has 12 heads of 64 dims; GPT-3 175B has 96 heads of 128 dims, with a 2048-token context window.

- **Source:** S9 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "GPT-3 Small 125M 12 768 12 64 0.5M 6.0× 10−4" — Table 2.1 (columns: nparams nlayers dmodel nheads dhead)
  - "GPT-3 175B or “GPT-3” 175.0B 96 12288 96 128 3.2M 0.6× 10−4" — Table 2.1
  - "nctx = 2048 tokens. We partition the model" — §2.1
- **Caveats:** arXiv v4 PDF (2020). Column order from the table header "Model Name nparams nlayers dmodel nheads dhead Batch Size Learning Rate". GPT-3 also alternates dense and locally banded sparse attention (C27). Context-window sizes are model- and date-specific (GPT-2: 1024, BERT: 512).

### C26. Context windows are fixed by design: GPT-2 doubled its window from 512 to 1024 tokens, GPT-3 used 2048, BERT-base 512 positions.

- **Source:** S10, S9, S19 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "We also increase the context size from 512 to 1024 tokens" — GPT-2 paper, §2.3 Model
  - ""max_position_embeddings": 512" — bge/BERT config
- **Caveats:** Historic values (2019-2020); modern models have far larger windows. GPT-2 paper is the OpenAI-hosted PDF (no arXiv version; undated). Pair with C25 for GPT-3.

### C27. Not every attention layer has to look at everything: GPT-3 alternates dense layers with locally banded sparse attention layers.

- **Source:** S9 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "we use alternating dense and locally banded sparse attention patterns in the layers of the transformer" — §2.1 Model and Architectures
- **Caveats:** Specific to GPT-3. Reduces the quadratic cost in some layers; details are in the Sparse Transformer paper cited there (not downloaded).

### C28. Attention itself has no sense of word order, so models add position information; the original Transformer added fixed sinusoidal vectors to the embeddings.

- **Source:** S1 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "we must inject some information about the relative or absolute position of the tokens in the sequence" — §3.5 Positional Encoding
  - "we use sine and cosine functions of different frequencies" — §3.5
- **Caveats:** Vaswani found learned positional embeddings gave nearly identical results (C29).

### C29. Learned absolute position embeddings (as in BERT) work about as well as sinusoids in the original paper; BERT sums token, segment and position embeddings.

- **Source:** S1, S3 (see register)
- **Type:** empirical  |  **Confidence:** Medium
- **Excerpts (verbatim):**
  - "found that the two versions produced nearly identical results" — §3.5 (Vaswani)
  - "constructed by summing the corresponding token, segment, and position embeddings" — §3 Input/Output Representations (BERT)
- **Caveats:** BERT paper does not use the word "learned" next to position embeddings in this sentence (it says "pre-train ... to learn the positional embeddings" in Appendix A.2, and the bge config says position_embedding_type "absolute"); that these are trainable lookup tables is standard but is stated most directly by Vaswani's "learned positional embeddings" comparison.

### C30. Rotary position embedding (RoPE) rotates query/key vectors by an angle that depends on position, so attention scores depend on relative distance between tokens.

- **Source:** S4 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "RoPE encodes the absolute position with a rotation matrix and meanwhile incorporates the explicit relative position dependency in self-attention formulation" — Abstract
  - "decaying inter-token dependency with increasing relative distances" — Abstract
- **Caveats:** RoFormer arXiv v5 (2023-11-09 stamp). Used in many modern LLMs but that adoption claim is not from this paper; do not cite adoption without another source.

### C31. Multi-query attention (MQA) shares one set of keys and values across all heads, shrinking the KV tensors and speeding up decoding at small quality cost.

- **Source:** S5 (see register)
- **Type:** empirical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "multi-query attention, where the keys and values are shared across all of the different attention "heads"" — Abstract
  - "greatly reducing the size of these tensors and hence the memory bandwidth requirements of incremental decoding" — Abstract
  - "incur only minor quality degradation from the baseline" — Abstract
- **Caveats:** arXiv v1 only (2019-11-06). Quality claim measured on translation / LM tasks of that era. Abstract text from arXiv abs page; PDF extract has spacing glitches.

### C32. Grouped-query attention (GQA) is a middle road: several query heads share each key/value head; one group equals MQA, one group per head equals normal multi-head attention.

- **Source:** S6 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "Grouped-query attention divides query heads into G groups, each of which shares a single key head and value head." — §2.2 Grouped-query attention
  - "GQA-1, with a single group and therefore single key and value head, is equivalent to MQA" — §2.2
  - "GQA-H, with groups equal to number of heads, is equivalent to MHA" — §2.2
- **Caveats:** arXiv v3. Note PDF line wraps break "GQA-1" across lines with spaces ("GQA -1"); semantics unaffected.

### C33. MQA/GQA shrink the KV cache and the data loaded per decoding step; going from multi-head to MQA cuts the cache by a factor equal to the number of heads.

- **Source:** S6 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "reducing the size of the key-value cache and therefore amount of data that needs to be loaded by a factor of H" — §2.2
  - "We show that uptrained GQA achieves quality close to multi-head attention with comparable speed to MQA" — Abstract
- **Caveats:** Excerpt 1 reads "going from MHA to MQA reduces H key and value heads to a single key and value head, reducing the size ..." (sentence spans line breaks). Quality statement is empirical on T5-family models (not downloaded in detail). GQA also says checkpoints can be uptrained with 5% of original pre-training compute (abstract).

### C34. In a real Hugging Face example, MQA cut the cache from about 15 GB to under 400 MB at 16,000 tokens; GQA with a few KV heads keeps most of the gain with less quality loss.

- **Source:** S15 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** Medium
- **Excerpts (verbatim):**
  - "we could therefore reduce the required memory consumption from 15 GB to less than 400 MB at an input sequence length of 16000" — §3.2.2 MQA
  - "almost all of the memory and speed gains from MQA can be kept while sacrificing less model capacity" — §3.2.3 GQA
- **Caveats:** Hugging Face tutorial (v5.20.2 build, accessed 2026-10-19), numbers specific to bigcode/octocoder; the "400 MB" is the tutorial's claim from its own arithmetic. The tutorial says GQA was "only recently proposed" and gives Llama-v2 as notable use: dated wording from ~2023.

### C35. The Transformer authors themselves said attention could make models more interpretable, but only showed example visualisations: some heads look related to sentence structure.

- **Source:** S1 (see register)
- **Type:** empirical  |  **Confidence:** Medium
- **Excerpts (verbatim):**
  - "self-attention could yield more interpretable models" — §4 Why Self-Attention
  - "many appear to exhibit behavior related to the syntactic and semantic structure of the sentences" — §4
- **Caveats:** Anecdotal inspection of chosen examples (Figs 3-5 in appendix), not a quantitative test; "many appear to" is hedged wording.

### C36. Attention weights are not guaranteed to be an explanation of why a model answered as it did: Jain and Wallace found they often do not line up with other importance measures and very different attention patterns can give the same prediction.

- **Source:** S7 (see register)
- **Type:** empirical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "learned attention weights are frequently uncorrelated with gradient-based measures of feature importance" — Abstract
  - "one can identify very different attention distributions that nonetheless yield equivalent predictions" — Abstract
  - "standard attention modules do not provide meaningful explanations and should not be treated as though they do" — Abstract
- **Caveats:** Experiments on BiLSTM models with an attention layer (and some simple models) for text classification/QA, NOT on today's Transformer self-attention. arXiv v3. Contested by S8 (C37).

### C37. Counter-view: whether attention "explains" a prediction depends on what you mean by explanation; the follow-up paper says Jain and Wallace did not disprove attention's usefulness.

- **Source:** S8 (see register)
- **Type:** empirical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "such a claim depends on one’s definition of explanation" — Abstract
  - "prior work does not disprove the usefulness of attention mechanisms for explainability" — Abstract
- **Caveats:** RNN-model focused; arXiv v2. CONFLICT with C36: the two papers disagree; neither establishes anything about causal use in modern Transformers. A safe teaching line: attention weights show where information was routed in one layer/head, not by themselves why the output was chosen.

### C38. Plausible vs faithful: an explanation can sound reasonable to humans without being an accurate account of what the model computed.

- **Source:** S8 (see register)
- **Type:** definition  |  **Confidence:** Medium
- **Excerpts (verbatim):**
  - "a plausible (but not necessarily faithful) reconstruction of the decision-making process" — §5 Defining Explanation
- **Caveats:** The sentence is Wiegreffe & Pinter's paraphrase of Rudin (2018) definition of explainability, not their own finding. Useful vocabulary.

### C39. Attention scores are divided by sqrt(d_k) because dot products of long vectors get large, which pushes softmax into regions where it barely learns.

- **Source:** S1 (see register)
- **Type:** empirical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "for large values of dk, the dot products grow large in magnitude, pushing the softmax function into regions where it has extremely small gradients" — §3.2.1 Scaled Dot-Product Attention (text before footnote mark 4)
- **Caveats:** The paper says "we suspect" and cites additive-vs-dot-product comparison [3]; it is a hypothesis with the footnote 4 variance argument (C40), not a direct experiment on gradients. Wording confirmed from PDF text: "...where it has extremely small gradients 4." (the 4 is the footnote marker; extraction renders the footnote number inline).

### C40. Why dot products grow: if query and key entries are independent with mean 0 and variance 1, their dot product has variance d_k, so typical magnitude grows like sqrt(d_k).

- **Source:** S1 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "assume that the components of q and k are independent random variables with mean 0 and variance 1" — Footnote 4, p.4
  - "has mean 0 and variance dk" — Footnote 4, p.4 (continues after dot-product sum)
- **Caveats:** Assumption-dependent (independent zero-mean unit-variance entries); real trained activations are not exactly this. Scaling by 1/sqrt(d_k) restores unit variance.

### C41. Softmax must be computed carefully to avoid overflow: the safe form subtracts the largest input from every input first; the result is mathematically identical.

- **Source:** S11 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "the line 3 of the algorithm 1 can overflow or underflow due to the exponent" — §2 Original softmax, p.2 (Milakov)
  - "There is a safe form of (1), which is immune to this problem" — §2
  - "All major DL frameworks are using this safe version for the Softmax computation" — §2
- **Caveats:** arXiv v2. The "all major DL frameworks" statement is as of the paper (2018) and lists TensorFlow etc.; not re-verified against framework source in 2026. Safe form = exp(x_i - max x) / sum exp(x_j - max x).

### C42. FlashAttention also uses this max-subtraction: "for numerical stability" it computes e^(x - max) and tracks the running max while processing blocks.

- **Source:** S2 (see register)
- **Type:** mathematical  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "For numerical stability, the softmax of vector" — §3.1 Tiling (arXiv HTML v2 shows m(x) := max x_i)
  - "the max-shifting step during softmax" — §B.1 Memory-efficient forward pass
- **Caveats:** Second excerpt is the FlashAttention appendix wording "we omit here the max-shifting step during softmax" (full algorithm in B.3 includes it). Verified against arXiv HTML v2 (math symbols render with spaces).

### C43. Softmax outputs are non-negative numbers between 0 and 1 that sum to 1 along the chosen dimension.

- **Source:** S18 (see register)
- **Type:** definition  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "will re-scale them so that the elements lie in the range [0, 1] and sum to 1" — torch.nn.functional.softmax docs
- **Caveats:** PyTorch 2.14, accessed 2026-10-19.

### C44. PyTorch warns that for numerical safety you can pass a dtype to softmax to avoid overflow, and prefers log_softmax for better numerical properties with NLLLoss.

- **Source:** S18 (see register)
- **Type:** provider- or model-specific  |  **Confidence:** High
- **Excerpts (verbatim):**
  - "This is useful for preventing data type overflows." — softmax Parameters, dtype
  - "Use log_softmax instead (it’s faster and has better numerical properties)." — softmax Note
- **Caveats:** PyTorch-specific API advice; PyTorch 2.14 docs, accessed 2026-10-19. Marginal for the lesson.

### C45. When one score is much larger than the others, softmax puts nearly all weight on that one position (close to one-hot) and gradients vanish. DERIVED, not stated verbatim by a primary source.

- **Source:** S1, S18 (see register)
- **Type:** mathematical  |  **Confidence:** Medium (derived)
- **Excerpts (verbatim):**
  - "pushing the softmax function into regions where it has extremely small gradients" — §3.2.1
  - "will re-scale them so that the elements lie in the range [0, 1] and sum to 1" — torch.nn.functional.softmax docs
- **Caveats:** No downloaded primary source uses the phrase "one-hot" or "saturate" for softmax. Vaswani gives only the small-gradient consequence; "nearly one-hot" follows from exp(a)/(exp(a)+exp(b)) -> 1 as a-b grows (elementary maths; demonstrate with a toy computation in the lesson rather than citing). Flag as derived in script notes.
