---
name: reproduce-and-fix-issues
description: Reproduce a triaged issue against the real app through the configured verification skill, verify whether a fix already exists, and open a bounded draft pull request only after before-and-after proof. Use only from the configured issue-bot reproduce automation.
---

# Reproduce and fix issues

Take one triaged ticket. Reproduce it against the real app. Fix it only if the repro is real and the fix is small. Open a draft PR only with before-and-after proof.

Read `.claude/issue-bot.yaml` first: the repo, the base branch, the control adapter, the limits, and who to escalate to.

**Every output of this automation is a draft for a human.** Nothing merges, nothing deploys, nothing closes.

## 1. Reproduce before anything else

Drive the real app through the repo's verification skill, named in the config. Launch, doctor, then the user path the ticket describes.

Three outcomes, and you say which:

- **Reproduced.** You have the failing observation: the response body, the screenshot, the exit code, the log line. Capture it as the **before** artifact and keep it.
- **Not reproduced.** Say exactly what you ran, on what version, with what data, and what you got instead. Then check whether it is already fixed (step 2) before concluding anything.
- **Cannot drive it.** A missing precondition, an environment you lack, auth you do not have. Escalate with the precondition named. **Do not substitute a code-reading theory for a repro.** A theory posted as a reproduction is the one thing this automation must never do.

## 2. Check whether it is already fixed

A ticket often outlives its bug. Before writing anything, check the base branch and the recent commits on the affected path for a fix that landed after the report. If one did, verify it against the repro steps, say which commit fixed it, and close out with that evidence and no PR.

## 3. Decide whether to fix at all

Fix only when all of these hold:

- The repro is yours, not the reporter's description.
- The root cause is located, not guessed (principle-fix-root-causes).
- The fix fits inside `max_files_changed` and `max_diff_lines`.
- The fix needs no new dependency, no schema change, no infrastructure change, and no public API change.

Anything else: stop, and hand back the repro, the located cause, and your assessment of what the fix needs. **A reproduced bug with a precise cause and no patch is a good outcome.** It is most of the work, and it is the part a human cannot parallelize.

## 4. Fix, with the test first

Write the failing test first where the path is cheap, per **tdd**. Then the smallest change the evidence justifies. Then rerun both the test and the original repro through the verification skill, and capture the **after** artifact.

No comments in the code (**comment-psycho**). No unrelated cleanup, however tempting. No scope beyond the ticket.

## 5. Open the draft PR

Branch per issue, off the base branch. Draft, always. The body follows `opening-a-pr.md`, with the proof section carrying both artifacts:

> **## Proof**
> Before: `<the failing output, inline or linked>`
> After: `<the passing output>`
> Driven through `verify-app`, feature `<name>`, on `<commit>`.

Link the ticket, and comment on the ticket with the PR link. Never mark it ready for review, never request a review, never merge.

## 6. Stop at the cap

At `max_minutes_per_issue` or `max_usd_per_issue`, stop where you are. Report what you reproduced, what you located, what you changed, and what is unverified. An unattended run that blows its budget chasing one bug is a worse outcome than three reproduced bugs with no patches.

## 7. Report

Per ticket: the outcome (`reproduced`, `not reproduced`, `already fixed`, `cannot drive`), the evidence pointers, the PR if there is one, the spend, and anything you deliberately left alone.
