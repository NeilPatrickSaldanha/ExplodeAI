# Learned merges turn bytes into billable tokens

*Pass 1 evidence report for ExplodeAI Lesson 02, "LLM tokenization, exploded". All sources accessed 2026-10-18. Synthesized from three research-note files in `research_notes/Tokenization primary sources/`: `tokenizer_papers.md`, `tokenizer_libraries.md`, `provider_token_counting.md`. Every excerpt is copied verbatim from those notes and is 25 words or fewer. No excerpt came through a summarizing fetch tool: papers were read from PDF text layers, library docs from pinned raw files plus string-matched live pages, and provider docs from raw `.md`/HTML downloads. No provider API was called and no API key was used.*

The primary sources describe one mechanism with remarkable consistency. Byte pair encoding (BPE) starts from a base alphabet, counts adjacent symbol pairs over a frequency-weighted list of words, merges the most frequent pair into a new symbol, and repeats; the final vocabulary is **the base alphabet plus the number of merges**, and in Sennrich et al. (2016) the merge count is "the only hyperparameter of the algorithm" ([SEN v5](https://arxiv.org/pdf/1508.07909v5)). New text is split back into base symbols and the learned merges are replayed, which makes BPE segmentation **deterministic**. Sennrich only implies the ordering, but the Hugging Face course states "Applying the merge rules learned in order" and tiktoken stores merges as ranks that "correspond to merge priority" ([LLM-6.5](https://huggingface.co/learn/llm-course/chapter6/5); [TT-EDU](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)). GPT-2 switched the base alphabet from Unicode code points (**over 130,000**) to **256 byte values**, which removes unknown tokens entirely, and blocked merges across "character categories" except for spaces, which is why tokens usually carry their leading space ([GPT2](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)). SentencePiece and the unigram LM are the main alternative lineage: they train on raw sentences, treat whitespace as the symbol U+2581, are configured by final vocabulary size, and (for unigram) can sample several segmentations ([SP v1](https://arxiv.org/pdf/1808.06226v1); [KUDO v1](https://arxiv.org/pdf/1804.10959v1)). On counting, all three providers expose a pre-send counting endpoint and all three tie counts to a specific model's tokenizer. They frame precision differently: Anthropic calls its free count "an estimate", OpenAI says its endpoint returns "the exact count", and Google says multimodal counts are estimates with billing truth in `usage_metadata`. Their English rules of thumb (about 4 characters per token for OpenAI and Gemini, about 3.5 for pre-Opus-4.7 Claude, roughly 30% more tokens on newer Claude models) do not line up, so a "token" is not a common unit across providers. The weakest evidence is the Gage 1994 article (third-party mirror only), the OpenAI help article and Tokenizer page (both returned HTTP 403), the undefined GPT-2 "character categories", and two internal conflicts in provider docs (Anthropic's 30% versus 1.35x, Gemini's 263 versus ~100/~300 video tokens per second).

## Training is a frequency-counting loop with one knob

Sennrich, Haddow and Birch took a 1994 compression trick and repurposed it: "We adapt byte pair encoding (BPE) (Gage, 1994), a compression algorithm, to the task of word segmentation" ([SEN v5](https://arxiv.org/pdf/1508.07909v5)). Gage's original replaced the most frequent pair of adjacent bytes with "a byte that was not in the original data" and repeated "until no further compression is possible" ([GAGE mirror](https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm)); that article was read only on a third-party transcription, so its excerpts are medium confidence. Sennrich's change was to merge "characters or character sequences" rather than bytes. Training initializes the symbol vocabulary with the character vocabulary, represents each word "as a sequence of characters, plus a special end-of-word symbol ‘·’", and then "We iteratively count all symbol pairs and replace each occurrence of the most frequent pair (‘A’, ‘B’) with a new symbol ‘AB’" ([SEN v5](https://arxiv.org/pdf/1508.07909v5), §3.2). Two efficiency choices shape the lesson's animation: **counting runs over a dictionary of words weighted by frequency**, not raw running text, and "we do not consider pairs that cross word boundaries." The arithmetic is exact: "The final symbol vocabulary size is equal to the size of the initial vocabulary, plus the number of merge operations", and "the latter is the only hyperparameter of the algorithm."

The paper's toy example needs care. Figure 1 shows merges learned "from dictionary {‘low’, ‘lowest’, ‘newer’, ‘wider’}" ("r · → r·", "l o → lo", "lo w → low", "e r· → er·"), but the Algorithm 1 Python uses a different vocabulary (low×5, lower×2, newest×6, widest×3) and spells the end-of-word marker `</w>` rather than "·" ([SEN v5](https://arxiv.org/pdf/1508.07909v5), p.4). Running Algorithm 1 will not reproduce Figure 1. The Hugging Face LLM course gives a cleaner worked example. It starts from the unique words "(after the normalization and pre-tokenization steps are completed)", builds the base vocabulary from "all the symbols used to write those words", searches for "the most frequent pair of existing tokens", and states "we rinse and repeat" until "the desired vocabulary size is reached by learning merges". On the corpus hug×10, pug×5, pun×12, bun×4, hugs×5, the first rule is ("u", "g") -> "ug" with **20 occurrences**, then ("u", "n") -> "un" (16), then ("h", "ug") -> "hug" ([LLM-6.5](https://huggingface.co/learn/llm-course/chapter6/5)). The course also warns that its hand-written trainer and the library's `train_new_from_iterator()` "won't result in the exact same vocabulary" because they break ties differently, so tie-breaking is an implementation detail and not part of the algorithm.

The single knob can be expressed two ways. Sennrich counts merges (59,500 for BPE and 89,500 for joint BPE in the experiments). SentencePiece instead "specifies the final size of vocabulary", because "the number of merge operations is a BPE specific parameter and can not be applicable to other segmentation algorithms" ([SP v1](https://arxiv.org/pdf/1808.06226v1), §3.3). The Transformers docs bridge the two: the target vocabulary size "equals the base vocabulary size plus the number of merges", and they give GPT-1 as **40,478 = 478 base tokens + 40,000 merges** ([TF-SUM](https://huggingface.co/docs/transformers/tokenizer_summary)). tiktoken's educational trainer makes the same loop explicit in code comments: "# Find the most common pair. This will become our next token" ([TT-EDU](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)).

## Encoding new text replays merges deterministically

At inference, BPE does not search for a best segmentation. Sennrich: "At test time, we first split words into sequences of characters, then apply the learned operations to merge the characters into larger, known symbols"; the unseen word ‘lower’ "would be segmented into ‘low er·’" ([SEN v5](https://arxiv.org/pdf/1508.07909v5)). Sennrich never states in so many words that merges apply in learned order. That ordering follows from Algorithm 1 producing an ordered list, and it is stated outright in later sources. The HF course lists inference as "1. Normalization 2. Pre-tokenization 3. Splitting the words into individual characters 4. Applying the merge rules learned in order on those splits" ([LLM-6.5](https://huggingface.co/learn/llm-course/chapter6/5)). tiktoken encodes merge order as rank: "The ranks correspond to merge priority", and its encoder repeatedly merges the adjacent pair with the lowest rank, "Then repeat" ([TT-EDU](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py)). Kudo summarizes the consequence: "BPE is based on a greedy and deterministic symbol replacement, which can not provide multiple segmentations with probabilities" ([KUDO v1](https://arxiv.org/pdf/1804.10959v1), §3.1).

Kudo's contribution is to show that determinism is a choice, not a necessity: "multiple segmentations are possible even with the same vocabulary", as in his "Hello World" table where "Hell/o/ world" and "H/ello/ world" get different IDs ([KUDO v1](https://arxiv.org/pdf/1804.10959v1)). His **unigram language model** assumes "each subword occurs independently", finds the best path "with the Viterbi algorithm", estimates probabilities "via the EM algorithm", and trains top-down. It starts from "a reasonably big seed vocabulary", keeps the top η% (η = 80 in his example) each round "until |V| reaches a desired vocabulary size", and keeps single characters: "we always keep the subwords consisting of a single character to avoid out-of-vocabulary." Sampling one segmentation per parameter update ("subword regularization") "boosted BLEU scores quite impressively (+1 to 2 points)" in all but one language pair, while plain BPE and unigram "show almost comparable BLEU scores" without it. The HF docs repeat the contrast in their own words: Unigram "is not deterministic based on a set of rules applied sequentially" ([HF-COMP](https://huggingface.co/docs/tokenizers/components)), and "Unlike BPE, which is deterministic and based on merge rules, Unigram is probabilistic" ([TF-SUM](https://huggingface.co/docs/transformers/tokenizer_summary)). For the lesson, BPE is built bottom-up (characters to merges) and segments deterministically; unigram prunes top-down and segments probabilistically. Kudo also notes that WordPiece "is different from BPE" because it "uses a likelihood instead of frequency."

## 256 byte values replace 130,000 code points as the base alphabet

GPT-2's §2.2 sets the design goal that "A general language model (LM) should be able to compute the probability of (and also generate) any string", and identifies the obstacle: "reference BPE implementations often operate on Unicode code points and not byte sequences", which "would result in a base vocabulary of over 130,000 before any multi-symbol tokens are added." By contrast, "a byte-level version of BPE only requires a base vocabulary of size 256" ([GPT2](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)). The vocabulary size, **50,257**, and the **1024-token** context appear in §2.3 "Model", not §2.2. The paper never breaks 50,257 down; the Transformers docs do: "256 byte tokens + 50,000 merges + special end-of-text token" ([TF-SUM](https://huggingface.co/docs/transformers/tokenizer_summary)). tiktoken's source corroborates this with `"explicit_n_vocab": 50257` and `<|endoftext|>` at ID 50256 ([TT-EXT](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py)), and a local run of tiktoken 0.14.0 found 50,256 mergeable ranks plus one special token in `r50k_base`.

The practical payoff is **no unknown token**. Character-level BPE still fails on unseen characters: the HF course tokenizes "mug" as ["[UNK]", "ug"] "since the letter "m" was not in the base vocabulary", and calls this "one reason why lots of NLP models are very bad at analyzing content with emojis" ([LLM-6.5](https://huggingface.co/learn/llm-course/chapter6/5)). Byte-level BPE closes the gap: "every character you can think of will still be included", and "GPT-2 doesn’t actually have an unknown token". The HF `ByteLevel` pre-tokenizer documents the mechanism: it remaps "all the bytes to a set of visible characters", needs "256 characters as initial alphabet", makes an unknown token "absolutely unnecessary", and renders non-ASCII text "completely unreadable, but it works nonetheless!" Its documented example output is "Hello", "Ġmy", Ġfriend", "," ..., where **Ġ is the printable stand-in for the space byte**, not a separate token ([HF-COMP](https://huggingface.co/docs/tokenizers/components)). Locally, tokenizers 0.23.3 reported `ByteLevel.alphabet()` length 256 and turned "café 😁" into `cafÃ©` and `ĠðŁĺģ`, which is a vivid demo of the unreadable-but-lossless mapping.

## Round trips are lossless only at the right level

Every family claims a round trip, but each scopes it differently, and the lesson should name the scope. SentencePiece defines "lossless tokenization" as `Decode(Encode(Normalize(text))) = Normalize(text)`, which is lossless **relative to normalized text** (NFKC by default), not raw input ([SP v1](https://arxiv.org/pdf/1808.06226v1), §3.1, §3.4). Its trick is that "Even whitespace is handled as a normal symbol", escaped "with a meta symbol _ (U+2581)", so the decoder is just `''.join(tokens).replace('_', ' ')`. The PDF text layer shows an ASCII underscore where the paper names U+2581 ("▁"); cite the codepoint. The motivating failure is that with ordinary pre-tokenized output "The information that no space exists between “world” and “.” is not kept", and subword-nmt's `@@` marker makes it "not possible to encode consecutive whitespaces with this representation". Sennrich's own end-of-word symbol exists for the same reason: it "allows us to restore the original tokenization after translation" ([SEN v5](https://arxiv.org/pdf/1508.07909v5)).

tiktoken's README lists the property first: "It's reversible and lossless, so you can convert tokens back into the original text", and its first code block asserts `enc.decode(enc.encode("hello world")) == "hello world"` ([TT-README](https://github.com/openai/tiktoken)). The source qualifies this. The `decode` docstring warns "the default behaviour of this function is lossy, since decoded bytes are not guaranteed to be valid UTF-8" ([TT-CORE](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py)), and the Cookbook says decoding single tokens "can be lossy for tokens that aren't on utf-8 boundaries" ([CB](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)). The two statements fit together. A whole token sequence round-trips exactly; a slice that cuts a multi-byte character does not. A local run confirmed `decode(encode(s)) == s` for all four OpenAI encodings on a mixed English/Japanese sample. In HF `tokenizers`, decoding is a separate API rather than a pipeline stage, and the default decoder converts IDs to tokens, removes special tokens, and then, in the docs' words, will "join those tokens with spaces". That yields `"welcome to the tok ##eni ##zer ##s library ."` until a matching `decoders.WordPiece()` is plugged in ([HF-PIPE](https://huggingface.co/docs/tokenizers/pipeline)). The ByteLevel decoder "Reverts the ByteLevel PreTokenizer" ([HF-COMP](https://huggingface.co/docs/tokenizers/components)). The general point is that a true inverse needs the decoder that matches the encoder. HF also tracks offsets through normalization, so "you can always get the part of your original sentence that corresponds to a given token" ([HF-QT](https://huggingface.co/docs/tokenizers/quicktour)).

## Pre-tokenization and special tokens set the edges

Hugging Face frames encoding as four stages, normalization, pre-tokenization, model and post-processing, with only the model trained ("the part of the pipeline that needs training on your corpus") and only the model mandatory ([HF-PIPE](https://huggingface.co/docs/tokenizers/pipeline); [HF-COMP](https://huggingface.co/docs/tokenizers/components)). In HF's words, "Pre-tokenization is the act of splitting a text into smaller objects that give an upper bound to what your tokens will be": it splits text into "words", and "your final tokens will be parts of those words", so "no token is bigger than a word returned by the pre-tokenizer" ([HF-QT](https://huggingface.co/docs/tokenizers/quicktour)). Changing the normalizer means you "should probably retrain it from scratch"; changing the post-processor does not require retraining.

GPT-2 shows why pre-tokenization matters even with bytes. Naive byte-level BPE produced "many versions of common words like dog since they occur in many variations such as dog. dog! dog?", so OpenAI chose to "prevent BPE from merging across character categories for any byte sequence", with "an exception for spaces which significantly improves the compression efficiency" ([GPT2](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)). The paper does not define "character categories"; the regex lives in released code that was not read. The visible result is documented across sources. The Cookbook says "Spaces are usually grouped with the starts of words (e.g., " is" instead of "is " or " "+"is")" ([CB](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)), and OpenAI's concepts page says "the first token of each word typically starts with a space character", decomposing " tokenization" into " token" and "ization" ([O-KC](https://developers.openai.com/api/docs/concepts)). The HF course's GPT-2 pre-tokenizer output shows 'Ġis' and 'Ġthe' ([LLM-6.5](https://huggingface.co/learn/llm-course/chapter6/5)). A local run under `cl100k_base` gave four different IDs for "hello", " hello", "Hello" and " Hello" (15339, 24748, 9906, 22691). That case and space sensitivity is observed behaviour, not a documented claim.

SentencePiece takes the opposite route. Existing tools "assume that the input is pre-tokenized into word sequences," which suits "European languages where words are segmented with whitespaces", whereas SentencePiece "can train subword models directly from raw sentences" ([SP v1](https://arxiv.org/pdf/1808.06226v1)). The Transformers docs give the reason in modern terms: whitespace splitting "doesn't work for languages like Chinese and Japanese that don't use spaces" ([TF-SUM](https://huggingface.co/docs/transformers/tokenizer_summary)). HF's `Metaspace` pre-tokenizer reproduces the convention by replacing whitespace "with a special char “▁” (U+2581)" ([HF-COMP](https://huggingface.co/docs/tokenizers/components)).

Special tokens sit outside the learned merges. SentencePiece "reserves vocabulary ids for special meta symbols, e.g., unknown symbol (<unk>), BOS (<s>), EOS (</s>) and padding (<pad>)" ([SP v1](https://arxiv.org/pdf/1808.06226v1)). In HF they are passed to the trainer "(they are not used at all during training) so that they get inserted in the vocabulary", and the post-processor inserts them, for example "[CLS]" or "[SEP]" ([HF-QT](https://huggingface.co/docs/tokenizers/quicktour)). GPT-2 has exactly one: "In the case of GPT-2, the only special token is "<|endoftext|>"" ([LLM-6.5](https://huggingface.co/learn/llm-course/chapter6/5)). tiktoken treats them as a security boundary. "Special tokens are artificial tokens used to unlock capabilities from a model," and because "they can be used to trick a model", "by default, encode will raise an error if it encounters text that corresponds to a special token" (`disallowed_special="all"`) ([TT-CORE](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py)). Locally, `cl100k_base.encode("<|endoftext|>")` raised a ValueError. With `allowed_special="all"` it returned [100257]. With `disallowed_special=()` it returned seven ordinary tokens. That makes a strong demo of the same string mapping to one special ID or several plain ones.

## Bigger vocabularies buy shorter sequences

Sennrich states the tension directly. There are "strong incentives to minimize the vocabulary size of neural models", yet "an increase in text length reduces efficiency" "and increases the distances over which neural models need to pass information." ([SEN v5](https://arxiv.org/pdf/1508.07909v5), §3.1). Footnote 8 adds that encoder-decoder cost "is at least linear to sequence length, and oversplitting harms efficiency." Table 1 quantifies the trade-off on the German training corpus.

| Segmentation | Tokens | Types | UNK |
|---|---|---|---|
| none (words) | 100 m | 1,750,000 | 1079 |
| characters | 550 m | 3,000 | 0 |
| character bigrams | 306 m | 20,000 | 34 |
| character trigrams | 214 m | 120,000 | 59 |
| BPE | 112 m | 63,000 | 0 |
| BPE (joint) | 111 m | 82,000 | 32 |

*Source: [SEN v5](https://arxiv.org/pdf/1508.07909v5), Table 1, p.6 (ACL p.1720).*

By the note-taker's arithmetic (not a sentence in the paper), characters make text **5.5× longer** than words, while BPE is only **12% longer** with a vocabulary about **28× smaller** and zero unknowns. That is the slider visual for the lesson. Kudo describes the same balance as "the vocabulary size and the step size (the number of tokens required to encode the sentence)" and notes that "with a small fixed size of vocabulary (usually 16k to 32k), the number of required symbols to encode a sentence will not significantly increase" ([KUDO v1](https://arxiv.org/pdf/1804.10959v1)). GPT-2 cites "32,000 to 64,000 token vocabularies often used with BPE" ([GPT2](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)). The Transformers docs give the two endpoints in plain language: word-level vocabulary "becomes extremely large because every unique word requires its own token", while at character level "sequences become much longer" and "A character like "l" carries far less meaning than "love"" ([TF-SUM](https://huggingface.co/docs/transformers/tokenizer_summary)). No source treats the chosen size as principled. Sennrich admits "our choice of vocabulary size is somewhat arbitrary, and mainly motivated by comparison to prior work."

Modern encodings show the same trend in practice. tiktoken says BPE "compresses the text" and that "On average, in practice, each token corresponds to about 4 bytes" ([TT-README](https://github.com/openai/tiktoken)). The Cookbook's stored outputs show "お誕生日おめでとう" taking **14 tokens in r50k_base, 9 in cl100k_base and 8 in o200k_base** ([CB](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb)). A local run on an 80-byte English/Japanese sample gave 27, 27, 23 and 20 tokens (2.96 to 4.00 bytes per token) across r50k, p50k, cl100k and o200k. The figure of 4 bytes per token is an English-heavy average, not a constant. No source measures how vocabulary size affects LLM context-window cost directly; the trend should be taught as observed, not as a law.

## Provider APIs count under each model's own tokenizer

**Anthropic.** `POST /v1/messages/count_tokens` (SDK `messages.count_tokens` / `messages.countTokens`) "accepts the same structured list of inputs for creating a message, including support for system prompts, tools, images, and PDFs", and returns `input_tokens` ([A-TC](https://platform.claude.com/docs/en/build-with-claude/token-counting)). Anthropic labels the result plainly: "The token count is an estimate", and actual usage "might differ by a small amount." Counting "is free to use but subject to requests per minute rate limits based on your usage tier." Those limits are "separate and independent" from message creation, and counting runs "without using caching logic." The tokenizer is model-specific. "Claude 4.7 and later models and Claude Mythos Preview use a newer tokenizer", on which "The same input text produces approximately 30 percent more tokens than on earlier models", and the endpoint "counts under the tokenizer of the model you pass." The pricing page adds that "Claude Sonnet 4.6 and earlier models use the previous tokenizer" ([A-PR](https://platform.claude.com/docs/en/about-claude/pricing)). The Opus 5.5 migration guide gives a range instead: "roughly 1x to 1.35x as many tokens when processing text compared to models before Claude Opus 4.7 (up to ~35% more, varying by content)." ([A-MG](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)). The glossary scopes the old rule of thumb to "earlier models, on which a token represents approximately 3.5 English characters", and says characters per token "depends on the model and the language" ([A-GL](https://platform.claude.com/docs/en/about-claude/glossary)). The models overview turns this into a concrete budget: **1M tokens ≈ 555k words on the current tokenizer versus about 750k words before it** ([A-MO](https://platform.claude.com/docs/en/models/overview)). Context windows ("up to 1M tokens, depending on the model"), prices ("$5 / MTok is $5 for every million tokens") and rate limits (RPM, ITPM, OTPM) are all denominated in tokens ([A-CW](https://platform.claude.com/docs/en/build-with-claude/context-windows); [A-RL](https://platform.claude.com/docs/en/api/rate-limits)).

**Google.** The Gemini API page opens with "For Gemini models, a token is equivalent to about 4 characters. 100 tokens is equal to about 60-80 English words" ([G-TOK](https://ai.google.dev/gemini-api/docs/tokens), last updated 2026-10-13 UTC). `count_tokens` "Returns the total number of tokens in the input only", and actual usage comes from "the usage on the interaction response" (fields such as `total_input_tokens` and `total_thought_tokens`). The string `usage_metadata` no longer appears on this page. Every modality is tokenized at stated rates: images are "258 tokens" up to 384 px or per 768×768 tile, and audio is "32 tokens per second". The video rate conflicts within the page, "263 tokens per second" in one place and "~100 tokens/second by default (low resolution) or ~300 tokens/second (high resolution)" in a table. The Cloud docs, which now redirect from "Vertex AI" to "Gemini Enterprise Agent Platform", say "The way that data is converted into tokens depends on the tokenizer used", that multimodal counts "are an estimation based on the chosen media_resolution", and that "The accurate usage for billing is only available after execution within the response's usage_metadata" ([G-LIST](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/list-token); [G-CT](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/get-token-count)). The Cloud page says CountTokens has "no charge or quota restriction" and, in the next sentence, "The maximum quota for the CountTokens API is 3000 requests per minute." It also recommends the SDK's integrated tokenizer instead, and the list-tokens page (Preview) exposes token IDs for text-only prompts.

**OpenAI.** The concepts page says tokens "represent commonly occurring sequences of characters" and gives "As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text" ([O-KC](https://developers.openai.com/api/docs/concepts)). The newer input-token-count endpoint (`POST /v1/responses/input_tokens`) "accepts the same input format as the Responses API" and, in OpenAI's words, "returns the exact count the model will receive", including "formatting tokens used to represent request structure, such as message roles and boundaries" ([O-TC](https://developers.openai.com/api/docs/guides/token-counting)). The same guide marks the limits of local counting: "Local tokenizers like tiktoken work for plain text, but they have limitations", and "estimates like characters / 4 are inaccurate" for images and files. Which encoding a current model uses is documented only in tiktoken. `model.py` at tag 0.14.0 maps gpt-4o, gpt-4.1, gpt-5 and the o-series to `o200k_base`, gpt-4 and gpt-3.5-turbo to `cl100k_base`, and `gpt-oss-` to `o200k_harmony`, under a comment saying the table "will likely be replaced by an API endpoint" ([TT-MODEL](https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py)). A grep of OpenAI's full API docs export found zero mentions of `o200k_base`. The help-center article "What are tokens and how to count them" and the Tokenizer page both returned HTTP 403, so the familiar "100 tokens ≈ 75 words" phrasing is unverified.

The rules of thumb put side by side show why cross-provider comparison fails.

| Source | Rule of thumb as written | Unit | Scope stated |
|---|---|---|---|
| OpenAI concepts | "1 token is approximately 4 characters or 0.75 words for English text." | characters / words | English |
| Gemini API | "a token is equivalent to about 4 characters. 100 tokens is equal to about 60-80 English words." | characters / words | Gemini, English words |
| Anthropic glossary | "a token represents approximately 3.5 English characters" | characters | Pre-Opus-4.7 models only |
| Anthropic models overview | "1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7)" | words / characters | Current Claude tokenizer |
| tiktoken README | "each token corresponds to about 4 bytes." | **bytes** | "On average, in practice" |

No provider explicitly says "don't compare token counts across providers". That lesson claim is an inference from each provider's per-tokenizer statements and the mismatched ratios above.

## Conclusion

The sources support teaching a token as **an ID under a specific tokenizer**, not as a unit of text. The same string yields different IDs with or without a leading space, different counts under r50k, cl100k and o200k, and about 30% more tokens on newer Claude models, while every provider scopes its rule of thumb to English. The lesson can therefore "explode" tokenization in two independent halves. The first is a fully deterministic mechanism that a learner can replay by hand (base alphabet, ordered merges, decode by concatenation). The second is a pricing and limits layer whose numbers are provider-specific and dated, and which providers themselves describe with different precision ("estimate" versus "exact count"). Two subtleties are worth teaching because the sources trip over them. Merge *order* is essential but is stated outright only in the HF course and tiktoken, not in Sennrich. And "about 4" in the rules of thumb means characters in OpenAI's and Google's docs but bytes in tiktoken's README, which diverge sharply for non-ASCII text.

For Pass 2 the highest-value checks are narrow: verify Gage 1994 on a publisher copy, read GPT-2's released encoder code for the "character categories" regex, get a human to load the OpenAI help article and Tokenizer page in a browser, settle which Anthropic tokenizer-delta figure to cite (30% or up to 35%), resolve Gemini's video token rate, and rerun the local observations (OBS) in a clean environment so the lesson's demos match pinned library versions.

---

## Appendix A. Source register

All access dates are **2026-10-18**. "Version read" is the most precise version identifier the note-takers could record.

| ID | Title | Publisher | URL read | Version read | Access date |
|---|---|---|---|---|---|
| SEN | Neural Machine Translation of Rare Words with Subword Units (Sennrich, Haddow & Birch) | arXiv; ACL 2016 | https://arxiv.org/pdf/1508.07909v5 (cross-checked https://aclanthology.org/P16-1162.pdf) | arXiv v5, 10 Jun 2016. ACL 2016 Proceedings pp. 1715–1725; text identical to v5 except header and page numbers. arXiv page n = ACL page 1714+n | 2026-10-18 |
| GPT2 | Language Models are Unsupervised Multitask Learners (Radford et al.) | OpenAI | https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf | Undated 24-page PDF. Metadata CreationDate 2019-02-14; HTTP Last-Modified 25 Sep 2020. Not an ICML paper despite template metadata | 2026-10-18 |
| SP | SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing (Kudo & Richardson) | arXiv; EMNLP 2018 System Demonstrations | https://arxiv.org/pdf/1808.06226v1 (cross-checked https://aclanthology.org/D18-2012.pdf) | arXiv v1 (only), 19 Aug 2018. EMNLP 2018 Demos pp. 66–71; PDF page n = proceedings page 65+n | 2026-10-18 |
| KUDO | Subword Regularization: Improving Neural Network Translation Models with Multiple Subword Candidates (Kudo) | arXiv | https://arxiv.org/pdf/1804.10959v1 | arXiv v1 (only), 29 Apr 2018. ACL 2018 version not read | 2026-10-18 |
| GAGE | A New Algorithm for Data Compression (Gage), C Users Journal 12(2), Feb 1994 | Third-party archive (jacobfilipp.com) | https://jacobfilipp.com/DrDobbs/articles/CUJ/1994/9402/gage/gage.htm | HTML transcription. **Not publisher-hosted**; drdobbs.com copy unreachable (DNS) | 2026-10-18 |
| HF-PIPE | The tokenization pipeline | Hugging Face (tokenizers docs) | https://huggingface.co/docs/tokenizers/pipeline | Live default docs v1.0.0-rc.2. Source `pipeline.mdx` at commit a73dbb3 (file changed 3fe1b852de47, 2026-09-21). Stable PyPI tokenizers 0.23.3 | 2026-10-18 |
| HF-COMP | Components | Hugging Face (tokenizers docs) | https://huggingface.co/docs/tokenizers/components | Same as HF-PIPE | 2026-10-18 |
| HF-QT | Quicktour | Hugging Face (tokenizers docs) | https://huggingface.co/docs/tokenizers/quicktour | Same as HF-PIPE | 2026-10-18 |
| TF-SUM | Tokenization algorithms (formerly "Summary of the tokenizers") | Hugging Face (Transformers docs) | https://huggingface.co/docs/transformers/tokenizer_summary | Live default Transformers docs v5.20.1. Source `tokenizer_summary.md` at commit d88946453f94 (file changed 83eb94c1febf, 2026-02-17) | 2026-10-18 |
| LLM-6.5 | Byte-Pair Encoding tokenization (LLM Course, ch. 6.5) | Hugging Face | https://huggingface.co/learn/llm-course/chapter6/5 | Live page. Source `chapter6/5.mdx` at commit 8b893f0ede6c (file changed e05c3b637f0a, 2025-09-29) | 2026-10-18 |
| TT-README | tiktoken README | OpenAI (GitHub) | https://github.com/openai/tiktoken | Tag 0.14.0 = commit 4e71bbe0c078 (2026-08-17); PyPI 0.14.0. README changed bb5805d0a3ee (2025-02-14) | 2026-10-18 |
| TT-MODEL | tiktoken/model.py | OpenAI (GitHub) | https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py | Tag 0.14.0 (file changed 212b893ba940, 2026-08-17) | 2026-10-18 |
| TT-CORE | tiktoken/core.py | OpenAI (GitHub) | https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py | Tag 0.14.0 (file changed fa8b65d062fb, 2026-05-15) | 2026-10-18 |
| TT-EDU | tiktoken/_educational.py | OpenAI (GitHub) | https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/_educational.py | Tag 0.14.0 (file changed 05e66e8db7ef, 2024-10-03) | 2026-10-18 |
| TT-EXT | tiktoken_ext/openai_public.py | OpenAI (GitHub) | https://github.com/openai/tiktoken/blob/0.14.0/tiktoken_ext/openai_public.py | Tag 0.14.0 | 2026-10-18 |
| CB | How to count tokens with tiktoken (Cookbook notebook) | OpenAI (GitHub) | https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb | Repo HEAD 5bd6cb40b6b8 (2026-10-09). Notebook changed db3144982aa2 (2024-10-08) | 2026-10-18 |
| OBS | Local observation run (**not a source**) | n/a | `uv run --no-project --with tiktoken==0.14.0 --with tokenizers==0.23.3 python -I obs.py` | tiktoken 0.14.0, tokenizers 0.23.3; encoding files from OpenAI's public blob store (possibly cached); no API keys | 2026-10-18 |
| A-TC | Token counting | Anthropic | https://platform.claude.com/docs/en/build-with-claude/token-counting (redirected from docs.claude.com) | Live page, no "last updated" stamp (`.md` variant) | 2026-10-18 |
| A-API | Count tokens in a Message (API reference) | Anthropic | https://platform.claude.com/docs/en/api/messages/count_tokens | Live page, no stamp | 2026-10-18 |
| A-GL | Glossary | Anthropic | https://platform.claude.com/docs/en/about-claude/glossary (redirected from docs.claude.com) | Live page, no stamp | 2026-10-18 |
| A-CW | Context windows | Anthropic | https://platform.claude.com/docs/en/build-with-claude/context-windows | Live page, no stamp | 2026-10-18 |
| A-PR | Pricing | Anthropic | https://platform.claude.com/docs/en/about-claude/pricing | Live page, no stamp | 2026-10-18 |
| A-MO | Models overview | Anthropic | https://platform.claude.com/docs/en/models/overview (redirected from /about-claude/models/overview) | Live page, no stamp | 2026-10-18 |
| A-MG | Migration guide (Opus 5.5) | Anthropic | https://platform.claude.com/docs/en/models/opus-5-5/migration-guide | Live page, no stamp | 2026-10-18 |
| A-RL | Rate limits | Anthropic | https://platform.claude.com/docs/en/api/rate-limits | Live page, no stamp | 2026-10-18 |
| A-WN | What's new (legacy Claude 4.7 URL) | Anthropic | requested .../about-claude/models/whats-new-claude-4-7 → redirects to https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5.md | Live page; **no tokenizer mention**. Opus 4.7 path guess returned 404 | 2026-10-18 |
| G-TOK | Understand and count tokens | Google (Gemini API) | https://ai.google.dev/gemini-api/docs/tokens | **Last updated 2026-10-13 UTC** | 2026-10-18 |
| G-LIST | List and count tokens \| Gemini Enterprise Agent Platform | Google Cloud | https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/list-token (redirected from cloud.google.com/vertex-ai/...) | **Last updated 2026-10-15 UTC**; marked Preview (Pre-GA) | 2026-10-18 |
| G-CT | Use the Count Tokens API | Google Cloud | https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/get-token-count (redirected from cloud.google.com/vertex-ai/...) | **Last updated 2026-10-15 UTC** | 2026-10-18 |
| O-KC | Key concepts | OpenAI | https://developers.openai.com/api/docs/concepts (redirected from platform.openai.com/docs/concepts) | Live page, no stamp (`.md` variant) | 2026-10-18 |
| O-TC | Counting tokens | OpenAI | https://developers.openai.com/api/docs/guides/token-counting | Live page, no stamp | 2026-10-18 |
| O-ADV | Advanced usage | OpenAI | https://developers.openai.com/api/docs/guides/advanced-usage | Live page, no stamp; **contains legacy gpt-3.5 content** | 2026-10-18 |
| O-IDX | API docs index (llms.txt / llms-full.txt) | OpenAI | https://developers.openai.com/api/docs/llms.txt | Live page | 2026-10-18 |
| O-HELP | What are tokens and how to count them? | OpenAI Help Center | https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them | **Unreachable: HTTP 403** bot challenge (curl and WebFetch) | 2026-10-18 |
| O-TOOL | Tokenizer | OpenAI | https://platform.openai.com/tokenizer | **Unreachable: HTTP 403** bot challenge | 2026-10-18 |

---

## Appendix B. Claims table

Confidence reflects source quality and how directly the excerpt states the claim. **Re-check in Pass 2:** **Yes** means a specific concern is noted. **Spot** means an undated live page, so confirm the wording is unchanged before publishing. **No** means a pinned or archival source, stable. In Markdown cells, pipe characters inside excerpts are escaped as `\|`; the source text has a plain `|`. Locators for SEN are arXiv v5 pages, with ACL pages added where recorded. For SP and KUDO they are arXiv v1 pages.

### B1. BPE training

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| T01 | Sennrich adapted Gage's compression algorithm to word segmentation | SEN | §1 contributions, p.2 (ACL p.1716) | "We adapt byte pair encoding (BPE) (Gage, 1994), a compression algorithm, to the task of word segmentation." | high | No |
| T02 | Original BPE replaces the most frequent byte pair with an unused byte | SEN | §3.2, p.3 | "a simple data compression technique that iteratively replaces the most frequent pair of bytes in a sequence with a single, unused byte" | high | No |
| T03 | Gage's own description of the algorithm | GAGE | Article body, ¶3 (no page numbers) | "finding the most frequently occurring pairs of adjacent bytes in the data and replacing all instances of the pair with a byte" | medium | **Yes**: third-party mirror; verify on publisher copy, pp. 23–38 |
| T04 | Gage repeats until no further compression | GAGE | Article body | "The algorithm repeats this process until no further compression is possible" | medium | **Yes**: same as T03 |
| T05 | Sennrich merges characters, not bytes | SEN | §3.2, p.3 | "Instead of merging frequent pairs of bytes, we merge characters or character sequences." | high | No |
| T06 | Training starts from characters plus an end-of-word symbol | SEN | §3.2, p.3 | "we initialize the symbol vocabulary with the character vocabulary, and represent each word as a sequence of characters, plus a special end-of-word symbol ‘·’" | high | No. Prose uses ‘·’ (U+00B7), code uses `</w>`; lesson must pick one |
| T07 | Count all pairs, merge the most frequent, repeat | SEN | §3.2, p.3 | "We iteratively count all symbol pairs and replace each occurrence of the most frequent pair (‘A’, ‘B’) with a new symbol ‘AB’." | high | No |
| T08 | Each merge creates a character n-gram symbol | SEN | §3.2, p.3 | "Each merge operation produces a new symbol which represents a character n-gram." | high | No |
| T09 | Counting runs on a frequency-weighted word dictionary | SEN | §3.2, p.3 | "The algorithm can thus be run on the dictionary extracted from a text, with each word being weighted by its frequency." | high | No |
| T10 | No merges across word boundaries | SEN | §3.2, p.3 | "For efficiency, we do not consider pairs that cross word boundaries." | high | No |
| T11 | Final vocabulary = initial vocabulary + merges | SEN | §3.2, p.3 | "The final symbol vocabulary size is equal to the size of the initial vocabulary, plus the number of merge operations" | high | No |
| T12 | Number of merges is the only hyperparameter | SEN | §3.2, p.3 | "the latter is the only hyperparameter of the algorithm." | high | No ("the latter" = number of merges) |
| T13 | Algorithm 1 toy vocabulary uses `</w>` | SEN | Algorithm 1, p.4 (ACL p.1718) | "vocab = {'l o w </w>' : 5, 'l o w e r </w>' : 2," | high | **Yes**: differs from Figure 1 caption; rerun if the lesson animates it |
| T14 | Figure 1 toy merges | SEN | Fig. 1, p.4 | "r · → r·" / "l o → lo" / "lo w → low" / "e r· → er·" | high | **Yes**: caption dictionary {low, lowest, newer, wider} ≠ code vocab |
| T15 | Training starts from unique words after normalization and pre-tokenization | LLM-6.5 | "Training algorithm" | "BPE training starts by computing the unique set of words used in the corpus (after the normalization and pre-tokenization steps are completed)" | high | Spot |
| T16 | Base vocabulary = all symbols used in those words | LLM-6.5 | "Training algorithm" | "then building the vocabulary by taking all the symbols used to write those words." | high | Spot |
| T17 | A "pair" means two consecutive tokens within a word | LLM-6.5 | "Training algorithm" | "the BPE algorithm will search for the most frequent pair of existing tokens (by "pair," here we mean two consecutive tokens in a word)." | high | Spot |
| T18 | Merge the most frequent pair and repeat | LLM-6.5 | "Training algorithm" | "That most frequent pair is the one that will be merged, and we rinse and repeat for the next step." | high | Spot |
| T19 | Training stops at the desired vocabulary size | LLM-6.5 | "Training algorithm" | "we add new tokens until the desired vocabulary size is reached by learning merges" | high | Spot |
| T20 | Worked example: first merge is u+g → ug (20 occurrences) | LLM-6.5 | "Training algorithm" | "Thus, the first merge rule learned by the tokenizer is ("u", "g") -> "ug"" | high | Optional: rerun the toy corpus locally |
| T21 | Hand-written and library trainers break ties differently | LLM-6.5 | "Implementing BPE", Tip | "Using train_new_from_iterator() on the same corpus won't result in the exact same vocabulary." | high | Spot |
| T22 | BPE starts from characters and merges the most frequent adjacent pair | TF-SUM | "Byte pair encoding (BPE)", step 3 | "BPE starts with individual characters and iteratively merges the most frequent adjacent pair." | high | Spot (page retitled) |
| T23 | Target vocabulary = base + merges | TF-SUM | BPE, step 5 | "BPE continues learning merge rules until it reaches the target vocabulary size, which equals the base vocabulary size plus the number of merges." | high | Spot |
| T24 | GPT-1: 40,478 = 478 base + 40,000 merges | TF-SUM | BPE, step 5 | "GPT uses BPE with a vocabulary size of 40,478 (478 base tokens + 40,000 merges)." | high | **Yes**: secondary; GPT-1 paper not read |
| T25 | HF Components description of BPE | HF-COMP | "Models", BPE row | "The Byte-Pair-Encoding works by starting with characters, while merging those that are the most frequently seen together, thus creating new tokens." | high | Spot (v1 rc docs) |
| T26 | SentencePiece sets final vocabulary size, not merge count | SP | §3.3, p.3 | "While subword-nmt specifies the number of merge operations, SentencePiece specifies the final size of vocabulary" | high | No |
| T27 | Reason: merge count is BPE-specific | SP | §3.3, p.3 | "as the number of merge operations is a BPE specific parameter and can not be applicable to other segmentation algorithms" | high | No |
| T28 | SentencePiece BPE training is O(N log N) with a heap | SP | §3.2, p.3 | "SentencePiece adopts an O(N log(N)) algorithm in which the merged symbols are managed by a binary heap (priority queue)." | high | No |
| T29 | tiktoken's educational trainer picks the most common pair | TT-EDU | `bpe_train` | "# Find the most common pair. This will become our next token" | high | No (pinned tag) |
| T30 | Merge counts used in Sennrich's experiments | SEN | §4.1, p.5 (ACL p.1719) | "Table 1 shows BPE with 59 500 merge operations, and joint BPE with 89 500 operations." | high | No |
| T31 | Joint BPE learns on the union of source and target vocabularies | SEN | §3.2, p.4 | "learning the encoding on the union of the two vocabularies (which we call joint BPE)" | high | No |

### B2. Applying merges to new text; BPE versus unigram

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| E01 | At test time, split into characters and apply learned merges | SEN | §3.2, p.4 | "At test time, we first split words into sequences of characters, then apply the learned operations to merge the characters into larger, known symbols." | high | **Yes**: learned order is implied, not stated; cite E05/E06 for order |
| E02 | Unseen word segmented from known units | SEN | §3.2, p.4 | "In our example, the OOV ‘lower’ would be segmented into ‘low er·’." | high | No |
| E03 | Only unknown characters remain unknown | SEN | Footnote 3, p.4 | "The only symbols that will be unknown at test time are unknown characters" | high | No |
| E04 | Learned merges give a test segmentation with no unknown symbols | SEN | §4.1, p.5 | "the learned merge operations can be applied to the test set to obtain a segmentation with no unknown symbols." | high | No |
| E05 | Inference applies merges in learned order | LLM-6.5 | "Tokenization algorithm" | "1. Normalization 2. Pre-tokenization 3. Splitting the words into individual characters 4. Applying the merge rules learned in order on those splits" | high | Spot |
| E06 | tiktoken ranks encode merge priority | TT-EDU | `SimpleBytePairEncoding.__init__` | "# A dictionary mapping token bytes to their ranks. The ranks correspond to merge priority" | high | No |
| E07 | tiktoken encode loop merges one pair and repeats | TT-EDU | `bpe_encode` | "# Otherwise, merge that pair and leave the rest unchanged. Then repeat." | high | No |
| E08 | BPE test segmentation reuses the same merge operations | KUDO | §3.1, p.3 | "Subword segmentation is performed by applying the same merge operations to the test sentence." | high | No |
| E09 | BPE is greedy and deterministic | KUDO | §3.1, p.3 | "BPE is based on a greedy and deterministic symbol replacement, which can not provide multiple segmentations with probabilities." | high | No |
| E10 | One vocabulary admits many segmentations | KUDO | Abstract, p.1 | "subword segmentation is potentially ambiguous and multiple segmentations are possible even with the same vocabulary." | high | No |
| E11 | BPE yields a unique sequence; alternatives exist | KUDO | §1, p.1 | "BPE encodes a sentence into a unique subword sequence. However, a sentence can be represented in multiple subword sequences even with the same vocabulary." | high | No |
| E12 | Example segmentations of "Hello World" with IDs | KUDO | Table 1, p.1 | "Multiple subword sequences encoding the same sentence “Hello World”" | high | No. Rows "Hell/o/ world" → 13586 137 255; text layer drops the space meta-symbol |
| E13 | Unigram LM assumes independent subwords | KUDO | §3.2, p.3 | "The unigram language model makes an assumption that each subword occurs independently" | high | No |
| E14 | Best segmentation via Viterbi | KUDO | §3.2, p.3 | "x∗ is obtained with the Viterbi algorithm (Viterbi, 1967)." | high | No |
| E15 | Subword probabilities estimated by EM | KUDO | §3.2, p.3 | "subword occurrence probabilities p(xi) are estimated via the EM algorithm" | high | No |
| E16 | Unigram training starts from a big seed vocabulary | KUDO | §3.2, p.3 | "Heuristically make a reasonably big seed vocabulary from the training corpus." | high | No |
| E17 | Prune by loss, keep top η% | KUDO | §3.2, p.3 | "Sort the symbols by lossi and keep top η % of subwords (η is 80, for example)." | high | No |
| E18 | Repeat until target vocabulary size | KUDO | §3.2, p.3 | "Repeat the following steps until \|V\| reaches a desired vocabulary size." | high | No |
| E19 | Single characters always kept | KUDO | §3.2, p.3 | "we always keep the subwords consisting of a single character to avoid out-of-vocabulary." | high | No |
| E20 | Unigram can output multiple segmentations with probabilities | KUDO | §3.4, p.4 | "the unigram language model is more flexible as it is based on a probabilistic language model and can output multiple segmentations with their probabilities" | high | No |
| E21 | Subword regularization samples per update | KUDO | §3.3, p.4 | "Subword regularization samples one subword segmentation from the distribution P (x\|X) for each parameter update." | high | No |
| E22 | BPE ≈ unigram without regularization | KUDO | §5.2, p.6 | "BPE and unigram language model without subword regularization (l = 1) show almost comparable BLEU scores." | high | No |
| E23 | Regularization adds +1 to 2 BLEU | KUDO | §5.2, p.6 | "subword regularization (l >1) boosted BLEU scores quite impressively (+1 to 2 points) in all language pairs except for WMT14 (en→cs) dataset." | high | No. Footnote 11 interleaved in text layer |
| E24 | Unigram also does not cross word boundaries | KUDO | §3.2, p.4 | "Similar to (Sennrich et al., 2016), we do not consider subwords that cross word boundaries." | high | No |
| E25 | WordPiece differs from BPE | KUDO | Footnote 1, p.3 | "Strictly speaking, wordpiece model (Schuster and Nakajima, 2012) is different from BPE." | high | No. Fn 2: "uses a likelihood instead of frequency." |
| E26 | HF: Unigram is not rule-based-deterministic | HF-COMP | "Models", Unigram row | "This is different from BPE in the way that this is not deterministic based on a set of rules applied sequentially." | high | Spot |
| E27 | Transformers: BPE deterministic, Unigram probabilistic | TF-SUM | "Unigram" | "Unlike BPE, which is deterministic and based on merge rules, Unigram is probabilistic and can sample different tokenizations during training." | high | Spot |
| E28 | SentencePiece sampling returns different pieces per call | SP | Fig. 6, p.5 | "[’_’, ’New’, ’_York’]" | high | No. Other output: "[’_’, ’N’, ’e’, ’w’, ’_York’]" |
| E29 | WordPiece marks word-internal tokens with ## | HF-COMP | "Models", WordPiece row | "It uses the famous ## prefix to identify tokens that are part of a word (ie not starting a word)." | high | Spot |

### B3. Encode/decode round trip

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| R01 | SentencePiece decoder is the inverse of the encoder on normalized text | SP | §3.1, p.2 (EMNLP p.67) | "SentencePiece implements the Decoder as an inverse operation of Encoder, i.e., Decode(Encode(Normalize(text))) = Normalize(text)." | high | No. Lossless relative to normalized text |
| R02 | Definition of lossless tokenization | SP | §3.1, p.2 | "We call this design lossless tokenization, in which all the information to reproduce the normalized text is preserved in the encoder’s output." | high | No |
| R03 | Default normalization is NFKC | SP | §3.4, p.3 | "By default, SentencePiece normalizes the input text with the Unicode NFKC normalization." | high | No |
| R04 | Whitespace treated as a normal symbol | SP | §3.1, p.2 | "Even whitespace is handled as a normal symbol." | high | No |
| R05 | Whitespace escaped as U+2581 | SP | §3.1, p.2 | "SentencePiece first escapes the whitespace with a meta symbol _ (U+2581), and tokenizes the input into an arbitrary subword sequence" | high | **Yes**: text layer shows ASCII "_"; confirm rendered glyph "▁" |
| R06 | Pre-tokenized output loses spacing information | SP | §3.1, p.2 | "The information that no space exists between “world” and “.” is not kept in the tokenized sequence." | high | No |
| R07 | subword-nmt's @@ cannot encode consecutive whitespace | SP | §3.1, p.3 | "it is not possible to encode consecutive whitespaces with this representation." | high | No |
| R08 | Example "Hello world." pieces (vocab_size=1000) | SP | Fig. 1, p.2 | "_He ll o _world ." | high | **Yes**: same glyph issue as R05; IDs 151 88 21 887 6 |
| R09 | End-of-word symbol lets the original tokenization be restored | SEN | §3.2, p.3 | "which allows us to restore the original tokenization after translation." | high | No |
| R10 | tiktoken: BPE is reversible and lossless | TT-README | "What is BPE anyway?" #1 | "It's reversible and lossless, so you can convert tokens back into the original text" | high | No |
| R11 | README round-trip assertion | TT-README | Top code block | `assert enc.decode(enc.encode("hello world")) == "hello world"` | high | No |
| R12 | tiktoken decode is lossy by default (invalid UTF-8) | TT-CORE | `Encoding.decode` docstring | "the default behaviour of this function is lossy, since decoded bytes are not guaranteed to be valid UTF-8." | high | No |
| R13 | Single-token decode can be lossy | CB | "4. Turn tokens into text" | "beware that it can be lossy for tokens that aren't on utf-8 boundaries." | high | No |
| R14 | HF default decoder removes special tokens and joins with spaces | HF-PIPE | "Decoding" | "The decoder will first convert the IDs back to tokens (using the tokenizer's vocabulary) and remove all special tokens, then join those tokens with spaces" | high | Spot |
| R15 | Default decoding of WordPiece output is not the inverse | HF-PIPE | "Decoding" | `"welcome to the tok ##eni ##zer ##s library ."` | high | Spot. With `decoders.WordPiece()`: "welcome to the tokenizers library." |
| R16 | ByteLevel decoder reverts the byte remapping | HF-COMP | "Decoders", ByteLevel row | "Reverts the ByteLevel PreTokenizer." | high | Spot |
| R17 | HF tracks alignment while normalizing | HF-COMP | "Normalizers" | "The specificity of tokenizers is that we keep track of the alignment while normalizing." | high | Spot |
| R18 | Offsets map tokens back to source text | HF-QT | "Using the tokenizer" | "you can always get the part of your original sentence that corresponds to a given token." | high | Spot |
| R19 | Observed: whole-string round trip exact for 4 encodings | OBS | n/a | n/a (observed `decode(encode(s)) == s` True for r50k, p50k, cl100k, o200k) | medium | **Yes**: observation; rerun in clean env |

### B4. Byte-level base alphabet and unknown tokens

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| B01 | An LM should model any string | GPT2 | §2.2, p.4 | "A general language model (LM) should be able to compute the probability of (and also generate) any string." | high | No |
| B02 | Pre-processing restricts model-able strings | GPT2 | §2.2, p.4 | "Current large scale LMs include pre-processing steps such as lowercasing, tokenization, and out-of-vocabulary tokens which restrict the space of model-able strings." | high | No |
| B03 | Pure byte-level LMs lagged word-level ones | GPT2 | §2.2, p.4 | "current byte-level LMs are not competitive with word-level LMs on large scale datasets such as the One Billion Word Benchmark" | high | No |
| B04 | BPE as middle ground between characters and words | GPT2 | §2.2, p.4 | "Byte Pair Encoding (BPE) (Sennrich et al., 2015) is a practical middle ground between character and word level language modeling" | high | No |
| B05 | Reference BPE operates on code points | GPT2 | §2.2, p.4 | "Despite its name, reference BPE implementations often operate on Unicode code points and not byte sequences." | high | No |
| B06 | Code-point base vocabulary would exceed 130,000 | GPT2 | §2.2, p.4 | "This would result in a base vocabulary of over 130,000 before any multi-symbol tokens are added." | high | No |
| B07 | Byte-level BPE needs 256 base symbols | GPT2 | §2.2, p.4 | "In contrast, a byte-level version of BPE only requires a base vocabulary of size 256." | high | No |
| B08 | Byte-level approach assigns probability to any Unicode string | GPT2 | §2.2, p.4 | "Since our approach can assign a probability to any Unicode string" | high | No |
| B09 | GPT-2 vocabulary 50,257; context 1024 | GPT2 | §2.3 "Model", p.4 | "The vocabulary is expanded to 50,257. We also increase the context size from 512 to 1024 tokens and a larger batchsize of 512 is used." | high | No. Cite §2.3, not §2.2 |
| B10 | 50,257 = 256 bytes + 50,000 merges + end-of-text | TF-SUM | "Byte-level BPE" | "GPT-2 uses byte-level BPE with a vocabulary size of 50,257 (256 byte tokens + 50,000 merges + special end-of-text token)." | high | Spot. Corroborated by B11/B12; GPT-2 paper itself gives no breakdown |
| B11 | tiktoken GPT-2 encoding declares 50,257 | TT-EXT | `def gpt2()` | `"explicit_n_vocab": 50257` | high | No |
| B12 | Observed: r50k_base = 50,256 ranks + 1 special | OBS | n/a | n/a (observed `n_vocab` 50257; `{'<\|endoftext\|>': 50256}`) | medium | **Yes**: rerun |
| B13 | Byte-level evaluation needs no lossy pre-processing | GPT2 | §3.1, p.4 | "Since our model operates on a byte level and does not require lossy pre-processing or tokenization, we can evaluate it on any language model benchmark." | high | No |
| B14 | HF ByteLevel remaps bytes to visible characters (from GPT-2) | HF-COMP | "Pre-tokenizers", ByteLevel row | "Splits on whitespaces while remapping all the bytes to a set of visible characters. This technique as been introduced by OpenAI with GPT-2" | high | Spot ("as been" is source typo) |
| B15 | ByteLevel base alphabet is 256 | HF-COMP | ByteLevel row | "a tokenizer using this only requires 256 characters as initial alphabet (the number of values a byte can have), as opposed to the 130,000+ Unicode characters." | high | Spot |
| B16 | ByteLevel needs no unknown token | HF-COMP | ByteLevel row | "it is absolutely unnecessary to have an unknown token using this since we can represent anything with 256 tokens" | high | Spot |
| B17 | Non-ASCII becomes unreadable but works | HF-COMP | ByteLevel row | "For non ascii characters, it gets completely unreadable, but it works nonetheless!" | high | Spot |
| B18 | "Ġ" marks a leading space in ByteLevel output | HF-COMP | ByteLevel row, Example | `"Hello", "Ġmy", Ġfriend", ",", "Ġhow", "Ġare", "Ġyou", "?"` | high | Spot (missing quote before Ġfriend is in source) |
| B19 | Byte-level BPE: base 256, every character included | LLM-6.5 | "Training algorithm", Tip | "This way the base vocabulary has a small size (256), but every character you can think of will still be included" | high | Spot |
| B20 | GPT-2 has no unknown token | LLM-6.5 | "Implementing BPE", Warning | "GPT-2 doesn’t actually have an unknown token (it’s impossible to get an unknown character when using byte-level BPE)" | high | Spot |
| B21 | Character-level BPE maps unseen characters to UNK | LLM-6.5 | "Training algorithm" | "If an example you are tokenizing uses a character that is not in the training corpus, that character will be converted to the unknown token." | high | Spot |
| B22 | Example: "mug" → [UNK], "ug" | LLM-6.5 | "Tokenization algorithm" | ""mug", however, will be tokenized as ["[UNK]", "ug"] since the letter "m" was not in the base vocabulary." | high | Spot |
| B23 | Emoji handling as a consequence of UNK | LLM-6.5 | "Training algorithm" | "That's one reason why lots of NLP models are very bad at analyzing content with emojis, for instance." | high | Spot |
| B24 | Byte-level BPE avoids "<unk>" | TF-SUM | "Byte-level BPE" | "Byte-level BPE uses 256 byte values as the base vocabulary instead, ensuring every word can be tokenized without the "<unk>" token." | high | Spot |
| B25 | tiktoken trainer requires vocab ≥ 256 | TT-EDU | `bpe_train` | "vocab_size must be at least 256, so we can encode all bytes" | high | No |
| B26 | Observed: ByteLevel alphabet 256; "café 😁" → `cafÃ©`, `ĠðŁĺģ` | OBS | n/a | n/a (observed, tokenizers 0.23.3) | medium | **Yes**: rerun |

### B5. Pre-tokenization, normalization, pipeline

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| P01 | HF encode pipeline stages | HF-PIPE | Intro | "When calling Tokenizer.encode or Tokenizer.encode_batch, the input text(s) go through the following pipeline:" | high | Spot. List: normalization, pre-tokenization, model, post-processing |
| P02 | Normalization cleans raw text | HF-PIPE | "Normalization" | "Normalization is, in a nutshell, a set of operations you apply to a raw string to make it less random or "cleaner"." | high | Spot |
| P03 | Normalization examples | HF-PIPE | "Normalization" | "Common operations include stripping whitespace, removing accented characters or lowercasing all text." | high | Spot |
| P04 | Changing normalization calls for retraining | HF-PIPE | "Normalization" | "Of course, if you change the way a tokenizer applies normalization, you should probably retrain it from scratch afterward." | high | Spot |
| P05 | Pre-tokenization bounds tokens | HF-PIPE | "Pre-Tokenization" | "Pre-tokenization is the act of splitting a text into smaller objects that give an upper bound to what your tokens will be" | high | Spot |
| P06 | Tokens are parts of pre-tokenized words | HF-PIPE | "Pre-Tokenization" | "the pre-tokenizer will split your text into "words" and then, your final tokens will be parts of those words." | high | Spot |
| P07 | No token bigger than a pre-token | HF-QT | "Training the tokenizer" | "Using a pre-tokenizer will ensure no token is bigger than a word returned by the pre-tokenizer." | high | Spot |
| P08 | Pre-tokenizer returns spans | HF-PIPE | "Pre-Tokenization" | "The output is a list of tuples, with each tuple containing one word and its span in the original sentence" | high | Spot |
| P09 | The model is the trained part | HF-PIPE | "Model" | "This is the part of the pipeline that needs training on your corpus (or that has been trained if you are using a pretrained tokenizer)." | high | Spot |
| P10 | The model splits words using learned rules | HF-PIPE | "Model" | "The role of the model is to split your "words" into tokens, using the rules it has learned." | high | Spot |
| P11 | The model maps tokens to IDs | HF-PIPE | "Model" | "It's also responsible for mapping those tokens to their corresponding IDs in the vocabulary of the model." | high | Spot |
| P12 | The model is the only mandatory component | HF-COMP | "Models" | "Models are the core algorithms used to actually tokenize, and therefore, they are the only mandatory component of a Tokenizer." | high | Spot |
| P13 | Naive byte BPE gives sub-optimal merges | GPT2 | §2.2, p.4 | "directly applying BPE to the byte sequence results in sub-optimal merges due to BPE using a greedy frequency based heuristic" | high | No |
| P14 | "dog." "dog!" "dog?" waste vocabulary | GPT2 | §2.2, p.4 | "We observed BPE including many versions of common words like dog since they occur in many variations such as dog. dog! dog?" | high | No |
| P15 | GPT-2 blocks merges across character categories | GPT2 | §2.2, p.4 | "To avoid this, we prevent BPE from merging across character categories for any byte sequence." | high | **Yes**: "categories" undefined; read OpenAI's released encoder regex |
| P16 | Exception for spaces | GPT2 | §2.2, p.4 | "We add an exception for spaces which significantly improves the compression efficiency while adding only minimal fragmentation of words across multiple vocab tokens." | high | No |
| P17 | Leading-space tokens in GPT-2 pre-tokenization output | LLM-6.5 | "Implementing BPE" | "defaultdict(int, {'This': 3, 'Ġis': 2, 'Ġthe': 1, 'ĠHugging': 1," | high | Spot. First learned merge `('Ġ', 't') -> 'Ġt'` |
| P18 | Spaces grouped with word starts (tiktoken) | CB | "How strings are typically tokenized" | "Spaces are usually grouped with the starts of words (e.g., " is" instead of "is " or " "+"is")." | high | No |
| P19 | First token of each word typically starts with a space | O-KC | "Tokens" | "Note that in a sentence, the first token of each word typically starts with a space character." | high | Spot |
| P20 | " tokenization" → " token" + "ization" | O-KC | "Tokens" | 'the string " tokenization" is decomposed as " token" and "ization"' | high | Spot. Encoding not named |
| P21 | Cookbook example split under cl100k_base | CB | Title cell | `["t", "ik", "token", " is", " great", "!"]` | high | No |
| P22 | tiktoken trainer comment shows the space byte starting a word | TT-EDU | `bpe_train` | `[b' ', b'w', b'o', b'r', b'l', b'd']` | high | No |
| P23 | Observed: case and leading space change IDs | OBS | n/a | n/a ("hello" 15339, " hello" 24748, "Hello" 9906, " Hello" 22691, cl100k_base) | medium | **Yes**: undocumented; rerun |
| P24 | SentencePiece trains from raw sentences | SP | Abstract, p.1 | "While existing subword segmentation tools assume that the input is pre-tokenized into word sequences, SentencePiece can train subword models directly from raw sentences" | high | No |
| P25 | Older tools assume whitespace-segmented languages | SP | §1, p.1 | "these tools are mainly designed for European languages where words are segmented with whitespaces." | high | No |
| P26 | SentencePiece is language independent | SP | §1, p.1 | "SentencePiece enables building a purely end-to-end system that does not depend on any language-specific processing." | high | No |
| P27 | Pre-tokenization was introduced for training efficiency | SP | §3.2, p.3 | "Such pre-tokenization was introduced for an efficient subword training (Sennrich et al., 2016)." | high | No |
| P28 | Whitespace splitting fails for Chinese and Japanese | TF-SUM | "SentencePiece" | "Standard BPE and Unigram assume whitespace separates words, which doesn't work for languages like Chinese and Japanese that don't use spaces." | high | Spot |
| P29 | SentencePiece includes "▁" in the vocabulary | TF-SUM | "SentencePiece" | "includes the space character, represented as "▁", in the vocabulary." | high | Spot |
| P30 | HF Metaspace replaces whitespace with ▁ | HF-COMP | "Pre-tokenizers", Metaspace row | "Splits on whitespaces and replaces them with a special char “▁” (U+2581)" | high | Spot |
| P31 | SentencePiece's four components | SP | §2, p.2 | "SentencePiece comprises four main components: Normalizer, Trainer, Encoder, and Decoder." | high | No |

### B6. Vocabulary size versus sequence length

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| V01 | Word-level NMT vocabularies were 30k–50k words | SEN | §1, p.1 | "The vocabulary of neural models is typically limited to 30 000–50 000 words" | high | No |
| V02 | Translation is open-vocabulary | SEN | Abstract, p.1 | "Neural machine translation (NMT) models typically operate with a fixed vocabulary, but translation is an open-vocabulary problem." | high | No |
| V03 | Incentive to minimize vocabulary | SEN | §3.1, p.3 | "there are strong incentives to minimize the vocabulary size of neural models to increase time and space efficiency" | high | No |
| V04 | Longer text reduces efficiency | SEN | §3.1, p.3 | "we also want a compact representation of the text itself, since an increase in text length reduces efficiency" | high | No |
| V05 | Longer text increases information-passing distance | SEN | §3.1, p.3 | "and increases the distances over which neural models need to pass information." | high | No |
| V06 | Explicit vocabulary-size versus text-size trade-off | SEN | §3.1, p.3 | "A simple method to manipulate the trade-off between vocabulary size and text size is to use shortlists of unsegmented words" | high | No |
| V07 | BPE gives good compression | SEN | §3.1, p.3 | "lets us learn a vocabulary that provides a good compression rate of the text." | high | No |
| V08 | Sequence length versus vocabulary size trade-off | SEN | §4.1, p.5 | "Character n-grams allow for different trade-offs between sequence length (# tokens) and vocabulary size (# types), depending on the choice of n." | high | No |
| V09 | BPE allows shorter sequences | SEN | §4.1, p.5 | "the more compact representation of BPE allows for shorter sequences, and that the attention model operates on variable-length units." | high | No |
| V10 | Cost is at least linear in sequence length | SEN | Footnote 8, p.5 | "The time complexity of encoder-decoder architectures is at least linear to sequence length, and oversplitting harms efficiency." | high | No |
| V11 | German corpus BPE row: 112 m tokens, 63,000 types, 0 UNK | SEN | Table 1, p.6 (ACL p.1720) | "BPE 112 m 63 000 0" | high | No. Full table in body |
| V12 | Vocabulary size choice was arbitrary | SEN | §6, p.9 | "our choice of vocabulary size is somewhat arbitrary, and mainly motivated by comparison to prior work." | high | No |
| V13 | BPE balances vocabulary size and step size | KUDO | §3.1, p.3 | "it can effectively balance the vocabulary size and the step size (the number of tokens required to encode the sentence)" | high | No |
| V14 | Typical small vocabularies 16k–32k | KUDO | §3.1, p.3 | "only with a small fixed size of vocabulary (usually 16k to 32k), the number of required symbols to encode a sentence will not significantly increase" | high | No |
| V15 | Limiting vocabulary increases unknown words | KUDO | §1, p.1 | "limiting vocabulary size increases the amount of unknown words, which makes the translation inaccurate especially in an open vocabulary setting." | high | No |
| V16 | Typical BPE vocabularies 32k–64k | GPT2 | §2.2, p.4 | "This is prohibitively large compared to the 32,000 to 64,000 token vocabularies often used with BPE." | high | No |
| V17 | Subword units sit between words and characters | TF-SUM | Intro | "They split text into units between words and characters, keeping the vocabulary compact while still capturing meaningful pieces." | high | Spot |
| V18 | Common words intact, rare words decompose | TF-SUM | Intro | "Common words stay intact as single tokens, and rare or unknown words decompose into subwords." | high | Spot |
| V19 | Same word splits differently depending on vocabulary | TF-SUM | Intro | "annoyingly might be split into ["annoying", "ly"] or ["annoy", "ing", "ly"] depending on the vocabulary." | high | Spot |
| V20 | Word-level vocabulary becomes extremely large | TF-SUM | "Word-level tokenization" | "Vocabulary size becomes extremely large because every unique word requires its own token, including all variations" | high | Spot |
| V21 | Word-level cannot handle new words | TF-SUM | "Word-level tokenization" | "Words not in the vocabulary map to an "<unk>" token, so the model can't handle new words." | high | Spot |
| V22 | Character-level: no UNK but much longer sequences | TF-SUM | "Character-level tokenization" | "The vocabulary is small and every word can be represented, so there's no "<unk>" problem. But sequences become much longer." | high | Spot |
| V23 | Characters carry less meaning | TF-SUM | "Character-level tokenization" | "A character like "l" carries far less meaning than "love", so performance suffers." | high | Spot |
| V24 | BPE builds unseen words, needs smaller vocabularies | HF-COMP | "Models", BPE row | "BPE is able to build words it has never seen by using multiple subword tokens, and thus requires smaller vocabularies" | high | Spot |
| V25 | BPE compresses text relative to bytes | TT-README | #3 | "It compresses the text: the token sequence is shorter than the bytes corresponding to the original text." | high | No |
| V26 | About 4 bytes per token on average | TT-README | #3 | "On average, in practice, each token corresponds to about 4 bytes." | high (as quoted) | **Yes**: English-heavy average; OBS gave 2.96–4.00 on EN/JA sample |
| V27 | Same Japanese string: 14 / 9 / 8 tokens across encodings | CB | "5. Comparing encodings" (stored output) | `r50k_base: 14 tokens` … `cl100k_base: 9 tokens` … `o200k_base: 8 tokens` | medium | **Yes**: stored output; tiktoken version not stated; rerun cells |
| V28 | Encodings differ in splitting, spaces and non-English handling | CB | "5. Comparing encodings" | "Different encodings vary in how they split words, group spaces, and handle non-English characters." | high | No |
| V29 | Observed token counts on an 80-byte EN/JA sample | OBS | n/a | n/a (r50k 27, p50k 27, cl100k 23, o200k 20 tokens) | medium | **Yes**: rerun |
| V30 | SentencePiece segmentation ~380× faster than subword-nmt on raw Japanese | SP | p.6 | "The segmentation speed of SentencePiece is about 380 times faster than that of subword-nmt in this setting." | high | No |

### B7. Special tokens

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| S01 | SentencePiece reserves IDs for meta symbols | SP | §3.3, p.3 | "SentencePiece reserves vocabulary ids for special meta symbols, e.g., unknown symbol (<unk>), BOS (<s>), EOS (</s>) and padding (<pad>)." | high | No |
| S02 | Post-processing adds special tokens | HF-PIPE | "Post-Processing" | "Post-processing is the last step of the tokenization pipeline, to perform any additional transformation to the Encoding before it's returned, like adding potential special tokens." | high | Spot |
| S03 | Changing the post-processor needs no retraining | HF-PIPE | "Post-Processing" | "you don't need to retrain a tokenizer after changing its post-processor." | high | Spot |
| S04 | Post-processor adds [CLS]/[SEP] | HF-QT | "Post-processing" | "We might want our tokenizer to automatically add special tokens, like "[CLS]" or "[SEP]". To do this, we use a post-processor." | high | Spot |
| S05 | Special tokens are inserted in the vocabulary but unused in training | HF-QT | "Training the tokenizer" | "(they are not used at all during training) so that they get inserted in the vocabulary." | high | Spot |
| S06 | GPT-2's only special token is end-of-text | LLM-6.5 | "Implementing BPE" | "In the case of GPT-2, the only special token is "<\|endoftext\|>"" | high | Spot |
| S07 | GPT-2 encoding: end-of-text at ID 50256 | TT-EXT | `def gpt2()` | `"special_tokens": {ENDOFTEXT: 50256}` | high | No |
| S08 | o200k_base special tokens | TT-EXT | `def o200k_base()` | `{ENDOFTEXT: 199999, ENDOFPROMPT: 200018}` | high | No. cl100k_base: ENDOFTEXT 100257, FIM 100258–100260 |
| S09 | What special tokens are | TT-CORE | `encode` docstring | "Special tokens are artificial tokens used to unlock capabilities from a model, such as fill-in-the-middle." | high | No |
| S10 | Why tiktoken is strict: special tokens can trick a model | TT-CORE | `encode` docstring | "they can be used to trick a model into doing something we don't want it to do." | high | No |
| S11 | encode raises on special-token text by default | TT-CORE | `encode` docstring | "by default, encode will raise an error if it encounters text that corresponds to a special token." | high | No |
| S12 | Default parameter value | TT-CORE | `Encoding.encode` signature | `disallowed_special: Literal["all"] \| Collection[str] = "all",` | high | No |
| S13 | Opt-out encodes special-token text as natural text | TT-CORE | `encode` docstring | "Setting disallowed_special to () will prevent this function from raising errors and cause all text corresponding to special tokens to be encoded as natural text." | high | No |
| S14 | Observed: ValueError / [100257] / 7 ordinary tokens | OBS | n/a | n/a (cl100k_base; `[27, 91, 8862, 728, 428, 91, 29]` with `disallowed_special=()`) | medium | **Yes**: rerun |

### B8. Encodings and model mapping (OpenAI / tiktoken)

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| M01 | tiktoken is OpenAI's BPE tokenizer | TT-README | Top | "tiktoken is a fast BPE tokeniser for use with OpenAI's models." | high | No |
| M02 | Models see token numbers, not text | TT-README | "What is BPE anyway?" | "Language models don't see text like you and I, instead they see a sequence of numbers (known as tokens)." | high | No |
| M03 | BPE works on arbitrary text | TT-README | #2 | "It works on arbitrary text, even text that is not in the tokeniser's training data" | high | No |
| M04 | BPE lets the model see common subwords | TT-README | #4 | "It attempts to let the model see common subwords." | high | No. Example "encod" + "ing" |
| M05 | Educational BPE module exists | TT-EDU | Module docstring | "This is an educational implementation of the byte pair encoding algorithm." | high | No |
| M06 | gpt-4o (and gpt-4.1, gpt-5, o1/o3/o4-mini) → o200k_base | TT-MODEL | `MODEL_TO_ENCODING` | `"gpt-4o": "o200k_base",` | high | **Yes**: dated mapping |
| M07 | gpt-4 / gpt-3.5-turbo / text-embedding-3-small → cl100k_base | TT-MODEL | `MODEL_TO_ENCODING` | `"gpt-4": "cl100k_base",` | high | **Yes**: dated |
| M08 | Legacy models → p50k_base / r50k_base | TT-MODEL | `MODEL_TO_ENCODING` | `"text-davinci-003": "p50k_base",` / `"davinci": "r50k_base",` | high | No |
| M09 | gpt-oss → o200k_harmony | TT-MODEL | `MODEL_PREFIX_TO_ENCODING` | `"gpt-oss-": "o200k_harmony",` | high | **Yes**: dated |
| M10 | Mapping may move to an API endpoint | TT-MODEL | Comment above `MODEL_PREFIX_TO_ENCODING` | "# TODO: these will likely be replaced by an API endpoint" | high | **Yes**: watch for change |
| M11 | Prefix matching covers new model versions | TT-MODEL | `encoding_name_for_model` | "# Prefix matching avoids needing library updates for every model version release" | high | No |
| M12 | tiktoken speed claim | TT-README | "Performance" | "tiktoken is between 3-6x faster than a comparable open source tokeniser" | high | **Yes**: benchmark against tokenizers 0.13.2 is dated |
| M13 | Different models use different encodings | CB | "Encodings" | "Encodings specify how text is converted into tokens. Different models use different encodings." | high | No |
| M14 | Cookbook says "three" encodings but lists four | CB | "Encodings" | "tiktoken supports three encodings used by OpenAI models:" | high | No (internal inconsistency; table predates gpt-4.1/gpt-5) |
| M15 | p50k_base ≈ r50k_base for non-code text | CB | "Encodings" | "Note that p50k_base overlaps substantially with r50k_base, and for non-code applications, they will usually give the same tokens." | high | No |
| M16 | Encoding files download on first use | CB | "2. Load an encoding" | "The first time this runs, it will require an internet connection to download." | high | No |
| M17 | No OpenAI platform doc names o200k_base | O-IDX (llms-full.txt grep) | n/a | n/a (0 occurrences) | low | **Yes**: absence finding |

### B9. Counting tokens with provider APIs

| ID | Claim | Source | Locator | Verbatim excerpt (≤25 words) | Conf. | Re-check in Pass 2 |
|---|---|---|---|---|---|---|
| A01 | Anthropic count_tokens takes Messages inputs | A-TC | "How to count message tokens" | "The token counting endpoint accepts the same structured list of inputs for creating a message, including support for system prompts, tools, images, and PDFs." | high | Spot |
| A02 | Response gives total input tokens | A-TC | "How to count message tokens" | "The response contains the total number of input tokens." | high | Spot. Example `{ "input_tokens": 14 }` |
| A03 | Anthropic count is an estimate | A-TC | Note | "The token count is an estimate." | high | Spot |
| A04 | Actual may differ slightly | A-TC | Note | "In some cases, the actual number of input tokens used when creating a message might differ by a small amount." | high | Spot |
| A05 | System-added tokens not billed | A-TC | Note | "You are not billed for system-added tokens. Billing reflects only your content." | high | Spot |
| A06 | All active models support counting | A-TC | "Supported models" | "All active models support token counting." | high | Spot |
| A07 | API reference: counts without creating a message | A-API | "Count tokens in a Message" | "The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it." | high | Spot |
| A08 | Other server tools return an error | A-TC | "Count tokens in messages with tools" | "Requests that include other server tools return an error." | high | **Yes**: feature-specific |
| A09 | Current-turn thinking counts as input | A-TC | "Count tokens in messages with thinking" | "Current assistant turn thinking does count toward your input tokens" | high | Spot |
| A10 | Free but RPM-limited by tier | A-TC | "Pricing and rate limits" | "Token counting is free to use but subject to requests per minute rate limits based on your usage tier." | high | **Yes**: tier RPM values (5k/10k/20k) dated |
| A11 | Separate rate limits | A-TC | "Pricing and rate limits", Note | "Token counting and message creation have separate and independent rate limits." | high | Spot |
| A12 | No prompt caching in counting | A-TC | FAQ | "No, token counting provides an estimate without using caching logic." | high | Spot |
| A13 | Newer models use a newer tokenizer | A-TC | "Supported models", Note | "Claude 4.7 and later models and Claude Mythos Preview use a newer tokenizer." | high | **Yes**: model-specific |
| A14 | About 30% more tokens on the newer tokenizer | A-TC | "Supported models", Note | "The same input text produces approximately 30 percent more tokens than on earlier models." | high | **Yes**: conflicts with A19 |
| A15 | Recount per target model | A-TC | "Supported models", Note | "Recount prompts against the model you plan to use rather than reusing counts measured against earlier models." | high | Spot |
| A16 | Count uses the passed model's tokenizer | A-TC | "Token counts on Claude Fable and Claude Mythos models" | "The token counting endpoint counts under the tokenizer of the model you pass." | high | Spot |
| A17 | Billing reflects the new tokenizer's counts | A-TC | Note "Billing and migration" | "Usage and billing on these models reflect this tokenizer's counts." | high | Spot |
| A18 | Don't reuse old-model counts | A-TC | Note "Billing and migration" | "When migrating from a model before Claude Opus 4.7, don't reuse token counts measured on the older model to estimate costs or context window fit." | high | **Yes**: model-specific |
| A19 | Migration range 1x–1.35x | A-MG | "Breaking changes", item 4 | "roughly 1x to 1.35x as many tokens when processing text compared to models before Claude Opus 4.7 (up to ~35% more, varying by content)." | high | **Yes**: conflicts with A14 |
| A20 | count_tokens differs between Opus 5.5 and Opus 4.6 | A-MG | "Breaking changes", item 4 | "/v1/messages/count_tokens returns a different number of tokens for Claude Opus 5.5 than it did for Claude Opus 4.6." | high | **Yes**: model-specific |
| A21 | Pricing page states the ~30% increase | A-PR | "Model pricing", notes | "This tokenizer produces approximately 30% more tokens for the same text. The exact increase depends on the content and workload shape." | high | **Yes**: dated |
| A22 | Sonnet 4.6 and earlier use the previous tokenizer | A-PR | "Model pricing", notes | "Claude Sonnet 4.6 and earlier models use the previous tokenizer." | high | **Yes**: dated |
| A23 | Anthropic token definition | A-GL | "Tokens" | "Tokens are the smallest individual units of a language model, and can correspond to words, subwords, characters, or even bytes (in the case of Unicode)." | high | Spot |
| A24 | Characters per token depend on model and language | A-GL | "Tokens" | "For Claude, the number of characters a token represents depends on the model and the language." | high | Spot |
| A25 | ~3.5 English characters per token on earlier models only | A-GL | "Tokens" | "…newer tokenizer that produces approximately 30 percent more tokens for the same text than earlier models, on which a token represents approximately 3.5 English characters." | high | **Yes**: scope to pre-Opus-4.7; mid-sentence excerpt |
| A26 | Glossary: use token counting for exact counts | A-GL | "Tokens" | "To get exact counts, use token counting with the model you plan to use." | high | **Yes**: conflicts with A03 ("an estimate") |
| A27 | Tokenization choice affects performance and vocabulary | A-GL | "Tokens" | "The choice of tokenization method can impact the model's performance, vocabulary size, and ability to handle out-of-vocabulary words." | high | Spot |
| A28 | 1M tokens ≈ 555k words on the current tokenizer | A-MO | "Compare models", table notes | "1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7)" | high | **Yes**: dated |
| A29 | Older tokenizer: ~750k words per 1M tokens | A-MO | "Compare models", table notes | "models before it fit about 750k words in 1M tokens. 200k tokens is roughly 150k words." | high | **Yes**: dated |
| A30 | Context window measured in tokens (up to 1M) | A-CW | "How the context window works" | "The context window (up to 1M tokens, depending on the model) holds the conversation history plus the new output Claude generates." | high | **Yes**: 1M figure dated |
| A31 | Context rot as token count grows | A-CW | "How the context window works" | "As token count grows, accuracy and recall degrade, a phenomenon known as context rot." | high | Spot |
| A32 | Image tokens count toward budgets | A-CW | Context awareness | "Image tokens are included in these budgets." | high | Spot |
| A33 | Prices per million tokens | A-PR | "Model pricing", notes | "MTok: Million tokens. $5 / MTok is $5 for every million tokens." | high | **Yes**: prices dated |
| A34 | Rate limits in RPM, ITPM, OTPM | A-RL | "Rate limits" | "The rate limits for the Messages API are measured in requests per minute (RPM), input tokens per minute (ITPM), and output tokens per minute (OTPM)" | high | Spot |
| A35 | Only uncached input counts toward ITPM (most models) | A-RL | "Cache-aware ITPM" | "For most Claude models, only uncached input tokens count toward your ITPM rate limits." | high | Spot |
| G01 | Gemini rule of thumb | G-TOK | Intro | "For Gemini models, a token is equivalent to about 4 characters. 100 tokens is equal to about 60-80 English words." | high | **Yes**: stamp 2026-10-13 |
| G02 | Tokens range from characters to whole words | G-TOK | "About tokens" | "Tokens can be single characters like z or whole words like cat. Long words are broken up into several tokens." | high | No (stamped) |
| G03 | Vocabulary and tokenization defined | G-TOK | "About tokens" | "The set of all tokens used by the model is called the vocabulary, and the process of splitting text into tokens is called tokenization." | high | No |
| G04 | Cost partly determined by tokens | G-TOK | "About tokens" | "is determined in part by the number of input and output tokens" | high | No |
| G05 | All modalities are tokenized | G-TOK | "Count tokens" | "All input to and output from the Gemini API is tokenized, including text, image files, and other non-text modalities." | high | No |
| G06 | count_tokens returns input-only total | G-TOK | "Count tokens" | "Call count_tokens with the input of the request. Returns the total number of tokens in the input only." | high | No. REST `:countTokens` |
| G07 | Actual counts from response usage | G-TOK | "Count tokens" | "Use the usage on the interaction response." | high | **Yes**: Interactions API `usage`; `usage_metadata` absent from this page |
| G08 | Image token rate | G-TOK | "Count multimodal tokens" | "Images ≤384 pixels in both dimensions count as 258 tokens. Larger images are tiled into 768x768 pixel tiles, each counting as 258 tokens." | high | **Yes**: rates change by model |
| G09 | Video 263 tokens per second | G-TOK | "Count multimodal tokens" | "Video : 263 tokens per second (applies to static processing)." | medium | **Yes**: conflicts with G10 |
| G10 | Video ~100 or ~300 tokens per second | G-TOK | "Video token usage by processing mode" | "~100 tokens/second by default (low resolution) or ~300 tokens/second (high resolution). All frames sampled at 1 FPS." | medium | **Yes**: conflicts with G09 |
| G11 | Audio 32 tokens per second | G-TOK | "Count multimodal tokens" | "Audio: 32 tokens per second" | high | **Yes**: dated rate |
| G12 | System instructions counted as input | G-TOK | "Count system instruction tokens" | "System instructions are counted as part of the input tokens" | high | No |
| G13 | Tools counted | G-TOK | "Count tool tokens" | "Tools (functions, code execution, Google Search) are also counted" | high | No |
| G14 | Context window = input + output limit | G-TOK | "Context window" | "Each Gemini model has a maximum number of tokens it can handle. The context window defines the combined limit of input and output tokens." | high | No |
| G15 | Models break prompts into tokens | G-LIST | "Tokens and the importance…" | "Generative AI models break down text and other data in a prompt into units called tokens for processing." | high | No (stamped 2026-10-15) |
| G16 | Tokenization depends on the tokenizer | G-LIST | "Tokens and the importance…" | "The way that data is converted into tokens depends on the tokenizer used. A token can be characters, words, or phrases." | high | No |
| G17 | Listed tokens come with IDs | G-LIST | "Tokens and the importance…" | "Each listed token is associated with a token ID, which helps you perform troubleshooting and analyze model behavior." | high | **Yes**: Preview feature |
| G18 | Token listing is text-only | G-LIST | "Get a list of tokens and token IDs" | "The prompt must contain only text. Multimodal prompts are not supported." | high | **Yes**: Preview |
| G19 | Local counting in the Gen AI SDK | G-LIST | "Count tokens locally" | "For large prompts, counting tokens using the Count Tokens API may be fairly memory-intensive. The Google Gen AI SDK also supports local token counting" | high | **Yes**: Preview |
| G20 | Multimodal counts are estimates | G-CT | Top Note | "Token counts for multimodal inputs (images, video, audio) are an estimation based on the chosen media_resolution." | high | No |
| G21 | Billing truth in usage_metadata | G-CT | Top Note | "The accurate usage for billing is only available after execution within the response's usage_metadata." | high | No |
| G22 | Google recommends the SDK's integrated tokenizer | G-CT | "Important" callout | "Instead of using the countTokens API, we recommend that you use the integrated tokenizer of the Agent Platform SDK for getting the token count." | high | **Yes**: product rename |
| G23 | CountTokens free; 3000 RPM maximum | G-CT | "Pricing and quota" | "There is no charge or quota restriction for using the CountTokens API. The maximum quota for the CountTokens API is 3000 requests per minute." | high | **Yes**: self-contradictory; dated |
| G24 | Console tokenizer excludes media | G-CT | "Console" | "Media tokens aren't supported." | high | No |
| O01 | OpenAI token definition | O-KC | "Tokens" | "Text generation and embeddings models process text in chunks called tokens. Tokens represent commonly occurring sequences of characters." | high | Spot |
| O02 | OpenAI rule of thumb | O-KC | "Tokens" (also O-ADV) | "As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text." | high | **Yes**: "100 tokens ≈ 75 words" (help article) unverified |
| O03 | Tokenizer tool exists | O-KC | "Tokens" | "Check out our tokenizer tool to test specific strings and see how they are translated into tokens." | high | **Yes**: tool page 403 |
| O04 | Tokens vary by language | O-ADV | "Managing tokens" | "in some languages tokens can be even shorter than one character or even longer than one word." | medium | **Yes**: legacy page |
| O05 | Tokenization may change between models | O-ADV | "Managing tokens" | "The exact way that messages are converted into tokens may change from model to model." | medium | **Yes**: legacy context (gpt-3.5-turbo-0613) |
| O06 | Legacy example: "ChatGPT is great!" = six tokens | O-ADV | "Managing tokens" | 'For example, the string "ChatGPT is great!" is encoded into six tokens:' | medium | **Yes**: dated; encoding unnamed |
| O07 | Legacy limit 4097 tokens for gpt-3.5-turbo | O-ADV | "Managing tokens" | "total tokens must be below the model's maximum limit (4097 tokens for gpt-3.5-turbo)" | medium | **Yes**: dated; do not teach as current |
| O08 | You pay per token | O-ADV | "Managing tokens" | "How much your API call costs, as you pay per token" | high | Spot |
| O09 | Input-token-count endpoint mirrors Responses input | O-TC | Intro | "The input token count endpoint accepts the same input format as the Responses API." | high | Spot. `POST /v1/responses/input_tokens` |
| O10 | OpenAI says the count is exact | O-TC | Intro | "Pass text, messages, images, files, tools, or conversations—the API returns the exact count the model will receive." | high | **Yes**: pricing and rate limits of endpoint undocumented |
| O11 | Count includes formatting tokens | O-TC | Intro | "The count includes formatting tokens used to represent request structure, such as message roles and boundaries." | high | Spot |
| O12 | Local tokenizers have limitations | O-TC | "Why use the token counting API?" | "Local tokenizers like tiktoken work for plain text, but they have limitations:" | high | Spot |
| O13 | chars/4 is inaccurate for images and files | O-TC | "Why use the token counting API?" | "Images and files are not supported—estimates like characters / 4 are inaccurate" | high | Spot |
| O14 | Model behaviour can change tokenization | O-TC | "Why use the token counting API?" | "Model-specific behavior can change tokenization (for example, reasoning, caching)" | high | Spot |
| O15 | Images consume tokens by size and detail | O-TC | "Count tokens with images" | "Images consume tokens based on size and detail level." | high | Spot |
| O16 | Response object shape | O-TC | "API reference" | 'The response includes input_tokens (integer) and object: "response.input_tokens".' | high | Spot |
| O17 | Output usage includes invisible tokens | O-TC | "Understand output token counts" | "Reported output token usage includes all tokens generated by the model, not only the text visible in a response." | high | Spot |
| O18 | Index: counting without estimation or tiktoken | O-IDX | Entry "Counting tokens" | "Use the Responses API to count input tokens for text, images, files, tools, and more—without estimation or tiktoken." | high | Spot |
| O19 | Count tokens to check length limits | CB | Title cell | "Knowing how many tokens are in a text string can tell you (a) whether the string is too long for a text model to process" | high | No |
| O20 | Count tokens to estimate cost | CB | Title cell | "and (b) how much an OpenAI API call costs (as usage is priced by token)." | high | No |
| O21 | Chat-message counts are estimates | CB | "6. Counting tokens for chat completions" | "Consider the counts from the function below an estimate, not a timeless guarantee." | high | No (superseded in practice by O09) |
| O22 | English tokens range from one character to one word | CB | "How strings are typically tokenized" | "In English, tokens commonly range in length from one character to one word (e.g., "t" or " great")" | high | No |
| O23 | Other languages: shorter than a character or longer than a word | CB | "How strings are typically tokenized" | "though in some languages tokens can be shorter than one character or longer than one word." | high | No |
| O24 | OpenAI help article content | O-HELP | n/a | n/a (HTTP 403 "Enable JavaScript and cookies to continue") | low | **Yes**: manual browser check |

---

## Appendix C. Known conflicts and inconsistencies

| # | Where | Conflict | How to handle in the lesson |
|---|---|---|---|
| C1 | SEN, within paper | Figure 1 caption uses dictionary {low, lowest, newer, wider}; Algorithm 1 code uses low×5, lower×2, newest×6, widest×3. Figure 1's merges (r·, er·) fit the caption, not the code | Do not claim Algorithm 1 reproduces Figure 1. Use the HF course toy corpus (T20) for a runnable example, or rerun Algorithm 1 and show its own output |
| C2 | SEN, within paper | End-of-word marker is "·" (U+00B7) in prose and figures, `</w>` in code | Pick one spelling and say they are the same marker |
| C3 | SEN vs SP, KUDO, LLM-6.5, TF-SUM | Sennrich's knob is merge count ("the only hyperparameter"); SentencePiece, Kudo and HF stop at a target vocabulary size | Not a contradiction: vocab = base + merges (T11, T23). Teach both framings |
| C4 | Merge order | Sennrich never states that merges apply in learned order (implied by Algorithm 1); LLM-6.5 and TT-EDU state it | Cite E05/E06 for the order claim, not Sennrich |
| C5 | GPT2 vs SP/KUDO citations | GPT-2 cites "Sennrich et al., 2015" (arXiv); SP/KUDO cite 2016 (ACL) | Same paper. Cite as Sennrich et al. 2016 (ACL), arXiv 1508.07909v5 |
| C6 | GPT2 metadata | PDF "Subject" says ICML 2019 (template leftover); the paper was not an ICML paper | Cite as an OpenAI technical report, 2019 |
| C7 | GPT2 vs TF-SUM | Paper gives 50,257 without breakdown; TF-SUM gives 256 + 50,000 + 1 | Use TF-SUM for the breakdown, corroborated by TT-EXT and OBS |
| C8 | "Lossless" scope (TT-README vs TT-CORE/CB; SP) | tiktoken README: "reversible and lossless"; `decode` docstring: "lossy" (invalid UTF-8); Cookbook: single tokens lossy. SentencePiece is lossless only relative to normalized text | Whole sequences round-trip; slices that split a UTF-8 character do not; SentencePiece round-trips NFKC-normalized text |
| C9 | HF decoding | Default decoder joins tokens with spaces, which is not an inverse for WordPiece ("tok ##eni ##zer ##s") | Teach that decoding needs the matching decoder |
| C10 | Anthropic, across pages | Token counting and glossary say "approximately 30 percent more tokens" and pricing says "approximately 30% more tokens"; the Opus 5.5 migration guide says "roughly 1x to 1.35x as many tokens" and "(up to ~35% more, varying by content)" | Cite one page; say about 30%, up to ~35% depending on content, with both links |
| C11 | Anthropic, within docs | Token counting page: "The token count is an estimate"; glossary: "To get exact counts, use token counting" | Teach the token counting page's own framing (estimate); note glossary wording loosely says "exact" |
| C12 | Anthropic naming | Token counting note says "Claude 4.7 and later models and Claude Mythos Preview"; elsewhere "introduced with Claude Opus 4.7"; pricing says "Claude Sonnet 4.6 and earlier models use the previous tokenizer" | Compatible; describe them as models from Claude Opus 4.7 on, and link |
| C13 | Precision framing across providers | Anthropic: "estimate"; OpenAI: "the exact count the model will receive"; Google Cloud: multimodal counts are estimates, billing truth in `usage_metadata` | Quote each provider in its own words; do not generalize |
| C14 | Gemini API, within page | Video "263 tokens per second" vs table "~100 tokens/second by default (low resolution) or ~300 tokens/second (high resolution)" | Avoid citing a video rate, or cite both with the conflict noted |
| C15 | Google Cloud, within sentence pair | "no charge or quota restriction" then "The maximum quota for the CountTokens API is 3000 requests per minute." | Quote both halves if used |
| C16 | Gemini API vs Cloud | Gemini page uses the Interactions API `usage` object and no longer mentions `usage_metadata`; the Cloud page still names `usage_metadata` | Name the field per surface (Gemini API vs Agent Platform) |
| C17 | Rules of thumb | OpenAI ~4 characters / 0.75 words; Gemini ~4 characters / 60–80 words per 100 tokens; Anthropic ~3.5 characters (earlier models), ~555k words per 1M tokens (current); tiktoken ~4 **bytes** | Present as provider-specific and English-only; flag bytes vs characters |
| C18 | Typical vocabulary sizes | SEN 30k–50k (word-level NMT); KUDO 16k–32k; GPT2 32k–64k (BPE); GPT-2 itself 50,257 | Different contexts and eras; give each with its source |
| C19 | CB, within notebook | "supports three encodings" but the table lists four; table omits gpt-4.1, gpt-5, o-series, gpt-oss | Use TT-MODEL (tag 0.14.0) for current mappings |
| C20 | TF-SUM page identity | Same URL now titled "Tokenization algorithms" (formerly "Summary of the tokenizers") | Cite current title |

---

## Appendix D. Dated and provider-specific items

| Item | Source | Date or version stamp | Why it is dated |
|---|---|---|---|
| Claude tokenizer change (≈30% / up to ~35% more tokens; Opus 4.7+, Mythos, Fable 5.x) | A-TC, A-PR, A-GL, A-MG | Live pages, no stamp, read 2026-10-18 | Model names and ratios tied to current generation |
| 555k vs 750k words per 1M tokens | A-MO | Live, no stamp | Tied to current tokenizer |
| "up to 1M tokens" context window | A-CW | Live, no stamp | Model-dependent and changes |
| "$5 / MTok" example; Start/Build/Scale tiers at 5,000/10,000/20,000 RPM for counting | A-PR, A-TC | Live, no stamp | Prices and tiers change; docs point to claude.com/pricing for current prices |
| Server-tool restriction on counting | A-TC | Live, no stamp | Feature support changes |
| Legacy "whats-new-claude-4-7" URL redirects to Opus 5.5 page (no tokenizer mention) | A-WN | Live | URL structure changed |
| Gemini rule of thumb, multimodal rates, Interactions API `usage` fields, `gemini-3.8-flash` REST sample | G-TOK | Last updated 2026-10-13 UTC | Model names, rates and API surface change |
| Vertex AI → Gemini Enterprise Agent Platform rename; list-tokens Preview (Pre-GA); 3000 RPM CountTokens quota | G-LIST, G-CT | Last updated 2026-10-15 UTC | Product branding and Preview status |
| `POST /v1/responses/input_tokens` endpoint and "exact count" claim | O-TC | Live, no stamp | New API surface |
| gpt-3.5-turbo examples: "ChatGPT is great!" six tokens, 4097-token limit, `cl100k_base` fallback | O-ADV | Live, no stamp; legacy content | Legacy model era |
| Model → encoding mapping (o200k_base, cl100k_base, o200k_harmony, gpt-5 entry) | TT-MODEL | tiktoken tag 0.14.0 (2026-08-17) | Comment says it "will likely be replaced by an API endpoint" |
| Cookbook encoding table and stored outputs | CB | Notebook last changed 2024-10-08 | Predates gpt-4.1, gpt-5, o-series, gpt-oss |
| tiktoken "3-6x faster" benchmark vs `tokenizers==0.13.2` | TT-README | README changed 2025-02-14 | Benchmark baseline is old |
| HF tokenizers docs default to v1.0.0-rc.2; banner says build/train examples "Not supported by the rc0 bindings yet" | HF-PIPE/COMP/QT | 2026-09-21 file commit; stable PyPI 0.23.3 | Release candidate; stable docs (v0.23.3) not compared |
| Transformers docs v5.20.1; BPE models list "Llama, Gemma, Qwen2" | TF-SUM | 2026-02-17 file commit | Model list changes |
| Local observations (IDs, counts, round trips) | OBS | tiktoken 0.14.0, tokenizers 0.23.3, 2026-10-18 | Pinned versions; encoding files possibly cached |

---

## Appendix E. Gaps

| # | Gap | Effect on the lesson | Suggested Pass 2 action |
|---|---|---|---|
| E1 | Gage 1994 read only on a third-party transcription; drdobbs.com unreachable; pp. 23–38 unverified | Gage excerpts medium confidence | Locate publisher or library copy |
| E2 | No Sennrich sentence says merges apply in the order learned | Order claim must rest on LLM-6.5 / TT-EDU | None needed if cited correctly |
| E3 | GPT-2 does not define "character categories"; pre-tokenization regex lives in released code that was not read | Cannot state the exact split rule | Read OpenAI's GPT-2 `encoder.py` and tiktoken's `pat_str` for each encoding |
| E4 | GPT-2 paper gives no 50,257 breakdown; encoder files not read | Breakdown rests on TF-SUM + TT-EXT + OBS | Optional: inspect `vocab.bpe` / `encoder.json` |
| E5 | SentencePiece U+2581 glyph appears as "_" in both PDF text layers | Glyph unconfirmed visually | View the rendered PDF page |
| E6 | SentencePiece repository docs not read; "lossless" for unnormalized raw bytes unverified | Do not claim byte-exact raw round trips for SentencePiece | Read SentencePiece README/options (e.g., normalization rules) |
| E7 | Kudo ACL 2018 version (P18-1007) not read | Locators arXiv-only | Optional cross-check |
| E8 | No source measures LLM context-window cost as a function of vocabulary size | Trade-off taught from NMT-era evidence and observed counts | Treat as observed trend |
| E9 | HF phrase "starts with initial tokens and merges the most frequent pairs" not found; API docstrings (`models.BPE`, `BpeTrainer`) not read | Use T22/T25 wording | Optional |
| E10 | HF stable v0.23.3 docs not compared with v1.0.0-rc.2 text | Wording may differ on stable docs | Diff the two versions |
| E11 | OpenAI help article and Tokenizer page unreachable (HTTP 403) | "100 tokens ≈ 75 words", non-English token inflation and the tool's model coverage are unverified | Manual browser check by a human |
| E12 | No OpenAI platform doc names `o200k_base`; encoding for current models documented only in tiktoken | Cite TT-MODEL for encodings | None |
| E13 | Pricing and rate limits of OpenAI's input-token-count endpoint not documented | Cannot say whether it is free | Check API reference page |
| E14 | No provider says "don't compare token counts across providers" | Must be framed as inference | None |
| E15 | No reachable doc says non-English text "often uses more tokens" in those words | Use CB Japanese example (V27) and OBS instead | Recheck O-HELP |
| E16 | Anthropic publishes no characters-per-token figure for the new tokenizer (only 2.5M characters per 1M tokens, implying ~2.5) | Derived figure only | Present as derived |
| E17 | Gemini docs do not say different Gemini models use different tokenizers, nor discuss language effects beyond "English words" | Only Cloud's "depends on the tokenizer used" | None |
| E18 | Standalone Opus 4.7 "what's new" page not found (404 on guessed path) | Tokenizer change sourced from token counting, pricing, glossary, migration pages | Optional |
| E19 | Cookbook stored outputs lack a tiktoken version; exact cells not rerun | V27 medium confidence | Rerun the notebook cells at tiktoken 0.14.0 |
| E20 | Case and leading-space ID differences rest only on local observation | Present as a demo, not a documented claim | Rerun OBS script and keep it in the lesson repo |
