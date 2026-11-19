---
name: create-formal-verification-skill
description: Generate a project-local skill that formally verifies the code where a bug costs the most and tests reach the least, in any language, with whichever verification tool fits. Use for /create-formal-verification-skill, "model-check this race", "prove this invariant", or when concurrency, retries, state machines, parsers, or money need more than tests.
---

# Create a formal verification skill

A test checks the cases someone thought to write. Formal verification checks every case in a stated scope: every order of steps in a model, every input up to a bound, or every input.

This skill finds the part of the repo where that matters most, verifies one property of it, and leaves a project-local skill that lets the next agent check a change against that property. Write that skill for an agent reading it cold, mid-change. The user must be able to trust the result and act on it without learning the verification language.

## Choose the target from the code

Answer from the codebase and ask the user only what you cannot observe. If they named an area or a bug, start there.

A good target is a promise the code makes, where a break harms users and tests rarely reach the case that breaks it. Choose the strongest such target in the repo, not the easiest to verify.

The usual high-value targets: a payment or ledger path where double-charging is possible, an idempotency key whose window can be violated, a retry and timeout interaction that can duplicate work, a lease or lock whose holder can change mid-operation, a state machine whose events can arrive out of order, a parser facing hostile input, a queue consumer under at-least-once delivery.

## Let the question choose the tool

Pick the tool that answers the question at the lowest cost.

- **Whether events can happen in a bad order** usually suits a model checker over a small model of the design. TLA+ with TLC is the default for that, in any language, and the **statechart** skill reads its output.
- **Whether the code itself behaves for every input** (memory safety, overflow, a data-structure invariant) usually suits a verifier that runs on the code.
- **Where no verifier runs on this language**, say so, and test the real code with generated inputs (property-based testing) rather than a hand model of the function.
- **A property that must hold at every size**, where a bound is not enough, can need a proof assistant. Say so plainly rather than pretending a bound covers it.

Prefer a tool the repo's developers can install and run, and tell the user why you chose it.

## What makes it good

- **True to the code.** Every part of the model points to code a reviewer can open. What the verification treats as one indivisible step is one indivisible step in the code. Names come from this repo.
- **Able to fail.** A check you have never seen fail proves nothing. Show each property failing on a broken variant of the code it guards: a removed check, a reordered step.
- **Findings stay findings.** When the current code breaks the property, report it with the counterexample in the code's terms. Do not weaken the property or the model until it passes, and do not change product code unless the user asks.
- **Honest about scope.** Say what is verified, under which bounds and assumptions, and what is left out. A pass covers the model or the bound, never the whole system.
- **Readable without the tool.** State the property and the harm in one plain sentence each. Tell a counterexample as a short sequence of steps in the code's words.
- **Cheap to rerun.** One command, a pinned tool version, and a run short enough that the next agent will actually use it.
- **Kept in step with the code.** Record which files and functions each check covers, and the commit at which you last confirmed the verification describes them.

## Generate the verify skill

Write a project-local skill with frontmatter naming the area and when to use it. From the skill alone, the next agent must be able to tell whether a change touches the verified code, run the check, tell a real bug from a modeling error, and update the verification when a change is intended.

Put the coverage record and the sync commit in the skill, and tell the next agent to move the sync commit forward only after confirming the verification still describes the code. Use this repo's real commands, paths, and nouns. Leave no placeholders.

## Prove it before you hand off

Follow the generated skill once, as the next agent would, on a scratch change that breaks the property in the real code. It must catch the break. Then drop the scratch change and confirm the check is back where it started.

**A verify skill that was never run is a draft.** If the skill misses the break, fix the skill or the verification, never the scratch change.

## Hand off

Tell the user what you verified, which tool and why, the bounds, what the check found in plain words, how to run it, and what it does not cover. Suggest a second target only if you found a close one. Point them at **maintain-formal-verification-skill** for bringing it back in line after changes that skipped it.
