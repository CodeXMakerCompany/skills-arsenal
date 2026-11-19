# Platform

Orchestration and deployment. Getting code to production fast and boring, and being able to debug it once it is there.

```
Platform/
├── deploy-pipeline/           cut the minutes, add the right gates, keep rollback one command
├── iac-review/                review the plan, not the diff: replacements, surface, cost, undo
└── observability-baseline/    logs with a trace id, the four metrics, alerts on symptoms
```

## Route

| Situation | Skill |
|---|---|
| The pipeline takes too long and people batch changes to avoid it | `deploy-pipeline` |
| Setting up CI/CD from scratch | `deploy-pipeline` |
| A Terraform or CloudFormation change is about to be applied | `iac-review` |
| A new service or LLM path is going live | `observability-baseline` |
| "We cannot tell why it broke" | `observability-baseline` |
| A deploy needs someone watching it | `deploy-pipeline`, because that is the bug |
| An incident right now | the `incident` playbook in [`Agentic`](../Agentic/MAP.md) |
| Forensic RCA on AWS logs | [`aws-log-insights`](../aws-log-insights/SKILL.md) at the root |

## The order for a new service

```
iac-review              before the first apply
   |
observability-baseline  before the first real traffic, not after the first outage
   |
deploy-pipeline         before the second week of manual deploys
```

Doing them in the other order is how a service ends up live, unobservable, and deployed by hand.

## The three tests

Each skill reduces to one question, and the question is the skill.

- **`deploy-pipeline`:** can a one-line fix reach production in minutes, with nobody watching it?
- **`iac-review`:** does the plan replace or destroy anything stateful, and does anyone know?
- **`observability-baseline`:** when it breaks at 2am, can you find out why without deploying anything?

A "no" on any of those is the work.

## Rules

- **Build once, promote the artifact.** Rebuilding per environment means production runs something that was never tested.
- **Review the plan, never the IaC diff alone.** Three lines can replace a database and the diff does not say so.
- **p95 and p99, never the average.** The average hides the tail, and the tail is the complaint.
- **Alert on symptoms, not causes.** CPU is a dashboard. The error rate on a route is a page.
- **Rollback is one command, rehearsed.** A rollback nobody has run is a plan, not a capability.
- **Telemetry is a cost line.** Logging every prompt at 50,000 requests a day is a real monthly number and a retention problem.

## Not here

- The merge gate that checks these happened: `nexus-guard` in [`Security`](../Security/MAP.md).
- The bill all of this rolls up into: [`FinOps`](../FinOps/MAP.md).
- Tuning the model call behind a slow AI endpoint: `inference-tuning` in [`AIEngineering`](../AIEngineering/MAP.md).
- Idempotent handlers and retry-safe steps: [`principle-make-operations-idempotent`](../Principles/principle-make-operations-idempotent/SKILL.md).
