# Beginner review: rag-pipeline (plain words)

Reviewed: `_source/rag-pipeline.json`, against `lesson.yaml`, `explain.yaml`, `teaching.yaml` and the code in `backend/app/experiments/rag/`. I also ran the pipeline to check every number and chunk name the experiment guide and stage "thread" lines quote.

## Summary

The lesson reads well for a beginner. The index-card story holds together from end to end, the honest "this is a simple helper, not a real AI model" labelling is repeated everywhere it matters, and the "what breaks if removed" lines match what the code really does. Nothing is outright false: every number I re-ran (11, 37, 65, 6 chunks; 66 of 200 words; 145 words; 1 included and 2 left out; service#1 4th versus 11th; the preset top-3 lists) is correct.

The problems are of three kinds:

1. **A few words used before they are explained.** The worst are "the page ... has limited room" at stage 2, "card box" at stage 1, "score", "slot", "word stems", "different spaces", "real spread", "Offline" and "reciprocal rank fusion".
2. **One name per idea is not kept.** The page, prompt, message and sheet are the same thing, and the room, limit and budget are the same thing. So are chunk, piece and card, and fingerprint, vector, embedding and list of numbers.
3. **A handful of places say more than the original.** "Using only what is on the page", "would put them close together", "The two returns chunks are what we want", "cannot be compared" and "the real thing" all go further than the source text or the code.

Counts: 0 WRONG, 12 MISLEADING, 21 CONFUSING.

Note on reading order: the caveat for the fingerprint analogy ("Unlike a real fingerprint...") sits in `big_picture.analogy.breaks`. If a learner meets the stages before the big picture, as this brief orders them, it arrives too late. If the big picture is shown first, it is a long way from stage 3.

---

## Job A and B findings

### CONFUSING (21)

**C1. Prerequisite uses two words the lesson itself teaches later.**
- Quote: "Knowing that a language model reads text in its prompt and writes text back."
- Location: `prerequisites[0]`
- Problem: a true beginner does not know "language model" or "prompt", and this is the very first thing they read. It also tells them they do not qualify.
- Replace: "Knowing that an AI chat program reads the text you type in and writes text back."

**C2. Objectives use "overlap" and "number-fingerprint" before either is explained.**
- Quotes: "how the size of the pieces, the overlap, the number kept and the room on the page change what the model sees" and "searching by number-fingerprint, by keywords and by both together rank the pieces differently".
- Location: `objectives[1]`, `objectives[2]`
- Problem: it is normal for objectives to run ahead, but nothing here hints that these are named things you will meet. "Number-fingerprint search" is especially opaque.
- Replace: "...the overlap (words that two neighbouring pieces share)..." and "...searching by the number lists, by matching keywords, and by both together..."

**C3. "The page" appears at stage 2 with no explanation and no reason for its limit.**
- Quote: "the page you send to the model has limited room." Related: `components[1].explain.why` "and fit on the page", `connections[0].explain` "a page has limited room".
- Location: `components[1].explain.story` (first mention in the lesson)
- Problem: nobody has said the model is sent a page, or why it has limited room. The "page" idea is only built at stage 7. The skipped step is "a model can only read so much at once".
- Replace: "The model can only read so much text at once, so whatever you send it (we will call this the page) has a size limit."

**C4. "Card box" used at stage 1, before it exists.**
- Quote: "rebuilding the card box (cutting them up again and giving the pieces new fingerprints)". The same wording is in `components[0].explain.check.answer`.
- Location: `components[0].explain.story`
- Problem: the learner has not met cutting, fingerprints or the card box yet. The brackets pile three new ideas into one sentence.
- Replace: "...you can change what the system knows just by swapping the documents and preparing them again. Nothing needs training again."

**C5. "Closer" for lists of numbers is never pictured.**
- Quote: "a matter of measuring how close two lists of numbers are."
- Location: `components[2].explain.why`
- Problem: a beginner cannot see how two lists of numbers can be near each other. The earlier source used a map-pin idea, and the plain text dropped it. The tab "Fingerprint map" does this later but is never pointed to here.
- Replace: "Think of each list of numbers as a pin on a map. Pieces about similar things get pins close together, so finding the best match means finding the nearest pins."

**C6. The embedder story needs several reads.**
- Quote: "it builds the fingerprint from the words used (and pairs of neighbouring words), weighted by how rare they are, and folded into 1024 numbers per chunk, so it matches words better than it matches meaning. Unrelated words can occasionally land in the same slot."
- Location: `components[2].explain.story`
- Problem: one 60-word sentence carries four ideas. "Folded" and "slot" are unexplained (the same "folded" is in `explain.example.steps`). Why rare words weigh more is not said.
- Replace: "In this lesson the built-in maker is deliberately simple. It looks at the words in a piece, and at pairs of words side by side, and gives rarer words more weight because they say more. It then squeezes all of that into a list of 1024 numbers. So it matches words better than it matches meaning. Because 1024 is a small space, two unrelated words can occasionally end up in the same place in the list."

**C7. "Score" is never defined, but is used many times.**
- Quotes: "score highest" (`components[2].explain.thread`); "Score every chunk" (`components[5].explain.example.steps`); "every score is about zero" and "(0.643 against 0.641)" (`experiment.guide.presets["Same idea, different words"].notice`); "Fingerprint rank · closeness".
- Problem: the beginner never learns that a score is how well a piece matches, or that bigger means a better match. The two numbers 0.643 and 0.641 are bare.
- Replace (once, at stage 6): "Each piece gets a score, a number saying how well it matches the question. A bigger score is a better match."

**C8. "Word stems" is not explained.**
- Quote: "Made lowercase and cut into word stems"
- Location: `components[4].explain.example.steps[0]`
- Replace: "Turned to lowercase, with endings such as a plural 's' trimmed off, so 'returns' and 'return' count as the same word"

**C9. "Different spaces" and "distances" appear out of nowhere.**
- Quote: "Their lists would live in different spaces, so the distances between them would mean nothing."
- Location: `components[4].explain.check.answer`
- Problem: nothing has said lists of numbers live somewhere or have distances. The stage's own `misconfigured` line is much clearer.
- Replace: "The two lists would be built in different ways, like measuring one thing in inches and another in kilometres, so comparing them would tell you nothing."

**C10. "Offline" is misleading to a layperson.**
- Quote: "Offline, ExplodeAI uses a simple helper that quotes sentences instead of an AI model."
- Location: `components[7].explain.what`
- Problem: to a beginner "offline" means no internet. The experiment runs on the site's own server, so this contradicts what they see. It really means "without calling a paid AI service".
- Replace: "To keep this free, ExplodeAI uses a simple helper that quotes sentences instead of a real AI model."

**C11. "Appears" and "off" in one sentence.**
- Quote: "Below its answer, an optional real-model panel appears; it is off unless the site owner has switched it on."
- Location: `components[7].explain.story`. Same pattern in `experiment.guide.tabs.answer`.
- Problem: it cannot both appear and be off. "Real-model panel" is also not explained.
- Replace: "Below the answer there can be a second box showing a real AI model's answer. It only shows up if the site owner has paid to switch it on."

**C12. The "Same idea, different words" notice stacks unexplained terms.**
- Quote: "battery#0 comes first by a coincidence (two unrelated words ended up in the same slot), and returns#0 and returns#1 follow only because ties are listed in the order of the chunks."
- Location: `experiment.guide.presets["Same idea, different words"].notice`
- Problem: "slot", "ties" and the bare scores are all unexplained, and "every score is about zero" sits beside a first-place score that is actually 0.075 (larger than some genuine matches elsewhere). The real point is lost.
- Replace: "With the simple fingerprint maker, no piece shares a single word with the question, so every piece scores about zero. The top spots are close to random: battery#0 wins by accident, because two unrelated words happened to get the same place in its list. The next two are only there because, when scores are equal, the pieces stay in the order of the documents."

**C13. The "ideas" assume a different starting question from the presets.**
- Quotes: "For the default question all three pick the same three chunks." and "Keeping 1 finds only returns#0."
- Location: `experiment.guide.ideas[1..3]`
- Problem: `ideas[0]` says "leave the question as it is", but the others do not. The "Return policy" button uses a longer question, whose top three are returns#0, service#1 and battery#1 (service#1 is then 2nd by fingerprint and 3rd by keywords, not 4th and 11th). A learner who just clicked the first preset, as the guide told them to, sees different results. The same mismatch exists with `components[5].explain.thread` ("returns#0, battery#1 and returns#1").
- Replace: put one line at the top of `ideas`: "These numbers are for the starting question, 'How long do I have to return a bike?'. If you clicked a quick-start button, put that question back first."

**C14. "Real spread" is meaningless to a beginner.**
- Quote: "The label says how much of the real spread this 3D picture keeps, so treat distances as hints."
- Location: `experiment.guide.tabs.space`
- Replace: "The label says how much of the real differences between the lists survive when they are squashed into this 3D picture. It is never all of it, so treat distances as hints."

**C15. Last sentence of the analogy's limits is muddled.**
- Quote: "A real writer would also sometimes ignore the sheet, and an AI model can too."
- Location: `big_picture.analogy.breaks`
- Problem: "a real writer" versus "an AI model" is unclear: the Writer stage is the AI model. "For a silly reason" also reads as flippant.
- Replace: "A person reading a card understands it. The computer only compares numbers, so it can pull out the wrong card by mistake. And the writer, whether a person or an AI model, may still ignore the sheet and say something not on it."

**C16. Challenge 1: the brief contradicts itself and the explanation has a vague "the whole one".**
- Quotes: "Fix how the documents are cut, without changing the question, the way of cutting or the way of searching." and "tiny chunks carry so few words that the whole one may still rank too low."
- Location: `challenges[0].brief`, `challenges[0].explanation`
- Problem: "fix how they are cut" and "do not change the way of cutting" read as opposites. "The whole one" has no clear referent.
- Replace brief: "...Fix it by changing only the size of each card and the words shared with the next card. Leave the question, the cutting style and the search style alone."
- Replace explanation: "...Words shared between neighbouring cards can keep the phrase together in one card, but a tiny card holds so few words that it may still rank too low to be kept."

**C17. Challenge 2: "search settings" does not match what is unlocked.**
- Quote: "Fix it using only the search settings."
- Location: `challenges[1].brief`
- Problem: "How to search" is locked in this challenge, and the control that fixes it is "How many cards to keep". "Room on the page" is not a search setting.
- Replace: "Fix it by changing only how many cards the search keeps."

**C18. Challenge 3: "reciprocal rank fusion" appears with no explanation.**
- Quote: "Blending the two rankings (reciprocal rank fusion)"
- Location: `challenges[2].explanation`
- Problem: a new technical name first appears in the last line of a challenge, and is not tied to the "Both together" control.
- Replace: "Blending the two rankings (the 'Both together' option) gives extra credit to a card for placing well in either list, so a card that one ranking missed can still make the cut when the other ranks it highly."

**C19. Long sentences needing a second read.**
- `connections[1].explain`: "Each piece gets its own fingerprint (made alongside the others, since how rare a word is depends on all the pieces), because the search will later hand back whole pieces, not whole documents." Replace: "Each piece gets its own fingerprint, because the search will later hand back whole pieces, not whole documents. (All the fingerprints are made together, because how rare a word is depends on all the pieces.)"
- `big_picture.story` last two sentences: "Getting the documents ready happens once, ahead of time, in a real system (the first four stages, which this demo repeats on every run). Answering happens every time someone asks (the last four)." Replace: "This lesson has two halves. The first four stages get the documents ready. In a real system that is done once, ahead of time (this demo repeats it on every run). The last four stages answer a question, and run every time someone asks."

**C20. Prompt builder analogy contradicts the order.**
- Quote: "Laying the relevant pages out on the desk, then pinning the question on top."
- Location: `components[6].explain.analogy`
- Problem: the same stage says "The chunks go first... the question come after", and the tour says "the question last". "On top" suggests first.
- Replace: "Laying the relevant pages out on the desk, then adding your question underneath them."

**C21. The same thing has several names (item 4 of the brief).**

| Idea | Names used |
|---|---|
| The message sent to the model | page, sheet, message, prompt, "finished page", "The page for the writer" |
| The size limit | room, room on the page, limit, size limit, word limit, budget, context budget |
| A piece of a document | piece, chunk, card (+ "sentence-sized pieces") |
| The list of numbers | fingerprint, list of numbers, vector, embedding |
| Where fingerprints are kept | card box, box, index, flat index, library catalogue |
| The AI that answers | writer, generator, AI model, language model, model, "the simple helper" |
| Finding the pieces | search, retrieval, card finder, "found", "kept", "retrieved" |
| The step that makes fingerprints | fingerprint maker, embedder, "embedding" (also a noun for the result) |

Problem: the learner has to work out each time that two names mean the same thing. The terms boxes define chunk, vector, embedding, prompt and context budget, but the stage text keeps switching between the plain name and the technical name without ever saying "also called".
Fix: say each pairing once, in the stage where the thing is introduced ("...pieces, called chunks"), then pick one name per idea. Keep "page" for the prompt everywhere, including in `big_picture.analogy` ("sheet"). Keep "room on the page" for the limit and "found" versus "kept" for the search stage. Also settle on "AI model" in preference to "language model" in learner-facing text, apart from the Terms box.

---

### MISLEADING (12)

**M1. The fingerprint analogy says the opposite of what a fingerprint is.**
- Quote: "Writing a fingerprint on every index card, so cards about similar things get similar fingerprints."
- Location: `components[2].explain.analogy`
- Problem: a real fingerprint is a unique ID where no two are alike, and similarity means nothing. The caveat only appears later, in `big_picture.analogy.breaks`.
- Replace: "Giving every index card a pin on a map. Cards about similar things get pins close together. (We call it a fingerprint because it stands for that one card, but unlike a real fingerprint, nearby ones mean similar things.)"

**M2. The Writer is said to use "only what is on the page".**
- Quote: "Writes an answer using only what is on the page."
- Location: `components[7].short`; echoed in `big_picture.analogy.mapping[7]` ("the writer who answers using only that sheet")
- Problem: that is an instruction we give it, not a guarantee. A real AI model can add things it learned in training, and the lesson says so in `connections[6]` and the analogy's `breaks`. The original said only "Writes an answer from the assembled prompt".
- Replace: "Writes an answer from the page. (It is told to use only the page, but a real AI model can still add things from its training.)"

**M3. "The two returns chunks are what we want."**
- Quote: "The two returns chunks are what we want."
- Location: `components[5].explain.thread`
- Problem: returns#1 is only "Custom-built bikes cannot be returned." It has nothing about how long you have, which is the question. Only returns#0 answers it. The sentence also hides the point that two of the three kept pieces are not helpful.
- Replace: "returns#0 is the piece we want, because it holds the 30-day rule. returns#1 is from the same article but only says custom bikes cannot be returned. The battery piece sneaks in because the simple fingerprint maker is only matching words, here the word 'long'."

**M4. "Using the same maker" contradicts the stage's own detail.**
- Quote: "The question needs the same treatment as the chunks, using the same maker, so the two can be compared."
- Location: `components[4].explain.story`
- Problem: `detail` and `happens` say some systems use a separate maker for questions. What is needed is that the two fingerprints match in kind, not that it is literally the same program.
- Replace: "The question needs a fingerprint of the same kind as the pieces, so the two can be compared. In this lesson one maker does both jobs."

**M5. "Every run here is the real thing."**
- Quote: "Every run here is the real thing."
- Location: `experiment.guide.intro`
- Problem: the writer is a stand-in that only quotes sentences, and the default fingerprint maker is deliberately simple. The same paragraph then says ranking is "not yet" by meaning. It overstates, and sounds like marketing.
- Replace: "Every run here really cuts, files, searches and builds the page. The one stand-in is the writer, a simple helper that quotes sentences."

**M6. Lexical notice promises what the AI model would do.**
- Quote: "so 'refund' and 'money back' do not land near each other. A small AI model would put them close together."
- Location: `ui.lexical_notice`
- Problem: "would" is a promise the experiment does not make. With that model, returns#0 is first by 0.643 against 0.641, so "close" is a tiny edge. "Land near each other" is unexplained. The `{dim}` placeholder is fine in code.
- Replace: "...so 'refund' and 'money back', which share no words, are treated as unrelated. A small AI model is built to give them similar numbers, though it does not always work."

**M7. A real model "would read returns#0 and answer."**
- Quote: "A real AI model would read returns#0 and answer."
- Location: `experiment.guide.presets["Same idea, different words"].notice`
- Problem: not tested here (it needs a paid call) and too certain. The text elsewhere warns that models get things wrong.
- Replace: "A real AI model reading returns#0 could likely answer, because that piece does talk about refunds."

**M8. The summary says RAG hands over "your documents".**
- Quote: "RAG ... gives it your documents to read before it answers."
- Location: `summary`
- Problem: RAG hands over only a few pieces of them, and the whole lesson is about why. A beginner will picture the entire document pile going in.
- Replace: "RAG finds the few pieces of your documents that match the question and gives just those to the model to read before it answers."

**M9. "Once, ahead of time" and "only shared words" stated flat.**
- Quote: "Every piece is turned into numbers once, ahead of time." and "so only shared words bring pieces together."
- Location: `components[2].detail`
- Problem: `happens` says this demo recomputes on every run, and the Same-idea preset shows unrelated words colliding.
- Replace: "In a real system every piece is turned into numbers once, ahead of time (this demo does it on every run). The built-in maker here only counts words, so almost always only shared words bring pieces together."

**M10. "Cannot be compared" is stronger than the source.**
- Quote: "fingerprints from different makers cannot be compared."
- Location: `components[2].explain.misconfigured`
- Problem: the source says "generally cannot". "Must" is also stronger than "should".
- Replace: "Questions and pieces should be given fingerprints in the same way, because fingerprints from different makers usually cannot be compared."

**M11. "Every later stage works on these documents and nothing else."**
- Quote: as above
- Location: `components[0].explain.story`
- Problem: a real AI model at the end also draws on its training (`connections[6]` says so). Fine for the demo helper, not for the real case.
- Replace: "Every later stage works on these documents and nothing else, apart from whatever a real AI model already learned in training."

**M12. "Get a ranking that goes by meaning" without "if installed".**
- Quote: "Switch to the small AI model on this computer to get a ranking that goes by meaning."
- Location: `components[5].explain.story`
- Problem: the control can say "(not installed)", and the preset notice does say "if it is installed". It also reads as a guarantee: even installed, the Same-idea result is only 0.643 versus 0.641.
- Replace: "If the small AI model on this computer is installed, you can switch to it to rank more by meaning than by shared words."

---

### WRONG (0)

None found. Checked and correct: all chunk counts and names, the "66 of 200 words", the 25-word battery#1, the two quoted answer sentences, `breaks_if_removed` for every stage against `ablation.py`, "Keeping 1 finds only returns#0", the 4th versus 11th rank for the default question, and the first four lines of each preset notice. The one number that sits close to a problem is "every score is about zero" (see C12).

---

## Tone: marketing or talking down (item 5)

Mostly fine. Small points:
- `summary`: "Take the whole machine apart piece by piece, run it for real, break it on purpose, and rebuild it." reads like an advert, and "run it for real" overreaches (see M5). Suggest: "You will take it apart one stage at a time, run it, break it on purpose, and put it back together."
- `big_picture.analogy.breaks`: "for a silly reason" is slightly flippant (see C15).
- `components[5].explain.thread`: "sneaks in" is playful but fine.

## What a beginner would have understood well (keep these)

- The index-card help-desk analogy (`big_picture.analogy`) and its stage-by-stage mapping. It carries the whole lesson.
- The open-book exam for stage 1, the librarian handing you three cards, and the highlighter for the writer.
- The "language model" and "RAG" terms in stage 1 are plain and short.
- Short, confident openings such as "Cuts each document into smaller pieces called chunks".
- Repeated honest labelling: "made-up", "not an AI model", "deliberately crude", "does not make them impossible". This builds trust.
- "A chunk found but left out" as a story (preset 3, `ideas[2]`, the budget challenge) is vivid and exact.
- The `check` questions are well pitched. The answers are one idea each.
- Each stage's `breaks_if_removed` and `connections` text tells you why the step exists.
- The two-halves split in `big_picture.story` and the "question joins at stage 5" note.
- The map-squash visual description ("Real numbers, squashed picture") and the tab text that says the answer helper does not read the page.
