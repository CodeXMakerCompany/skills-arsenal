# Session pickup

**You own the resume point. Read the prior trail, do not redo it.**

1. **Find the trail.** The decision log from **show-me-your-work**, the branch and its commits, the open PR and its review threads, the prior session's final report. Read the metadata and the last messages first, then scan back for the decision points.
2. **Parse long material in a subagent** and keep the reduced timeline in the main thread (principle-guard-the-context-window). A transcript or a CI log never enters your context whole.
3. **Reconstruct the operational state from the repo, not from the story.** The branch, what already landed (`git log`, `git diff` against the base), what is uncommitted, which checks are green, what the PR says. The trail tells you intent; the repo tells you truth. Where they disagree, the repo wins and the disagreement is worth reporting.
4. **Resist re-deriving.** The prior run's conclusions are authoritative input. Re-verify only a conclusion whose evidence you cannot find, and say which ones those were.
5. **Restate the goal and the next concrete step** before touching anything, then continue under the playbook the work was already running.

For context across several recent sessions rather than one, use **recall**. For catching the human up on what happened while they were away, use **ketchup**.
