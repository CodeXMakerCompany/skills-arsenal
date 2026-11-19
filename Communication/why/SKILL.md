---
name: why
description: Answer "why does X work this way" from the record rather than the code: commits, PR discussions, tickets, ADRs, incidents. Returns a cited read on decisions and tradeoffs. Use how for runtime behavior instead.
---

# Why

Answer from the record, not the code. The code shows what is true now and never says what it was weighed against.

Read the commits and PR discussions that introduced the target and each later change to it. Where the trail is thin, widen it: the ticket, the ADR or design doc, the incident that preceded the change, the revert and what it said, the chat thread the PR links to, the dependency bump that forced it.

- **Cite what the authors wrote.** Quote the commit, the review comment, the ADR line, with its identifier.
- **Mark your own inferences as inferences.** "The commit does not say why, so this is inference: the retry was added two days after the incident on the same path."
- **Say what the record does not answer.** A missing why is a finding, and often the most useful one, because it tells the reader that nobody wrote it down and the constraint may no longer exist.
- **Keep the confidence language exact.** A hedge here is a result, not a style choice. Another skill that reuses your answer must be able to tell what is documented from what you concluded.

Watch for the three common shapes: the decision that was deliberate and is still right, the decision that was deliberate and whose constraint is gone, and the accident that got load-bearing. Name which one you found, because the reader's next move differs for each.

Useful for: design rationale, "why we picked Y", a regression's history, a postmortem, and any threshold or magic number whose value someone must now change.
