# How ExplodeAI explains things (and why)

Written 2026-11-08. This records the research behind the 2026-11-08 redesign and how each idea shows up in the lessons. **The evidence below came from web searches that mostly returned secondary sources** (course-design sites and summaries of the original studies), not the original papers. Treat the techniques as well-supported teaching practice, not as proven numbers. Where a search found nothing, this page says so.

## The problem we set out to fix
Each stage had a one-or-two-word label and a short explanation. A learner could see *what each part is* but not *how the parts fit together*, *why one hands something to the next*, or *what to follow through the machine*. A newcomer was left to connect the dots alone.

## Techniques we used

| Technique | What the research says (as found) | What we did |
|---|---|---|
| **Pre-training** (Mayer's multimedia principles) | People learn better from a lesson when they already know the names and characteristics of the main concepts. | A **big picture** card opens every lesson: the whole system in plain words, and every stage named with its stand-in in an analogy, before any stage is opened. |
| **Signalling and spatial contiguity** (Mayer) | Cues that show how material is organised help, and related words and pictures should sit near each other. | The explanation of each hand-off sits next to the stage it belongs to ("How it connects"), with arrows and clickable stage names. The "In our example" box is highlighted. |
| **Segmenting** (Mayer) | Learner-paced chunks beat one continuous block. | Stories are short (a few sentences), the tour moves one stage at a time, and depth stays behind collapsible sections. |
| **Coherence** (Mayer) | Leave out extraneous material. | We removed the keyboard-hint lines and the stage-timings strip, which didn't help anyone learn. |
| **Worked example, then fade the concrete** | Starting concrete and moving to the abstract helps; a review notes that abstract-only material can leave people manipulating symbols without understanding. A critique notes it is not equally effective in every domain. | **One running example per lesson** (a question, a sentence, a request) is followed through every stage with its real values, in the "In our example" box. The numbers come from the real experiment and are checked by tests. |
| **Analogy with its limits** (structure mapping) | Comparing structure helps, but learning from a single analogy risks over-generalising. | Each lesson has **one analogy mapped stage by stage**, plus an explicit **"where the analogy stops being true"** note. Analogies stay labelled as teaching aids. |
| **Retrieval practice and self-explanation** | A widely cited review rates practice testing as highly useful and self-explanation as moderately useful; re-reading and highlighting rank low. Evidence on self-explanation is thinner. | Every stage has a **"Check yourself"** question. The answer stays hidden until the learner asks. |
| **Progressive disclosure** | Reveal in layers so beginners aren't overloaded while experts can dig in; it can slow task completion if overdone. | The story and example are always visible. "Why it is needed", "What happens to the data", "If it is set up wrong" and "Learn more" stay collapsed. |

**Not found:** our searches returned nothing on "predict before you reveal" as a technique, so we did not claim it. The check-yourself question is justified by the retrieval-practice and self-explanation findings above.

## What every lesson now contains
Stored in `content/lessons/<lesson>/teaching.yaml` (separate from the verified lesson file, so the three-pass verification of the claims is untouched):
- **Big picture:** a plain-words story, one analogy mapped to every stage with where it breaks, and the running example.
- **Hand-off explanations:** one or two full sentences for every link between stages: what the sender passes on and why the receiver needs it.
- **Per stage:** a short story, "In our example" (what this stage does to the running example, with real numbers), and a check-yourself question and answer.

**This is teaching text, not verified claims.** It must stay consistent with the verified claims and with the code. `backend/tests/test_teaching.py` runs each lesson's real example and asserts every number the stories quote (chunk counts, token ids, vector lengths, scores, step counts), and the content validator requires every published lesson to have all of it.

## Sources consulted (secondary; verify against the originals before citing)
- Mayer's principles of multimedia learning (summaries): <https://lucidea.com/blog/mayers-12-principles-of-multimedia-learning>, <https://www.digitallearninginstitute.com/blog/mayers-principles-multimedia-learning>, <https://teachfloor.com/elearning-glossary/mayer-design-principles>
- Concreteness fading, worked examples and analogical comparison: Fyfe, McNeil, Son and Goldstone, *Concreteness fading in mathematics and science instruction: a systematic review* (Educational Psychology Review, 2014): <https://link.springer.com/10.1007/s10648-014-9268-0>
- Effective learning techniques (Dunlosky et al., 2013) as summarised by Digital Promise and Columbia University: <https://digitalpromise.org/2015/02/07/five-learning-strategies-that-work/>
- Progressive disclosure: <https://blog.logrocket.com/ux-design/progressive-disclosure-ux-types-use-cases>

## Independent accuracy review (2026-11-08)
A separate reviewer checked every sentence of the teaching text against the code, the verified claims and real runs of each experiment (report: `research_notes/Teaching review/teaching_review.md`). It found 17 errors, 35 risks and 24 nits. They were fixed in the `teaching.yaml` files, and `backend/tests/test_teaching.py` now also asserts the extra numbers the text cites (the 94% / 42% head-scale figures and the 0.45 order gap) and a tokenization merge check that previously never ran. The reviewer did not render the UI, did not verify vocabulary sizes of Claude or Gemini (the text no longer claims them), and did not research parallel tool calls; the text now says "in this lesson" where it describes one call at a time.

## Plain words for newcomers (2026-11-09)
A first reader with no AI background found many terms unexplained. Every lesson now has two voices, switched in the header. **Plain words** is the default: everyday names for stages, controls and tabs, short sentences, and a "Words you will hear" box at each stage that introduces the technical words one at a time. **Technical names** is the original wording. The verified claims and the experiments are the same in both. The rulebook is `docs/PLAIN_WORDS.md`, the text lives in `content/lessons/<lesson>/plain.yaml`, and `backend/tests/test_plain_words.py` fails if a plain-voice text uses a technical word before the stage that introduces it, or quotes a number the technical text does not have. This has not yet been read by an independent newcomer, so treat the wording as a first version.

### Beginner read-through (2026-11-09)
Five independent reviewers each read one lesson's plain text as a complete beginner and checked it against the technical text and the code (reports: `research_notes/Beginner review/`). They found 4 wrong, 48 misleading and 108 confusing items in total (0 wrong in Attention, RAG and Agents). Common problems were one idea going by several names, terms used before they were explained, analogies that suggested the wrong picture, and statements stronger than the verified claims. All were fixed in the `plain.yaml` files. Every quoted number was re-run by the reviewers and matched the code.
