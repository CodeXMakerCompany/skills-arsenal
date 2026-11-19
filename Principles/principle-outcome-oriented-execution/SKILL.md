---
name: principle-outcome-oriented-execution
description: Apply during planned rewrites and migrations with explicit phase boundaries. Converge on the target architecture; do not preserve smooth intermediate states with throwaway compatibility code.
---

# Outcome-Oriented Execution

Optimize for the intended, verifiable end state rather than for a smooth path to it.

Keeping every intermediate step fully stable creates temporary compatibility code, and temporary compatibility code becomes long-lived debt. Converge on the target architecture and prove correctness at explicit verification boundaries instead.

**Core rule:**

- Prioritize end-state integrity over transitional stability.
- Intermediate breakage is acceptable when it is planned, scoped, and reversible.

**Guardrails:**

- Use this for planned rewrites and migrations with explicit phase boundaries, not as a license to leave trunk broken.
- Declare up front where temporary breakage is acceptable, and for how long.
- Keep high-signal checks running on the areas you are actively touching.
- Require full static and runtime verification at plan completion, not phase by phase.

**Where this inverts:** anything already serving production traffic. A database migration, an auth change, or a public API cannot take planned breakage, so those phases get the opposite treatment: expand, migrate, contract, each step independently safe and reversible. Say which regime each phase is in before you start.
