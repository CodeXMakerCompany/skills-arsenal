# AI Engineering

Taking an LLM feature to production: measured, tuned, and observable. Not prompt tips.

```
AIEngineering/
├── llm-evals/          the set, the grader, and the gate that stops a regression
└── inference-tuning/   quality, latency and cost, and the knobs in order
```

## Start here

**`llm-evals`.** Nothing else in this category means anything without it. Tuning without an eval is rearranging a prompt until it feels better, and a model upgrade without one is a coin flip you cannot score.

## Route

| The question | Skill |
|---|---|
| Did that prompt change help? | `llm-evals` |
| Which model should this route use? | `inference-tuning`, measured on the eval set |
| Why is this endpoint slow? | `inference-tuning` |
| What does this cost? | `cost-per-request` in [`FinOps`](../FinOps/MAP.md) |
| Can this be attacked? | `llm-threat-model` in [`Security`](../Security/MAP.md) |
| Is it debuggable in production? | `observability-baseline` in [`Platform`](../Platform/MAP.md) |

## The path to production

```
architect            the shape, and what the model is actually for
   |
inference-tuning     caching, context, output, effort, then model
   |
llm-evals            the set and the grader, wired into CI as a gate
   |
llm-threat-model     injection, exfiltration, tool abuse, cost abuse
   |
cost-per-request     the number, with the traffic assumption
   |
observability-       tokens, cost, latency, failure and refusal rates
 baseline
   |
nexus-guard          ships / doesn't
```

Skipping a step is a choice, not an oversight, so name which one and why.

## The three facts that drive most decisions here

- **Output tokens cost several times input tokens**, and generation time is dominated by them. The cheapest optimization is almost always asking for less.
- **Caching the stable prefix is the largest free win**, and it silently fails if anything volatile sits above the cache point. Verify it from the response's cache-read count.
- **A prompt tuned for an older model is often too prescriptive for a newer one** and scores worse, which reads as the new model being worse. Rerun the whole eval set on every model change.

## Not here

- The agent workflows that *use* models to do work: [`Agentic`](../Agentic/MAP.md).
- The Claude API itself, model ids, parameters and SDK code: the bundled `claude-api` skill, which these skills defer to rather than duplicating.
- Spanish content generation and narration: the root content skills, in [`ARSENAL-MAP.md`](../ARSENAL-MAP.md).

## Known gap

No skill yet for retrieval quality (chunking, embeddings, reranking, measuring recall against a labeled set) or for agent tool-surface design. Both are real gaps, logged for `monthly-skills-checkup` to propose.
