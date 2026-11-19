---
name: arena
description: Spawn N parallel candidates at the same task, pick a base, graft the strongest parts of the losers into it. Use for /arena, "arena this", "throw it in the arena", or when one attempt at a non-trivial artifact would lock in the wrong shape.
---

# Arena

Open a task list with one entry per phase (Frame, Fan out, Cross-judge, Pick, Graft, Verify) before launching anything.

## Phase A: Frame

Every candidate gets the same prompt, so the prompt is the contract.

1. State the artifact each candidate produces.
2. Derive the rubric: three to six concrete gradeable criteria for success on *this* task. It is the picker's tool in Phase D. Candidates never see it, only the task.
3. Pick the runners from the `arena runners` line in `~/.claude/arsenal-models.md`. By default one seat each on `claude-opus-5-5` at effort `high`, `claude-sonnet-5-5` at effort `high`, and a non-Anthropic model where one is configured. Repeat one model when the work is generation-bound rather than judgment-sensitive. Spawn more seats for genuinely different design directions, not for more of the same.
4. Give each candidate its own output location: a git worktree where possible, otherwise its own scratch directory (principle-separate-before-serializing-shared-state).

## Phase B: Fan out

Spawn all N in one message, in the background, each with the task, the path to the shared grounding, its own output path, and instructions to produce the artifact plus a short rationale naming what it considered and rejected. Each kickoff opens with `Read <codex-mode path>/worker.md before anything else.`

If a candidate produces nothing, proceed with N-1 and note the dropout.

## Phase C: Cross-judge

After the candidates finish, spawn one read-only judge on a different vendor's model than the parent where one is configured, otherwise the cheapest seat that can hold the rubric. It scores each candidate by path label against each criterion and recommends a base. It never sees which model wrote which candidate.

## Phase D: Pick a base

Read every candidate end to end before picking. Score criterion by criterion, not on holistic feel, then compare with the judge. Agreement confirms the pick. Disagreement means one of you is biased or the rubric was ambiguous, so read both rationales before deciding.

Pick the base a future maintainer can extend most easily without breaking invariants.

## Phase E: Graft

Walk each losing candidate once more for what is worth porting, usually one or two things each, not most of it. Fold each graft in by hand so the result stays coherent under one mental model. Never paste mechanically.

Convergence on one shape is strong agreement: note it and ship the consensus, no graft needed. Wild divergence means Phase A was under-specified, so reframe and rerun rather than averaging the divergence.

## Phase F: Verify

Verify the synthesized artifact like any other output (principle-prove-it-works). If verification finds something the arena missed, either Phase A was wrong or a candidate caught it and you missed the graft. Do not paper over it.

## Outputs

One synthesized artifact, plus a note naming the base and why, the judge's verdict or that no judge ran, each graft with its source, what was rejected, any convergence or dropouts, and the verification result.
