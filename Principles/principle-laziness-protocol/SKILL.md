---
name: principle-laziness-protocol
description: Apply when refactoring, evaluating diff size, or tempted to add abstractions, layers, or signal threading. Bias toward deletion and the smallest change that solves the problem.
---

# Laziness Protocol

The best change is the one you did not have to make. The second best is the smallest one that solves the problem.

- **Minimize the diff.** Fewer lines beat elegant boilerplate. A 6-line fix that a reviewer can hold in their head beats a 200-line refactor that happens to include it.
- **Consolidate decisions.** Do not repeat the same choice in several places. Put it behind one source of truth and pass the result as a simple value.
- **Resist the layer.** An interface with one implementation, a wrapper with one caller, a config option nobody sets, a factory that makes one thing. Each is a layer the next reader must trace through to learn nothing.
- **Delete rather than deprecate** where no external consumer depends on it (principle-migrate-callers-then-delete-legacy-apis).
- **Do not generalize on the first instance.** Two cases are a coincidence. Three are a pattern.

The honest version of this principle: most of the work in a mature codebase is deciding what not to build. An agent that writes 600 lines where 40 would do has not been productive, it has added 560 lines of maintenance.
