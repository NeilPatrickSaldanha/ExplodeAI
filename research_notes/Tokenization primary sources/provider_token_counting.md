# Provider documentation on tokens and token counting (Anthropic, Google Gemini API / Vertex AI, OpenAI)

Access date for every source: **2026-10-18**. Method: raw pages downloaded with curl (browser user agent). The `.md` versions of platform.claude.com and developers.openai.com pages were used where available, and `ai.google.dev/...tokens.md.txt` plus the HTML for Google. Text was extracted with Python. No provider API was called and no API key was used or looked for.

**Excerpt verification:** every excerpt below was string-matched against the downloaded source with a script that normalised whitespace and stripped markdown link, bold and backtick markup. All matched. Two Vertex excerpts failed the first pass only because of inline `<code>` tags, and were then confirmed by hand in the raw HTML. No excerpt depends on a summarising fetch tool, so **no [WF] tags are needed**. WebFetch was tried only for the two OpenAI pages that block scripts, and it returned 403 (no content).

**Date stamps:** Anthropic (platform.claude.com) and OpenAI (developers.openai.com) pages show **no "last updated" stamp**, so they are recorded as "live page at access date". Google pages show stamps: Gemini API tokens page "Last updated 2026-10-13 UTC", and both Cloud pages "Last updated 2026-10-15 UTC".

**Model names are dated:** model names in these docs (Claude Opus 5.5, Fable 5.1, Gemini 3.8 Flash, gemini-4 "Argon", gpt-6-astra, etc.) are current as of the access date and will go stale.

### Source register (URL requested, then final URL after redirects)

| ID | Provider | Requested URL | Final URL (redirects) | Stamp |
|---|---|---|---|---|
| A-TC | Anthropic | https://docs.claude.com/en/docs/build-with-claude/token-counting | https://platform.claude.com/docs/en/build-with-claude/token-counting (1 redirect). Text read from the `.md` variant at the same path | live page at access date |
| A-API | Anthropic | https://platform.claude.com/docs/en/api/messages/count_tokens.md | same (0 redirects) | live page |
| A-GL | Anthropic | https://docs.claude.com/en/docs/about-claude/glossary | https://platform.claude.com/docs/en/about-claude/glossary (1 redirect). `.md` variant used | live page |
| A-CW | Anthropic | https://platform.claude.com/docs/en/build-with-claude/context-windows.md | same | live page |
| A-PR | Anthropic | https://platform.claude.com/docs/en/about-claude/pricing.md | same | live page |
| A-MO | Anthropic | https://platform.claude.com/docs/en/about-claude/models/overview.md | https://platform.claude.com/docs/en/models/overview.md (1 redirect) | live page |
| A-WN | Anthropic | https://platform.claude.com/docs/en/about-claude/models/whats-new-claude-4-7.md | redirects to https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5.md. That page has **no** tokenizer mention. `.../models/opus-4-7/whats-new-opus-4-7.md` returns 404 | live page |
| A-MG | Anthropic | https://platform.claude.com/docs/en/models/opus-5-5/migration-guide.md (linked from the index https://platform.claude.com/docs/en/about-claude/models/migration-guide) | same | live page |
| A-RL | Anthropic | https://platform.claude.com/docs/en/api/rate-limits.md | same | live page |
| G-TOK | Google (Gemini API) | https://ai.google.dev/gemini-api/docs/tokens (plus `tokens.md.txt`) | same URL, after a 4-hop cookie/OAuth `prompt=none` bounce through accounts.google.com. Without a cookie jar it loops forever | **Last updated 2026-10-13 UTC** |
| G-LIST | Google Cloud (formerly "Vertex AI") | https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/list-token | 301 to docs.cloud.google.com/vertex-ai/..., then 301 to **https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/list-token**. Page title: "List and count tokens \| Gemini Enterprise Agent Platform". Marked **Preview** (Pre-GA) | **Last updated 2026-10-15 UTC** |
| G-CT | Google Cloud | https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/get-token-count | 2 redirects to **https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/get-token-count**. Title: "Use the Count Tokens API" | **Last updated 2026-10-15 UTC** |
| O-KC | OpenAI | https://platform.openai.com/docs/concepts | 1 redirect to https://developers.openai.com/api/docs/concepts. `.md` variant used | live page |
| O-TC | OpenAI | https://developers.openai.com/api/docs/guides/token-counting.md | same | live page |
| O-ADV | OpenAI | https://developers.openai.com/api/docs/guides/advanced-usage.md | same | live page. **Contains dated/legacy content** (gpt-3.5-turbo, 4097 tokens) |
| O-IDX | OpenAI | https://developers.openai.com/api/docs/llms.txt (and llms-full.txt export) | same | live page |
| O-HELP | OpenAI | https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them | **HTTP 403, unreachable**. Body: "Enable JavaScript and cookies to continue" (bot challenge, not bypassed). WebFetch also 403 | n/a |
| O-TOOL | OpenAI | https://platform.openai.com/tokenizer | **HTTP 403, unreachable** (same bot challenge). WebFetch also 403 | n/a |

---

## Q1. Anthropic: the token counting endpoint (inputs, estimate vs actual, cost, rate limits)

### Takeaway
Anthropic's count_tokens endpoint (`POST /v1/messages/count_tokens`, SDK `messages.count_tokens` / `messages.countTokens`) takes the same inputs as Messages: system, tools, images, PDFs and thinking. It returns `input_tokens`, which Anthropic explicitly calls an **estimate** that "might differ by a small amount". It is **free** but rate-limited (RPM by usage tier), and those limits are separate from message-creation limits.

### Cited Findings
- **[Anthropic]** Same inputs as message creation. Locator: A-TC, "How to count message tokens". Excerpt: "The token counting endpoint accepts the same structured list of inputs for creating a message, including support for system prompts, tools, images, and PDFs." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Output. Locator: A-TC, "How to count message tokens". Excerpt: "The response contains the total number of input tokens." The example response shown is `{ "input_tokens": 14 }`. — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Estimate, not exact. Locator: A-TC, Note under "How to count message tokens". Excerpts: "The token count is an estimate." and "In some cases, the actual number of input tokens used when creating a message might differ by a small amount." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** System-added tokens. Locator: same Note. Excerpt: "You are not billed for system-added tokens. Billing reflects only your content." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Model coverage. Locator: A-TC, "Supported models". Excerpt: "All active models support token counting." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** SDK method names, from the code samples under "Count tokens in basic messages": Python `client.messages.count_tokens(...)`, TypeScript `client.messages.countTokens(...)`, cURL `https://api.anthropic.com/v1/messages/count_tokens`, CLI `ant messages count-tokens`. — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** API reference. Locator: A-API, "Count tokens in a Message". Excerpt: "The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it." — [Count tokens in a Message](https://platform.claude.com/docs/en/api/messages/count_tokens)
- **[Anthropic]** Tool limits. Locator: A-TC, "Count tokens in messages with tools". Client tools and the advisor tool are supported. Excerpt: "Requests that include other server tools return an error." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Thinking. Locator: A-TC, "Count tokens in messages with thinking". Excerpt: "Current assistant turn thinking does count toward your input tokens". — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** PDFs. Locator: A-TC, "Count tokens in messages with PDFs". Base64 PDFs are supported. The page says the endpoint "doesn't support `url` or `file` document sources". This was confirmed in the source; the excerpt is omitted from the table because it contains code formatting. — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Free but rate-limited. Locator: A-TC, "Pricing and rate limits". Excerpt: "Token counting is free to use but subject to requests per minute rate limits based on your usage tier." Table as of the access date: Start 5,000 RPM, Build 10,000 RPM, Scale 20,000 RPM (tier names and values are dated). — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Separate limits. Locator: A-TC, Note in "Pricing and rate limits". Excerpt: "Token counting and message creation have separate and independent rate limits." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** No caching. Locator: A-TC, "FAQ", "Does token counting use prompt caching?". Excerpt: "No, token counting provides an estimate without using caching logic." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Limits measured in tokens. Locator: A-RL, "Rate limits". Excerpt: "The rate limits for the Messages API are measured in requests per minute (RPM), input tokens per minute (ITPM), and output tokens per minute (OTPM)". — [Rate limits](https://platform.claude.com/docs/en/api/rate-limits)
- **[Anthropic]** Locator: A-RL, "Cache-aware ITPM". Excerpt: "For most Claude models, only uncached input tokens count toward your ITPM rate limits." — [Rate limits](https://platform.claude.com/docs/en/api/rate-limits)

### Inferences
- For the lesson: "Anthropic gives an *estimate* before sending; the authoritative number is `usage` on the actual response." The doc states the estimate part directly. That billing follows actual usage is implied by "Usage and billing on these models reflect this tokenizer's counts" (Q2) and "Billing reflects only your content".

### Gaps
- No "last updated" stamp is shown on any platform.claude.com page.
- I did not fetch anthropic.com/claude.com/pricing (marketing page). The docs pricing page itself says "For the most current pricing information, visit claude.com/pricing".

---

## Q2. Anthropic: tokenizers differ between Claude models, and the glossary definition

### Takeaway
Anthropic documents a tokenizer change in four places. "Claude 4.7 and later models and Claude Mythos Preview" (the token counting page names the change as introduced with Claude Opus 4.7) use a newer tokenizer that produces **about 30% more tokens for the same text**. The Opus 5.5 migration guide gives a range instead, "roughly 1x to 1.35x" ("up to ~35% more"). The glossary gives **~3.5 English characters per token for the earlier models** only, and says characters-per-token "depends on the model and the language". Anthropic tells developers to recount with the target model rather than reuse old counts.

### Cited Findings
- **[Anthropic]** Locator: A-TC, "Supported models" (Note). Excerpts: "The same input text produces approximately 30 percent more tokens than on earlier models." and "Recount prompts against the model you plan to use rather than reusing counts measured against earlier models." The same Note opens: "Claude 4.7 and later models and Claude Mythos Preview use a newer tokenizer." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Locator: A-TC, "Token counts on Claude Fable and Claude Mythos models". Excerpt: "The token counting endpoint counts under the tokenizer of the model you pass." The section also states that Fable 5.1, Mythos 5.1, Fable 5 and Mythos 5 "share the tokenizer introduced with Claude Opus 4.7". — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Locator: A-TC, same section, Note "Billing and migration". Excerpts: "Usage and billing on these models reflect this tokenizer's counts." and "When migrating from a model before Claude Opus 4.7, don't reuse token counts measured on the older model to estimate costs or context window fit." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Anthropic]** Glossary definition. Locator: A-GL, "Tokens". Excerpt: "Tokens are the smallest individual units of a language model, and can correspond to words, subwords, characters, or even bytes (in the case of Unicode)." — [Glossary](https://platform.claude.com/docs/en/about-claude/glossary)
- **[Anthropic]** Varies by model and language. Locator: A-GL, "Tokens". Excerpt: "For Claude, the number of characters a token represents depends on the model and the language." — [Glossary](https://platform.claude.com/docs/en/about-claude/glossary)
- **[Anthropic]** The 3.5-character figure applies to *earlier* models. Locator: A-GL, "Tokens". Excerpt: "…newer tokenizer that produces approximately 30 percent more tokens for the same text than earlier models, on which a token represents approximately 3.5 English characters." — [Glossary](https://platform.claude.com/docs/en/about-claude/glossary)
- **[Anthropic]** Locator: A-GL, "Tokens". Excerpts: "To get exact counts, use token counting with the model you plan to use." and "The choice of tokenization method can impact the model's performance, vocabulary size, and ability to handle out-of-vocabulary words." — [Glossary](https://platform.claude.com/docs/en/about-claude/glossary)
- **[Anthropic]** Pricing page. Locator: A-PR, "Model pricing" (paragraph after the table notes). Excerpts: "This tokenizer produces approximately 30% more tokens for the same text. The exact increase depends on the content and workload shape." and "Claude Sonnet 4.6 and earlier models use the previous tokenizer." — [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- **[Anthropic]** Words per 1M tokens by tokenizer. Locator: A-MO, "Compare models" (table notes, "Context window"). Excerpts: "1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7)" and "models before it fit about 750k words in 1M tokens. 200k tokens is roughly 150k words." — [Models overview](https://platform.claude.com/docs/en/models/overview)
- **[Anthropic]** A different magnitude stated. Locator: A-MG, "Migrating to Claude Opus 5.5 from Claude Opus 4.6 and earlier Opus models", then "Breaking changes", item 4 "Updated token counting". Excerpt: "roughly 1x to 1.35x as many tokens when processing text compared to models before Claude Opus 4.7 (up to ~35% more, varying by content)." — [Opus 5.5 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)
- **[Anthropic]** Locator: A-MG, same item. Excerpt: "/v1/messages/count_tokens returns a different number of tokens for Claude Opus 5.5 than it did for Claude Opus 4.6." The checklist under "Claude Opus 4.6 or earlier" also says: "Re-test any client-side token-count estimations." — [Opus 5.5 migration guide](https://platform.claude.com/docs/en/models/opus-5-5/migration-guide)

### Inferences
- **Internal inconsistency to handle:** the token counting, glossary and pricing pages say "approximately 30%". The migration guide says "roughly 1x to 1.35x… up to ~35% more". These are compatible if 30% is a typical value and 35% the upper end, but the lesson should cite one page and say it varies by content.
- The 555k vs 750k words per 1M tokens in the models overview gives a concrete, citable illustration: the same token budget holds fewer words on the newer tokenizer.
- The old "~3.5 English characters per token" figure must be framed as **pre-Opus-4.7 models only**. The current glossary scopes it to "earlier models".

### Gaps
- The legacy URL `about-claude/models/whats-new-claude-4-7` now redirects to the Opus 5.5 "What's new" page, which does not mention the tokenizer. I could not find a standalone Opus 4.7 "what's new" page (a guessed path returned 404).
- Anthropic does not publish a characters-per-token figure for the *new* tokenizer in the glossary. The models overview implies about 2.5 Unicode characters per token (2.5M characters per 1M tokens), but that is derived, not stated per token.

---

## Q3. Anthropic: context windows and pricing are measured in tokens

### Takeaway
Context window sizes (up to 1M tokens) and prices (per million tokens, "MTok") are stated in tokens.

### Cited Findings
- **[Anthropic]** Locator: A-CW, "How the context window works" (bullet "Context window capacity"). Excerpt: "The context window (up to 1M tokens, depending on the model) holds the conversation history plus the new output Claude generates." — [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- **[Anthropic]** Locator: A-CW, "How the context window works". Excerpt: "As token count grows, accuracy and recall degrade, a phenomenon known as context rot." — [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- **[Anthropic]** Locator: A-CW, context awareness section. Excerpt: "Image tokens are included in these budgets." — [Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- **[Anthropic]** Locator: A-PR, "Model pricing" (table notes). Excerpt: "MTok: Million tokens. $5 / MTok is $5 for every million tokens." The table columns are "Base input tokens … Output tokens". — [Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

### Inferences
- Because of Q2, the same text costs more tokens on newer Claude models. A per-MTok price comparison across model generations is therefore not a like-for-like text-cost comparison.

### Gaps
- None material. Specific prices and the 1M figure are dated (October 2026).

---

## Q4. Google: Gemini API "Understand and count tokens" and Cloud (formerly Vertex AI) count tokens docs

### Takeaway
The Gemini API docs give the rule of thumb **~4 characters per token, 100 tokens ≈ 60–80 English words**. They document `count_tokens`/`countTokens` (input only) and the response `usage` fields. They give fixed multimodal rates: images 258 tokens per tile, video 263 tokens/s, audio 32 tokens/s. The same page also has a video table with ~100/~300 tokens/s, which is an internal inconsistency. The Cloud docs, now under the brand "Gemini Enterprise Agent Platform", say tokenization "depends on the tokenizer used". They say multimodal counts are estimates and billing truth is `usage_metadata`. CountTokens has no charge (with a stated 3000 RPM maximum quota).

### Cited Findings
- **[Google Gemini API]** Rule of thumb. Locator: G-TOK, page intro (bold, above "About tokens"). Excerpt: "For Gemini models, a token is equivalent to about 4 characters. 100 tokens is equal to about 60-80 English words." — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Definition. Locator: G-TOK, "About tokens". Excerpts: "Tokens can be single characters like z or whole words like cat. Long words are broken up into several tokens." and "The set of all tokens used by the model is called the vocabulary, and the process of splitting text into tokens is called tokenization." — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Billing. Locator: G-TOK, "About tokens". The cost of a call "is determined in part by the number of input and output tokens" (the sentence begins "When billing is enabled, the cost of a call to the Gemini API…"). — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Locator: G-TOK, "Count tokens". Excerpt: "All input to and output from the Gemini API is tokenized, including text, image files, and other non-text modalities." — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** countTokens. Locator: G-TOK, "Count tokens". Excerpt: "Call count_tokens with the input of the request. Returns the total number of tokens in the input only." The REST sample uses `POST .../v1beta/models/gemini-3.8-flash:countTokens`, and JS uses `client.models.countTokens`. — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Response usage. Locator: G-TOK, "Count tokens". Excerpt: "Use the usage on the interaction response." The listed fields are `total_input_tokens`, `total_output_tokens`, `total_thought_tokens`, `total_cached_tokens`, `total_tool_use_tokens` and `total_tokens`. **Dated note:** as of 2026-10-13 this page uses the Interactions API `usage` object. The string `usage_metadata` does **not** appear on this page (0 hits), so the brief's "usage_metadata in responses" is now documented only on the Cloud page (below). — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Images. Locator: G-TOK, "Count multimodal tokens". Excerpt: "Images ≤384 pixels in both dimensions count as 258 tokens. Larger images are tiled into 768x768 pixel tiles, each counting as 258 tokens." — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Video and audio. Locator: G-TOK, "Count multimodal tokens". Excerpts: "Video : 263 tokens per second (applies to static processing)." and "Audio: 32 tokens per second". — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Conflicting video rate. Locator: G-TOK, "Video token usage by processing mode" (table, Static row). Excerpt: "~100 tokens/second by default (low resolution) or ~300 tokens/second (high resolution). All frames sampled at 1 FPS." The same table says agentic processing gives "Up to 88% fewer tokens for long-form content". — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Locator: G-TOK, "Count system instruction tokens" and "Count tool tokens". Excerpts: "System instructions are counted as part of the input tokens" and "Tools (functions, code execution, Google Search) are also counted". — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Gemini API]** Locator: G-TOK, "Context window". Excerpt: "Each Gemini model has a maximum number of tokens it can handle. The context window defines the combined limit of input and output tokens." — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)
- **[Google Cloud]** Locator: G-LIST, "Tokens and the importance of token listing and counting". Excerpts: "Generative AI models break down text and other data in a prompt into units called tokens for processing." and "The way that data is converted into tokens depends on the tokenizer used. A token can be characters, words, or phrases." — [List and count tokens](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/list-token)
- **[Google Cloud]** Token IDs. Locator: G-LIST, same section. Excerpt: "Each listed token is associated with a token ID, which helps you perform troubleshooting and analyze model behavior." Under "Get a list of tokens and token IDs for a prompt": "The prompt must contain only text. Multimodal prompts are not supported." — [List and count tokens](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/list-token)
- **[Google Cloud]** Local counting. Locator: G-LIST, "Count tokens locally". Excerpt: "For large prompts, counting tokens using the Count Tokens API may be fairly memory-intensive. The Google Gen AI SDK also supports local token counting". The page says `count_tokens` counts and `compute_tokens` returns IDs. The page is marked Preview (Pre-GA). — [List and count tokens](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/list-token)
- **[Google Cloud]** Estimates for media. Locator: G-CT, top Note. Excerpts: "Token counts for multimodal inputs (images, video, audio) are an estimation based on the chosen media_resolution." and "The accurate usage for billing is only available after execution within the response's usage_metadata." — [Use the Count Tokens API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/get-token-count)
- **[Google Cloud]** Locator: G-CT, "Important" callout. Excerpt: "Instead of using the countTokens API, we recommend that you use the integrated tokenizer of the Agent Platform SDK for getting the token count." — [Use the Count Tokens API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/get-token-count)
- **[Google Cloud]** Cost and quota. Locator: G-CT, "Pricing and quota". Excerpt: "There is no charge or quota restriction for using the CountTokens API. The maximum quota for the CountTokens API is 3000 requests per minute." — [Use the Count Tokens API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/get-token-count)
- **[Google Cloud]** Console tokenizer. Locator: G-CT, "Console". It shows tokens colour-coded by token ID. Excerpt: "Media tokens aren't supported." — [Use the Count Tokens API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/get-token-count)

### Inferences
- The Gemini rule of thumb (~4 characters; 60–80 words per 100 tokens) is close to OpenAI's but not identical (OpenAI implies 75 words per 100 tokens). That supports the "don't compare across providers" point.
- The "Pricing and quota" sentence is self-contradictory ("no … quota restriction" followed by a 3000 RPM maximum quota). Quote both halves if used.
- Product rename: "Vertex AI" URLs now redirect to "Gemini Enterprise Agent Platform". Lesson citations should use the final URL and mention the redirect.

### Gaps
- The Gemini page does not say that token counts differ across languages, beyond scoping the rule of thumb to "English words". It also does not say that different Gemini models use different tokenizers.
- The "263 tokens per second" vs "~100/~300 tokens/second" video conflict is unresolved on the page itself. I did not check the video-understanding page.
- The supported-models lists on the Cloud pages render as collapsed lists of codenamed models ("Gemini 4 Argon", etc.). Not relied on.

---

## Q5. OpenAI: rule of thumb, language effects, tokenizer naming, Tokenizer tool, counting endpoint

### Takeaway
OpenAI's reachable platform docs (developers.openai.com) give **"1 token is approximately 4 characters or 0.75 words for English text"**. They say tokens can be shorter or longer than characters or words "in some languages". There is now a **Responses API input-token-count endpoint** (`POST /v1/responses/input_tokens`) that OpenAI describes as returning "the exact count", and the docs note that tiktoken/local estimates miss images, files, tools and formatting tokens. The help-center article and the Tokenizer web page were **unreachable** (403 bot challenge). No reachable OpenAI platform doc names **o200k_base**.

### Cited Findings
- **[OpenAI]** Definition. Locator: O-KC, "Tokens". Excerpt: "Text generation and embeddings models process text in chunks called tokens. Tokens represent commonly occurring sequences of characters." — [Key concepts](https://developers.openai.com/api/docs/concepts)
- **[OpenAI]** Example. Locator: O-KC, "Tokens". Excerpts: 'the string " tokenization" is decomposed as " token" and "ization"' and "Note that in a sentence, the first token of each word typically starts with a space character." — [Key concepts](https://developers.openai.com/api/docs/concepts)
- **[OpenAI]** Rule of thumb. Locator: O-KC, "Tokens" (the same sentence is repeated in O-ADV "Managing tokens"). Excerpt: "As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text." — [Key concepts](https://developers.openai.com/api/docs/concepts); [Advanced usage](https://developers.openai.com/api/docs/guides/advanced-usage)
- **[OpenAI]** Tokenizer tool reference. Locator: O-KC, "Tokens". Excerpt: "Check out our tokenizer tool to test specific strings and see how they are translated into tokens." (The link points to https://platform.openai.com/tokenizer.) — [Key concepts](https://developers.openai.com/api/docs/concepts)
- **[OpenAI]** Language variation. Locator: O-ADV, "Managing tokens". Excerpt: "in some languages tokens can be even shorter than one character or even longer than one word." — [Advanced usage](https://developers.openai.com/api/docs/guides/advanced-usage)
- **[OpenAI]** Model-to-model variation (legacy context). Locator: O-ADV, "Managing tokens". Excerpt: "The exact way that messages are converted into tokens may change from model to model." **Dated:** this sits next to a `gpt-3.5-turbo-0613` counting function with a `cl100k_base` fallback. — [Advanced usage](https://developers.openai.com/api/docs/guides/advanced-usage)
- **[OpenAI, DATED]** Locator: O-ADV, "Managing tokens". Excerpts: 'For example, the string "ChatGPT is great!" is encoded into six tokens:' (the list given is `["Chat", "G", "PT", " is", " great", "!"]`) and "total tokens must be below the model's maximum limit (4097 tokens for gpt-3.5-turbo)". The page does not name the encoding behind the six-token example. Treat it as legacy-era. — [Advanced usage](https://developers.openai.com/api/docs/guides/advanced-usage)
- **[OpenAI]** Billing in tokens. Locator: O-ADV, "Managing tokens". Excerpt: "How much your API call costs, as you pay per token". — [Advanced usage](https://developers.openai.com/api/docs/guides/advanced-usage)
- **[OpenAI]** Counting endpoint. Locator: O-TC, intro. Excerpts: "The input token count endpoint accepts the same input format as the Responses API." and "Pass text, messages, images, files, tools, or conversations—the API returns the exact count the model will receive." Endpoint in the samples: `https://api.openai.com/v1/responses/input_tokens`. — [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting)
- **[OpenAI]** Locator: O-TC, intro. Excerpt: "The count includes formatting tokens used to represent request structure, such as message roles and boundaries." — [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting)
- **[OpenAI]** Limits of local tokenizers. Locator: O-TC, "Why use the token counting API?". Excerpts: "Local tokenizers like tiktoken work for plain text, but they have limitations:", "Images and files are not supported—estimates like characters / 4 are inaccurate", and "Model-specific behavior can change tokenization (for example, reasoning, caching)". — [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting)
- **[OpenAI]** Locator: O-TC, "Count tokens with images". Excerpt: "Images consume tokens based on size and detail level." — [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting)
- **[OpenAI]** Locator: O-TC, "API reference". Excerpt: 'The response includes input_tokens (integer) and object: "response.input_tokens".' — [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting)
- **[OpenAI]** Locator: O-TC, "Understand output token counts". Excerpt: "Reported output token usage includes all tokens generated by the model, not only the text visible in a response." — [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting)
- **[OpenAI]** Index description. Locator: O-IDX, entry "Counting tokens". Excerpt: "Use the Responses API to count input tokens for text, images, files, tools, and more—without estimation or tiktoken." — [OpenAI API guides index](https://developers.openai.com/api/docs/llms.txt)

### Inferences
- "0.75 words per token" implies about 75 words per 100 tokens. The explicit phrase "100 tokens ≈ 75 words" was **not** found in reachable docs. It is believed to be in the help-center article, which I could not reach.
- Contrast for the lesson: Anthropic calls its pre-send count an "estimate". OpenAI's guide says its endpoint returns "the exact count the model will receive". Google Cloud says media counts are estimates and billing truth is in `usage_metadata`. Each provider frames precision differently. Cite each in its own words.

### Gaps
- **help.openai.com "What are tokens and how to count them?" was unreachable**: HTTP 403 with "Enable JavaScript and cookies to continue", via both curl with a browser user agent and WebFetch. Its claims are **unverified**: "100 tokens ≈ 75 words", non-English text using more tokens, and any encoding names. Do not cite them without a manual browser check.
- **platform.openai.com/tokenizer was unreachable** (same 403). What the tool page says (which models or encodings it covers) is unverified.
- **o200k_base**: a grep of the full OpenAI API docs export (`developers.openai.com/api/docs/llms-full.txt`, about 5.4 MB) found **0** occurrences. The only encoding named is `cl100k_base`, inside the legacy gpt-3.5 code sample. No reachable OpenAI platform doc names the current models' encoding. Use the tiktoken repo (another researcher's scope) for that claim.
- The OpenAI counting guide does not state whether the input-token-count endpoint is free or what its rate limits are (grep for "free", "rate limit" and "charge": no hits).

---

## Q6. Do provider docs say counts differ across languages or model families? ("token counts are tokenizer-specific; don't compare across providers")

### Takeaway
Yes, partly, within each provider. No provider doc found says anything about *cross-provider* comparison. That part of the lesson's claim is an inference supported by each provider's per-tokenizer statements and differing rules of thumb.

### Cited Findings
- **[Anthropic]** Depends on model and language: "For Claude, the number of characters a token represents depends on the model and the language." — [Glossary](https://platform.claude.com/docs/en/about-claude/glossary)
- **[Anthropic]** Counts differ between Claude model generations ("approximately 30 percent more tokens"), and counts are tokenizer- and model-specific: "The token counting endpoint counts under the tokenizer of the model you pass." — [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- **[Google Cloud]** "The way that data is converted into tokens depends on the tokenizer used." — [List and count tokens](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/list-token)
- **[OpenAI]** Languages: "in some languages tokens can be even shorter than one character or even longer than one word." Models: "The exact way that messages are converted into tokens may change from model to model." Also "Model-specific behavior can change tokenization (for example, reasoning, caching)". — [Advanced usage](https://developers.openai.com/api/docs/guides/advanced-usage); [Counting tokens](https://developers.openai.com/api/docs/guides/token-counting)
- **[Google Gemini API]** The rule of thumb is scoped to Gemini and English: "For Gemini models, a token is equivalent to about 4 characters. 100 tokens is equal to about 60-80 English words." — [Understand and count tokens](https://ai.google.dev/gemini-api/docs/tokens)

### Inferences
- The rules of thumb differ: Gemini ≈4 characters per token (60–80 words per 100 tokens); OpenAI ≈4 characters per token or 0.75 words; Anthropic ≈3.5 English characters per token on earlier models, with about 30% more tokens on 4.7+ (implying about 555k words per 1M tokens). This is citable evidence that "a token" is not a common unit across providers, or even across one provider's model generations.
- Each provider scopes its rule of thumb to English ("English text", "English words", "English characters"). That supports the claim that non-English ratios differ, though only Anthropic (indirectly) and OpenAI (legacy page) say so.

### Gaps
- No provider doc explicitly says "don't compare token counts across providers". Frame it as an inference.
- No reachable doc states that non-English text "often uses more tokens" in those words. The OpenAI help article may say so, but it was unreachable.

---

## Claims table

| # | Claim | Provider | Source (final URL) | Locator | Verbatim excerpt (≤25 words) | Confidence | Dated? / notes |
|---|---|---|---|---|---|---|---|
| 1 | count_tokens takes the same inputs as Messages (system, tools, images, PDFs) | Anthropic | https://platform.claude.com/docs/en/build-with-claude/token-counting | How to count message tokens | "The token counting endpoint accepts the same structured list of inputs for creating a message, including support for system prompts, tools, images, and PDFs." | high | Live page, no stamp. Redirected from docs.claude.com |
| 2 | Count is an estimate and may differ slightly from actual usage | Anthropic | same | Note under How to count message tokens | "In some cases, the actual number of input tokens used when creating a message might differ by a small amount." | high | Pair with "The token count is an estimate." |
| 3 | Not billed for system-added tokens | Anthropic | same | same Note | "You are not billed for system-added tokens. Billing reflects only your content." | high | |
| 4 | Token counting is free but rate-limited by tier | Anthropic | same | Pricing and rate limits | "Token counting is free to use but subject to requests per minute rate limits based on your usage tier." | high | RPM values and tier names (Start/Build/Scale) are dated |
| 5 | Separate rate limits from message creation | Anthropic | same | Pricing and rate limits (Note) | "Token counting and message creation have separate and independent rate limits." | high | |
| 6 | API reference: counts tools, images, documents without creating a message | Anthropic | https://platform.claude.com/docs/en/api/messages/count_tokens | Count tokens in a Message | "The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it." | high | POST /v1/messages/count_tokens |
| 7 | Newer Claude tokenizer gives ~30% more tokens for same text | Anthropic | https://platform.claude.com/docs/en/build-with-claude/token-counting | Supported models (Note) | "The same input text produces approximately 30 percent more tokens than on earlier models." | high | Model-version-specific (Claude 4.7+ / Mythos Preview) |
| 8 | Recount per target model; don't reuse old counts | Anthropic | same | Supported models (Note) | "Recount prompts against the model you plan to use rather than reusing counts measured against earlier models." | high | |
| 9 | Count depends on the model's tokenizer | Anthropic | same | Token counts on Claude Fable and Claude Mythos models | "The token counting endpoint counts under the tokenizer of the model you pass." | high | Model names dated |
| 10 | Migration range 1x–1.35x | Anthropic | https://platform.claude.com/docs/en/models/opus-5-5/migration-guide | Breaking changes, item 4 "Updated token counting" | "roughly 1x to 1.35x as many tokens when processing text compared to models before Claude Opus 4.7 (up to ~35% more, varying by content)." | high | Inconsistent with the "~30%" wording elsewhere. Model-specific |
| 11 | Pricing page states the tokenizer change; Sonnet 4.6 and earlier use the old one | Anthropic | https://platform.claude.com/docs/en/about-claude/pricing | Model pricing (notes) | "This tokenizer produces approximately 30% more tokens for the same text. The exact increase depends on the content and workload shape." | high | Dated |
| 12 | Token definition (words/subwords/characters/bytes) | Anthropic | https://platform.claude.com/docs/en/about-claude/glossary | Tokens | "Tokens are the smallest individual units of a language model, and can correspond to words, subwords, characters, or even bytes (in the case of Unicode)." | high | Redirected from docs.claude.com |
| 13 | Characters per token depends on model and language | Anthropic | same | Tokens | "For Claude, the number of characters a token represents depends on the model and the language." | high | |
| 14 | ~3.5 English characters per token on earlier models only | Anthropic | same | Tokens | "…newer tokenizer that produces approximately 30 percent more tokens for the same text than earlier models, on which a token represents approximately 3.5 English characters." | high | **Scope it to pre-Opus-4.7 models**; mid-sentence excerpt |
| 15 | 1M tokens ≈ 555k words (new) vs ~750k words (old tokenizer) | Anthropic | https://platform.claude.com/docs/en/models/overview | Compare models (table notes) | "1M tokens is roughly 555k words or 2.5M Unicode characters on the current tokenizer (introduced with Claude Opus 4.7)" | high | Second half: "models before it fit about 750k words in 1M tokens." Redirected from /about-claude/models/overview |
| 16 | Context window measured in tokens | Anthropic | https://platform.claude.com/docs/en/build-with-claude/context-windows | How the context window works | "The context window (up to 1M tokens, depending on the model) holds the conversation history plus the new output Claude generates." | high | 1M figure dated |
| 17 | Pricing measured per million tokens | Anthropic | https://platform.claude.com/docs/en/about-claude/pricing | Model pricing (notes) | "MTok: Million tokens. $5 / MTok is $5 for every million tokens." | high | Prices dated |
| 18 | Rate limits measured in tokens (ITPM/OTPM) | Anthropic | https://platform.claude.com/docs/en/api/rate-limits | Rate limits | "The rate limits for the Messages API are measured in requests per minute (RPM), input tokens per minute (ITPM), and output tokens per minute (OTPM)" | high | |
| 19 | Gemini rule of thumb: ~4 chars; 100 tokens ≈ 60–80 English words | Google (Gemini API) | https://ai.google.dev/gemini-api/docs/tokens | Intro (above About tokens) | "For Gemini models, a token is equivalent to about 4 characters. 100 tokens is equal to about 60-80 English words." | high | Last updated 2026-10-13 UTC |
| 20 | Token definition / vocabulary / tokenization | Google (Gemini API) | same | About tokens | "The set of all tokens used by the model is called the vocabulary, and the process of splitting text into tokens is called tokenization." | high | |
| 21 | All modalities are tokenized | Google (Gemini API) | same | Count tokens | "All input to and output from the Gemini API is tokenized, including text, image files, and other non-text modalities." | high | |
| 22 | count_tokens returns input-only total | Google (Gemini API) | same | Count tokens | "Call count_tokens with the input of the request. Returns the total number of tokens in the input only." | high | REST `:countTokens` |
| 23 | Response usage fields give actual counts | Google (Gemini API) | same | Count tokens | "Use the usage on the interaction response." | high | **Dated:** Interactions API `usage`; `usage_metadata` absent from this page |
| 24 | Images: 258 tokens (≤384px) or per 768×768 tile | Google (Gemini API) | same | Count multimodal tokens | "Images ≤384 pixels in both dimensions count as 258 tokens. Larger images are tiled into 768x768 pixel tiles, each counting as 258 tokens." | high | Rates may change by model |
| 25 | Video 263 tok/s; audio 32 tok/s | Google (Gemini API) | same | Count multimodal tokens | "Video : 263 tokens per second (applies to static processing)." | medium | Conflicts with the ~100/~300 tok/s table on the same page. Audio: "Audio: 32 tokens per second" |
| 26 | Video static mode ~100 or ~300 tok/s | Google (Gemini API) | same | Video token usage by processing mode | "~100 tokens/second by default (low resolution) or ~300 tokens/second (high resolution). All frames sampled at 1 FPS." | medium | Same internal conflict |
| 27 | Context window = combined input + output token limit | Google (Gemini API) | same | Context window | "Each Gemini model has a maximum number of tokens it can handle. The context window defines the combined limit of input and output tokens." | high | |
| 28 | Tokenization depends on the tokenizer | Google Cloud | https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/list-token | Tokens and the importance of token listing and counting | "The way that data is converted into tokens depends on the tokenizer used. A token can be characters, words, or phrases." | high | Last updated 2026-10-15 UTC. Preview. Redirected from cloud.google.com/vertex-ai/... |
| 29 | Local token counting / compute_tokens in the SDK | Google Cloud | same | Count tokens locally | "For large prompts, counting tokens using the Count Tokens API may be fairly memory-intensive. The Google Gen AI SDK also supports local token counting" | high | Preview |
| 30 | Multimodal counts are estimates; billing truth in usage_metadata | Google Cloud | https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/get-token-count | Top Note | "The accurate usage for billing is only available after execution within the response's usage_metadata." | high | Pair with "…are an estimation based on the chosen media_resolution." |
| 31 | CountTokens is free; 3000 RPM max quota | Google Cloud | same | Pricing and quota | "There is no charge or quota restriction for using the CountTokens API. The maximum quota for the CountTokens API is 3000 requests per minute." | high | Self-contradictory wording. Last updated 2026-10-15 UTC |
| 32 | OpenAI token definition | OpenAI | https://developers.openai.com/api/docs/concepts | Tokens | "Text generation and embeddings models process text in chunks called tokens. Tokens represent commonly occurring sequences of characters." | high | Redirected from platform.openai.com/docs/concepts |
| 33 | OpenAI rule of thumb: ~4 chars or 0.75 words (English) | OpenAI | same | Tokens | "As a rough rule of thumb, 1 token is approximately 4 characters or 0.75 words for English text." | high | "100 tokens ≈ 75 words" not verified (help article unreachable) |
| 34 | Tokens differ by language | OpenAI | https://developers.openai.com/api/docs/guides/advanced-usage | Managing tokens | "in some languages tokens can be even shorter than one character or even longer than one word." | medium | Page contains legacy gpt-3.5 content |
| 35 | Tokenization may change between models | OpenAI | same | Managing tokens | "The exact way that messages are converted into tokens may change from model to model." | medium | Legacy context (gpt-3.5-turbo-0613, cl100k_base) |
| 36 | Input-token-count endpoint, same input as Responses | OpenAI | https://developers.openai.com/api/docs/guides/token-counting | Intro | "The input token count endpoint accepts the same input format as the Responses API." | high | POST /v1/responses/input_tokens |
| 37 | OpenAI claims an exact count | OpenAI | same | Intro | "Pass text, messages, images, files, tools, or conversations—the API returns the exact count the model will receive." | high | Contrast with Anthropic "estimate" |
| 38 | Local tokenizers (tiktoken) miss images, files, tools; chars/4 inaccurate | OpenAI | same | Why use the token counting API? | "Images and files are not supported—estimates like characters / 4 are inaccurate" | high | |
| 39 | Hidden formatting tokens count | OpenAI | same | Intro | "The count includes formatting tokens used to represent request structure, such as message roles and boundaries." | high | |
| 40 | Tokenizer tool exists for testing strings | OpenAI | https://developers.openai.com/api/docs/concepts | Tokens | "Check out our tokenizer tool to test specific strings and see how they are translated into tokens." | high | Tool page itself unreachable (403) |
| 41 | Current models use o200k_base | OpenAI | not found in platform docs | n/a | n/a | low | 0 hits in the full API docs export. Defer to the tiktoken repo |
| 42 | Help article "What are tokens…" content | OpenAI | https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them | n/a | n/a (HTTP 403 "Enable JavaScript and cookies to continue") | low | Unreachable. Verify manually before citing |
