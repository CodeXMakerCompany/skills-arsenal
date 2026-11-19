---
name: show-me-your-work
description: Keep a reviewable decision trail for long-running or unattended work: a TSV log with one row per decision (what, why, evidence, result). Local by default, committed when a reviewer needs the trail to trust the result. Use for /show-me-your-work, autonomous runs, multi-phase work, incidents, or anything a human reviews after stepping away.
---

# Show me your work

Keep one canonical log. Other skills route their trail here rather than inventing a format.

## The format

A single TSV file, one row per decision. Cells stay on one line. Evidence is a pointer, not prose.

Columns: `ts`, `phase`, `decision`, `why`, `evidence`, `result`.

- **ts.** ISO 8601 timestamp.
- **phase.** The phase or workstream.
- **decision.** What was chosen or done, one line.
- **why.** The reason in plain words. If a principle drove it, say the reason plainly rather than tagging the principle.
- **evidence.** A link or path that proves it: a commit SHA, a PR number, `file:line`, an artifact, a trace, a screenshot path, a dashboard link. Never a paragraph.
- **result.** The outcome or predicate state: `tests green`, `reverted`, `p95 410ms`, `INCONCLUSIVE`, `open`.

An example, plain enough that a reviewer reads it at a glance:

```
ts	phase	decision	why	evidence	result
2026-11-18T09:02:00Z	frame	counted the work first, 41 endpoints and roughly 30 hours	wanted the size before starting a long run	commit 3a9f1c2	found 5 things to sort out first
2026-11-18T09:40:00Z	harness	captured p95 per endpoint before touching anything	so every later number reads as old against new	scripts/bench.sh, baseline/	baseline saved, 41 endpoints
2026-11-18T11:15:00Z	auth	moved token parsing to the boundary	one parse, typed inside, no re-validation downstream	commit 7c21e0a	tests green, p95 unchanged
2026-11-18T12:30:00Z	auth	threw out a worker's result, its run never hit the server	checked the access log instead of trusting its summary	worktree reset	reverted, brief tightened
```

## Logging a row

Write each entry the way you would tell a teammate what you did. Plain words, concrete actions, no jargon (**unslop** applies to log text too).

Use `scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>`. It stamps `ts`, writes the header on first use, strips stray tabs and newlines, and quotes any cell starting with `=`, `+`, `-`, or `@` so a spreadsheet cannot execute it.

Log decision points and checkpoints, not every action: a fork chosen, a unit completed with its verification result, a pivot or revert with its trigger, a blocker surfaced, a gate fixed. One row per iteration for loop runs. Skip the trivial.

A run is one agent conversation. A pickup, a replacement agent, or a new session starts a new run, and its first row in an existing log has phase `start`, naming the timestamp range of rows it did not write. Use phase `start` for nothing else.

## Where it lives

By default a working artifact, not committed: `decisions.tsv` in the work directory, or `.audit/<task-slug>.tsv` when several efforts run at once. Commit it only when the work is ambitious enough that a reviewer needs the trail to trust the result.

## Rules

- **Append only.** A wrong call gets a new row that supersedes it. Never edit or delete history.
- **Evidence from committed scripts beats hand-made one-offs** (principle-encode-lessons-in-structure).
- **Audit the log before handing back.** Walk your rows against what actually happened. Every row maps to a real decision, and every evidence pointer resolves and shows what the row claims. A fork or abandoned approach that shaped the work and is not logged is a gap, so add it. Correct the log by superseding, never by rewriting.
- **Cross-model review of the trail.** Before handing back, spawn a subagent on another vendor's model where one is configured, otherwise a different model than the one that did the work. It reads the trail and flags what the user should look at: decisions with weak evidence, verification claimed without proof, choices that look risky in hindsight, gaps a skim would miss. Self-review is not a substitute.

Every reply for a run that produced a trail ends with an **Attention** section: the reviewing model on its own line, then each flag pointing at specific rows. "No flags" is a valid value.

## Reading the trail

Top to bottom, following the evidence pointers, spot-checking. GitHub renders a committed TSV as a table. `column -s$'\t' -t decisions.tsv` renders it in a terminal.
