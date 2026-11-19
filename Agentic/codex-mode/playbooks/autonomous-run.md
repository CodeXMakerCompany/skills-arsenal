# Autonomous run

**You own the exit condition. Define done, then drive to it without stopping.** For work the human starts and walks away from.

1. **State the exit condition as a checkable predicate** before the first iteration: tests green, the repro fixed, all N PRs verified, the pixel diff at zero, the eval above the threshold. A run with a vague exit never ends.
2. **Set the budget before you start.** Wall clock, token spend, and dollars where the run calls models or provisions anything. Report spend against it when you stop.
3. **Keep the trail.** **show-me-your-work** from the first decision, not retroactively. A run nobody watched is only as trustworthy as its log.
4. **Loop: hypothesis, smallest change, measure on the real artifact, keep or revert.** Never stack unverified changes. `INCONCLUSIVE` is not a pass and does not advance the loop.
5. **Do not block.** Make the reasonable call on anything reversible and record what you chose and what would change it. Hold only the irreversible steps, finish everything else, and say at the end what you held and why.
6. **Self-heal.** When a check fails for a reason the loop can fix, fix it and continue. When the gate itself is wrong, fix the gate in its own change rather than routing around it.
7. **Stop on the predicate, the budget, or three consecutive iterations with no movement.** Say which one stopped you.
8. **Hand back** the predicate's state, what is verified and how, the spend, the trail path, and the single most useful next action.

Never force-push, deploy, delete data, or message anyone outside the team during an unattended run.
