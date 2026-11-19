---
name: correct
description: Find the mistakes agents keep repeating in this repo and make each one impossible. Try architecture first, then types, then a lint whose error names the fix, then a test, and write docs last. Prove each check fails on a real past mistake. Use for /correct, or each time you correct an agent for something it already did once.
---

# Correct

The operator keeps correcting agents in this repo for the same mistakes. Change the repo so the next agent cannot make them.

Assume every contributor is an agent that sees only the files it opened, copies the nearest example, and takes the shortest path that compiles. Design the repo so a change that looks right from one file is right for the whole repo.

## Find the mistake classes

Read recent commits, reverts, review comments, agent instruction files (`CLAUDE.md`, `.cursor/rules`), and the comments that explain workarounds. Group the mistakes into classes. **A class counts once it has happened twice.**

Common classes worth looking for: a wrong import that compiles, a second way to do something the repo already has one way to do, a hand-synced list that drifted, a boundary where validation was skipped, a test that was weakened to pass, a secret or config read from the wrong place, a model call added with no cost or eval attached.

## Fix each class at the highest level that works

1. **Eliminate it with architecture.** Give each piece of state one owner and each task one supported way. Hide internals so the wrong import fails. Replace hand-synced lists with one source of truth. Delete the old way and the dead code an agent would copy.
2. **Enforce it with types** so the bad state cannot be written. If bad code still compiles, add a lint or CI check **whose error names the fix**: not "invalid pattern" but "use `parseInvoice()` from `src/domain/invoice.ts` instead of casting the row". Where the pattern is already widespread, fail only when a change adds more of it.
3. **Test the behavior.** Fix or delete any test that still passes when the behavior it checks breaks, or fails when only the internals change.
4. **Write docs or agent rules last**, and only for judgment calls. Nothing fails when an agent skips prose.

## Fix and prove

Fix the most frequent classes now, one commit each. **Prove each new check fails on a real past mistake**: check out the commit that made it, run the check, show it red. A check that has never been seen failing is decoration.

Run the same command locally and in CI. Exceptions go on the offending line with a reason, an expiry date, and a human's approval.

## Keep the rule table

Keep a table in the agent instruction file pairing each rule with what enforces it:

```
| Rule | Enforced by |
|------|-------------|
| Parse external data at the boundary | lint: no-raw-row-cast |
| No comments in application code | comment-psycho gate in CI |
| Every model call reports cost per request | PR template check |
```

When the operator corrects you, fix the mistake and add the rule. If the rule was already there and nothing enforces it, that is a repeat: fix it at the highest level in the same change. Drop a rule once its mistake cannot happen.

**Reply:** each class with its evidence, the level you picked, why a higher level did not work, and the red-then-green proof for each new check.
