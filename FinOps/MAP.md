# FinOps

Every design ships with its cost per request. The house rule, and the one that does not bend for a deadline.

```
FinOps/
├── cost-per-request/      price one design: tokens, resources, traffic, levers
└── cloud-cost-forecast/   explain the bill, forecast it, rank the actions
```

## The two jobs

They are different, and conflating them produces a report nobody acts on.

| Scope | Skill | Answers |
|---|---|---|
| One design, before it ships | `cost-per-request` | "What will this cost per request, and per month at our traffic?" |
| The whole bill, after it shipped | `cloud-cost-forecast` | "Why did it go up, and where is it going?" |

`cost-per-request` is a design-time gate. `cloud-cost-forecast` is a monthly or pre-commitment exercise. The first one feeding the second is what makes a forecast a forecast instead of an extrapolation: a feature priced at design time becomes a forecast line, and one that was not becomes a surprise.

## Route

| Situation | Skill |
|---|---|
| Designing anything that calls a model or allocates a resource | `cost-per-request`, before the code |
| "Is this too expensive?" | `cost-per-request`, which turns the feeling into a number |
| The bill moved and nobody knows why | `cloud-cost-forecast` |
| A reserved instance or savings plan decision | `cloud-cost-forecast`, with the break-even stated |
| A budget conversation next week | `cloud-cost-forecast`, as a range, not a point |
| The model line specifically | `inference-tuning` in [`AIEngineering`](../AIEngineering/MAP.md) |
| A spend spike that might be abuse | `llm-threat-model` in [`Security`](../Security/MAP.md) |

## The rules both skills hold

- **A cost with no traffic assumption is unfalsifiable.** "About a cent a call" means nothing until someone states the call volume.
- **Free levers before quality-trading ones.** Caching, input hygiene, output caps, batching, and input validation all come before lowering effort or switching models.
- **Judge per completed task, not per request.** A cheaper call that needs two retries or a human correction is not cheaper.
- **Verify the price before quoting it.** Rates change, and a stale number gets a design approved on the wrong basis.
- **Every unbounded thing gets a cap.** A token ceiling, a retry limit, a concurrency limit, a budget alarm. That is what keeps a bug from becoming a bill.

## Not here

- The latency side of the same change: `benchmark-checklist` in [`Verification`](../Verification/MAP.md).
- The cost of infrastructure a plan creates: `iac-review` in [`Platform`](../Platform/MAP.md), which reports the monthly delta.
- Comparing vendors and pricing models before buying: [`stack-scout`](../stack-scout/SKILL.md) at the root.
