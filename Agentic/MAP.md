# Agentic

How work gets run. Not what gets built: the style, the playbooks, the parallelism, the memory between sessions, and the one gate that stops all of it.

```
Agentic/
├── codex-mode/              THE ENTRY POINT. Style, principles, model routing, autonomy
│   ├── worker.md            rules every spawned subagent reads first
│   └── playbooks/           investigation · bug-fix · feature · refactoring
│                            perf-issue · prototype · eval · shipping
│                            opening-a-pr · autonomous-run · session-pickup · incident
├── clarity/                 hard gate on ambiguous requirements. Blocks execution
├── architect/               shapes, types, boundaries and the price, before code
├── arena/                   N candidates at one task, pick a base, graft the rest
├── swarm/                   N workers over slices or a race, one report back
├── figure-it-out/           design a playbook when none fits
├── sharpen/                 make a task deeper, not bigger
├── recall/                  rebuild context across recent sessions
├── ketchup/                 catch the human up, and list what waits on them
└── show-me-your-work/       the decision trail for long or unattended runs
```

## Start here

**`codex-mode`.** Everything else in this category is something it routes to. Read it once end to end, then let the playbooks pull the rest.

## Route

| Situation | Skill |
|---|---|
| A task arrived as a ticket, spec, or request | `clarity`, **before anything else** |
| Any non-trivial task | `codex-mode`, then match a playbook |
| About to write code across a boundary | `architect` |
| The design is contested or has no precedent | `arena` |
| The work splits into independent slices | `swarm` |
| No playbook fits: a migration, an ambitious multi-part change | `figure-it-out` |
| The prompt you were given is too shallow | `sharpen` |
| Starting work and you have lost the thread | `recall` |
| The human stepped away and is back | `ketchup` |
| A run nobody is watching | `show-me-your-work`, from the first decision |

## clarity is the one skill here that stops you

Everything else in this category keeps work moving. `clarity` is the exception: when a *requirement* is ambiguous, inconsistent, or missing, it blocks execution until the owner resolves it in writing.

That looks like a contradiction with [`principle-never-block-on-the-human`](../Principles/principle-never-block-on-the-human/SKILL.md), and the line between them is the point:

- **Ambiguous about how to build it** (library, pattern, file layout, types) → decide and proceed. A wrong guess costs a refactor.
- **Ambiguous about what to build** (behavior, who it is for, what counts as correct, the money or data rule) → block. A wrong guess costs a rewrite, and it is not your decision to make.

The test: **if I guess wrong, is the fix a refactor or a rewrite?**

## Combinations that matter

- **`clarity` runs before `architect`.** Designing a shape for requirements nobody has pinned is how you architect the wrong product beautifully.
- **`architect` runs `arena`** when the design is contested. Do not run both by hand.
- **`arena` and `swarm` are different tools.** Arena is N attempts at *one* artifact, judged and merged. Swarm is N workers on *different* slices, aggregated. Picking the wrong one wastes the fan-out.
- **`figure-it-out` ends in `show-me-your-work`.** Work ambitious enough to need a designed playbook is ambitious enough to need a trail.
- **`recall` is not `session-pickup`.** Recall loads context across several recent sessions. The `session-pickup` playbook resumes one specific thread.
- **`swarm` loses to a script** whenever the work is mechanical and checkable. See `principle-build-the-lever`.

## Not here

- The rules `codex-mode` cites: [`Principles`](../Principles/MAP.md).
- Proving the work: [`Verification`](../Verification/MAP.md).
- Gating it before merge: [`Security`](../Security/MAP.md).
- Changing how `codex-mode` itself behaves: `automate-me` and `reflect` in [`Meta`](../Meta/MAP.md).
