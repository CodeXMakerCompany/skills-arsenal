---
name: principle-subtract-before-you-add
description: Apply when sequencing an addition, refactor, or rewrite. Remove dead code, redundant validators, and stub references first, then build on the simpler base.
---

# Subtract Before You Add

When evolving a system, remove complexity first, then build. Default to subtraction.

- **Sequence removal before construction.** The deletion is its own commit, and it lands first. Building on top of dead code means the dead code now has a dependent.
- **Cut before you polish.** Get to the minimum before investing in quality.
- **Design for observed usage, not speculative edge cases.** No validator, parser, or guard beyond what the spec demands and the boundary requires.
- **Delete rather than stub.** When a reference, doc, or example has no novel content, remove it instead of leaving a placeholder.
- **Simplify prompts the same way.** A system prompt with three overlapping instructions about tone is worse than one, and it costs input tokens on every single request.

Make simplification a continual investment: leave the design slightly simpler and more capable behind the same or smaller surface than you found it.

**The honest check before adding anything:** what would have to be true for this not to be needed? If the answer is "the thing I am about to delete anyway", delete it first and see whether the addition is still necessary. Often it is not.
