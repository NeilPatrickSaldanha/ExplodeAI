# ExplodeAI Creator Bible

*Self-contained reference for creating LinkedIn videos and posts about ExplodeAI. Written 2026-10-22 from the actual repository (code, docs, five lesson files, verification reports), from running the app and its backend, and from the creator's own written answers (section 1A). Everything stated as working was confirmed. Anything I could not confirm is marked **[UNVERIFIED]**. No planned feature is described as built.*

---

## How to use this document
- Treat sections 1–5 as ground truth about the product. Section 1A holds the creator's own statements about himself, his goals and his boundaries. Do not add features, numbers or claims that are not here.
- Section 1B explains how everything works in plain English. Section 3 is the teaching content (stages, flows, concepts, misconceptions, sources). Section 4 is the screen-recording guide. Section 5 is the engineering story. Section 6 is a menu of material available for content. Section 7 is a short context prompt for Claude Chat.
- Observed demo numbers (for example "35 tokens → 8") are **deterministic outputs from the app on 2026-10-22** with the settings stated. They are safe to show on screen and to quote, with those settings.

---

# 1. What ExplodeAI is

**One sentence:** ExplodeAI is an interactive web app where you learn AI engineering by taking a real system apart: rotate it in 3D, pull it apart with a slider, isolate a part, run its real code with your own input, break it on purpose, then rebuild it.

**Why it exists / philosophy (stated in the product and docs):**
- Learn by seeing and doing instead of reading. The home page reads: "AI engineering, taken apart. Learn systems by exploding them. Rotate a system in 3D, pull it apart, isolate a part, run it for real, break it on purpose, then rebuild it. Every claim links to its source."
- Honesty about what is real. Every visual carries a badge: **Real execution**, **Simulation** or **Conceptual**. The site footer says: "every claim cited, every experiment real, every simulation labelled."
- Verified content. Every technical claim cites exact short excerpts from official sources and records three verification passes (primary-source research, independent cross-check, technical test). The system refuses to publish a lesson otherwise. It does not claim this guarantees correctness: it means each claim has inspectable evidence.
- Free and offline by default. No API keys are needed. Paid AI is an optional extra, off by default, with server-side limits.

**Who it is for:** anyone interested in learning AI, especially students, beginners and young developers who struggle with text-heavy explanations and learn better by seeing how a system or process actually works. Experienced developers who want to visualise or revisit a concept are also a target audience. The design (3D model, flow animations, plain-words explanations, analogies, runnable examples) serves visual and hands-on learners. This is a design goal and the creator's personal experience, **not** a tested claim: do not say visual learning is faster or proven.

**What makes it different from a typical AI tutorial (all verifiable in the app):**
1. You can *operate* the system: change chunk size, merges, heads, tool descriptions, and see the real result.
2. "What breaks if removed?" actually runs the system without that part, side by side with the full run. It is not an illustration.
3. Break & fix challenges: a deliberately broken setup, some controls locked, and the server re-runs your fix and checks it.
4. Every claim is cited with exact excerpts and shows its three verification passes.
5. Simulations and toy models are labelled, never passed off as real models.

**Technical architecture and technologies (from the code and docs):**
- Frontend: Vite, React 19, TypeScript; three.js through react-three-fiber and drei (loaded lazily); Radix UI primitives; Phosphor icons; Vitest and Playwright for tests.
- Backend: FastAPI (Python, managed with uv); SQLModel on SQLite (progress, experiment runs, paid-AI ledger); numpy for the experiments.
- Local neural model: BAAI bge-small-en-v1.5 (Qdrant's ONNX export) run on CPU through fastembed. Free, no key.
- Content: lessons are YAML files plus a source registry (`content/`); a validator enforces the publishing rules.
- Delivery: Docker Compose; GitHub Actions CI. Lessons are served over a REST API; the browser keeps an anonymous random id for progress (no accounts).
- A reusable "exploded-view engine" draws any system from a spec of parts (shape, size, positions) and links (source → target). All five lessons use the same engine and the same lesson shell, so they behave identically.

---

# 1A. About the creator and the content goals (the creator's own statements)

*These are Neil's answers, kept close to his words. They describe him, his reasons, and the boundaries he wants respected. They are not product facts. Preserve his voice and these limits.*

**Who he is.** Neil. Background in software development, AI automation, and building applications that connect AI models to real systems and APIs. Advanced Diploma in Computer Systems Technology: Software Development and Network Engineering, Sheridan College. Experience with AI automation tools, APIs, Python, backend development, RAG applications and AI-assisted development workflows. He wants any personal introduction to be brief, with the focus on the project and what people can learn.

**How he describes ExplodeAI:** "ExplodeAI is an interactive, visual-first learning platform that helps people understand AI engineering by taking complex systems apart, exploring their components, and seeing how everything works together."

**Why he built it.** He believes technical learning is easier when people can see what they are trying to understand. Many people, himself included, learn better from visuals and hands-on demonstrations than from long text; he finds it hard to stay engaged with nothing but paragraphs. When he can watch how a system works, how its parts interact and what happens at each stage, he understands it faster. He wanted people to go beyond memorising definitions and understand why each component of RAG, tokenization, embeddings, attention and AI agents exists, by exploring, taking apart and experimenting. He also uses the project to strengthen his own understanding. It is both a personal learning project and a public educational resource.
- **Boundary:** he has not scientifically tested visual learning and does not claim people learn two or three times faster. His reason is personal experience. The value proposition is a different, more interactive way to approach technical education.

**Audience.** Anyone interested in learning AI: students, beginners, young developers around his age, people who struggle with text-heavy explanations, and also experienced developers who want to visualise or revisit concepts.

**Transparency about AI-assisted development.** He used Claude Code extensively (frontend, backend, visualisations, implementation, tests, Git commits and commit messages) and does not want to hide it or imply he wrote every line. He is comfortable mentioning it naturally. What he did: guided the vision, educational direction, requirements, visual learning experience and quality expectations. He wants to understand the whole system and be able to explain and demonstrate everything he presents.

**Accuracy stance.** He required a research and verification workflow based on authoritative sources (documentation from OpenAI, Anthropic, Google, Hugging Face and others, and original research papers) because an educational platform should not mislead learners however good it looks. Publicly, **distinguish what the project implements (the verification process) from what has been independently confirmed.** Do not claim every piece of content is guaranteed correct just because an AI-assisted verification process exists. Section 5.4 states exactly what was done.

**Timeline.** Describe it naturally as a project he has been working on over the past week; he does not want exact dates emphasised.

**What the content is for.** Two purposes: (1) introduce the project, explain his motivation and show what he has built; (2) help viewers genuinely learn AI engineering concepts using the interactive features. He is especially interested in showing what actually happens inside AI systems, how components connect to larger systems and why they matter, rather than repeating definitions viewers could read in documentation.

**Practical preferences.**
- Maximum video length 15 minutes; shorter whenever a subject can be explained well in less. The introductory video should be considerably shorter than the educational deep dives.
- Natural, conversational, approachable; not corporate or overly promotional.
- Calls to action: mainly the ExplodeAI website, once it is public (it is not yet; see 2.7). No unnecessary promotional links, no excessive hashtags, no generic engagement-bait. He wants people to visit because they are curious about how AI works.
- Current lessons: RAG, Tokenization, Embeddings, Attention, Tool-using agents. He may add more later, but prefers to thoroughly understand, test and demonstrate these five first.

**What he wants to be.** Someone genuinely curious about AI engineering who enjoys building useful things, is open about using AI coding tools, and cares about helping other people learn. Above all he does not want to publish an explanation or claim about ExplodeAI that he cannot confidently explain or demonstrate. Everything in section 1B exists so he can.

---

# 1B. How ExplodeAI works, in plain English

*Written so the creator can explain every part. Where the repository does not record why a technology was chosen, the "why" below is the usual purpose of that tool, not a documented decision.*

**The technologies, and what each does here**

| Technology | What it does in ExplodeAI | Why it is a fit (general purpose) |
|---|---|---|
| React 19 + TypeScript | Builds the web interface: lesson pages, panels, tabs, controls | Component model for a highly interactive UI; TypeScript catches mistakes early |
| Vite | Dev server and production build (a 1.6 MB static site) | Fast development loop; builds plain static files |
| three.js via react-three-fiber / drei | Draws the 3D exploded models in the browser and handles camera and picking | Lets the 3D scene be written as React components; loaded lazily so the first page stays light |
| Radix UI, Phosphor icons | Accessible slider, tabs, toggle buttons; icons | Keyboard and screen-reader behaviour comes built in |
| FastAPI (Python) | The backend: serves lessons, runs experiments, stores progress, guards paid AI | Python is where the AI/numeric libraries live; FastAPI gives typed, validated endpoints |
| numpy | The maths inside experiments (vectors, attention, ranking) | Standard array library; keeps experiments small and inspectable |
| SQLite + SQLModel | Stores anonymous progress, experiment run history, and the paid-AI ledger | Zero-setup database in one file; fine for local and small deployments |
| fastembed + ONNX (bge-small-en-v1.5) | Runs a real embedding model locally on CPU for Lesson 03 and the RAG option | Free, no API key, works offline after one download |
| YAML lesson files | Lessons are data: claims, components, challenges, sources | Content can be validated and tested like code |
| pytest, Vitest, Playwright | Backend tests, frontend unit tests, real-browser end-to-end tests | Three layers: logic, components, whole app |
| Docker Compose, GitHub Actions | Local containers; automatic checks on every push | Repeatable setup and CI |

**How the frontend and backend talk.** The browser app asks the backend for data over plain web requests under `/api/...`: the list of lessons, one lesson's content, "run this experiment with these settings", "check this challenge fix", "save my progress", "ask the tutor". The backend answers in JSON. In development, Vite forwards `/api` to the backend on port 8000; in production the site and API would need to share one web address (see 2.7). The browser keeps an anonymous random id so progress can be saved without accounts.

**One experiment run, end to end.** You move a slider (for example "Merges learned"). About a quarter of a second later the app sends your settings to the backend. The backend runs the real pipeline (for example it trains and applies a small tokenizer), times every stage, and returns the results. The page shows them in tabs, and the numbers also appear as small live readouts on the 3D parts ("8 TOKENS").

**How the 3D exploded view works.** A lesson describes its system as parts (shape, size, resting position, and how far each moves when exploded) and links (which part feeds which, and what travels between them). The engine places every part at its resting position plus its explode offset multiplied by the slider value (0 to 1). That is linear, so each 10% moves everything the same distance, plus a small upward arc while parts are in motion. Some shapes also "sub-explode" (slices separate, disks stack). The camera automatically finds a distance at which the fully exploded layout fits the window. Labels are normal web elements positioned from the 3D points each frame. Animated packets travel along the links (paused by Flow, or replaced by static markers under Calm). Isolate fades everything except the selected part and its neighbours. A flat 2D version built from the same description is the fallback and is fully keyboard-accessible.

**How the AI experiments work, and what is real.** See the table in 2.5. In one line each: Lesson 01 really chunks text, searches by keyword and by meaning, merges the rankings and assembles a prompt; Lesson 02 really trains and runs a small byte-pair-encoding tokenizer; Lesson 03 really runs a small neural embedding model on your computer; Lesson 04 really computes attention, but with fixed random numbers instead of a trained model; Lesson 05 really runs an agent loop with real tools and checks, but a short hand-written rule plays the part of the language model.

**"What breaks if removed?"** This is not a drawing. The backend runs the same pipeline again with one part switched off and returns both results so you can compare them. Tests check that each statement written in the lesson matches what the code does.

**How the research and verification system works.** Every claim in a lesson has: exact short excerpts from official sources with links, a locator (the section), and three recorded passes. (1) Primary-source research: gather evidence from official documentation and original papers using a research workflow. (2) Independent cross-check: a separate agent re-fetches each source, checks that every excerpt appears word for word and that the claim says no more than the source does, and looks for other sources; the lesson is corrected from its findings. (3) Technical test: where a claim can be tested in code, a test is tied to it and must pass. A validator refuses to publish a lesson that has unresolved issues, and a test requires every claim marked as technically verified to have had a passing test in that run. This is evidence you can inspect. It is **not** a guarantee that every sentence is correct, and the project says so.

**External APIs and services.**
- *Optional paid AI providers (Anthropic, OpenAI, Google Gemini).* Only used if you add a key to the backend's private settings file. All requests go through the backend, never the browser. A guard refuses a request unless the kill switch is off, features are enabled, a key exists, the model is on an allow-list with known prices, you confirmed that request, the output cap and the hourly and daily limits allow it, and the lifetime budget (configured as $4) would not be exceeded. Keys never reach the browser. Every attempt is recorded in a ledger.
- *Hugging Face / Qdrant model files.* The local embedding model is downloaded once on first use (or baked into a Docker image).
- *Google Fonts.* The page loads three fonts from Google when it opens.
- Nothing else is called; the lessons' sources are cited links, not live calls.

**Testing and deployment.** Tests: 377 backend, 40 frontend unit, 128 end-to-end browser tests, plus a content gate and a claim-coverage gate. GitHub Actions runs four jobs on every push: content validation, backend tests, frontend type-check/tests/build, and end-to-end browser tests with no API keys. Docker Compose runs the app locally. **Production deployment has not been done yet**; the deployment guide in the repository lays out the options.

---

# 2. Verified feature inventory

Confirmed by reading the code, running the app in a browser, and the test suites. At the last full run (2026-10-22): **377 backend tests, 40 frontend unit tests, 128 end-to-end browser tests, all passing.** (Some older numbers in `docs/testing.md` are out of date: 257 / 39 / 107. Use the numbers here.)

## 2.1 The lesson page (identical in all five lessons)
- **3D exploded view.** Drag to rotate, scroll or pinch to zoom. Reset-camera button. The camera frames the fully exploded machine on load.
- **Opening animation.** On load the machine opens up (about 0.35 s after the page is ready) and stage 01 is selected.
- **Explode slider, 0–100%.** Linear: every 10% moves the parts by the same visible amount. Lessons open at 100%. (Until 2026-10-22 the response was eased and 80–100% looked identical; this was fixed.) Keyboard: arrow keys move it by 1%.
- **View toolbar toggles:**
  - **Flow on/off:** play or pause the animated packets moving along the links between stages.
  - **Data:** show what travels on every link (default: only the selected stage's links).
  - **Move:** dragging slides the whole diagram instead of rotating it (3D only; hold Shift or right-drag to slide without turning it on).
  - **Isolate:** fade everything except the selected stage and its neighbours (needs a selected stage).
  - **3D / 2D:** switch to a flat SVG diagram of the same system. The 2D view is also the automatic fallback without WebGL.
  - **Calm:** reduce motion (also follows the operating system setting).
  - **Reset camera.**
- **Keyboard:** with the model focused, ← → move between stages, Enter isolates, Esc clears. Every part is also reachable as a button in the stage bar and in 2D. Screen readers get an announcement when the selection changes.
- **Stage bar** along the bottom: one card per stage with its icon and tagline; clicking jumps to that stage. Visited stages are marked.
- **Stage panel (right side) — "Understand this stage":** a plain-words explanation, an analogy (explicitly labelled *Analogy · teaching aid*), connected-stage chips, a playable mini example (input → steps → output, with Play and Step), and collapsible sections: *Why it is needed*, *What happens to the data*, *Where it goes next*, *If it is set up wrong*, *Learn more (technical)*. Below it, **goes in / comes out** cards show real values from your last experiment run, and a **What breaks if removed?** card.
- **Verified claims with sources:** each stage lists the claims behind it; each claim card shows its three pass states and links to its sources. A "All N sources for this lesson" drawer lists every source with publisher, version and access date.
- **Status badge** at the top: "Verified: N/N claims through all three passes", plus a progress line: "EXPLORED x/8 · FIXED y/z · REBUILT yes/no". Progress is saved in the backend under an anonymous id stored in the browser.
- **Stage timings strip:** a bar chart of how long each stage took in the last real run.
- **Light and dark theme** toggle in the header; skip-to-content link; layout works on phones with no horizontal scroll (checked by automated tests; real-device testing is listed as a manual step in `docs/mobile-checklist.md`).

## 2.2 The five modes
1. **Explore:** click any part or stage card to see what goes in, what comes out, and what breaks without it.
2. **Tour:** a guided walk through the stages. **Play** advances one stage automatically every 8 seconds (4 seconds at 2×), shows a countdown, and stops at the end; **Pause** stops it anywhere; arrows step manually; Play on the last step restarts from the first. It only starts when the viewer presses Play.
3. **Experiment:** change real parameters and see real results. Runs happen automatically about 0.25 s after the last change (debounced); each is a real backend execution and is logged. Results appear in tabs (see each lesson).
4. **Break & fix:** pick a broken setup (some controls are locked), fix it with the unlocked controls, press **Check my fix**. The server re-runs your settings and answers "Fixed." or "Still broken." with the reason. Locked parameters are forced back to their broken values server-side, so the client cannot cheat. Each lesson has 3 or 4 challenges.
5. **Rebuild:** put the stages in an order that could actually run. Drag them, or use the Move up / Move down buttons. The server checks the order against the real dependency graph.

## 2.3 First-run onboarding
- On a visitor's first-ever visit, a **12-step walkthrough** opens about 1.2 seconds after the scene loads. Steps: welcome; turn the machine; zoom; pull it apart (explode slider); open a stage; learn at your own pace; five ways to learn; play the tour; view controls; ask the tutor; keyboard and touch; you are ready. Some steps ask the viewer to try the control. It can be skipped and replayed any time from the **How to use** button. Completion is remembered in the browser (`localStorage`).

## 2.4 "Ask ExplodeAI" tutor (a floating button on every lesson page)
- Answers **only** from ExplodeAI's own verified lesson content (claims, stage explanations, tours, challenge write-ups). Every sentence shows the claim ids behind it; sources are one click away. If the lessons don't cover a question it says so ("ExplodeAI's lessons don't cover that, so I won't guess").
- Free and offline by default: it uses retrieval over the lessons (keyword search plus a local embedding model, fused), not a language model. No keys.
- Knows which stage you have open. Remembers the last 6 turns of the conversation (the browser sends them back; the server stores no conversation): "explain it simpler", "give me an example", "tell me more", "what did I just ask you about?" all work. Answers greetings and small talk; answers "what are the lessons?" with the course overview; has a "Quiz me" tutor mode on the open stage.
- **Optional paid mode "Explain with AI":** off by default; only available when the owner adds a key and enables it; shows the model, worst-case and actual cost; uses server-built prompts from retrieved passages only. See 2.6.

## 2.5 Real experiments vs simulations (the honest summary)
| Lesson | What really executes | What is simulated, toy or made up |
|---|---|---|
| 01 RAG | Chunking, embedding, keyword search (BM25), rank fusion, 3D projection (PCA), prompt assembly; optional local neural embedder | Default embedder is a simple lexical hashing embedder (it fails synonyms on purpose); the offline answer step is a labelled extractive baseline, not an LLM; the knowledge base is six made-up bike-shop articles |
| 02 Tokenization | A real byte-pair-encoding tokenizer trained at runtime on a tiny corpus; encode and decode | It is ExplodeAI's educational BPE, **not** GPT's, Claude's or Gemini's tokenizer; the corpus is a made-up lighthouse keeper's log |
| 03 Embeddings | The real bge-small-en-v1.5 model, run stage by stage on CPU; real vectors, pooling, ranking | A 24-sentence made-up library; the 3D map is a PCA projection and says how much variance it keeps; results are for Qdrant's ONNX build, not measured against BAAI's original weights |
| 04 Attention | Real attention maths (Q/K/V, scaling, mask, softmax, heads, output) | A **toy**: fixed random weights and word vectors, nothing trained; the patterns do not show what a trained model attends to |
| 05 Agents | The loop, the four tools, argument checking, the approval gate, step limits, token counting | The decision-maker is a short **stand-in rule, not a language model** (labelled *Simulation*); the shop, orders and refunds are made up and no money moves |

## 2.6 Paid AI (optional, off by default)
- The app works fully with no keys. A paid answer is an optional extra in Lesson 01's Experiment → Answer tab and in the tutor's "Explain with AI".
- Server-side guard (fails closed): kill switch, features-enabled flag, key present, model on an allow-list with prices, explicit confirmation per request, output cap, hourly and daily limits, and a lifetime budget (configured at $4.00). Keys never reach the browser; the API only reports whether a key is present.
- **Live paid API calls have been made.** The local ledger (`AIUsage`, read 2026-10-22) records 8 requests between 2026-10-19 and 2026-10-21: OpenAI `gpt-4.1-nano` (6, ok), Google `gemini-3.1-flash-lite` (1, ok) and `gemini-2.5-flash-lite` (1, an error). Their recorded **estimated** cost totals about $0.0007. No Anthropic request is recorded. The ledger stores estimates, so exact bills are on the provider dashboards. The README previously said the clients had never been called live; that was wrong and was corrected on 2026-10-22. The test suite itself never calls paid providers (it uses mocked HTTP and blanks all keys). The creator wants core experiences to stay free and to work without paid services.
- Do not record the paid features on camera: they need keys and show spend.

## 2.7 Known limitations and unfinished things (do not hide these)
- Five lessons exist; nothing else is built. `docs/next-lessons-visuals.md` lists a candidate "Evaluation harness" lesson, which is **planned, not built**.
- No accounts: progress is tied to one browser. Single-node SQLite.
- The tokenizer, the attention layer and the agent's decisions are educational stand-ins (see 2.5).
- Lesson 03 needs the local model (`uv sync --extra neural`, downloaded once on first use); without it that lesson's endpoints return 503. The Docker image includes it.
- Token counts in Lesson 05 use Lesson 02's teaching tokenizer, so they differ from real providers' counts.
- Chunk sizes and context budgets in Lesson 01 are counted in **words**, not tokens.
- **Not yet public.** There is no live website URL yet; deployment has not been done. A deployment and licensing guide (`docs/DEPLOYMENT_AND_LICENSING.md` in the repository) found the app is a static frontend plus a small Python API that needs about 280 MB of memory with its local model loaded, that a single-container deployment behind one web address is the simplest route, and that free hosts sleep when idle (so the first visit after a quiet period can take up to about a minute). There is **no software licence file in the repository yet**; a licence decision is pending. The footer of every page reads **"Made by Neil"** (added 2026-10-22).
- Verification passes give inspectable evidence, not a guarantee of absolute correctness (the project's own wording).
- **Known inconsistency in Lesson 04:** the **Order** preset's note says "the Order matters check in the stats shows it", but the experiment's stats strip has no such readout (see section 3, Lesson 04, for where it does appear). Don't tell viewers to look for it there.
- **Stale docs:** `docs/testing.md` still quotes old test counts (257 backend, 39 unit, 107 browser); use the numbers in this document. (`docs/architecture.md` now describes the linear explode correctly.)

---

# 3. Complete lesson breakdown

Shared structure: each lesson is a machine of 8 stages. The same five modes and the same view controls apply everywhere. "If removed" means the app really ran the system without that part.

### Lesson 01 · Retrieval-Augmented Generation, exploded (25 min, 33 verified claims, 26 sources)

**Learning objectives (from the lesson file)**
- Name the eight stages of a RAG pipeline and what each passes to the next.
- Predict how chunk size, overlap, top-k and context budget change what the model sees.
- Explain why lexical, dense and hybrid retrieval rank chunks differently.
- Diagnose a broken pipeline from its retrieved chunks and assembled prompt.

**Stages (the parts of the 3D machine, in order)**

| # | Stage | What it does | Goes in → comes out | If removed (the real system is run without it) |
|---|---|---|---|---|
| 01 | **Knowledge source** | The documents the model can draw on. | Help-centre articles → Documents | Nothing exists to chunk, index or search, so every question comes back with no evidence. |
| 02 | **Chunker** | Splits documents into retrievable pieces. | Documents → Chunks | Each whole document becomes one chunk. Retrieval can only return entire documents, which use up the context budget faster. |
| 03 | **Chunk embedder** | Turns each chunk into a vector. | Chunks → Chunk vectors | No chunk vectors exist, so dense retrieval scores nothing. Keyword (BM25) retrieval still works because it never needed vectors. |
| 04 | **Vector index** | Stores vectors for fast lookup. | Chunk vectors → Searchable index | Nothing is stored, so no retrieval method has anything to search. |
| 05 | **Query embedder** | Encodes the question into the chunks' vector space. | Your question → Query vector | The question is never embedded, so dense retrieval scores nothing. BM25 still matches the raw question text. |
| 06 | **Retriever** | Ranks chunks and keeps the top k. | Query vector + Searchable index → Top-k chunks | Chunks reach the prompt unranked, in corpus order, so a tight context budget can drop the one chunk that answers the question. |
| 07 | **Prompt assembler** | Packs retrieved chunks and the question into one prompt. | Top-k chunks + Your question → Assembled prompt | The generator receives only the question, with no retrieved documents to ground its answer. |
| 08 | **Generator** | Writes an answer from the assembled prompt. | Assembled prompt → Answer with citations | The prompt is assembled but never answered. |

**How information flows:** Knowledge source → Chunker (documents, document line); Chunker → Chunk embedder (chunks, document line); Chunk embedder → Vector index (chunk vectors, vector line); Vector index → Retriever (searchable index, vector line); Query embedder → Retriever (query vector, vector line); Retriever → Prompt assembler (top-k chunks, document line); Prompt assembler → Generator (assembled prompt, document line).

**Key concepts, accurately stated (all backed by verified claims)**
- RAG retrieves relevant information from a knowledge base and adds it to the model's prompt before the model answers.
- Knowledge lives in the index, so you can update it by replacing the index without retraining the generator.
- Chunk size, boundaries and overlap change what retrieval can find. Overlap reduces the chance that a fact is cut in half at a boundary. Splitting can also strip context a chunk needs.
- An embedding is a vector of numbers; for vectors of length 1, dot product equals cosine similarity. A bi-encoder embeds queries and passages separately, so passages can be embedded once ahead of time.
- A flat index compares the query with every vector (exact). Approximate indexes such as HNSW trade some accuracy for speed.
- BM25 scores keyword matches with diminishing returns for repeated terms (k1) and a document-length adjustment (b). Plain keyword search misses synonyms.
- Reciprocal rank fusion merges rankings using only ranks: score = Σ 1/(k + rank), with k = 60 in the original paper.
- Where documents go in the prompt matters, and models use information at the start or end of a long context better than the middle.
- Retrieval reduces hallucination but does not eliminate it.

**Best interactive features to demonstrate:** the Experiment tab with the **Synonym test**; the **Vector space** tab (3D map with a "variance kept" label); the **Ranking** tab (dense vs BM25 vs hybrid ranks side by side); the **Prompt** tab (which chunks were dropped by the budget); "What breaks if removed?" on the Retriever.

**Interesting experiments viewers can try (observed on 2026-10-22; deterministic)**
- Preset **Synonym test**, question “Can I get my money back?”, Top-k 3, sentence chunks of 40, default **TF-IDF hashing** embedder with **Dense** retrieval: the retrieved chunks are `battery#0`, `returns#0`, `returns#1`. The top result is the battery article, not the returns policy.
- Switch Embedder to **Local neural** (if installed): Dense gives `returns#0`, `warranty#1`, `returns#1`; **Hybrid** gives `returns#0`, `returns#1`, `warranty#1`. The returns policy is now first.
- Challenge **The fact that got cut in half**: set chunk size 8 and overlap 0 and watch the return window split across chunks.
- Challenge **Retrieved, then dropped**: the right chunk is retrieved but the context budget (15 words) drops it.

**Common misconceptions to address:** "RAG stops hallucination" (it reduces it, it doesn't eliminate it); "retrieved means the model saw it" (the budget can drop it); "a bigger top-k is always better" (it costs context budget); "embeddings from any model can be mixed" (generally they can't); "keyword search and embeddings do the same thing" (they fail in different ways).

**Real vs simulated:** see 2.5. The six articles are fictional (Ridgeline Bikes); the default embedder is deliberately weak.

**Presets built into the Experiment tab**
- **Return policy**: “How long do I have to return a bike, and what must I include?”
- **Warranty**: “What does the warranty cover for the frame and for components like brakes?”
- **Battery storage**: “How should I store the battery long term?”
- **Synonym test (lexical embedder fails it)**: “Can I get my money back?”

**Break & fix challenges (each fails when broken and passes with a known fix)**
- **The fact that got cut in half**: The return window is split across two chunks, so no retrieved chunk contains all of it. Fix the chunking without changing the question, strategy or retriever.
- **Half an answer**: The question needs two facts that live in different chunks, but the retriever only returns one. Fix it using retrieval settings only.
- **The ranker that missed**: With k = 3, dense retrieval still misses the chunk about the frame's lifetime warranty. Keep k at 3 and change how chunks are ranked.
- **Retrieved, then dropped**: The right chunk is retrieved, but it never reaches the model. Fix it without changing retrieval.

**Tour order (Tour mode, one stage per step):** Start with what the model doesn't know → Cut documents into retrievable pieces → Turn chunks into vectors → Store the vectors → Encode the question the same way → Rank and keep the top k → Assemble the prompt → Generate, and check the sources.

**What each visual is labelled as in the product**
- **Conceptual diagram** (conceptual): Positions and shapes are a visual metaphor. Data flow follows the real pipeline order.
- **Conceptual animation** (conceptual): Moving packets show which stage feeds which. Orange solid lines carry text, dashed lines carry vectors, and the blue dotted line is your question. Their speed carries no meaning.
- **Real execution, stage removed** (real execution): The pipeline really runs without the chosen stage, side by side with the full pipeline.
- **Real execution** (real execution): Chunking, embedding, retrieval and prompt assembly run on the ExplodeAI backend with the parameters you set.
- **Real data, approximate projection** (real execution): The real chunk and query vectors are projected to 3D with PCA. 3D distances only approximate the true ones.
- **Real execution, not an LLM** (real execution): The offline answer is an extractive baseline that quotes retrieved sentences. It is not a language model.

**Official documentation and verified references used by this lesson** (every claim cites these with a short excerpt; all were read and re-checked for the lesson)
- Introducing Contextual Retrieval. Anthropic, published 19 Sep 2024. <https://www.anthropic.com/news/contextual-retrieval> (read 2026-10-18)
- RAG Engine overview. Google Cloud, last updated 2026-10-16 (page brands it part of Gemini Enterprise Agent Platform). <https://docs.cloud.google.com/vertex-ai/generative-ai/docs/rag-engine/rag-overview> (read 2026-10-18)
- Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. arXiv / NeurIPS 2020, arXiv v4 (12 Apr 2021); full text read via ar5iv rendering. <https://arxiv.org/abs/2005.11401> (read 2026-10-18)
- Recursive text splitter. LangChain documentation, live page at access date. <https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter> (read 2026-10-18)
- Retrieval guide. OpenAI (API docs), live page at access date (no date shown). <https://developers.openai.com/api/docs/guides/retrieval> (read 2026-10-18)
- Vector embeddings guide. OpenAI (API docs), live page at access date (no date shown; platform.openai.com redirects here). <https://developers.openai.com/api/docs/guides/embeddings> (read 2026-10-18)
- MetricType and distances (wiki). Meta AI Research — facebookresearch/faiss, GitHub wiki page at access date. <https://github.com/facebookresearch/faiss/wiki/MetricType-and-distances> (read 2026-10-18)
- Embeddings. Anthropic (Claude Platform docs), live page at access date (docs.claude.com redirects here). <https://platform.claude.com/docs/en/build-with-claude/embeddings> (read 2026-10-18)
- Retrieve & Re-Rank. Sentence Transformers documentation (Hugging Face), docs for sentence-transformers v6.1.0. <https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html> (read 2026-10-18)
- Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. arXiv / EMNLP 2019, v1 (arXiv PDF 1908.10084v1; abstract page as of access date). <https://arxiv.org/abs/1908.10084> (read 2026-10-18)
- Dense Passage Retrieval for Open-Domain Question Answering. arXiv / EMNLP 2020, arXiv v3 (30 Sep 2020). <https://arxiv.org/abs/2004.04906> (read 2026-10-18)
- Guidelines to choose an index (wiki). Meta AI Research — facebookresearch/faiss, GitHub wiki page at access date. <https://github.com/facebookresearch/faiss/wiki/Guidelines-to-choose-an-index> (read 2026-10-18)
- Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs. arXiv, arXiv v4 (14 Aug 2018); abstract in Pass 1, full text read in Pass 2. <https://arxiv.org/abs/1603.09320> (read 2026-10-18)
- The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval 3(4), 333–389 (DOI 10.1561/1500000019), author-hosted PDF of the 2009 FnTIR monograph. <https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf> (read 2026-10-18)
- Similarity settings (BM25 defaults). Elastic documentation, live page at access date. <https://www.elastic.co/docs/reference/elasticsearch/index-settings/similarity> (read 2026-10-18)
- Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods. SIGIR 2009 (pp. 758–759, DOI 10.1145/1571941.1572114), author PDF of the SIGIR '09 short paper. <http://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf> (read 2026-10-18)
- Cross-Encoders. Sentence Transformers documentation (Hugging Face), docs for sentence-transformers v6.1.0. <https://sbert.net/examples/cross_encoder/applications/README.html> (read 2026-10-18)
- Prompting best practices (long context section). Anthropic (Claude Platform docs), live page at access date (older long-context tips page redirects here). <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices> (read 2026-10-18)
- Lost in the Middle: How Language Models Use Long Contexts. arXiv / TACL vol. 12 (2024), pp. 157–173, arXiv v3 (20 Nov 2023) PDF. <https://arxiv.org/abs/2307.03172> (read 2026-10-18)
- Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools. arXiv, arXiv v1 (30 May 2024); abstract. <https://arxiv.org/abs/2405.20362> (read 2026-10-18)
- Reduce hallucinations. Anthropic (Claude Platform docs), live page at access date. <https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations> (read 2026-10-18)
- Citations. Anthropic (Claude Platform docs), live page at access date. <https://platform.claude.com/docs/en/build-with-claude/citations> (read 2026-10-18)
- Grounding overview. Google Cloud, last updated 2026-10-15. <https://docs.cloud.google.com/vertex-ai/generative-ai/docs/grounding/overview> (read 2026-10-18)
- Embeddings (Gemini API). Google AI for Developers, last updated 2026-10-09. <https://ai.google.dev/gemini-api/docs/embeddings> (read 2026-10-19)
- Embedding model migration. Qdrant documentation (vector-database vendor), live page at access date. <https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/> (read 2026-10-19)
- Text embeddings. Voyage AI documentation, live page at access date. <https://docs.voyageai.com/docs/embeddings> (read 2026-10-19)


---

### Lesson 02 · Tokenization, exploded (20 min, 32 verified claims, 18 sources)

**Learning objectives (from the lesson file)**
- Explain how BPE learns merges from a corpus and replays them, in order, on new text.
- Predict how the number of merges changes vocabulary size and the number of tokens a text needs.
- Explain why a byte-level alphabet never needs an unknown token, and why a character alphabet can.
- Read token counts critically. They depend on the tokenizer, so they do not transfer between models or providers.

**Stages (the parts of the 3D machine, in order)**

| # | Stage | What it does | Goes in → comes out | If removed (the real system is run without it) |
|---|---|---|---|---|
| 01 | **Training corpus** | The text the tokenizer learns its merges from. | Lighthouse log → Training text | Nothing is learned: zero merges, so text is spelled one byte per token, or entirely as [UNK] with the character alphabet. |
| 02 | **Pre-tokenizer** | Cuts text into word-like pieces before any merging. | Training text → Word pieces | Text is no longer cut at word boundaries, so learned merges can join pieces of different words. |
| 03 | **Base alphabet** | The starting symbols every piece is spelled with. | Word pieces → Symbol sequences | There are no starting symbols, so every character of the input becomes [UNK] and the text cannot be recovered. |
| 04 | **Merge learner** | Repeatedly merges the most frequent adjacent pair. | Symbol sequences → Ordered merges | No merges are learned: every token is a single base symbol, so the sequence is as long as it can be. |
| 05 | **Vocabulary** | Base symbols, learned merges, and special tokens, each with an id. | Ordered merges → Vocabulary + merge order | No table maps symbols to ids, so the encoder cannot produce any token ids. |
| 06 | **Input text** | New text to turn into tokens. | Your text → New text | There is nothing to encode, so no tokens are produced. |
| 07 | **Encoder** | Pre-tokenizes, spells in base symbols, then replays the merges in order. | Vocabulary + New text → Token ids | No ids are produced, so the decoder has nothing to turn back into text. |
| 08 | **Decoder** | Turns token ids back into bytes, then text. | Token ids → Text | Ids are produced but never turned back into text, so the round trip cannot be checked. |

**How information flows:** Training corpus → Pre-tokenizer (training text, document line); Pre-tokenizer → Base alphabet (word pieces, document line); Base alphabet → Merge learner (symbol sequences, vector line); Merge learner → Vocabulary (ordered merges, vector line); Vocabulary → Encoder (vocabulary and merge order, vector line); Input text → Encoder (new text, query line); Encoder → Decoder (token ids, vector line).

**Key concepts, accurately stated**
- BPE started as a compression technique: repeatedly replace the most frequent pair of symbols with a new symbol. Training starts from single symbols, counts adjacent pairs, merges the most frequent pair, and repeats.
- The final vocabulary is the starting alphabet plus one symbol per merge (plus special tokens), so the number of merges sets the vocabulary size.
- To tokenize new text: split into base symbols, then apply the learned merges **in the order they were learned**.
- A byte-level alphabet has only 256 symbols and can encode any text, so it needs no unknown token. A character alphabet limited to the training characters turns anything else into an unknown token and the text can't be recovered.
- In GPT-style tokenizers a space usually belongs to the start of the next word, so " the" and "the" are different tokens.
- Tokens are not words or characters. **Token counts depend on the tokenizer**, so counts from one model do not transfer to another.
- Providers price and limit by tokens, which is why counts matter in practice.

**Best interactive features to demonstrate:** the **Merges learned** slider with the **Tokens** tab (colourful token strip); the **Replay** tab (watch each merge happen step by step); the **Merges** tab (the learned merge table); the **Trade-off** chart (vocabulary size vs tokens for your text).

**Interesting experiments viewers can try (observed 2026-10-22; deterministic; byte alphabet, word pre-tokenizer, learned order)**
- Default sentence “The keeper lit the lantern at dusk.”: **35 tokens at 0 merges → 15 at 25 → 8 at 100 → 8 at 300**; vocabulary 257 → 282 → 357 → 473.
- Preset **Unseen words**, “The lanternkeepers rewound clockwork.”: **37 → 23 → 18 → 16** tokens at 0 / 25 / 100 / 300 merges. At 100 merges the pieces are: `The`, ` lantern`, `ke`, `ep`, `er`, `s`, ` `, `r`, `e`, `w`, `o`, `un`, `d`, ` clock`, `w`, `or`, `k`, `.` — known words are single tokens, unseen words fall apart into pieces.
- Preset **Accents and emoji** with base alphabet **Training characters**: characters never seen in training become `[UNK]` and the text can't be decoded; switch to **256 bytes** and it round-trips.

**Common misconceptions:** "a token is a word" (it isn't); "token counts are universal" (they're tokenizer-specific, and this lesson's tokenizer is **not** any provider's); "more merges is always better" (it trades vocabulary size against sequence length); "unknown words break the model" (subword/byte tokenizers spell them out of smaller pieces).

**Real vs simulated:** the BPE training and encoding really run, on a tiny made-up corpus (a lighthouse keeper's log). It is educational and explicitly not GPT's, Claude's or Gemini's tokenizer.

**Presets built into the Experiment tab**
- **Familiar sentence**: “The keeper lit the lantern at dusk.”
- **Unseen words**: “The lanternkeepers rewound clockwork.”
- **Accents and emoji**: “Café crème at the lantern ☕”
- **Numbers (none in the corpus)**: “Tide at 04:15, height 3.2 metres.”

**Break & fix challenges (each fails when broken and passes with a known fix)**
- **The characters that vanished**: The capital C, the accented letters and the emoji come out as [UNK], so the text cannot be decoded back. Fix it without changing the text, the merges or the pre-tokenizer.
- **Over the token budget**: This sentence needs far more tokens than the budget allows. Get it to 12 tokens or fewer without changing the text or how it is split.
- **Merges replayed backwards**: The encoder replays the merges last-learned first, so words the tokenizer learned as single tokens come out in fragments. Make “ keeper” and “ lantern” single tokens again, using only the encoder settings.
- **Tokens that swallowed the spaces**: With no pre-tokenizer, the learner merged across spaces and learned tokens like “ the ” and “d the ”. Stop any learned token from spanning two words without changing the merge count.

**Tour order (Tour mode, one stage per step):** A tokenizer is learned from text → Cut the text into word pieces → Start from bytes → Merge the most frequent pair, again and again → More merges, bigger vocabulary → New text, including words never seen → Replay the merges in order → Decode and compare.

**What each visual is labelled as in the product**
- **Real execution, stage removed** (real execution): The tokenizer really runs without the chosen stage, side by side with the full tokenizer.
- **Conceptual diagram** (conceptual): Positions and shapes are a visual metaphor. Data flow follows the real tokenizer stages.
- **Conceptual animation** (conceptual): Moving packets show which stage feeds which. Their speed carries no meaning.
- **Real execution · educational BPE** (real execution): Training, encoding and decoding run on the ExplodeAI backend with the settings you choose. This is a small BPE written for teaching, not any provider's tokenizer.
- **Real execution, replayed** (real execution): Each step is a merge the backend actually applied to your text, in the order it was learned. The replay only changes which step you look at.
- **Real data, tiny corpus** (real execution): Vocabulary size and token counts measured on the sample corpus, replaying the first n learned merges (identical to training with n merges, which a test checks). Bytes per token are measured on the training corpus itself, so they are in-sample. The trend is real, but the numbers are far from production scale.

**Official documentation and verified references used by this lesson** (every claim cites these with a short excerpt; all were read and re-checked for the lesson)
- Neural Machine Translation of Rare Words with Subword Units. arXiv / ACL 2016, arXiv v5 (10 Jun 2016); cross-checked against ACL Anthology P16-1162 (pp. 1715–1725). <https://arxiv.org/abs/1508.07909> (read 2026-10-18)
- Byte-Pair Encoding tokenization (LLM Course, chapter 6.5). Hugging Face, live page at access date (source file commit e05c3b637f0a, 2025-09-29). <https://huggingface.co/learn/llm-course/chapter6/5> (read 2026-10-18)
- Tokenization algorithms (formerly "Summary of the tokenizers"). Hugging Face Transformers documentation, docs v5.20.1 (source file commit 83eb94c1febf, 2026-02-17). <https://huggingface.co/docs/transformers/tokenizer_summary> (read 2026-10-18)
- Subword Regularization: Improving Neural Network Translation Models with Multiple Subword Candidates. arXiv / ACL 2018, arXiv v1 (29 Apr 2018). <https://arxiv.org/abs/1804.10959> (read 2026-10-18)
- BPE-Dropout: Simple and Effective Subword Regularization. arXiv / ACL 2020, arXiv v2 (abstract via the arXiv export API); added in Pass 2. <https://arxiv.org/abs/1910.13267> (read 2026-10-19)
- SentencePiece: A simple and language independent subword tokenizer and detokenizer for Neural Text Processing. arXiv / EMNLP 2018 (system demonstrations), arXiv v1 (19 Aug 2018); cross-checked against ACL Anthology D18-2012. <https://arxiv.org/abs/1808.06226> (read 2026-10-18)
- Language Models are Unsupervised Multitask Learners. OpenAI, OpenAI PDF (undated; PDF created 2019-02-14, HTTP Last-Modified 2020-09-25). <https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf> (read 2026-10-18)
- Components. Hugging Face Tokenizers documentation, live docs v1.0.0-rc.2 (source file commit 3fe1b852de47, 2026-09-21). <https://huggingface.co/docs/tokenizers/components> (read 2026-10-18)
- tiktoken README. OpenAI (GitHub), git tag 0.14.0 (commit 4e71bbe0c078); PyPI 0.14.0. <https://github.com/openai/tiktoken/blob/0.14.0/README.md> (read 2026-10-18)
- How to count tokens with tiktoken. OpenAI Cookbook (GitHub), notebook last changed in commit db3144982aa2 (2024-10-08). <https://github.com/openai/openai-cookbook/blob/db3144982aa2/examples/How_to_count_tokens_with_tiktoken.ipynb> (read 2026-10-18)
- tiktoken/core.py (Encoding.encode and Encoding.decode docstrings). OpenAI (GitHub), git tag 0.14.0. <https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/core.py> (read 2026-10-18)
- The tokenization pipeline. Hugging Face Tokenizers documentation, live docs v1.0.0-rc.2 (source file commit 3fe1b852de47, 2026-09-21). <https://huggingface.co/docs/tokenizers/pipeline> (read 2026-10-18)
- Glossary (Tokens). Anthropic (Claude Platform docs), live page at access date (redirected from docs.claude.com). <https://platform.claude.com/docs/en/about-claude/glossary> (read 2026-10-18)
- Token counting. Anthropic (Claude Platform docs), live page at access date (redirected from docs.claude.com). <https://platform.claude.com/docs/en/build-with-claude/token-counting> (read 2026-10-18)
- tiktoken/model.py (model to encoding mapping). OpenAI (GitHub), git tag 0.14.0. <https://github.com/openai/tiktoken/blob/0.14.0/tiktoken/model.py> (read 2026-10-18)
- Key concepts (Tokens). OpenAI API documentation, live page at access date (redirected from platform.openai.com/docs/concepts). <https://developers.openai.com/api/docs/concepts> (read 2026-10-18)
- Understand and count tokens. Google AI for Developers (Gemini API docs), Last updated 2026-10-13 UTC. <https://ai.google.dev/gemini-api/docs/tokens> (read 2026-10-18)
- Migrating to Claude Opus 5.5 (Updated token counting). Anthropic (Claude Platform docs), live page at access date; added in Pass 2. <https://platform.claude.com/docs/en/models/opus-5-5/migration-guide> (read 2026-10-19)


---

### Lesson 03 · Embeddings, exploded (25 min, 24 verified claims, 20 sources)

**Learning objectives (from the lesson file)**
- Trace a sentence through tokenizer, encoder, pooling and normalization to one vector.
- Explain why related sentences land close together, and when they don't.
- Choose a similarity measure, and say when cosine, dot product and Euclidean distance agree.
- Diagnose broken setups such as lexical matching, mixed models and missing query instructions.

**Stages (the parts of the 3D machine, in order)**

| # | Stage | What it does | Goes in → comes out | If removed (the real system is run without it) |
|---|---|---|---|---|
| 01 | **Sample library** | The sentences your text is compared against. | Sample sentences → 24 sentences | There is nothing to compare against, so there are no neighbours. |
| 02 | **Your text** | The sentence you want to find neighbours for. | Your text → Model input | There is nothing to embed, so there are no neighbours. |
| 03 | **Tokenizer** | Splits text into WordPiece tokens and ids. | Sentences + Your text → Token ids | The model reads token ids, not raw text, so no vectors are produced. |
| 04 | **Encoder** | Twelve transformer layers give every token a context-aware vector. | Token ids → One vector per token | Token ids exist, but nothing turns them into vectors. |
| 05 | **Pooling** | Turns many token vectors into one sentence vector. | One vector per token → One 384-D vector | There is one vector per token but none for the whole text, so texts of different lengths cannot be compared. |
| 06 | **Normalizer** | Scales the vector to length 1. | One 384-D vector → Unit-length vector | Vectors keep their raw length, so dot-product scores are no longer bounded between -1 and 1. Cosine itself is unaffected. |
| 07 | **Similarity** | Scores your vector against every library vector and ranks them. | Your vector + Library vectors → Ranked neighbours | Nothing is ranked: the library comes back in its stored order. |
| 08 | **Semantic space** | A 3D map of the vectors. | All vectors → 3D points | No 3D map is drawn, yet the neighbours are unchanged: the map is only a view of the real vectors. |

**How information flows:** Sample library → Tokenizer (sentences, document line); Your text → Tokenizer (your text, query line); Tokenizer → Encoder (token ids, document line); Encoder → Pooling (token vectors, vector line); Pooling → Normalizer (sentence vector, vector line); Normalizer → Similarity (unit vectors, vector line); Normalizer → Semantic space (unit vectors, vector line).

**Key concepts, accurately stated**
- An embedding turns text into a list of numbers; related text gets vectors that are close, unrelated text further apart.
- Early word embeddings (word2vec) gave one vector per word regardless of context; transformer encoders give the same word a different vector in each context.
- bge-small-en-v1.5 is a 12-layer BERT-style encoder with 384-dimensional output and a 512-token limit; longer text is truncated, so the end never reaches the model. It takes the [CLS] token's vector as the sentence vector and normalizes it to length 1.
- For vectors of length 1, cosine, dot product and Euclidean distance rank results the same way.
- Raw similarity scores are not calibrated: even unrelated texts can score well above zero, so the **order** matters more than the number.
- Vectors from different embedding models generally live in different spaces and can't be compared.
- A 3D picture of high-dimensional vectors loses information. This lesson uses PCA, shows how much variance it keeps, and labels the map approximate; t-SNE plots can mislead about cluster distances.
- For short retrieval queries BGE recommends an instruction prefix ("Represent this sentence for searching relevant passages:"); passages don't need it.
- In the MTEB paper no single embedding model was best at every task.

**Best interactive features to demonstrate:** the **Semantic space** tab (3D map: your text flies in among 24 sentences in four topics, with shapes and colours per topic; hover to read; a "Show as table" alternative); the **Neighbours** list; the **Tokens** tab; the **Vector** tab (real numbers); the **Library embedder / Your-text embedder** switches.

**Interesting experiments viewers can try (observed 2026-10-22; deterministic; neural embedder, [CLS] pooling, cosine, top 3)**
- Preset **Bookshelf**, “a place to put my books”: nearest neighbours are the bookshelf sentence (0.695), the desk (0.566) and the armchair (0.554), all *furniture*. With the **Lexical** embedder the same search returns animal sentences at score 0.0, because no word is shared.
- Preset **Where it goes wrong**, “a vehicle that runs on rails”: the neural top three are a truck (0.619), a horse (0.613) and a small plane (0.597). The train sentence is **not** in the top three; the lesson says it ranks 14th of 24. A good honest example that embeddings are approximate.
- Preset **Commute**, “getting to the office”: the top match is a desk (0.588), then a bus (0.561). This is the lesson's "short query" challenge: switching the BGE query instruction on is the intended fix, and the lesson notes the margin is thin (it is a tendency, not a guarantee).
- Preset **Long text** shows the 512-token cut-off (the Tokens tab warns the text was truncated).

**Common misconceptions:** "similar score = similar meaning in a calibrated way" (scores are relative); "the 3D map is exact" (it's an approximate projection); "any two embeddings can be compared" (not across models); "embeddings understand like humans" (they're trained to place related text close, and fail in visible ways).

**Real vs simulated:** the neural model is real and runs locally. The library is made up. The map is an approximate PCA view, labelled as such.

**Presets built into the Experiment tab**
- **Puppy**: “A puppy playing fetch in the park”
- **Bookshelf**: “a place to put my books”
- **Commute**: “getting to the office”
- **Where it goes wrong**: “a vehicle that runs on rails” (The train sentence never says "rails", and this small model ranks it only 14th of 24, below a truck, a horse and a plane. Nearby in meaning is not the same as correct.)

**Break & fix challenges (each fails when broken and passes with a known fix)**
- **Same meaning, no shared words**: No library sentence shares a content word with this question, so the search finds nothing useful. Fix it without changing the question.
- **Two models, one search**: The library was embedded with one model and your text with another. Make the search work again without re-embedding the library.
- **The short query**: For this short search query the top match is a desk, not a way to get to work. Fix it without changing the text, the model or the similarity measure.

**Tour order (Tour mode, one stage per step):** Start with what you'll search → Your text goes in → Text becomes token ids → Every token gets a vector → Many vectors become one → Length becomes 1 → Rank by closeness → See the clusters.

**What each visual is labelled as in the product**
- **Real execution, stage removed** (real execution): The model really runs without the chosen stage, side by side with the full model.
- **Conceptual diagram** (conceptual): Positions and shapes are a visual metaphor. Data flow follows the real pipeline order.
- **Conceptual animation** (conceptual): Moving packets show which stage feeds which. Solid lines carry text, dashed lines carry vectors, and dotted is your text. Speed carries no meaning.
- **Real execution** (real execution): bge-small-en-v1.5 (Qdrant's reduced-precision ONNX port, via fastembed) runs locally, stage by stage, on your text.
- **Real data, approximate projection** (real execution): The real 384-D vectors projected to 3D with PCA. Distances in 3D only approximate the real ones.

**Official documentation and verified references used by this lesson** (every claim cites these with a short excerpt; all were read and re-checked for the lesson)
- Vector embeddings guide. OpenAI (API docs), live page at access date (no date shown; platform.openai.com redirects here). <https://developers.openai.com/api/docs/guides/embeddings> (read 2026-10-18)
- Efficient Estimation of Word Representations in Vector Space. arXiv, arXiv v3 (7 Sep 2013). <https://arxiv.org/abs/1301.3781> (read 2026-10-19)
- How Contextual are Contextualized Word Representations?. arXiv / EMNLP 2019, arXiv v1 (2 Sep 2019) PDF. <https://arxiv.org/abs/1909.00512> (read 2026-10-19)
- BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. arXiv / NAACL 2019, arXiv v2 (24 May 2019). <https://arxiv.org/abs/1810.04805> (read 2026-10-19)
- BAAI/bge-small-en-v1.5 (model card and config files). Beijing Academy of Artificial Intelligence (Hugging Face), repo commit 5c38ec7 (last modified 2024-02-22). <https://huggingface.co/BAAI/bge-small-en-v1.5> (read 2026-10-19)
- Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. arXiv / EMNLP 2019, v1 (arXiv PDF 1908.10084v1; abstract page as of access date). <https://arxiv.org/abs/1908.10084> (read 2026-10-18)
- SimCSE: Simple Contrastive Learning of Sentence Embeddings. arXiv / EMNLP 2021, arXiv v4 (18 May 2022). <https://arxiv.org/abs/2104.08821> (read 2026-10-19)
- Computing Embeddings. Sentence Transformers documentation (Hugging Face), live docs at access date (v6.x). <https://sbert.net/examples/sentence_transformer/applications/computing-embeddings/README.html> (read 2026-10-19)
- fastembed — ONNX text embedding implementation. Qdrant — qdrant/fastembed (GitHub), main at commit de502ca (2026-10-15). <https://github.com/qdrant/fastembed/blob/main/fastembed/text/onnx_embedding.py> (read 2026-10-19)
- Embeddings. Anthropic (Claude Platform docs), live page at access date (docs.claude.com redirects here). <https://platform.claude.com/docs/en/build-with-claude/embeddings> (read 2026-10-18)
- Embeddings (Gemini API). Google AI for Developers, last updated 2026-10-09. <https://ai.google.dev/gemini-api/docs/embeddings> (read 2026-10-19)
- Introduction to Information Retrieval, §6.3.1 Dot products. Cambridge University Press (online edition), online edition at access date. <https://nlp.stanford.edu/IR-book/html/htmledition/dot-products-1.html> (read 2026-10-19)
- Retrieve & Re-Rank. Sentence Transformers documentation (Hugging Face), docs for sentence-transformers v6.1.0. <https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html> (read 2026-10-18)
- Embedding model migration. Qdrant documentation (vector-database vendor), live page at access date. <https://qdrant.tech/documentation/tutorials-operations/embedding-model-migration/> (read 2026-10-19)
- Text embeddings. Voyage AI documentation, live page at access date. <https://docs.voyageai.com/docs/embeddings> (read 2026-10-19)
- Visualizing Data using t-SNE. Journal of Machine Learning Research 9 (2008) 2579–2605, JMLR published PDF. <https://www.jmlr.org/papers/volume9/vandermaaten08a/vandermaaten08a.pdf> (read 2026-10-19)
- How to Use t-SNE Effectively. Distill (DOI 10.23915/distill.00002), published 13 Oct 2016. <https://distill.pub/2016/misread-tsne/> (read 2026-10-19)
- Matryoshka Representation Learning. arXiv / NeurIPS 2022, arXiv v4 (8 Feb 2024). <https://arxiv.org/abs/2205.13147> (read 2026-10-19)
- MTEB: Massive Text Embedding Benchmark. arXiv / EACL 2023, arXiv v3 (19 Mar 2023). <https://arxiv.org/abs/2210.07316> (read 2026-10-19)
- Create embeddings (API reference). OpenAI (API docs), live page at access date (no date shown). <https://developers.openai.com/api/reference/resources/embeddings/methods/create> (read 2026-10-19)


---

### Lesson 04 · Attention, exploded (25 min, 31 verified claims, 18 sources)

**Learning objectives (from the lesson file)**
- Trace one self-attention head from words to queries, keys and values, scores, weights and a weighted sum.
- Explain why scores are scaled, why a mask hides later words, and why position vectors are needed.
- Read an attention grid without mistaking it for a full explanation of a model.
- Diagnose broken setups: peeking ahead, saturated softmax, and order-blind attention.

**Stages (the parts of the 3D machine, in order)**

| # | Stage | What it does | Goes in → comes out | If removed (the real system is run without it) |
|---|---|---|---|---|
| 01 | **Words in** | The sentence, cut into words. | Your sentence → Words | There are no words, so there is nothing to attend over. |
| 02 | **Vectors + position** | Each word becomes a vector, plus a sense of where it sits. | Words → Word vectors | Without position vectors, and with no mask, each word's output is the same whatever order the words come in, so the sentence is treated as a bag of words. |
| 03 | **Q · K · V** | Every word makes a query, a key and a value. | Word vectors → Queries + Keys + Values | Words are compared directly, so each word's strongest match is itself. |
| 04 | **Score grid** | Each query is compared with every key. | Queries + Keys → Scores | Every visible word gets the same weight, so each output is just an average. |
| 05 | **Mask** | Hide the words a word is not allowed to see. | Scores → Masked scores | Every word can attend to the words after it, so it can peek at the future. |
| 06 | **Softmax** | Scores become shares that add up to 100%. | Masked scores → Attention weights | Raw scores are used as weights, so rows do not add up to 1 and can be negative. |
| 07 | **Weighted sum** | Blend the values using the weights. | Attention weights + Values → Mixed values | There is a table of weights but no weighted sum, so no new word vectors. |
| 08 | **Heads + output** | Heads are joined and projected back. | Mixed values from each head → New word vectors | Each head's result stays separate, so there is no single vector per word. |

**How information flows:** Words in → Vectors + position (words, document line); Vectors + position → Q · K · V (word vectors, vector line); Q · K · V → Score grid (queries and keys, vector line); Score grid → Mask (scores, query line); Mask → Softmax (masked scores, query line); Softmax → Weighted sum (weights, query line); Q · K · V → Weighted sum (values, vector line); Weighted sum → Heads + output (mixed values, vector line).

**Key concepts, accurately stated**
- Attention takes a query and a set of key-value pairs and returns a weighted sum of the values; each value's weight comes from how well the query matches its key.
- In self-attention, queries, keys and values all come from the same sequence, each made by multiplying a word's vector by a learned weight matrix.
- One head computes softmax(QKᵀ/√d_k)V. Softmax turns each row of scores into non-negative weights that add up to 1.
- If query and key components have mean 0 and variance 1, their dot product has variance d_k, so scores grow like √d_k. Dividing by √d_k brings the spread back; without it softmax can saturate on one word.
- A **causal mask** sets later positions' scores to −∞ before the softmax so they get weight 0: a word can't look ahead. This is different from the padding "attention mask" in tokenizers.
- Self-attention alone has no sense of order; position information (in the original Transformer, sine and cosine waves) must be added.
- Multi-head attention runs several heads in parallel and concatenates them with one more projection.
- Cost grows with the square of the sequence length. The KV cache keeps keys and values of earlier words when generating, which is valid because of the causal mask.
- Attention is not the whole Transformer (it also has feed-forward layers, residual connections, layer norm). Attention weights are **not** guaranteed to explain why a model answered as it did.

**Best interactive features to demonstrate:** the **Attention grid** (an accessible table; row = the asking word, column = the word looked at; heights and printed percentages); the **One word** view; the **Q · K · V** and **Output** tabs; the **Causal mask** switch (hidden cells shown with a hatch and a dash, not colour alone); the Heads switch (1, 2, 4, 8) and per-head view.

**Interesting experiments viewers can try (observed 2026-10-22; deterministic; toy layer)**
- Preset **Order**, “dog bites man”: with **Position vectors off** (and mask off) the layer cannot tell the sentence from “man bites dog”: the backend's order-change measure is exactly **0**; with position vectors **on** it is about **0.45**. In the interface this shows up in two places: the **Order-blind attention** challenge (its check says reordering "changes nothing: the layer treats the sentence as a bag of words" until Position vectors are on) and the **What breaks if removed?** card on **Vectors + position** ("Order matters: yes/no"). It is **not** shown in the experiment's numbers strip.
- Default sentence “the cat sat on the mat”, 2 heads, scaling on: the strongest weight averages about **35%** of each row. With **8 heads and scaling off** it averages about **63%**: attention piles onto single words (the "One word takes everything" challenge).
- Turn the **Causal mask** on: the upper triangle of the grid (15 cells for a 6-word sentence) is hidden and "Attention on later words" reads 0%.

**Common misconceptions:** "the toy grid shows what a real model attends to" (it doesn't: weights are random and untrained; the lesson says so everywhere); "attention weights explain the model" (contested in the literature); "attention is the whole Transformer" (it isn't); "the causal mask and the padding mask are the same" (they're different); "attention is cheap" (it's quadratic in length).

**Real vs simulated:** the attention maths really runs (and is checked against an independent plain-Python implementation). The model is a toy with fixed random weights.

**Presets built into the Experiment tab**
- **Cat**: “the cat sat on the mat” (Repeated words ("the") start from the same vector, but with random weights that does not make them attend to each other. A trained model learns which words to match.)
- **Pronoun**: “the animal did not cross the street because it was too tired” (A trained model might link "it" to "animal". This toy layer has random weights, so it will not. Do not read meaning into its grid.)
- **Order**: “dog bites man” (Turn Position vectors off and the Causal mask off: the layer can no longer tell this sentence from "man bites dog". The Order matters check in the stats shows it.)

**Break & fix challenges (each fails when broken and passes with a known fix)**
- **The model that cheats**: This layer is meant to write text left to right, so each word may only see the words before it. Right now words look ahead. Fix it without changing the sentence.
- **One word takes everything**: With a wide head and no scaling, almost every word attends to a single word. Spread the attention out without changing the sentence.
- **Order-blind attention**: This layer gives each word the same output for "dog bites man" and "man bites dog", whichever order the words come in. Make it sensitive to word order without changing the sentence.

**Tour order (Tour mode, one stage per step):** Start with the words → Meaning plus position → Query, key, value → Compare everything → No peeking → Scores to shares → Blend the values → Join the heads.

**What each visual is labelled as in the product**
- **Real execution, step removed** (real execution): The toy attention layer really runs without the chosen step, side by side with the full layer.
- **Conceptual diagram** (conceptual): Positions and shapes are a visual metaphor. Data flow follows the real order of the computation.
- **Conceptual animation** (conceptual): Moving packets show which step feeds which. Solid lines carry words, dashed lines carry vectors, dotted lines carry scores and weights. Speed carries no meaning.
- **Real execution · toy layer** (real execution): A real attention layer with fixed random weights runs on your sentence. It shows the mechanism, not what a trained model attends to.

**Official documentation and verified references used by this lesson** (every claim cites these with a short excerpt; all were read and re-checked for the lesson)
- Attention Is All You Need. arXiv / NIPS 2017, v7 (2 Aug 2023). <https://arxiv.org/abs/1706.03762> (read 2026-10-19)
- torch.nn.functional.scaled_dot_product_attention. PyTorch documentation, PyTorch 2.14 documentation. <https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.scaled_dot_product_attention.html> (read 2026-10-19)
- torch.nn.functional.softmax. PyTorch documentation, PyTorch 2.14 documentation. <https://docs.pytorch.org/docs/2.14/generated/torch.nn.functional.softmax.html> (read 2026-10-19)
- Online normalizer calculation for softmax. arXiv, v2. <https://arxiv.org/abs/1805.02867> (read 2026-10-19)
- FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness. arXiv / NeurIPS 2022, v2. <https://arxiv.org/abs/2205.14135> (read 2026-10-19)
- A Mathematical Framework for Transformer Circuits. Transformer Circuits Thread (Anthropic), published 22 Dec 2021 (page shows no version or commit). <https://transformer-circuits.pub/2021/framework/index.html> (read 2026-10-19)
- Glossary. Hugging Face Transformers documentation, Transformers v5.20.2 docs (page shows no date). <https://huggingface.co/docs/transformers/v5.20.2/en/glossary> (read 2026-10-19)
- BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. arXiv / NAACL 2019, arXiv v2 (24 May 2019). <https://arxiv.org/abs/1810.04805> (read 2026-10-19)
- RoFormer: Enhanced Transformer with Rotary Position Embedding. arXiv, v5. <https://arxiv.org/abs/2104.09864> (read 2026-10-19)
- How caching works. Hugging Face Transformers documentation, Transformers v5.20.2 docs (page shows no date). <https://huggingface.co/docs/transformers/v5.20.2/en/cache_explanation> (read 2026-10-19)
- Optimizing LLMs for Speed and Memory. Hugging Face Transformers documentation, Transformers v5.20.2 docs (page shows no date). <https://huggingface.co/docs/transformers/v5.20.2/en/llm_tutorial_optimization> (read 2026-10-19)
- Fast Transformer Decoding: One Write-Head is All You Need. arXiv, v1. <https://arxiv.org/abs/1911.02150> (read 2026-10-19)
- GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints. arXiv / EMNLP 2023, v3. <https://arxiv.org/abs/2305.13245> (read 2026-10-19)
- Language Models are Few-Shot Learners. arXiv / NeurIPS 2020, v4. <https://arxiv.org/abs/2005.14165> (read 2026-10-19)
- BAAI/bge-small-en-v1.5 (model card and config files). Beijing Academy of Artificial Intelligence (Hugging Face), repo commit 5c38ec7 (last modified 2024-02-22). <https://huggingface.co/BAAI/bge-small-en-v1.5> (read 2026-10-19)
- Neural Machine Translation by Jointly Learning to Align and Translate. arXiv / ICLR 2015, v7 (19 May 2016). <https://arxiv.org/abs/1409.0473> (read 2026-10-19)
- Attention is not Explanation. arXiv / NAACL 2019, v3 (8 May 2019). <https://arxiv.org/abs/1902.10186> (read 2026-10-19)
- Attention is not not Explanation. arXiv / EMNLP 2019, v2 (5 Sep 2019). <https://arxiv.org/abs/1908.04626> (read 2026-10-19)


---

### Lesson 05 · Tool-using agents, exploded (30 min, 24 verified claims, 15 sources)

**Learning objectives (from the lesson file)**
- Trace one pass round an agent loop: goal, tool list, decision, check, run, result, memory and stop.
- Explain why the model only asks for a tool and the application runs it, and why the application must check the call first.
- Read the cost of a loop: the whole conversation is re-read on every step.
- Diagnose broken setups: a loop that never stops, vague tool descriptions, and an instruction hidden in a tool result.

**Stages (the parts of the 3D machine, in order)**

| # | Stage | What it does | Goes in → comes out | If removed (the real system is run without it) |
|---|---|---|---|---|
| 01 | **Goal** | What the customer asked for. | Customer message → First message | Nothing tells the agent what to do, so it does nothing. |
| 02 | **Tool registry** | The menu of things the agent may ask for. | Tool definitions → Tool list for the model | The agent cannot look anything up, so it answers without checking the order or the policy. |
| 03 | **Decide** | Pick a tool and its arguments, or give the final answer. | Goal + Tool list + Conversation so far → A tool call, or the final answer | Nothing chooses an action, so no tool is ever called and no answer comes out. |
| 04 | **Check** | Is the call well formed? | Tool call → Checked call, or an error | A malformed order ID goes straight to the tool, which finds no such order, so the agent tells the customer their order doesn't exist. |
| 05 | **Run** | The application runs the tool. | Checked call → Raw tool output | Tool calls are made but nothing runs them, so no result ever comes back and the agent repeats the same request until the step limit stops it. |
| 06 | **Result** | What the tool sent back. | Raw tool output → A result message | Tools run but their results never reach the agent, so it repeats the same call until the step limit stops it. |
| 07 | **Context** | The conversation, re-read on every step. | Result message → A longer conversation | The agent only remembers its goal and the latest result, so it forgets what it found and goes round in circles. |
| 08 | **Stop** | Answer, or run out of steps. | Decision → Answer, or a stopped run | Nothing ends the loop, not even the agent's own answer, so it keeps running until the experiment's hard cap cuts it off. |

**How information flows:** Goal → Decide (request, query line); Tool registry → Decide (tool list, vector line); Decide → Check (tool call, vector line); Check → Run (checked call, vector line); Run → Result (raw output, vector line); Result → Context (result message, document line); Context → Decide (whole conversation, document line); Decide → Stop (final answer, document line).

**Key concepts, accurately stated**
- Anthropic separates **workflows** (code orchestrates the model and tools along predefined paths) from **agents** (the model directs its own process and tool use), and calls both "agentic systems". In the typical case an agent is "just LLMs using tools based on environmental feedback in a loop".
- A tool is described to the model with a **name, a description and a schema** for its parameters (JSON Schema for Anthropic and OpenAI; a subset of the OpenAPI schema for Gemini). Anthropic says detailed descriptions are by far the most important factor in tool performance.
- **The model only asks; the application runs the tool** and sends the result back, linked to the call it answers.
- A model's tool call is a request, not a guarantee: validate the arguments before running anything.
- Each step of a plain API loop re-sends the whole conversation, so tokens re-read grow every step. Tool definitions and tool results count as input.
- Agent loops commonly include stopping conditions such as a maximum number of iterations. Autonomy means higher cost and compounding errors.
- **Indirect prompt injection**: instructions planted in data an application retrieves can act like commands. OWASP says it is unclear whether foolproof prevention exists. Mitigations: limit tools and permissions to the minimum necessary, and require a human to approve high-impact actions. The MCP specification says there SHOULD always be a human able to deny tool invocations.

**Best interactive features to demonstrate:** the **Return** preset in the Experiment tab (watch the loop trace: the agent writes “1001”, the **Check** step rejects it, it reads the error and retries with “A1001”, then the refund waits for **Approve this refund**); the tool-match bars under each decision (each tool's score, with the chosen one marked CHOSEN); **What the model reads** tab; the **Token cost** chart; the **Forum post** switch; "What breaks if removed?" on Check, Run and Stop.

**Interesting experiments viewers can try (deterministic)**
- **Return** preset, default settings: 5 decisions; step 2 is rejected ("must match ^A\d{4}$"); step 5 waits for a person. Click **Approve this refund**: 6 steps, answered ("delivered 16 days ago … within 30 days of delivery … Refund R-001 of 2,899.00 CAD was issued"). Total tokens read across the steps is about 11,000 before approval and about 14,000 after, with each step reading more than the last (about 1,475 → 2,799 tokens on the first five).
- Set **Tool descriptions: Vague** and **Step limit: None**: the stand-in keeps searching the help centre until the experiment's own safety cap of **30 steps**, re-reading far more tokens.
- Turn **Forum post: On**, **Person approves refunds: Off**, goal “What is your returns policy?”: the stand-in obeys an instruction hidden in a retrieved page and issues an unapproved refund. Turn approval back on, or switch the refund tool off, and it can't.
- Preset **Too late** (“Can I return order A1002?”): the agent searches the policy, looks up the order, counts 50 days, and says it is past the 30-day window.

**Common misconceptions:** "the model runs the tools" (the application does); "an agent remembers" (in a plain loop, everything is re-sent each step); "a step limit makes the agent correct" (it only stops the damage); "tool results are safe data" (a model reads them like any other text); "this demo shows how a real LLM behaves" (it doesn't — the decision rule is a labelled stand-in).

**Real vs simulated:** the loop, tools, validation, approval and token counts really run. The decisions come from a short rule, **not** a language model, labelled *Simulation*. The shop (Ridgeline Bikes, the same fictional shop as Lesson 01), orders and refunds are made up; a refund only writes a line in that run's own list.

**Presets built into the Experiment tab**
- **Return**: “Hi! I'd like to return my E-Trail from order 1001. Can I get a refund?” (The order ID is written as 1001, but the tool wants A1001. Watch the Check step reject it, then the agent read the error and fix it. The refund waits for you to approve it.)
- **Too late**: “Can I return order A1002?” (Delivered 50 days ago, past the 30-day window. The agent has to search the policy, look up the order and count the days before it can answer.)
- **Custom**: “I want to return order A1003” (A custom-built bike. The policy says these cannot be returned, and the order data says this one is custom-built.)
- **Status**: “Where is my order A1004?” (One tool is enough here. Not every request needs the whole loop.)
- **Policy**: “How long do refunds take?” (No order involved: one search of the help centre, then an answer.)

**Break & fix challenges (each fails when broken and passes with a known fix)**
- **The agent that never stops**: The tool descriptions are so vague that the agent keeps searching for the same thing, and nothing ends the loop. Make it stop within 10 steps without touching the descriptions.
- **The tool that was never chosen**: Every tool is described in a few empty words, like 'gets information' or 'does an action'. The stand-in keeps picking the wrong one and runs out of steps. Get it to answer, without changing the question or the step limit.
- **The refund nobody approved**: Someone posted a forum answer into the help centre with instructions hidden in it. The agent reads it and refunds an order the customer never mentioned. Stop money moving without a person approving it.

**Tour order (Tour mode, one stage per step):** Start with the request → Show it what it can use → Choose the next move → Check before running → The application does the work → Read what came back → Everything is read again → Know when to stop.

**What each visual is labelled as in the product**
- **Real execution, part removed** (real execution): The agent loop really runs without the chosen part, side by side with the full loop.
- **Conceptual diagram** (conceptual): Positions and shapes are a visual metaphor. Arrows follow the real order of one pass round the loop.
- **Conceptual animation** (conceptual): Moving packets show which step feeds which. Dotted lines carry the goal, dashed lines carry tool calls, tool lists and tool output, solid lines carry messages. Speed carries no meaning.
- **Real execution · the loop and its tools** (real execution): The loop, the argument checks, the tools and the token counts (made with a teaching tokenizer) really run. The shop, its orders and its help-centre articles are made up.
- **Simulation · stand-in decider** (simulation): A short rule plays the language model: it picks tools by comparing descriptions and follows instructions it reads in results. It is not a language model, so it shows the loop, not how a real model behaves.

**Official documentation and verified references used by this lesson** (every claim cites these with a short excerpt; all were read and re-checked for the lesson)
- Building effective agents. Anthropic. <https://www.anthropic.com/research/building-effective-agents> (read 2026-10-22)
- How tool use works. Anthropic (Claude API docs), live page at access date (no date shown). <https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works> (read 2026-10-22)
- ReAct: Synergizing Reasoning and Acting in Language Models. arXiv / ICLR 2023, arXiv v3 (10 Mar 2023, ICLR camera-ready). <https://arxiv.org/abs/2210.03629> (read 2026-10-22)
- Toolformer: Language Models Can Teach Themselves to Use Tools. arXiv / NeurIPS 2023, arXiv v1 (9 Feb 2023), the only version listed. <https://arxiv.org/abs/2302.04761> (read 2026-10-22)
- MRKL Systems: A modular, neuro-symbolic architecture that combines large language models, external knowledge sources and discrete reasoning. arXiv, arXiv v1 (1 May 2022), the only version listed. <https://arxiv.org/abs/2205.00445> (read 2026-10-22)
- Define tools. Anthropic (Claude API docs), live page at access date (no date shown). <https://platform.claude.com/docs/en/agents-and-tools/tool-use/define-tools> (read 2026-10-22)
- Function calling. OpenAI (API docs), live page at access date (no date shown). <https://developers.openai.com/api/docs/guides/function-calling> (read 2026-10-22)
- Function calling with the Gemini API. Google AI for Developers, live page at access date (no date shown). <https://ai.google.dev/gemini-api/docs/function-calling> (read 2026-10-22)
- Tool use with Claude (overview, including pricing). Anthropic (Claude API docs), live page at access date (no date shown); the old tool-use-pricing-and-tokens URL redirects here. <https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview> (read 2026-10-22)
- Tools (Model Context Protocol specification). Model Context Protocol, specification 2025-06-18 (read as this dated version; a newer version may exist). <https://modelcontextprotocol.io/specification/2025-06-18/server/tools> (read 2026-10-22)
- Running agents (OpenAI Agents SDK for Python). OpenAI, live page at access date (no version or date shown). <https://openai.github.io/openai-agents-python/running_agents/> (read 2026-10-22)
- Context windows. Anthropic (Claude API docs), live page at access date (no date shown). <https://platform.claude.com/docs/en/build-with-claude/context-windows> (read 2026-10-22)
- Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection. arXiv, arXiv v2 (5 May 2023); first posted v1 on 23 Feb 2023. <https://arxiv.org/abs/2302.12173> (read 2026-10-22)
- LLM01:2025 Prompt Injection (OWASP Top 10 for LLM Applications). OWASP GenAI Security Project, 2025 list; page shows only a 2025 copyright. <https://genai.owasp.org/llmrisk/llm01-prompt-injection/> (read 2026-10-22)
- LLM06:2025 Excessive Agency (OWASP Top 10 for LLM Applications). OWASP GenAI Security Project, 2025 list; page shows only a 2025 copyright. <https://genai.owasp.org/llmrisk/llm062025-excessive-agency/> (read 2026-10-22)


---

# 4. LinkedIn video demonstration guide

## 4.0 Set-up for every recording
- **Run the app locally:** `make dev` (API on port 8000, web on http://127.0.0.1:5173). Use a wide desktop window (the lesson page has the 3D scene on the left and the stage panel on the right). Check at your recording size that stage labels don't overlap; if they crowd, press **Isolate**, switch to **2D**, or use a larger window.
- **Lesson 03 needs the local model** (installed by `make setup`; downloaded on first use). Do one practice run first so the first real take isn't slow.
- **Wait 3–4 seconds after page load.** The 3D scene loads lazily ("Loading 3D view…") and the machine opens with a short animation.
- **First-visit walkthrough:** it opens by itself on a browser profile that has never visited. For a clean demo, press **Skip**, or use a profile that has finished it. To *record* the walkthrough, use a fresh browser profile.
- **Progress counters** ("EXPLORED 3/8 · FIXED 1/3 …") persist per browser. Use a fresh profile or clear site data if you want a clean 0/8 on screen.
- **Do not leave Calm on** (it removes the moving data packets). Leave **Flow on**.
- **Don't click paid features** (Lesson 01 Answer tab "Ask a real LLM", the tutor's Explain with AI). They need keys and show spend.
- Results update automatically about a quarter of a second after each control change. After clicking, wait a beat before narrating the result.
- The slider reacts to keyboard arrows (1% per press), which is handy for a slow, controlled explode. Pressing keys while the toolbar is focused can scroll the page.

## 4.1 Intro + RAG (series opener) — see section 6, Video 0
**Most visually engaging moment:** the machine opening up, then the Synonym test flipping from the *wrong* result (battery article first) to the right one after switching the embedder.
**Recording sequence**
1. Open `/` (home) for 2 seconds, click **Retrieval-Augmented Generation, exploded**.
2. Let the machine open. Drag the model slowly to rotate it. Move the **Explode** slider down to 0% and back up to 100%.
3. Click **Chunker** in the stage bar (watch the camera and panel respond). Optionally click **Retriever**.
4. Click the **Experiment** tab. Click the preset **Synonym test**. Leave Embedder on **TF-IDF hashing**, Retrieval **Dense**, Top-k 3. Open the **Chunks** or **Ranking** tab and show the retrieved list (first is the battery chunk).
5. Switch **Embedder** to **Local neural**. Show the first result is now the returns policy. Optionally switch **Retrieval** to **Hybrid**.
6. Optionally open **Vector space** to show your question as a point among chunks (note the "approximate projection" label).
**What viewers should see change:** the retrieved list reorders; the question point in the 3D map moves next to the returns chunks.
**Unpredictable:** "Local neural" is greyed out if the neural extra isn't installed; the first neural run may take a moment.
**Checklist:** ☐ fresh or clean profile, tutorial skipped ☐ neural embedder available ☐ window wide enough, labels readable ☐ Synonym test shows `battery#0` first on lexical ☐ neural shows `returns#0` first ☐ no keys/paid panel on screen.

## 4.2 Tokenization
**Most visually engaging moment:** dragging **Merges learned** from 0 up to 100 and watching the colourful token strip collapse from 35 tokens to 8.
**Sequence**
1. Open Lesson 02, let it open. Click the **Experiment** tab (default text “The keeper lit the lantern at dusk.”).
2. **Tokens** tab: at **Merges learned 0** the strip shows 35 byte-sized tokens. Drag the slider (or use arrow keys) to 25, then 100: the count falls (15, then 8) and the vocabulary grows (257 → 282 → 357).
3. Open **Replay** and step through the merges to show one merge at a time.
4. Click preset **Unseen words**: known words stay whole (` lantern`, ` clock`), unseen words fall into pieces (`ke`,`ep`,`er`,`s`).
5. Click preset **Accents and emoji**, set **Base alphabet** to **Training characters** to show `[UNK]`, then **256 bytes** to fix it.
6. Optionally open the **Trade-off** chart.
**Unpredictable:** none known beyond the general ones. Token counts are this teaching tokenizer's, so say so on camera.
**Checklist:** ☐ merges slider starts at 0 for the take ☐ say "this is a small educational tokenizer, not GPT's" ☐ show 35 → 15 → 8 ☐ UNK example uses Training characters.

## 4.3 Embeddings
**Most visually engaging moment:** typing or choosing a sentence and watching its point land among the 24 sentences in the 3D semantic map.
**Sequence**
1. Open Lesson 03, wait for the neural model (first load can be slow). Experiment tab → preset **Bookshelf**.
2. **Semantic space** tab: rotate the map; hover points; show your point near the furniture group. Open **Neighbours** to read the scores (0.695 bookshelf first).
3. Switch **Library embedder** and **Your-text embedder** both to **Lexical**: neighbours become animal sentences at 0.0 (no shared words). Switch back to **Neural**.
4. Switch only **one** embedder to Lexical to show the "can't compare different models" notice.
5. Try **Where it goes wrong** (“a vehicle that runs on rails”) to show a miss honestly.
6. Optionally: **Tokens** tab for the WordPiece tokens, **Vector** tab for the real numbers.
**Unpredictable:** first neural run is slow; the neural model must be installed; scores are relative, not calibrated (say so).
**Checklist:** ☐ neural model installed and warmed up ☐ Bookshelf first (success) then Lexical (failure) ☐ mention the map is an approximate PCA projection ☐ avoid claiming the top match is "the" answer for every phrase.

## 4.4 Attention
**Most visually engaging moment:** turning the **Causal mask** on and watching the upper triangle of the grid hatch out; or the *Order* demo showing the layer can't tell "dog bites man" from "man bites dog".
**Sequence**
1. Open Lesson 04, Experiment tab, default “the cat sat on the mat”. **Attention grid** tab: explain rows and columns; click a row label.
2. Open **One word** and click “mat” to read where it looks.
3. Switch **Causal mask** to **On**: the upper triangle hatches out (15 cells).
4. Order demo, using **Break & fix**: open the challenge **Order-blind attention** (Position vectors starts Off), press **Check my fix** ("Still broken": reordering changes nothing), switch **Position vectors On**, press **Check my fix** again ("Fixed."). Alternative: select **Vectors + position** and press its **What breaks if removed?** button to compare "Order matters" yes vs no.
5. Optionally set **Heads 8** and **Scale scores Off** to show attention piling on single words.
**Unpredictable:** none known. Always say it is a toy with random weights.
**Checklist:** ☐ say "toy layer, nothing trained" ☐ show the grid table, not just the 3D ☐ mask On then Off ☐ position On/Off for the order demo.

## 4.5 Tool-using agents
**Most visually engaging moment:** the loop trace on the **Return** preset: a bad ID rejected, the agent fixing it, then the refund held for approval, and you pressing **Approve this refund**.
**Sequence**
1. Open Lesson 05. Click the **Experiment** tab. The default **Return** run is already there: show **The loop** tab (5 steps; the second is rejected; the last says "Not run: waiting for a person to approve").
2. Click **Approve this refund**: it becomes 6 steps, "Answered".
3. Open **What the model reads** to show the whole conversation and note it's re-sent every step; open **Token cost** to show the growing bars.
4. Switch **Tool descriptions** to **Vague** and **Step limit** to **None**: show the loop going to the 30-step safety cap.
5. Reset (set Detailed, limit 8). Turn **Forum post** On and **Person approves refunds** Off to show the injected refund; then turn approval On.
6. Optionally click **Check** in the stage bar and press **Run without the check** to show the real "order doesn't exist" failure.
**Unpredictable:** changing any setting **revokes** an earlier approval (by design), so approve last. The stage labels in the 3D view can crowd at some window sizes; use Isolate or 2D if needed. Say clearly that the decisions come from a stand-in rule, not an LLM.
**Checklist:** ☐ say "simulation, not a real model" ☐ approve only once, last ☐ show the tool-match bars for the vague case ☐ forum-post demo ends with approval on.

## 4.6 Reusable moments for any lesson
- **Tour autoplay time-lapse:** Tour tab → Play at 1× (8 s per stage, about a minute for eight stages) or 2×.
- **Break & fix:** pick a challenge, press **Check my fix** on the broken state ("Still broken."), apply the fix, press again ("Fixed.").
- **"What breaks if removed?":** select a stage, press **Run without the …**, and read the side-by-side comparison.
- **Rebuild:** shuffle puzzle; use Move up/down for a clean, readable demo.

---

# 5. Project story and engineering

**Only what the repository supports. Anything about motivation, background, audience, time spent or results is left for you.**

## 5.1 Engineering problems the project solves
- **Teaching systems you can touch:** a reusable 3D exploded-view engine so one lesson spec drives the 3D scene, the 2D fallback, keyboard navigation, labels, link animations and the camera, for any system.
- **Making explanations trustworthy:** a content system where every claim carries exact excerpts, source versions, and three recorded passes, enforced by a validator and CI.
- **Keeping animations honest:** the 3D parts equal the executed pipeline stages; diagram edges equal the stage dependency graph; "what breaks if removed" text is backed by tests that run the real system without that part.
- **Running real systems in a browser product without paid APIs:** real chunking/BM25/rank fusion, a real BPE tokenizer, a real local embedding model, a real attention computation and a real agent loop on the backend; a spend-guarded optional paid path.

## 5.2 How the pieces work together
- A lesson is data: `content/lessons/<id>/lesson.yaml` (claims, components, connections, challenges, tour) and `explain.yaml` (plain-words stage text). The backend loads it into typed models and refuses to serve it unless it is published and valid.
- The frontend lesson page turns that data into an engine spec (parts, links), draws it in 3D, and overlays **live values from your last real run** (for example "4 TOOLS", "2,799 TOKENS").
- Each experiment is a backend pipeline whose stage names are the contract shared with the 3D model and the Rebuild puzzle. Running it returns real results and per-stage timings.
- Break & fix and "what breaks if removed" re-run the same pipeline server-side (with locked parameters forced back, or with a stage removed) and judge the result with check types the engine declares.
- Progress, run history and the paid-AI ledger live in SQLite.

## 5.3 Interesting implementation details (all in the repo)
- The camera finds the distance at which every part fits the viewport by binary search, framing the *fully exploded* layout so it never has to move as parts separate; portrait phones orbit 90° so long pipelines run vertically.
- Labels are plain DOM elements projected from 3D each frame (no per-frame React rendering).
- A 2D SVG layout engine (pills, collision avoidance, leader lines, portrait mode) shares the same spec and is fully keyboard-focusable.
- Per-shape "sub-explosions": slices separate, disks stack, lens elements part.
- Rule-based tutor intent handling plus retrieval; a relevance gate refuses questions the lessons don't cover; the server keeps no conversation state.
- The paid-AI guard **fails closed** and is tested only against mocked HTTP in the test suite, which blanks all keys.
- The agent lesson's token counts come from the Lesson 02 tokenizer, so the lessons compose.
- A fix made on 2026-10-22: the explode slider was eased, so 80–100% looked identical; it is now linear with a unit test pinning equal steps.

## 5.4 Testing and verification (what to say, factually)
- **Content gate:** schema, citations, sources, publishing rule. **Claim-coverage gate:** every claim marked technically passed must have had a passing test in that run.
- **Totals at publication of the fifth lesson:** 144 claims across five lessons; 91 sources in the registry; 377 backend tests, 40 unit tests, 128 browser tests.
- **Per-lesson claims:** RAG 33, Tokenization 32, Embeddings 24, Attention 31, Agents 24.
- **How lessons were verified (from the reports):** Pass 1 used the `deep-research` skill (parallel research agents on primary sources); Pass 2 was a separate agent that re-fetched every cited source and string-matched every excerpt, then the lesson was corrected from its findings; Pass 3 is executable tests. Reports: `reports/<Lesson> verification.md`. For Lesson 05, Pass 2 found no fabricated quotes but required 14 claims to be reworded or corrected, all of which were fixed. The reports state that these passes provide evidence, not a guarantee.
- **AI-assisted development (the creator wants this said openly):** ExplodeAI was built with Claude Code, which helped with the frontend, backend, interactive visualisations, implementation, tests and Git commits, including writing commit messages. The creator guided the vision, educational direction, requirements, visual learning experience and quality bar, and uses Claude Code as his AI-assisted development tool. He does not claim to have hand-written every line, and he wants to understand the whole system (section 1B). The research and verification passes also used AI agents (see 5.4).

## 5.5 Demonstrable achievements (checkable in the repo)
- Five complete lessons, each with an 8-part 3D model, Tour, Experiment, Break & fix (3–4 challenges), and Rebuild.
- 144 cited claims with 3 recorded verification passes each.
- Full accessibility paths (keyboard, 2D fallback, reduced motion, screen-reader announcements) covered by automated tests.
- Built over roughly one week. (The creator prefers not to emphasise exact dates; describe it as a project he has been working on over the past week.)

## 5.6 Things I could not find in the repository (mark/provide)
- Not in the repository: user numbers, feedback received, audience research, repository visibility or licence decision, and any roadmap commitments. The creator says he may add lessons over time but prefers to understand, test and demonstrate the five existing lessons thoroughly first. Do not invent metrics, users or results.

---

# 6. Material available for content

*A neutral menu of what exists, organised by topic, so the creator and Claude Chat can plan the series and each video themselves. Nothing here prescribes an order, length, structure or style. Section 4 gives the exact screen sequences, and section 3 the concepts and demo numbers.*

## Per-lesson material
- **01 RAG** — Concept: giving a model information it wasn't trained on by retrieving it first. Moments: the machine opening; the same question retrieving the wrong chunk with the simple embedder and the right one with the neural one; a fact cut in half by chunking; a right chunk dropped by the context budget; the vector-space map. Teaches: chunking, embeddings in retrieval, keyword vs meaning search, rank fusion, prompt assembly, why RAG reduces but doesn't remove hallucination.
- **02 Tokenization** — Concept: how text becomes the numbers a model reads. Moments: 35 tokens collapsing to 8 as merges are learned; unseen words falling into pieces; the Replay of merges; `[UNK]` appearing and disappearing with the base alphabet. Teaches: byte-pair encoding, vocabulary size vs sequence length, why counts differ between tokenizers.
- **03 Embeddings** — Concept: meaning as position in a space. Moments: a sentence landing among 24 others in 3D; a search finding "bookshelf" for "a place to put my books" with no shared words; the lexical embedder returning nothing useful; an honest miss ("a vehicle that runs on rails"); the 512-token cut-off. Teaches: embeddings, pooling, normalisation, cosine vs dot product, why scores are relative, why vectors from different models can't be compared, why a 3D map is approximate.
- **04 Attention** — Concept: each word choosing which other words to look at. Moments: the attention grid; the causal mask hatching out the future; attention piling onto one word without scaling; a layer that can't tell "dog bites man" from "man bites dog" until position is added. Teaches: queries, keys, values, scaling, softmax, masks, position, heads. Always a toy with random weights.
- **05 Tool-using agents** — Concept: a model in a loop, with the application doing the work. Moments: a malformed ID rejected then fixed; a refund waiting for approval; the whole conversation re-read every step with growing token cost; a loop running to its safety cap; a hidden instruction in a retrieved page causing an unapproved refund. Teaches: the agent loop, tool definitions, validation, approval gates, step limits, context cost, prompt injection. The decisions are a labelled stand-in, not a real model.

## Cross-lesson connections that are true in the product
- Lesson 05 uses the same fictional shop as Lesson 01 (Ridgeline Bikes) and counts its tokens with Lesson 02's tokenizer.
- Lesson 01's neural embedder option is the same local model (bge-small-en-v1.5) that Lesson 03 takes apart; that model is a 12-layer transformer with 12 attention heads on a 384-wide vector, which connects to Lesson 04.
- Lesson 03's 512-token limit is why Lesson 01 splits documents into chunks.
- The tutor's own search is a small RAG system over the lessons, using the techniques of Lessons 01 and 03.

## Cross-cutting topics
- **What breaks if you remove a part** — the real ablation feature, available in every lesson.
- **Break & fix challenges** — a broken system, locked controls, and a server-side check (17 challenges across the five lessons: RAG 4, Tokenization 4, Embeddings 3, Attention 3, Agents 3).
- **Real vs simulated** — every visual says which it is; this is a theme in itself.
- **How the content is verified** — three passes, exact excerpts, and the honest limits (sections 1A and 5.4).
- **Building it with Claude Code** — what the creator directed and what Claude Code did (sections 1A and 5.4); the engineering details in 1B and 5.3.
- **The creator's motivation and the visual-learning idea** — in his words in section 1A, with the boundary that it is personal experience, not a tested claim.
- **The Ask ExplodeAI tutor** — answers only from the lessons, refuses what they don't cover.

## Constraints to carry into any content (from the creator, section 1A)
Maximum 15 minutes per video and shorter where possible, with a considerably shorter introduction; natural, conversational tone; the website as the main link once public; no extra links, no excessive hashtags, no engagement bait; no claim that visual learning is proven faster; no claim that content is guaranteed correct; open about AI-assisted development; nothing the creator cannot explain or demonstrate.

---

# 7. Claude Chat handoff prompt

*Paste this into Claude Chat together with this whole document.*

```text
I'm Neil. I'm attaching the ExplodeAI Creator Bible, which describes my project ExplodeAI, how it works, what it can demonstrate, who I am, and what I want my LinkedIn content to achieve and avoid.

I want your help planning and creating my LinkedIn content about ExplodeAI: an introduction, then videos and posts about the project and what viewers can learn from it. Please plan the series and write the scripts and posts yourself, using the Bible's material (section 6), the screen sequences (section 4), and my goals and boundaries (section 1A).

Treat the Bible as the only source of truth about ExplodeAI. Don't invent features, numbers, quotes, sources, results, users or stories. If something you need isn't in the Bible, ask me. I want to be able to explain and demonstrate everything I present, so tell me when you are relying on something you're unsure about, and keep what is real, what is a toy or a simulation, and what has been verified clearly separated.

Before you start, tell me in a few lines what you understood about the project and about me, and ask any questions you need answered.
```
