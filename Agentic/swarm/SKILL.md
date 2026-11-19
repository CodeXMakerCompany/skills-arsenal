---
name: swarm
description: Fan out N parallel workers, drain them, and return one report. Use for /swarm, "swarm this", or parallel coverage, races, gauntlets and exploration.
---

# Swarm

Open a task list with one entry per phase before launching anything: Frame, Fan out, Aggregate, Report.

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. **Choose the shape.** Partition into slices, race N workers on identical briefs, or mix both. For a race or a mix, declare the selection rule before spawning: `first pass`, `rank all`, or `best-of`. Declaring it afterwards is picking the winner you liked.
3. **Pick the worker model** from the `swarm workers` line in `~/.claude/arsenal-models.md`, default `claude-haiku-5-5` for mechanical work and `claude-sonnet-5-5` where a slice needs judgment. For a model race, name each arm's model up front.
4. **Give each worker its own writable output.** When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method: sample count, what one sample is, and the order. The worker records both in its result.

## Phase B: Fan out

Spawn all N in one message, in the background. Each kickoff opens with `Read <codex-mode path>/worker.md before anything else.`

Every brief stands alone: the goal, the scope, the exact slice or race arm, how to verify, and what to report. Reports come back `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the terminal results. Drop any result that does not record the SHAs and the method its brief named, and respawn that worker once. After a second miss, record a gap. **A gap is not a pass.** For coverage, every required slice needs a result. For a race, apply the rule you declared in Phase A.

Never paste raw worker dumps into the main thread (principle-guard-the-context-window).

## Phase D: Report

One consolidated report: a result table, one line per issue, the gaps and dropouts, and the race rule where one applied. Write it through **unslop**.

## When not to swarm

A deterministic script beats fan-out whenever the work is mechanical and checkable (principle-build-the-lever). Ten workers doing a codemod by hand is ten chances to do it differently. Write the codemod, prove it on one unit, then run it.
