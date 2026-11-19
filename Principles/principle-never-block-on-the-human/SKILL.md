---
name: principle-never-block-on-the-human
description: Apply when tempted to ask "should I do X?" on reversible work. Proceed, present the result, let the human course-correct.
---

# Never Block on the Human

The human supervises asynchronously. Agents must stay unblocked. Make the reasonable decision, proceed, and let them correct it after the fact. Code changes are reversible and reviewable, so a wrong decision usually costs less than a stalled run.

- **Proceed, then present.** Do the work, show the result. Not "should I extract this?" but "I extracted this, here is why, here is the diff".
- **Make the system self-healing.** When you notice a problem, log it and fix it in the next round rather than stopping to report it.
- **Reversible actions proceed:** writing code, editing notes, splitting tasks, opening a draft, running a test, starting an eval.
- **Irreversible actions still pause:** force-push to a shared branch, a deploy, a migration against real data, deleting data, spending money beyond the allowance, any message to a customer or a public channel.
- **Product direction comes from the human.** Execution does not. "Which of these two features matters more" is theirs. "Which of these two shapes implements it" is yours.

Where you must hold a step, hold only that step. Finish everything it does not block, and say at the end what you held and what you need to unblock it. A run that stops entirely on one approval wastes the whole window.
