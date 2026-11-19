# Opening a PR

Invoked at the end of every other playbook.

Work from a branch off trunk and keep unrelated work out of it. Rebase into small, landable commits, each one green on its own.

Run **comment-psycho** over the diff before the first commit. Run **unslop** and **technical-writing** over the body.

## The body

A reviewer reads this in under a minute. Four sections, nothing else.

- **## Why.** The goal, in the words the task used. One paragraph. Not "refactored the service layer" but what the user could not do before and can now.
- **## What changed.** The shape of the change, not a file list. Name the one thing a reviewer should look at hardest.
- **## Proof.** The command and its output: the test that failed before and passes now, the screenshot, the measured number with its run count and limiter. For a change that adds a model call or a resource, the cost per request.
- **## Risk and rollback.** What this could break, how you checked, and the trigger and command that reverts it.

Never paste swarm logs, SHA lists, metric tables, or an agent's full report into the body. Link them.

## Commits

Imperative subject under 72 characters, saying what changes for the user. Body carries the why when the subject cannot. The decision trail belongs in the commit and the PR, never in a code comment.
