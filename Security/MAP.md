# Security

Review and security at AI speed. Code arrives faster than anyone can read it, so review scales with blast radius instead of with line count, and the gate is one checklist with a verdict.

```
Security/
├── ai-diff-review/      tier the diff, apply the review depth that tier earns
├── llm-threat-model/    the six attack surfaces an LLM feature adds
└── nexus-guard/         the last gate: seven checks, ships or doesn't
```

## The order

They run in this order, and the order is the point.

```
agent writes a diff
        |
   ai-diff-review          tier 0-3, then the review that tier earns
        |
   llm-threat-model        only if the change touches a model, a tool, or retrieval
        |
   nexus-guard             at the head that will actually land
        |
   ships / doesn't ship
```

Running `nexus-guard` without `ai-diff-review` first means the gate's fourth check fails: it verifies the tiered review happened, it does not perform it.

## Route

| Situation | Skill |
|---|---|
| An agent wrote this, how much review does it need? | `ai-diff-review` |
| Is this AI feature safe to expose? | `llm-threat-model` |
| Can this merge? Can this deploy? | `nexus-guard` |
| A secret is in the history | **stop.** Rotate first, then the `incident` playbook |

## What each one owns

- **`ai-diff-review`** owns the question of *depth*. Four tiers from trivial to critical, taken from the highest-risk hunk, plus the eight failure modes specific to generated code: the invented API, the plausible error path, the test that tests mocks, the uncapped retry, the unbounded query, the copied wrong pattern, the confident comment, the silent scope creep.
- **`llm-threat-model`** owns the surface that no existing control sees: prompt injection direct and indirect, data exfiltration, tool and agent abuse, output handling, cost abuse, and refusal paths. A WAF does not read intent, and the attacker is usually an authenticated user.
- **`nexus-guard`** owns the verdict. Seven checks: secrets, dependency risk, boundaries, AI-code review, cost delta, observability, rollback. Any failure means it does not ship, with the file and line named.

## Rules

- **The gate runs at the landing head.** A gate run on a stale head verified a different change.
- **An override is written down**, in the PR, with who accepted what. Never soften a finding because the change is urgent.
- **A pass says what was checked, never that the change is secure.** "No secrets found by `<tool>` in the diff" is honest. "This is secure" is not.
- **Cost is a security check.** An unbounded loop around a paid call is an availability and abuse problem, not just a bill.

## Not here

- Finding bugs adversarially: `interrogate` in [`Verification`](../Verification/MAP.md).
- The eval that stops a prompt regression: `llm-evals` in [`AIEngineering`](../AIEngineering/MAP.md).
- IAM and network surface in infrastructure: `iac-review` in [`Platform`](../Platform/MAP.md).
- Making a repeated mistake impossible: `correct` in [`Meta`](../Meta/MAP.md).
