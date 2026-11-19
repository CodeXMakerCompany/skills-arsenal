# Shipping

**You own what lands. Verify each PR independently, land only the verified run, then keep your hands off.**

1. **Verify before landing, with an agent that did not write the code.** One verifier per PR, running the change the way a user would, reporting `PASS`, `PASS+NOTES`, or `FAIL` on that PR. Green CI is not a verdict: CI runs the tests the author wrote. An approving bot review is not a verdict either.
2. **Land the contiguous verified run from the bottom.** Walk up from the lowest unmerged PR and stop at the first without a pass. A verified PR above an unverified one waits, because it cannot land without the code beneath it.
3. **Every new head needs its own green CI.** A verdict covers one patch. A rebase that leaves `git patch-id` unchanged keeps its verdict; anything else needs a fresh one.
4. **Run the gates once more at the head that will actually land**: **nexus-guard**, the migration plan, the rollback trigger. For a deploy that touches infrastructure, the Terraform plan is reviewed by a human, not by you.
5. **Check the deploy, do not assume it.** After merge, read the pipeline to green, then the real signal: error rate, p95, the dashboard the feature changed, the cost line if the change adds spend. Say what you checked and what you did not.
6. **State the rollback trigger before you merge**, not after something breaks. What number, on what dashboard, at what threshold, and the command that reverts.

Never merge on the user's behalf unless they said to. Never enable auto-merge unless they asked.
