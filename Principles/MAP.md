# Principles

Twenty-four leaves. Each one is a rule that changes a decision inside other work.

**These are cited, not run.** You do not "do" a principle. You name it and the choice it changed, and `codex-mode` requires that in the reply. Read a leaf in full before citing it.

## Core: what to build and how much

| Apply when | Principle |
|---|---|
| Sizing a diff, tempted to add a layer | [laziness-protocol](principle-laziness-protocol/SKILL.md) |
| Before writing logic: types, structures, sequence | [foundational-thinking](principle-foundational-thinking/SKILL.md) |
| Integrating a new requirement into an old design | [redesign-from-first-principles](principle-redesign-from-first-principles/SKILL.md) |
| Two fixes sharing one premise failed the same gate | [attack-the-premise](principle-attack-the-premise/SKILL.md) |
| Sequencing an addition, refactor or rewrite | [subtract-before-you-add](principle-subtract-before-you-add/SKILL.md) |
| Code that is hard to trace | [minimize-reader-load](principle-minimize-reader-load/SKILL.md) |
| A planned migration with phase boundaries | [outcome-oriented-execution](principle-outcome-oriented-execution/SKILL.md) |
| A product, UX or scope tradeoff | [experience-first](principle-experience-first/SKILL.md) |
| A decision with no precedent in the codebase | [exhaust-the-design-space](principle-exhaust-the-design-space/SKILL.md) |
| Any non-trivial work | [build-the-lever](principle-build-the-lever/SKILL.md) |

## Architecture: where things live

| Apply when | Principle |
|---|---|
| Stateful logic, or branching that repeats a shape | [model-the-domain](principle-model-the-domain/SKILL.md) |
| Wiring validation, errors, framework adapters | [boundary-discipline](principle-boundary-discipline/SKILL.md) |
| Designing types or a signature | [type-system-discipline](principle-type-system-discipline/SKILL.md) |
| Handlers and loops that run amid retries and crashes | [make-operations-idempotent](principle-make-operations-idempotent/SKILL.md) |
| A new internal API while old callers exist | [migrate-callers-then-delete-legacy-apis](principle-migrate-callers-then-delete-legacy-apis/SKILL.md) |
| Concurrent actors might write the same thing | [separate-before-serializing-shared-state](principle-separate-before-serializing-shared-state/SKILL.md) |

## Verification: how you know

| Apply when | Principle |
|---|---|
| Before declaring done | [prove-it-works](principle-prove-it-works/SKILL.md) |
| Debugging | [fix-root-causes](principle-fix-root-causes/SKILL.md) |
| Multi-step work, and how you stack commits | [sequence-verifiable-units](principle-sequence-verifiable-units/SKILL.md) |
| Writing, changing or keeping a test | [test-behavior-not-implementation](principle-test-behavior-not-implementation/SKILL.md) |
| Before you measure, and before you trust a number | [explain-the-number](principle-explain-the-number/SKILL.md) |

## Delegation and meta

| Apply when | Principle |
|---|---|
| Context filling with payloads, planning a fan-out | [guard-the-context-window](principle-guard-the-context-window/SKILL.md) |
| Tempted to ask "should I?" on reversible work | [never-block-on-the-human](principle-never-block-on-the-human/SKILL.md) |
| You are about to write the same instruction twice | [encode-lessons-in-structure](principle-encode-lessons-in-structure/SKILL.md) |

## The four that fire most often

If you only internalize a handful: [`principle-prove-it-works`](principle-prove-it-works/SKILL.md) (nothing is done until it ran), [`principle-fix-root-causes`](principle-fix-root-causes/SKILL.md) (the guard is not the fix), [`principle-type-system-discipline`](principle-type-system-discipline/SKILL.md) (the compiler holds the rule, the comment does not), [`principle-build-the-lever`](principle-build-the-lever/SKILL.md) (the tool is the artifact a reviewer reruns).

## Where they lead

A principle that keeps firing is a signal to leave the leaf behind and build something: [`principle-encode-lessons-in-structure`](principle-encode-lessons-in-structure/SKILL.md) routes to [`correct`](../Meta/correct/SKILL.md), which turns the rule into a lint, a type, or a CI gate. A principle you had to cite three times in one review is a missing check.
