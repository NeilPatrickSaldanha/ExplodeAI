# Video 0: What is ExplodeAI? (series opener and app tour)

Draft 2, written 2026-11-16. This replaces the first draft. The goal: you mostly **show**, and you **talk while you do it** so nobody wonders what you are clicking. Each beat has what you do on screen, what you say, and a short "under the hood" line for what is really happening.

**Length:** about 7 to 8 minutes if you keep everything. Beats marked **[CUT IF LONG]** can go to get closer to 5 minutes.
**Tone:** a friendly teacher. Short sentences. Say what you are about to do, do it, then say what just happened.

**Before you record**
- Open Lesson 03 (Embeddings). Plain words is on. Click Skip on the first-visit walkthrough once.
- Warm up the small AI model: click Experiment and run any example once, so the first real run is fast on camera.
- Close other tabs. Zoom the browser so the buttons are readable on a phone.
- Website link: only say it if the site is public. [OWNER: confirm URL and date]

---

## Beat 1. Cold open (about 20 seconds)

**On screen:** Lesson 03 diagram, all stages together. Slowly drag the **Explode** slider from 0 to 100%.

**Say:**
"This is a sentence going through an AI model. Watch. I pull the machine apart, and now every part is separate. Each one does one job. This is ExplodeAI, and in this video I will show you how it works, step by step."

---

## Beat 2. What it is, and why (about 40 seconds)

**On screen:** your face, or the home page with the five lessons.

**Say:**
"I'm Neil. ExplodeAI is a visual way to learn how AI systems work. You take a system apart, look inside each piece, change things, and even break it on purpose.

I built it because I learn better when I can see something happen. Long paragraphs lose me. So I made the thing I wanted to learn from.

One honest thing: I built this with Claude Code. I decided what to teach and how good it has to be. I'm also making sure I understand every part I show you."

---

## Beat 3. The five lessons (about 25 seconds)

**On screen:** the lesson list on the left. Point at each name. Point at one tick.

**Say:**
"There are five lessons. RAG, tokenization, embeddings, attention, and agents. Each one takes about 25 to 30 minutes. When you explore every stage of a lesson, you get a tick here. I'll open Embeddings, because it's easy to see."

---

## Beat 4. Plain words or Technical names (about 30 seconds)

**On screen:** click the switch at the top. Show Technical names, then switch back to Plain words. Point at one stage name that changes.

**Say:**
"First, this switch. Plain words is on by default. It uses everyday names. Look, this part says Word chopper. If I click Technical names, the same part says Tokenizer. Same part, same facts. Plain words is for when you are new. Technical names is for when you want the real terms. And each stage shows both, so you learn the real word next to the simple one."

**Under the hood:** it is the same lesson underneath. Only the words change.

---

## Beat 5. The big picture (about 30 seconds)

**On screen:** open the **The big picture** bar. Scroll slowly. Close it.

**Say:**
"Every lesson starts with the big picture. A short story of what the whole thing does. One comparison, like a town where similar sentences live close together. And one example sentence that we follow through every stage. It stays closed so it doesn't push the diagram down, and you open it when you want it."

---

## Beat 6. The diagram (about 60 seconds)

**On screen:**
1. Drag the Explode slider back to 0, then to 100%.
2. Point at the buttons: Flow, Data, Move, Isolate, 3D, Calm.
3. Click **Flow**. Click **Data**. Click **Isolate** on one stage. Click 3D to switch to 2D, then back.

**Say:**
"This is the machine. Each block is one stage, and the numbers show the order.

The slider pulls it apart. Flow turns on the moving dots, so you see which stage hands things to which. Data shows real numbers from the last run, not made-up ones. Isolate looks at one part on its own. This button switches between 3D and a flat 2D view. And Calm turns the motion down if it's too much."

**Under the hood:** the positions and shapes are a visual way of explaining. But the order of the stages is the real order of the computation. Each block is labelled so you can tell what is real data and what is only a picture.

---

## Beat 7. A single stage (about 75 seconds)

**On screen:** click **Meaning reader**. Slowly scroll down the panel, pausing on each section: What goes in / comes out, the story, "In our example", the comparison, "Words you will hear", "Check yourself".

**Say:**
"Let me click one stage. This is the Meaning reader.

At the top: what goes in, and what comes out. Then a short story in plain words. Here is the useful part. 'In our example' shows what this stage does to the sentence we're following, with the real numbers. Our eight pieces become eight lists of 384 numbers each.

Here is a comparison, and it also tells you where the comparison stops being true. Because every comparison breaks somewhere.

'Words you will hear' gives you one technical word at a time. You never meet a word before it is explained.

And at the end, a question. Try to answer it first. Then click, and see if you were right."

**Under the hood:** what you are seeing, the numbers, comes from running a real small AI model on this computer, not from a pre-written example.

---

## Beat 8. What breaks if removed (about 45 seconds)

**On screen:** find **What breaks if removed?** on the same stage. Click it. Wait for the result to show side by side with the full version.

**Say:**
"This is my favourite part. 'What breaks if removed?' I click it, and the lesson takes this stage out and runs the whole system again, without it. Now I can see what this stage was for. Not read about it. See it."

**Under the hood:** it is a real second run with that stage taken out, shown next to the normal run. Below it, every fact has a link to its source.

---

## Beat 9. Tour mode **[CUT IF LONG]** (about 20 seconds)

**On screen:** click the **Tour** tab. Press Play. Let two stages go by. Press Pause.

**Say:**
"If you don't want to click around, there's Tour. Press play and it walks you through the stages one by one, in order. You can pause any time."

---

## Beat 10. Experiment: change a real run (about 100 seconds)

**On screen:**
1. Click the **Experiment** tab.
2. Click the **Bookshelf** example. Open the **Nearest sentences** tab.
3. Point at the top three scores (0.695, 0.566, 0.554).
4. Set both "How … become numbers" settings to **Word matching only**. Point at the zeros.
5. Switch them back to **Small AI model**. Click the **Meaning map** tab and hover a point.

**Say:**
"Now the Experiment tab. This is where you change things. Notice the box on the right. It tells me what to try, and what I should see.

I click Bookshelf. My sentence is 'a place to put my books.' It shares no real words with the sentence we hope it finds. Let's look at the nearest sentences. Bookshelf, desk, armchair. All furniture. The model matched the meaning, not the words.

Now I'll break it on purpose. I switch this to Word matching only. This is a simple counter that only looks at which words appear. Look: every score is zero. There are no shared words, so nothing matches. That list at the top is just the first sentences in the library. That's a tie, not a match.

Back to the small AI model, and we get furniture again. And here is the map. My sentence is this ring, and its neighbours are close by. I hover a point to read it."

**Under the hood:** when you click, the page sends your sentence to the backend, which chops it into pieces, turns it into 384 numbers, and compares those numbers with every example sentence. The map squashes 384 numbers down to 3 so you can look at them, so it loses some detail. The list uses the full numbers.

---

## Beat 11. Break and fix (about 45 seconds)

**On screen:** click **Break & fix**. Pick **Same meaning, different words**. Show the broken setup. Change the setting. Click **Check my fix**. Show the result.

**Say:**
"Break and fix gives you something that's broken. Here the search finds nothing useful. My job is to find out why. I look at the settings, and I see the search only matches words. I switch it to the small AI model, and press Check my fix. It says fixed.

The lesson didn't just say yes. It ran my settings again and checked the result."

**Under the hood:** the check is done by the backend running your exact settings, so you can't pass by guessing.

---

## Beat 12. Rebuild **[CUT IF LONG]** (about 25 seconds)

**On screen:** click **Rebuild**. Drag a few stages into order. Click check.

**Say:**
"Rebuild is the last one. I get the stages in a jumbled pile, and I put them in an order that could really work. Each stage has to come after the things it needs. There can be more than one right answer, and the check knows that."

---

## Beat 13. Ask ExplodeAI and the tour guide **[CUT IF LONG]** (about 20 seconds)

**On screen:** click **Ask ExplodeAI**. Type "Why does it need a start marker?" Show the answer. Close it. Click **How to use** once.

**Say:**
"If you get stuck, there's Ask ExplodeAI. It's meant to answer from the lessons, and to tell you when the lessons don't cover something. And 'How to use' replays the quick walkthrough of the buttons."

[OWNER: run the question first so you know what it says before you film it.]

---

## Beat 14. Honesty (about 35 seconds)

**On screen:** point at the Real execution / Simulation / Conceptual badges. Point at the Verified badge. Point at one source link.

**Say:**
"Some honesty before I finish. Every part has a label that says what it is: a real run, a simulation, or only a picture. The sentences and the shop are made up. Nothing here makes a claim about the world.

Each fact links to its source, and each one went through a three-step check. I'm not saying it's perfect. That's exactly why the sources are there, so you can check me."

---

## Beat 15. What comes next (about 30 seconds)

**On screen:** the lesson list. Point at each lesson as you name it.

**Say:**
"From the next video, each one takes a single topic, and we go deep. How an AI looks things up before it answers. How text becomes numbers. How a computer compares meaning. How words look at each other. And how an AI uses tools. If something looks wrong, or you have a question, tell me."

**If the website is public, add:** "You can try it yourself at the link."

---

## Be ready to explain
- Why Plain words is the default, and what Technical names changes (only the words).
- "What breaks if removed" is a real second run with that stage taken out.
- What Word matching only does (counts shared words) and why every score is zero for the bookshelf sentence.
- That the map squashes 384 numbers into 3 and loses detail.
- That the sentences, the shop and the orders are made up. The attention lesson uses random numbers. The agents lesson uses a simple rule instead of a real AI model.
- What the Verified badge means: the claims went through the project's three-step check. It does not mean everything is independently proven.
- How much you built with Claude Code and what you did yourself.

## Do not say
"Guaranteed correct". "Learn two or three times faster". How many people use it. Anything about the optional paid AI features.

## Filming tips
- Say what you will click before you click it, then click, then say what happened. That keeps the actions easy to follow.
- Pause one second after each result so the viewer can read it.
- If a run is slow, talk through what it is doing instead of waiting in silence.
