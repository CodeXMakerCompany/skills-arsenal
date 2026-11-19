---
name: figure-it-out
description: Design an auditable playbook when no narrower one fits: a large migration, an ambitious multi-part change, or work a human reviews after stepping away. Scales rigor to the task, runs a hypothesis loop, and logs decisions. Use for /figure-it-out, "figure it out", or "resuélvelo".
---

# Figure it out

When the task matches no playbook, design one. The deliverable before any code is the workflow itself: phases that scale rigor to the task, run the scientific method, and leave a trail a human can audit after stepping away.

## Start

Open a task list whose first item is to read the Principles section of **codex-mode**. Then add the phases below.

## Phase A: Frame

Ground first, then commit. Do not start the run until you can state:

- **Done, as a falsifiable predicate** (principle-prove-it-works).
- **Scope, quantified.** Rough units and effort, plus the blockers grounding surfaced.
- **The rigor level, biased high.** One-way doors and wide blast radius get more. Reversible low-stakes steps get less. Rigor is gates and artifacts, not trying harder.
- **The budget.** Wall clock, tokens, and dollars where the run calls models or provisions infrastructure.

Present the framing and the tradeoffs before committing to a long run. Reversible work proceeds (principle-never-block-on-the-human), but a multi-hour run earns one checkpoint.

## Phase B: Design the workflow

Decompose into atomic, independently landable units. Sequence riskiest-unknown-first. Scaffold and verification come before features (principle-foundational-thinking).

- **Build the verification harness before the work**, with the baseline captured from the pre-change state, so every check reads as old value against new value.
- **For a one-way-door design decision, run architect** (which runs **arena**). Skip it for mechanical work whose shape is already concrete: a second arena over a settled design is over-engineering.
- **Decide what fans out.** Parallelize only across seams, one worktree or branch per worker. Do not over-fan.
- **Write the phase list down.** That list is what the human reviews.

Then execute it. Add the concrete steps to the task list between Phase C and Phase D, run each under the Phase C loop, and weave the Phase D log through them as each step lands rather than writing the trail at the end.

## Phase C: Run the loop

Each unit is an experiment. State the hypothesis, make the smallest change, measure against the predicate on the real artifact, keep it if it advanced and revert it if it did not. Verify each unit before starting the next (principle-sequence-verifiable-units).

- Verify by inspecting the artifact, never a self-report. When something passes too easily, suspect the observation method before the system.
- Pair delegated work with a judge. If a worker games the gate, reset and harden the contract. If the gate itself is wrong, fix the gate in its own change rather than routing around it.
- A verdict is `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`. Inconclusive is not a pass. Never hide a negative.

## Phase D: Keep the audit trail

Log the run through **show-me-your-work**. Work this ambitious usually earns committing the trail so the reviewer can read it in the PR. The trail plus the diff is what lets the human come back and trust the result.

## Phase E: Verify and hand back

Check the whole against the Phase A predicate on the real product, not just the harness. Encode every recurring correction as a gate, a lint, a type, or a script (principle-encode-lessons-in-structure).

**Reply:** the playbook you designed, the rigor level and why, the trail path, what is verified against the predicate, the spend against the budget, and what is still open.
