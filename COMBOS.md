# Combos

Small sets that work well together. Two to four skills each, in order, with what you get.

Nothing here is complex on purpose. If a combo needs more than four steps it belongs in a `codex-mode` playbook, not here.

---

## Daily

**Starting a ticket**
`clarity` → `in-your-own-words` → `architect`
Requirements checked and blocked if ambiguous, the goal restated, the shape decided. The three things that are cheap now and expensive later.

**Picking up yesterday's work**
`recall` → `codex-mode`
Where things stand and what the next move is, then straight into the playbook that fits.

**Dropped into an unfamiliar repo**
`heatmap` → `how`
The map and the business logic marked, then the specific question you actually had.

**A question you want answered properly**
`forever-learning`
On its own. The invariant and where it breaks, no basics.

---

## Shipping

**A normal feature**
`architect` → `cost-per-request` → `comment-psycho` → `nexus-guard`
Shape, price, clean code, gate. The minimum that keeps a feature honest.

**A bug fix**
`tdd` → `blast-radius` → `correct`
Failing test first, check what else it touches, then make the class of mistake impossible.

**A diff an agent wrote**
`ai-diff-review` → `nexus-guard`
Tier it, review at that depth, then the gate. Skipping the first one makes the gate report a gap.

**A design you are not sure about**
`arena` → `interrogate`
Several candidates judged blind, then adversaries try to break the winner.

**Opening the PR**
`unslop` → `technical-writing`
Slop out, then the four sections a reviewer reads in a minute.

---

## AI features

**Shipping an LLM endpoint**
`llm-evals` → `llm-threat-model` → `cost-per-request`
Can you tell better from worse, can it be attacked, what does it cost. In that order.

**It is slow or expensive**
`inference-tuning` → `benchmark-checklist`
Pull the free levers first, then verify the number is real before reporting it.

**A new model came out**
`llm-evals` → `inference-tuning`
Rerun the whole set before believing anything, then re-tune effort per route.

---

## Production

**A new service going live**
`iac-review` → `observability-baseline` → `deploy-pipeline`
Review the plan, make it debuggable, then stop deploying it by hand.

**Something is broken right now**
`incident` playbook → `aws-log-insights` → `correct`
Mitigate and preserve evidence, find it in the logs, then make the monitoring catch it next time.

**The bill jumped**
`cloud-cost-forecast` → `cost-per-request`
Decompose the move, then price whatever caused it properly.

---

## Talking to people

**A demo or a video**
`feeling` → `script-stakeholder` or `script-qa` → `demo-video` → `anti-slop`
Decide what they should feel, storyboard for that audience, render, then the last gate.

**Explaining your work to someone**
`teach` → `bro`
The full explanation, then the plain version if it landed as jargon.

**Bad news for a stakeholder**
`feeling` → `enjoyable-talk`
Aim at trust, then say it fast and plainly with the path forward.

---

## Keeping the arsenal sharp

**End of a session that taught you something**
`reflect`
On its own, with approval before it edits anything.

**Monthly**
`monthly-skills-checkup`
Target model, scores, rewrites, logged.

**You corrected the same mistake twice**
`correct`
Architecture, then types, then a lint whose error names the fix.

---

## Rules for combining

- **One skill owns the deliverable.** The rest gate it.
- **Order matters where a skill consumes another's output.** `ai-diff-review` before `nexus-guard`, `llm-evals` before `inference-tuning`, `clarity` before anything.
- **Two is usually enough.** A four-skill combo on a one-hour task is ceremony.
- **`clarity` and `nexus-guard` are the bookends.** Nothing starts without clear requirements, nothing ships without the gate.
