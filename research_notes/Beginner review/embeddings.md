# Beginner review: Embeddings, exploded (plain-words voice)

Reviewed: `_source/embeddings.json`, read in learner order (stages, then big_picture, connections, experiment.guide, challenges, tour). Checked against `content/lessons/embeddings/lesson.yaml`, `explain.yaml`, `teaching.yaml`, `plain.yaml`, and the code in `backend/app/experiments/embed/` (`pipeline.py`, `model.py`, `corpus.py`) plus `rag/embedding.py`, `rag/projection.py`.

## Summary

The lesson is in good shape. The town-of-houses idea carries the first half well, the "same word, different numbers" and "no shared words" examples are strong, and the honest failure case ("Where it goes wrong") is a real strength. Counts: 1 WRONG, 7 MISLEADING, 14 CONFUSING.

Main problems:

1. **A skipped step around "size" and "direction".** The Size equaliser talks about a list's "overall size" and "which way it points" without ever saying why a list of numbers has a direction. Arrows then appear inside a town analogy.
2. **Two kinds of "numbers".** The Word chopper gives each piece a label number, and the Meaning reader gives each piece 384 meaning numbers. Both are just called "numbers".
3. **Absolute statements about meaning.** "Closer in meaning" and "will find sentences that mean something similar" are stated flatly. The lesson's own rails example disproves them.
4. **Several terms changed between source and display.** "Pieces" and "tokens", "list", "vector" and "numbers", "hint" and "instruction", and "squash" used for three different operations.
5. **A broken sentence in the source.** The Tokens tab text ends mid-sentence.
6. **Technical words in learner-facing places.** The experiment description and the Long text preset use jargon the lesson has not taught.

Accuracy is mostly faithful. One sentence is literally false, and a few are stronger than the verified claims or drop a caveat.

## What a beginner would understand well (keep these)

- library.explain.analogy and story: "houses that are already built", each with "an address". The 24 houses and the "one on the furniture street" thread are clear and friendly.
- big_picture.story: "A computer cannot read meaning. It can only work with numbers." This is a clean, honest starting point.
- your_text thread and check: "a place to put my books" shares no words with the bookshelf sentence. The test is concrete and shows why word matching fails.
- tokenizer thread: "a start marker, the six words, and an end marker" adds up to 8 and is easy to follow.
- encoder story: "bank" beside a river versus "bank" for money. The rows and columns table (8 rows, 384 columns) is also helpful.
- pooling.analogy "one summary line for a whole paragraph".
- similarity.check ("Is a score of 0.6 quite similar? Not on its own") and "The scores are not percentages". These stop the most common misreading.
- semantic_space.misconfigured and check: they say plainly that the picture loses detail and the list is the truth.
- Terms boxes (Model, Embedding, Token, Vector, Layer, Pooling, PCA, Cluster) are short and plain.
- Presets "Where it goes wrong" and "Long text" show failures honestly. The guide's "tie, not a match" for all-zero scores is excellent.
- guide.ideas[0]: "like trying to find a house using addresses from two different towns".
- Tone: no marketing language found. Nothing talks down. The lesson owns its limits ("a real miss for this small model", "a tendency, not a guarantee").

## Findings

Ordered by severity, then by where the learner meets them.

### WRONG

**W1. "share no words at all"**
- Quote: "The dog and the horse share no words at all, so the model matched them on meaning." Also "The first one shares the words \"puppy\" and \"fetch\" with your sentence."
- Location: experiment.guide.presets.Puppy.notice
- Problem: Your sentence "A puppy playing fetch in the park" does share small words ("a", "the", "in") with "A horse grazed quietly in the green field" and "The dog chased a ball across the yard". The teaching text only said "share nothing" about the dog and horse. The library sentence is "Our puppy fetches sticks...", so the shared word is "puppy", and "fetch" is a form of "fetches". The matching idea is right, but the literal sentence is false and stronger than the source.
- Replacement: "The first one shares the word \"puppy\" and a form of \"fetch\" with your sentence. The dog and the horse share no important words with it, only small ones like \"a\" and \"the\", so the model matched them on meaning."

### MISLEADING

**M1. Flat promise that meaning is found**
- Quotes:
  - "A higher score means closer in meaning." (similarity.explain.story)
  - "The machine will find which example sentences mean something similar." (your_text.explain.what)
  - "which example sentences are closest in meaning?" (your_text.explain.why)
  - "in a way that sentences with a similar meaning get nearby addresses" (big_picture.story)
  - "Sentences with a similar meaning get similar numbers." (top-level summary)
- Problem: These read as guarantees. The lesson's own rails example, where a truck, a horse and a plane beat the train, shows the model sometimes fails. The verified teaching text says "usually" and "often". The strong wording is stronger than the claims.
- Replacements:
  - "A higher score means the model thinks the two sentences are closer in meaning, though it can be wrong."
  - "The machine will list the example sentences whose numbers are nearest to yours, which are usually the ones that mean something similar."
  - "Sentences with a similar meaning usually get similar numbers."

**M2. The "distance" analogy points the wrong way**
- Quotes:
  - "Measuring the distance from the visitor to every house, then listing the houses from nearest to furthest." (similarity.explain.analogy; same idea in big_picture.analogy.mapping)
  - "Each comparison gives one score. A higher score means closer." (similarity.explain.happens)
- Problem: A distance gets smaller as things get closer, but the score gets bigger. A beginner will stumble when a higher number means nearer. Also, the Straight-line distance option is stored as a negative number (the code negates it so that higher is still closer), and no plain text says so. A learner who switches to it will see minus signs.
- Replacement: "Giving every house a closeness score for the visitor, where a bigger score means a nearer house, then listing the houses from highest score to lowest. (If you pick the straight-line distance option, the scores show as negative numbers so that the nearest house still has the highest one.)"

**M3. Mismatched summarising "usually gives slightly worse results"**
- Quote: "Using a different way of summarising than the one the model was trained with usually gives slightly worse results."
- Location: pooling.explain.misconfigured
- Problem: The verified claim only says the way of summarising should match training. Sentence-BERT found that the choice hardly mattered in one setup and mattered a lot in another. The only measurement in this lesson is one sentence going from 0.695 to 0.645. "Usually" and "slightly" are both stronger than the evidence.
- Replacement: "The summary should be made the way the model was trained to make it. A different way can give worse results, sometimes only a little, sometimes a lot, so it is worth testing."

**M4. The hint's caveat is dropped**
- Quote: "A very short question, with no hint, may land next to the wrong sentences. The model's makers suggest a hint for short questions."
- Location: your_text.explain.misconfigured
- Problem: The original adds that for this version of the model, leaving the hint out costs only slightly, so test both. The plain version makes the hint sound more important than the evidence says. The Commute preset (0.515 versus 0.502) shows how thin the effect is.
- Replacement: "The model's makers suggest a hint for short questions. Leaving it out can send a very short question to slightly worse matches, but for this model the difference is small, so try it both ways."

**M5. Switching off "Make every list size 1": only the range is mentioned**
- Quotes:
  - "some scoring methods give numbers outside the usual range" (normalizer.breaks_if_removed)
  - "The scores are no longer kept between -1 and 1, because the lists keep their original sizes." (guide.ideas[2].see)
- Problem: Only the range of the scores is mentioned. Without this step, Multiply and add favours long lists, so the order of the nearest sentences can change as well, and the sentences then agree less with Direction match. The learner is told elsewhere that the methods "agree", so they may assume only the numbers move. (The code confirms Direction match normalises internally, so it is unaffected.)
- Replacement: "The scores can go outside -1 to 1, and for 'Multiply and add' and 'Straight-line distance' the order of the sentences can change too, because lists with bigger numbers get an unfair advantage. 'Direction match' is not affected."

**M6. "Rounds of thinking"**
- Quotes: "which are twelve rounds of thinking about how the pieces relate" (encoder.explain.happens); "Layer: One round of thinking inside the model." (terms); "Twelve rounds of thinking give each piece 384 numbers" (tour).
- Problem: The model does not think. Each layer is one step of arithmetic that mixes information between the pieces. The word invites a person-in-a-box picture, which is the main wrong idea beginners have about AI.
- Replacement: "The model passes the pieces through twelve layers. A layer is one step of calculation that lets each piece's numbers be adjusted using the other pieces around it."

**M7. The map analogy says flat and two-directional, but the picture is 3D**
- Quotes:
  - "The paper map of the neighbourhood, a flat drawing of the real town." (semantic_space.explain.analogy)
  - "A paper map has two directions. This one has 384, so the 3D picture has to squash them down and loses detail." (big_picture.analogy.breaks)
- Problem: The lesson shows a 3D picture, not a flat one. "Directions" is never defined. The paper map is called a flat drawing of the real town, but the real town (addresses of 384 numbers) is not like a town at all. This blurs which thing is the "real" map and which is the picture.
- Replacement: "A town address needs only two numbers, like a street and a house number. Our addresses need 384, which cannot be drawn. So the 3D picture squeezes them down to three numbers per sentence, like a flat photo of a round planet, and loses some detail. The list of nearest sentences uses all 384 numbers."

### CONFUSING

**C1. Two different kinds of "numbers"**
- Quotes: "gives each piece a number" (tokenizer.explain.what); "Each piece is swapped for its number from a fixed list." (tokenizer.explain.happens); "turned into numbers" (used throughout).
- Problem: The tokenizer's numbers are just ID labels, like page numbers, and carry no meaning. The Meaning reader's 384 numbers do carry meaning. Both are called "numbers". The distinction only appears at encoder.breaks_if_removed ("only the labels of the pieces").
- Replacement (add to tokenizer.explain.what): "Cuts the sentence into small pieces, called tokens, and gives each piece a label number from a fixed list, like a page number. The label only says which piece it is. It does not yet say anything about meaning."

**C2. The hint is never shown**
- Quotes: "you can add a hint sentence in front" (your_text.explain.happens); "adding a hint in front" (your_text.detail); "Hint for short questions" (control).
- Problem: The learner never sees what the hint says, or that it is added to your sentence only and not to the examples. They will wonder whether it is a clue they type themselves.
- Replacement: "The hint is a fixed line of words the model's makers wrote, 'Represent this sentence for searching relevant passages:'. When you turn it on, it is placed in front of your sentence automatically. It is not added to the example sentences."

**C3. "Size" and "direction" of a list of numbers: a step is skipped**
- Quotes: "Rescales the list so that its overall size is exactly 1, without changing what it points towards." (normalizer.explain.what); "only the direction the list points in matters" (normalizer.detail); "Redrawing every arrow to the same length" (analogy, and also in big_picture mapping).
- Problem: A list of numbers is not an arrow, and "size" is never defined. A true beginner has no way to connect "384 numbers" with "arrow", "length" or "points towards". The town analogy has no arrows, so a new picture arrives mid-story. "Size" and "length" are also used for the same thing.
- Replacement: "Think of the list of numbers as an arrow drawn from one starting point: the numbers tell you how far the arrow goes in each of many directions. The arrow's length is its 'size'. This step shrinks or stretches every arrow to the same length, 1, without changing where it points. Then, when two arrows are compared, the only thing that counts is whether they point the same way."

**C4. The normalizer refers to measures the learner has not met, and the names of the measures differ**
- Quotes:
  - "the different ways of measuring closeness, which you will meet in the next stage" (normalizer.explain.story)
  - The normalizer check question ("two ways of measuring closeness agree") and its answer ("called cosine similarity ... multiplying and adding")
  - "Cosine similarity" (terms), "Dot product", "Euclidean distance" (similarity terms)
  - Controls: "Direction match", "Multiply and add", "Straight-line distance"
  - "The closeness-by-direction method is not affected" (breaks_if_removed)
- Problem: The check question comes before the learner has seen any of the measures (the next stage defines only two). The same three things are called six different names: "cosine similarity" / "measuring by direction" / "closeness-by-direction method" / "Direction match", and so on. The similarity stage never says which is used by default.
- Replacement (for normalizer.explain.check.answer): "There are three common ways to score two lists: 'Direction match' (cosine similarity), which checks whether two arrows point the same way; 'Multiply and add' (dot product), which multiplies matching numbers and adds them up; and 'Straight-line distance' (Euclidean distance), which measures how far apart the arrow tips are. When every arrow has length 1, the first two give exactly the same answer and the third puts the sentences in the same order. This lesson starts with 'Direction match'." Then use the control names everywhere and show the technical name once beside them.

**C5. Pooling: how can one marker summarise the sentence, and "squash" is overloaded**
- Quotes: "It keeps the row for the start marker, which the model was trained to use as a summary of the sentence." (pooling.explain.happens); "Squashes the many lists, one per piece, into one list for the whole sentence." (what); "Squashed into one list" (library.explain.example.steps).
- Problem: The step that makes it work is skipped. The start marker was read together with every other piece, so its numbers already carry the whole sentence. Without that, "keep one row, throw away the rest" sounds like throwing information away. Also, "squash" is used for pooling (many lists into one), for the size equaliser's neighbours, and for PCA (384 numbers into 3). "Squash many lists into one" is also inaccurate when the start marker's row is simply picked.
- Replacement: "The start marker was read together with all the other pieces in the last step, so its list of numbers already blends information from the whole sentence. The model was trained to treat that one list as the summary, so this step keeps it and sets the other lists aside." Use "combine" or "pick" for pooling and keep "squash" only for the 384-to-3 picture.

**C6. "Word matching only" arrives without explanation**
- Quotes: "unless both settings for turning sentences into numbers are set to \"Word matching only\"" (guide.intro); "set both \"how to turn sentences into numbers\" settings to \"Word matching only\"" (presets.Bookshelf.try); "Word matching can only match words that appear in both sentences." (challenges[0].explanation).
- Problem: The learner has never been told that numbers can also come from counting words, or that this is a simple stand-in without meaning. The quoted control name ("how to turn sentences into numbers") is not the label on screen: the labels are "How the example sentences become numbers" and "How your sentence becomes numbers". Behind the label, the code uses hashed word counts that ignore small words and trim plurals ("fetches" would be treated roughly as "fetch"), which "Word matching only" hides.
- Replacement (add to guide.intro): "Each of the two settings picks how a sentence becomes numbers. 'Small AI model (bge-small)' is the real model. 'Word matching only' is a simple stand-in that turns a sentence into numbers by counting which words it uses, so it knows nothing about meaning." Also change the Bookshelf "try" to: "Set 'How the example sentences become numbers' and 'How your sentence becomes numbers' both to 'Word matching only'."

**C7. The same thing under several names**
- Quotes and locations (examples; all from the displayed text):
  - pieces / tokens: "pieces called tokens" (tokenizer.story); the tab is "Pieces", but the Long text preset says "Tokens tab"; the technical name sits small beside it.
  - list / vector / embedding / "addresses" / "the numbers" / "sets of numbers": for example "a list of 384 numbers", "Embedding", "the two sets of numbers" (guide.ideas[0]).
  - start marker / [CLS] marker: pooling.story switches between them mid-sentence.
  - example sentences / library: "the first sentences in the library" (guide.presets.Bookshelf.notice) while the stage is "Example sentences".
  - model: sometimes the whole machine ("This model uses the list from the start marker"), sometimes just the Meaning reader ("The meaning reader is the model itself" in encoder.story), and "same model" in library.check, so the Word chopper looks like a different thing.
  - hint / instruction: "hint" in the plain text; "BGE instruction" is the technical name.
  - nearest sentences / closest / neighbours / "nearest neighbours": semantic_space.thread says "Its three nearest neighbours".
  - size / length: the normalizer uses "size" but the technical text uses "length".
  - "squash" for pooling, PCA and the arrow step.
- Problem: A beginner cannot tell whether two names mean one thing or two.
- Replacement: Choose one plain name for each: "piece" (and show "token" once in brackets), "list of numbers" (with "vector" defined once), "start marker", "example sentences", "the model" (say "the whole model" or "the Meaning reader" when you mean one part), "hint", "nearest sentences", "size". Use "squash" only for the 384-to-3 picture. Use the on-screen label in every how-to line.

**C8. A sentence ends mid-way in the Pieces tab text**
- Quote: "Rare words are split into smaller parts that begin with"
- Location: experiment.guide.tabs.tokens. The plain.yaml text ends "...begin with ##.", so the "##" is lost somewhere before the JSON, probably by a stripping step or Markdown.
- Problem: The tab description ends in the middle of a sentence. Even with the "##" present, a beginner does not know what "##" means.
- Replacement: "Rare words are split into smaller parts, and every part after the first starts with two hash signs (##) so you can see that it continues the previous part." Also check that the display does not strip "##".

**C9. The Long text preset is full of untaught jargon**
- Quotes (inside experiment.presets[Long text].text): "Embedding models read a fixed number of tokens... counting the special CLS and SEP tokens", "embed the whole recipe as one vector", "retrieval systems split long documents into chunks", "Hosted embedding models", "If you are reading this inside the lesson, look at the Tokens tab now."
- Problem: It is the text the learner sees fed into the model and then reads. It uses many terms the lesson has not defined (embed, vector, chunk, retrieval, hosted), and it says "Tokens tab" while the tab is named "Pieces". The reference "Lesson 01 shows a chunker" is fine. The passage is also very long for a beginner.
- Replacement: Keep it as test data but make the preface in the note do the explaining, and rename: "Look at the Pieces tab" in the passage. In the note: "This passage is long on purpose. It is here to be cut off, so you do not need to understand it."

**C10. Technical details and "server" in learner-facing text**
- Quotes: "A small model called bge-small-en-v1.5 (a reduced-precision version made by Qdrant, run through a tool called fastembed) runs on this computer, stage by stage, on your sentence." (visuals[experiment].description); "The server runs your settings again and checks the result." and "controls that are left unlocked" (ui.challenges_intro).
- Problem: "Reduced-precision", "Qdrant", "fastembed" and "server" are unexplained. "Runs on this computer" and "your own computer" (guide.intro) sit beside "the server", which sounds like a different machine. The code says the model files are downloaded once and cached locally, so the wording is correct only for a local install. If the lesson is ever hosted, it will be wrong.
- Replacement: "A small, ready-made AI model (bge-small-en-v1.5, in a slightly shrunken version that is quicker to run) is used for real, step by step, on your sentence." And: "When you press the check button, the lesson runs your settings again and tells you whether the right sentences now come first. Controls that are not part of the puzzle are greyed out."

**C11. Meaning map: "spread", "25 lists", "neighbours", "ring"**
- Quotes: "The label says how much of the real spread the picture keeps." (semantic_space.explain.happens); "25 lists of 384 numbers" (example.input); "Its three nearest neighbours, by the real numbers, are all furniture." (thread).
- Problem: "Spread" is never defined. The learner has only seen 24 sentences, so "25" appears from nowhere (the 24 plus your sentence). "Neighbours" is used before it is explained.
- Replacement: "The label shows, as a percentage, how much of the differences between the sentences the picture manages to keep. The map has 25 points: the 24 example sentences plus yours, which is drawn as a ring. The 'neighbours' of your sentence are the example sentences nearest to it."

**C12. The rails preset note blurs two ideas**
- Quote: "Being close in meaning is not the same as being correct."
- Location: experiment.presets[Where it goes wrong].note
- Problem: The real point is that the model's numbers are not a perfect picture of meaning, so it missed the train sentence. "Close in meaning" versus "correct" is a different (and muddled) distinction.
- Replacement: "The model is only guessing at meaning from patterns it learned, so it can miss. Here it ranked the train sentence 14th out of 24."

**C13. Six images in one analogy**
- Quotes: big_picture.analogy.mapping runs through houses, word cards, a reader's notes, a summary line, redrawn arrows, a paper map.
- Problem: Only the first two or three are really about a town. The arrows and the paper map arrive from outside it, so the learner has to hold several pictures at once. The "visitor" and "houses" frame disappears at the Size equaliser.
- Replacement: Keep the town for the beginning and the end, and add a one-line bridge for the arrow step, for example: "Imagine each house address is an arrow from the town centre. The visitor only cares which way the arrow points, so everyone's arrow is first made the same length."

**C14. Long or heavy sentences that need a second read, and a number that is not general**
- Quotes:
  - experiment.guide.tabs.vector: "The first 48 of the 384 numbers in your sentence's list, before it was rescaled to size 1 (the line under it shows the size going from about 9.25 to 1.00). A bar's height shows how big a number is, and its fill shows whether it is positive or negative. Rescaling divides every number by that size, so the list keeps the same shape. The lists for each piece are on the Pieces tab." This is five sentences with a bracket in the middle. The "9.25" belongs to the bookshelf sentence only, and the Pieces tab shows only the first 24 numbers of each piece (code: `TOKEN_PREVIEW_DIMS = 24`).
  - guide.ideas[3].see: five sentences covering what pooling does, why the model prefers one option, a number, and a second experiment.
  - normalizer.explain.story: "After it, the different ways of measuring closeness, which you will meet in the next stage, all put the sentences in the same order."
  - guide.presets.Bookshelf.notice: five sentences including a rank-tie explanation.
- Problem: Each needs two readings, and the vector tab hides the fact that 9.25 changes with the sentence.
- Replacement for tabs.vector: "This shows the first 48 of the 384 numbers in your sentence's list. Each bar is one number: taller means bigger, and the fill shows whether it is positive or negative. Under the chart, the 'size' of the whole list is shown before and after it is rescaled to 1 (for the bookshelf sentence it goes from about 9.25 to 1.00; other sentences give other starting sizes). Rescaling keeps the shape of the bars. The Pieces tab shows the first 24 numbers for each piece."

## Notes on things checked and found fine

- Tokenizer thread (8 pieces) and encoder thread (8 by 384) agree with the code.
- The 512 limit, 12 layers, 384 numbers, 24 sentences, the 14th-of-24 rails result and the top-3 lists match the teaching text and the code (library order breaks ties, so the all-zero bookshelf result does list the animal sentences first).
- The mixed-models explanation is correct. The lexical stand-in has 1024 numbers and the model 384, so the "lists are not even the same length" hint is accurate. The plain text states "384" as a fixed fact elsewhere without saying that this is the model's size and the word-matching stand-in is different; this is minor.
- Marketing and talk-down: none found. The mildest cases are "Only the meaning can connect them" (big_picture.example.note) and the cheerful "squashed", both acceptable once the "usually" wording in M1 is fixed.
