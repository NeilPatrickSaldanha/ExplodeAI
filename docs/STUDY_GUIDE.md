# ExplodeAI Study Guide: know your system in and out

Written for Neil, 2026-10-23. Every "you should see…" below was **checked against the real backend** (the numbers are deterministic, so you will see the same ones). Do the guide once from top to bottom and you will know where to start, where to end, and what every control does.

**How to use it:** Part 1 gets the app running. Part 2 is a map of the five modes. Part 3 is a guided Experiment run for each lesson. Part 4 is Break & fix. Part 5 is Rebuild. Part 6 lists the extras that are easy to miss. Part 7 is a teaching arc (where to start, where to end) and a self-test.

---

# Part 1. Starting the app, systematically

## 1.1 One-time setup
You need **uv** (version 0.13 or newer) and **Node 22 or newer** installed. Then, in the project folder (`~/explodeai`):

```bash
make setup
```

This installs the backend (including the local neural model package), the frontend, and the Playwright browser used by the tests. The neural model files themselves download the first time Lesson 03 (or the RAG neural option) runs, so do one practice run before filming.

## 1.2 Every time you work
```bash
make dev
```
- The **API** starts on port 8000 and the **website** on **http://127.0.0.1:5173**. Open that address.
- `Ctrl-C` in the terminal stops both.
- **Check the backend is alive:** open http://127.0.0.1:8000/api/health in a browser. If it answers, the API is up.
- Alternative with no local Python or Node: `docker compose up --build` (same ports).

## 1.3 What "healthy" looks like (a 60-second check)
1. The home page shows five lessons, numbered 01 to 05, and "Made by Neil" bottom right.
2. Open Lesson 01. The machine opens up by itself and stage 01 is selected. The header says **"Verified: 33/33 claims through all three passes"**.
3. Open Lesson 03 and click **Experiment**. Results appear (the first run may take a moment while the model loads). If instead you see an error about the model, run `cd backend && uv sync --extra neural` and restart.
4. If the home page says **"Could not reach the ExplodeAI backend. Start it with make dev"**, the backend isn't running (or port 8000 is taken by another program).

## 1.4 Common situations
| Situation | What to do |
|---|---|
| First-visit walkthrough pops up | Press **Skip**, or replay it any time with **How to use**. To see it as a new visitor again, use a private window or clear the site's data. |
| Progress counters ("EXPLORED 3/8…") aren't zero | Progress is saved per browser. Use a private window or clear site data for a clean start. |
| Port already in use | Stop the other program using 8000 or 5173, or stop an earlier `make dev`. |
| Want to run all the checks | `make test` (content check, backend tests, frontend tests, browser tests). |

## 1.5 Where things live (so you know what you built)
Read in this order and the whole system will make sense:
1. `content/lessons/<lesson>/lesson.yaml` and `explain.yaml`: the lesson itself (claims, stages, challenges, tour). **Start here.**
2. `backend/app/experiments/<lesson>/`: the real code each experiment runs (`pipeline.py` is the main file; `ablation.py` runs it with a part removed).
3. `backend/app/routers/`: the web endpoints the page calls.
4. `frontend/src/lessons/<lesson>/`: the lesson's screens.
5. `frontend/src/engine/`: the reusable 3D exploded-view engine (shared by all lessons).
6. `frontend/src/lessons/shared/cine/`: the lesson shell (modes, tour, toolbar) shared by all lessons.
7. `backend/tests/` and `frontend/e2e/`: the proof that it works.

---

# Part 2. The modes, in a few lines (Explore and Tour you know)

- **Experiment.** You change real settings and the backend **really runs** the system, then shows the results in tabs. It re-runs about a quarter of a second after each change. The same numbers also appear as small live labels on the 3D parts. *Look for:* what changed in the results when you changed one thing.
- **Break & fix.** The app gives you a system that is **broken in one specific way**. Some controls are **locked** (the line "LOCKED · …" lists them), the others are yours. You press **Check my fix** and the server re-runs your settings and answers **"Fixed."** or **"Still broken."** with the reason. **Hint** opens a clue. After you fix one, it explains *why* it was broken. *Look for:* the check message: it tells you exactly what is wrong.
- **Rebuild.** A shuffled list of the lesson's stages. Put them in an order that could actually run (each stage after everything it needs). Drag, or use the **Move up / Move down** buttons, then press **Check order**. *Look for:* the message telling you which stages run too early.
- **"What breaks if removed?"** (inside the stage panel, in Explore and Tour). This is the hidden fourth experiment: press **Run without the …** and the system really runs without that part, side by side with the full run.

**Order I recommend:** Explore and Tour first (what the parts are), then Experiment (how settings change results), then Break & fix (diagnosing), then Rebuild (the capstone: do you know what depends on what).

---

# Part 3. Guided experiments (do this, expect that)

For each lesson: open it, click **Experiment**, and follow the steps. "Tab" means the result tabs inside the Experiment panel.

## Lesson 01 · RAG
*Idea: a model can't know your documents, so you search them first and put the best pieces in the prompt.*

**Experiment 1: see the pipeline at its defaults.** Leave everything as it is (question "How long do I have to return a bike?", sentence chunks of 40 words, overlap 0, TF-IDF hashing, Dense, top-k 3, budget 200 words).
- **Chunks tab:** the six made-up help articles became **11 chunks**. The retrieved ones are marked: `returns#0`, `battery#1`, `returns#1`.
- **Notice:** `battery#1` is there even though the question is about returns. The default embedder is deliberately simple, so it sometimes picks the wrong thing. That is the setup for Experiment 4.
- **Answer tab:** a labelled **extractive baseline, not an LLM**: it quotes "Ridgeline Bikes accepts returns of unused bikes within 30 days of delivery." and "Returned bikes must include the original packaging."

**Experiment 2: change the chunk size.** Set **Chunking: Fixed words**, **Chunk size 8**, **Overlap 0**.
- You now have **37 chunks** (tiny pieces). Retrieved: `returns#0`, `battery#3`, `warranty#2`.
- Set **Overlap to 4**: **65 chunks**, and neighbouring chunks now share words.
- Set **Chunk size 120**: only **6 chunks**, one per article. The retrieved set is `returns#0`, `service#0`, `warranty#0`, and the prompt now carries about 137 words of your 200-word budget.
- **What to take away:** small chunks cut facts in half; big chunks drag in unrelated text and use up the budget.

**Experiment 3: top-k and budget.**
- Set **Top-k 1**: only `returns#0` is retrieved. Set **Top-k 6**: six chunks and about 145 words of context.
- Set **Context budget 15 words** (with top-k 3). **Prompt tab:** **1 chunk included, 2 dropped**. The right chunk can be retrieved and still never reach the model.

**Experiment 4: the synonym test.** Click the preset **Synonym test** ("Can I get my money back?"), top-k 3, sentence chunks of 40.
- **TF-IDF hashing + Dense:** retrieved `battery#0`, `returns#0`, `returns#1`. **The battery article is first.** There's no shared word between "money back" and "refund", so the weak embedder can't connect them.
- Switch **Embedder to Local neural**. **Dense:** `returns#0`, `warranty#1`, `returns#1`. **Hybrid:** `returns#0`, `returns#1`, `warranty#1`. The returns policy is now first.
- **Vector space tab:** your question appears as a diamond among the chunks; the label says how much of the real spread the 3D picture keeps ("approximate projection").
- **What to take away:** keyword matching needs shared words; embeddings match meaning; hybrid combines both rankings.

## Lesson 02 · Tokenization
*Idea: a model reads numbers, not letters. Byte-pair encoding learns which character pairs to glue together.*

**Experiment 1: the merges slider.** Default sentence "The keeper lit the lantern at dusk.", 256 bytes, Words, Learned order. Drag **Merges learned** (or use the arrow keys):
| Merges | Tokens | Vocabulary size |
|---|---|---|
| 0 | **35** | 257 |
| 25 | **15** | 282 |
| 100 | **8** | 357 |
| 300 | **8** | 473 |
- **Tokens tab:** at 0 merges every token is one byte; by 100 it's whole words. After ~100 more merges don't help this sentence.
- **Trade-off tab:** the chart of vocabulary size against tokens for your text, with your current setting marked.
- **Replay tab:** step through the learned merges one at a time. **Merges tab:** the ordered merge table.
- **What to take away:** more merges = bigger vocabulary but shorter sequences.

**Experiment 2: unseen words.** Click **Unseen words** ("The lanternkeepers rewound clockwork."), set merges to 100.
- It becomes 18 tokens (37 at 0 merges, 23 at 25, 16 at 300). Known words stay whole (` lantern`, ` clock`); unseen words fall into pieces (`ke`, `ep`, `er`, `s`, … `un`, `d`).
- **What to take away:** subword tokenizers can spell words they've never seen.

**Experiment 3: accents and emoji.** Click **Accents and emoji**. Set **Base alphabet: Training characters**.
- Some tokens show as `[UNK]` (unknown) and **decoding no longer gives the original text back**. Switch to **256 bytes**: no `[UNK]`, and the text round-trips exactly.
- **What to take away:** a byte alphabet can encode anything; a character alphabet can't.

**Remember to say:** this is **ExplodeAI's small educational tokenizer, not GPT's, Claude's or Gemini's**. Real token counts differ.

## Lesson 03 · Embeddings
*Idea: text becomes a list of numbers; similar meaning lands nearby. This lesson runs a real small model (bge-small) on your computer, stage by stage.*

**Experiment 1: meaning without shared words.** Click **Bookshelf** ("a place to put my books"). Leave both embedders on Neural (bge-small), Pooling [CLS], Cosine.
- **Neighbours tab:** the nearest sentences are the bookshelf (**0.695**), the desk (**0.566**) and the armchair (**0.554**), all furniture.
- **Semantic space tab:** your text appears as a ring among 24 sentences, shaped and coloured by topic. Hover a point to read it. **Show as table** gives the same data as a table.

**Experiment 2: the same search, lexical.** Switch **both** embedders to **Lexical**.
- The neighbours become animal sentences with score **0.0**: no word is shared, so nothing matches. Switch back to Neural.

**Experiment 3: mixing models.** Set **Library embedder: Neural** and **Your-text embedder: Lexical** (only one of them).
- A red notice says the vectors **can't be compared** because they come from different models.

**Experiment 4: the honest miss.** Click **Where it goes wrong** ("a vehicle that runs on rails").
- Top three are a truck (0.619), a horse (0.613) and a small plane (0.597). The train sentence isn't there (the lesson says it ranks 14th of 24). **Embeddings are approximate.**

**Experiment 5: the query instruction.** Click **Commute** ("getting to the office").
- The top match is a **desk** (0.588), then a bus (0.561). Turn **BGE query instruction: On**: the **bus/vehicle** wins (0.515). The lesson says plainly this margin is thin: a tendency, not a guarantee.

**Also try:** the **Tokens tab** (the WordPiece pieces the model reads), the **Vector tab** (the real 384 numbers), and **Long text** (the Tokens tab warns the model cut the text off at 512 tokens).

## Lesson 04 · Attention
*Idea: each word looks at every other word and blends what it finds. This is a **toy** (random weights, nothing trained): it shows the mechanism, not what a real model attends to.*

**Experiment 1: read the grid.** Default "the cat sat on the mat", 2 heads, scale On, mask Off, position On. **Attention grid tab:**
- Each row is "the word asking", each column "the word being looked at". The printed numbers in a row add up to about 100%. **Click a row label** to pick a word.
- Below the grid, the numbers strip says the strongest weight averages about **35%**.

**Experiment 2: one word.** **One word tab**, click "mat": a note says where "mat" looks and how it blends the others.

**Experiment 3: the causal mask.** Set **Causal mask: On**.
- The **upper triangle hatches out** (15 cells for 6 words). "Attention on later words" reads **0%**. A word can't peek ahead.

**Experiment 4: attention piles onto one word.** Set **Heads 8** and **Scale scores: Off**.
- The strongest weight rises to about **63%**: scores get too large, softmax saturates. Turn scaling back **On** to spread it out.

**Experiment 5: word order.** Click **Order** ("dog bites man"). Set **Position vectors: Off**, **Causal mask: Off**.
- The layer can't tell this from "man bites dog". (The interface shows this in **Break & fix → Order-blind attention** and in **"What breaks if removed?" on Vectors + position**, not in the numbers strip.) Turn position **On** and it can.

**Tabs worth opening:** **Q · K · V** (the three roles each word plays) and **Output** (the final vectors).

## Lesson 05 · Tool-using agents
*Idea: a model in a loop. The model only **asks** for a tool; **your code runs it**. The "decisions" here come from a short stand-in rule, **not a language model** (labelled Simulation). The shop and orders are made up.*

**Experiment 1: the Return request.** Default goal "Hi! I'd like to return my E-Trail from order 1001…". **The loop tab** shows 5 steps:
1. Searches the help centre for the returns policy.
2. **Calls `get_order` with "1001"** and the **Check** step **rejects it** ("must match ^A\d{4}$"). The call was never run.
3. Reads the error and retries with **A1001**.
4. Counts days between delivery (2026-10-05) and "today" (2026-10-21): **16 days**.
5. Wants `issue_refund` for 2,899 CAD: **"Not run: waiting for a person to approve."**
- A card says **"The agent wants to move money"**. Click **Approve this refund**: it becomes **6 steps, Answered** ("…delivered 16 days ago… within 30 days of delivery… Refund R-001 of 2,899.00 CAD was issued"). No real money moves; it's a pretend list.
- Under each decision, the **tool-match bars** show each tool's score and which was CHOSEN.

**Experiment 2: what the model reads.** **What the model reads tab:** the whole conversation, which is **re-sent on every step**. **Token cost tab:** bars growing from about 1,475 to 2,799 tokens over the first five steps; about 11,000 tokens read in total (about 14,000 after approval). Every step pays again for everything before it.

**Experiment 3: a runaway loop.** Set **Tool descriptions: Vague** and **Step limit: None**.
- The stand-in keeps searching until the experiment's own **safety cap of 30 steps**, and the token total balloons. Set the step limit back to 8: it stops at 8 with no answer. A limit stops the damage; it doesn't make the agent right.

**Experiment 4: checking off.** Set **Check arguments before running: Off**.
- "1001" goes straight to the tool, which finds no such order, and the agent answers "I couldn't find an order called 1001": confidently wrong.

**Experiment 5: the hidden instruction.** Set the goal to "What is your returns policy?" (type it), **Forum post in the help centre: On**, **Person approves refunds: Off**.
- The stand-in obeys an instruction hidden in a retrieved page and issues an **unapproved refund**. Turn approval **On** (or the refund tool **Off**) and it can't.
- **Note:** changing *any* setting cancels an earlier approval (by design). Approve last.

---

# Part 4. Break & fix: every challenge, with the clue and the fix

**Process for any challenge:** read the brief → look at the **LOCKED** line (those controls are off-limits) → press **Check my fix** *first* to see the failure message → use the **Hint** if stuck → change an unlocked control → **Check my fix** → read the explanation shown when it says **"Fixed."** Fixing a challenge marks it **SOLVED** and raises the "FIXED x/y" counter.

| Lesson | Challenge | What the failure message says | The fix (unlocked control) | What it teaches |
|---|---|---|---|---|
| 01 | **The fact that got cut in half** | “within 30 days of delivery” and “original packaging” are not in a retrieved chunk | **Chunk size 12 or 20** (it starts at 8). **16 fails** (“original packaging” goes missing) | Boundaries split facts, and a bigger chunk isn't automatically better: where the cut falls matters |
| 01 | **Half an answer** | “lifetime warranty” and “covered for 2 years” are not retrieved | **Top-k 3** (starts at 1) | The answer lives in several chunks |
| 01 | **The ranker that missed** | “lifetime warranty” not retrieved, “covered for 2 years” is | **Retrieval: Hybrid** (starts Dense) | Different rankers miss different things |
| 01 | **Retrieved, then dropped** | “between 40 and 60 percent” is not in the assembled prompt | **Context budget 60 words** (starts at 15) | Retrieved isn't the same as read by the model |
| 02 | **The characters that vanished** | 4 tokens are [UNK]; decoding doesn't give back the input | **Base alphabet: 256 bytes** | Bytes can spell anything |
| 02 | **Over the token budget** | The text is 50 tokens; the budget is 12 | **Merges 150** (starts at 0) → **10 tokens** | Merges shorten sequences |
| 02 | **Merges replayed backwards** | “ keeper” and “ lantern” are not single tokens | **Merge order: Learned order** | Merges must be replayed in the order learned |
| 02 | **Tokens that swallowed the spaces** | 84 learned tokens span a word boundary, e.g. “e ” | **Pre-tokenizer: Words** | Cut at word boundaries before merging |
| 03 | **Same meaning, no shared words** | Top match is animals (score 0.0); expected furniture | **Both embedders → Neural** (text is locked) | Keyword matching can't see meaning |
| 03 | **Two models, one search** | Query and library come from different models | **Your-text embedder → Neural** (library is locked on Neural) | Vectors from different models can't be compared |
| 03 | **The short query** | Top match is furniture (0.588); expected vehicles | **BGE query instruction: On** → vehicles 0.515 | Short queries benefit from the instruction (a thin margin) |
| 04 | **The model that cheats** | Words still put 44% of attention on later words | **Causal mask: On** | The mask hides the future |
| 04 | **One word takes everything** | The strongest weight averages 93%: softmax is almost one-hot | **Scale scores: On** (also try more heads) | Scaling by √d_k keeps softmax from saturating |
| 04 | **Order-blind attention** | Reordering changes nothing: a bag of words | **Position vectors: On** | Attention alone has no sense of order |
| 05 | **The agent that never stops** | The loop ran 30 steps (limit for this check: 10) | **Step limit: 8** (descriptions are locked) | A cap stops a runaway loop |
| 05 | **The tool that was never chosen** | The agent never answered | **Tool descriptions: Detailed** | The agent picks tools from their descriptions |
| 05 | **The refund nobody approved** | A refund went out with nobody approving it | **Person approves refunds: On**, or **Refund tool: Off** | Approval and least privilege limit damage |

**Try wrong fixes on purpose.** For example, in “The fact that got cut in half” try chunk sizes 8, 12, 16 and 20 and read each message: 12 and 20 pass, but 16 fails with “original packaging” still missing. The failure messages are the best teachers.

---

# Part 5. Rebuild

**What it is:** the lesson's eight stages come shuffled. You arrange them in an order that **could actually run**: no stage may run before something it needs. **More than one order can be correct.**

**How to do it:** drag a stage by its grip, or press its **Move up** / **Move down** button (works by keyboard and is easier to demonstrate). Press **Check order**.

**What you'll see:**
- Wrong: a message like **"7 stage(s) run before something they need."** (e.g. the chunker listed before the corpus it needs).
- Right: **"Every stage runs after what it depends on."** The header's **REBUILT** switches to **YES** and the lesson remembers it.

**The dependencies you should be able to say out loud:**
| Lesson | What depends on what |
|---|---|
| 01 RAG | Knowledge source → Chunker → Chunk embedder → Vector index → Retriever. Query embedder → Retriever. Retriever → Prompt assembler → Generator. (So the query embedder can sit anywhere before the retriever: that's why several orders work.) |
| 02 Tokenization | Corpus → Pre-tokenizer → Base alphabet → Merge learner → Vocabulary → Encoder (which also needs Input text) → Decoder |
| 03 Embeddings | Sample library and Your text come first (neither needs anything). Tokenizer needs both. Then Encoder → Pooling → Normalizer, and **both** Similarity and Semantic space depend on the Normalizer. |
| 04 Attention | Words → Vectors + position → Q·K·V → Score grid → Mask → Softmax → Weighted sum (needs softmax *and* V) → Heads + output |
| 05 Agents | Goal and Tool registry → Decide → Check → Run → Result → Context. Stop depends on Decide. *(One pass round the loop; the loop-back from Context to Decide is shown as a link, not an order.)* |

A good way to learn: before pressing Check order, say the chain aloud. If you can, you understand the system.

---

# Part 6. Extras that are easy to miss

- **Live labels on the 3D parts** ("4 TOOLS", "2,799 TOKENS") come from your last real run. In Lesson 05 the Stop part shows "WAITING FOR A PERSON" when a refund is held.
- **Goes in / Comes out cards** in the stage panel show real values from your last run.
- **Stage timings strip** under the stage bar shows how long each stage actually took.
- **"What breaks if removed?"** exists on every stage: it's a real re-run, not a drawing.
- **Toolbar:** *Flow* pauses the packets, *Data* labels every link, *Move* slides the diagram instead of rotating, *Isolate* fades everything but the stage and its neighbours, *3D/2D* swaps to a flat diagram, *Calm* reduces motion, ⟳ resets the camera. The Explode slider moves the parts evenly from 0 to 100%, and arrow keys move it 1% at a time.
- **Keyboard:** ← → between stages, Enter isolates, Esc clears.
- **"Understand this stage" sections** (Why, What happens to the data, Where it goes next, If it's set up wrong, Learn more) are collapsed by default. The **mini example** can be played or stepped.
- **Claim cards:** each stage lists the verified claims behind it, with their three pass states and source links. **"All N sources"** at the bottom lists every source with its publisher, version and date read.
- **The "Verified: N/N" badge** counts claims through all three passes. It means the process was completed, **not** that every statement is guaranteed correct.
- **Ask ExplodeAI** (bottom right) answers only from the lessons, with the claims behind each sentence, refuses what it doesn't cover, remembers the last few turns ("explain it simpler", "what did I just ask?"), and has **Quiz me**. "Explain with AI" is off unless a key is configured: don't use it on camera.
- **Progress** is saved per browser: EXPLORED (only your own clicks count), FIXED, REBUILT.
- **How to use** replays the 12-step walkthrough. The theme button switches light and dark.
- **Lesson 03 map:** hover points to read them, **Show as table** for an accessible list. **Lesson 04:** per-head view (Heads 2, 4, 8) and the grid is a real table for screen readers. **Lesson 05:** the **Tools** tab lists the four tools with their descriptions and rules.

---

# Part 7. A teaching arc and a self-test

## Where to start and where to end (default arc for any lesson)
1. **Open the home page** and say what the lesson is for (one sentence from the lesson's objectives).
2. **Let the machine open**, rotate it, slide Explode down and up so people see "a system with parts".
3. **Walk the stages in order** (Tour, or click along): what goes in, what comes out, for each.
4. **Click one stage and press "Run without the …"**: show that the part matters.
5. **Experiment:** one or two of the experiments in Part 3.
6. **Break & fix:** do one challenge live, including a wrong attempt.
7. **Rebuild:** say the dependency chain, then check it.
8. **End** with the claims and sources (one claim card, the sources list) and the limits ("the tokenizer is educational", "the attention layer is a toy", "the agent's decisions are a stand-in").

## Self-test: can you answer these in one or two sentences?
**RAG:** Why can retrieval find the right chunk and the model still never see it? *(The context budget drops chunks that don't fit.)* Why does "money back" fail with the simple embedder? *(No shared words; it's keyword-like.)* What does hybrid do? *(Merges the keyword and meaning rankings using their ranks.)*
**Tokenization:** What does one merge do? *(Glues the most frequent adjacent pair into one new symbol.)* Why does a byte alphabet never need [UNK]? *(Every possible byte is in it.)* Why can't you compare token counts across models? *(Different tokenizers.)*
**Embeddings:** What is pooling? *(Turning many token vectors into one sentence vector; here, the [CLS] token's.)* Why compare order, not score? *(Scores aren't calibrated; even unrelated texts score above zero.)* Why is the 3D map approximate? *(It squeezes 384 dimensions into 3 with PCA and loses information.)*
**Attention:** What do Q, K and V mean? *(What a word looks for, what it offers, what it passes on.)* Why divide by √d_k? *(Keeps the scores' spread steady so softmax doesn't saturate.)* What does the causal mask do? *(Sets later words' scores to −∞ so they get zero weight.)* Why position vectors? *(Attention alone doesn't know word order.)*
**Agents:** Who runs the tool? *(Your application, not the model.)* Why validate arguments? *(A model's call is a request, not a guarantee.)* Why does cost grow each step? *(The whole conversation is re-read every time.)* Why approve refunds? *(An instruction hidden in data can steer the agent; limit tools and require a person for high-impact actions.)*

## Say these limits yourself so no one else has to
- The **tokenizer** is a small teaching one, not any provider's.
- The **attention layer** is a toy with random weights; the grid isn't what a real model attends to.
- The **agent's decisions** come from a stand-in rule, not a language model; the shop is made up.
- The **embedding model** is real, run locally in a reduced-precision build.
- The **verification** shows evidence for each claim; it doesn't guarantee correctness.
- You haven't tested that visual learning is faster; it's your personal experience.
