---
name: feeling
description: Name the one feeling an artifact must transmit before producing it, pick the mechanisms that actually transmit it, then check the artifact against it with someone who never saw the intent. Use for /feeling, "what feeling do I want to transmit", "qué quiero que sientan", before a video, demo, UI, landing page, stakeholder update, or any artifact a human will react to.
---

# Feeling

Every artifact a person sees transmits a feeling, whether you chose it or not. The default is usually *nothing*, which reads as indifference, or *impressed by the author*, which reads as noise.

So choose it first, in one word, and then build backwards from the mechanisms that actually produce it.

This is not decoration applied at the end. The feeling decides what you show first, what you leave out, and how long you hold on it. Those are structural decisions, and they are expensive to change once the thing is built.

---

## 1. Name it before you build

Three lines, before the first frame, the first component, or the first sentence:

- **The feeling:** one word. Confidence, relief, urgency, calm, curiosity, delight, trust, respect.
- **The feeling to avoid:** also one word, and this is the useful half. A demo aiming at *confidence* usually fails into *overwhelmed*. A stakeholder update aiming at *trust* fails into *defensive*.
- **Who feels it:** a specific person, not an audience. "A tech lead deciding whether to adopt this" transmits differently than "a CFO approving the budget".

**One feeling per artifact.** Two is none: the structural choices that produce calm and the ones that produce urgency are opposites, and an artifact trying for both reads as confused.

## 2. Build it from mechanisms, not adjectives

A feeling is produced by structure, pacing, and specificity. Never by saying the word.

| To transmit | The mechanism |
|---|---|
| **Confidence** | Show the real thing working on real data, first, with no preamble. One number with its limiter attached. No hedging on what you verified. |
| **Relief** | Show the pain for exactly as long as it takes to recognize it, then the single move that removes it. The relief is in the contrast, so cutting the pain entirely kills it. |
| **Urgency** | The cost of waiting, as a number with a date. Never a louder adjective. |
| **Calm** | Fewer elements. No motion. Honest empty states. Nothing blinking. A loading state that says what it is doing. |
| **Curiosity** | Open with the result that should not be possible, then stop. The question does the work. |
| **Trust** | Say what it does not do, and what you did not check. A caveat offered before it is asked for buys more trust than any claim. |
| **Delight** | One unexpected detail that costs the viewer nothing and was clearly nobody's requirement. One. Two reads as a theme and the surprise is gone. |
| **Respect** | Skip what they already know. Nothing transmits respect for a senior like not explaining the basics. |
| **Competence** | The detail only someone who actually did it would know. The gotcha, the real number, the thing that broke first. |

## 3. The failure feelings

Check against these explicitly, because each one is the common failure of a specific good intention.

| You aimed at | You often land on | The tell |
|---|---|---|
| Confidence | **Overwhelmed** | Everything shown at once, no first thing |
| Competence | **Impressed by you** | The artifact is about the work rather than the result |
| Thoroughness | **Suspicious** | Over-explaining, pre-defending, too many qualifiers |
| Helpful | **Patronized** | Explaining what they know, defining their own terms back at them |
| Enthusiastic | **Sold to** | Adjectives in place of numbers, no stated limitation |
| Honest | **Defensive** | The caveat arrives after the question instead of before |

## 4. Check it on someone who never saw the intent

**You cannot judge this yourself**, because you know what you meant and you feel it on their behalf.

Show the artifact with no framing, to a person or to a subagent that was given the artifact and nothing else, and ask two questions: *what did you feel?* and *what is this for?* Do not prompt with your intended word, and do not list options.

If the answer is not your word or a neighbour of it, the mechanisms are wrong, not the viewer. Change the structure, not the adjectives.

## 5. Where this applies

- **A demo or a video.** The feeling decides the opening shot and what gets cut. Pairs with [`demo-video`](../../demo-video/SKILL.md), [`script-qa`](../../script-qa/SKILL.md) and [`script-stakeholder`](../../script-stakeholder/SKILL.md), which already pick an audience; this picks what that audience should feel.
- **A UI.** Especially empty states, errors, and loading. An error message is the highest-feeling-per-word surface in any product, and most are written last by whoever was closest.
- **A PR body or a design doc.** Aim at *confidence* and *respect*: the proof first, no narration of your process.
- **A stakeholder update, good or bad news.** Aim at *trust*. The caveat goes first, the number goes second, the plan goes third.
- **An incident update.** Aim at *calm*. What is happening, what you are doing, when the next update comes. Nothing else.

## 6. Output

The feeling, the feeling avoided, the person, the three mechanisms you used, and what the blind check reported back. If the check disagreed with your intent, say what you changed structurally.

Then the honest line: **if the artifact only transmits the feeling because you explained the feeling, it does not transmit the feeling.**
