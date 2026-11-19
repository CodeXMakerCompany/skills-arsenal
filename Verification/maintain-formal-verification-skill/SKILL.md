---
name: maintain-formal-verification-skill
description: Bring a project's formal verification back in line with the code after the code changed: find the commits that touched verified code, update the model or properties to describe the code as it is now, rerun, and say whether each failure is drift in the verification or a bug in the code. Use for /maintain-formal-verification-skill, "is the model still true to the code", or after merges and refactors that touched verified code without rechecking it.
---

# Maintain a formal verification skill

A formal check proves a property of what it describes. When the code changes and the verification does not, the check can keep passing while it describes code that no longer exists. **That pass is the dangerous case, because it looks like a proof.**

This is the upkeep loop for a verify skill from **create-formal-verification-skill**, or any project-local skill that runs a model checker, prover, or code-level verifier against named code. The project-local skill handles changes an agent makes while using it. This skill handles the changes that skipped it: merges, edits made without it, and drift accumulated across many commits.

## Outcomes

Give each check one outcome and say which:

- **in sync.** Nothing since the last sync alters what the check describes, and it passes.
- **updated.** The code changed, the verification now describes the new code, and the check passes.
- **bug.** The verification describes the current code, and the code breaks the property. This is a finding about the code, not drift.
- **blocked.** The check could not be brought back in line or could not run. Say exactly why.

A check can be both updated and bug: the update makes the verification describe the code again, and then the property fails on it.

## Edit scope

Only the verification: models, harnesses, property files, and the verify skill itself. Never edit product code during a run unless the user asks. **When a property fails on current code, never weaken the property or the model to make it pass.** Report the failure.

## Pass

1. **Find the checks.** A verify skill has no fixed name, so find it by what it does. For each check, collect the property, the code it covers, the bounds and assumptions, the command that runs it, and the commit where it was last confirmed. No verify skill means stop and point at **create-formal-verification-skill**. No recorded sync commit means use the last commit that changed the verification files, and say that you did.
2. **Run it as it is**, once, before changing anything, and record the result. A pass here does not tell you the code is correct. It tells you the old description still holds. A failure here can be drift or a bug, and you do not decide which until step 5.
3. **Read every change to covered code.** Diff the covered files from the sync commit to now and read each commit message. Look for code that moved: a covered function renamed, split, or relocated is still covered. Look for new code that touches the state a check guards. Classify each change:
   - **No effect.** Formatting, comments, or paths the verification does not cover. Check this against the model, not against the commit message.
   - **The verification no longer describes the code.** A step that was indivisible is now two, a branch appeared or vanished, a check moved, a new path reaches the guarded state, a value's range changed.
   - **The promise changed on purpose.** Evidence in the change says so: the doc comment, the tests, the changelog, the commit message. The property must change, and you must cite that evidence.
   - **The promise may be broken.** The code changed and nothing says the promise did. A failure that follows is a bug candidate.
4. **Update from the code, not from the result.** Change the model so each changed part again points to code a reviewer can open, keeping one indivisible step as one step. Write the update before you rerun, and do not shape it by what makes the check pass. Change a property only for a promise that changed on purpose, recording the old wording, the new wording, and the evidence. Keep the bounds unless the change makes them wrong, and say so if you must reduce one.
5. **Rerun and judge each result.**
   - **Pass:** the check may have lost the ability to fail. Break the new code the way the property guards against and confirm it catches that. Then drop the break.
   - **Fail:** replay the counterexample against the real code, step by step. If a step cannot happen, the verification is wrong, so fix it and say what was wrong. If every step can happen, it is a bug: name the commit that introduced it, tell the counterexample as steps in the code's own words, and state the harm in one sentence.
6. **Update the verify skill.** The covered code, the commands, the bounds, the assumptions, and the sync commit, set to the commit you checked. Never move the sync commit for a blocked check. Then follow the skill once as the next agent would, so you know its steps still run.

## Report

For each check: the outcome and the commits you read; what changed in the verification and why; the rerun result and the break you used to show it can still fail; each bug in plain words with its counterexample, harm, and introducing commit; and what the verification still does not cover.

Say outright which failures were drift and which were bugs. For a check that passed before your update and fails after, say that the old pass was on a stale description.

Put the verification updates in a change of their own, separate from any product fix.
