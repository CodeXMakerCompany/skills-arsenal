# Communication

Understanding things, being understood, and the register you do it in. Half of forward-deployed work is this.

```
Communication/
├── how/                   how does X work, from the code
├── why/                   why is X this way, from the record
├── heatmap/               snapshot a repo, mark the business logic, diff the drift
├── teach/                 explain this work to a person, at their pace
├── forever-learning/      master a technology at senior depth. No basics
├── bro/                   say it again with no jargon
├── in-your-own-words/     restate the goal before acting
├── feeling/               what the artifact should make someone feel
├── enjoyable-talk/        the working register, and feedback worth having
├── unslop/                cut AI tells from English prose
└── technical-writing/     docs, RFCs, ADRs, runbooks, PRs, commits
```

## The four pairs

Each pair looks interchangeable and is not. Picking wrong wastes the work.

**`how` and `why`.** `how` reads the code, so it is always answerable. `why` reads the record (commits, PRs, tickets, incidents), so "nobody wrote it down" is a real and useful answer: it tells you the constraint may no longer exist.

**`teach` and `forever-learning`.** `teach` explains *this codebase's work* to a person and runs `how` and `why` underneath. `forever-learning` masters *a technology or process* at senior depth and deliberately refuses the basics. One is about your system, the other about the world.

**`how` and `heatmap`.** `how` answers one question in conversation. `heatmap` produces dated artifacts in `snapshots/` for a whole repo, with the business logic marked, so two runs diff into an architecture drift report.

**`feeling` and `enjoyable-talk`.** `feeling` is the emotion an *artifact* transmits, decided before you build it. `enjoyable-talk` is the register of the *conversation*. One is produced, the other is lived.

## Route

| Situation | Skill |
|---|---|
| New to a subsystem, about to change it | `how` |
| New to a whole repository | `heatmap`, then `how` for the specifics |
| Where is the business logic? | `heatmap` |
| A threshold or magic number someone must now change | `why` |
| A person needs to understand this change | `teach` |
| You half-know a technology and want to own it | `forever-learning` |
| Your last answer landed as noise | `bro` |
| Before starting work with ambiguous intent | `in-your-own-words` |
| Requirements that are ambiguous, not just the intent | `clarity` in [`Agentic`](../Agentic/MAP.md), which blocks |
| About to make a video, demo, UI, or stakeholder update | `feeling`, first |
| Giving feedback on someone's work | `enjoyable-talk` |
| Any prose leaving the session | `unslop` |
| A doc, ADR, runbook, PR body, or commit message | `technical-writing` |
| A Spanish short-form video script | [`anti-slop`](../anti-slop/SKILL.md) at the root |

## Language

Artifacts are English: docs, PR bodies, commits, findings, reports. `unslop` and `technical-writing` own that.

Talk follows the person. `teach`, `forever-learning`, `bro`, `enjoyable-talk` and `ketchup` answer in the language they were asked in, keeping technical nouns in English and never translating them.

## The rules worth remembering

- **`how` explores in a subagent.** A subsystem walkthrough reads a lot of files and none of them belong in the main thread.
- **`teach` does not redo `how` and `why`.** It runs them and weaves the results, keeping `why`'s hedges exactly, because those are findings rather than style.
- **`bro` is a translation, not a summary.** Every fact survives. If the news was bad, the plain version is still bad.
- **`forever-learning` starts where the quickstart stopped.** The invariant and the failure envelope, never the syntax.
- **`feeling` is structural.** It decides what you show first and what you cut, so it runs before you build, not after.
- **`enjoyable-talk` never costs information.** If the warm version is vaguer, ship the plain one.
- **`heatmap` commits its snapshots.** The value is in the diff, and a gitignored snapshot cannot be compared.

## Not here

- Catching the human up on a session: `ketchup` in [`Agentic`](../Agentic/MAP.md), which borrows `bro`'s voice.
- Blocking on ambiguous requirements: `clarity` in [`Agentic`](../Agentic/MAP.md).
- Killing comments in code: `comment-psycho` in [`Development`](../Development/MAP.md). Code says it with names and types, not prose.
- Choosing between tools rather than understanding one: [`stack-scout`](../stack-scout/SKILL.md) at the root.
