---
name: clarity
description: Hard gate on ambiguous requirements. Extract every requirement as a testable statement, and when one is ambiguous, inconsistent, or missing, stop execution and get it resolved in writing with the owner before any code is written. Use for /clarity, "check these requirements", "is this ticket clear", "está ambiguo", or at the start of any development task handed over as a spec, ticket, or request.
---

# Clarity

**Building the wrong thing correctly is the most expensive outcome in software.** It passes review, passes tests, ships, and then has to be undone along with everything built on top of it. The cost of asking is one message.

So this skill blocks. When a requirement is ambiguous, inconsistent, or missing, execution stops until the owner resolves it in writing.

---

## The line this skill draws

This arsenal also holds [`principle-never-block-on-the-human`](../../Principles/principle-never-block-on-the-human/SKILL.md), which says reversible work proceeds without asking. Both are right, because they are about different things, and knowing which you are facing is the whole skill.

| Ambiguity about | Example | What you do |
|---|---|---|
| **How to build it** | Which library, which pattern, where the file goes, how to shape the types, whether to extract a function | **Decide and proceed.** Reversible, yours to own, and asking wastes the owner's attention. |
| **What to build** | What the system must do, for whom, what counts as correct, what happens on failure, what the money or data rule is | **Block.** Not reversible by a refactor, and not yours to decide. |

The test: **if I guess wrong, is the fix a refactor or a rewrite?** A refactor means proceed. A rewrite, a data migration, a conversation with a customer, or a compliance problem means block.

A second test that catches the rest: **could two competent engineers read this and build different products?** If yes, it is a requirement problem, whatever it looks like.

---

## 1. Extract the requirements

Read every source: the ticket, the PRD, the designs, the thread where it was asked for, the acceptance criteria, the conversation in this session. Then rewrite each requirement as **one testable statement**.

Testable means someone could run it and say pass or fail. "The export should be fast" is not a requirement. "The export of 60k rows completes in under 5 seconds at p95" is.

List them numbered. That list is the artifact everything else hangs off, and writing it is often where the ambiguity becomes obvious.

## 2. Classify each one

| Class | Meaning | Action |
|---|---|---|
| **clear** | Testable, single reading, owner-confirmed or self-evident | Proceed |
| **ambiguous** | Two or more readings a competent engineer could hold | **Block** |
| **inconsistent** | Two sources disagree | **Block**, and never silently pick the newer one |
| **missing** | A behavior the feature cannot work without, and nobody specified | **Block** |
| **unverifiable** | Stated but no way to tell whether it is met | **Block**, and ask for the threshold |
| **assumed** | Nobody said it, but it is obvious and cheap to reverse | Proceed, state the assumption in writing |

## 3. The ambiguity checklist

Run this, because the gaps are predictable and the same ones recur:

- **Unquantified adjective.** Fast, secure, soon, scalable, simple, robust, user-friendly. Every one needs a number or a named condition.
- **Undefined term.** A domain noun used as if it were obvious: "active user", "closed account", "verified", "delivered". Ask what it is in the data.
- **No failure behavior.** What happens when the payment declines, the upstream times out, the file is malformed, the user is offline, the quota is hit. Unspecified failure behavior is the most common missing requirement.
- **No actor or permission.** Who can do this, who can see it, who gets notified, what a user sees about another tenant.
- **Missing edge cases.** Zero, one, empty, maximum, negative, duplicate, concurrent, retried.
- **Unstated units.** Currency, timezone, locale, cents against dollars, inclusive against exclusive dates, UTC against local.
- **Data rules unstated.** What is retained and for how long, what is PII, what can be logged, what crosses a border, what must be deletable.
- **Implicit acceptance criteria.** "Like the other screen" and "the way Stripe does it" are references, not requirements. Pin what specifically transfers.
- **Conflicting sources.** The ticket, the designs, and what the stakeholder said in the call. **This is the one that must never be resolved silently**, because picking one makes you the author of a decision you cannot defend.
- **Scope with no edge.** "And anything else needed." Ask what is explicitly out.

## 4. Write the clarification, not a question

**Never send "can you clarify the requirements?"** It costs the owner a thinking session and comes back vague.

Send a numbered list where each item is answerable in one line:

> **3. What counts as an "active" subscriber for the monthly report?**
> The ticket says active subscribers. The data has three candidate states: `trialing`, `active`, `past_due`.
> - **Reading A:** `active` only. The report shows 4,100.
> - **Reading B:** `active` + `trialing`. The report shows 5,350.
> - **Reading C:** `active` + `trialing` + `past_due`. The report shows 5,900.
>
> **My pick: B**, because the revenue dashboard already counts trials this way and two reports disagreeing is worse than either definition.
> **If it is wrong:** the number in a board deck is off by 23%, and the fix is a one-line query change, but the deck has already gone out.

Each item carries: the quoted ambiguity, the readings with their real consequence, **your pick with a reason**, and what the wrong guess costs. A leader can answer that in one word. That is the point.

## 5. Route each question to the right owner

Blocking on the wrong person is as slow as not asking.

| Question about | Owner |
|---|---|
| What the product should do, who it is for, which reading is intended | Product owner |
| Which system owns it, what the contract is, what we are allowed to break | Tech lead or architect |
| Retention, PII, access, auditability, what can be logged | Security, privacy, or legal |
| Exact interaction, states, copy | Designer |
| Whether the number is right, what the rule is | The person who will read the output |

Ask all of them at once, not serially. A chain of three sequential clarifications is three days.

## 6. What you do while blocked

**Blocked means blocked on the ambiguous requirement, not idle.** Stopping entirely wastes the window.

- Do every part of the task that does not depend on the answer: the scaffolding, the types that are settled, the tests for the clear requirements, the harness.
- Build the thing that makes the answer cheap: the query that produces all three numbers, the prototype of both readings, the screenshot of each option. **Often this converts a blocking question into a one-second decision**, and sometimes it answers it outright, at which point you unblock yourself and say so.
- Never build on the ambiguous branch, not even "to save time". That is the work you will throw away.

## 7. Resume only on a written answer

- **The answer goes in the source of truth**, the ticket or the spec, not a DM and not only this session's history. If the answer came verbally, you write it into the ticket yourself and confirm it back in one line.
- **An answer that is itself ambiguous is not an answer.** Re-ask once, narrower, with the readings.
- **Silence is not consent.** If nobody answers and the work must move, say in writing which reading you are proceeding on, what it cost to not know, and that it is reversible or not. Then proceed only if it is reversible. If it is not, it stays blocked and you escalate.
- **Update the requirement list** and restate the now-clear statement before writing code.

## 8. Report

```
CLARITY — <task>

Requirements extracted: 11
  clear 7 · ambiguous 2 · inconsistent 1 · missing 1

BLOCKED on 4 items, routed to 2 owners:
  #3  "active subscriber" undefined           → product   (3 readings, 23% delta)
  #6  no behavior on payment decline          → product
  #7  ticket says 30 days, designs say 90     → product   (sources conflict)
  #9  retention for the exported PII          → security

Proceeding meanwhile: the schema, the 7 clear requirements, and a query
that produces all three numbers for #3.

Not started: the report itself. It depends on #3 and #7.
```

A task that passes with zero blocks is a good outcome and worth saying plainly, because it means the spec was actually written well and the author should hear that.
