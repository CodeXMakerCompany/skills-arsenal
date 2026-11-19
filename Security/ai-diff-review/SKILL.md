---
name: ai-diff-review
description: Risk-tier a diff an agent wrote and apply the review depth that tier earns, so review scales with blast radius instead of with diff size. Use for /ai-diff-review, "review this AI code", "how much review does this need", "revisa este diff", or on any agent-authored change before it reaches a human reviewer.
---

# AI diff review

Review at AI speed means review that scales with risk, not with how many lines arrived. A 400-line generated test file needs a skim. A 6-line change to the authorization check needs an adversary.

Tier first, then review. Guessing the depth is how a team ends up reading everything shallowly.

---

## Tier the change

Take the **highest** tier any hunk in the diff reaches.

| Tier | The change touches | Review |
|------|--------------------|--------|
| **0 — trivial** | Comments, formatting, a rename with no semantic change, a doc, a test for behavior that already shipped | Read the diff. Confirm the claim of triviality is true, because "just a rename" that crosses a serialization boundary is not. |
| **1 — local** | One module's internals, no boundary, no persisted data, no money, no credentials | Read it yourself plus the tests. Confirm the tests would fail if the behavior broke (principle-test-behavior-not-implementation). |
| **2 — boundary** | An API contract, a queue message shape, a schema, a shared type, a dependency, a config default, anything another service reads | **blast-radius** with the one safety fact proven by a run, plus **interrogate** with two adversaries. |
| **3 — critical** | Auth, authorization, payments or ledger, PII, secrets, a migration, infrastructure, rate limits, an LLM call that reaches a tool or a datastore | Tier 2 work plus: a human on the PR, **nexus-guard** at the landing head, and an adversarial pass by a model from a different family than the author. For an ordering or concurrency risk, **statechart**. |

Say the tier and the hunk that set it in the first line of your report. A tier nobody can trace to a file is a tier someone will argue down.

---

## What generated code gets wrong

Look for these specifically. They are not general code smells, they are the failure modes of a model writing code that has to typecheck and look right.

- **The invented API.** A method, flag, or option that does not exist but is named exactly as it should be. Typechecks against a loose signature, fails at runtime. Check every unfamiliar call against the installed version's own source, not against what the name implies.
- **The plausible error path.** A `try` that catches, logs, and continues, where the right move was to fail. The code reads as careful and silently eats the bug.
- **The test that tests mocks.** Three assertions on what a mock was called with and none on what the system did.
- **The retry with no cap.** Or no backoff, or around an error that is deterministic, so it turns one failure into three plus latency.
- **The unbounded thing.** A query with no limit, a loop over an unpaginated list, a fan-out sized by input, a prompt built from a whole table.
- **The copied wrong pattern.** An agent copies the nearest example. If the nearest example was already wrong, the diff spreads it. Check whether the pattern is right, not whether it matches.
- **The confident comment.** A comment asserting an invariant nothing enforces. Delete it and encode the invariant, or delete it and the claim with it (**comment-psycho**).
- **The silent scope creep.** Three unrelated improvements bundled with the fix, each individually fine, together unreviewable.

---

## Review rules

- **The author never clears their own work.** An agent reviewing its own diff checks what it meant to build. The reviewer is a different agent, on a different model where one is configured, at tier 2 and above.
- **A finding needs a run.** At tier 2 and above, a claimed defect comes with the command and the output. An argument is a hypothesis.
- **Judge the bot comments on their merits.** A scanner's finding is a reviewer's opinion, not an authority. Confirm it in the code before acting, and dismiss it in writing with the reason when it is wrong.
- **Count the diff's honesty, not its size.** A large mechanical diff from a committed codemod is easier to trust than a small hand-made one, because the reviewer can rerun the codemod (principle-build-the-lever).

---

## Output

- **Tier**, and the hunk that set it.
- **Reviews run**, and by what.
- **Findings**, each with `file:line`, the failure mode from the list above where it matches, the command that proves it, and the fix.
- **Cleared**, briefly: what you checked and why it is fine.
- **Verdict**: ready for human review, or not, and what is missing.
