# Embedding Foundations: from word2vec to bge-small-en-v1.5 (Pass 1, primary sources)

Access date for every source: 2026-10-19. Method: raw files were downloaded with curl (HF `raw/main` files, the HF model API, GitHub raw files, arXiv `export.arxiv.org/abs` pages, and ar5iv full-text HTML), then searched for exact strings. I copied excerpts out of the downloaded text myself, not from an LLM summary. Whitespace is normalized and LaTeX symbols that ar5iv drops are shown as "...". Excerpts are 25 words or fewer.

Versions read:
- arXiv abstract pages: the latest version listed in each submission history. 1301.3781 v3 (7 Sep 2013); 1310.4546 v1 (16 Oct 2013); 1810.04805 v2 (24 May 2019); 1909.00512 v1 (2 Sep 2019); 1908.10084 v1 (27 Aug 2019); 2309.07597 v5 (24 Sep 2024); 2104.08821 v4 (18 May 2022).
- Full text: read from ar5iv (`https://ar5iv.labs.arxiv.org/html/<id>`). ar5iv does not print which version it rendered. **Caveat:** for 2309.07597, the ar5iv text says "training methods for BGE", but the v5 abstract says "C-TEM". So ar5iv is showing an earlier version (somewhere in v1 to v4), not v5. Pass 2 should check C-Pack quotes against the v5 PDF (https://arxiv.org/pdf/2309.07597v5).
- BAAI/bge-small-en-v1.5 on Hugging Face: repo commit `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, lastModified 2024-02-22, created 2023-09-12 (from https://huggingface.co/api/models/BAAI/bge-small-en-v1.5).
- Qdrant/bge-small-en-v1.5-onnx-Q: commit `aa8f8b060edb00e03bfdd08813a2949946c8ba55`, lastModified 2026-09-24, created 2024-01-15.
- qdrant/fastembed: `main` at commit `de502ca83baa2b81922cb5a46acf689f5e2c72a1` (2026-10-15). Latest release tag is v0.9.0 (2026-10-07).

## Q1. Distributional idea and static word embeddings (word2vec)

### Takeaway
Mikolov et al. learn one dense vector per word. They show that similar words land close together and that relationships between words show up as vector offsets (King − Man + Woman ≈ Queen). Their own follow-up paper names the limits: word vectors ignore word order and cannot represent idiomatic phrases. Later work (Ethayarajh 2019) states the one-vector-per-word-type limit explicitly.

### Cited Findings
- The paper proposes architectures "for computing continuous vector representations of words from very large data sets" (abstract, v3). — [Mikolov et al. 2013a, arXiv 1301.3781](https://arxiv.org/abs/1301.3781)
- Training is cheap: "less than a day to learn high quality word vectors from a 1.6 billion words data set" (abstract). — [arXiv 1301.3781](https://arxiv.org/abs/1301.3781)
- On similarity, the authors expect "not only will similar words tend to be close to each other, but that words can have multiple degrees of similarity" (Sec. 1.1). — [ar5iv 1301.3781](https://ar5iv.labs.arxiv.org/html/1301.3781)
- On analogies: "vector("King") - vector("Man") + vector("Woman") results in a vector that is closest to the vector representation of the word Queen" (Sec. 1.1). The paper cites earlier work [20] for this finding. — [ar5iv 1301.3781](https://ar5iv.labs.arxiv.org/html/1301.3781)
- The paper's dimensionality for prior work: "a modest dimensionality of the word vectors between 50 - 100" (Sec. 1.1). — [ar5iv 1301.3781](https://ar5iv.labs.arxiv.org/html/1301.3781)
- Skip-gram vectors "capture a large number of precise syntactic and semantic word relationships" (abstract). — [Mikolov et al. 2013b, arXiv 1310.4546](https://arxiv.org/abs/1310.4546)
- A second analogy example: "vec("Madrid") - vec("Spain") + vec("France") is closer to vec("Paris") than to any other word vector" (Sec. 1). — [ar5iv 1310.4546](https://ar5iv.labs.arxiv.org/html/1310.4546)
- Stated limit: "An inherent limitation of word representations is their indifference to word order and their inability to represent idiomatic phrases" (abstract). The example given is "Air Canada". — [arXiv 1310.4546](https://arxiv.org/abs/1310.4546)
- The same paper introduces "negative sampling" as "a simple alternative to the hierarchical softmax" (abstract). This idea comes back in contrastive training. — [arXiv 1310.4546](https://arxiv.org/abs/1310.4546)
- One vector per word type: "these word embeddings were static: each word had a single vector, regardless of context". As a result, "all senses of a polysemous word had to share the same representation." — [Ethayarajh 2019, ar5iv 1909.00512](https://ar5iv.labs.arxiv.org/html/1909.00512)

### Inferences
- The word2vec papers themselves never use the phrase "one vector per word type". That framing comes from later work such as Ethayarajh 2019. A lesson should attribute it correctly.
- The papers do not cite or name the "distributional hypothesis" (Harris/Firth) in the passages I checked. Any lesson text that mentions it needs its own source.

### Gaps
- I did not search the full text for any explicit mention of the "distributional hypothesis". It is not in either abstract.

## Q2. Contextual embeddings: BERT [CLS], WordPiece, and anisotropy

### Takeaway
BERT uses a 30,000-token WordPiece vocabulary. The final hidden state of its [CLS] token is the "aggregate sequence representation for classification tasks". The paper itself warns that this vector is not a meaningful sentence representation unless the model is fine-tuned. Ethayarajh (2019) finds that contextual representations are anisotropic (they sit in a narrow cone) and become more context-specific in upper layers.

### Cited Findings
- The vocabulary: "We use WordPiece embeddings (Wu et al. 2016) with a 30,000 token vocabulary" (Sec. 3, Input/Output Representations). — [Devlin et al., ar5iv 1810.04805](https://ar5iv.labs.arxiv.org/html/1810.04805)
- The [CLS] token: "The final hidden state corresponding to this token is used as the aggregate sequence representation for classification tasks" (Sec. 3). — [ar5iv 1810.04805](https://ar5iv.labs.arxiv.org/html/1810.04805)
- The warning: "The vector C is not a meaningful sentence representation without fine-tuning, since it was trained with NSP" (footnote in Sec. 3.1). — [ar5iv 1810.04805](https://ar5iv.labs.arxiv.org/html/1810.04805)
- Model card config check: bge-small-en-v1.5's `config.json` has `"vocab_size": 30522` and `"model_type": "bert"`. The paper rounds this to "30,000"; the exact count in the file is 30,522. — [BAAI config.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/config.json)
- BERT conditions "on both left and right context in all layers" (abstract, v2). — [arXiv 1810.04805](https://arxiv.org/abs/1810.04805)
- Anisotropy: the representations "are not isotropic in any layer" (abstract). They are "anisotropic, occupying a narrow cone in the vector space" (Sec. 1, finding 1). — [Ethayarajh, arXiv 1909.00512](https://arxiv.org/abs/1909.00512) / [ar5iv](https://ar5iv.labs.arxiv.org/html/1909.00512)
- How extreme it gets: "The anisotropy in GPT-2's last layer is so extreme that two random words will on average have almost perfect cosine similarity!" — [ar5iv 1909.00512](https://ar5iv.labs.arxiv.org/html/1909.00512)
- Context-specificity: "this self-similarity is much lower in upper layers," suggesting "upper layers of contextualizing models produce more context-specific representations" (abstract). — [arXiv 1909.00512](https://arxiv.org/abs/1909.00512)
- Static embeddings explain little: "on average, less than 5% of the variance in a word's contextualized representations can be explained by a static embedding" (abstract). — [arXiv 1909.00512](https://arxiv.org/abs/1909.00512)

### Inferences
- Anisotropy explains why raw BERT-style vectors give high cosine scores even for unrelated inputs. It also helps explain why contrastive fine-tuning (SimCSE, BGE) is needed. SimCSE makes this link itself (see Q6).

### Gaps
- Ethayarajh studies ELMo, BERT and GPT-2, not BGE. Whether the narrow-cone finding applies to bge-small is my inference, not something the paper tests.

## Q3. Sentence embeddings and pooling (SBERT)

### Takeaway
SBERT compares three pooling strategies (CLS, MEAN, MAX) and uses MEAN by default. With NLI training, pooling made little difference: MEAN 80.78 vs CLS 79.80 vs MAX 79.07. Without fine-tuning, BERT CLS (29.19) and averaged BERT outputs (54.81) did worse than averaged GloVe on STS. The paper concludes that out-of-the-box BERT sentence vectors are "rather unsuitable" for cosine similarity.

### Cited Findings
- How pooling works: "SBERT adds a pooling operation to the output of BERT / RoBERTa to derive a fixed sized sentence embedding" (Sec. 3). — [Reimers & Gurevych, ar5iv 1908.10084](https://ar5iv.labs.arxiv.org/html/1908.10084)
- The three strategies: "Using the output of the CLS-token, computing the mean of all output vectors (MEAN-strategy), and computing a max-over-time..." (Sec. 3). — [ar5iv 1908.10084](https://ar5iv.labs.arxiv.org/html/1908.10084)
- The default: "Our default pooling strategy is MEAN" (Sec. 3, Training Details). — [ar5iv 1908.10084](https://ar5iv.labs.arxiv.org/html/1908.10084)
- Table 6 (dev set of STSb, Spearman). Trained on NLI: MEAN 80.78, MAX 79.07, CLS 79.80. Trained on STSb with regression: MEAN 87.44, MAX 69.92, CLS 86.62. The paper adds that with NLI training "the pooling strategy has a rather minor impact." — [ar5iv 1908.10084](https://ar5iv.labs.arxiv.org/html/1908.10084)
- Raw BERT is weak: "Averaging the BERT embeddings achieves an average correlation of only 54.81, and using the CLS-token output only achieves an average correlation of 29.19." The paper says both are "worse than computing average GloVe embeddings" (Sec. 4.1). — [ar5iv 1908.10084](https://ar5iv.labs.arxiv.org/html/1908.10084)
- The conclusion: "BERT out-of-the-box maps sentences to a vector space that is rather unsuitable to be used with common similarity measures like cosine-similarity" (Sec. 8). — [ar5iv 1908.10084](https://ar5iv.labs.arxiv.org/html/1908.10084)
- Why bi-encoders: finding the most similar pair among 10,000 sentences with BERT cross-encoding "requires about 50 million inference computations (~65 hours)". SBERT does it in "about 5 seconds" (abstract). — [arXiv 1908.10084](https://arxiv.org/abs/1908.10084)
- A nuance: on SentEval, "average BERT embeddings and the BERT CLS-token output achieves decent results". So raw BERT is poor mainly for similarity with cosine, not for every task. — [ar5iv 1908.10084](https://ar5iv.labs.arxiv.org/html/1908.10084)

### Inferences
- The SBERT result does not say "MEAN beats CLS in general". It says pooling matters little once the model is fine-tuned. That fits with BGE choosing CLS pooling and still performing strongly, because BGE is contrastively fine-tuned (Q4).

### Gaps
- None for the questions asked.

## Q4. BGE: C-Pack paper and the bge-small-en-v1.5 model card

### Takeaway
The model files show that bge-small-en-v1.5 is a 12-layer BERT. It outputs 384 dimensions, accepts at most 512 tokens, uses CLS pooling, and L2-normalizes its outputs. With normalized vectors, the dot product used in the card's examples equals cosine similarity. For short-query-to-passage retrieval, the card suggests adding "Represent this sentence for searching relevant passages: " to queries only, never to passages. v1.5 "alleviate[s] the issue of the similarity distribution" and retrieves better without the instruction. Training is RetroMAE pre-training followed by contrastive learning on large-scale pairs, with temperature 0.01 per the card.

### Cited Findings
**Dimension and sequence length**
- `config.json`: `"hidden_size": 384`, `"num_hidden_layers": 12`, `"num_attention_heads": 12`, `"max_position_embeddings": 512`. — [config.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/config.json)
- `sentence_bert_config.json`: `"max_seq_length": 512, "do_lower_case": true`. — [sentence_bert_config.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/sentence_bert_config.json)
- The model card's MTEB table row: "BAAI/bge-small-en-v1.5 | 384 | 512 | 62.17" (columns are Dimension, Sequence Length, Average of 56 tasks). — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)

**Pooling and normalization**
- `1_Pooling/config.json`: `"pooling_mode_cls_token": true, "pooling_mode_mean_tokens": false`. — [1_Pooling/config.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/1_Pooling/config.json)
- `modules.json` lists three modules in order: Transformer, then Pooling, then `sentence_transformers.models.Normalize` (path `2_Normalize`). — [modules.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/modules.json)
- The card text: "select the last hidden state of the first token (i.e., [CLS]) as the sentence embedding". — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- The card's code: "# Perform pooling. In this case, cls pooling." then `model_output[0][:, 0]`, then `torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)`. — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- Similarity: the examples use `normalize_embeddings=True` and score with `embeddings_1 @ embeddings_2.T`. The LangChain example comments "set True to compute cosine similarity". — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)

**Query instruction**
- The model list gives the bge-small-en-v1.5 instruction as `Represent this sentence for searching relevant passages: ` (note the trailing space). — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- Footnote [1]: "If you need to search the relevant passages to a query, we suggest to add the instruction to the query". Also: "In all cases, **no instruction** needs to be added to passages." — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- FAQ 3, specific to v1.5: "No instruction only has a slight degradation in retrieval performance compared with using instruction." The card recommends instructions for "short queries" and says to choose "the setting that achieves better performance on your task." — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- The paper on instruction tuning: "a task specific instruction is attached to the query side". Its example prompt is "search relevant passages for the query" (Sec. 3, task-specific fine-tuning). — [C-Pack, ar5iv 2309.07597](https://ar5iv.labs.arxiv.org/html/2309.07597)

**What v1.5 changed**
- The news entry: release "`bge-*-v1.5` embedding model to alleviate the issue of the similarity distribution, and enhance its retrieval ability without instruction." — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- The model-list description: "version 1.5 with more reasonable similarity distribution". — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- FAQ 2, on the similarity distribution: "Since we finetune the models by contrastive learning with a temperature of 0.01, the similarity distribution of the current BGE model is about in the interval [0.6, 1]." — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- FAQ 2 continues: "a similarity score greater than 0.5 does not indicate that the two sentences are similar". What matters is "the relative order of the scores, not the absolute value". It suggests thresholds such as 0.8, 0.85 or 0.9, tuned on your own data. — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- **Ambiguity to flag:** the [0.6, 1] statement describes "the current BGE model" and appears right after the advice to use v1.5. The card does not say clearly whether [0.6, 1] still applies to v1.5 or only to v1. Treat it as a v1 characteristic that v1.5 "alleviates". Do not present it as a measured v1.5 range.
- The card gives no detailed changelog of how v1.5 was retrained (data, hyperparameters).

**Training approach**
- The card's Train section: "We pre-train the models using retromae and train them on large-scale pairs data using contrastive learning." — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- The card also says "the pre-trained model cannot be used for similarity calculation directly, it needs to be fine-tuned." — [model card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- The paper's general-purpose stage: the model "is learned to discriminate the paired texts from their negative samples". It relies on "in-batch negative samples" with batch sizes "as large as 19,200". — [C-Pack, ar5iv 2309.07597](https://ar5iv.labs.arxiv.org/html/2309.07597)
- The paper's task-specific stage: "in addition to the in-batch negative samples, one hard negative sample is mined for each text pair". — [ar5iv 2309.07597](https://ar5iv.labs.arxiv.org/html/2309.07597)
- Architecture and English data: the models "are based on the BERT-like architecture". The English training set "consists of 200M text pairs". — [ar5iv 2309.07597](https://ar5iv.labs.arxiv.org/html/2309.07597)
- The paper's abstract (v5): "The English models achieve state-of-the-art performance on MTEB benchmark". This is dated to the time of release. — [arXiv 2309.07597](https://arxiv.org/abs/2309.07597)

### Inferences
- Unit-length vectors make the dot product the same as cosine similarity. The card shows this through its examples and the LangChain comment, but does not state it as a rule.
- The C-Pack paper gives small/base/large as 24M/102M/326M parameters, but in the context of the **Chinese** models. The English bge-small-en-v1.5 `model.safetensors` is 133,466,304 bytes, which at fp32 (4 bytes per parameter) is about 33M parameters. Do not quote "24M" for the English small model. The 33M figure is my calculation, not a stated fact.
- The C-Pack paper (in the version I read) does not mention CLS pooling or v1.5. Those facts come only from the model card and repo config files.

### Gaps
- I did not fetch the FlagEmbedding GitHub README separately. The HF card contains the same model list and FAQ. The card's links point to github.com/FlagOpen/FlagEmbedding, which may have newer text.
- I could not confirm from a primary source whether the v1.5 similarity distribution is still roughly [0.6, 1].
- The ar5iv rendering of C-Pack predates v5, so section wording may differ in v5.

## Q5. Qdrant/bge-small-en-v1.5-onnx-Q and fastembed

### Takeaway
fastembed's `BAAI/bge-small-en-v1.5` entry actually downloads `Qdrant/bge-small-en-v1.5-onnx-Q` and loads `model_optimized.onnx`. The model card calls it a "Quantized ONNX port". However, the repo's `ort_config.json` shows an empty `quantization` block with `fp16: true` and optimization level 2. Its file size (66.5 MB) is about half of BAAI's fp32 ONNX file (133.1 MB). So "quantized" here most likely means an fp16, graph-optimized export, not int8; this needs Pass-2 confirmation. fastembed copies the original pipeline: it takes the CLS token (`[:, 0]`) and then normalizes. Its default `query_embed` adds **no** BGE instruction prefix.

### Cited Findings
- The model card in full: "Quantized ONNX port of BAAI/bge-small-en-v1.5 for text classification and similarity searches." (license MIT, pipeline_tag sentence-similarity). — [Qdrant model card](https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q)
- `ort_config.json` (optimum 1.15.0): `"quantization": {}`, `"fp16": true`, `"optimization_level": 2`, `"optimize_for_gpu": true`, `"enable_gelu_approximation": true`. — [ort_config.json](https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q/blob/main/ort_config.json)
- File sizes from the HF tree API: Qdrant `model_optimized.onnx` = 66,465,124 bytes; BAAI `onnx/model.onnx` = 133,093,490 bytes. — [Qdrant tree](https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q/tree/main), [BAAI onnx tree](https://huggingface.co/BAAI/bge-small-en-v1.5/tree/main/onnx)
- fastembed's registry entry: `model="BAAI/bge-small-en-v1.5", dim=384`, `sources=ModelSource(hf="Qdrant/bge-small-en-v1.5-onnx-Q")`, `model_file="model_optimized.onnx"`, `size_in_GB=0.067`. — [fastembed onnx_embedding.py @ main de502ca](https://github.com/qdrant/fastembed/blob/main/fastembed/text/onnx_embedding.py)
- The entry's description: "Text embeddings, Unimodal (text), English, 512 input tokens truncation, Prefixes for queries/documents: not so necessary, 2023 year." — [onnx_embedding.py](https://github.com/qdrant/fastembed/blob/main/fastembed/text/onnx_embedding.py)
- Post-processing: for 3-D output, `processed_embeddings = embeddings[:, 0]` then `return normalize(processed_embeddings)`. — [onnx_embedding.py](https://github.com/qdrant/fastembed/blob/main/fastembed/text/onnx_embedding.py)
- `query_embed` in the base class just calls `self.embed(...)` with the comment "This is model-specific, so that different models can have specialized implementations". `OnnxTextEmbedding` does not override it, so no instruction is prepended. — [text_embedding_base.py](https://github.com/qdrant/fastembed/blob/main/fastembed/text/text_embedding_base.py)
- The README says the default model "supports "query" and "passage" prefixes for the input text". It shows `TextEmbedding(model_name="BAAI/bge-small-en-v1.5")` and "Vector of 384 dimensions". It also says fastembed uses "the ONNX Runtime" instead of PyTorch. — [fastembed README](https://github.com/qdrant/fastembed)

### Inferences
- When fastembed users ask for "BAAI/bge-small-en-v1.5", they get Qdrant's fp16-optimized ONNX export, not BAAI's own weights file. Output vectors should be close to the original but may differ slightly. No source I found quantifies the difference.
- To use the BGE retrieval instruction with fastembed, you must prepend it to queries yourself. The README's mention of "query"/"passage" prefixes does not match the code for this model (they look like E5-style prefixes). Flag this for Pass 2.

### Gaps
- No Qdrant source explains what "Quantized" means for this repo, or gives accuracy deltas against the original. The card is 900 bytes long.
- The Qdrant repo was modified on 2026-09-24. I did not check which files changed.
- I did not fetch the fastembed docs site (qdrant.github.io/fastembed); I used the code and README only.

## Q6. Contrastive training in general (SimCSE)

### Takeaway
SimCSE defines contrastive learning as pulling semantically close neighbours together and pushing non-neighbours apart. It uses a cross-entropy objective with in-batch negatives, a temperature τ, and cosine similarity. It also shows that this objective spreads out the anisotropic space of pre-trained embeddings. BGE's training (Q4) follows the same recipe at much larger scale.

### Cited Findings
- The definition: "Contrastive learning aims to learn effective representation by pulling semantically close neighbors together and pushing apart non-neighbors (Hadsell et al., 2006)" (Sec. 2). — [Gao et al., ar5iv 2104.08821](https://ar5iv.labs.arxiv.org/html/2104.08821)
- The objective: "take a cross-entropy objective with in-batch negatives". In the equation, τ "is a temperature hyperparameter" and sim is "the cosine similarity" (Sec. 2). — [ar5iv 2104.08821](https://ar5iv.labs.arxiv.org/html/2104.08821)
- Unsupervised SimCSE "takes an input sentence and predicts itself in a contrastive objective, with only standard dropout used as noise" (abstract, v4). — [arXiv 2104.08821](https://arxiv.org/abs/2104.08821)
- Supervised SimCSE uses "'entailment' pairs as positives and 'contradiction' pairs as hard negatives" (abstract). — [arXiv 2104.08821](https://arxiv.org/abs/2104.08821)
- The link to anisotropy: the objective "regularizes pre-trained embeddings' anisotropic space to be more uniform" (abstract). — [arXiv 2104.08821](https://arxiv.org/abs/2104.08821)
- Results: BERT-base reaches "76.3% and 81.6% Spearman's correlation" (unsupervised and supervised) on STS (abstract). — [arXiv 2104.08821](https://arxiv.org/abs/2104.08821)

### Inferences
- A very low temperature (BGE uses 0.01 per its card) sharpens the softmax over negatives. That plausibly connects to BGE v1's compressed similarity range (roughly [0.6, 1]), and BGE's card links the two causally. Exactly how this works is not explained in either source.

### Gaps
- None for the questions asked.

---

## Claims table

| # | Claim | Source URL | Excerpt (≤25 words) | Confidence |
|---|---|---|---|---|
| 1 | word2vec learns continuous word vectors from large data | https://arxiv.org/abs/1301.3781 (v3) | "computing continuous vector representations of words from very large data sets" | high |
| 2 | Similar words are close; words have multiple degrees of similarity | https://ar5iv.labs.arxiv.org/html/1301.3781 | "not only will similar words tend to be close to each other, but that words can have multiple degrees of similarity" | high |
| 3 | King − Man + Woman ≈ Queen (offset arithmetic) | https://ar5iv.labs.arxiv.org/html/1301.3781 | "results in a vector that is closest to the vector representation of the word Queen" | high |
| 4 | Skip-gram vectors capture syntactic and semantic relationships | https://arxiv.org/abs/1310.4546 (v1) | "capture a large number of precise syntactic and semantic word relationships" | high |
| 5 | Word vectors ignore word order and idioms | https://arxiv.org/abs/1310.4546 | "their indifference to word order and their inability to represent idiomatic phrases" | high |
| 6 | Static embeddings: one vector per word, all senses shared | https://ar5iv.labs.arxiv.org/html/1909.00512 | "each word had a single vector, regardless of context" | high |
| 7 | BERT uses a 30,000-token WordPiece vocabulary | https://ar5iv.labs.arxiv.org/html/1810.04805 | "We use WordPiece embeddings (Wu et al. 2016) with a 30,000 token vocabulary" | high |
| 8 | Exact vocab size in bge-small config is 30,522 | https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/config.json | "vocab_size": 30522 | high |
| 9 | [CLS] final state is the aggregate sequence representation | https://ar5iv.labs.arxiv.org/html/1810.04805 | "used as the aggregate sequence representation for classification tasks" | high |
| 10 | Raw BERT CLS is not a meaningful sentence vector without fine-tuning | https://ar5iv.labs.arxiv.org/html/1810.04805 | "not a meaningful sentence representation without fine-tuning, since it was trained with NSP" | high |
| 11 | Contextual representations are anisotropic (narrow cone) | https://ar5iv.labs.arxiv.org/html/1909.00512 | "anisotropic, occupying a narrow cone in the vector space" | high |
| 12 | Upper layers are more context-specific | https://arxiv.org/abs/1909.00512 (v1) | "upper layers of contextualizing models produce more context-specific representations" | high |
| 13 | A static embedding explains <5% of contextual variance | https://arxiv.org/abs/1909.00512 | "less than 5% of the variance in a word's contextualized representations can be explained by a static embedding" | high |
| 14 | SBERT compares CLS, MEAN, MAX pooling | https://ar5iv.labs.arxiv.org/html/1908.10084 | "Using the output of the CLS-token, computing the mean of all output vectors (MEAN-strategy), and computing a max-over-time" | high |
| 15 | SBERT default pooling is MEAN | https://ar5iv.labs.arxiv.org/html/1908.10084 | "Our default pooling strategy is MEAN" | high |
| 16 | With NLI training, pooling has minor impact (MEAN 80.78 / CLS 79.80 / MAX 79.07) | https://ar5iv.labs.arxiv.org/html/1908.10084 | "the pooling strategy has a rather minor impact" | high |
| 17 | Raw BERT avg 54.81, CLS 29.19, both below avg GloVe on STS | https://ar5iv.labs.arxiv.org/html/1908.10084 | "Averaging the BERT embeddings achieves an average correlation of only 54.81, and using the CLS-token output only achieves an average correlation of 29.19" | high |
| 18 | Out-of-the-box BERT is unsuitable for cosine similarity | https://ar5iv.labs.arxiv.org/html/1908.10084 | "rather unsuitable to be used with common similarity measures like cosine-similarity" | high |
| 19 | bge-small-en-v1.5 is 384-dim, 12 layers | https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/config.json (commit 5c38ec7) | "hidden_size": 384 ... "num_hidden_layers": 12 | high |
| 20 | Max sequence length 512 | https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/sentence_bert_config.json | "max_seq_length": 512 | high |
| 21 | Uses CLS pooling | https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/1_Pooling/config.json | "pooling_mode_cls_token": true, "pooling_mode_mean_tokens": false | high |
| 22 | Embeddings are L2-normalized (Normalize module) | https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/modules.json | "type": "sentence_transformers.models.Normalize" | high |
| 23 | Normalized + dot product = cosine similarity (recommended scoring) | https://huggingface.co/BAAI/bge-small-en-v1.5 | "encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity" | medium (shown in examples, not stated as a rule) |
| 24 | Retrieval query instruction string | https://huggingface.co/BAAI/bge-small-en-v1.5 | "Represent this sentence for searching relevant passages: " | high |
| 25 | Instruction goes on queries only, never passages | https://huggingface.co/BAAI/bge-small-en-v1.5 | "In all cases, **no instruction** needs to be added to passages." | high |
| 26 | v1.5 works well without instruction; use it for short queries | https://huggingface.co/BAAI/bge-small-en-v1.5 | "No instruction only has a slight degradation in retrieval performance compared with using instruction." | high |
| 27 | v1.5 alleviates similarity distribution, improves no-instruction retrieval | https://huggingface.co/BAAI/bge-small-en-v1.5 | "alleviate the issue of the similarity distribution, and enhance its retrieval ability without instruction" | high |
| 28 | Temperature 0.01 → similarity roughly in [0.6, 1] | https://huggingface.co/BAAI/bge-small-en-v1.5 | "contrastive learning with a temperature of 0.01, the similarity distribution of the current BGE model is about in the interval [0.6, 1]" | medium (unclear whether it applies to v1.5) |
| 29 | Relative order of scores matters, not absolute value | https://huggingface.co/BAAI/bge-small-en-v1.5 | "what matters is the relative order of the scores, not the absolute value." | high |
| 30 | Training: RetroMAE pre-training + contrastive learning on pairs | https://huggingface.co/BAAI/bge-small-en-v1.5 | "We pre-train the models using retromae and train them on large-scale pairs data using contrastive learning." | high |
| 31 | C-Pack uses in-batch negatives with batch up to 19,200 | https://ar5iv.labs.arxiv.org/html/2309.07597 (pre-v5 render) | "we purely rely on in-batch negative samples ... and resort to a big batch size (as large as 19,200)" | medium (verify against v5) |
| 32 | Task-specific stage adds instruction on query side + one hard negative | https://ar5iv.labs.arxiv.org/html/2309.07597 | "in addition to the in-batch negative samples, one hard negative sample is mined for each text pair" | medium (verify against v5) |
| 33 | English training data is 200M text pairs | https://ar5iv.labs.arxiv.org/html/2309.07597 | "which consists of 200M text pairs" | medium (verify against v5) |
| 34 | Qdrant repo is described as a quantized ONNX port of BGE-small | https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q (commit aa8f8b0) | "Quantized ONNX port of BAAI/bge-small-en-v1.5 for text classification and similarity searches." | high (that the card says it) |
| 35 | That "quantization" is actually fp16 + ORT optimization, not int8 | https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q/blob/main/ort_config.json | "quantization": {} ... "fp16": true ... "optimization_level": 2 | medium (inferred from config and size) |
| 36 | fastembed's bge-small entry loads the Qdrant ONNX file | https://github.com/qdrant/fastembed/blob/main/fastembed/text/onnx_embedding.py (main de502ca) | sources=ModelSource(hf="Qdrant/bge-small-en-v1.5-onnx-Q"), model_file="model_optimized.onnx" | high |
| 37 | fastembed does CLS pooling + normalization | https://github.com/qdrant/fastembed/blob/main/fastembed/text/onnx_embedding.py | processed_embeddings = embeddings[:, 0] ... return normalize(processed_embeddings) | high |
| 38 | fastembed query_embed adds no BGE instruction prefix | https://github.com/qdrant/fastembed/blob/main/fastembed/text/text_embedding_base.py | "This is model-specific, so that different models can have specialized implementations" (then calls self.embed) | medium-high (code at one commit) |
| 39 | fastembed describes prefixes as not very necessary for bge-small | https://github.com/qdrant/fastembed/blob/main/fastembed/text/onnx_embedding.py | "Prefixes for queries/documents: not so necessary, 2023 year." | high |
| 40 | Contrastive learning pulls neighbours together, pushes non-neighbours apart | https://ar5iv.labs.arxiv.org/html/2104.08821 | "pulling semantically close neighbors together and pushing apart non-neighbors" | high |
| 41 | SimCSE objective: cross-entropy, in-batch negatives, temperature, cosine | https://ar5iv.labs.arxiv.org/html/2104.08821 | "take a cross-entropy objective with in-batch negatives" | high |
| 42 | Contrastive objective makes anisotropic space more uniform | https://arxiv.org/abs/2104.08821 (v4) | "regularizes pre-trained embeddings' anisotropic space to be more uniform" | high |
| 43 | English bge-small is ~33M params (not the paper's 24M Chinese small) | https://huggingface.co/BAAI/bge-small-en-v1.5/tree/main | model.safetensors 133,466,304 bytes (fp32 → ~33M) | low (derived, not stated) |
