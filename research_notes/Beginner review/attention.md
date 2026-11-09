# Beginner review: Lesson 04, Attention, exploded (plain words)

Reviewed against `_source/attention.json`, with `lesson.yaml`, `explain.yaml`, `teaching.yaml` and `backend/app/experiments/attend/{model,pipeline,ablation}.py` as the accuracy reference. I also re-ran the toy layer to check every number the plain text quotes (35%, 30% for "sat" to "on", 28% / 9% for "it", 94% / 42%, 63% / 37% with 8 groups, 15 of 36 hidden squares, 0 vs 0.45 order gap). All of them check out.

## Summary

The plain voice is good. The story arc (question, tag, message, match, share, blend) is clear, and nearly every figure is true to the code. No sentence is flatly false. The main problems are:

1. **The sentences that explain "no position" mention the no-peeking rule five stages before it is introduced.** This is the biggest confusion in the lesson.
2. **Names drift.** Head, group and "wide group"; position, place and seat number; weights as two different things; "grid" for two different grids.
3. **A few undefined words are used as if known:** layer, trained, square root, head size, padding mask, "the original paper".
4. **"Raise every score to a power" is a misleading description of softmax.** It also leaves out why a hidden score becomes exactly zero.
5. **Two small accuracy slips:** "the next stage" after the scores is the mask, not softmax; and a caveat is dropped ("subtracting the biggest score gives the same result").

Counts: WRONG 0, MISLEADING 10, CONFUSING 34 (44 findings).

## Job A / Job B findings

Order below follows the learner's path.

### Tokens stage

1. **CONFUSING.** Quote: "The machine works on a list of items, so the sentence is first cut into words." Location: `components[0].explain.story` and `.why`. Problem: "the machine" is a new, vague name for the thing doing the work. Later text says "the layer", "the model", "the toy". A beginner wonders if these are four different things. Replacement: "Attention needs a list of separate items to work on, so the sentence is first cut into words."

2. **CONFUSING.** Quote: "A real model cuts text into smaller pieces, as in Lesson 2, but this toy uses whole words". Location: `components[0].explain.story` and `.misconfigured`. Problem: "toy" and "model" are used before they are defined (the definition comes in the big picture and the experiment note). Also the "smaller pieces than words" claim is slightly stronger than the original: real tokenizers often keep common words whole and only split long or rare ones. Replacement: "A real system often cuts longer or rarer words into smaller pieces, as in Lesson 2. This lesson uses a deliberately simplified demo, called a toy here, that keeps every word whole so the grid stays easy to read."

3. **CONFUSING (naming).** Quote: "Words" (label), "up to 12 of them", and "words and punctuation marks". Location: `components[0].label` and `.detail`. Problem: the stage is called "Words", but commas and full stops also count as items. A sentence with a full stop will show one more "word" than the learner counted. Replacement (detail): "This toy splits your sentence into words and punctuation marks, and keeps the first 12. Each one is called a word here, even a full stop."

### Numbers and seat number stage

4. **CONFUSING (biggest issue).** Quote: "Without it, and with nothing hiding later words, each word gets exactly the same result whatever order the words arrive in". Location: `components[1].explain.story`. The same phrase appears in `.misconfigured`, `.check.answer` and `breaks_if_removed` ("with nothing hiding later words"). Problem: the no-peeking rule is introduced five stages later, and nothing here says why it matters for order. The sentence is also about 45 words long with a parenthetical in the middle. The accuracy is right (the original says "with no mask"), but a beginner cannot parse it. Replacement: "Without a place pattern, a word would get the same new list however the sentence is ordered, so 'dog bites man' and 'man bites dog' would look identical to it. (One later rule, which you will meet soon, can also reveal order. It is switched off here.)" For the check answer: "Attention only compares lists of numbers, so by itself it ignores order. Adding each word's place gives the layer something to tell orders apart."

5. **CONFUSING.** Quote: "so the sentence is treated as a bag of words." Location: `components[1].breaks_if_removed`. Problem: "bag of words" is jargon; the challenge text calls the same idea "a pile of words" (see item 33). Replacement: "so the sentence is treated like a pile of words with no order."

6. **MISLEADING (analogy).** Quote: "Writing each word on a card and stamping its seat number on it." Location: `components[1].explain.analogy`; also label "Numbers and seat number". Problem: a seat number is one separate label. In the toy, the "place" is a whole pattern of 64 numbers mixed into the word's own numbers, so the word changes, it does not just get a sticker. The beginner will think there is one number per word, which clashes with "64 numbers" and "the two 'the' words differ". Replacement: "Writing each word on a card, then blending a place-specific pattern into the numbers on that card, like adding a unique tint to each card depending on its seat."

7. **CONFUSING (naming).** Quote: "place number", "seat number", "place", "position pattern", "pattern for its place". Location: `components[0].explain.check`, `components[0].explain.goes_to`, `components[1].detail`, `components[1].explain.terms[1]`, experiment label "Seat numbers", presets note "Position vectors". Problem: five names for one thing. The preset note ("Turn Position vectors off") is the worst: the control the learner sees says "Seat numbers". Replacement: pick one, for example "place pattern", say once that "this is what the on-screen control calls 'Seat numbers'", and use it everywhere. The Order preset note should read: "Turn Seat numbers off and Hide the words that come later off."

8. **CONFUSING.** Quote: "a pattern for its place is added, and the result is scaled so the numbers keep a steady size." Location: `components[1].explain.happens[1]`. Problem: "scaled" and "steady size" are undefined, and the lesson later uses "sensible size" for a different step (the score division). A beginner may merge the two ideas. Replacement: "A place pattern is added, then everything is shrunk by a fixed amount so the numbers stay about the same size as before."

9. **CONFUSING.** Quote: "Each word becomes a list of numbers, called a vector (64 numbers here)." Location: `components[1].explain.story`. Problem: it never says why a word needs to be numbers at all (the connections say "before any maths can happen", but that comes later). It also does not say that these particular numbers are random in this toy and carry no meaning of the word; that appears only in the "fixed list of random numbers" bullet. Replacement: "A computer can only compare numbers, so each word becomes a list of numbers (called a vector; 64 numbers here). In this toy the numbers are random and do not capture the word's meaning."

### Question, tag and message stage

10. **CONFUSING.** Quote: "layer" (e.g. "so the layer knows where each word sits", "one real layer of attention"). Location: `components[1].explain.what`, `big_picture.story`, many others. Problem: "layer" is never defined. A beginner will think "layer" means something visual, such as a layer of the page. Replacement (first use): "…so this one round of attention (called a layer) knows where each word sits."

11. **CONFUSING.** Quote: "Each word's list is multiplied by three different tables of numbers." Location: `components[2].explain.happens[0]`, also `.story`, `.example` and `.detail`. Problem: a learner has no picture of "multiplying a list by a table". It is also not said that the same three tables are used for every word. Replacement: "Each word's list goes through three fixed recipes (each recipe is a table of numbers that turns one list into another list). The same three recipes are used for every word."

12. **CONFUSING.** Quote: "With 2 heads, each head reads all 64 numbers and makes its own 32-number query, key and value. A head is one separate set of questions, tags and messages." Location: `components[2].explain.story`. Problem: "head" is used before it is defined in the next sentence. It was also already introduced in `.detail` as "groups, called heads". Replacement: "A head is one separate set of questions, tags and messages. This lesson uses 2 heads. Each head reads all 64 numbers and makes its own, shorter 32-number question, tag and message."

13. **CONFUSING (naming).** Quote: "head", "group", "head size", "a 64-wide head", "wide group", "head width", "the width of the group". Location: `components[2].detail`, `components[3].explain.story`, `components[6].explain.misconfigured`, `challenges[1].brief`, `challenges[1].hint`, `challenges[1].explanation`, tour "Several groups (heads)", Softmax thread "both heads", guide "the two groups". Problem: the same thing is called a head in most stage text and a group in the controls and guide. "Size" and "width" are used for the same measure, how many numbers are in one question, and nowhere is it said that "head size" means 32 here. Replacement: pick one pair, for example: "group (the technical name is head)" and "group size (how many numbers are in each question, 32 here)". Use that pair in every stage, challenge, and note. If "head" is kept for stage text, the guide should say "group (head)" at least once.

14. **MISLEADING (analogy).** Quote: "the labels on the shelves are the keys, and the books are the values. You do not take one book. You get a blend of every book". Location: `components[2].explain.analogy`. Problem: nobody blends library books, so the analogy asks the learner to accept an odd picture. More important, it hides that every word plays all three roles at once (asker, shelf label and book). A beginner will picture two sets of things: askers and shelves. Replacement: "Imagine every word is both a reader and a shelf. As a reader it holds up a question. As a shelf it has a label (what it offers) and a book (what it hands over). Each reader takes a mixture of books, with more from the shelves whose label matched best."

15. **MISLEADING (analogy).** Quote: "each student's question, name tag, and what they would say if called on" and "everyone's name tag". Location: `big_picture.analogy.mapping[2]` and `[3]`, `connections[2]`. Problem: a name tag says who you are, but the key is what you offer, so the learner expects names to be matched. The text elsewhere says "tag (what it offers)". Replacement: "a label saying what that student can help with".

16. **CONFUSING.** Quote: "In a trained model they are learned." Location: `components[2].explain.misconfigured`. Problem: "trained" and "learned" are first used here without definition. The only explanation ("practising on huge amounts of text") is in the big-picture analogy. Replacement: "In a real model, these tables are adjusted during training, a long practice run on huge amounts of text, so that they end up asking useful questions. In this toy they stay random."

### Match grid stage

17. **CONFUSING.** Quote: "divided by the square root of the head size". Location: `components[3].explain.story`, `.happens[1]`, `.check.question`, `.check.answer`, tour. Problem: the learner has to know what a square root is (the plain text does not say) and what "head size" is (item 13). The "why" is only given in the check answer. Replacement: "Each score is divided by a fixed number that grows as each question gets longer (it is the square root of how many numbers are in each question; for 32 numbers, about 5.7). This keeps the scores from becoming huge."

18. **MISLEADING (slip, order of stages).** Quote: "Without the division, a wide head gives scores that are far apart, and the next stage then gives almost all the attention to one word." Location: `components[3].explain.misconfigured`. Same issue in `.check.answer` ("the next stage can pile almost everything onto one word"). Problem: the stage after the Match grid is the No-peeking rule, not the shares. It is Attention shares (softmax) that piles everything onto one word. The original says "the next step" for the same slip (explain.yaml), but the plain version is where beginners will read it, and the order matters. Replacement: "…and the step after the no-peeking rule, which turns scores into shares, then gives almost all the attention to one word."

19. **CONFUSING.** Quote: "The grid also grows with the square of the sentence length." Location: `components[3].explain.misconfigured` and `components[6].explain.misconfigured`. Problem: it is dropped into a "what goes wrong without the division" paragraph where it does not belong, and "the square of the sentence length" is not explained. Replacement: "The grid also gets big fast: a sentence twice as long needs four times as many squares."

20. **CONFUSING (naming).** Quote: "a grid of scores" (Match grid) and "Rows are words that ask, columns are the words they look at. The numbers in each row add up to about 100%." (tab "Who looks at whom"). Location: `components[3].explain.story`, `experiment.guide.tabs.grid`, `experiment.guide.presets.Cat`. Problem: two different grids are both called "the grid": one of raw scores, one of shares that add up to 100%. In the Match-grid stage the learner may open the "Who looks at whom" tab and expect scores, not percentages. Replacement: "match grid" (raw scores) vs "who-looks-at-whom grid" (shares), and say once that the second is the first after the no-peeking rule and the conversion to shares.

21. **CONFUSING.** Quote: "Every visible word gets the same share, so each result is just an average." Location: `components[3].breaks_if_removed`. Problem: "visible" appears before the learner knows words can be hidden. Also the heading is about removing the Match grid, but the sentence next to "divided by a number" can make the learner think the division is what is removed. Replacement: "Every word gets the same share, so each new list is just a plain average of all the messages."

### No-peeking rule stage

22. **CONFUSING.** Quote: "Scores for later words are set to the lowest possible number. The next stage turns those into exactly zero attention." Location: `components[4].explain.happens`, `.detail`, `components[4].explain.story`, `challenges[0].explanation`. Problem: there is no "lowest possible number"; the original is minus infinity. More importantly, the reason a very low score gives zero attention is never given, because the shares stage says "raise every score to a power" (item 24). The learner has to take it on trust. Replacement: "Scores for later words are replaced by minus infinity, a number lower than any real score. In the next stage, that makes their share exactly zero."

23. **CONFUSING.** Quote: "Padding masks are a different thing." and "Do not mix it up with a padding mask, which is a different thing." Location: `components[4].detail` and `.misconfigured`. Problem: the beginner has never heard of a padding mask and is told not to confuse the lesson with it. It is noise at this level, and the sentence tells them nothing. Replacement: delete both sentences, or say "Another kind of mask, which hides blank filler space, is not used in this lesson."

### Attention shares stage

24. **MISLEADING.** Quote: "Raise every score to a power, so they are all positive." and "Raise each to a power". Location: `components[5].explain.happens[1]`, `.example.steps[0]`. Problem: this reads as "score to the power something" (for example, squaring), which would not make negatives positive and is not what softmax does. What happens is that a fixed number (about 2.7) is raised to the power of the score. A learner who tries this on a calculator with the 2.0 / 1.0 / 0.0 example will not get 67% / 24% / 9%. Replacement: "Turn each score into a positive number by raising 2.7 (a fixed special number) to the power of the score. A low score gives a number close to zero; minus infinity gives exactly zero."

25. **MISLEADING (dropped caveat).** Quote: "Subtract the row's biggest score, so nothing gets too large." Location: `components[5].explain.happens[0]`. Problem: the original says "the result is the same, but huge scores cannot overflow" (claim `attn-softmax-stable`). Without "the result is the same", a beginner will think subtracting changes the shares. Replacement: "First subtract the row's biggest score from every score. This does not change the final shares, it only stops the numbers from getting too big for the computer."

26. **CONFUSING.** Quote: "In this toy, an unscaled head that is 64 wide gives almost all its attention to a single word." Location: `components[5].explain.misconfigured`. Problem: "unscaled", "head" and "64 wide" are all unexplained here. It is also a claim about an average (94% in the experiment), not about every row. Replacement: "In this toy, with one big group of 64 numbers and the score-size control switched off, the biggest share averages about 94%, so most of each word's attention goes to a single word."

27. **CONFUSING (naming).** Quote: "Attention weights: The shares of attention each word gives to every word." Location: `components[5].explain.terms[1]`; compare presets notes "random weights" and "with random weights that does not make them attend to each other" (`experiment.presets[0].note`, `[1].note`). Problem: "weights" means the shares in one place and the fixed random tables in another. In the preset notes it is used without a definition. The experiment label "Weights" is rendered "Shares", but these notes bypass it. Replacement: in the notes, say "random tables of numbers" and keep "shares" for the attention percentages. For the term, say "Attention shares (the technical name is attention weights)".

### Message blender stage

28. **MISLEADING (simplification).** Quote: "sat's new list is a blend: about 30% from 'on', plus smaller shares from the other words and from itself." Location: `components[6].explain.thread`. Problem: the 30% is an average of the two groups (the softmax thread says "Averaged over both heads"; this one drops that). In the layer, each group blends its own messages with its own shares (28% and 32% for "on") and the results are then combined. So there is no single 30% blend. The original teaching text has the same wording, so this is not stronger than the original, but a careful reader will be confused when the One word tab shows 28 and 32. Replacement: "Each group blends the messages with its own shares. For 'sat', 'on' gets about 30% on average between the two groups."

29. **CONFUSING.** Quote: "Mixing paints. Each word's colour is a blend of the others, in proportion to its shares." Location: `components[6].explain.analogy`. Problem: the blend also includes the word itself (the stage's own check answer says "its own included"). "of the others" is not accurate. Replacement: "Each word's colour is a blend of all the words' colours, itself included, in proportion to its shares."

30. **CONFUSING.** Quote: "Researchers disagree about what counts as an explanation." Location: `components[6].explain.misconfigured`. Problem: lands abruptly under a "what goes wrong" heading, and the learner does not know why it matters. The original also limits this to older (recurrent) models, which the plain text drops. Replacement: "Do not treat a picture of these shares as a full explanation of why a model answers as it does. Early studies, mostly of an older kind of model, found the shares often do not line up with other ways of measuring what matters, and researchers still disagree about what counts as an explanation."

### Combine the groups stage

31. **MISLEADING (over-claim).** Quote: "Several heads let the layer look for different things at once. One single averaged head could not pay attention to different kinds of information in different places." Location: `components[7].explain.why`. Problem: this is the authors' reason, not a verified result (claim `attn-multihead-motivation`; the experiment itself says the heads in the toy are random). The check answer correctly says "The authors' reason is", so the two sentences disagree in strength. "One single averaged head" is also unexplained. Replacement: "The researchers who designed this say several groups let the layer look for different kinds of information at once, which one group would blur together. In this toy the groups are random, so they do not actually learn different jobs."

32. **CONFUSING.** Quote: "in the original tests, too many heads also made things worse." and "The authors' reason is that…" Location: `components[7].explain.misconfigured`, `.check.answer`; challenge hint "What did the original paper divide them by?" (`challenges[1].hint`). Problem: "the original tests", "the authors" and "the original paper" are never introduced. The beginner does not know who they are or what test. Replacement: introduce once, in the first stage that uses it: "the 2017 research paper that introduced this design (called the Transformer)". Then refer to "the 2017 paper" each time.

### Big picture, analogy and tour

33. **CONFUSING (naming).** Quote: "bag of words" (`components[1].breaks_if_removed`) vs "pile of words" (`challenges[2].explanation`); titles "Attention that ignores order" and "Order-blind attention" (`experiment.guide.presets.Order`). Problem: three names for one idea. Replacement: use "ignores word order" throughout.

34. **CONFUSING.** Quote: "turning the scores into shares of attention that add up to 100%" / "several small discussion groups at once, whose notes are then put together". Location: `big_picture.analogy.mapping[5]` and `[7]`. Problem: the "Attention shares" row does not map to a classroom action; it restates the stage. The learner is left without a picture. Replacement: "each student dividing 100 listening points among the students they could listen to, giving the most to the best match".

35. **MISLEADING (tone/over-claim).** Quote: "WORDS → QUESTIONS, TAGS, MESSAGES → BLENDED MEANING". Location: `ui.eyebrow`. Problem: "blended meaning" claims the output carries meaning. In this lesson the numbers are random, so the output is blended numbers, not meaning, and the page itself says so repeatedly. Replacement: "WORDS → QUESTIONS, TAGS, MESSAGES → NEW LISTS OF NUMBERS".

36. **CONFUSING (minor).** Quote: "Every word will get a turn to look at all the others." / "lets every word look at every other word". Location: `components[0].explain.what`, `big_picture.story`. Problem: a word also looks at itself (the lesson says so only at the mask and the blender). A learner counting 6 x 5 squares will find 6 x 6. Replacement: "every word, itself included".

### Experiment, presets and challenges

37. **CONFUSING.** Quote: "The size of the difference is exactly 0 in one case and about 0.45 in the other." Location: `experiment.guide.presets.Order.notice`. Problem: the learner is not told what "the difference" is a difference of, or what 0.45 means. (In the code, it is the largest change between a word's new numbers in the original and in the reversed sentence.) Replacement: "The check measures how much each word's new numbers change when the same words are put in reverse order. With seat numbers off the change is exactly 0, so order made no difference. With them on, it is about 0.45."

38. **CONFUSING.** Quote: "The biggest share (the average of each row's largest share, over both groups) is about 35%." Location: `experiment.guide.presets.Cat.notice`. Problem: a very long sentence with a nested definition and "about 100%" next to it, while elsewhere the lesson says the shares add up to 100%. Replacement: "Each row adds up to 100% (the grid may show a rounding gap of a point or so). Take each row's biggest share and average them across all rows and both groups: about 35%."

39. **CONFUSING.** Quote: "How spread out the scores were / How spread out the scores are now". Location: `experiment.labels` ("Score spread before scaling", "Score spread used"). Problem: "spread out" is undefined and the pair does not say which number is good. Replacement: "Typical gap between scores before dividing" and "Typical gap between scores after dividing".

40. **MISLEADING (title).** Quote: "One word takes everything" and "almost every word pays attention to a single word". Location: `challenges[1].title`, `.brief`. Problem: a reader will assume a single word is winning the attention of the whole sentence. What actually happens is that each word puts most of its own attention on one word, which can be a different word for each row. Replacement title: "Each word fixes on one word"; brief: "With one big group and the score-size control off, each word puts almost all its attention on a single word (not always the same one). Spread the attention out without changing the sentence."

41. **CONFUSING.** Quote: "Dividing by that square root, or splitting into four or more narrower heads, keeps the attention spread out." Location: `challenges[1].explanation`. Problem: "narrower heads" is jargon; and "four or more" is true for this sentence and this pass mark (80%), not in general. Replacement: "Dividing by that number, or using four or more smaller groups, brings it down in this puzzle. With two groups and no dividing it stays too concentrated."

42. **CONFUSING.** Quote: "(A rule hiding later words would also do it, but that rule is locked in this puzzle.)" Location: `challenges[2].explanation`. Problem: the learner cannot see why hiding later words would restore word order; that is true but never explained. Replacement: delete the parenthesis, or add: "(Hiding later words also makes each word's view depend on its place, but that rule is locked here.)"

43. **CONFUSING.** Quote: "The server runs your settings again and checks the result." Location: `ui.challenges_intro`. Problem: "the server" is jargon for a beginner. Replacement: "The site runs the layer again with your settings and checks the result."

44. **CONFUSING (naming).** Quote: "puzzle", "challenge", "Break & fix". Location: `ui.challenges_intro`, `challenges`, guide. Problem: three names for the same section. Replacement: use "Break & fix puzzle" or just "puzzle".

## What a beginner would understand well (keep)

- The three-line summary in the big picture: "Each word asks a question, every word offers something in reply, the best matches get the biggest share of attention, and each word ends up as a blend of what it paid attention to." This is the clearest sentence in the lesson.
- The question / tag / message trio and the one-line check answer ("what I am looking for / what I offer so others can find me / what I hand over if you pick me").
- The cards analogy for words, the "cover the rest of the page with a card" analogy for the mask, "100 attention points" for softmax, "several people read the same page for different reasons" for combining groups, and "mixing paints" (apart from item 29).
- Honest framing about the toy: every stage repeats "random numbers, so patterns mean nothing". The Pronoun preset ("it" does not link to "animal") is a strong, honest teaching move.
- Worked numbers: 6 words numbered 0 to 5, 6 x 6 = 36 scores, 15 of 36 hidden, the two "the" words that differ only by place, 2.0 / 1.0 / 0.0 giving about 67% / 24% / 9%. All are correct.
- "Dot product" defined in plain terms. "Weighted sum" defined well.
- Caveats that were kept: no full explanation from attention pictures; real models have extra steps after the combine stage; more groups are not automatically better.
- Tone: no marketing or hype and no talking down. Only mild point: the repeated imperative "Do not mix it up / Do not treat" in the misconfigured text is slightly scolding, but it is acceptable.

## Accuracy notes

- No plain sentence is wrong. The numbers match the code.
- Over-claim or dropped caveats that matter: items 18 (wrong next stage), 24 (power), 25 ("same result" dropped), 31 (authors' motivation stated as fact), 35 (blended meaning).
- Caveats dropped but not worth fixing for a beginner: accented letters in the toy tokenizer become separate pieces; the FlashAttention and cache detail; the opposite True/False mask conventions in code libraries; the claim about mainly older models in the explanation research (but see item 30).
