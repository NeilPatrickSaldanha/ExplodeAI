# Normalized vectors turn meaning into geometry

*Pass 1 evidence report for an ExplodeAI lesson on text embeddings. All sources accessed 2026-10-19. Synthesized from three research-note files in `research_notes/Embeddings primary sources/`: `embedding_foundations.md`, `similarity_geometry.md`, `embeddings_in_practice.md`. Excerpts are copied from those notes and are 25 words or fewer. Read fidelity differs by note. The foundations note downloaded raw files (pinned Hugging Face commits, GitHub raw files, arXiv abstract pages, ar5iv full text) and string-matched every excerpt. The geometry note used a summarizing fetch tool for most web pages but extracted the t-SNE and Ethayarajh PDFs locally, so those excerpts are exact. The practice note used the summarizing fetch tool throughout. The claims table in Appendix B marks every excerpt that came through the summarizer for Pass 2 re-checking. No paid API was called.*

The primary sources agree on what a text embedding is: a **fixed-length vector learned so that geometric closeness tracks relatedness of meaning**. The papers document three steps. word2vec gave each word one vector. BERT made token vectors depend on context. Contrastively fine-tuned encoders such as SBERT, SimCSE and BGE produce one vector per sentence or passage that works with cosine similarity. For the lesson's reference model, the config files in BAAI's Hugging Face repo (commit `5c38ec7`) pin down the whole pipeline. bge-small-en-v1.5 is a **12-layer BERT** with a **30,522-entry lowercase WordPiece vocabulary**. It accepts at most **512 tokens** and returns the **[CLS] token's 384-dimension hidden state**, which an explicit `Normalize` module scales to unit length. Queries, but never passages, can optionally take the prefix "Represent this sentence for searching relevant passages: ". Because the output vectors have length 1, **cosine similarity, dot product and Euclidean distance give identical rankings**. That is the one claim in this report that is pure mathematics and holds for every model. Almost everything else is empirical, model-specific or dated. Contextual representations are **anisotropic**, and BGE's own card warns that raw scores are uncalibrated ("a similarity score greater than 0.5 does not indicate that the two sentences are similar"). Matryoshka shortening works only for models trained for it and needs re-normalization. 2D maps distort by construction. MTEB finds that **no single model wins every task**. Input limits (8,192 tokens at OpenAI and Gemini, 32,000 at Voyage, 512 for BGE), query/document conventions and model compatibility all differ by provider; Google, for example, says its two current embedding spaces are "incompatible". Four items most need Pass 2 checks. First, what Qdrant's "quantized" ONNX export really is: its config says fp16 with an empty quantization block. Second, whether BGE's "[0.6, 1]" score range still applies to v1.5. Third, why fastembed's README advertises query prefixes that its code does not add. Fourth, every vendor-doc excerpt that came through a summarizing fetch tool.

## Word vectors became sentence vectors through contrastive fine-tuning

The modern idea starts with Mikolov et al., who proposed architectures "for computing continuous vector representations of words from very large data sets". They learned high-quality vectors from a 1.6-billion-word corpus in "less than a day" ([arXiv 1301.3781 v3](https://arxiv.org/abs/1301.3781)). The paper expects that "not only will similar words tend to be close to each other, but that words can have multiple degrees of similarity". Its best-known result is offset arithmetic: vector("King") − vector("Man") + vector("Woman") gives "a vector that is closest to the vector representation of the word Queen" ([ar5iv 1301.3781](https://ar5iv.labs.arxiv.org/html/1301.3781), Sec. 1.1, which credits earlier work for the finding). The follow-up skip-gram paper adds a second analogy (Madrid − Spain + France ≈ Paris). It introduces **negative sampling**, the ancestor of contrastive training. It also names the method's limit: "their indifference to word order and their inability to represent idiomatic phrases" ([arXiv 1310.4546 v1](https://arxiv.org/abs/1310.4546)). The phrase "one vector per word type" is not in the word2vec papers. It comes from later work: Ethayarajh writes that static embeddings gave "each word... a single vector, regardless of context", so "all senses of a polysemous word had to share the same representation" ([ar5iv 1909.00512](https://ar5iv.labs.arxiv.org/html/1909.00512)). Neither word2vec abstract mentions the distributional hypothesis (Harris/Firth), and the full texts were not searched for it. Any lesson sentence that names it needs its own source.

BERT made representations contextual. It conditions "on both left and right context in all layers" ([arXiv 1810.04805 v2](https://arxiv.org/abs/1810.04805)) and uses "WordPiece embeddings (Wu et al. 2016) with a 30,000 token vocabulary". The final hidden state of its special [CLS] token "is used as the aggregate sequence representation for classification tasks" ([ar5iv 1810.04805](https://ar5iv.labs.arxiv.org/html/1810.04805), Sec. 3). The same paper warns that this vector "is not a meaningful sentence representation without fine-tuning, since it was trained with NSP" (footnote, Sec. 3.1). Ethayarajh then measured how contextual these vectors are. In ELMo, BERT and GPT-2, **less than 5% of the variance** in a word's contextual representations can be explained by a static embedding, and upper layers are the most context-specific ([arXiv 1909.00512 v1](https://arxiv.org/abs/1909.00512)).

Raw BERT outputs proved poor at sentence similarity, and the SBERT paper quantifies this. Averaged BERT embeddings reach an average STS correlation of **only 54.81**, and the CLS output **only 29.19**. Both are "worse than computing average GloVe embeddings". The paper concludes that out-of-the-box BERT maps sentences to a space "rather unsuitable to be used with common similarity measures like cosine-similarity" ([ar5iv 1908.10084](https://ar5iv.labs.arxiv.org/html/1908.10084), Sec. 4.1 and 8). SBERT's fix is a **pooling layer plus fine-tuning**. Its pooling options are the CLS token, the mean of all outputs (MEAN, the default) or max-over-time. Once the model is trained on NLI, "the pooling strategy has a rather minor impact": on the STSb dev set, MEAN scores 80.78, CLS 79.80 and MAX 79.07. Raw BERT is weak at cosine similarity specifically, not at every task. On SentEval, the paper reports, averaged BERT and CLS achieve "decent results". The efficiency case matters too. Finding the most similar pair among 10,000 sentences takes BERT cross-encoding about 50 million inferences (~65 hours), while SBERT's independent sentence vectors do it in about 5 seconds ([arXiv 1908.10084](https://arxiv.org/abs/1908.10084)). This is why embeddings are computed once per document and compared cheaply afterwards.

SimCSE supplies the general recipe that BGE scales up. Contrastive learning works by "pulling semantically close neighbors together and pushing apart non-neighbors". The objective is cross-entropy with in-batch negatives, a temperature τ and cosine similarity ([ar5iv 2104.08821](https://ar5iv.labs.arxiv.org/html/2104.08821), Sec. 2). Unsupervised SimCSE uses dropout as its only noise. Supervised SimCSE uses NLI "entailment" pairs as positives and "contradiction" pairs as hard negatives. It reaches 76.3% and 81.6% Spearman on STS with BERT-base. The paper also states that the objective "regularizes pre-trained embeddings' anisotropic space to be more uniform" ([arXiv 2104.08821 v4](https://arxiv.org/abs/2104.08821)), which links contrastive training directly to the anisotropy problem discussed below.

## bge-small-en-v1.5 is a 384-dimension CLS-pooled, unit-normalized BERT

Every stage of the reference model can be read from files in the BAAI repository, pinned at commit `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a` (lastModified 2024-02-22, created 2023-09-12). The model card's prose agrees with those files. The C-Pack paper, in the version read, does not mention CLS pooling or v1.5. **Those facts rest on the card and config files alone.**

| Stage | What the primary source says | Source file |
|---|---|---|
| Tokenizer | `"vocab_size": 30522`, `"model_type": "bert"` (BERT's paper rounds to "30,000"); `"do_lower_case": true` | [config.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/config.json), [sentence_bert_config.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/sentence_bert_config.json) |
| Input limit | `"max_seq_length": 512`; `"max_position_embeddings": 512` | same two files |
| Encoder | `"num_hidden_layers": 12`, `"num_attention_heads": 12`, `"hidden_size": 384` | config.json |
| Pooling | `"pooling_mode_cls_token": true, "pooling_mode_mean_tokens": false`; card code `model_output[0][:, 0]` | [1_Pooling/config.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/1_Pooling/config.json), [model card](https://huggingface.co/BAAI/bge-small-en-v1.5) |
| Normalization | modules in order: Transformer → Pooling → `sentence_transformers.models.Normalize`; card code `torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)` | [modules.json](https://huggingface.co/BAAI/bge-small-en-v1.5/blob/main/modules.json), model card |
| Output | 384 dimensions; card MTEB row "BAAI/bge-small-en-v1.5 \| 384 \| 512 \| 62.17" (dimension, sequence length, average over 56 tasks) | model card |
| Query instruction | `Represent this sentence for searching relevant passages: ` (trailing space), on queries only | model card |

The card describes pooling in plain words: "select the last hidden state of the first token (i.e., [CLS]) as the sentence embedding" ([model card](https://huggingface.co/BAAI/bge-small-en-v1.5)). The choice fits SBERT's finding that pooling matters little once a model is fine-tuned. BGE uses the CLS vector that BERT's authors called meaningless *without* fine-tuning, and it is heavily fine-tuned. The card summarizes training as "We pre-train the models using retromae and train them on large-scale pairs data using contrastive learning". It adds that the pre-trained model "cannot be used for similarity calculation directly". The C-Pack paper gives more detail. The general stage learns "to discriminate the paired texts from their negative samples" using **in-batch negatives with batches "as large as 19,200"**. The task-specific stage attaches "a task specific instruction... to the query side" and mines "one hard negative sample... for each text pair". The English training set "consists of 200M text pairs" ([ar5iv 2309.07597](https://ar5iv.labs.arxiv.org/html/2309.07597)). One caution applies: the ar5iv rendering predates the v5 abstract (24 Sep 2024), which renames the training method "C-TEM". All C-Pack wording should be checked against the [v5 PDF](https://arxiv.org/pdf/2309.07597v5). The paper's 24M/102M/326M parameter counts describe the **Chinese** models. The English small model's `model.safetensors` is 133,466,304 bytes, which at fp32 works out to roughly **33M parameters**. That figure is a derived estimate, not a stated fact.

The card's instruction guidance is nuanced. The footnote suggests adding the instruction when you "search the relevant passages to a query", and says "In all cases, **no instruction** needs to be added to passages". FAQ 3 adds that for v1.5, "No instruction only has a slight degradation in retrieval performance compared with using instruction". It recommends the instruction for "short queries" and tells users to pick "the setting that achieves better performance on your task" ([model card](https://huggingface.co/BAAI/bge-small-en-v1.5)). The v1.5 release note (dated 09/12/2023) says the update was made "to alleviate the issue of the similarity distribution, and enhance its retrieval ability without instruction". The card gives no changelog of how v1.5 was retrained.

On scoring, the card's examples set `normalize_embeddings=True` and compute `embeddings_1 @ embeddings_2.T`. The LangChain snippet comments "set True to compute cosine similarity". The card therefore *shows*, but never states as a rule, that a dot product of its outputs is cosine similarity. The geometry note adds that the card's quick-start snippet itself does not show normalization. When the model is loaded through sentence-transformers, the `Normalize` module in `modules.json` normalizes the output regardless.

### fastembed serves a Qdrant fp16 ONNX export without the query instruction

The production path for the lesson differs in two ways from BAAI's reference code. In fastembed (`main` at commit `de502ca`, 2026-10-15; latest release v0.9.0, 2026-10-07), the registry entry `model="BAAI/bge-small-en-v1.5", dim=384` actually downloads `sources=ModelSource(hf="Qdrant/bge-small-en-v1.5-onnx-Q")` and loads `model_file="model_optimized.onnx"` (`size_in_GB=0.067`). Its description reads "512 input tokens truncation, Prefixes for queries/documents: not so necessary, 2023 year" ([onnx_embedding.py](https://github.com/qdrant/fastembed/blob/main/fastembed/text/onnx_embedding.py)). Post-processing matches BAAI's pipeline: `embeddings[:, 0]` (CLS) followed by `normalize(...)`. The Qdrant model card (commit `aa8f8b0`, lastModified 2026-09-24) calls the repo a "Quantized ONNX port of BAAI/bge-small-en-v1.5" ([Qdrant card](https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q)). Its `ort_config.json` (optimum 1.15.0) contradicts that label: it has `"quantization": {}`, `"fp16": true`, `"optimization_level": 2` and `"enable_gelu_approximation": true` ([ort_config.json](https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q/blob/main/ort_config.json)). The file is 66,465,124 bytes, about half of BAAI's fp32 `onnx/model.onnx` at 133,093,490 bytes. Both facts point to **an fp16, graph-optimized export, not int8 quantization**, but no Qdrant source says so. Second, `query_embed` in the base class simply calls `self.embed(...)` and comments that the behaviour "is model-specific". `OnnxTextEmbedding` does not override it, so **fastembed adds no BGE instruction to queries** ([text_embedding_base.py](https://github.com/qdrant/fastembed/blob/main/fastembed/text/text_embedding_base.py)). The README nonetheless says the default model "supports "query" and "passage" prefixes" ([fastembed README](https://github.com/qdrant/fastembed)). That wording looks E5-style and does not match the code. To use BGE's instruction, a fastembed user must prepend it manually. No source quantifies how far the fp16 export's vectors drift from BAAI's fp32 weights.

## Unit length makes cosine, dot product and Euclidean rank identically

The comparison rules are the most solid part of the evidence base, because they are mathematics. The IR textbook defines cosine similarity as "the standard way of quantifying the similarity between two documents". Its denominator exists "to length-normalize the vectors", so cosine "can be viewed as the dot product of the normalized versions of the two document vectors" ([Manning, Raghavan & Schütze, IR book §6.3.1](https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html)). The book motivates normalization with document length: "two documents with very similar content can have a significant vector difference" when one is much longer. The equivalence follows in one line. **‖x − y‖² = ‖x‖² + ‖y‖² − 2x·y**, which for unit vectors becomes **2 − 2·cos(x, y)**. That is a strictly decreasing function of cosine, so the highest cosine, the highest dot product and the smallest Euclidean or squared-Euclidean distance pick the same neighbours, provided **both** query and corpus vectors are unit length. Without normalization, x·y = ‖x‖·‖y‖·cos θ, so a longer vector scores higher whatever its direction.

Every library and vendor source restates this rule for its own system. FAISS's `METRIC_L2` "reports squared Euclidean (L2) distance, avoiding the square root". Its inner product "is not by itself cosine similarity, unless the vectors are normalized". Cosine search is done by normalizing query and database vectors so the problem "can be mapped back to a maximum inner product search". For normalized data, inner-product search is "equivalent to using an index with METRIC_L2" ([FAISS wiki, MetricType and distances](https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances), last edited 2024-12-03). The practical trap is direct: `IndexFlatIP` on unnormalized vectors is **not** cosine search. sentence-transformers offers COSINE (default), DOT_PRODUCT, EUCLIDEAN (negative Euclidean distance) and MANHATTAN. It notes that "Dot product on normalized embeddings is equivalent to cosine similarity", and that "dot" is faster because "cosine" "will re-normalize the embeddings again" ([sbert.net STS docs](https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)). Its `Normalize` module "L2-normalizes the embeddings... to have unit length", by default on the pooled `sentence_embedding` ([sbert.net Modules](https://sbert.net/docs/package_reference/sentence_transformer/models.html)). OpenAI states that its embeddings "are normalized to length 1". Cosine therefore "can be computed slightly faster using just a dot product", and "Cosine similarity and Euclidean distance will result in the identical rankings". Its advice is "We recommend cosine similarity. The choice of distance function typically doesn't matter much" ([OpenAI Embeddings guide](https://developers.openai.com/api/docs/guides/embeddings)). OpenAI's "doesn't matter much" holds *because* its vectors are unit length. It is not a general law. The research found **no primary source measuring what information, if any, the vector norm carries** in modern sentence embeddings. Once a model ends in `Normalize`, the norm is discarded at scoring time by design. Some models are trained for unnormalized dot-product scoring, but that claim was not sourced in this pass.

### Anisotropy means a cosine score is a rank, not a percentage

If vectors pointed uniformly in all directions, random pairs would average a cosine of zero. Ethayarajh states this baseline directly: under isotropy, "the average cosine similarity between uniformly randomly sampled words would be 0" ([arXiv 1909.00512 v1 PDF](https://arxiv.org/pdf/1909.00512v1), §4.1). Real contextual representations are not like that. They are "anisotropic, occupying a narrow cone in the vector space", and in GPT-2 the random-pair cosine "is roughly 0.6 in layers 2 through 8 but increases exponentially from layers 8 through 12". The paper's most quotable line follows: "two random words will on average have almost perfect cosine similarity!" (§1). Ethayarajh subtracts an anisotropy baseline from every metric (§3.4, "Adjusting for Anisotropy"), because raw cosine values are inflated. Gao et al. found the same effect in likelihood-trained language-model word embeddings with weight tying. They called it "the representation degeneration problem": embeddings "degenerate and be distributed into a narrow cone", and the authors propose a regularizer to fix it ([arXiv 1907.12009 v1](https://arxiv.org/abs/1907.12009)).

These two papers study 2019-era word and token representations (ELMo, BERT, GPT-2), not BGE. The evidence that modern sentence encoders also produce uncalibrated scores comes from BGE's own card. FAQ 2 says that "Since we finetune the models by contrastive learning with a temperature of 0.01, the similarity distribution of the current BGE model is about in the interval [0.6, 1]". It continues that "a similarity score greater than 0.5 does not indicate that the two sentences are similar" and "what matters is the relative order of the scores, not the absolute value". It suggests thresholds such as 0.8, 0.85 or 0.9, chosen "based on the similarity distribution on your data". The FAQ also says "Suggest to use bge v1.5, which alleviates the issue of the similarity distribution" ([model card](https://huggingface.co/BAAI/bge-small-en-v1.5)). The two research notes read this passage differently. One records "[0.6, 1]" as a high-confidence BGE fact. The other notes that "the current BGE model" sits next to advice to switch to v1.5, so the range most likely describes **v1**, and v1.5 "alleviates" it without giving a new range. This report takes the cautious reading. Teach that BGE scores are compressed and uncalibrated. Do not present [0.6, 1] as a measured v1.5 range, and do not let a lesson demo assert any specific interval until Pass 2 measures it. For learners, the lesson is that **a cosine of 0.7 is not "70% similar"**. Thresholds belong to one model and one dataset, and they do not transfer.

## Prefixes of vectors and 2D maps both trade fidelity for convenience

Embedding sizes are a training choice, not a law. Matryoshka Representation Learning (MRL) trains a single vector that "encodes information at different granularities", so that its prefixes are usable smaller embeddings. These coarse-to-fine representations are "at least as accurate and rich" as separately trained low-dimensional models. The paper reports "up to 14x smaller embedding size for ImageNet-1K classification at the same level of accuracy" and "up to 2% accuracy improvements for long-tail few-shot classification" ([Kusupati et al., arXiv 2205.13147 v4, 8 Feb 2024](https://arxiv.org/abs/2205.13147)). Those numbers come from image classification, not text retrieval. OpenAI's guide says text-embedding-3-small defaults to **1536** dimensions and text-embedding-3-large to **3072**. Both "were trained with a technique that allows developers to trade-off performance and cost", and the guide links that phrase to the MRL paper without using the word "Matryoshka". Developers can "shorten embeddings (i.e. remove some numbers from the end of the sequence) without the embedding losing its concept-representing properties". OpenAI's vendor claim is that 3-large "can be shortened to a size of 256 while still outperforming an unshortened `text-embedding-ada-002` embedding" on MTEB. The guide prefers the `dimensions` parameter. When users truncate manually, "you need to be sure to normalize the dimensions of the embedding" ([OpenAI guide](https://developers.openai.com/api/docs/guides/embeddings)). The API reference limits `dimensions` to "`text-embedding-3` and later models" ([OpenAI API reference](https://developers.openai.com/api/reference/resources/embeddings/methods/create)). Other providers document the same control. Gemini recommends "768, 1536, or 3072 output dimensions". gemini-embedding-2 "introduces automatic renormalization for non-default dimensions", while gemini-embedding-001 needs manual normalization below 3072 ([Gemini docs](https://ai.google.dev/gemini-api/docs/embeddings)). Voyage says to "truncate them by keeping the leading subset of dimensions, then normalize them again". It also offers int8 and binary output, reducing "storage, memory, and costs by 4x and 32x, respectively" ([Anthropic embeddings page](https://platform.claude.com/docs/en/build-with-claude/embeddings)). sentence-transformers exposes the same idea as `truncate_dim` ([SentenceTransformer API](https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html)). Re-normalization follows from mathematics: a prefix of a unit vector has norm ≤ 1, so after truncation a dot product is no longer cosine. Whether truncation preserves quality is an empirical question about how the model was trained. No source here claims bge-small-en-v1.5 was trained with MRL, so the lesson should not truncate its 384 dimensions.

Visualizing 384 or 3,072 dimensions in two dimensions loses information by construction. The t-SNE authors themselves write that "it is by definition impossible to fully represent the structure of intrinsically high-dimensional data in two or three dimensions" ([van der Maaten & Hinton 2008, JMLR 9(86):2579–2605, §6.2](https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf)). They describe PCA and classical MDS as "linear techniques that focus on keeping the low-dimensional representations of dissimilar datapoints far apart". For data on a nonlinear manifold, "it is usually more important to keep the low-dimensional representations of very similar datapoints close together", and t-SNE is built for that (§1). They list t-SNE's own weaknesses: unclear performance on general dimensionality reduction, its "relatively local nature", and no guarantee of a global optimum. Its maps "may be different each time t-SNE is run from an initial random configuration" (§6.2). UMAP's authors claim it "arguably preserves more of the global structure with superior run time performance" ([McInnes, Healy & Melville, arXiv 1802.03426 v3](https://arxiv.org/abs/1802.03426)). The "arguably" is theirs, and no independent check was fetched. Distill's reading guide gives the practical warnings: "you cannot see relative sizes of clusters in a t-SNE plot"; "distances between well-separated clusters in a t-SNE plot may mean nothing"; random noise can form clumps; "The perplexity value has a complex effect on the resulting pictures"; and "there's no fixed number of steps that yields a stable result". It recommends "analyzing multiple plots with different perplexities" ([Wattenberg, Viégas & Johnson, Distill, 2016-10-13](https://distill.pub/2016/misread-tsne/)). The lesson rule that follows is to **use 2D plots to form hypotheses about neighbourhoods and to compute every similarity in the original space**. Anisotropy adds a further, unsourced risk: if all vectors share a dominant direction, the top principal component may capture that shared offset rather than meaning. No fetched source states PCA's maximal-variance property; cite a textbook in Pass 2.

## Every provider sets its own limits, prefixes and compatibility rules

MTEB is the benchmark cited across the sources, and its headline result argues against a single best model. It "spans 8 embedding tasks covering a total of 58 datasets and 112 languages" and benchmarks 33 models. It finds "that no particular text embedding method dominates across all tasks" ([Muennighoff et al., arXiv 2210.07316 v3, 19 Mar 2023](https://arxiv.org/abs/2210.07316)). The names of the eight task types and the EACL 2023 venue were not confirmed from a fetched source. Leaderboard positions are dated by nature. C-Pack's claim that its English models "achieve state-of-the-art performance on MTEB benchmark" ([arXiv 2309.07597 v5](https://arxiv.org/abs/2309.07597)) and BGE's 62.17 average over 56 tasks describe 2023 and 2024. They say nothing about rank in October 2026. The lesson should teach learners to pick models on the MTEB category that matches their task (retrieval, for RAG) and then test on their own data.

On use cases the vendors broadly agree. OpenAI lists search, clustering, recommendations, anomaly detection, diversity measurement and classification ("where text strings are classified by their most similar label") ([OpenAI guide](https://developers.openai.com/api/docs/guides/embeddings)). Gemini lists information retrieval, search reranking, anomaly detection, classification and clustering, and calls RAG "a common use case for AI products" ([Gemini docs](https://ai.google.dev/gemini-api/docs/embeddings); list items paraphrased by the fetch tool). sentence-transformers leads with "semantic search, semantic textual similarity, and paraphrase mining" ([sbert.net](https://sbert.net/)). Anthropic's page frames embeddings for "search, recommendations, and anomaly detection" ([Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)). Search, clustering, classification and anomaly detection are the safe common ground.

The query/document asymmetry is real, but every provider handles it with a different mechanism.

| Provider or model | Mechanism | Exact strings and rules | Source |
|---|---|---|---|
| BGE (bge-small-en-v1.5) | Manual prefix on queries only | `Represent this sentence for searching relevant passages: `; "the documents/passages do not need to add the instruction"; optional in v1.5 | [BGE card](https://huggingface.co/BAAI/bge-small-en-v1.5) |
| Voyage (via Anthropic docs) | `input_type` prepends fixed prompts | Query: "Represent the query for retrieving supporting documents: "; document: "Represent the document for retrieval: "; "Do not omit `input_type` or set `input_type=None`" | [Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings) |
| Gemini gemini-embedding-001 | `task_type` enum | SEMANTIC_SIMILARITY, CLASSIFICATION, CLUSTERING, RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, CODE_RETRIEVAL_QUERY, QUESTION_ANSWERING, FACT_VERIFICATION | [Gemini docs](https://ai.google.dev/gemini-api/docs/embeddings) |
| Gemini gemini-embedding-2 | None via `task_type` | "You cannot use the `task_type` field for the `gemini-embedding-2` model." Replacement guidance not captured | [Gemini docs](https://ai.google.dev/gemini-api/docs/embeddings) |
| sentence-transformers | `encode_query` / `encode_document` plus prompts | "The prompt text will be prepended before any text during inference." | [SentenceTransformer API](https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html) |
| OpenAI | No query/document parameter found | Absence in guide and reference; not proof | [OpenAI guide](https://developers.openai.com/api/docs/guides/embeddings) |
| fastembed (bge-small) | `query_embed` = `embed`, no prefix | README claims prefix support; code adds none | [text_embedding_base.py](https://github.com/qdrant/fastembed/blob/main/fastembed/text/text_embedding_base.py) |

Voyage explains why the asymmetry helps: specifying query or document "can create better dense vector representations for retrieval, which can lead to better retrieval quality". The general rule for the lesson is that whatever convention indexed the corpus must also be used at query time.

Input limits also differ, and **silent truncation** is the main pitfall. OpenAI states that input "must not exceed the max input tokens for the model (8192 tokens for all embedding models)". It also caps arrays at 2,048 inputs (its text says "2048 dimensions") and requests at "300,000 tokens summed across all inputs" ([OpenAI API reference](https://developers.openai.com/api/reference/resources/embeddings/methods/create)). Whether OpenAI errors or truncates on overflow was not confirmed. Gemini's limit is 8,192 tokens, and "The system silently truncates inputs that exceed this limit" ([Gemini docs](https://ai.google.dev/gemini-api/docs/embeddings)). Voyage's voyage-4 family has a 32,000-token context and voyage-law-2 has 16,000. voyage-context-4 accepts 120,000 tokens only with `enable_auto_chunking` set to `true` ([Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)). bge-small-en-v1.5 accepts 512 tokens. sentence-transformers truncates "to the first `model.max_seq_length` tokens", and "You cannot increase the length higher than what is maximally supported by the respective transformer model". It equates 512 BERT tokens to "about 300-400 words (for English)" and warns that a model "trained on short texts" may represent long texts poorly ([sbert computing embeddings](https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html)). Its all-MiniLM-L6-v2 example shows a limit of only 256. For RAG, chunking below the model's limit is therefore required, not optional.

Model changes require re-embedding. Google gives the clearest official statement: "The embedding spaces between `gemini-embedding-001` and `gemini-embedding-2` are **incompatible**", and "If you are upgrading to `gemini-embedding-2`, you must re-embed all of your existing data" ([Gemini docs](https://ai.google.dev/gemini-api/docs/embeddings)). Qdrant, a vector-database vendor, says "Switching models requires re-embedding all vectors in your collection". A new collection must match the new model's "vector size and similarity function" ([Qdrant migration tutorial](https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/)). The tutorial's dual-write migration pattern was seen only in a search summary. No OpenAI statement on cross-model compatibility was found, and Pinecone's docs were not fetched. Teaching incompatibility as a general rule is an inference, but a safe one. Google is the official example and Qdrant the corroboration. The fastembed case adds a subtler version of the same point: an fp16 export of the "same" model may produce slightly different vectors.

Multimodal embedding is the fastest-changing area. Google calls gemini-embedding-2 "the first multimodal embedding model in the Gemini API". It "maps text, images, video, audio, and documents into a unified embedding space" and supports "over 100 languages" ([Gemini docs, last updated 2026-10-09](https://ai.google.dev/gemini-api/docs/embeddings)). Voyage's `voyage-multimodal-3.5` "can vectorize interleaved text, images, and videos" through `multimodal_embed()`, and the page calls voyage-4-large "The best general-purpose and multilingual retrieval quality" ([Anthropic embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)). "Anthropic does not offer its own embedding model", and the page points to Voyage AI by MongoDB. Lesson text should date these model names or describe multimodality generically.

## Conclusion

Three layers of evidence come out of this pass, and the lesson should keep them separate. **Mathematics** guarantees that unit-length vectors rank identically under cosine, dot product and Euclidean distance, that truncation breaks unit length, and that a 2D map cannot preserve high-dimensional structure. These facts never need re-checking. **Empirical findings** come from papers measuring specific models: anisotropy, pooling effects, MRL's size savings and MTEB's "no single winner". They explain *why* engineering rules exist, but they were measured on older models or other domains, so they should be taught as tendencies, not laws. **Provider and model specifics** include BGE's 384 dimensions and prefix string, the 8,192-token limits, Voyage's `input_type`, Gemini's incompatible spaces and fastembed's missing prefix. These are what a learner's code actually touches, and they are the most likely to be wrong next year. The most useful lesson framing is therefore about checking, not memorizing: read the model's `modules.json` and pooling config, confirm normalization before choosing a FAISS index, calibrate thresholds on your own data, and re-embed whenever the model file changes.

For Pass 2, the highest-value checks are narrow. Embed a fixed test set with BAAI's fp32 weights and with fastembed's Qdrant export, and measure the vector drift and the actual v1.5 score distribution. This settles both the "quantized" question and the [0.6, 1] question with data. Check C-Pack quotes against the v5 PDF. Re-fetch the OpenAI, Gemini, Anthropic/Voyage, sbert.net and FAISS pages with a raw (non-summarizing) fetch and confirm every excerpt. Find a primary source for the distributional hypothesis, for PCA's variance property and for MTEB's eight task names before any of them appears in lesson text.

---

## Appendix A. Source register

All access dates are **2026-10-19**. "Read method" records fidelity: **raw** means downloaded files with exact string matching; **PDF-extract** means local text extraction from the PDF; **summarizer** means a fetch tool that summarizes pages, whose quoted strings still need verbatim confirmation.

| ID | Title / author | Publisher | URL read | Version or date read | Read method |
|---|---|---|---|---|---|
| W2V-A | Efficient Estimation of Word Representations in Vector Space (Mikolov et al. 2013a) | arXiv | https://arxiv.org/abs/1301.3781; https://ar5iv.labs.arxiv.org/html/1301.3781 | v3, 7 Sep 2013 (ar5iv version unstated) | raw |
| W2V-B | Distributed Representations of Words and Phrases and their Compositionality (Mikolov et al. 2013b) | arXiv | https://arxiv.org/abs/1310.4546; https://ar5iv.labs.arxiv.org/html/1310.4546 | v1, 16 Oct 2013 | raw |
| BERT | BERT (Devlin et al.) | arXiv | https://arxiv.org/abs/1810.04805; https://ar5iv.labs.arxiv.org/html/1810.04805 | v2, 24 May 2019 | raw |
| ETH | How Contextual are Contextualized Word Representations? (Ethayarajh) | arXiv; EMNLP 2019 | https://arxiv.org/abs/1909.00512; https://arxiv.org/pdf/1909.00512v1; https://ar5iv.labs.arxiv.org/html/1909.00512 | v1, 2 Sep 2019 | raw + PDF-extract |
| SBERT | Sentence-BERT (Reimers & Gurevych) | arXiv | https://arxiv.org/abs/1908.10084; https://ar5iv.labs.arxiv.org/html/1908.10084 | v1, 27 Aug 2019 | raw |
| SIMCSE | SimCSE (Gao, Yao & Chen) | arXiv | https://arxiv.org/abs/2104.08821; https://ar5iv.labs.arxiv.org/html/2104.08821 | v4, 18 May 2022 | raw |
| CPACK | C-Pack (Xiao et al.) | arXiv | https://arxiv.org/abs/2309.07597; https://ar5iv.labs.arxiv.org/html/2309.07597 | Abstract v5, 24 Sep 2024; **full text is a pre-v5 ar5iv render** (says "BGE" where v5 says "C-TEM") | raw |
| GAO | Representation Degeneration Problem in Training Natural Language Generation Models (Gao et al.) | arXiv; ICLR 2019 | https://arxiv.org/abs/1907.12009 | v1, 28 Jul 2019; abstract only | summarizer |
| MRL | Matryoshka Representation Learning (Kusupati et al.) | arXiv | https://arxiv.org/abs/2205.13147 | v4, 8 Feb 2024 (v1 26 May 2022); abstract | summarizer |
| TSNE | Visualizing Data using t-SNE (van der Maaten & Hinton) | JMLR 9(86):2579–2605, 2008 | https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf; https://www.jmlr.org/papers/v9/vandermaaten08a.html | 2008 | PDF-extract |
| UMAP | UMAP (McInnes, Healy & Melville) | arXiv | https://arxiv.org/abs/1802.03426 | v3, 18 Sep 2020 (v1 9 Feb 2018); abstract | summarizer |
| DISTILL | How to Use t-SNE Effectively (Wattenberg, Viégas & Johnson) | Distill | https://distill.pub/2016/misread-tsne/ | 2016-10-13, DOI 10.23915/distill.00002 | summarizer |
| MTEB | MTEB: Massive Text Embedding Benchmark (Muennighoff et al.) | arXiv | https://arxiv.org/abs/2210.07316 | v3, 19 Mar 2023 (v1 13 Oct 2022); abstract; venue not verified | summarizer |
| IRB | Introduction to Information Retrieval §6.3.1 "Dot products" (Manning, Raghavan & Schütze) | Cambridge UP 2008; Stanford HTML | https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html | HTML edition page dated 2009-04-07 | summarizer |
| BGE | BAAI/bge-small-en-v1.5 model card + `config.json`, `sentence_bert_config.json`, `1_Pooling/config.json`, `modules.json`, `onnx/` tree | Hugging Face | https://huggingface.co/BAAI/bge-small-en-v1.5 (and `/blob/main/<file>`); https://huggingface.co/api/models/BAAI/bge-small-en-v1.5 | Commit `5c38ec7c405ec4b44b94cc5a9bb96e735b38267a`, lastModified 2024-02-22, created 2023-09-12; v1.5 news entry dated 09/12/2023; MIT | raw (foundations); summarizer (geometry/practice re-reads) |
| QD | Qdrant/bge-small-en-v1.5-onnx-Q model card + `ort_config.json` + tree | Hugging Face | https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q | Commit `aa8f8b060edb00e03bfdd08813a2949946c8ba55`, lastModified 2026-09-24, created 2024-01-15; optimum 1.15.0; MIT | raw |
| FE | qdrant/fastembed: `fastembed/text/onnx_embedding.py`, `fastembed/text/text_embedding_base.py`, README | GitHub | https://github.com/qdrant/fastembed | `main` at `de502ca83baa2b81922cb5a46acf689f5e2c72a1` (2026-10-15); latest release v0.9.0 (2026-10-07) | raw |
| FAISS | MetricType and distances | GitHub wiki | https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances | Last edited 2024-12-03 (16 revisions) | summarizer |
| SBD-STS | Semantic Textual Similarity | sbert.net | https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html | No version shown; © 2026; homepage banner "Sentence Transformers v6.0 recently released" | summarizer |
| SBD-MOD | Modules reference | sbert.net | https://sbert.net/docs/package_reference/sentence_transformer/models.html | same | summarizer |
| SBD-API | SentenceTransformer API | sbert.net | https://sbert.net/docs/package_reference/sentence_transformer/SentenceTransformer.html | same | summarizer |
| SBD-CE | Computing Embeddings | sbert.net | https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html | same | summarizer |
| SBD-HOME | Homepage | sbert.net | https://sbert.net/ | same | summarizer |
| OAI-G | Embeddings guide | OpenAI | https://developers.openai.com/api/docs/guides/embeddings | No date shown; matched a 2026-10-18 extracted Markdown copy | summarizer (+ Markdown copy) |
| OAI-R | Create embeddings API reference | OpenAI | https://developers.openai.com/api/reference/resources/embeddings/methods/create | No date shown | summarizer |
| OAI-BLOG | New embedding models and API updates | OpenAI | https://openai.com/index/new-embedding-models-and-api-updates/ | **HTTP 403, not read** | n/a |
| GEM | Gemini API embeddings | Google | https://ai.google.dev/gemini-api/docs/embeddings | "Last updated 2026-10-09 UTC" | summarizer |
| ANT | Embeddings (Voyage AI guidance) | Anthropic | https://platform.claude.com/docs/en/build-with-claude/embeddings | No date; model blog links up to 2026-09-30 (rerank-3) | summarizer |
| QD-MIG | Migrate to a New Embedding Model | Qdrant (vendor) | https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/ | © 2026 only | summarizer |
| PC | Bring your own vectors quickstart | Pinecone | https://docs.pinecone.io/guides/get-started/quickstart/bring-your-own-vectors | **Not fetched** (search hit only) | n/a |

---

## Appendix B. Claims table

**Type:** MATH = derivable, model-independent. EMP = empirical finding measured in a paper on specific models or data. MODEL = fact about one model's files or card. PROV = provider or library documentation, provider-specific. DEF = definition or descriptive framing. INF = derived by the note-taker or this report, not stated by a source.
**Confidence** reflects source quality and how directly the excerpt states the claim.
**Re-check in Pass 2:** **Yes** = a specific concern is noted. **Spot** = live/undated page or summarizer fetch, so confirm the wording verbatim. **No** = pinned version read raw or PDF-extracted, stable.
Pipe characters inside excerpts are escaped as `\|`.

### B1. Static to contextual to sentence embeddings

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| E01 | word2vec learns continuous word vectors from very large data | DEF | W2V-A abstract | "computing continuous vector representations of words from very large data sets" | high | No |
| E02 | Trains on 1.6B words in under a day | EMP | W2V-A abstract | "less than a day to learn high quality word vectors from a 1.6 billion words data set" | high | No |
| E03 | Similar words are close; multiple degrees of similarity | EMP | W2V-A Sec. 1.1 | "not only will similar words tend to be close to each other, but that words can have multiple degrees of similarity" | high | No |
| E04 | King − Man + Woman ≈ Queen (credited to prior work [20]) | EMP | W2V-A Sec. 1.1 | "results in a vector that is closest to the vector representation of the word Queen" | high | No |
| E05 | Prior word vectors used 50–100 dimensions | EMP | W2V-A Sec. 1.1 | "a modest dimensionality of the word vectors between 50 - 100" | high | No |
| E06 | Skip-gram captures syntactic and semantic relationships | EMP | W2V-B abstract | "capture a large number of precise syntactic and semantic word relationships" | high | No |
| E07 | Madrid − Spain + France ≈ Paris | EMP | W2V-B Sec. 1 | "vec("Madrid") - vec("Spain") + vec("France") is closer to vec("Paris") than to any other word vector" | high | No |
| E08 | Word vectors ignore word order and idioms (e.g. "Air Canada") | DEF | W2V-B abstract | "their indifference to word order and their inability to represent idiomatic phrases" | high | No |
| E09 | Negative sampling introduced | DEF | W2V-B abstract | "a simple alternative to the hierarchical softmax" | high | No |
| E10 | Static embeddings: one vector per word, senses shared (framing from later work, not word2vec) | DEF | ETH | "each word had a single vector, regardless of context" | high | No |
| E11 | BERT is bidirectional in all layers | DEF | BERT abstract v2 | "on both left and right context in all layers" | high | No |
| E12 | BERT uses 30,000-token WordPiece vocabulary | MODEL | BERT Sec. 3 | "We use WordPiece embeddings (Wu et al. 2016) with a 30,000 token vocabulary" | high | No |
| E13 | [CLS] final state is the aggregate sequence representation | DEF | BERT Sec. 3 | "used as the aggregate sequence representation for classification tasks" | high | No |
| E14 | Raw [CLS] not a meaningful sentence vector without fine-tuning | EMP | BERT Sec. 3.1 fn | "not a meaningful sentence representation without fine-tuning, since it was trained with NSP" | high | No |
| E15 | Upper layers are more context-specific | EMP | ETH abstract | "upper layers of contextualizing models produce more context-specific representations" | high | No |
| E16 | Static embedding explains <5% of contextual variance | EMP | ETH abstract | "less than 5% of the variance in a word's contextualized representations can be explained by a static embedding" | high | No |
| E17 | SBERT adds pooling to BERT output | DEF | SBERT Sec. 3 | "SBERT adds a pooling operation to the output of BERT / RoBERTa to derive a fixed sized sentence embedding" | high | No |
| E18 | Pooling options CLS, MEAN, MAX | DEF | SBERT Sec. 3 | "Using the output of the CLS-token, computing the mean of all output vectors (MEAN-strategy), and computing a max-over-time" | high | No |
| E19 | SBERT default pooling is MEAN | PROV | SBERT Sec. 3 | "Our default pooling strategy is MEAN" | high | No |
| E20 | With NLI training pooling matters little (MEAN 80.78 / CLS 79.80 / MAX 79.07; STSb regression 87.44 / 86.62 / 69.92) | EMP | SBERT Table 6 | "the pooling strategy has a rather minor impact" | high | No |
| E21 | Raw BERT avg 54.81, CLS 29.19, both below avg GloVe on STS | EMP | SBERT Sec. 4.1 | "Averaging the BERT embeddings achieves an average correlation of only 54.81, and using the CLS-token output only achieves an average correlation of 29.19" | high | No |
| E22 | Out-of-the-box BERT unsuitable for cosine similarity | EMP | SBERT Sec. 8 | "rather unsuitable to be used with common similarity measures like cosine-similarity" | high | No |
| E23 | Raw BERT is decent on SentEval (not useless for every task) | EMP | SBERT | "average BERT embeddings and the BERT CLS-token output achieves decent results" | high | No |
| E24 | Cross-encoder 10,000-sentence search ~65 h vs SBERT ~5 s | EMP | SBERT abstract | "requires about 50 million inference computations (~65 hours)" | high | No |
| E25 | Contrastive learning pulls neighbours together, pushes others apart | DEF | SIMCSE Sec. 2 | "pulling semantically close neighbors together and pushing apart non-neighbors" | high | No |
| E26 | Objective: cross-entropy with in-batch negatives, temperature τ, cosine | DEF | SIMCSE Sec. 2 | "take a cross-entropy objective with in-batch negatives" | high | No |
| E27 | Unsupervised SimCSE uses dropout as noise | DEF | SIMCSE abstract v4 | "with only standard dropout used as noise" | high | No |
| E28 | Supervised SimCSE uses entailment positives, contradiction hard negatives | DEF | SIMCSE abstract | "'entailment' pairs as positives and 'contradiction' pairs as hard negatives" | high | No |
| E29 | Contrastive objective makes anisotropic space more uniform | EMP | SIMCSE abstract | "regularizes pre-trained embeddings' anisotropic space to be more uniform" | high | No |
| E30 | SimCSE BERT-base: 76.3% / 81.6% Spearman on STS | EMP | SIMCSE abstract | "76.3% and 81.6% Spearman's correlation" | high | No |

### B2. bge-small-en-v1.5 (BAAI repo commit 5c38ec7)

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| B01 | Vocabulary 30,522, BERT architecture | MODEL | BGE config.json | "vocab_size": 30522 ... "model_type": "bert" | high | No |
| B02 | Lowercasing tokenizer | MODEL | BGE sentence_bert_config.json | "do_lower_case": true | high | No |
| B03 | 384 hidden size, 12 layers, 12 heads | MODEL | BGE config.json | "hidden_size": 384 ... "num_hidden_layers": 12 | high | No |
| B04 | Max sequence length 512 | MODEL | BGE sentence_bert_config.json | "max_seq_length": 512 | high | No |
| B05 | Card MTEB row: 384 dims, 512 length, 62.17 avg of 56 tasks | MODEL | BGE card | "BAAI/bge-small-en-v1.5 \| 384 \| 512 \| 62.17" | high | No (dated score) |
| B06 | CLS pooling | MODEL | BGE 1_Pooling/config.json | "pooling_mode_cls_token": true, "pooling_mode_mean_tokens": false | high | No |
| B07 | Card prose describes CLS pooling | MODEL | BGE card | "select the last hidden state of the first token (i.e., [CLS]) as the sentence embedding" | high | No |
| B08 | Pipeline ends in a Normalize module | MODEL | BGE modules.json | "type": "sentence_transformers.models.Normalize" | high | No |
| B09 | Card code L2-normalizes | MODEL | BGE card | `torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)` | high | No |
| B10 | Normalized + dot = cosine (shown in examples, not stated as rule) | MODEL | BGE card | "encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity" | medium | No |
| B11 | Quick-start snippet itself does not show normalization | MODEL | BGE card (geometry note) | n/a (absence reported by fetch) | low | **Yes**: confirm against raw card |
| B12 | Retrieval query instruction string (with trailing space) | MODEL | BGE card | "Represent this sentence for searching relevant passages: " | high | No |
| B13 | Instruction on queries only, never passages | MODEL | BGE card | "In all cases, **no instruction** needs to be added to passages." | high | No |
| B14 | v1.5: no instruction costs only slightly; recommended for short queries | MODEL | BGE card FAQ 3 | "No instruction only has a slight degradation in retrieval performance compared with using instruction." | high | No |
| B15 | v1.5 instruction is optional for convenience | MODEL | BGE card | "So you can generate embedding without instruction in all cases for convenience." | high | Spot (summarizer) |
| B16 | v1.5 alleviates similarity distribution, improves no-instruction retrieval | MODEL | BGE card news (09/12/2023) | "alleviate the issue of the similarity distribution, and enhance its retrieval ability without instruction" | high | No |
| B17 | Temperature 0.01 → similarity roughly [0.6, 1] | EMP/MODEL | BGE card FAQ 2 | "contrastive learning with a temperature of 0.01, the similarity distribution of the current BGE model is about in the interval [0.6, 1]" | medium | **Yes**: unclear if v1 or v1.5; measure |
| B18 | Score > 0.5 does not mean similar | MODEL | BGE card FAQ 2 | "a similarity score greater than 0.5 does not indicate that the two sentences are similar" | high | No |
| B19 | Relative order matters, not absolute value | MODEL | BGE card FAQ 2 | "what matters is the relative order of the scores, not the absolute value" | high | No |
| B20 | Thresholds (e.g. 0.8/0.85/0.9) must be tuned on your data | MODEL | BGE card FAQ 2 | "select an appropriate similarity threshold based on the similarity distribution on your data" | high | No |
| B21 | Training: RetroMAE pre-training + contrastive learning on pairs | MODEL | BGE card | "We pre-train the models using retromae and train them on large-scale pairs data using contrastive learning." | high | No |
| B22 | Pre-trained (not fine-tuned) model unusable for similarity | MODEL | BGE card | "the pre-trained model cannot be used for similarity calculation directly, it needs to be fine-tuned." | high | No |
| B23 | General stage: in-batch negatives, batch up to 19,200 | EMP | CPACK (pre-v5 render) | "resort to a big batch size (as large as 19,200)" | medium | **Yes**: check v5 PDF |
| B24 | Task stage: query-side instruction + one hard negative per pair | DEF | CPACK (pre-v5 render) | "in addition to the in-batch negative samples, one hard negative sample is mined for each text pair" | medium | **Yes**: check v5 PDF |
| B25 | Paper's instruction example | DEF | CPACK | "search relevant passages for the query" | medium | **Yes**: check v5 PDF |
| B26 | English training data 200M pairs; BERT-like architecture | EMP | CPACK | "which consists of 200M text pairs" | medium | **Yes**: check v5 PDF |
| B27 | English models were MTEB SOTA at release (dated) | EMP | CPACK abstract v5 | "The English models achieve state-of-the-art performance on MTEB benchmark" | high | No (dated) |
| B28 | English bge-small ≈ 33M params (133,466,304-byte fp32 safetensors); paper's 24M is Chinese small | INF | BGE tree; CPACK | model.safetensors 133,466,304 bytes | low | **Yes**: confirm parameter count |

### B3. Qdrant ONNX export and fastembed

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| Q01 | Qdrant card calls it a quantized ONNX port | PROV | QD card | "Quantized ONNX port of BAAI/bge-small-en-v1.5 for text classification and similarity searches." | high (that card says so) | No |
| Q02 | ort_config: empty quantization, fp16, optimization level 2, GELU approximation | PROV | QD ort_config.json | "quantization": {} ... "fp16": true ... "optimization_level": 2 | high | No |
| Q03 | Export is fp16 + graph optimization, not int8 | INF | QD ort_config + sizes (66,465,124 vs 133,093,490 bytes) | n/a | medium | **Yes**: inspect ONNX tensor dtypes |
| Q04 | fastembed bge-small entry loads Qdrant's ONNX file | PROV | FE onnx_embedding.py @ de502ca | sources=ModelSource(hf="Qdrant/bge-small-en-v1.5-onnx-Q"), model_file="model_optimized.onnx" | high | No |
| Q05 | fastembed describes 512-token truncation; prefixes "not so necessary" | PROV | FE onnx_embedding.py | "512 input tokens truncation, Prefixes for queries/documents: not so necessary, 2023 year." | high | No |
| Q06 | fastembed does CLS pooling + normalize | PROV | FE onnx_embedding.py | processed_embeddings = embeddings[:, 0] ... return normalize(processed_embeddings) | high | No |
| Q07 | fastembed `query_embed` adds no BGE instruction | PROV | FE text_embedding_base.py | "This is model-specific, so that different models can have specialized implementations" | medium-high | Spot (code at one commit) |
| Q08 | README claims default model supports "query"/"passage" prefixes; uses ONNX Runtime | PROV | FE README | "supports "query" and "passage" prefixes for the input text" | high (that README says so) | **Yes**: conflicts with Q07 |
| Q09 | Output drift between fp16 export and fp32 original is unquantified | INF | none | n/a | low | **Yes**: measure |

### B4. Similarity geometry

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| G01 | Cosine is the standard document-similarity measure | DEF | IRB §6.3.1 | "the standard way of quantifying the similarity between two documents" | high | Spot (summarizer) |
| G02 | Cosine denominator length-normalizes | MATH | IRB §6.3.1 | "The effect of the denominator of Equation 24 is thus to length-normalize the vectors" | high | Spot |
| G03 | Cosine = dot product of normalized vectors | MATH | IRB §6.3.1 | "can be viewed as the dot product of the normalized versions of the two document vectors" | high | Spot |
| G04 | Length differences distort raw vector differences | MATH | IRB §6.3.1 | "two documents with very similar content can have a significant vector difference" | high | Spot |
| G05 | Unit vectors: ‖x−y‖² = 2 − 2cos, so cosine, dot and L2 rank identically | MATH | derivation; FAISS | "equivalent to using an index with METRIC_L2" | high (math) | Spot (FAISS equation formatting not seen) |
| G06 | FAISS L2 returns squared distance | PROV | FAISS | "reports squared Euclidean (L2) distance, avoiding the square root" | high | Spot |
| G07 | Inner product ≠ cosine unless normalized | MATH/PROV | FAISS | "This is not by itself cosine similarity, unless the vectors are normalized." | high | Spot |
| G08 | Cosine search = normalize then MIPS | PROV | FAISS | "By normalizing query and database vectors beforehand, the problem can be mapped back to a maximum inner product search." | high | Spot |
| G09 | Unnormalized dot product rewards longer vectors | MATH | derivation (x·y = ‖x‖‖y‖cos θ) | n/a | high | No |
| G10 | sentence-transformers default similarity is cosine; also dot, Euclidean, Manhattan | PROV | SBD-STS | "Cosine Similarity (default)" | high | Spot |
| G11 | Dot on normalized = cosine; dot is faster | PROV | SBD-STS | "Dot product on normalized embeddings is equivalent to cosine similarity" | high | Spot |
| G12 | "cosine" re-normalizes already-normalized vectors | PROV | SBD-STS | "“cosine” will re-normalize the embeddings again" | high | Spot |
| G13 | Normalize module makes unit length, on pooled embedding by default | PROV | SBD-MOD | "L2-normalizes the embeddings under one of the feature keys to have unit length." | high | Spot |
| G14 | Normalize can also act on token embeddings for ColBERT-style models | PROV | SBD-MOD | "useful for multi-vector / ColBERT-style models that score with MaxSim" | high | Spot |
| G15 | OpenAI recommends cosine; choice rarely matters | PROV | OAI-G | "We recommend cosine similarity. The choice of distance function typically doesn't matter much." | high | Spot |
| G16 | OpenAI embeddings are unit length; cosine and Euclidean rank identically | PROV | OAI-G | "Cosine similarity and Euclidean distance will result in the identical rankings" | high | Spot |
| G17 | Cosine computable faster via dot product (OpenAI) | PROV | OAI-G | "can be computed slightly faster using just a dot product" | high | Spot |
| G18 | Norm of sentence embeddings carries information | n/a | none fetched | n/a | low | **Yes**: gap |

### B5. Anisotropy and uncalibrated scores

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| A01 | Contextual representations are anisotropic, in a narrow cone | EMP | ETH §1 | "anisotropic, occupying a narrow cone in the vector space" | high | No |
| A02 | Not isotropic in any layer | EMP | ETH abstract | "are not isotropic in any layer" | high | No |
| A03 | GPT-2 last layer: random words have near-perfect cosine | EMP | ETH §1 | "two random words will on average have almost perfect cosine similarity!" | high | No |
| A04 | Isotropic baseline: random-pair cosine ≈ 0 | MATH | ETH §4.1 | "the average cosine similarity between uniformly randomly sampled words would be 0" | high | No |
| A05 | GPT-2 random-pair cosine ~0.6 in layers 2–8, rising sharply 8–12 | EMP | ETH §4.1 | "roughly 0.6 in layers 2 through 8 but increases exponentially from layers 8 through 12" | high | No |
| A06 | Ethayarajh adjusts metrics for anisotropy | EMP | ETH §3.4 heading | "Adjusting for Anisotropy" | high | No |
| A07 | LM word embeddings degenerate into a narrow cone | EMP | GAO abstract | "most of the learnt word embeddings tend to degenerate and be distributed into a narrow cone" | high | Spot (summarizer; setting wording) |
| A08 | Named "representation degeneration problem"; regularizer proposed | DEF | GAO abstract | "which we call the representation degeneration problem" | high | Spot |
| A09 | Narrow-cone findings concern 2019 word/token reps, not tested on BGE | INF | ETH, GAO scope | n/a | high | No |
| A10 | Cosine of 0.7 ≠ "70% similar"; thresholds don't transfer between models | INF | from B17–B20, A01–A05 | n/a | high | No |

### B6. Dimensionality and Matryoshka

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| D01 | MRL: nested coarse-to-fine representations as accurate as separate ones | EMP | MRL abstract | "MRL learns coarse-to-fine representations that are at least as accurate and rich" | high | Spot |
| D02 | MRL encodes multiple granularities | DEF | MRL abstract | "encodes information at different granularities" | high | Spot |
| D03 | Up to 14× smaller on ImageNet-1K at equal accuracy (image, not text) | EMP | MRL abstract | "up to 14x smaller embedding size for ImageNet-1K classification at the same level of accuracy" | high | Spot |
| D04 | Up to 2% gain on long-tail few-shot | EMP | MRL abstract | "up to 2% accuracy improvements for long-tail few-shot classification" | high | Spot |
| D05 | OpenAI defaults 1536 (3-small) / 3072 (3-large) | PROV | OAI-G | "the length of the embedding vector is `1536` for `text-embedding-3-small` or `3072` for `text-embedding-3-large`" | high | Spot (dated) |
| D06 | OpenAI v3 trained with shortening technique (links to MRL; "Matryoshka" word not confirmed) | PROV | OAI-G | "Both of our new embedding models were trained with a technique that allows developers to trade-off performance and cost" | high | Spot |
| D07 | Shortening = removing trailing numbers | PROV | OAI-G | "remove some numbers from the end of the sequence" | high | Spot |
| D08 | 3-large at 256 beats ada-002 at 1536 on MTEB | EMP (vendor) | OAI-G | "can be shortened to a size of 256 while still outperforming an unshortened `text-embedding-ada-002` embedding" | medium | **Yes**: vendor claim; blog table 403 |
| D09 | Prefer `dimensions` parameter | PROV | OAI-G | "using the `dimensions` parameter when creating the embedding is the suggested approach" | high | Spot |
| D10 | Manual truncation needs re-normalization | MATH/PROV | OAI-G | "you need to be sure to normalize the dimensions of the embedding" | high | Spot |
| D11 | Shortening trades accuracy for size | PROV | OAI-G | "trading off some accuracy in exchange for the smaller vector size" | high | Spot |
| D12 | Larger embeddings cost more compute, memory, storage | PROV | OAI-G | "generally costs more and consumes more compute, memory and storage than using smaller embeddings." | medium | **Yes**: fragment |
| D13 | `dimensions` only on text-embedding-3 and later | PROV | OAI-R | "Only supported in `text-embedding-3` and later models." | high | Spot |
| D14 | Gemini recommends 768/1536/3072 | PROV | GEM | "We recommend using 768, 1536, or 3072 output dimensions." | high | Spot (dated) |
| D15 | gemini-embedding-2 auto-renormalizes; 001 needs manual normalization below 3072 | PROV | GEM | "`gemini-embedding-2` introduces automatic renormalization for non-default dimensions." | high (001 part medium, paraphrased) | Spot |
| D16 | Voyage: keep leading dims then re-normalize | PROV | ANT | "truncate them by keeping the leading subset of dimensions, then normalize them again." | high | Spot |
| D17 | Voyage int8/binary cut storage 4×/32× | PROV | ANT | "reducing storage, memory, and costs by 4x and 32x, respectively." | high | Spot |
| D18 | sentence-transformers `truncate_dim` and `normalize_embeddings` | PROV | SBD-API | "The dimension to truncate sentence embeddings to." | high | Spot |
| D19 | Prefix of a unit vector has norm ≤ 1, so truncation breaks dot = cosine | MATH | derivation | n/a | high | No |
| D20 | Truncating a model not trained for it can degrade quality; no source says bge-small uses MRL | INF | MRL premise | n/a | medium | No |

### B7. Visualization

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| V01 | PCA/MDS are linear and keep dissimilar points apart | DEF | TSNE §1 | "linear techniques that focus on keeping the low-dimensional representations of dissimilar datapoints far apart" | high | No |
| V02 | On nonlinear manifolds, keeping similar points close matters more | DEF | TSNE §1 | "it is usually more important to keep the low-dimensional representations of very similar datapoints close together" | high | No |
| V03 | t-SNE reveals structure at many scales (authors' claim) | EMP | TSNE abstract page | "better than existing techniques at creating a single map that reveals structure at many different scales" | high | Spot |
| V04 | t-SNE weaknesses: general use unclear, local nature, no global optimum guarantee | DEF | TSNE §6.2 | "(1) it is unclear how t-SNE performs on general dimensionality reduction tasks, (2) the relatively local nature of t-SNE" | high | No |
| V05 | 2D/3D cannot fully represent high-dim structure | MATH | TSNE §6.2 | "it is by definition impossible to fully represent the structure of intrinsically high-dimensional data in two or three dimensions" | high | No |
| V06 | t-SNE runs differ from random starts | EMP | TSNE §6.2 | "may be different each time t-SNE is run from an initial random configuration of map points" | high | No |
| V07 | UMAP arguably preserves more global structure, faster | EMP (authors) | UMAP abstract | "arguably preserves more of the global structure with superior run time performance" | medium | Spot |
| V08 | UMAP built on Riemannian geometry and algebraic topology | DEF | UMAP abstract | "constructed from a theoretical framework based in Riemannian geometry and algebraic topology" | high | Spot |
| V09 | t-SNE cluster sizes not meaningful | EMP | DISTILL | "you cannot see relative sizes of clusters in a t-SNE plot" | high | Spot |
| V10 | Inter-cluster distances may mean nothing | EMP | DISTILL | "distances between well-separated clusters in a t-SNE plot may mean nothing" | high | Spot |
| V11 | Random noise can form clumps | EMP | DISTILL | "Recognizing these clumps as random noise is an important part of reading t-SNE plots." | high | Spot |
| V12 | Perplexity strongly shapes output | EMP | DISTILL | "The perplexity value has a complex effect on the resulting pictures." | high | Spot |
| V13 | No fixed step count gives stability | EMP | DISTILL | "there's no fixed number of steps that yields a stable result" | high | Spot |
| V14 | Compare plots at multiple perplexities | PROV (advice) | DISTILL | "analyzing multiple plots with different perplexities" | high | Spot |
| V15 | PCA preserves maximal variance among linear 2D projections | MATH | none fetched | n/a | low (unsourced here) | **Yes**: cite textbook |
| V16 | Anisotropy may dominate the top PC | INF | none | n/a | low | **Yes** |

### B8. Benchmarks

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| M01 | MTEB: 8 tasks, 58 datasets, 112 languages | EMP | MTEB abstract | "MTEB spans 8 embedding tasks covering a total of 58 datasets and 112 languages" | high | Spot (dated: v3 2023) |
| M02 | 33 models benchmarked | EMP | MTEB abstract | "Through the benchmarking of 33 models on MTEB" | high | Spot |
| M03 | No method dominates all tasks | EMP | MTEB abstract | "We find that no particular text embedding method dominates across all tasks." | high | Spot |
| M04 | Names of the 8 task types | n/a | not confirmed | n/a | low | **Yes**: read paper body |
| M05 | EACL 2023 venue | n/a | not confirmed | n/a | low | **Yes** |

### B9. Practice: use cases, asymmetry, limits, re-embedding, multimodal

| ID | Claim | Type | Source | Verbatim excerpt (≤25 words) | Conf. | Re-check |
|---|---|---|---|---|---|---|
| P01 | OpenAI uses: search, clustering, recommendations, anomaly detection, diversity measurement, classification | PROV | OAI-G | "Embeddings are commonly used for:" | high | Spot |
| P02 | OpenAI classification by most similar label | PROV | OAI-G | "where text strings are classified by their most similar label" | high | Spot |
| P03 | Gemini uses: retrieval, reranking, anomaly detection, classification, clustering | PROV | GEM | "Text embeddings are crucial for a variety of common AI use cases, such as:" | medium | **Yes**: list items paraphrased |
| P04 | RAG is a common use case | PROV | GEM | "Building Retrieval Augmented Generation (RAG) systems is a common use case for AI products." | high | Spot |
| P05 | sentence-transformers: semantic search, STS, paraphrase mining | PROV | SBD-HOME | "including semantic search, semantic textual similarity, and paraphrase mining." | high | Spot |
| P06 | Anthropic frames search, recommendations, anomaly detection | PROV | ANT | "tasks like search, recommendations, and anomaly detection" | high | Spot |
| P07 | Anthropic has no embedding model of its own; points to Voyage AI by MongoDB | PROV | ANT | "Anthropic does not offer its own embedding model." | high | Spot (dated) |
| P08 | Voyage: always set input_type for retrieval | PROV | ANT | "Do not omit `input_type` or set `input_type=None`." | high | Spot |
| P09 | Voyage input_type prepends prompts | PROV | ANT | "special prompts are prepended to the input text prior to embedding." | high | Spot |
| P10 | Voyage query prompt | PROV | ANT | "Represent the query for retrieving supporting documents: " | high | Spot |
| P11 | Voyage document prompt | PROV | ANT | "Represent the document for retrieval: " | high | Spot |
| P12 | Voyage: asymmetry improves retrieval quality | PROV | ANT | "can create better dense vector representations for retrieval, which can lead to better retrieval quality." | high | Spot |
| P13 | Gemini task_type on gemini-embedding-001 (8 values listed) | PROV | GEM | "For `gemini-embedding-001`, you can specify the `task_type` in the `embedContent` method." | high | Spot (dated) |
| P14 | Gemini task_type not available on gemini-embedding-2 | PROV | GEM | "You cannot use the `task_type` field for the `gemini-embedding-2` model." | high | Spot (dated) |
| P15 | Gemini RETRIEVAL_DOCUMENT / SEMANTIC_SIMILARITY descriptions | PROV | GEM | "Embeddings optimized for document search." | high | Spot |
| P16 | sentence-transformers encode_query / encode_document | PROV | SBD-API | "Computes embeddings specifically optimized for query representation." | high | Spot |
| P17 | sentence-transformers prompts are prepended | PROV | SBD-API | "The prompt text will be prepended before any text during inference." | high | Spot |
| P18 | No OpenAI query/document parameter found | INF | OAI-G, OAI-R | n/a (absence) | low | **Yes** |
| P19 | OpenAI 8192-token per-input limit | PROV | OAI-R | "The input must not exceed the max input tokens for the model (8192 tokens for all embedding models)" | high | Spot (dated) |
| P20 | OpenAI 2,048 inputs per array (worded "dimensions"); 300,000 tokens per request | PROV | OAI-R | "maximum of 300,000 tokens summed across all inputs in a single request." | high | Spot |
| P21 | OpenAI guide table: 3-small 62,500 / 62.3% / 8192 | PROV | OAI-G | "\| text-embedding-3-small \| 62,500 \| 62.3% \| 8192 \|" | medium | **Yes**: column labels (pages per dollar?) unconfirmed |
| P22 | OpenAI overflow behaviour (error vs truncate) | n/a | not confirmed | n/a | low | **Yes** |
| P23 | Gemini 8192-token limit, silently truncated | PROV | GEM | "The system silently truncates inputs that exceed this limit." | high | Spot (dated) |
| P24 | Voyage-4 family 32,000 tokens; voyage-law-2 16,000; voyage-context-4 120,000 with auto-chunking | PROV | ANT | "when you set `enable_auto_chunking` to `true`" | high | Spot (dated) |
| P25 | sentence-transformers truncates to max_seq_length | PROV | SBD-CE | "Longer texts will be truncated to the first `model.max_seq_length` tokens" | high | Spot |
| P26 | max_seq_length capped by the transformer | PROV | SBD-CE | "You cannot increase the length higher than what is maximally supported by the respective transformer model." | high | Spot |
| P27 | 512 BERT tokens ≈ 300–400 English words | PROV | SBD-CE | "A common value for BERT-based models are 512 tokens, which corresponds to about 300-400 words (for English)." | high | Spot |
| P28 | Models trained on short text may embed long text poorly | PROV | SBD-CE | "if a model was trained on short texts, the representations for long texts might not be that good." | high | Spot |
| P29 | all-MiniLM-L6-v2 max length 256 | MODEL | SBD-CE | "Max Sequence Length: 256" | high | Spot |
| P30 | gemini-embedding-001 and -2 spaces incompatible | PROV | GEM | "The embedding spaces between `gemini-embedding-001` and `gemini-embedding-2` are **incompatible**." | high | Spot (dated) |
| P31 | Upgrading requires re-embedding all data | PROV | GEM | "you must re-embed all of your existing data." | high | Spot |
| P32 | Switching models requires re-embedding (vendor) | PROV | QD-MIG | "Switching models requires re-embedding all vectors in your collection, which can take time." | high | Spot |
| P33 | New collection must match new model's size and similarity function | PROV | QD-MIG | "compatible with the new model in terms of vector size and similarity function" | high | Spot |
| P34 | Dual-write migration pattern | PROV | QD-MIG | n/a (search summary only) | low | **Yes** |
| P35 | Re-embedding on model change is a general rule | INF | P30–P33 | n/a | medium-high | No |
| P36 | gemini-embedding-2 is the first multimodal Gemini embedding model | PROV | GEM | "the first multimodal embedding model in the Gemini API." | high (as of 2026-10-09) | Spot (dated) |
| P37 | One space for text, images, video, audio, documents | PROV | GEM | "maps text, images, video, audio, and documents into a unified embedding space" | high | Spot |
| P38 | 100+ languages | PROV | GEM | "over 100 languages" | high | Spot |
| P39 | voyage-multimodal-3.5 handles interleaved text, images, video via multimodal_embed() | PROV | ANT | "can vectorize interleaved text, images, and videos" | high | Spot (dated) |
| P40 | voyage-4-large best general-purpose and multilingual retrieval (vendor) | PROV | ANT | "The best general-purpose and multilingual retrieval quality." | high (that page says so) | Spot (dated) |

---

## Appendix C. Known conflicts and inconsistencies

| # | Where | Conflict | How to handle in the lesson |
|---|---|---|---|
| C1 | BERT paper vs BGE config.json | Paper: "30,000 token vocabulary"; file: `"vocab_size": 30522` | Quote 30,522 for bge-small and say BERT's paper rounds it |
| C2 | BGE card FAQ 2 vs v1.5 news | "[0.6, 1]" describes "the current BGE model", next to advice that v1.5 "alleviates" the issue. Notes disagree on confidence (geometry: high; foundations: medium) | Present the range as a v1 characteristic. Teach "uncalibrated, use rank" without a number until measured on v1.5 |
| C3 | Qdrant card vs ort_config.json | Card says "Quantized"; config has empty `quantization`, `fp16: true`; file is half the fp32 size | Describe it as an fp16 optimized ONNX export pending Pass 2; avoid "int8" |
| C4 | fastembed README vs code | README: default model "supports "query" and "passage" prefixes"; code: `query_embed` = `embed`, no prefix; registry: prefixes "not so necessary" | Tell learners to prepend BGE's instruction manually if they want it |
| C5 | CPACK abstract v5 vs ar5iv full text | v5 renames training method "C-TEM"; ar5iv text says "BGE" (older version) | Re-quote from v5 PDF before publishing |
| C6 | CPACK sizes vs English model file | Paper's 24M small is Chinese; English safetensors implies ~33M | Do not quote 24M for bge-small-en; label 33M as an estimate |
| C7 | BGE card snippets | Some snippets normalize explicitly; quick-start reportedly does not. `modules.json` normalizes anyway under sentence-transformers | If using raw transformers code, normalize explicitly |
| C8 | BGE card footnote vs FAQ 3 vs fastembed | Footnote "suggest[s]" instruction for query→passage search; FAQ says optional in v1.5 with slight loss; fastembed says "not so necessary" | Consistent once read together: optional, helps short queries, test both |
| C9 | OpenAI API reference wording | "any array must be 2048 dimensions or less" means 2,048 inputs, not vector dimensions | Paraphrase as "2,048 inputs per request" |
| C10 | OpenAI "distance doesn't matter much" vs FAISS/sbert caveats | True only because OpenAI vectors are unit length | Teach the condition, not the slogan |
| C11 | BGE vs Voyage instruction strings | "Represent this sentence for searching relevant passages: " vs "Represent the query for retrieving supporting documents: " | Prefixes are model-specific and must not be swapped between models |

---

## Appendix D. Classification: mathematical, empirical, provider- or model-specific, dated

### D1. Mathematical (stable; no re-check beyond confirming wording)

Cosine equals the dot product of normalized vectors (G02, G03). Unit vectors satisfy ‖x−y‖² = 2 − 2cos, so cosine, dot product and (squared) Euclidean distance rank identically (G05). Inner product is not cosine without normalization (G07), and an unnormalized dot product rewards vector length (G09). A truncated unit vector has norm ≤ 1, which forces re-normalization (D10, D19). An isotropic distribution gives random-pair cosine ≈ 0 (A04). Two or three dimensions cannot fully represent intrinsically high-dimensional structure (V05). PCA's maximal-variance property (V15) is mathematical but still unsourced.

### D2. Empirical (measured on specific models or data; teach as findings, with scope)

word2vec similarity and analogies (E02–E07). Contextual variance <5% and layer trends (E15, E16). Raw BERT's poor STS and pooling insensitivity after fine-tuning (E14, E20–E24). SimCSE's uniformity effect and scores (E29, E30). Anisotropy and degeneration in ELMo/BERT/GPT-2 and LM word embeddings (A01–A07). BGE's compressed similarity range (B17). C-Pack training scale (B23, B26). MRL savings, measured on image classification (D01–D04). OpenAI's 256-vs-ada-002 claim, a vendor measurement (D08). t-SNE behaviour (V03, V06, V09–V13). UMAP's hedged global-structure claim (V07). MTEB's no-single-winner finding (M01–M03).

### D3. Provider- or model-specific

**bge-small-en-v1.5 only:** 30,522 vocab, lowercasing, 12 layers, 384 dims, 512 tokens, CLS pooling, Normalize, instruction string, threshold advice (B01–B22). **Qdrant/fastembed only:** fp16 export, CLS+normalize code, no query prefix (Q01–Q09). **OpenAI:** unit length, 1536/3072 defaults, `dimensions`, 8,192/2,048/300,000 limits (G15–G17, D05–D13, P19–P21). **Gemini:** task_type on 001 only, 8,192 with silent truncation, 768/1536/3072, auto-renormalization on 2, incompatible spaces, multimodality (P13–P15, P23, P30–P31, P36–P38, D14–D15). **Voyage via Anthropic:** input_type prompts, 32k/16k/120k contexts, int8/binary, multimodal model (P07–P12, P24, P39–P40, D16–D17). **sentence-transformers:** default cosine, Normalize module, encode_query/encode_document, truncation (G10–G14, P16–P17, P25–P29). **FAISS:** squared L2, normalize-then-MIPS (G06–G08). **SBERT paper:** MEAN default (E19).

### D4. Dated items

| Item | Source | Date or version stamp | Why it is dated |
|---|---|---|---|
| gemini-embedding-001 / -2 names, task_type support, incompatibility, multimodality, 100+ languages, 768/1536/3072 | GEM | Last updated 2026-10-09 UTC | Model lineup changes; -2 is new |
| Voyage model names (voyage-4 family, voyage-law-2, voyage-context-4, voyage-multimodal-3.5), context lengths, "best" claim | ANT | No stamp; blog links to 2026-09-30 | Vendor lineup changes fast |
| "Anthropic does not offer its own embedding model" | ANT | No stamp | Product policy can change |
| OpenAI 1536/3072 defaults, 8,192 limit, 300k/request, 62,500 / 62.3% table | OAI-G, OAI-R | No stamp | Limits and price columns change |
| 3-large@256 > ada-002 | OAI-G | No stamp; blog 403 | Comparison against a legacy model |
| BGE MTEB 62.17 / "state-of-the-art" | BGE, CPACK | Card 2024-02-22; v5 2024-09-24 | Leaderboard has moved since |
| fastembed registry and query_embed behaviour | FE | main de502ca, 2026-10-15; v0.9.0 | Code can change in any release |
| Qdrant ONNX repo | QD | aa8f8b0, modified 2026-09-24 (changed files not checked) | Recently modified; recheck what changed |
| MTEB 8 / 58 / 112 / 33 | MTEB | v3, 2023-03-19 | Benchmark has since expanded (MMTEB etc. out of scope) |
| sbert.net docs | SBD-* | v6.0 banner, © 2026 | API surface (encode_query, truncate_dim) is recent |
| FAISS wiki | FAISS | Last edited 2024-12-03 | Wiki pages change |

---

## Appendix E. Gaps and items needing independent verification

| # | Gap | Effect on the lesson | Suggested Pass 2 action |
|---|---|---|---|
| E1 | Whether "[0.6, 1]" applies to v1.5; no v1.5 interval given | Cannot state a numeric score range for the lesson's model | Embed random and related pairs with bge-small-en-v1.5; report the distribution |
| E2 | Meaning of "Quantized" for the Qdrant export; accuracy delta vs fp32 unquantified | Cannot say how close fastembed vectors are to BAAI's | Inspect ONNX initializer dtypes; compare cosine between fp32 and Qdrant vectors on a fixed set |
| E3 | fastembed README vs code on prefixes | Learners may assume a prefix is applied | Re-read README and docs site (qdrant.github.io/fastembed, not fetched); open an issue if inconsistent |
| E4 | C-Pack quotes from a pre-v5 render | Wording may differ | Re-quote from https://arxiv.org/pdf/2309.07597v5 |
| E5 | English bge-small parameter count not stated | 33M is an estimate | Count parameters from safetensors header |
| E6 | Distributional hypothesis not sourced | Cannot attribute to Harris/Firth | Fetch a primary source before using the term |
| E7 | No source on what vector norm encodes | Norm discussion must stay inferential | Candidates (unverified): Schakel & Wilson 2015 (arXiv 1508.02297); sbert docs on dot-product models |
| E8 | No source that some models are trained for unnormalized dot product | Cannot warn about this with a citation | Fetch sbert.net pretrained-models page (msmarco "dot" models) |
| E9 | PCA maximal-variance property unsourced | V15 unsupported | Cite a textbook |
| E10 | MTEB task names and venue unconfirmed | M04, M05 unsupported | Read MTEB paper body |
| E11 | OpenAI launch blog returned HTTP 403; "Matryoshka" not confirmed on any OpenAI page | Dimension/performance table unread | Human browser check |
| E12 | OpenAI overflow behaviour and query/document parameter not confirmed | P18, P22 open | Read API reference error docs; small free-tier test only with permission |
| E13 | Gemini replacement for task_type on gemini-embedding-2; per-modality limits | Asymmetry guidance for Gemini-2 incomplete | Re-fetch Gemini page raw |
| E14 | Voyage `truncation` parameter (on MongoDB docs) not read | Voyage overflow behaviour unknown | Fetch Voyage/MongoDB docs |
| E15 | Pinecone and Weaviate docs not fetched | Re-embedding rule rests on Google + Qdrant | Fetch Pinecone "bring your own vectors" page |
| E16 | Qdrant dual-write pattern seen only in search summary | P34 low confidence | Re-fetch tutorial raw |
| E17 | All practice-note and most geometry-note web excerpts came through a summarizing fetch tool | Wording may not be exact | Raw re-fetch (curl or browser) and string-match every "Spot" excerpt |
| E18 | Gao et al. body not read | A07 setting wording unverified | Read PDF body |
| E19 | UMAP's global-structure claim has no independent check | V07 stays "arguably" | Optional |
| E20 | Ethayarajh/Gao narrow-cone results not tested on BGE | A09: cannot claim bge-small is anisotropic in the 2019 sense | Measure mean random-pair cosine in E1's experiment |
