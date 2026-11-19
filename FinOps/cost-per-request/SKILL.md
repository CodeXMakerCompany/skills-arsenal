---
name: cost-per-request
description: Price a design before it ships: tokens, cloud resources, and the traffic assumption, down to cost per request and cost per month, then the levers in order from free to quality-trading. Use for /cost-per-request, "what does this cost", "cuánto cuesta esto", "the bill went up", or on any design that calls a model or allocates a resource.
---

# Cost per request

**Every design ships with its cost per request.** Not a feeling about whether it is expensive. A number, with the assumption behind it and the limiter that bounds it.

This is the house rule, and it is cheap to hold: the arithmetic takes five minutes at design time and is nearly impossible to retrofit after the architecture is set.

---

## 1. Write the unit first

Pick the unit the business actually counts: a request, a document processed, a user per month, a conversation, an invoice. Then state the traffic assumption as a number you can defend, from a dashboard where one exists and from the user where it does not.

A cost with no traffic assumption is unfalsifiable. "About a cent a call" means nothing until someone says how many calls.

## 2. Count the tokens, do not estimate them

For a model call, count the real thing with a token-counting endpoint on a real sample, never by dividing characters by four. Then split the input into:

- **the stable prefix** (system prompt, tool definitions, few-shot examples, the retrieved corpus if it repeats),
- **the volatile part** (this request's content),
- **the output**.

That split is what decides the cost, because the stable prefix is the part caching makes nearly free, and most designs are input-dominated.

## 3. Do the arithmetic

Rates per million tokens, as of 2026-11: Opus 5.5 at $4 in and $20 out, cache reads $0.20. Sonnet 5.5 at $2 and $10, cache reads $0.10. Haiku 5.5 at $0.10 and $0.50 up to a 100k prompt. Fable 5.2 at $8 and $40. Batch processing is half price. **Verify these before quoting them**, because they change, and a stale price is how a design gets approved on the wrong number.

A worked example, a summarization endpoint at 50,000 requests a day, 3,000 input tokens of which 2,500 are a stable prefix, 500 output tokens, on Sonnet 5.5:

| | Per request | Per day | Per month |
|---|---|---|---|
| No caching | $0.011 | $550 | $16,500 |
| Stable prefix cached | $0.00625 | $313 | $9,375 |
| Same work on Haiku 5.5, cached | $0.00055 | $28 | $825 |

Three numbers from the same design. The architecture did not change, only where the tokens went and which model read them. **This table is the deliverable**, and it is why the arithmetic happens before the code.

A cache write costs more than a base input token, so caching pays from the second read onward and does nothing for a prefix that changes every request. Verify the hit rate from the response's own cache-read token count rather than assuming it worked: a timestamp or an unsorted JSON blob in the prefix silently invalidates everything after it.

## 4. Count the rest of the request

The model is usually the biggest line and never the only one. For the same unit, add: the compute (per-invocation and per-GB-second, or the share of an always-on instance), the egress, every storage read and write with its own per-request price, the queue and notification messages, the logs ingested and retained, the per-request cost of the observability you are adding, the vector store, and any per-seat or per-call third-party API.

Logs and traces are the line people forget. Logging the whole prompt and response at 50,000 requests a day is a real monthly number, and it is also a data-retention problem.

## 5. Pull the levers in order

Free first. Never trade quality before taking the wins that cost nothing.

1. **Cache the stable prefix.** Order it so nothing volatile sits before the cache point. The largest single win in most LLM designs.
2. **Stop buying tokens you do not use.** Trim the system prompt, cut the overlapping instructions, drop the few-shot examples the model no longer needs, retrieve three chunks instead of ten, and stop re-sending the whole history when a summary does the job.
3. **Cap the output.** Ask for the shape you need. Output tokens cost five times input on every model in the table.
4. **Batch what is not interactive.** Half price, for anything a nightly job can do.
5. **Validate before you spend.** Reject the oversized input, dedupe the repeat request, short-circuit the case a lookup answers.
6. **Then lower the effort.** The first quality-trading lever, and often free in practice on routine work.
7. **Then the cheaper model**, measured against an eval, not assumed. Try the strongest model at lower effort before a cascade: a cascade splits your cache across models and the handoff logic becomes something else to maintain.
8. **Then the architecture.** Pre-compute, denormalize, move the work to a cheaper service, or do not do it per request at all.

## 6. Judge per completed task

**A cheaper request that needs two retries or three turns is not cheaper.** Measure the cost of finishing the job: include the retries, the failed parses, the second pass a weaker model needs, and the human minutes a wrong answer costs. A model that is 20x cheaper per call and wrong a fifth of the time is not a saving, it is a transfer to whoever cleans up.

## 7. Report

- **Cost per unit**, with the traffic assumption stated.
- **The monthly number** at current traffic, and at the traffic the business expects next.
- **The breakdown**, biggest line first.
- **The limiter.** What bounds this cost, and what would double it (principle-explain-the-number).
- **The levers you took and the ones you left**, with what the remaining ones are worth.
- **The guard.** For anything unbounded, the cap that keeps a bug from becoming a bill: the token ceiling, the retry cap, the concurrency limit, the budget alarm and its threshold.

For the month-over-month and multi-cloud view, run **cloud-cost-forecast**. For the latency side of the same change, **benchmark-checklist**. For the knobs behind the model line, **inference-tuning**.
