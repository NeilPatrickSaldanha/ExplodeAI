# Tokenizer libraries: Hugging Face `tokenizers` / Transformers / LLM course, and OpenAI `tiktoken`

Access date for every source below: **2026-10-18**. Collection method: raw files were downloaded with `curl` from raw.githubusercontent.com, pinned to a commit. The live HF pages were also downloaded and converted to plain text with Python, and every HF excerpt below was checked by exact string match against that live text. No summarising fetch tool was used, so **no excerpt is marked [WF]**. Excerpts are verbatim and 25 words or fewer. Markdown/MDX markup (backticks, `**bold**`, link brackets) is dropped where the rendered page drops it, and typos in the source are kept as written.

### Source register (version stamps)

| ID | URL read (rendered) | Raw source pinned | Version / last-updated stamp |
|---|---|---|---|
| HF-PIPE | https://huggingface.co/docs/tokenizers/pipeline | https://raw.githubusercontent.com/huggingface/tokenizers/a73dbb3f65b259d6b199c2670f6d23e9e2d22eca/docs/source-doc-builder/pipeline.mdx | The live page defaults to doc version **v1.0.0-rc.2** (version selector lists main, v1.0.0-rc.2, v0.23.3, ...). File last changed in commit 3fe1b852de47 (2026-09-21). Repo HEAD a73dbb3 (2026-10-15). Latest stable PyPI `tokenizers` is 0.23.3 (2026-10-09). |
| HF-COMP | https://huggingface.co/docs/tokenizers/components | same repo/commit, `components.mdx` | Same as HF-PIPE (v1.0.0-rc.2 live; file commit 3fe1b852de47). |
| HF-QT | https://huggingface.co/docs/tokenizers/quicktour | same repo/commit, `quicktour.mdx` | Same as HF-PIPE. |
| TF-SUM | https://huggingface.co/docs/transformers/tokenizer_summary | https://raw.githubusercontent.com/huggingface/transformers/d88946453f945ecdc7bc5cf4427084a5d6c215fe/docs/source/en/tokenizer_summary.md | Live page defaults to Transformers docs **v5.20.1**. File last changed in commit 83eb94c1febf (2026-02-17). **The page at this URL is now titled "Tokenization algorithms", not "Summary of the tokenizers".** |
| LLM-6.5 | https://huggingface.co/learn/llm-course/chapter6/5 | https://raw.githubusercontent.com/huggingface/course/8b893f0ede6c781045692a7f892f25a0c92b4805/chapters/en/chapter6/5.mdx | Live page at access date (title "Byte-Pair Encoding tokenization"). File last changed in commit e05c3b637f0a (2025-09-29). |
| TT-README | https://github.com/openai/tiktoken (README.md) | https://raw.githubusercontent.com/openai/tiktoken/4e71bbe0c078468e00fefbf94b39849389f346e5/README.md | Git tag **0.14.0** = commit 4e71bbe0c078 (also repo HEAD, 2026-08-17). PyPI `tiktoken` **0.14.0** (uploaded 2026-08-17). README last changed in commit bb5805d0a3ee (2025-02-14). |
| TT-MODEL | https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py | same commit, `tiktoken/model.py` | Tag 0.14.0. File last changed in commit 212b893ba940 (2026-08-17). |
| TT-CORE | https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py | same commit, `tiktoken/core.py` | Tag 0.14.0. File last changed in commit fa8b65d062fb (2026-05-15). |
| TT-EDU | https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py | same commit, `tiktoken/_educational.py` | Tag 0.14.0. File last changed in commit 05e66e8db7ef (2024-10-03). |
| TT-EXT | https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py | same commit, `tiktoken_ext/openai_public.py` | Tag 0.14.0. |
| CB | https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb | https://raw.githubusercontent.com/openai/openai-cookbook/5bd6cb40b6b84b69b2032d810610aa85064102df/examples/How_to_count_tokens_with_tiktoken.ipynb | Repo HEAD 5bd6cb40b6b8 (2026-10-09). Notebook last changed in commit db3144982aa2 (2024-10-08). |
| OBS | Local run (not a source) | `uv run --no-project --with tiktoken==0.14.0 --with tokenizers==0.23.3 python -I obs.py` | tiktoken 0.14.0, tokenizers 0.23.3. tiktoken encoding files come from OpenAI's public blob store (`openaipublic.blob.core.windows.net`, URLs listed in TT-EXT). That store is free and needs no API key, though the files may have been served from a local cache. No API keys were used and no paid calls were made. |

**Version caveat for HF tokenizers docs.** At the access date the default live docs are the v1 release candidate. Pipeline, Components and Quicktour each open with this banner: "Not supported by the rc0 bindings yet. rc0 loads a `tokenizer.json` and encodes and decodes with it" [HF-PIPE / HF-COMP / HF-QT, top-of-page Tip]. The conceptual text cited below is unchanged on the live pages. Only the build-and-train code examples are flagged as not yet runnable on the rc bindings.

---

## Q1. HF `tokenizers` pipeline: stages, what each does, trainable model, ByteLevel, offsets, special tokens, decoders

### Takeaway
The HF docs name four encode stages: normalization → pre-tokenization → model → post-processing. Decoding is the reverse step. Only the model (BPE, Unigram, WordLevel or WordPiece) is trained and mandatory. Post-processing adds special tokens. The library tracks alignment and offsets through normalization. The ByteLevel pre-tokenizer remaps bytes to visible characters (e.g. "Ġmy"), so the base alphabet is 256 symbols and there is no need for an unknown token.

### Cited Findings
- **Stages.** "When calling Tokenizer.encode or Tokenizer.encode_batch, the input text(s) go through the following pipeline:" The list that follows is `normalization`, `pre-tokenization`, `model`, `post-processing` — [HF-PIPE, "The tokenization pipeline" intro](https://huggingface.co/docs/tokenizers/pipeline)
- **Normalization.** "Normalization is, in a nutshell, a set of operations you apply to a raw string to make it less random or "cleaner"." — [HF-PIPE, "Normalization"](https://huggingface.co/docs/tokenizers/pipeline)
- **Normalization examples.** "Common operations include stripping whitespace, removing accented characters or lowercasing all text." — [HF-PIPE, "Normalization"](https://huggingface.co/docs/tokenizers/pipeline)
- **Changing the normalizer needs retraining.** "Of course, if you change the way a tokenizer applies normalization, you should probably retrain it from scratch afterward." — [HF-PIPE, "Normalization"](https://huggingface.co/docs/tokenizers/pipeline)
- **Pre-tokenization.** "Pre-tokenization is the act of splitting a text into smaller objects that give an upper bound to what your tokens will be" — [HF-PIPE, "Pre-Tokenization"](https://huggingface.co/docs/tokenizers/pipeline)
- **Pre-tokens versus tokens.** "the pre-tokenizer will split your text into "words" and then, your final tokens will be parts of those words." — [HF-PIPE, "Pre-Tokenization"](https://huggingface.co/docs/tokenizers/pipeline)
- **Pre-tokenizer as a boundary.** "Using a pre-tokenizer will ensure no token is bigger than a word returned by the pre-tokenizer." — [HF-QT, "Training the tokenizer"](https://huggingface.co/docs/tokenizers/quicktour)
- **The model is the trained part.** "This is the part of the pipeline that needs training on your corpus (or that has been trained if you are using a pretrained tokenizer)." — [HF-PIPE, "Model"](https://huggingface.co/docs/tokenizers/pipeline)
- **What the model does.** "The role of the model is to split your "words" into tokens, using the rules it has learned." — [HF-PIPE, "Model"](https://huggingface.co/docs/tokenizers/pipeline)
- **Token → ID mapping.** "It's also responsible for mapping those tokens to their corresponding IDs in the vocabulary of the model." — [HF-PIPE, "Model"](https://huggingface.co/docs/tokenizers/pipeline)
- **Supported models.** The page lists `models.BPE`, `models.Unigram`, `models.WordLevel` and `models.WordPiece` — [HF-PIPE, "Model"](https://huggingface.co/docs/tokenizers/pipeline)
- **Only the model is mandatory.** "Models are the core algorithms used to actually tokenize, and therefore, they are the only mandatory component of a Tokenizer." — [HF-COMP, "Models"](https://huggingface.co/docs/tokenizers/components)
- **BPE (Components wording).** "The Byte-Pair-Encoding works by starting with characters, while merging those that are the most frequently seen together, thus creating new tokens." — [HF-COMP, "Models" table, BPE row](https://huggingface.co/docs/tokenizers/components)
- **BPE iterates.** "It then works iteratively to build new tokens out of the most frequent pairs it sees in a corpus." — [HF-COMP, "Models", BPE row](https://huggingface.co/docs/tokenizers/components)
- **BPE handles unseen words.** "BPE is able to build words it has never seen by using multiple subword tokens, and thus requires smaller vocabularies" — [HF-COMP, "Models", BPE row](https://huggingface.co/docs/tokenizers/components)
- **WordLevel cost.** "it requires extremely large vocabularies for a good coverage." — [HF-COMP, "Models", WordLevel row](https://huggingface.co/docs/tokenizers/components)
- **WordPiece.** "It uses the famous ## prefix to identify tokens that are part of a word (ie not starting a word)." — [HF-COMP, "Models", WordPiece row](https://huggingface.co/docs/tokenizers/components)
- **Unigram contrast.** "This is different from BPE in the way that this is not deterministic based on a set of rules applied sequentially." — [HF-COMP, "Models", Unigram row](https://huggingface.co/docs/tokenizers/components)
- **ByteLevel definition.** "Splits on whitespaces while remapping all the bytes to a set of visible characters. This technique as been introduced by OpenAI with GPT-2" ("as been" is the source's typo) — [HF-COMP, "Pre-tokenizers", ByteLevel row](https://huggingface.co/docs/tokenizers/components)
- **ByteLevel: 256-character alphabet.** "a tokenizer using this only requires 256 characters as initial alphabet (the number of values a byte can have), as opposed to the 130,000+ Unicode characters." — [HF-COMP, "Pre-tokenizers", ByteLevel row](https://huggingface.co/docs/tokenizers/components)
- **ByteLevel: no unknown token.** "it is absolutely unnecessary to have an unknown token using this since we can represent anything with 256 tokens" — [HF-COMP, "Pre-tokenizers", ByteLevel row](https://huggingface.co/docs/tokenizers/components)
- **ByteLevel: non-ASCII readability.** "For non ascii characters, it gets completely unreadable, but it works nonetheless!" — [HF-COMP, "Pre-tokenizers", ByteLevel row](https://huggingface.co/docs/tokenizers/components)
- **ByteLevel "Ġ" example.** Input `"Hello my friend, how are you?"` gives Output: `"Hello", "Ġmy", Ġfriend", ",", "Ġhow", "Ġare", "Ġyou", "?"`. The missing quote before Ġfriend is in the source. — [HF-COMP, "Pre-tokenizers", ByteLevel row, Example column](https://huggingface.co/docs/tokenizers/components)
- **Metaspace (SentencePiece-style).** "Splits on whitespaces and replaces them with a special char “▁” (U+2581)" — [HF-COMP, "Pre-tokenizers", Metaspace row](https://huggingface.co/docs/tokenizers/components)
- **Alignment tracking while normalizing.** "The specificity of tokenizers is that we keep track of the alignment while normalizing. This is essential to allow mapping from the generated tokens back to the input text." — [HF-COMP, "Normalizers"](https://huggingface.co/docs/tokenizers/components). This is two sentences totalling 25 words. Split them if a shorter quote is needed.
- **Offsets.** "it comes with full alignment tracking, meaning you can always get the part of your original sentence that corresponds to a given token." — [HF-QT, "Using the tokenizer"](https://huggingface.co/docs/tokenizers/quicktour)
- **Offsets storage.** "Those are stored in the offsets attribute of our Encoding object." — [HF-QT, "Using the tokenizer"](https://huggingface.co/docs/tokenizers/quicktour)
- **Pre-tokenizer spans feed offsets.** "The output is a list of tuples, with each tuple containing one word and its span in the original sentence" — [HF-PIPE, "Pre-Tokenization"](https://huggingface.co/docs/tokenizers/pipeline)
- **Post-processing adds special tokens.** "Post-processing is the last step of the tokenization pipeline, to perform any additional transformation to the Encoding before it's returned, like adding potential special tokens." — [HF-PIPE, "Post-Processing"](https://huggingface.co/docs/tokenizers/pipeline)
- **No retraining for post-processor changes.** "you don't need to retrain a tokenizer after changing its post-processor." — [HF-PIPE, "Post-Processing"](https://huggingface.co/docs/tokenizers/pipeline)
- **Post-processor in the Quicktour.** "We might want our tokenizer to automatically add special tokens, like "[CLS]" or "[SEP]". To do this, we use a post-processor." — [HF-QT, "Post-processing"](https://huggingface.co/docs/tokenizers/quicktour)
- **Post-processor in Components.** "After the whole pipeline, we sometimes want to insert some special tokens before feed a tokenized string into a model" ("before feed" is the source's wording) — [HF-COMP, "Post-Processors"](https://huggingface.co/docs/tokenizers/components)
- **Special tokens at training time.** The special_tokens list is passed "(they are not used at all during training) so that they get inserted in the vocabulary." — [HF-QT, "Training the tokenizer"](https://huggingface.co/docs/tokenizers/quicktour)
- **Decoding.** "The decoder will first convert the IDs back to tokens (using the tokenizer's vocabulary) and remove all special tokens, then join those tokens with spaces" — [HF-PIPE, "Decoding"](https://huggingface.co/docs/tokenizers/pipeline)
- **Decoders component.** "The Decoder knows how to go from the IDs used by the Tokenizer, back to a readable piece of text." — [HF-COMP, "Decoders"](https://huggingface.co/docs/tokenizers/components)
- **ByteLevel decoder.** "Reverts the ByteLevel PreTokenizer. This PreTokenizer encodes at the byte-level, using a set of visible Unicode characters to represent each byte" — [HF-COMP, "Decoders", ByteLevel row](https://huggingface.co/docs/tokenizers/components)
- **WordPiece decoding example.** Default decoding yields `"welcome to the tok ##eni ##zer ##s library ."`. With `decoders.WordPiece()` it yields `"welcome to the tokenizers library."` — [HF-PIPE, "Decoding"](https://huggingface.co/docs/tokenizers/pipeline)
- **Observed (not a source claim; OBS, tokenizers 0.23.3).** `pre_tokenizers.ByteLevel.alphabet()` has length **256**. `ByteLevel(add_prefix_space=False).pre_tokenize_str("Hello my friend, how are you?")` returned `[('Hello', (0, 5)), ('Ġmy', (5, 8)), ('Ġfriend', (8, 15)), (',', (15, 16)), ('Ġhow', (16, 20)), ('Ġare', (20, 24)), ('Ġyou', (24, 28)), ('?', (28, 29))]`. These are the pieces from the docs example, each with character offsets. `"café 😁"` returned `[('cafÃ©', (0, 4)), ('ĠðŁĺģ', (4, 6))]`, which shows the "unreadable" non-ASCII mapping. `decoders.ByteLevel().decode(["Hello","Ġmy","Ġfriend"])` returned `"Hello my friend"`.

### Inferences
- A lesson can present "normalize → pre-tokenize → model → post-process", plus "decode", as the HF library's own framing. The "Ġ" glyph is a printable stand-in for the space byte. It is not a separate token.
- "Decoding" is not listed as a pipeline stage on HF-PIPE. It is a separate API, `Tokenizer.decode`, covered in its own section.

### Gaps
- The exact phrase "starts with initial tokens and merges the most frequent pairs" was **not found** on the HF tokenizers pages I read. The closest wording is the Components BPE row quoted above. The Transformers page says "BPE starts with individual characters and iteratively merges the most frequent adjacent pair" (see Q2). If the phrase exists, it is probably in the API reference docstrings (`models.BPE` / `BpeTrainer`), which I did not read for this note.
- I did not verify whether the v0.23.3 stable docs carry identical text. The live default is v1.0.0-rc.2, and that is what I cite.

---

## Q2. LLM course BPE chapter and Transformers tokenizer summary: training, inference, trade-offs, GPT-2 vocab, unknown tokens

### Takeaway
BPE training builds a base vocabulary of characters, counts adjacent pairs, merges the most frequent pair, and repeats until it reaches the target vocabulary size. New text is split into characters and the learned merges are applied in the order they were learned. The Transformers page (now titled "Tokenization algorithms") states the GPT-2 count exactly: 50,257 = 256 byte tokens + 50,000 merges + 1 end-of-text token. It also lays out the word-level vs character-level trade-off. Character-level BPE can produce unknown tokens. Byte-level BPE cannot.

### Cited Findings
- **Origin of BPE.** "Byte-Pair Encoding (BPE) was initially developed as an algorithm to compress texts, and then used by OpenAI for tokenization when pretraining the GPT model." — [LLM-6.5, intro](https://huggingface.co/learn/llm-course/chapter6/5)
- **Training, step 1.** "BPE training starts by computing the unique set of words used in the corpus (after the normalization and pre-tokenization steps are completed)" — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Base vocabulary.** "then building the vocabulary by taking all the symbols used to write those words." — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Unknown tokens with character-level BPE.** "If an example you are tokenizing uses a character that is not in the training corpus, that character will be converted to the unknown token." — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Emoji consequence.** "That's one reason why lots of NLP models are very bad at analyzing content with emojis, for instance." — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Byte-level BPE.** "they don't look at words as being written with Unicode characters, but with bytes." — [LLM-6.5, "Training algorithm", Tip box](https://huggingface.co/learn/llm-course/chapter6/5)
- **Byte-level base vocabulary.** "This way the base vocabulary has a small size (256), but every character you can think of will still be included" — [LLM-6.5, "Training algorithm", Tip box](https://huggingface.co/learn/llm-course/chapter6/5)
- **Name.** "This trick is called byte-level BPE." — [LLM-6.5, "Training algorithm", Tip box](https://huggingface.co/learn/llm-course/chapter6/5)
- **Merges until target size.** "we add new tokens until the desired vocabulary size is reached by learning merges" — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **What a merge is.** "rules to merge two elements of the existing vocabulary together into a new one." — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Count pairs.** "the BPE algorithm will search for the most frequent pair of existing tokens (by "pair," here we mean two consecutive tokens in a word)." — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Merge and repeat.** "That most frequent pair is the one that will be merged, and we rinse and repeat for the next step." — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Worked example.** With corpus ("hug", 10), ("pug", 5), ("pun", 12), ("bun", 4), ("hugs", 5), the merges learned are `("u", "g") -> "ug"` (20 occurrences), then `("u", "n") -> "un"` (16), then `("h", "ug") -> "hug"`. Verbatim: "Thus, the first merge rule learned by the tokenizer is ("u", "g") -> "ug"" — [LLM-6.5, "Training algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Inference steps.** The tokenization list is "1. Normalization 2. Pre-tokenization 3. Splitting the words into individual characters 4. Applying the merge rules learned in order on those splits" — [LLM-6.5, "Tokenization algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Inference unknowns.** ""mug", however, will be tokenized as ["[UNK]", "ug"] since the letter "m" was not in the base vocabulary." — [LLM-6.5, "Tokenization algorithm"](https://huggingface.co/learn/llm-course/chapter6/5)
- **GPT-2 special token.** "In the case of GPT-2, the only special token is "<|endoftext|>"" — [LLM-6.5, "Implementing BPE"](https://huggingface.co/learn/llm-course/chapter6/5)
- **GPT-2 has no unknown token.** "GPT-2 doesn’t actually have an unknown token (it’s impossible to get an unknown character when using byte-level BPE)" (curly apostrophes on the rendered page) — [LLM-6.5, "Implementing BPE", final Warning box](https://huggingface.co/learn/llm-course/chapter6/5)
- **Tie-breaking differs from the library.** "Using train_new_from_iterator() on the same corpus won't result in the exact same vocabulary." The page explains that its own code picks the first pair encountered, while the library picks by internal IDs. — [LLM-6.5, "Implementing BPE", Tip](https://huggingface.co/learn/llm-course/chapter6/5)
- **Leading-space marker in the course's GPT-2 pre-tokenization output.** "defaultdict(int, {'This': 3, 'Ġis': 2, 'Ġthe': 1, 'ĠHugging': 1," — [LLM-6.5, "Implementing BPE"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Subword as middle ground.** "They split text into units between words and characters, keeping the vocabulary compact while still capturing meaningful pieces." — [TF-SUM, intro ("Tokenization algorithms")](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Subword behaviour.** "Common words stay intact as single tokens, and rare or unknown words decompose into subwords." — [TF-SUM, intro](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Example.** "annoyingly might be split into ["annoying", "ly"] or ["annoy", "ing", "ly"] depending on the vocabulary." — [TF-SUM, intro](https://huggingface.co/docs/transformers/tokenizer_summary)
- **BPE popularity.** "Byte pair encoding (BPE) is the most popular tokenization algorithm in Transformers, used by models like Llama, Gemma, Qwen2, and more." — [TF-SUM, "Byte pair encoding (BPE)"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **BPE in one line.** "BPE starts with individual characters and iteratively merges the most frequent adjacent pair." — [TF-SUM, "Byte pair encoding (BPE)", step 3](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Vocabulary size formula.** "BPE continues learning merge rules until it reaches the target vocabulary size, which equals the base vocabulary size plus the number of merges." — [TF-SUM, "Byte pair encoding (BPE)", step 5](https://huggingface.co/docs/transformers/tokenizer_summary)
- **GPT (v1).** "GPT uses BPE with a vocabulary size of 40,478 (478 base tokens + 40,000 merges)." — [TF-SUM, "Byte pair encoding (BPE)", step 5](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Unknown tokens with character-level BPE.** "Any character not in the base vocabulary maps to an unknown token like "<unk>"." — [TF-SUM, "Byte pair encoding (BPE)"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Byte-level BPE.** "Byte-level BPE uses 256 byte values as the base vocabulary instead, ensuring every word can be tokenized without the "<unk>" token." — [TF-SUM, "Byte-level BPE"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **GPT-2 vocabulary (exact page wording).** "GPT-2 uses byte-level BPE with a vocabulary size of 50,257 (256 byte tokens + 50,000 merges + special end-of-text token)." — [TF-SUM, "Byte-level BPE"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Word-level downside.** "Vocabulary size becomes extremely large because every unique word requires its own token, including all variations" — [TF-SUM, "Word-level tokenization"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Word-level unknowns.** "Words not in the vocabulary map to an "<unk>" token, so the model can't handle new words." — [TF-SUM, "Word-level tokenization"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Character-level trade-off.** "The vocabulary is small and every word can be represented, so there's no "<unk>" problem. But sequences become much longer." — [TF-SUM, "Character-level tokenization"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Character-level meaning.** "A character like "l" carries far less meaning than "love", so performance suffers." — [TF-SUM, "Character-level tokenization"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **BPE vs Unigram.** "Unlike BPE, which is deterministic and based on merge rules, Unigram is probabilistic and can sample different tokenizations during training." — [TF-SUM, "Unigram"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **SentencePiece motivation.** "Standard BPE and Unigram assume whitespace separates words, which doesn't work for languages like Chinese and Japanese that don't use spaces." — [TF-SUM, "SentencePiece"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **SentencePiece space symbol.** "includes the space character, represented as "▁", in the vocabulary." — [TF-SUM, "SentencePiece"](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Corroborating source code (TT-EXT).** tiktoken's `gpt2()` constructor sets `"explicit_n_vocab": 50257` and `"special_tokens": {ENDOFTEXT: 50256}` — [TT-EXT, `def gpt2()` / `def r50k_base()`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py)
- **Observed (OBS, tiktoken 0.14.0).** `r50k_base` has `n_vocab` 50257 and 50256 mergeable ranks, plus 1 special token `{'<|endoftext|>': 50256}`. That fits 256 single-byte ranks + 50,000 merges + 1 special token. tiktoken's `_educational.bpe_train` assigns ranks 0–255 to single bytes, which is consistent with this.

### Inferences
- The GPT-2 decomposition 256 + 50,000 + 1 = 50,257 is stated verbatim on TF-SUM and corroborated by tiktoken source and observation. **The LLM course page does not state 50,257.** It gives only "256" for the byte-level base and "<|endoftext|>" as the only special token.
- Older versions of the Transformers page were titled "Summary of the tokenizers". Any lesson citation should use the current title, "Tokenization algorithms".

### Gaps
- I found no explicit statement on these pages that merges are applied "in the order they were learned" at inference, beyond the course's list item "Applying the merge rules learned in order on those splits". In tiktoken this corresponds to "ranks correspond to merge priority" (see Q3).

---

## Q3. tiktoken: README, BPE properties, `_educational`, encodings and model mapping, round trip, special tokens

### Takeaway
The README describes tiktoken as "a fast BPE tokeniser for use with OpenAI's models". It lists four BPE properties: reversible and lossless; works on arbitrary text; compresses text (about 4 bytes per token on average); lets the model see common subwords. It ships an educational BPE submodule. `model.py` maps model names to `o200k_base` (gpt-4o, gpt-4.1, gpt-5, o-series), `cl100k_base` (gpt-4, gpt-3.5-turbo, embeddings), `p50k_base` / `r50k_base` (legacy), `gpt2`, and `o200k_harmony` (gpt-oss). `encode` refuses special-token text by default (`disallowed_special="all"`). The source code also warns that `decode` can be lossy when token boundaries split UTF-8 characters.

### Cited Findings
- **Tagline.** "tiktoken is a fast BPE tokeniser for use with OpenAI's models." — [TT-README, top](https://github.com/openai/tiktoken)
- **Round trip in the README code.** `assert enc.decode(enc.encode("hello world")) == "hello world"` (using `tiktoken.get_encoding("o200k_base")`) — [TT-README, top code block](https://github.com/openai/tiktoken)
- **Model lookup.** "# To get the tokeniser corresponding to a specific model in the OpenAI API:" followed by `enc = tiktoken.encoding_for_model("gpt-4o")` — [TT-README, top code block](https://github.com/openai/tiktoken)
- **Speed claim.** "tiktoken is between 3-6x faster than a comparable open source tokeniser" (measured on 1GB of text against `GPT2TokenizerFast` from `tokenizers==0.13.2`) — [TT-README, "Performance"](https://github.com/openai/tiktoken)
- **Tokens as numbers.** "Language models don't see text like you and I, instead they see a sequence of numbers (known as tokens)." — [TT-README, "What is BPE anyway?"](https://github.com/openai/tiktoken)
- **Property 1.** "It's reversible and lossless, so you can convert tokens back into the original text" — [TT-README, "What is BPE anyway?" item 1](https://github.com/openai/tiktoken)
- **Property 2.** "It works on arbitrary text, even text that is not in the tokeniser's training data" — [TT-README, item 2](https://github.com/openai/tiktoken)
- **Property 3.** "It compresses the text: the token sequence is shorter than the bytes corresponding to the original text." — [TT-README, item 3](https://github.com/openai/tiktoken)
- **About 4 bytes per token.** "On average, in practice, each token corresponds to about 4 bytes." — [TT-README, item 3](https://github.com/openai/tiktoken)
- **Property 4.** "It attempts to let the model see common subwords." Example: "BPE encodings will often split "encoding" into tokens like "encod" and "ing"" — [TT-README, item 4](https://github.com/openai/tiktoken)
- **Why subwords help.** "it helps models generalise and better understand grammar." — [TT-README, item 4](https://github.com/openai/tiktoken)
- **Educational submodule.** "tiktoken contains an educational submodule that is friendlier if you want to learn more about the details of BPE" — [TT-README, "What is BPE anyway?"](https://github.com/openai/tiktoken). Usage shown: `from tiktoken._educational import *`, `train_simple_encoding()`, `SimpleBytePairEncoding.from_tiktoken("cl100k_base")`.
- **Educational module docstring.** "This is an educational implementation of the byte pair encoding algorithm." — [TT-EDU, module docstring](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)
- **Ranks = merge priority.** "# A dictionary mapping token bytes to their ranks. The ranks correspond to merge priority" — [TT-EDU, `SimpleBytePairEncoding.__init__`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)
- **Encode loop.** "# Iterate over all pairs and find the pair we want to merge the most" and "# Otherwise, merge that pair and leave the rest unchanged. Then repeat." The code selects the adjacent pair with the lowest rank. — [TT-EDU, `bpe_encode`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)
- **Byte base vocabulary in training.** "# First, add tokens for each individual byte value". The function raises "vocab_size must be at least 256, so we can encode all bytes" — [TT-EDU, `bpe_train`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)
- **Training merge step.** "# Find the most common pair. This will become our next token" — [TT-EDU, `bpe_train`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)
- **Model → encoding mapping.** `MODEL_TO_ENCODING` (exact entries) includes `"gpt-5": "o200k_base"`, `"gpt-4.1": "o200k_base"`, `"gpt-4o": "o200k_base"`, `"o1"`/`"o3"`/`"o4-mini": "o200k_base"`, `"gpt-4": "cl100k_base"`, `"gpt-3.5-turbo": "cl100k_base"`, `"text-embedding-3-small": "cl100k_base"`, `"text-davinci-003": "p50k_base"`, `"davinci": "r50k_base"` and `"gpt2": "gpt2"`. `MODEL_PREFIX_TO_ENCODING` includes `"gpt-oss-": "o200k_harmony"` and `"gpt-4o-": "o200k_base"` — [TT-MODEL](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py)
- **Mapping caveat.** "# TODO: these will likely be replaced by an API endpoint" — [TT-MODEL, above `MODEL_PREFIX_TO_ENCODING`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py)
- **Prefix matching.** "# Prefix matching avoids needing library updates for every model version release" — [TT-MODEL, `encoding_name_for_model`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py)
- **Encoding files.** The files are downloaded from `https://openaipublic.blob.core.windows.net/encodings/{r50k_base,p50k_base,cl100k_base,o200k_base}.tiktoken`. The gpt2 encoding uses `.../gpt-2/encodings/main/vocab.bpe` and `encoder.json` — [TT-EXT](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py)
- **Special tokens per encoding (TT-EXT).** In cl100k_base: `ENDOFTEXT: 100257`, FIM tokens 100258–100260, and `<|endofprompt|>` (100276, value observed). In o200k_base: `{ENDOFTEXT: 199999, ENDOFPROMPT: 200018}` — [TT-EXT](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py)
- **Default disallows special tokens.** The `encode` signature is `disallowed_special: Literal["all"] | Collection[str] = "all",` — [TT-CORE, `Encoding.encode`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py)
- **What special tokens are.** "Special tokens are artificial tokens used to unlock capabilities from a model, such as fill-in-the-middle." — [TT-CORE, `encode` docstring](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py)
- **Why the default is strict.** "they can be used to trick a model into doing something we don't want it to do." — [TT-CORE, `encode` docstring](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py)
- **Default behaviour.** "by default, encode will raise an error if it encounters text that corresponds to a special token." — [TT-CORE, `encode` docstring](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py)
- **Opt-out.** "Setting disallowed_special to () will prevent this function from raising errors and cause all text corresponding to special tokens to be encoded as natural text." — [TT-CORE, `encode` docstring](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py)
- **Decode is lossy by default.** "WARNING: the default behaviour of this function is lossy, since decoded bytes are not guaranteed to be valid UTF-8." — [TT-CORE, `Encoding.decode` docstring](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py)
- **Observed (OBS, tiktoken 0.14.0).** Sample string: `"Tokenization isn't magic: hello world, Hello world, お誕生日おめでとう!"`, which is 80 UTF-8 bytes.
  - `decode(encode(s)) == s` was **True** for all four encodings.
  - Token counts: r50k_base 27, p50k_base 27, cl100k_base 23, o200k_base 20. That is 2.96, 2.96, 3.48 and 4.00 bytes per token.
  - `encoding_for_model("gpt-4o")` returned `o200k_base`. `encoding_for_model("gpt-4")` returned `cl100k_base`.
  - `cl100k_base.encode("<|endoftext|>")` raised "ValueError: Encountered text corresponding to disallowed special token '<|endoftext|>'."
  - With `allowed_special="all"` it returned `[100257]`. With `disallowed_special=()` it returned 7 ordinary tokens `[27, 91, 8862, 728, 428, 91, 29]`.

### Inferences
- The two "lossless" statements fit together. The README's claim is about the token sequence as a whole. The `decode` warning, and the Cookbook's warning about single tokens (Q4), concern decoding sequences that end mid-UTF-8 character. The observed round trips confirm whole-string decoding is exact.
- "About 4 bytes per token" is an average for typical (English-heavy) text. In the observed sample with Japanese, older encodings got under 3 bytes per token.

### Gaps
- `model.py` does **not** say which encoding newer non-listed models (e.g. any 2026 models beyond the `gpt-5` prefix) use. The mapping is explicitly flagged as likely to be replaced by an API endpoint.
- The README gives no per-language token statistics.

---

## Q4. OpenAI Cookbook "How to count tokens with tiktoken": encodings per model, why counting matters, languages

### Takeaway
The Cookbook gives two reasons to count tokens: fitting the model's length limit and estimating cost, since usage is priced by token. It maps encodings to models (o200k_base → gpt-4o / gpt-4o-mini, cl100k_base → gpt-4 / gpt-3.5-turbo / embeddings, and so on). It says tokens range from one character to one word in English, but can be shorter than a character or longer than a word in other languages. It states that spaces are usually grouped with the starts of words. Its stored outputs show the same Japanese string taking 14, 9 and 8 tokens under different encodings.

### Cited Findings
- **Why tokens.** "Splitting text strings into tokens is useful because GPT models see text in the form of tokens." — [CB, title cell](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Limits.** "Knowing how many tokens are in a text string can tell you (a) whether the string is too long for a text model to process" — [CB, title cell](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Cost.** "and (b) how much an OpenAI API call costs (as usage is priced by token)." — [CB, title cell](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Example split.** For `"tiktoken is great!"` with `"cl100k_base"`, the notebook shows `["t", "ik", "token", " is", " great", "!"]` — [CB, title cell](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Encodings per model.** "Encodings specify how text is converted into tokens. Different models use different encodings." — [CB, "Encodings"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Encoding table.** `o200k_base` → `gpt-4o`, `gpt-4o-mini`. `cl100k_base` → `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`, `text-embedding-ada-002`, `text-embedding-3-small`, `text-embedding-3-large`. `p50k_base` → Codex models, `text-davinci-002`, `text-davinci-003`. `r50k_base` (or `gpt2`) → GPT-3 models like `davinci` — [CB, "Encodings" table](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Internal inconsistency.** The text says "tiktoken supports three encodings used by OpenAI models:" but the table that follows lists four — [CB, "Encodings"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **p50k vs r50k.** "Note that p50k_base overlaps substantially with r50k_base, and for non-code applications, they will usually give the same tokens." — [CB, "Encodings"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Token length in English.** "In English, tokens commonly range in length from one character to one word (e.g., "t" or " great")" — [CB, "How strings are typically tokenized"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Other languages.** "though in some languages tokens can be shorter than one character or longer than one word." — [CB, "How strings are typically tokenized"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Leading spaces.** "Spaces are usually grouped with the starts of words (e.g., " is" instead of "is " or " "+"is")." — [CB, "How strings are typically tokenized"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Comparing encodings.** "Different encodings vary in how they split words, group spaces, and handle non-English characters." — [CB, "5. Comparing encodings"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Stored outputs (source data, produced by the notebook authors).**
  - `"お誕生日おめでとう"`: r50k_base 14 tokens, p50k_base 14, cl100k_base 9, o200k_base 8.
  - `"antidisestablishmentarianism"`: r50k_base 5 (`ant|idis|establishment|arian|ism`), cl100k_base 6, o200k_base 6 (`ant|idis|est|ablishment|arian|ism`).
  - `"2 + 2 = 4"`: r50k_base 5, cl100k_base 7, o200k_base 7.
  - Source: [CB, outputs of cells "compare_encodings(...)"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Single-token decode caveat.** "beware that it can be lossy for tokens that aren't on utf-8 boundaries." — [CB, "4. Turn tokens into text with encoding.decode()"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Chat counting is an estimate.** "Consider the counts from the function below an estimate, not a timeless guarantee." — [CB, "6. Counting tokens for chat completions API calls"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Download note.** "The first time this runs, it will require an internet connection to download." — [CB, "2. Load an encoding"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)

### Inferences
- The Cookbook's encoding table is older than `model.py` (notebook last changed 2024-10-08). It omits gpt-4.1, gpt-5, the o-series and gpt-oss/o200k_harmony. For current mappings, cite TT-MODEL (tag 0.14.0) rather than the Cookbook table.
- The Japanese example is the most direct primary evidence on languages. The same 9-character string costs 14 tokens under r50k_base and 8 under o200k_base.

### Gaps
- The notebook does not say which tiktoken version produced its stored outputs. My local run (OBS) reproduced the same Japanese pieces for r50k/cl100k/o200k inside a longer string, but I did not rerun the exact cells.
- The notebook links to the OpenAI Tokenizer webpage at `beta.openai.com/tokenizer`. I did not check that page; it is out of scope.

---

## Q5. Primary statements that a token is not a word, that tokenizers differ, and that leading spaces are part of tokens

### Takeaway
All three claims have primary support. Tokens are pieces between characters and words (TF-SUM, HF-PIPE), and in some languages they are smaller than a character or larger than a word (CB). Different models and encodings tokenize the same text differently (CB; observed). Leading spaces attach to the following word, shown as `" is"` in tiktoken and as `Ġ` in HF ByteLevel (CB; HF-COMP; LLM-6.5; TT-EDU).

### Cited Findings
- **Not a word.** "your final tokens will be parts of those words." — [HF-PIPE, "Pre-Tokenization"](https://huggingface.co/docs/tokenizers/pipeline)
- **Not a word.** "They split text into units between words and characters" — [TF-SUM, intro](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Not a word.** "in some languages tokens can be shorter than one character or longer than one word." — [CB, "How strings are typically tokenized"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Not a word.** "Language models don't see text like you and I, instead they see a sequence of numbers (known as tokens)." — [TT-README, "What is BPE anyway?"](https://github.com/openai/tiktoken)
- **Differs by tokenizer.** "Different models use different encodings." — [CB, "Encodings"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Differs by tokenizer.** "Different encodings vary in how they split words, group spaces, and handle non-English characters." — [CB, "5. Comparing encodings"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Differs by vocabulary.** "annoyingly might be split into ["annoying", "ly"] or ["annoy", "ing", "ly"] depending on the vocabulary." — [TF-SUM, intro](https://huggingface.co/docs/transformers/tokenizer_summary)
- **Leading spaces (tiktoken).** "Spaces are usually grouped with the starts of words (e.g., " is" instead of "is " or " "+"is")." — [CB, "How strings are typically tokenized"](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)
- **Leading spaces (HF ByteLevel).** Output: `"Hello", "Ġmy", Ġfriend", ",", "Ġhow", "Ġare", "Ġyou", "?"` — [HF-COMP, ByteLevel row](https://huggingface.co/docs/tokenizers/components)
- **Leading spaces (course).** `'Ġis': 2, 'Ġthe': 1` appear in the GPT-2 pre-tokenizer output, and the first learned merge is `('Ġ', 't') -> 'Ġt'` — [LLM-6.5, "Implementing BPE"](https://huggingface.co/learn/llm-course/chapter6/5)
- **Leading spaces (tiktoken source comment).** For `data = "Hello world"` the comment shows words `[b'H', b'e', b'l', b'l', b'o']` and `[b' ', b'w', b'o', b'r', b'l', b'd']` — [TT-EDU, `bpe_train`](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)
- **Observed (OBS, cl100k_base, tiktoken 0.14.0).** `"hello"` → [15339], `" hello"` → [24748], `"Hello"` → [9906], `" Hello"` → [22691]. That is four different IDs for the same word, depending on leading space and case. The sample sentence's `"isn't"` became `b' isn', b"'t"` under cl100k_base but the single token `b" isn't"` under o200k_base.

### Inferences
- A lesson can say, citing primary docs: "a token is usually a piece of a word, often carrying its leading space, and the same text splits differently under different tokenizers". The case and space sensitivity of IDs is observed behaviour, not a documented claim.

### Gaps
- No primary source I read states the case and leading-space ID differences directly. That point rests only on local observation.

---

## Claims table

Abbreviations follow the source register. All sources were accessed 2026-10-18. Versions: HF tokenizers docs v1.0.0-rc.2 (src 3fe1b852de47). TF-SUM v5.20.1 (src 83eb94c1febf). LLM-6.5 live (src e05c3b637f0a). tiktoken tag 0.14.0 (4e71bbe0c078). CB src db3144982aa2.

| # | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Confidence | Notes |
|---|---|---|---|---|---|---|
| 1 | HF encode pipeline has 4 stages | HF-PIPE | "The tokenization pipeline" intro | "the input text(s) go through the following pipeline:" (then normalization, pre-tokenization, model, post-processing) | high | Decoding has its own section, not a pipeline stage |
| 2 | Normalization cleans raw text | HF-PIPE | Normalization | "a set of operations you apply to a raw string to make it less random or "cleaner"." | high | |
| 3 | Pre-tokenization bounds tokens; tokens are parts of words | HF-PIPE | Pre-Tokenization | "your final tokens will be parts of those words." | high | |
| 4 | The model is the trained part | HF-PIPE | Model | "This is the part of the pipeline that needs training on your corpus" | high | |
| 5 | Model splits words and maps tokens to IDs | HF-PIPE | Model | "It's also responsible for mapping those tokens to their corresponding IDs in the vocabulary of the model." | high | |
| 6 | Model is the only mandatory component | HF-COMP | Models | "they are the only mandatory component of a Tokenizer." | high | |
| 7 | Supported models: BPE, Unigram, WordLevel, WordPiece | HF-PIPE | Model | `models.BPE` / `models.Unigram` / `models.WordLevel` / `models.WordPiece` (list) | high | |
| 8 | BPE merges most frequent pairs starting from characters | HF-COMP | Models, BPE row | "works by starting with characters, while merging those that are the most frequently seen together, thus creating new tokens." | high | Requested phrase "starts with initial tokens…" not found verbatim |
| 9 | Post-processing adds special tokens | HF-PIPE | Post-Processing | "to perform any additional transformation to the Encoding before it's returned, like adding potential special tokens." | high | |
| 10 | Post-processor change needs no retraining | HF-PIPE | Post-Processing | "you don't need to retrain a tokenizer after changing its post-processor." | high | |
| 11 | ByteLevel remaps bytes to visible chars, from GPT-2 | HF-COMP | Pre-tokenizers, ByteLevel | "remapping all the bytes to a set of visible characters. This technique as been introduced by OpenAI with GPT-2" | high | "as been" is the source typo |
| 12 | ByteLevel base alphabet = 256 | HF-COMP | Pre-tokenizers, ByteLevel | "only requires 256 characters as initial alphabet (the number of values a byte can have)" | high | Observed: `ByteLevel.alphabet()` length 256 |
| 13 | ByteLevel needs no unknown token | HF-COMP | Pre-tokenizers, ByteLevel | "it is absolutely unnecessary to have an unknown token using this" | high | |
| 14 | "Ġ" marks a leading space in ByteLevel output | HF-COMP | ByteLevel example | `"Hello", "Ġmy", Ġfriend", ",", "Ġhow"` | high | Observed identical pieces with offsets |
| 15 | Alignment/offsets tracked | HF-QT | Using the tokenizer | "you can always get the part of your original sentence that corresponds to a given token." | high | Also HF-COMP Normalizers |
| 16 | Decoder converts IDs back, removing special tokens | HF-PIPE | Decoding | "convert the IDs back to tokens (using the tokenizer's vocabulary) and remove all special tokens" | high | |
| 17 | ByteLevel decoder reverts byte remapping | HF-COMP | Decoders, ByteLevel | "Reverts the ByteLevel PreTokenizer." | high | |
| 18 | BPE training starts from the words' symbols | LLM-6.5 | Training algorithm | "building the vocabulary by taking all the symbols used to write those words." | high | |
| 19 | Merge most frequent pair, repeat | LLM-6.5 | Training algorithm | "That most frequent pair is the one that will be merged, and we rinse and repeat for the next step." | high | |
| 20 | Stop at target vocab size | LLM-6.5 | Training algorithm | "we add new tokens until the desired vocabulary size is reached by learning merges" | high | |
| 21 | Inference applies learned merges in order | LLM-6.5 | Tokenization algorithm | "Applying the merge rules learned in order on those splits" | high | tiktoken: "ranks correspond to merge priority" (TT-EDU) |
| 22 | Char-level BPE yields [UNK] for unseen characters | LLM-6.5 | Tokenization algorithm | ""mug", however, will be tokenized as ["[UNK]", "ug"] since the letter "m" was not in the base vocabulary." | high | |
| 23 | Byte-level BPE base = 256, no UNK | LLM-6.5 | Training algorithm, Tip | "the base vocabulary has a small size (256), but every character you can think of will still be included" | high | |
| 24 | GPT-2 has no unknown token | LLM-6.5 | Implementing BPE, Warning | "GPT-2 doesn’t actually have an unknown token" | high | Curly apostrophe on the rendered page |
| 25 | GPT-2 vocab = 50,257 = 256 + 50,000 + EOT | TF-SUM | Byte-level BPE | "a vocabulary size of 50,257 (256 byte tokens + 50,000 merges + special end-of-text token)." | high | Corroborated by TT-EXT `explicit_n_vocab: 50257` and observed 50256 ranks + 1 special; not stated on LLM-6.5 |
| 26 | Vocab size = base + number of merges | TF-SUM | BPE step 5 | "the target vocabulary size, which equals the base vocabulary size plus the number of merges." | high | |
| 27 | Word-level: huge vocab, UNK for new words | TF-SUM | Word-level tokenization | "Vocabulary size becomes extremely large because every unique word requires its own token" | high | |
| 28 | Char-level: long, less meaningful sequences | TF-SUM | Character-level tokenization | "But sequences become much longer. A character like "l" carries far less meaning than "love"" | high | |
| 29 | Subword is the middle ground | TF-SUM | intro | "They split text into units between words and characters, keeping the vocabulary compact" | high | Page title is now "Tokenization algorithms" |
| 30 | BPE originally a compression algorithm, adopted by OpenAI for GPT | LLM-6.5 | intro | "initially developed as an algorithm to compress texts, and then used by OpenAI for tokenization when pretraining the GPT model." | high | |
| 31 | tiktoken is a fast BPE tokeniser for OpenAI models | TT-README | top | "tiktoken is a fast BPE tokeniser for use with OpenAI's models." | high | |
| 32 | BPE is reversible and lossless | TT-README | What is BPE anyway? #1 | "It's reversible and lossless, so you can convert tokens back into the original text" | high | Observed round trip True for 4 encodings |
| 33 | BPE works on arbitrary text | TT-README | #2 | "It works on arbitrary text, even text that is not in the tokeniser's training data" | high | |
| 34 | About 4 bytes per token on average | TT-README | #3 | "On average, in practice, each token corresponds to about 4 bytes." | high (as quoted) | Observed 2.96–4.00 bytes/token on a mixed EN/JA sample |
| 35 | BPE lets model see common subwords | TT-README | #4 | "It attempts to let the model see common subwords." | high | Example "encod" + "ing" |
| 36 | tiktoken has an educational BPE module | TT-README / TT-EDU | What is BPE anyway? / module docstring | "This is an educational implementation of the byte pair encoding algorithm." | high | |
| 37 | gpt-4o, gpt-4.1, gpt-5, o-series → o200k_base | TT-MODEL | MODEL_TO_ENCODING | `"gpt-4o": "o200k_base",` | high | Exact dict entries; gpt-5 included |
| 38 | gpt-4 / gpt-3.5-turbo / embeddings → cl100k_base | TT-MODEL | MODEL_TO_ENCODING | `"gpt-4": "cl100k_base",` | high | Observed `encoding_for_model("gpt-4")` = cl100k_base |
| 39 | Legacy models → p50k_base / r50k_base; gpt2 → gpt2 | TT-MODEL | MODEL_TO_ENCODING | `"text-davinci-003": "p50k_base",` / `"davinci": "r50k_base",` | high | |
| 40 | gpt-oss → o200k_harmony | TT-MODEL | MODEL_PREFIX_TO_ENCODING | `"gpt-oss-": "o200k_harmony",` | high | |
| 41 | Model mapping may move to an API | TT-MODEL | top comment | "# TODO: these will likely be replaced by an API endpoint" | high | |
| 42 | encode disallows special tokens by default | TT-CORE | Encoding.encode | "by default, encode will raise an error if it encounters text that corresponds to a special token." | high | Observed ValueError |
| 43 | Reason: special tokens can trick models | TT-CORE | Encoding.encode | "they can be used to trick a model into doing something we don't want it to do." | high | |
| 44 | decode can be lossy (invalid UTF-8) | TT-CORE | Encoding.decode | "the default behaviour of this function is lossy, since decoded bytes are not guaranteed to be valid UTF-8." | high | Qualifies claim 32 |
| 45 | Count tokens for limits and cost | CB | title cell | "how much an OpenAI API call costs (as usage is priced by token)." | high | Also "(a) whether the string is too long…" |
| 46 | Different models use different encodings | CB | Encodings | "Encodings specify how text is converted into tokens. Different models use different encodings." | high | |
| 47 | Tokens can be shorter than a character or longer than a word | CB | How strings are typically tokenized | "in some languages tokens can be shorter than one character or longer than one word." | high | |
| 48 | Leading spaces grouped with word starts | CB | How strings are typically tokenized | "Spaces are usually grouped with the starts of words (e.g., " is" instead of "is " or " "+"is")." | high | |
| 49 | Same Japanese string: 14 / 9 / 8 tokens across encodings | CB | 5. Comparing encodings (stored output) | `r50k_base: 14 tokens` … `cl100k_base: 9 tokens` … `o200k_base: 8 tokens` | medium | Stored notebook output; tiktoken version not stated |
| 50 | Cookbook says "three encodings" but lists four | CB | Encodings | "tiktoken supports three encodings used by OpenAI models:" | high | Internal inconsistency; table predates gpt-4.1/gpt-5 |
| 51 | Chat-message counts are estimates | CB | 6. Counting tokens for chat completions | "Consider the counts from the function below an estimate, not a timeless guarantee." | high | |
| 52 | HF docs default is a v1 release candidate whose bindings can't yet build/train | HF-PIPE/COMP/QT | top Tip | "Not supported by the rc0 bindings yet. rc0 loads a tokenizer.json and encodes and decodes with it" | high | Live version selector: v1.0.0-rc.2 |
| 53 | Same word gets different IDs with/without leading space or capital | OBS | n/a | n/a (observed: "hello" 15339, " hello" 24748, "Hello" 9906, " Hello" 22691, cl100k_base) | medium | Observation, not a documented claim |
