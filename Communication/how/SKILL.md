---
name: how
description: Answer "how does X work" from the code: subsystem architecture, runtime flow, onboarding mental models, and placement questions (where should this live, which package owns this, is this the right layer). Use why for motivation instead.
---

# How

Explore the codebase to answer "how does X work?".

If the scope is ambiguous, state your interpretation and explore anyway. The user can redirect faster than they can specify.

## 1. Explain

Spawn one read-only subagent that explores and explains in one pass. Give it the user's question and this brief:

> You are writing an architectural explanation for a senior engineer who has never worked in this area. Explore the codebase and write an explanation they could read and walk away with a solid mental model, good enough to start making changes confidently. Cover the entry points, the flow of control and data, who owns which state, and the boundaries. Cite `file:line` for every claim about what the code does. Say what you could not determine from the code. You have read-only access.

Keep the exploration in the subagent (principle-guard-the-context-window). A subsystem walkthrough reads a lot of files, and none of them need to be in the main thread.

## 2. Present

Present the subagent's output. Light edits for clarity, or for context from the conversation, are fine. Do not substantially rewrite it, and do not add claims it did not make.

## Related questions this skill also answers

- **Placement.** "Where should this live", "which package owns this", "is this the right layer". Answer from the existing boundaries and say which rule you are applying, not from taste.
- **Onboarding.** "I am new to this area, what do I need to know". Same brief, with the entry points first.

For *why* the code is shaped this way, run **why**, which reads the record rather than the code. For what a change to it would break, run **blast-radius**. For a plain explanation at a person's pace, run **teach**, which calls both.
