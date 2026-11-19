# Verification

Proof. Not "it compiles", not "it looks right", not a subagent's summary.

```
Verification/
├── interrogate/                          adversaries try to break it, only runs count
├── blast-radius/                         what breaks elsewhere, and the one safety fact
├── benchmark-checklist/                  vet a performance number before reporting it
├── tdd/                                  failing test first, when the path is cheap
├── statechart/                           model-check an ordering risk with TLA+
├── create-verification-skill/            build the repo's own way to drive the real app
├── maintain-verification-skill/          keep that skill and its feature map honest
├── create-formal-verification-skill/     prove an invariant where tests cannot reach
└── maintain-formal-verification-skill/   stop a stale model from looking like a proof
```

## Start here

For a repo with no scripted way to prove behavior, **`create-verification-skill`** is the highest-value thing in this category. Everything else gets better once it exists, because "prove it" stops meaning "argue convincingly".

## Route

| The question | Skill |
|---|---|
| Is this change wrong? | `interrogate` |
| What else does it break? | `blast-radius` |
| Is this number real? | `benchmark-checklist` |
| Will this bug come back? | `tdd` |
| Can these events happen in a bad order? | `statechart` |
| Can an agent drive this app and prove a feature works? | `create-verification-skill` |
| Does our verification still describe the app? | `maintain-verification-skill` |
| Can we prove this invariant for every case, not the cases we thought of? | `create-formal-verification-skill` |
| Is the model still true to the code? | `maintain-formal-verification-skill` |

## The verification ladder

How sure you are, cheapest first. Get as far down as the stakes justify, and **say where you stopped**.

1. You said so. Worthless alone.
2. You pointed at the line. A real `file:line`.
3. You showed the bad case cannot reach.
4. You ran it. A script against the real code that fails loud if you are wrong.
5. You reproduced it in the running system.
6. You proved it for every case in a stated scope. `statechart` and the formal skills live here.

## Combinations that matter

- **`interrogate` finds, it does not fix.** It reports, you fix under the owning skill.
- **`blast-radius` before `nexus-guard`**, not after. The gate checks that you looked; this is the looking.
- **`benchmark-checklist` runs twice** on a perf task: once on the baseline before you plan from it, once on the final number.
- **The create/maintain pairs are a loop.** A generated verification skill rots the week the app changes, so the maintain pass is the half people skip and the half that keeps it true.
- **`statechart` pairs with `state-machine-architect`** ([Development](../Development/MAP.md)): one designs the machine, the other proves it.

## A verifier is never the author

An agent checks what it meant to build. Verification runs on a different agent, and usually a cheaper model, because reading an outcome is easier than producing one. `codex-mode`'s model table routes verification to the cheap tier for exactly this reason.

## Not here

- Reviewing a diff for risk tier: `ai-diff-review` in [`Security`](../Security/MAP.md).
- The merge gate itself: `nexus-guard` in [`Security`](../Security/MAP.md).
- Measuring an LLM's output quality: `llm-evals` in [`AIEngineering`](../AIEngineering/MAP.md).
- The rule behind all of this: [`principle-prove-it-works`](../Principles/principle-prove-it-works/SKILL.md).

## Known gap

`statechart` documents the TLA+ method, the spec rules, and how to read a counterexample, but it ships none of the upstream model-checking pipeline. You install TLC yourself. Flagged in the checkup log for the first `monthly-skills-checkup` to judge.
