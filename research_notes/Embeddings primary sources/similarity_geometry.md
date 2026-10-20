# Geometry of Embedding Spaces: Similarity, Normalization, Dimensionality, Visualization

Pass 1 (primary-source research). Access date for every source: **2026-10-19** unless noted. Excerpts are verbatim, 25 words or fewer. "[MATH]" marks a mathematical fact anyone can derive; "[EMPIRICAL]" marks a finding that depends on the model and data.

Method note: the arXiv abstract pages, the Stanford IR book, the FAISS wiki, the sbert.net docs, the HF model card and distill.pub were fetched with WebFetch. Its summarizer returns quoted strings, which I treat as verbatim but which still need checking in Pass 2. The t-SNE paper (JMLR PDF) and Ethayarajh 2019 (arXiv PDF v1) were downloaded, and their text was extracted locally with macOS PDFKit. The excerpts quoted from those two are exact text from the extraction. The OpenAI guide was fetched today; an extracted Markdown copy of the same URL from 2026-10-18 was used for exact wording and matches today's fetch. **The OpenAI blog post `openai.com/index/new-embedding-models-and-api-updates/` returned HTTP 403 and was NOT read**. Its claims appear here only as restated in the OpenAI guide.

## Cosine similarity, dot product and Euclidean distance

### Takeaway
[MATH] Cosine similarity is the dot product of the length-normalized vectors. For unit vectors, ||x − y||² = 2 − 2·cos(x, y), so cosine, dot product and (squared) L2 distance give identical rankings. Without normalization, the dot product depends on vector length, and the cosine denominator exists to cancel that effect.

### Cited Findings
- Cosine similarity is the standard document-similarity measure in the vector space model. Its numerator is the dot (inner) product and its denominator is the product of the Euclidean lengths. Excerpt: "the standard way of quantifying the similarity between two documents" — [Manning, Raghavan & Schütze, *Introduction to Information Retrieval*, §6.3.1 "Dot products"](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html) (Cambridge UP © 2008; HTML edition page dated 2009-04-07)
- The cosine denominator length-normalizes the vectors. Excerpt: "The effect of the denominator of Equation 24 is thus to length-normalize the vectors" — [IR book §6.3.1](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html)
- [MATH] Cosine is the dot product of the normalized vectors. Excerpt: "(25) can be viewed as the dot product of the normalized versions of the two document vectors" — [IR book §6.3.1](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html)
- Length breaks raw difference-based similarity. Excerpt: "two documents with very similar content can have a significant vector difference" (when one document is much longer) — [IR book §6.3.1](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html)
- FAISS METRIC_L2 returns *squared* Euclidean distance. Excerpt: "reports squared Euclidean (L2) distance, avoiding the square root" — [FAISS wiki, "MetricType and distances"](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances) (last edited 2024-12-03 by mengdilin, 16 revisions)
- Inner product is not cosine unless the vectors are normalized. Excerpt: "This is not by itself cosine similarity, unless the vectors are normalized." — [FAISS wiki](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)
- Cosine search is done by normalizing vectors and then running maximum inner product search. Excerpt: "By normalizing query and database vectors beforehand, the problem can be mapped back to a maximum inner product search." — [FAISS wiki](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances)
- [MATH] For normalized vectors, L2 and inner-product search are equivalent, via |x − y|² = 2 − 2⟨x, y⟩. Excerpt: "equivalent to using an index with METRIC_L2" — [FAISS wiki](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances). The identity was reported by the fetch summarizer; I did not see the page's exact equation formatting. Verify in Pass 2.
- sentence-transformers similarity options are COSINE (default), DOT_PRODUCT, EUCLIDEAN ("Negative Euclidean Distance") and MANHATTAN ("Negative Manhattan Distance"). Excerpt: "Cosine Similarity (default)" — [sbert.net, Semantic Textual Similarity](https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html) (no version shown; "© Copyright 2026")
- On normalized embeddings, dot equals cosine, and dot is faster. Excerpts: "Dot product on normalized embeddings is equivalent to cosine similarity" and "the “dot” metric will be faster than “cosine”" — [sbert.net STS docs](https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)
- OpenAI recommends cosine and says the choice rarely matters. Excerpt: "We recommend cosine similarity. The choice of distance function typically doesn't matter much." — [OpenAI Embeddings guide, "Which distance function should I use?"](https://developers.openai.com/api/docs/guides/embeddings) (no page date shown)
- OpenAI embeddings are unit length, so cosine reduces to a dot product and gives the same ranking as Euclidean distance. Excerpts: "OpenAI embeddings are normalized to length 1"; "Cosine similarity and Euclidean distance will result in the identical rankings" — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)

### Inferences
- [MATH, derivation] ||x−y||² = ||x||² + ||y||² − 2x·y. With ||x|| = ||y|| = 1 this is 2 − 2x·y = 2 − 2cos(x, y). The map from cos to distance is strictly decreasing, so ranking by highest cosine = highest dot = lowest L2 (or squared L2). This holds only when **both** query and corpus vectors are unit length.
- [MATH] An unnormalized dot product is x·y = ||x||·||y||·cos θ. Scaling a document vector by c > 0 scales its score by c, so longer vectors rank higher regardless of direction. The IR book's motivation for normalization is the document-length version of this effect.
- Practical consequence: in FAISS, IndexFlatIP on unnormalized vectors is **not** cosine search. This is a common silent bug.

### Gaps
- I did not see the exact formatted equation |x−y|² = 2 − 2⟨x,y⟩ on the FAISS page myself. The summarizer reported it. Pass 2 should confirm.
- The IR book page does not discuss Euclidean distance between normalized vectors. Its related exercise, §6.3 "Exercise 6.18" (relation between Euclidean distance and cosine for unit vectors), was not fetched.

## Does vector norm carry information, and why normalize?

### Takeaway
Libraries put normalization in the model pipeline (sentence-transformers' Normalize module) so that dot product = cosine, which makes search faster and ranking length-invariant. I found **no fetched primary source** that measures what information the norm carries in modern sentence embeddings.

### Cited Findings
- The sentence-transformers Normalize module L2-normalizes pooled sentence embeddings to unit length. Excerpt: "L2-normalizes the embeddings under one of the feature keys to have unit length." — [sbert.net, Modules reference](https://sbert.net/docs/package_reference/sentence_transformer/models.html) (no version shown; "© Copyright 2026")
- By default it acts on the pooled sentence embedding. Excerpt: "By default operates on the pooled `sentence_embedding` produced by a Pooling layer." — [sbert.net Modules](https://sbert.net/docs/package_reference/sentence_transformer/models.html)
- It can also normalize token-level embeddings for multi-vector models. Excerpt: "useful for multi-vector / ColBERT-style models that score with MaxSim" — [sbert.net Modules](https://sbert.net/docs/package_reference/sentence_transformer/models.html)
- If a model ends in Normalize, sbert advises choosing "dot", because "cosine" re-normalizes. Excerpt: "“cosine” will re-normalize the embeddings again" — [sbert.net STS docs](https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)
- The BGE model card's examples normalize embeddings (e.g. `normalize_embeddings=True`). The fetch reported that the bge-small-en-v1.5 quick-start snippet itself does not show normalization — [HF model card BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5)
- The classic IR motivation is that without length normalization, long documents get an advantage or differ by length rather than content (see the IR book excerpt above) — [IR book §6.3.1](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html)

### Inferences
- Once a model is trained with a cosine objective (or ends in Normalize), any information in the norm is discarded by design at scoring time. The training objective decides whether norm matters. This is an inference, not a sourced claim.
- Some models are trained for dot-product scoring and are deliberately not normalized. For those, normalizing changes rankings. Check the model card. (General knowledge; not sourced here.)

### Gaps
- No primary source was fetched that empirically shows the norm of sentence embeddings encodes, for example, word frequency, specificity or confidence. Candidates for Pass 2: work on word-vector norm and frequency (e.g. Schakel & Wilson 2015, arXiv 1508.02297), and the Reimers/sbert docs on dot-product versus cosine models (msmarco "dot" models). These were not verified here; do not cite them without fetching.

## Dimensionality and Matryoshka representations

### Takeaway
[EMPIRICAL] Matryoshka Representation Learning (MRL) trains one embedding whose prefixes are usable lower-dimensional embeddings. OpenAI's text-embedding-3 models were trained "with a technique" linked to the MRL paper, and they expose this through the `dimensions` parameter. If you truncate manually, you must re-normalize.

### Cited Findings
- MRL learns coarse-to-fine representations as accurate as independently trained low-dimensional ones. Excerpt: "MRL learns coarse-to-fine representations that are at least as accurate and rich" — [Kusupati et al., arXiv 2205.13147 v4 (v1 26 May 2022; v4 8 Feb 2024)](https://arxiv.org/abs/2205.13147)
- MRL encodes information at multiple granularities so that one embedding can fit varying compute budgets. Excerpt: "encodes information at different granularities" — [arXiv 2205.13147](https://arxiv.org/abs/2205.13147)
- [EMPIRICAL] Excerpt: "up to 14x smaller embedding size for ImageNet-1K classification at the same level of accuracy" — [arXiv 2205.13147](https://arxiv.org/abs/2205.13147)
- [EMPIRICAL] Excerpt: "up to 2% accuracy improvements for long-tail few-shot classification" — [arXiv 2205.13147](https://arxiv.org/abs/2205.13147)
- OpenAI default dimensions are 1536 for text-embedding-3-small and 3072 for text-embedding-3-large. Excerpt: "the length of the embedding vector is `1536` for `text-embedding-3-small` or `3072` for `text-embedding-3-large`" — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- OpenAI states the v3 models were trained with a technique that allows shortening. The link in the text points to arXiv 2205.13147 (MRL). Excerpt: "Both of our new embedding models were trained with a technique that allows developers to trade-off performance and cost" — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- Shortening means dropping trailing numbers. Excerpt: "shorten embeddings (i.e. remove some numbers from the end of the sequence) without the embedding losing its concept-representing properties" — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- [EMPIRICAL, vendor claim] Excerpt: "a `text-embedding-3-large` embedding can be shortened to a size of 256 while still outperforming an unshortened `text-embedding-ada-002` embedding" (on MTEB, at size 1536) — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)
- The `dimensions` parameter is preferred. Manual truncation requires re-normalization. Excerpts: "using the `dimensions` parameter when creating the embedding is the suggested approach"; "you need to be sure to normalize the dimensions of the embedding" — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings). The guide's code samples slice to 256 and then divide by the L2 magnitude.
- Shortening trades accuracy for size. Excerpt: "trading off some accuracy in exchange for the smaller vector size" — [OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)

### Inferences
- [MATH] A prefix of a unit vector has norm ≤ 1. After truncation, the dot product is no longer cosine and the identical-ranking guarantee breaks until you re-normalize. This explains OpenAI's re-normalization instruction.
- Truncating a model **not** trained with MRL-style losses can destroy quality. The prefix property is a property of training, not of embeddings in general. (Inference from the MRL premise.)

### Gaps
- OpenAI's launch blog (openai.com/index/new-embedding-models-and-api-updates/) returned HTTP 403. Its MTEB/performance-by-dimension table was not read, and the word "Matryoshka" was not confirmed on any OpenAI page. The guide only links to the arXiv paper.

## Visualizing high-dimensional embeddings (PCA, t-SNE, UMAP)

### Takeaway
[MATH/EMPIRICAL] 2D/3D projections cannot faithfully preserve the geometry of intrinsically high-dimensional embeddings. The t-SNE authors themselves call this impossible. PCA (linear) favours keeping dissimilar points apart. t-SNE favours local neighbourhoods, so cluster sizes and between-cluster distances are not meaningful, and results depend on hyperparameters and random seed. UMAP claims more global structure, but "arguably".

### Cited Findings
- PCA and classical MDS are linear and prioritise keeping dissimilar points far apart. Excerpt: "linear techniques that focus on keeping the low-dimensional representations of dissimilar datapoints far apart" — [van der Maaten & Hinton 2008, JMLR 9(86):2579–2605, §1](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf)
- For data near a nonlinear manifold, keeping similar points close matters more, and linear maps typically cannot do it. Excerpt: "it is usually more important to keep the low-dimensional representations of very similar datapoints close together" — [van der Maaten & Hinton 2008, §1](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf)
- t-SNE's claimed strength: Excerpt: "better than existing techniques at creating a single map that reveals structure at many different scales" — [JMLR abstract page](https://www.jmlr.org/papers/v9/vandermaaten08a.html)
- The authors list three self-identified weaknesses: Excerpt: "(1) it is unclear how t-SNE performs on general dimensionality reduction tasks, (2) the relatively local nature of t-SNE" (sensitive to intrinsic dimensionality), "(3) ... not guaranteed to converge to a global optimum" — [van der Maaten & Hinton 2008, §6.2 "Weaknesses"](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf)
- The key caution, from the t-SNE authors. Excerpt: "it is by definition impossible to fully represent the structure of intrinsically high-dimensional data in two or three dimensions" — [van der Maaten & Hinton 2008, §6.2](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf)
- Results vary from run to run. Excerpt: "may be different each time t-SNE is run from an initial random configuration of map points" — [van der Maaten & Hinton 2008, §6.2](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf)
- UMAP's claims: Excerpts: "arguably preserves more of the global structure with superior run time performance"; "constructed from a theoretical framework based in Riemannian geometry and algebraic topology" — [McInnes, Healy & Melville, arXiv 1802.03426 v3 (v1 9 Feb 2018; v3 18 Sep 2020)](https://arxiv.org/abs/1802.03426)
- Distill cautions (Wattenberg, Viégas & Johnson, *Distill*, 2016-10-13, DOI 10.23915/distill.00002):
  - Excerpt: "you cannot see relative sizes of clusters in a t-SNE plot" — [distill.pub/2016/misread-tsne](https://distill.pub/2016/misread-tsne/)
  - Excerpt: "distances between well-separated clusters in a t-SNE plot may mean nothing" — [distill.pub](https://distill.pub/2016/misread-tsne/)
  - Excerpt: "Recognizing these clumps as random noise is an important part of reading t-SNE plots." — [distill.pub](https://distill.pub/2016/misread-tsne/)
  - Excerpt: "The perplexity value has a complex effect on the resulting pictures." — [distill.pub](https://distill.pub/2016/misread-tsne/)
  - Excerpt: "there's no fixed number of steps that yields a stable result" — [distill.pub](https://distill.pub/2016/misread-tsne/)
  - Excerpt: "analyzing multiple plots with different perplexities" — [distill.pub](https://distill.pub/2016/misread-tsne/)

### Inferences
- Lesson framing: use 2D plots to generate hypotheses about neighbourhoods, never to read off similarity values, cluster sizes or inter-cluster distances. Compute similarity in the original space.
- [MATH, unsourced here] PCA projects onto the directions of maximal variance, which are orthogonal. Its 2D projection preserves as much total variance as any linear 2D projection can, but it shrinks distances along the discarded directions. No fetched source in this pass states this; cite a textbook in Pass 2.
- Anisotropy (next section) interacts with PCA: if embeddings share a dominant common direction, the top PC may reflect that shared offset or frequency rather than semantics. This is an inference only.

### Gaps
- UMAP's "arguably" global-structure claim is the authors' own. No independent verification was fetched.
- No primary source explicitly quantifying PCA distortion on text embeddings was fetched.

## Anisotropy / representation degeneration and uncalibrated cosine scores

### Takeaway
[EMPIRICAL] Contextual word representations from ELMo, BERT and GPT-2 (Ethayarajh 2019) and LM-trained word embeddings (Gao et al. 2019) occupy a narrow cone. Random pairs therefore have high cosine similarity: near 1 in GPT-2's last layer. Raw cosine values are not on an absolute, calibrated scale. BGE's model card makes the same practical point for a modern sentence-embedding model: scores cluster in roughly [0.6, 1], and only relative order matters.

### Cited Findings
- Ethayarajh: representations are anisotropic and occupy a narrow cone. Excerpt: "they are anisotropic, occupying a narrow cone in the vector space" — [Ethayarajh 2019, arXiv 1909.00512 v1 (2 Sep 2019; EMNLP 2019), §1](https://arxiv.org/abs/1909.00512)
- [EMPIRICAL] Extreme case: Excerpt: "The anisotropy in GPT-2’s last layer is so extreme that two random words will on average have almost perfect cosine similarity!" — [Ethayarajh 2019, §1](https://arxiv.org/pdf/1909.00512v1)
- Isotropy baseline: under isotropy, random-pair cosine ≈ 0. Excerpt: "If word representations from a particular layer were isotropic (i.e., directionally uniform), then the average cosine similarity between uniformly randomly sampled words would be 0" — 28 words; trimmed version: "then the average cosine similarity between uniformly randomly sampled words would be 0" — [Ethayarajh 2019, §4.1](https://arxiv.org/pdf/1909.00512v1)
- [EMPIRICAL] Layer trend in GPT-2. Excerpt: "the average cosine similarity between uniformly randomly words is roughly 0.6 in layers 2 through 8 but increases exponentially from layers 8 through 12" (sic, "randomly words") — [Ethayarajh 2019, §4.1](https://arxiv.org/pdf/1909.00512v1)
- Ethayarajh adjusts his metrics by subtracting an anisotropy baseline (§3.4 "Adjusting for Anisotropy"), because raw cosine values are inflated. The section heading was observed in the extracted text — [Ethayarajh 2019, §3.4](https://arxiv.org/pdf/1909.00512v1)
- Only a small share of the variance is static: Excerpt: "less than 5% of the variance in a word's contextualized representations can be explained by a static embedding" — [arXiv 1909.00512 abstract](https://arxiv.org/abs/1909.00512)
- Gao et al. name the phenomenon: Excerpt: "which we call the representation degeneration problem" — [Gao et al., arXiv 1907.12009 v1 (28 Jul 2019; ICLR 2019)](https://arxiv.org/abs/1907.12009)
- Excerpt: "most of the learnt word embeddings tend to degenerate and be distributed into a narrow cone" — [arXiv 1907.12009](https://arxiv.org/abs/1907.12009). The setting is word embeddings in natural language generation models trained by likelihood maximization with weight tying (context from the abstract; verify wording in Pass 2).
- Their fix is a regularizer. Excerpt: "propose a novel regularization method to address it" — [arXiv 1907.12009](https://arxiv.org/abs/1907.12009)
- [EMPIRICAL] BGE similarity distribution: Excerpt: "the similarity distribution of the current BGE model is about in the interval [0.6, 1]" (attributed to contrastive training "with a temperature of 0.01") — [HF model card, BAAI/bge-small-en-v1.5](https://huggingface.co/BAAI/bge-small-en-v1.5) (card note dated 09/12/2023 for v1.5 release)
- v1.5 is recommended to alleviate this. Excerpt: "Suggest to use bge v1.5, which alleviates the issue of the similarity distribution." — [HF BGE card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- Only relative order matters. Excerpt: "what matters is the relative order of the scores, not the absolute value" — [HF BGE card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- Thresholds should be data-specific. Excerpt: "select an appropriate similarity threshold based on the similarity distribution on your data" (examples given: 0.8, 0.85, 0.9) — [HF BGE card](https://huggingface.co/BAAI/bge-small-en-v1.5)
- bge-small-en-v1.5 has 384 dimensions and a 512-token max length (MTEB table on the card) — [HF BGE card](https://huggingface.co/BAAI/bge-small-en-v1.5)

### Inferences
- Implication for learners: a cosine of 0.7 is not "70% similar". Cosine ranges are model-specific (and layer-specific). Any absolute threshold must be calibrated per model on your own data. Thresholds from one model do not transfer to another.
- The Ethayarajh and Gao findings concern **word/token** representations in older LMs (2019). The BGE card is the evidence that compressed score ranges also occur in modern **sentence** embedding models. Do not overgeneralize "narrow cone" to every current embedding model.

### Gaps
- The terms "anisotropy" and "narrow cone" are not in the Ethayarajh abstract. They are in the body (§1, §4.1), which I verified via the PDF text. For Gao et al., I did not read the PDF body. Excerpts come from the abstract only.
- I did not verify whether BGE v1.5's card gives a new numeric interval after the "alleviation". No such number was reported.

## Benchmarks: MTEB

### Takeaway
[EMPIRICAL] MTEB (2022) spans 8 task types, 58 datasets and 112 languages, and benchmarks 33 models. It finds no embedding method dominates across all tasks, so model choice should depend on the task.

### Cited Findings
- Excerpt: "MTEB spans 8 embedding tasks covering a total of 58 datasets and 112 languages" — [Muennighoff et al., arXiv 2210.07316 v3 (v1 13 Oct 2022; v3 19 Mar 2023)](https://arxiv.org/abs/2210.07316)
- Excerpt: "Through the benchmarking of 33 models on MTEB, we establish the most comprehensive benchmark of text embeddings to date." — [arXiv 2210.07316](https://arxiv.org/abs/2210.07316)
- Excerpt: "We find that no particular text embedding method dominates across all tasks." — [arXiv 2210.07316](https://arxiv.org/abs/2210.07316)
- The arXiv page lists no peer-reviewed venue (cs.CL; cross-listed cs.IR, cs.LG). The paper was published at EACL 2023 per general knowledge, but this was **not verified** in this pass — [arXiv 2210.07316](https://arxiv.org/abs/2210.07316)

### Inferences
- Pick models on the MTEB task category that matches your use (e.g. retrieval rather than the overall average), then validate on your own data.

### Gaps
- The names of the 8 task types (expected: bitext mining, classification, clustering, pair classification, reranking, retrieval, STS, summarization) were **not** confirmed from a fetched source in this pass. Verify from the paper body.
- MTEB's current leaderboard and later versions (e.g. MMTEB) are out of scope and not checked.

---

### Claims table

| # | Claim | Source URL | Excerpt (≤25 words) | Confidence |
|---|---|---|---|---|
| 1 | [MATH] Cosine = dot product of length-normalized vectors | https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html | "can be viewed as the dot product of the normalized versions of the two document vectors" | high |
| 2 | Cosine denominator length-normalizes the vectors | https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html | "The effect of the denominator of Equation 24 is thus to length-normalize the vectors" | high |
| 3 | Length differences distort raw vector-difference similarity | https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html | "two documents with very similar content can have a significant vector difference" | high |
| 4 | FAISS L2 metric returns squared distance | https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances | "reports squared Euclidean (L2) distance, avoiding the square root" | high |
| 5 | Inner product ≠ cosine unless normalized | https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances | "This is not by itself cosine similarity, unless the vectors are normalized." | high |
| 6 | [MATH] Unit vectors: \|x−y\|² = 2 − 2⟨x,y⟩, so L2 and IP search are equivalent | https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances | "equivalent to using an index with METRIC_L2" | high (math); medium (exact page wording) |
| 7 | Cosine search = normalize, then maximum inner product search | https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances | "By normalizing query and database vectors beforehand, the problem can be mapped back to a maximum inner product search." | high |
| 8 | sentence-transformers default similarity is cosine | https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html | "Cosine Similarity (default)" | high |
| 9 | Dot on normalized embeddings = cosine, and faster | https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html | "Dot product on normalized embeddings is equivalent to cosine similarity" | high |
| 10 | Normalize module L2-normalizes to unit length | https://sbert.net/docs/package_reference/sentence_transformer/models.html | "L2-normalizes the embeddings under one of the feature keys to have unit length." | high |
| 11 | OpenAI recommends cosine; choice rarely matters | https://developers.openai.com/api/docs/guides/embeddings | "We recommend cosine similarity. The choice of distance function typically doesn't matter much." | high |
| 12 | OpenAI embeddings are unit length; cosine and Euclidean rank identically | https://developers.openai.com/api/docs/guides/embeddings | "Cosine similarity and Euclidean distance will result in the identical rankings" | high |
| 13 | Defaults: 1536 (3-small), 3072 (3-large) | https://developers.openai.com/api/docs/guides/embeddings | "the length of the embedding vector is `1536` for `text-embedding-3-small` or `3072` for `text-embedding-3-large`" | high |
| 14 | v3 models trained with an MRL-linked technique; can drop trailing numbers | https://developers.openai.com/api/docs/guides/embeddings | "shorten embeddings (i.e. remove some numbers from the end of the sequence) without the embedding losing its concept-representing properties" | high |
| 15 | [EMPIRICAL, vendor] 3-large at 256 dims beats ada-002 at 1536 on MTEB | https://developers.openai.com/api/docs/guides/embeddings | "can be shortened to a size of 256 while still outperforming an unshortened `text-embedding-ada-002` embedding" | medium (vendor claim, not independently checked) |
| 16 | Manual truncation needs re-normalization | https://developers.openai.com/api/docs/guides/embeddings | "you need to be sure to normalize the dimensions of the embedding" | high |
| 17 | MRL: coarse-to-fine nested representations as accurate as separately trained ones | https://arxiv.org/abs/2205.13147 | "MRL learns coarse-to-fine representations that are at least as accurate and rich" | high |
| 18 | [EMPIRICAL] MRL up to 14× smaller embeddings on ImageNet-1K at equal accuracy | https://arxiv.org/abs/2205.13147 | "up to 14x smaller embedding size for ImageNet-1K classification at the same level of accuracy" | high (as reported) |
| 19 | PCA/MDS keep dissimilar points far apart (linear) | https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf | "linear techniques that focus on keeping the low-dimensional representations of dissimilar datapoints far apart" | high |
| 20 | High-dim structure cannot be fully shown in 2D/3D | https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf | "it is by definition impossible to fully represent the structure of intrinsically high-dimensional data in two or three dimensions" | high |
| 21 | t-SNE is non-convex; runs differ | https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf | "may be different each time t-SNE is run from an initial random configuration of map points" | high |
| 22 | UMAP arguably preserves more global structure, faster | https://arxiv.org/abs/1802.03426 | "arguably preserves more of the global structure with superior run time performance" | medium (authors' own hedged claim) |
| 23 | t-SNE cluster sizes are not meaningful | https://distill.pub/2016/misread-tsne/ | "you cannot see relative sizes of clusters in a t-SNE plot" | high |
| 24 | t-SNE inter-cluster distances may mean nothing | https://distill.pub/2016/misread-tsne/ | "distances between well-separated clusters in a t-SNE plot may mean nothing" | high |
| 25 | t-SNE perplexity strongly shapes the picture | https://distill.pub/2016/misread-tsne/ | "The perplexity value has a complex effect on the resulting pictures." | high |
| 26 | [EMPIRICAL] Contextual reps (ELMo/BERT/GPT-2) occupy a narrow cone | https://arxiv.org/pdf/1909.00512v1 | "they are anisotropic, occupying a narrow cone in the vector space" | high |
| 27 | [EMPIRICAL] GPT-2 last layer: random words have near-perfect cosine | https://arxiv.org/pdf/1909.00512v1 | "two random words will on average have almost perfect cosine similarity!" | high |
| 28 | Isotropic baseline: random-pair cosine ≈ 0 | https://arxiv.org/pdf/1909.00512v1 | "the average cosine similarity between uniformly randomly sampled words would be 0" | high |
| 29 | [EMPIRICAL] LM word embeddings degenerate into a narrow cone | https://arxiv.org/abs/1907.12009 | "most of the learnt word embeddings tend to degenerate and be distributed into a narrow cone" | high |
| 30 | [EMPIRICAL] BGE similarities lie roughly in [0.6, 1] | https://huggingface.co/BAAI/bge-small-en-v1.5 | "the similarity distribution of the current BGE model is about in the interval [0.6, 1]" | high |
| 31 | Use relative order, not absolute similarity values | https://huggingface.co/BAAI/bge-small-en-v1.5 | "what matters is the relative order of the scores, not the absolute value" | high |
| 32 | Thresholds must be chosen per data distribution | https://huggingface.co/BAAI/bge-small-en-v1.5 | "select an appropriate similarity threshold based on the similarity distribution on your data" | high |
| 33 | MTEB: 8 tasks, 58 datasets, 112 languages | https://arxiv.org/abs/2210.07316 | "MTEB spans 8 embedding tasks covering a total of 58 datasets and 112 languages" | high |
| 34 | MTEB: 33 models benchmarked | https://arxiv.org/abs/2210.07316 | "Through the benchmarking of 33 models on MTEB" | high |
| 35 | No single embedding method dominates all tasks | https://arxiv.org/abs/2210.07316 | "We find that no particular text embedding method dominates across all tasks." | high |
| 36 | Norm of sentence embeddings carries semantic information | (none fetched) | n/a | low (unsourced; gap) |
| 37 | MTEB's 8 task-type names | (not confirmed) | n/a | low (unverified; gap) |
