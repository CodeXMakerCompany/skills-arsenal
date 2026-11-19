---
name: interrogate
description: Adversaries try to break a change or a design, and only findings proven by a run survive. Use for "interrogate", "adversarial review", "multi-model review", "challenge this", "stress test this", "find blind spots", "tear this apart", "rómpelo".
---

# Interrogate

Adversaries try to break a change or a design. A finding survives only when a run proves it. Report the findings. Do not apply fixes.

## Frame

The scope is what the user names. Otherwise it is the branch diff from its merge base with the base branch, through the working tree.

State the intent with **in-your-own-words**, drawn from the user's message, the commits, and the PR description. Ask the user when the intent is genuinely unclear, because an adversary that attacks the wrong intent produces noise.

## Fan out

Run **arena** Phase A steps 3 and 4 and Phase B, with four changes. Read the `interrogate reviewers` line of `~/.claude/arsenal-models.md` in place of `arena runners`. Copy the scope's uncommitted changes into each worktree. Give each adversary the scope, the intent, and this brief:

> Break this change. Prove each finding with a run against the real code: a failing test, a repro script, a request that returns the wrong body, command output that shows the wrong behavior. For a design or a plan, run a prototype or probe the current tree. Keep repros in your own worktree. Report each finding with a title, the exact command, the output it printed, and the output the intent requires. Leave out anything you did not run. That excludes style, naming, structure, and risks that need a future change to matter. No findings is a valid result.

Seat the panel on different model families where more than one is configured. Different models catch different real bugs, and two seats on one model mostly agree with each other.

## Verify

Rerun each finding's command yourself. Keep a finding when the output shows the failure and the failure breaks the intent. Drop the rest. Merge findings that share a root cause.

Skip arena Phases C, D, and E. Adversaries find different failures, so the verdict keeps every verified finding rather than one adversary's list.

## Output

- **Intent.** The restatement.
- **Findings.** For each verified finding: the command, its output, how it breaks the intent, and which adversaries found it. Say "no verified findings" when none survive.
- **Dropped.** Per adversary, how many findings were dropped and why.

A clean interrogation is a real result. Padding it with style notes wastes the next reader's attention and teaches them to skim the next one.
