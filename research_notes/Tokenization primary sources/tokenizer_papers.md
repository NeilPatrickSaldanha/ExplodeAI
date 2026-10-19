# Subword tokenization primary sources: BPE, byte-level BPE, SentencePiece / unigram

Access date for every source below: **2026-10-18**. I downloaded each PDF with `curl` into a fresh scratch directory and extracted the text with `uv run --with pypdf python -I extract.py <pdf>`, with the script kept outside the download directory. No excerpt below came from a summarising fetch tool, so nothing is marked [WF]. The one non-PDF source (the Gage mirror) was fetched with `curl` as raw HTML, and the tags were stripped locally.

**Excerpt conventions.** Excerpts are verbatim from the PDF text layer, with three mechanical normalisations: (1) a hyphen that only splits a word across a line break is removed ("re-places" becomes "replaces"); (2) typographic ligatures are expanded ("ﬁ" becomes "fi"); (3) footnote markers are dropped. Real hyphens such as "end-of-word" and "open-vocabulary" are kept. Each excerpt is 25 words or fewer.

**Source register (exact URLs read, versions, file hashes)**

| ID | Paper | URL read (full text) | Version read | Notes |
|---|---|---|---|---|
| SEN | Sennrich, Haddow & Birch, "Neural Machine Translation of Rare Words with Subword Units" | https://arxiv.org/pdf/1508.07909v5 (PDF); version history from https://arxiv.org/abs/1508.07909; cross-checked against https://aclanthology.org/P16-1162.pdf | arXiv **v5, Fri 10 Jun 2016** (v1 31 Aug 2015, v2 27 Nov 2015, v3 17 Mar 2016, v4 3 Jun 2016). ACL PDF: *Proceedings of the 54th Annual Meeting of the ACL*, pp. 1715–1725, Berlin, 7–12 Aug 2016 | Text of ACL PDF = arXiv v5 apart from the header and page numbers (checked with a diff). Page mapping: arXiv PDF page n = ACL proceedings page 1714+n. sha256 v5 f4e5a6bb…6401; ACL ebf5b384…d9ce |
| GPT2 | Radford, Wu, Child, Luan, Amodei & Sutskever, "Language Models are Unsupervised Multitask Learners" | https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf | Undated OpenAI PDF, 24 pages. PDF metadata CreationDate 2019-02-14T23:21:39Z; HTTP Last-Modified Fri, 25 Sep 2020 22:57:58 GMT; 582,775 bytes; sha256 d9d852e2…4f4e | The PDF metadata "Subject" says "Proceedings of the International Conference on Machine Learning 2019". That is a leftover from the ICML LaTeX template. Do not cite the paper as an ICML paper. |
| SP | Kudo & Richardson, "SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing" | https://arxiv.org/pdf/1808.06226v1; history from https://arxiv.org/abs/1808.06226; cross-checked against https://aclanthology.org/D18-2012.pdf | arXiv **v1, Sun 19 Aug 2018** (only version). ACL PDF: *Proceedings of EMNLP 2018 (System Demonstrations)*, pp. 66–71, Brussels, 31 Oct–4 Nov 2018 | Spot-checked passages (§3.1 lossless tokenization, U+2581) read the same in both. PDF page n = proceedings page 65+n. sha256 v1 8a81eb8b…838d; ACL cf056aa0…9924 |
| KUDO | Kudo, "Subword Regularization: Improving Neural Network Translation Models with Multiple Subword Candidates" | https://arxiv.org/pdf/1804.10959v1; history from https://arxiv.org/abs/1804.10959 | arXiv **v1, Sun 29 Apr 2018** (only version) | I did not read the ACL 2018 proceedings version. sha256 61af976a…e44f |
| GAGE | Philip Gage, "A New Algorithm for Data Compression", *C Users Journal* 12(2), Feb 1994 | https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm | HTML transcription of the February 1994 CUJ article, hosted on a third-party archive site | **Not publisher-hosted.** A Dr. Dobb's (publisher-successor) copy, https://drdobbs.com/a-new-algorithm-for-data-compression/184402829, appeared in search results, but `curl` could not resolve drdobbs.com from this machine. Treat GAGE excerpts as medium confidence. |

## Q1. Sennrich et al. 2016: how BPE for word segmentation works, what it solved, Gage credit, test-time application, merge counts

### Takeaway
Sennrich et al. adapt Gage's 1994 byte-pair compression algorithm to word segmentation:
- Start from characters, with an end-of-word symbol "·" (written `</w>` in the Algorithm 1 code).
- Repeatedly count symbol pairs and merge the most frequent pair, never across word boundaries.
- The final vocabulary size equals the initial vocabulary plus the number of merges, and the number of merges is "the only hyperparameter."
- At test time, the learned merge operations are applied to character-split words.

The motivation is open-vocabulary NMT for rare and unknown words without a back-off dictionary. The paper reports 59,500 merges for BPE and 89,500 for joint BPE.

### Cited Findings
**Problem and motivation**
- Abstract, p.1 (ACL p.1715): "Neural machine translation (NMT) models typically operate with a fixed vocabulary, but translation is an open-vocabulary problem." — [SEN arXiv v5](https://arxiv.org/pdf/1508.07909v5)
- Abstract, p.1: "making the NMT model capable of open-vocabulary translation by encoding rare and unknown words as sequences of subword units." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §1 Introduction, p.1: "The vocabulary of neural models is typically limited to 30 000–50 000 words" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- Abstract, p.1, headline result: "improve over a back-off dictionary baseline for the WMT 15 translation tasks English→German and English→Russian by up to 1.1 and 1.3 BLEU" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)

**Credit to Gage 1994**
- §1 contributions, p.2 (ACL p.1716): "We adapt byte pair encoding (BPE) (Gage, 1994), a compression algorithm, to the task of word segmentation." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §3.2, p.3 (ACL p.1717): "a simple data compression technique that iteratively replaces the most frequent pair of bytes in a sequence with a single, unused byte" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- References, p.10: "Philip Gage. 1994. A New Algorithm for Data Compression. C Users J., 12(2):23–38, February." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §1 contributions, p.2: "BPE allows for the representation of an open vocabulary through a fixed-size vocabulary of variable-length character sequences" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)

**The algorithm (§3.2, p.3, ACL p.1717)**
- "Instead of merging frequent pairs of bytes, we merge characters or character sequences." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "we initialize the symbol vocabulary with the character vocabulary, and represent each word as a sequence of characters, plus a special end-of-word symbol ‘·’" — [SEN v5](https://arxiv.org/pdf/1508.07909v5). In the text layer the symbol is U+00B7 MIDDLE DOT.
- On the end-of-word symbol's purpose: "which allows us to restore the original tokenization after translation." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "We iteratively count all symbol pairs and replace each occurrence of the most frequent pair (‘A’, ‘B’) with a new symbol ‘AB’." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "Each merge operation produces a new symbol which represents a character n-gram." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "Frequent character n-grams (or whole words) are eventually merged into a single symbol, thus BPE requires no shortlist." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "The final symbol vocabulary size is equal to the size of the initial vocabulary, plus the number of merge operations" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- The same sentence continues: "the latter is the only hyperparameter of the algorithm." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "For efficiency, we do not consider pairs that cross word boundaries." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "The algorithm can thus be run on the dictionary extracted from a text, with each word being weighted by its frequency." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)

**Algorithm 1 and Figure 1 (p.4, ACL p.1718)**
- The heading is "Algorithm 1 Learn BPE operations". Its Python defines `get_stats(vocab)`, which counts `pairs[symbols[i],symbols[i+1]] += freq`, and `merge_vocab(pair, v_in)`. The main loop is `for i in range(num_merges): pairs = get_stats(vocab); best = max(pairs, key=pairs.get); vocab = merge_vocab(best, vocab)`. — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- The toy vocabulary in the code uses `</w>` as the end-of-word marker. Verbatim code line: "vocab = {'l o w </w>' : 5, 'l o w e r </w>' : 2," — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- Figure 1 caption: "BPE merge operations learned from dictionary {‘low’, ‘lowest’, ‘newer’, ‘wider’}." Figure body: "r · → r·", "l o → lo", "lo w → low", "e r· → er·". — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "In practice, we increase efficiency by indexing all pairs, and updating data structures incrementally." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)

**Applying merges to new text (p.4)**
- "At test time, we first split words into sequences of characters, then apply the learned operations to merge the characters into larger, known symbols." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- "In our example, the OOV ‘lower’ would be segmented into ‘low er·’." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- Footnote 3: "The only symbols that will be unknown at test time are unknown characters". The footnote also covers symbols fully merged away, such as ‘safeguar’, and a fix by "recursively reversing specific merges". — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §4.1, p.5: "the learned merge operations can be applied to the test set to obtain a segmentation with no unknown symbols." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)

**Joint BPE and merge counts**
- p.4: "learning the encoding on the union of the two vocabularies (which we call joint BPE)" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §4.1, p.5 (ACL p.1719): "Table 1 shows BPE with 59 500 merge operations, and joint BPE with 89 500 operations." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- Table 2, p.6: system names BPE-60k and BPE-J90k, with source/target network vocabularies "60 000 60 000" and "90 000 90 000". — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- Conclusion §6, p.9: "our choice of vocabulary size is somewhat arbitrary, and mainly motivated by comparison to prior work." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- Footnote 14, p.9: source code at https://github.com/rsennrich/subword-nmt — [SEN v5](https://arxiv.org/pdf/1508.07909v5)

**Gage 1994 itself (GAGE mirror, article body; the HTML has no page numbers)**
- "a simple general-purpose data compression algorithm, called Byte Pair Encoding (BPE)" — [GAGE mirror](https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm)
- "finding the most frequently occurring pairs of adjacent bytes in the data and replacing all instances of the pair with a byte" — [GAGE mirror](https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm)
- The replacement is "a byte that was not in the original data" — [GAGE mirror](https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm)
- "The algorithm repeats this process until no further compression is possible" — [GAGE mirror](https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm)
- "The algorithm writes out the table of pair substitutions before the packed data." — [GAGE mirror](https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm)

### Inferences
- The figure and the code in Sennrich use different toy data. The Figure 1 caption names the dictionary {low, lowest, newer, wider}. The Algorithm 1 code vocabulary is low×5, lower×2, newest×6, widest×3. The figure's merges (r·, er·) fit the caption's words, not the code's. A lesson that runs Algorithm 1 should not expect it to reproduce Figure 1.
- The paper uses two spellings for the end-of-word marker: "·" in the prose and figures, `</w>` in the code. The lesson can present them as the same thing, but should say which one it shows.
- "Merge the most frequent pair" uses frequency-weighted counts over a word-frequency dictionary (`+= freq`), not over raw running text.
- Merges are applied in the order they were learned. This is implied, not stated: Algorithm 1 learns an ordered list (it prints `best` each iteration), and the paper says to "apply the learned operations". No sentence says "in order".
- Why BPE is open-vocabulary: the base vocabulary is all characters and every merge is reversible, so any word built from known characters can be segmented. Footnote 3 states the exceptions.

### Gaps
- No sentence in Sennrich says merges must be applied "in the same order they were learned". The ordering follows from Algorithm 1 and the phrase "learned operations", but I found no verbatim statement.
- Gage 1994 could not be read on a publisher-hosted page. drdobbs.com did not resolve via DNS from this machine. The jacobfilipp.com copy is a third-party transcription. I did not verify page 23–38 locators or the original print layout.
- Sennrich does not give a number for "number of merges" alone versus final vocabulary for the 59,500 setting. Table 1 reports 63,000 types for BPE and 82,000 for joint BPE, and the paper explains (p.5) that network vocabularies are slightly smaller because "we did not include infrequent subword units".

## Q2. Radford et al. 2019 (GPT-2) §2.2 Input Representation: byte-level BPE

### Takeaway
GPT-2 runs BPE over UTF-8 bytes, which needs a base vocabulary of 256, instead of Unicode code points, which would need over 130,000 base symbols. To stop vocabulary slots being wasted on variants like "dog." "dog!" "dog?", BPE is prevented from merging across character categories, with an exception for spaces. §2.3 gives the vocabulary (50,257) and the context size (1024 tokens).

### Cited Findings
All §2.2 excerpts are on PDF p.4, §2.2 "Input Representation" — [GPT2 PDF](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf).

**Design goal and the problem with plain byte-level models**
- "A general language model (LM) should be able to compute the probability of (and also generate) any string."
- "Current large scale LMs include pre-processing steps such as lowercasing, tokenization, and out-of-vocabulary tokens which restrict the space of model-able strings."
- "current byte-level LMs are not competitive with word-level LMs on large scale datasets such as the One Billion Word Benchmark"

**BPE as a middle ground**
- "Byte Pair Encoding (BPE) (Sennrich et al., 2015) is a practical middle ground between character and word level language modeling". The paper cites the 2015 arXiv date of Sennrich et al.
- BPE "effectively interpolates between word level inputs for frequent symbol sequences and character level inputs for infrequent symbol sequences."

**Why bytes and not Unicode code points**
- "Despite its name, reference BPE implementations often operate on Unicode code points and not byte sequences."
- "This would result in a base vocabulary of over 130,000 before any multi-symbol tokens are added."
- "This is prohibitively large compared to the 32,000 to 64,000 token vocabularies often used with BPE."
- "In contrast, a byte-level version of BPE only requires a base vocabulary of size 256."

**Merge restriction across character categories**
- "directly applying BPE to the byte sequence results in sub-optimal merges due to BPE using a greedy frequency based heuristic"
- "We observed BPE including many versions of common words like dog since they occur in many variations such as dog. dog! dog?"
- "To avoid this, we prevent BPE from merging across character categories for any byte sequence."
- "We add an exception for spaces which significantly improves the compression efficiency while adding only minimal fragmentation of words across multiple vocab tokens."
- "Since our approach can assign a probability to any Unicode string". The sentence continues that this allows evaluation on any dataset regardless of tokenization.

**Model details and evaluation**
- §2.3 "Model", p.4: "The vocabulary is expanded to 50,257. We also increase the context size from 512 to 1024 tokens and a larger batchsize of 512 is used."
- §3.1, p.4: "Since our model operates on a byte level and does not require lossy pre-processing or tokenization, we can evaluate it on any language model benchmark."

### Inferences
- The 50,257 figure and the 1024-token context are in §2.3 "Model", not §2.2. The lesson should cite §2.3 for them.
- "Character categories" plus the space exception explains why GPT-2-style tokens often begin with a leading space (" dog"). That reading comes from the space exception, not from an explicit statement in the paper.

### Gaps
- The paper does not break 50,257 down (for example 256 byte tokens + 50,000 merges + 1 special end-of-text token). Any such breakdown would need OpenAI's released encoder files or code, which were out of scope and not read.
- The paper does not define "character categories" (for example Unicode general categories or a specific regex). The pre-tokenisation regex lives in OpenAI's released code, which I did not read.
- No arXiv version exists. The PDF is undated on its face; the dates in the register come from PDF metadata and HTTP headers.

## Q3. Kudo & Richardson 2018 (SentencePiece): raw-sentence training, whitespace as a symbol, lossless tokenization, BPE and unigram, fixed final vocabulary size

### Takeaway
SentencePiece trains subword models directly from raw sentences, with no pre-tokenisation, which makes it language independent. It escapes whitespace as the meta symbol U+2581 and treats it as a normal symbol, so Decode(Encode(Normalize(text))) = Normalize(text) ("lossless tokenization"). It implements both BPE and the unigram LM. It is configured by final vocabulary size rather than by number of merges, because merge count only makes sense for BPE.

### Cited Findings
All page numbers refer to the arXiv v1 PDF; add 65 for the EMNLP proceedings page.

**Raw sentences and language independence**
- Abstract, p.1: "While existing subword segmentation tools assume that the input is pre-tokenized into word sequences, SentencePiece can train subword models directly from raw sentences" — [SP arXiv v1](https://arxiv.org/pdf/1808.06226v1)
- Abstract, p.1, continued: "which allows us to make a purely end-to-end and language independent system." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- §1, p.1, on Moses-style tools: "these tools are mainly designed for European languages where words are segmented with whitespaces." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- §1, p.1: "SentencePiece enables building a purely end-to-end system that does not depend on any language-specific processing." — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**Predetermined vocabulary and the two algorithms**
- §1, p.1: "mainly for Neural Network-based text generation systems where the size of vocabulary is predetermined prior to the Neural model training" — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- §1, p.1: "SentencePiece implements two subword segmentation algorithms, byte-pair-encoding (BPE) (Sennrich et al., 2016) and unigram language model (Kudo, 2018)" — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**System components and command-line example**
- §2, p.2: "SentencePiece comprises four main components: Normalizer, Trainer, Encoder, and Decoder." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- Figure 1, p.2: `spm_train --vocab_size=1000`; encoding "Hello world." gives "_He ll o _world ." and ids "151 88 21 887 6"; both decode back to "Hello world." — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**Lossless tokenization (§3.1, p.2)**
- The problem with ordinary tokenisers: "The information that no space exists between “world” and “.” is not kept in the tokenized sequence." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- "SentencePiece implements the Decoder as an inverse operation of Encoder, i.e., Decode(Encode(Normalize(text))) = Normalize(text)." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- "We call this design lossless tokenization, in which all the information to reproduce the normalized text is preserved in the encoder’s output." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- "Even whitespace is handled as a normal symbol." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- "SentencePiece first escapes the whitespace with a meta symbol _ (U+2581), and tokenizes the input into an arbitrary subword sequence" — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- Worked example, p.2: "Tokenized: [Hello] [_wor] [ld] [.]". Detokenisation code: `detok = ''.join(tokens).replace('_', ' ')` — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**Contrast with subword-nmt (§3.1)**
- p.2: subword-nmt "uses @@ as an intra-word boundary marker." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- p.3: "it is not possible to encode consecutive whitespaces with this representation." — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**Training speed (§3.2, p.3)**
- "Such pre-tokenization was introduced for an efficient subword training (Sennrich et al., 2016)." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- "SentencePiece adopts an O(N log(N)) algorithm in which the merged symbols are managed by a binary heap (priority queue)." The naive cost is stated as O(N^2). — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**Vocabulary size instead of merge count (§3.3, p.3)**
- "While subword-nmt specifies the number of merge operations, SentencePiece specifies the final size of vocabulary" — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- "as the number of merge operations is a BPE specific parameter and can not be applicable to other segmentation algorithms" — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- "SentencePiece reserves vocabulary ids for special meta symbols, e.g., unknown symbol (<unk>), BOS (<s>), EOS (</s>) and padding (<pad>)." — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**Normalisation (§3.4, p.3)**
- "By default, SentencePiece normalizes the input text with the Unicode NFKC normalization." — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**Subword sampling (Figure 6, p.5)**
- `SampleEncodeAsPieces('New York',-1, 0.1)` gives different outputs on repeated calls, for example "[’_’, ’New’, ’_York’]" and "[’_’, ’N’, ’e’, ’w’, ’_York’]". — [SP v1](https://arxiv.org/pdf/1808.06226v1)

**Experiments**
- Table 1, p.5, ja→en: Word model (80k/80k) BLEU 28.24; SentencePiece (8k shared) 29.55. — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- Table 2 caption, p.6: "We found that BPE and unigram language models show almost comparable performance." — [SP v1](https://arxiv.org/pdf/1808.06226v1)
- p.6: "The segmentation speed of SentencePiece is about 380 times faster than that of subword-nmt in this setting." The setting is raw Japanese, without pre-tokenisation. — [SP v1](https://arxiv.org/pdf/1808.06226v1)

### Inferences
- In the PDF text layer the meta symbol is an ASCII underscore "_", even though the paper names it U+2581 (LOWER ONE EIGHTH BLOCK, "▁"). Both the arXiv and ACL text layers show "_". I could not confirm the glyph as rendered on the page. For the lesson, cite the codepoint the paper names ("U+2581") rather than the extracted glyph.
- "Lossless" is defined relative to normalised text (NFKC by default), not the raw input. A lesson should not claim that SentencePiece round-trips arbitrary raw bytes exactly.

### Gaps
- The paper does not use the word "lossless" for byte-exact round-trips of unnormalised input. Claims about that would need the SentencePiece repository documentation, which I did not read.

## Q4. Kudo 2018 (Subword Regularization): the unigram LM tokenizer, multiple segmentations, BPE as deterministic and greedy

### Takeaway
Kudo shows that one vocabulary admits many segmentations of the same sentence (for example "Hello World"). He proposes a unigram language-model segmenter:
- Each subword is assumed independent, and the best segmentation is found with Viterbi.
- Subword probabilities are estimated by EM.
- The vocabulary is pruned from a large seed down to the target size by dropping low-loss subwords, always keeping single characters.

This segmenter can sample segmentations, whereas BPE "is based on a greedy and deterministic symbol replacement."

### Cited Findings
All excerpts from [KUDO arXiv v1](https://arxiv.org/pdf/1804.10959v1).

**Ambiguity of segmentation**
- Abstract, p.1: "subword segmentation is potentially ambiguous and multiple segmentations are possible even with the same vocabulary."
- Abstract, p.1: "we propose a new subword segmentation algorithm based on a unigram language model."
- Table 1, p.1, caption: "Multiple subword sequences encoding the same sentence “Hello World”". Rows include "Hell/o/ world" → ids "13586 137 255" and "H/ello/ world" → "320 7363 255". The text layer drops the space meta-symbol in this table.
- §1, p.1: "BPE encodes a sentence into a unique subword sequence. However, a sentence can be represented in multiple subword sequences even with the same vocabulary."
- §1, p.1: "While these sequences encode the same input “Hello World”, NMT handles them as completely different inputs."

**BPE described (§3.1, p.3)**
- "BPE first splits the whole sentence into individual characters."
- "The most frequent adjacent pairs of characters are then consecutively merged until reaching a desired vocabulary size."
- "Subword segmentation is performed by applying the same merge operations to the test sentence."
- "Frequent substrings will be joined early, resulting in common words remaining as one unique symbol."
- "BPE is based on a greedy and deterministic symbol replacement, which can not provide multiple segmentations with probabilities."
- Footnote 1, p.3: "Strictly speaking, wordpiece model (Schuster and Nakajima, 2012) is different from BPE." Footnote 2 adds that WordPiece "uses a likelihood instead of frequency."

**The unigram LM model (§3.2, pp.3–4)**
- p.3: "The unigram language model makes an assumption that each subword occurs independently"
- p.3, Eq. 6–7: P(x) = ∏ p(xi) over a "pre-determined vocabulary" V; "x∗ is obtained with the Viterbi algorithm (Viterbi, 1967)."
- p.3: "subword occurrence probabilities p(xi) are estimated via the EM algorithm"

**Vocabulary pruning loop (p.3)**
- "Heuristically make a reasonably big seed vocabulary from the training corpus."
- "Repeat the following steps until |V| reaches a desired vocabulary size."
- "Sort the symbols by lossi and keep top η % of subwords (η is 80, for example)."
- "we always keep the subwords consisting of a single character to avoid out-of-vocabulary."

**Word boundaries and character fallback (p.4)**
- "Similar to (Sennrich et al., 2016), we do not consider subwords that cross word boundaries."
- Unigram segmentation "can be seen as a probabilsitic mixture of characters, subwords and word segmentations." The spelling "probabilsitic" is the paper's own typo.

**Sampling (§3.3, p.4)**
- "Subword regularization samples one subword segmentation from the distribution P (x|X) for each parameter update."

**BPE versus unigram (§3.4, p.4)**
- "BPE was originally introduced in the data compression literature (Gage, 1994)."
- BPE "incrementally finds a set of symbols such that the total number of symbols for encoding the text is minimized"
- "the unigram language model is reformulated as an entropy encoder that minimizes the total code length for the text."
- "the unigram language model is more flexible as it is based on a probabilistic language model and can output multiple segmentations with their probabilities"

**Results (§5.2, p.6)**
- "BPE and unigram language model without subword regularization (l = 1) show almost comparable BLEU scores."
- "subword regularization (l >1) boosted BLEU scores quite impressively (+1 to 2 points) in all language pairs except for WMT14 (en→cs) dataset."

### Inferences
- Lesson contrast. BPE builds its vocabulary bottom-up (characters to merges) and segments deterministically. The unigram LM works top-down, pruning from a large seed to the target size, and segments probabilistically: Viterbi gives the best path, and sampling gives alternatives.
- Both Kudo papers treat a "desired"/"predetermined" vocabulary size as the stopping criterion. That matches SentencePiece's `--vocab_size`, as opposed to subword-nmt's merge count.

### Gaps
- I did not read the ACL 2018 proceedings version of this paper (P18-1007), so locators are arXiv v1 only.

## Q5. Statements on the trade-off between vocabulary size and sequence length

### Takeaway
Sennrich states the trade-off explicitly: neural models want small vocabularies, but "an increase in text length reduces efficiency". Their Table 1 quantifies it on German: characters give 550 M tokens and 3,000 types; unsegmented words give 100 M tokens and 1.75 M types; BPE gives 112 M tokens and 63 K types. Kudo calls BPE's strength balancing "the vocabulary size and the step size (the number of tokens required to encode the sentence)." GPT-2 frames it as a middle ground between character and word level.

### Cited Findings
**Sennrich (arXiv v5)**
- §3.1, p.3: "there are strong incentives to minimize the vocabulary size of neural models to increase time and space efficiency" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §3.1, p.3: "we also want a compact representation of the text itself, since an increase in text length reduces efficiency" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §3.1, p.3, same sentence continued: "and increases the distances over which neural models need to pass information." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §3.1, p.3: "A simple method to manipulate the trade-off between vocabulary size and text size is to use shortlists of unsegmented words" — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §3.1, p.3: BPE "lets us learn a vocabulary that provides a good compression rate of the text." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §4.1, p.5: "Character n-grams allow for different trade-offs between sequence length (# tokens) and vocabulary size (# types), depending on the choice of n." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- §4.1, p.5: "the more compact representation of BPE allows for shorter sequences, and that the attention model operates on variable-length units." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)
- Footnote 8, p.5: "The time complexity of encoder-decoder architectures is at least linear to sequence length, and oversplitting harms efficiency." — [SEN v5](https://arxiv.org/pdf/1508.07909v5)

**Sennrich Table 1, p.6 (ACL p.1720), German training corpus**

| segmentation | # tokens | # types | # UNK |
|---|---|---|---|
| none | 100 m | 1 750 000 | 1079 |
| characters | 550 m | 3000 | 0 |
| character bigrams | 306 m | 20 000 | 34 |
| character trigrams | 214 m | 120 000 | 59 |
| BPE | 112 m | 63 000 | 0 |
| BPE (joint) | 111 m | 82 000 | 32 |

Source: [SEN v5](https://arxiv.org/pdf/1508.07909v5)

**Kudo (arXiv v1)**
- §3.1, p.3: "it can effectively balance the vocabulary size and the step size (the number of tokens required to encode the sentence)" — [KUDO v1](https://arxiv.org/pdf/1804.10959v1)
- §3.1, p.3: "only with a small fixed size of vocabulary (usually 16k to 32k), the number of required symbols to encode a sentence will not significantly increase" — [KUDO v1](https://arxiv.org/pdf/1804.10959v1)
- §1, p.1: "BPE segmentation gives a good balance between the vocabulary size and the decoding efficiency" — [KUDO v1](https://arxiv.org/pdf/1804.10959v1)
- §1, p.1: "limiting vocabulary size increases the amount of unknown words, which makes the translation inaccurate especially in an open vocabulary setting." — [KUDO v1](https://arxiv.org/pdf/1804.10959v1)

**GPT-2**
- §2.2, p.4: BPE is "a practical middle ground between character and word level language modeling" — [GPT2 PDF](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)

### Inferences
- From Sennrich Table 1: characters are 5.5× longer than words (550 m vs 100 m tokens). BPE is only 12% longer than words (112 m vs 100 m), with a vocabulary about 28× smaller (63 K vs 1.75 M types) and 0 UNK. This is my arithmetic on the table, not a sentence in the paper, and it suits a slider visual.
- "Bigger vocabulary means fewer tokens per text" is directionally supported by Table 1: going from characters to trigrams to words, types rise and tokens fall. No paper states it as a general law. The lesson should phrase it as an observed trend in these experiments.

### Gaps
- None of these papers measures LLM context-window cost (tokens per context) as a function of vocabulary size. GPT-2 gives the vocabulary size (50,257) and context size (1024) but does not discuss the trade-off between them.

## Claims table

| # | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Confidence | Notes |
|---|---|---|---|---|---|---|
| 1 | Word-level NMT has a fixed vocabulary, but translation is open-vocabulary | SEN arXiv v5 (10 Jun 2016), https://arxiv.org/pdf/1508.07909v5 | Abstract, p.1 (ACL p.1715) | "Neural machine translation (NMT) models typically operate with a fixed vocabulary, but translation is an open-vocabulary problem." | high | |
| 2 | Sennrich encodes rare/unknown words as sequences of subword units | SEN v5 | Abstract, p.1 | "making the NMT model capable of open-vocabulary translation by encoding rare and unknown words as sequences of subword units." | high | |
| 3 | NMT vocabularies were typically 30k–50k words | SEN v5 | §1, p.1 | "The vocabulary of neural models is typically limited to 30 000–50 000 words" | high | |
| 4 | Sennrich credits Gage 1994 for BPE as a compression algorithm | SEN v5 | §1 contributions, p.2 (ACL p.1716) | "We adapt byte pair encoding (BPE) (Gage, 1994), a compression algorithm, to the task of word segmentation." | high | Bibliography p.10: C Users J., 12(2):23–38, February |
| 5 | Original BPE replaces the most frequent byte pair with an unused byte | SEN v5 | §3.2, p.3 | "a simple data compression technique that iteratively replaces the most frequent pair of bytes in a sequence with a single, unused byte" | high | |
| 6 | Gage's own description of BPE compression | GAGE (third-party mirror), https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm | Article body, ¶3 (no page numbers) | "finding the most frequently occurring pairs of adjacent bytes in the data and replacing all instances of the pair with a byte" | medium | Not publisher-hosted; drdobbs.com unreachable |
| 7 | Sennrich merges characters or character sequences, not bytes | SEN v5 | §3.2, p.3 | "Instead of merging frequent pairs of bytes, we merge characters or character sequences." | high | |
| 8 | Training starts from characters plus an end-of-word symbol | SEN v5 | §3.2, p.3 | "we initialize the symbol vocabulary with the character vocabulary, and represent each word as a sequence of characters, plus a special end-of-word symbol ‘·’" | high | Text uses ‘·’ (U+00B7); Algorithm 1 code uses `</w>` |
| 9 | The end-of-word symbol lets the original tokenization be restored | SEN v5 | §3.2, p.3 | "which allows us to restore the original tokenization after translation." | high | |
| 10 | Count all pairs, merge the most frequent, repeat | SEN v5 | §3.2, p.3 | "We iteratively count all symbol pairs and replace each occurrence of the most frequent pair (‘A’, ‘B’) with a new symbol ‘AB’." | high | |
| 11 | Final vocabulary = initial vocabulary + number of merges | SEN v5 | §3.2, p.3 | "The final symbol vocabulary size is equal to the size of the initial vocabulary, plus the number of merge operations" | high | |
| 12 | Number of merges is the only hyperparameter | SEN v5 | §3.2, p.3 | "the latter is the only hyperparameter of the algorithm." | high | "the latter" = number of merge operations |
| 13 | No merges across word boundaries | SEN v5 | §3.2, p.3 | "For efficiency, we do not consider pairs that cross word boundaries." | high | |
| 14 | BPE learning runs on a frequency-weighted word dictionary | SEN v5 | §3.2, p.3 | "The algorithm can thus be run on the dictionary extracted from a text, with each word being weighted by its frequency." | high | |
| 15 | Algorithm 1 is a minimal Python BPE learner | SEN v5 | Algorithm 1, p.4 (ACL p.1718) | "vocab = {'l o w </w>' : 5, 'l o w e r </w>' : 2," | high | Code line; the Figure 1 caption uses a different toy dictionary (see Inferences) |
| 16 | Toy merges learned in Figure 1 | SEN v5 | Fig. 1, p.4 | "r · → r·" / "l o → lo" / "lo w → low" / "e r· → er·" | high | Caption dictionary {low, lowest, newer, wider} |
| 17 | At test time, split into characters and apply the learned merges | SEN v5 | §3.2, p.4 | "At test time, we first split words into sequences of characters, then apply the learned operations to merge the characters into larger, known symbols." | high | "In learned order" is implied, not stated |
| 18 | An unseen word is segmented from known units | SEN v5 | §3.2, p.4 | "In our example, the OOV ‘lower’ would be segmented into ‘low er·’." | high | |
| 19 | Merge counts used: 59,500 (BPE) and 89,500 (joint BPE) | SEN v5 | §4.1, p.5 (ACL p.1719) | "Table 1 shows BPE with 59 500 merge operations, and joint BPE with 89 500 operations." | high | Systems named BPE-60k / BPE-J90k (Table 2, p.6) |
| 20 | Joint BPE is learned on the union of source and target vocabularies | SEN v5 | §3.2, p.4 | "learning the encoding on the union of the two vocabularies (which we call joint BPE)" | high | |
| 21 | Longer text reduces efficiency (trade-off) | SEN v5 | §3.1, p.3 | "we also want a compact representation of the text itself, since an increase in text length reduces efficiency" | high | |
| 22 | Explicit vocabulary-size vs text-size trade-off | SEN v5 | §3.1, p.3 | "A simple method to manipulate the trade-off between vocabulary size and text size is to use shortlists of unsegmented words" | high | |
| 23 | Sequence length vs vocabulary size trade-off | SEN v5 | §4.1, p.5 | "Character n-grams allow for different trade-offs between sequence length (# tokens) and vocabulary size (# types), depending on the choice of n." | high | |
| 24 | BPE gives shorter sequences than characters | SEN v5 | §4.1, p.5 | "the more compact representation of BPE allows for shorter sequences, and that the attention model operates on variable-length units." | high | |
| 25 | German corpus stats: chars 550 m tokens / 3000 types; words 100 m / 1.75 M; BPE 112 m / 63 K | SEN v5 | Table 1, p.6 (ACL p.1720) | "BPE 112 m 63 000 0" | high | Table row as extracted (tokens, types, UNK) |
| 26 | Vocabulary size choice was somewhat arbitrary | SEN v5 | §6, p.9 | "our choice of vocabulary size is somewhat arbitrary, and mainly motivated by comparison to prior work." | high | |
| 27 | GPT-2 goal: an LM should model any string | GPT2 PDF (created 2019-02-14), cdn URL | §2.2, p.4 | "A general language model (LM) should be able to compute the probability of (and also generate) any string." | high | |
| 28 | BPE is a middle ground between character and word level | GPT2 | §2.2, p.4 | "Byte Pair Encoding (BPE) (Sennrich et al., 2015) is a practical middle ground between character and word level language modeling" | high | |
| 29 | Reference BPE implementations operate on Unicode code points | GPT2 | §2.2, p.4 | "Despite its name, reference BPE implementations often operate on Unicode code points and not byte sequences." | high | |
| 30 | Code-point BPE would need a base vocabulary over 130,000 | GPT2 | §2.2, p.4 | "This would result in a base vocabulary of over 130,000 before any multi-symbol tokens are added." | high | |
| 31 | Typical BPE vocabularies are 32k–64k | GPT2 | §2.2, p.4 | "This is prohibitively large compared to the 32,000 to 64,000 token vocabularies often used with BPE." | high | |
| 32 | Byte-level BPE needs only 256 base symbols | GPT2 | §2.2, p.4 | "In contrast, a byte-level version of BPE only requires a base vocabulary of size 256." | high | |
| 33 | Naive byte-level BPE wastes slots on "dog." "dog!" "dog?" | GPT2 | §2.2, p.4 | "We observed BPE including many versions of common words like dog since they occur in many variations such as dog. dog! dog?" | high | |
| 34 | GPT-2 blocks merges across character categories | GPT2 | §2.2, p.4 | "To avoid this, we prevent BPE from merging across character categories for any byte sequence." | high | Categories not defined in the paper |
| 35 | Exception for spaces | GPT2 | §2.2, p.4 | "We add an exception for spaces which significantly improves the compression efficiency while adding only minimal fragmentation of words across multiple vocab tokens." | high | |
| 36 | GPT-2 vocabulary 50,257; context 1024 tokens | GPT2 | §2.3 "Model", p.4 | "The vocabulary is expanded to 50,257. We also increase the context size from 512 to 1024 tokens and a larger batchsize of 512 is used." | high | In §2.3, not §2.2; breakdown of 50,257 not given |
| 37 | Byte-level input lets GPT-2 be evaluated on any benchmark | GPT2 | §3.1, p.4 | "Since our model operates on a byte level and does not require lossy pre-processing or tokenization, we can evaluate it on any language model benchmark." | high | |
| 38 | SentencePiece trains directly from raw sentences | SP arXiv v1 (19 Aug 2018), https://arxiv.org/pdf/1808.06226v1 | Abstract, p.1 (EMNLP p.66) | "While existing subword segmentation tools assume that the input is pre-tokenized into word sequences, SentencePiece can train subword models directly from raw sentences" | high | |
| 39 | SentencePiece is language independent | SP v1 | §1, p.1 | "SentencePiece enables building a purely end-to-end system that does not depend on any language-specific processing." | high | |
| 40 | SentencePiece implements BPE and unigram LM | SP v1 | §1, p.1 | "SentencePiece implements two subword segmentation algorithms, byte-pair-encoding (BPE) (Sennrich et al., 2016) and unigram language model (Kudo, 2018)" | high | |
| 41 | Vocabulary size is predetermined before model training | SP v1 | §1, p.1 | "mainly for Neural Network-based text generation systems where the size of vocabulary is predetermined prior to the Neural model training" | high | |
| 42 | Decode(Encode(Normalize(text))) = Normalize(text) | SP v1 | §3.1, p.2 (EMNLP p.67) | "SentencePiece implements the Decoder as an inverse operation of Encoder, i.e., Decode(Encode(Normalize(text))) = Normalize(text)." | high | Lossless relative to normalised (NFKC) text |
| 43 | Definition of lossless tokenization | SP v1 | §3.1, p.2 | "We call this design lossless tokenization, in which all the information to reproduce the normalized text is preserved in the encoder’s output." | high | |
| 44 | Whitespace is treated as a normal symbol, escaped as U+2581 | SP v1 | §3.1, p.2 | "SentencePiece first escapes the whitespace with a meta symbol _ (U+2581), and tokenizes the input into an arbitrary subword sequence" | high | Text layer shows ASCII "_"; cite codepoint U+2581 ("▁") |
| 45 | subword-nmt's @@ cannot encode consecutive whitespace | SP v1 | §3.1, p.3 | "it is not possible to encode consecutive whitespaces with this representation." | high | |
| 46 | SentencePiece sets final vocabulary size, not number of merges | SP v1 | §3.3, p.3 | "While subword-nmt specifies the number of merge operations, SentencePiece specifies the final size of vocabulary" | high | |
| 47 | Why: merge count is BPE-specific | SP v1 | §3.3, p.3 | "as the number of merge operations is a BPE specific parameter and can not be applicable to other segmentation algorithms" | high | |
| 48 | Default normalisation is NFKC | SP v1 | §3.4, p.3 | "By default, SentencePiece normalizes the input text with the Unicode NFKC normalization." | high | |
| 49 | Example: "Hello world." → "_He ll o _world ." → ids 151 88 21 887 6 | SP v1 | Fig. 1, p.2 | "_He ll o _world ." | high | vocab_size=1000 toy model |
| 50 | BPE and unigram perform almost comparably (speed table) | SP v1 | Table 2 caption, p.6 | "We found that BPE and unigram language models show almost comparable performance." | high | Refers to training/segmentation performance |
| 51 | A sentence can be segmented in multiple ways with the same vocabulary | KUDO arXiv v1 (29 Apr 2018), https://arxiv.org/pdf/1804.10959v1 | Abstract, p.1 | "subword segmentation is potentially ambiguous and multiple segmentations are possible even with the same vocabulary." | high | Table 1 "Hello World" example |
| 52 | BPE gives a unique segmentation | KUDO v1 | §1, p.1 | "BPE encodes a sentence into a unique subword sequence. However, a sentence can be represented in multiple subword sequences even with the same vocabulary." | high | |
| 53 | BPE is greedy and deterministic | KUDO v1 | §3.1, p.3 | "BPE is based on a greedy and deterministic symbol replacement, which can not provide multiple segmentations with probabilities." | high | |
| 54 | BPE segments test text with the same merge operations | KUDO v1 | §3.1, p.3 | "Subword segmentation is performed by applying the same merge operations to the test sentence." | high | |
| 55 | BPE balances vocabulary size and tokens per sentence | KUDO v1 | §3.1, p.3 | "it can effectively balance the vocabulary size and the step size (the number of tokens required to encode the sentence)" | high | |
| 56 | Unigram LM assumes independent subwords | KUDO v1 | §3.2, p.3 | "The unigram language model makes an assumption that each subword occurs independently" | high | Best path via Viterbi; p(x) via EM |
| 57 | Unigram training prunes a big seed vocabulary to the target size | KUDO v1 | §3.2, p.3 | "Repeat the following steps until |V| reaches a desired vocabulary size." | high | Seed: "reasonably big seed vocabulary"; keep top η% (e.g. 80) |
| 58 | Single characters are always kept | KUDO v1 | §3.2, p.3 | "we always keep the subwords consisting of a single character to avoid out-of-vocabulary." | high | |
| 59 | Unigram LM can output multiple segmentations with probabilities | KUDO v1 | §3.4, p.4 | "the unigram language model is more flexible as it is based on a probabilistic language model and can output multiple segmentations with their probabilities" | high | |
| 60 | Kudo also credits BPE to the compression literature | KUDO v1 | §3.4, p.4 | "BPE was originally introduced in the data compression literature (Gage, 1994)." | high | |
| 61 | Subword regularization improves BLEU by +1 to 2 in most pairs | KUDO v1 | §5.2, p.6 | "subword regularization (l >1) boosted BLEU scores quite impressively (+1 to 2 points) in all language pairs except for WMT14 (en→cs) dataset." | high | In the text layer a page footnote (fn 11, KyTea URL) is interleaved between "2" and "points)"; the sentence itself is contiguous on the page |
