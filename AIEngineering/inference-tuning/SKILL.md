---
name: inference-tuning
description: Tune a production LLM call across the three axes that trade against each other, quality, latency and cost, with the knobs in the order that costs least: caching, context, output, effort, model, then serving. Use for /inference-tuning, "make this LLM call faster", "optimize this prompt", "which model should this use", "está muy lento el endpoint de IA".
---

# Inference tuning

Three things trade against each other: **quality, latency, cost**. You cannot optimize all three, and any change that claims to improve all three without a measurement is a guess.

So fix the order: name which one you are buying and which you are willing to spend, pull the knobs that are free first, and measure each change against an eval before keeping it.

**Prerequisite:** an eval that can tell better from worse (**llm-evals**), and a baseline measurement of latency, tokens, and cost per request. Tuning without those is rearranging the prompt until it feels better.

---

## 1. Measure where the time and money actually go

Per request, split out: time to first token, generation time, the token count in and out, any retrieval or tool time, and the retries. Then tag it per route, because an app has several shapes of request and a global average hides all of them.

The usual surprises: the retrieval step costing more than the model, a 6,000-token system prompt on a 50-token question, a retry storm from a too-tight timeout, a cache hit rate of zero because something volatile sits at the top of the prompt.

## 2. The knobs, in order

**Free, no quality cost:**

1. **Prompt caching.** Order the request so everything stable comes first and the volatile part comes last, then put the cache point after the stable block. Cache reads cost a fraction of input tokens, so this is the biggest single win in almost every production call. **Verify it from the response's cache-read token count**, not from the fact you configured it: a timestamp, an unsorted map, or a per-request id in the prefix invalidates everything after it.
2. **Stream.** It does not change total time, it changes the time the user waits for the first word, which is the number they experience. Required anyway for large outputs, which otherwise hit request timeouts.
3. **Input hygiene.** Cut the overlapping instructions, drop the few-shot examples a stronger model no longer needs, retrieve three good chunks instead of ten mediocre ones, and summarize the history instead of resending it whole.
4. **Output shape.** Ask for exactly the fields you need, with a schema. Output tokens cost several times input, and generation time is dominated by them. A model asked to "explain your reasoning and then answer" when you only parse the answer is paying twice.
5. **Parallelize what is independent.** Retrieval alongside a classification, independent tool calls in one turn.
6. **Batch what is not interactive.** Half price for anything a nightly job can do.

**Trades quality, so measure each one:**

7. **Effort.** The first real lever, and often free in practice. Lower it for chat, classification, and high-volume routes. Raise it for coding, long-horizon agentic work, and anything where a wrong answer is expensive. Tune it per route, never globally, and re-tune after a model change because the levels are recalibrated between models.
8. **Model.** Try the strongest model at lower effort before you try a weaker model at high effort: on current models the former often wins on both quality and cost. Then measure a cheaper model on the eval set rather than assuming it will do. A cascade (cheap model first, escalate on low confidence) is a real pattern, but it costs you a split cache and routing logic to maintain, so make it earn that.
9. **Thinking.** Leave adaptive thinking on by default. Where a route must not think, use the mechanism the model supports rather than an instruction telling it not to, and expect to re-verify that route on every model change.

**Serving and plumbing:**

10. **Timeouts and retries.** A timeout shorter than the p99 generates retries, which triples cost and latency on exactly the requests already struggling. Set the timeout from the measured distribution, cap the retries, and back off.
11. **Fallback chain.** Name what happens on a timeout, a rate limit, or a refusal: a smaller model, a cached answer, a degraded response, or an honest error. A fallback that is never exercised is a hope, so test it deliberately.
12. **Where it runs.** First-party API, or a cloud provider's hosted version close to your data. Feature parity and pricing differ between them, so check both before standardizing, and note that a provider-hosted deployment can lag on the newest parameters.

## 3. One change at a time

Change one knob, run the eval, read the three numbers, keep or revert. Never stack. A batch of six changes that collectively improved the number tells you nothing about which five to keep.

Hold the quality bar as a hard constraint: a latency or cost win that drops eval score below the threshold is not a win, it is a product change, and it needs the human who owns the product to accept it.

## 4. Report

A table with the baseline and each kept change: p50 and p95 latency, time to first token, input and output tokens, cost per request, and eval score. Then the limiter (what bounds the current number), what you reverted and why, and the guard rails in place: the max token setting, the retry cap, the concurrency limit, the budget alarm.

Vet every latency number with **benchmark-checklist** and every cost number with **cost-per-request** before reporting it.
