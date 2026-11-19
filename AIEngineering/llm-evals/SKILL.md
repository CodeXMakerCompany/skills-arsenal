---
name: llm-evals
description: Build the eval set and the grader that let you change a prompt, a model, or a retrieval strategy and know whether it got better, then wire it as a gate and keep it honest. Use for /llm-evals, "build an eval", "how do I know if this prompt is better", "set up evals", "¿mejoró el prompt?", or before any LLM feature ships.
---

# LLM evals

**Shipping a prompt with no eval is shipping untested code.** The difference is that the untested code fails loudly and the prompt fails quietly, in the 7% of traffic nobody looks at.

An eval is three things: a set, a grader, and a number you trust enough to act on. Most eval work that fails, fails on the grader.

---

## 1. Define what "better" means, first

Write the decision the eval will settle and the result that would change it, before building anything. "We ship the new prompt if accuracy on the 150-item set is up and the refusal rate does not rise." No decision, no eval: you will build a dashboard and keep shipping on vibes.

Then name the failure modes you actually care about, from real traffic, not from imagination. For an extraction task: the wrong value, the missing field, the hallucinated field, the right value in the wrong shape. Each becomes a criterion.

## 2. Build the set from real traffic

- **Real inputs beat synthetic ones.** Pull them from logs, tickets, or user sessions, and strip the PII as you go.
- **Stratify deliberately.** Include the common case, the known failure modes, the adversarial inputs (keep the prompt-injection suite from **llm-threat-model** in here), the empty and malformed inputs, and the long-tail shapes. An eval set of the happy path measures the happy path.
- **Split it.** A train slice you may look at and tune against, and a **test slice you score every round and never tune against**. Without that split you are measuring how well you memorized the set.
- **50 to 200 items is usually enough** to see a real effect, if they are the right items. Hundreds of near-duplicates measure one item loudly.
- **Version it with the code.** An eval set that drifts silently makes every historical number meaningless.

## 3. Fix the grader before you trust a number

In order of preference:

1. **Deterministic check**, where the answer is checkable: an exact match, a parsed field, a schema validation, a passing test, a number inside a tolerance. Free, fast, and it never drifts.
2. **Rubric with a model judge**, where quality is a judgment. The judge runs on a **different model family than any arm**, sees the output without knowing which arm produced it, and scores independently gradeable criteria rather than giving one holistic score out of ten.
3. **Human labels**, for the sample that calibrates the other two.

**Validate the grader against human labels on 20 to 30 items before you trust it.** A judge that disagrees with you a third of the time is measuring something, just not what you asked. This step is skipped almost always and is the usual reason an eval and production disagree.

## 4. Run it honestly

- **One variable per arm.** An arm that changes the prompt and the model answers nothing.
- **Blind the grader.** Opaque arm labels, shuffled order, and the author of an arm never grades it.
- **Three trials minimum per arm**, and report the spread. **A gap smaller than the run-to-run spread is no difference**, and saying so is a valid, valuable result.
- **Price the run before it runs:** items times arms times trials times tokens. Batch it where latency does not matter, at half price.
- **Check that every run did the task.** Count the errors, the refusals, the empty outputs, and the truncations separately. A run that errored fast and scored zero is not a quality signal, it is a bug in the harness (**benchmark-checklist** questions 4 and 7).

## 5. Wire it as a gate and keep it honest

- **In CI** on any change to a prompt, a tool definition, a retrieval parameter, a model id, or an effort setting. Those are code changes, and the eval is their test suite.
- **A threshold that fails the build**, not a dashboard someone checks weekly.
- **Online, not just offline.** Trace real production calls with their inputs, outputs, latency, tokens, and cost, so the offline set can be refreshed from what actually happens. Each production failure that the set would have missed becomes a new item: that is how the set stays relevant instead of aging into a regression suite for last quarter's problems.
- **Rerun the whole set on every model change.** A model upgrade is not a drop-in. Prompts tuned for an older model are often too prescriptive for a newer one and score worse, which reads as the new model being worse.
- **Watch for the set going stale.** When every arm scores above 90%, the set has stopped discriminating. Add harder items rather than celebrating.

## 6. Report

The decision, the set with its size and strata, the grader and its agreement with human labels, the per-arm scores with spread and trial count, the cost of the run, and the verdict in the words of the decision from step 1. Then the one item you would add to the set next.
