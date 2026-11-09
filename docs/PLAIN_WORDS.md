# Writing ExplodeAI in plain words

Written 2026-11-09. This is the rulebook for the default "Plain words" voice of every lesson. The audience is a person who has learned nothing about AI yet. The original, technical wording is still there behind the "Technical names" switch, and every verified claim is unchanged.

## How the two voices work
- `lesson.yaml`, `explain.yaml` and `teaching.yaml` hold the technical voice. They are the source of truth for facts and are covered by the claim checks.
- `plain.yaml` (one per lesson) is laid over them when the learner is in the plain voice (`backend/app/content/loader.py`, `_apply_plain`). It can replace titles, stage names, stage text, the big picture, hand-off explanations, experiment hints, example texts, challenges, tour steps and the names of controls and tabs.
- Each stage keeps its standard name as a **technical name** shown next to the everyday one, and lists **Words you will hear**: the technical words that stage introduces, each in one everyday sentence. The learner learns the real vocabulary, but never meets a word before it is explained.

## Rules
1. **One idea per sentence, short sentences.** Aim for fewer than 18 words. No sentence needs a second read.
2. **Everyday word first, technical word second.** Write "a list of numbers (called a vector)", never the reverse. After a word has been introduced you may use it.
3. **A word may not appear before the stage that introduces it**, except the always-allowed words in `backend/tests/test_plain_words.py`. A test checks this.
4. **Start from something the reader already knows**: addresses, maps, libraries, sorting, cooking. Say where the comparison stops being true.
5. **Say what it is for before how it works.** "It exists so that…" comes first.
6. **Numbers are concrete and come from the real run** (24 sentences, 384 numbers, 8 pieces). A test checks that every number in the plain text also appears in the verified text.
7. **No hedging pile-ups and no claims the verified text does not make.** Plain does not mean less careful: when something is only a tendency, say "usually" or "often".
8. **Never use "simply", "just", "obviously" or "of course".** If it were obvious, the learner would not be here.
9. **Controls and tabs get an everyday name.** The technical name is shown small beside it, so the two are linked.
