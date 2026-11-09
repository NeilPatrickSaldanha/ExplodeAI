# Beginner review: Tokenization (plain-words voice)

Reviewed: `_source/tokenization.json`, checked against `content/lessons/tokenization/{lesson,explain,teaching}.yaml` and the code in `backend/app/experiments/tokenize/` (`bpe.py`, `pipeline.py`). I also ran the experiment code to check every number quoted in the experiment guide.

## Summary

The lesson reads well for a newcomer. It starts from a clear problem (computers need numbers), follows one sentence through every stage, and says plainly what the toy tokenizer is not. Every number in the guide checks out against the real code: 35/15/8/8 pieces, catalogue 257/282/357/473, 216 steps learned at 300, 18 pieces for the unseen-words preset, 4 unknown pieces with practice letters only, 17 pieces with bytes, 84 boundary-crossing pieces, 28 pieces and 6 unknowns for the digits preset, 8 numbers 262...46, and the six steps that build " keeper". No plain sentence is wildly wrong. The real problems are:

1. The word "piece" is used for three different things, so the "8 pieces" at the word splitter and the "8 pieces" at the end look like the same 8.
2. Several words are used before they are explained or never explained: byte, model, sequence, special piece, GPT-2, hex numbers, "sort first", PARTIAL, in-sample.
3. The stage stories use the technical names (encoder, decoder, learner) while the labels and the rest of the text use the plain names, so the same thing has up to four names.
4. A handful of sentences say something stronger than the verified source (round trip "proves", "A computer cannot read letters", "cannot be decoded", unseen words "chopped into many small pieces").

Counts: WRONG 2, MISLEADING 8, CONFUSING 16.

Order of findings below: WRONG, then MISLEADING, then CONFUSING (within each, learner order).

---

## WRONG

**W1. "A computer cannot read letters" (changes the subject of the source claim)**
- Quote: "A computer reads numbers, not letters." (`summary`) and "A computer cannot read letters. It reads numbers." (`big_picture.story`)
- Source says: "A language model can't read letters" (teaching.yaml big_picture.story).
- Problem: A beginner is reading letters on a computer right now. The statement is false as written; it is only true for an AI language model, which is the thing the lesson is about. It also makes a beginner doubt the lesson on the first line.
- Replace: "An AI language model cannot read letters. Inside, it only works with numbers. A tokenizer is the translator between the two." Summary: "An AI model works with numbers, not letters."

**W2. Unknown letters "can no longer be decoded"**
- Quote: "With only practice letters, 4 pieces come out as unknown: ... and the text can no longer be decoded." (`experiment.guide.presets["Accents and emoji"].notice`)
- Source says: "decoding no longer gives the text back" (teaching.yaml). I ran it: decoding still runs and returns `�af� cr�me at the lantern �`.
- Problem: Decoding works; it just returns the wrong text, with gaps. "Cannot be decoded" suggests an error message.
- Replace: "With only practice letters, 4 pieces come out as unknown ... and turning the numbers back into text gives you gaps instead of the original letters."

---

## MISLEADING

**M1. Round trip "proves"**
- Quote: "It proves the tokenizer lost nothing: if the text that comes out matches the text that went in, nothing was damaged on the way." (`components[7].explain.why`)
- Source (explain.yaml): "It shows whether anything was lost." One sentence matching only shows nothing was lost for that sentence. (The story is more careful: "A passing round trip shows..." and adds the good caveat.)
- Replace: "It checks whether anything was lost: if the text that comes out matches the text that went in, nothing was lost for that sentence."

**M2. Unseen words always "chopped into many small pieces"**
- Quotes: "Words that never appear in it get chopped into many small pieces." (`components[0].explain.misconfigured`); "A word that never appeared in the practice text still works, but it is spelled out in many small pieces, which is less efficient." (`components[4].explain.misconfigured`)
- Source: "a corpus that looks nothing like your text produces merges that suit the wrong words, so your text is split into many small tokens."
- Problem: The lesson's own preset contradicts this. "lanternkeepers" comes out as " lantern" plus "ke", "ep", "er", "s". A new word is made of familiar bits, so it is chopped less than the plain text says.
- Replace (corpus): "If your sentence looks nothing like the practice text, it is cut into many small pieces, because the big pieces were learned for other words." Replace (input): "A word that never appeared in the practice text still works. It is spelled out from smaller pieces, usually more of them, which is less efficient."

**M3. Counts "do not carry over between different AI models"**
- Quote: "They depend on the tokenizer, so they do not carry over between different AI models." (`objectives[3]`)
- Source: "Different models can use different tokenizers ... counts from one model should not be reused for another." Two models can share a tokenizer.
- Replace: "They depend on the tokenizer, and different AI models can use different tokenizers, so do not reuse a count from one model for another."

**M4. Speed claim not in the source**
- Quote: "Common groups of letters become single pieces, so common words need fewer pieces and the model reads text more quickly." (`components[3].explain.why`)
- Source: "so common words take fewer tokens." Reading faster is not a verified claim.
- Replace: "Common groups of letters become single pieces, so common words need fewer pieces."

**M5. "Giving more weight to pairs in common words"**
- Quotes: `components[3].detail` ("giving more weight to pairs in common words"), `components[3].explain.happens[0]`.
- Source: pair counts are weighted by how often each word occurs, which is the same as counting every occurrence in the text.
- Problem: "More weight" sounds like a bonus given to common words. It is simply that a pair in a word that appears 50 times is counted 50 times.
- Replace: "Count every pair of neighbouring symbols, once for each time it appears in the text. A pair inside a word that appears often is counted many times."

**M6. Any other order makes words "fall apart"**
- Quote: "If the gluing is done in a different order from the one that was learned, words fall apart into fragments." (`components[6].explain.misconfigured`)
- Source: "Applying merges in a different order than they were learned gives different tokens." Only the backwards order was tested; other orders give different pieces, not necessarily fragments.
- Replace: "If the gluing is done in a different order from the one that was learned, you get different pieces. Done backwards, words fall apart into fragments."

**M7. Claims about GPT, Claude and Gemini tokenizers**
- Quote: "...tokenizers inside big AI models such as GPT, Claude or Gemini, which learned far bigger catalogues from far more text." (`ui.tokenizer_notice`)
- Problem: The verified claims only cover GPT-2 (50,257 pieces) and two OpenAI encodings. Nothing verified says what size Claude's or Gemini's catalogue is or how much text it learned from. The same wording is in the frontend fallback, so this predates the plain text, but the plain text repeats it. The core message (this tiny tokenizer's counts say nothing about theirs) is right.
- Replace: "Its piece counts say nothing about the tokenizers inside big AI models. Each model has its own, and real ones learn from far more text. GPT-2's catalogue, for example, has 50,257 pieces."

**M8. "Token" defined as only a word or part of a word**
- Quote: "One piece of text that a model reads. It can be a whole word or just part of a word." (`components[0].explain.terms[1]`)
- Source (tokens-not-words): a token can be shorter than one character or longer than one word. In this very lesson pieces include "." and a lone space.
- Replace: "One piece of text that an AI model reads. It can be a whole word, part of a word, a space or a punctuation mark."

---

## CONFUSING

**C1. "Piece" means three things; two different "8"s**
- Quotes: "Our sentence is cut into 8 pieces: The, \" keeper\", ..." (`components[1].explain.thread`) versus "The whole sentence shrinks from 35 symbols to 8 pieces" (`components[6].explain.thread`). Also "Pieces spelled in symbols", "word pieces", "Pieces" (tab label), "Token: One piece of text".
- Problem: Piece = a chunk made by the word splitter, also = a final token, also = a bit of a glued word. The counts are both 8 only by coincidence (at 100 gluing steps every word is one piece). A beginner will think the word splitter already made the final pieces.
- Replace (word splitter thread): "Our sentence is cut into 8 word chunks: The, \" keeper\", \" lit\", \" the\", \" lantern\", \" at\", \" dusk\" and \".\". Later, when we glue, these chunks happen to stay whole, so the final count is also 8. That is a coincidence of this sentence." Then call the splitter's output "word chunks" everywhere and keep "pieces" for the final tokens.

**C2. Gluing and "pairs" mentioned before they are explained**
- Quotes: "The tokenizer glues together the pairs it sees most often." (`components[0].explain.check.answer`); "The counts decide which pairs get glued together first." (`components[0].explain.happens[2]`); `\" the\" with a space in front is a different piece` (`components[0].explain.example.steps`).
- Problem: This is stage 1. Pairs of what? Glued how? The leading-space rule is only explained in stage 2.
- Replace: "The tokenizer later joins together the letters that often sit side by side. So words that are common in its practice text end up as single pieces, and rare words are split up." Example step: "\" the\" with a space in front and \"the\" with none count as different (you will see why in the next stage)."

**C3. "Byte" appears before it is explained; awkward definition; "the byte choice"**
- Quotes: "With bytes, there are always 256 starting symbols" (`components[2].detail`); "Here those are the 256 possible bytes" (`components[2].explain.story`); "Why can the byte choice spell any text, when an alphabet of only the characters seen in practice cannot?" (`.check.question`); "With the byte choice ... With the practice-letters choice" (`.happens`); "A byte is one of the 256 values a computer can use to store a symbol." (`.what`) and term "Letters, emoji and punctuation are all stored as one or more bytes."
- Problems: (a) the definition comes after the story, thread and check; (b) "one of the 256 values ... to store a symbol" and "a symbol is one or more bytes" seem to contradict; (c) "the byte choice" refers to a setting the learner has not met.
- Replace definition: "A byte is the computer's smallest storage unit for a symbol. It holds a number from 0 to 255, so there are 256 possible bytes. A plain letter takes one byte; an accented letter or an emoji takes two to four." Put it first in the story. Replace "the byte choice" with "starting from all 256 bytes" and "the practice-letters choice" with "starting from only the letters seen in the practice text".

**C4. "Model" / "language model" never explained**
- Quotes: "Knowing that a language model reads text as a sequence of numbers, not letters." (`prerequisites[0]`); "the model reads text more quickly" (`components[3].explain.why`); "That number is what the model really receives." (`components[4].explain.story`); "and in a real system the language model itself" (`components[6].explain.goes_to`).
- Problem: The lesson never says what "the model" is, and the one prerequisite is exactly the thing the summary teaches.
- Replace in summary or first stage story: "The AI model is the program that reads these numbers and writes the reply, like the engine behind a chatbot." Drop the prerequisite or restate it: "You do not need to know anything about AI. You only need to know that a computer stores text as numbers."

**C5. "Sequence" never defined**
- Quotes: "see how a bigger catalogue of pieces means shorter sequences" (`summary`); "Too few gluing steps leave long sequences of tiny pieces." (`components[3].explain.misconfigured`); "A bigger catalogue means shorter sequences" (`tour[4].body`); "shorter sequences" (`challenges[1].explanation`).
- Replace: "means a shorter list of pieces for the same sentence".

**C6. "Special pieces" and "end-of-text marker" are never explained**
- Quotes: "a few special pieces" (`components[4].short`); "Here there is one special end-of-text marker, as in GPT-2." (`.detail`); "Special pieces, such as an end-of-text marker, are added." (`.explain.happens[1]`).
- Replace: "A few extra entries with a job instead of a meaning. This lesson adds one: a marker that means 'this text ends here'. The marker is added to the catalogue but is never used in the experiment."

**C7. "GPT-2" is not introduced**
- Quotes: "as in GPT-2" (`components[4].detail`); "Real tokenizers, such as GPT-2's with 50,257 pieces" (`big_picture.analogy.breaks`); "GPT-2's version also keeps punctuation apart from words." (`challenges[3].explanation`).
- Replace on first use: "GPT-2, an early, well-known AI language model from OpenAI".

**C8. Hexadecimal numbers with no hint**
- Quote: "Look up its bytes: 20 74 68 65" (`components[7].explain.example.steps`).
- Problem: A beginner sees four numbers that are not 32, 116, 104, 101 and has no idea why.
- Replace: "Look up its four bytes. Computers often write these in a counting style that uses letters as well as digits, which is why you see 20 74 68 65. Here 20 is a space, 74 is t, 68 is h and 65 is e."

**C9. "In the code"**
- Quote: "Spell each piece in starting symbols (in the code, those symbols are already numbers)." (`components[6].explain.happens[1]`)
- Problem: A beginner has not seen any code, and this is the very step they need to understand (where the numbers come from).
- Replace: "Spell each piece in starting symbols. Each starting symbol already has a number, so the list of symbols is already a list of numbers."

**C10. "Whose bytes sort first"**
- Quote: "If two pairs tie, the one whose bytes sort first wins, so the result is always the same." (`components[3].detail`)
- Replace: "If two pairs are equally common, a fixed rule picks one (the one that comes first in the computer's own ordering of symbols), so the same practice text always gives the same result."

**C11. "PARTIAL", "in-sample", "bytes per piece" in the experiment**
- Quotes: "é, è and ☕ show up as PARTIAL pieces, because each is spelled with 2 or 3 bytes." (`experiment.guide.presets["Accents and emoji"].notice`); label "Practice-text bytes per piece (in-sample)" (`experiment.labels`).
- Problem: PARTIAL is in capitals without saying it is a tag on screen or what it means; "in-sample" means "measured on the same text it learned from", never explained.
- Replace: "é, è and ☕ are marked PARTIAL, which means the piece holds only part of the symbol: each is stored in 2 or 3 bytes and the tokenizer has no single piece for them." Label: "Practice-text bytes per piece (measured on the same text it learned from)".

**C12. Tour and decoder detail mention broken characters with no set-up**
- Quotes: "A single piece can hold part of a character, so reading only some of the pieces can produce broken text." (`components[7].detail`); "Reading only some of the pieces can break a character in half." (`tour[7].body`)
- Problem: The reader has not been told an accented letter or emoji takes several bytes in a way that can be split across pieces.
- Replace: "An emoji takes several bytes, and the pieces may split those bytes between them. If you read only some of the pieces, you can end up with half an emoji, which shows as a broken symbol."

**C13. Same thing, several names (the biggest consistency problem)**
- Quotes and where:
  - Practice text / corpus / "pile of example text": `components[0].explain.story` says "That pile is called the corpus", then never again.
  - Number translator / encoder / "translating": stage label and connections say "number translator", but `components[6].explain.story` begins "The encoder turns your sentence into numbers" and the decoder story begins "The decoder does the reverse", while the labels are "Number translator" and "Back-translator". The stories never tie the two names together (the stage terms do, but after the story).
  - Pair gluer / "the learner" / merge learner: connections and `components[1].explain.why` say "the learner could glue..." and "The learner counts which neighbouring symbols appear together most" (`connections[2]`). In a lesson where the reader is also "the learner", this is easy to misread.
  - Gluing step / merge / recipe: `components[3].explain.story` ("Each round is called a merge ... 100 gluing recipes"), `.thread` ("The first recipes are small"), guide ("gluing steps", tab "Gluing steps", control "Gluing steps done" but tab text says the "Merges applied" slider, `experiment.guide.tabs.replay`).
  - Catalogue / vocabulary; starting symbols / alphabet / "basic symbols" / bytes; piece / token / symbol / brick.
- Fix: choose one plain name per thing and use it in the story text, with the technical name shown once beside it: "the number translator (called the encoder)". Rename "the learner" to "the pair gluer". Make the replay-tab text say "the Gluing steps done slider".

**C14. Long or hard-to-read sentences**
- `experiment.guide.presets["Familiar sentence"].notice`: five sentences with nine numbers. Split into two lines: first the piece counts (35, 15, 8, 8), then the catalogue sizes (257, 282, 357, 473) and the "ran out" explanation.
- `experiment.guide.presets["Unseen words"].notice`: one sentence lists "ke", "ep", "er", "s" finish ..., "w", "or", "k" finish ..., "rewound" breaks into 7 pieces (a space, r, e, w, o, un, d). Use a short list: lanternkeepers = " lantern" + "ke" + "ep" + "er" + "s"; clockwork = " clock" + "w" + "or" + "k"; rewound = a space, r, e, w, o, un, d (7 pieces).
- `components[2].explain.what`: two sentences with a definition inside. Move the byte definition to the story (see C3).
- `components[3].explain.story`: seven sentences introducing merge, BPE, 100 merges, and recipes. Split the BPE naming into the terms list only.
- `components[6].short`: "Cuts the text into word pieces, spells them in symbols, then glues them again in the order they were learned." Fine for a second read but it is the first thing the learner sees on this stage.

**C15. The brick analogy skips the numbers**
- Quotes: `big_picture.analogy.mapping` (all rows); `components[6].explain.analogy` "Rebuilding a sentence from bricks by repeating the gluing in the order you learned it."
- Problem: The point of a tokenizer is the numbers. The analogy gives each brick an "item number" in the catalogue row but the number translator row only talks about building the sentence, so the step "list of brick item numbers comes out" is not shown. Also, gluing LEGO bricks is permanent, so "undoing" is awkward in the back-translator row.
- Replace (number translator row): "building the sentence out of bricks the same way, then writing down the item number of each brick you used. That list of numbers is what comes out."

**C16. A few tone slips**
- "(256 + 100 + 1; simple arithmetic)" (`components[4].explain.example.output`): "simple arithmetic" talks down; drop it ("256 + 100 + 1").
- "This is the whole point of a tokenizer" (`components[6].explain.why`): slightly salesy; say "This is what a tokenizer is for".
- `ui.scene_title` "Exploded view of a machine that chops text into numbered pieces" and the lesson title "Tokenization, exploded": "exploded view" is a designers' term for a diagram with the parts pulled apart. Add: "(a diagram with the parts pulled apart so you can see each one)".

---

## What a beginner would understand well (keep)

- The summary's three-step outline: numbers not letters, cut into pieces, give each piece a number.
- The practice-text analogy and the lighthouse diary thread: concrete and memorable.
- The leading-space rule with the quoted examples "keeper" and " keeper" (stage 2 story). This is a hard idea, explained simply.
- The running example sentence, which is followed from stage to stage ("35 symbols to 8 pieces", " keeper" "7 symbols to 1 piece"). It gives the learner a way to check themselves.
- The merge learner example (h and e become "he", then " t", then " the"): small and checkable.
- "Why must the gluing be repeated in the same order" check and its answer: the "later steps use pieces earlier steps made" idea is clear.
- The honest caveats: the round-trip story saying the 35-piece version "makes the round trip too", the "ran out of pairs" explanation, the analogy "breaks" note, and the tokenizer notice.
- The presets' "Try / Notice" pairs with a concrete before and after. The Unseen words preset is the best demonstration of why pieces matter.
- The `breaks_if_removed` lines are all short and clear.
- Challenge briefs are written as stories ("The letters that vanished", "Gluing done backwards"), with hints that point at the idea not the answer.

## Accuracy notes (no action needed or low risk)

- The Vocabulary `misconfigured` text ("If the catalogue is lost or reordered, the same text would be turned into different numbers, and the model would read nonsense") replaces the source's trade-off statement with a different, plausible statement that is not one of the verified claims. It is true in general. Consider also saying "A bigger catalogue gives shorter sequences, a smaller one gives longer ones" so the verified claim (`vocab-length-tradeoff`) is covered at this stage.
- `tour[4]` ("A bigger catalogue means shorter sequences") drops "until words are already single pieces". The guide covers it, so the tour is only too brief, not wrong.
- `challenges[3].explanation` ("a word splitter that cuts at spaces") is slightly loose: the cut goes before the space, which stays with the word that follows. Not harmful.
- All numbers and example outputs in `experiment.guide` and `ideas` were reproduced by running the real code (8/15/35 pieces; 18/37/23/16; 17 and 13 pieces with 4 unknowns; 84 boundary-crossing pieces including " the " and "d the "; 28 pieces with 6 unknowns for digits).
