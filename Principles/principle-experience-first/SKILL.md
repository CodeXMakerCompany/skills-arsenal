---
name: principle-experience-first
description: Apply when product, UX, or feature-scope tradeoffs come up. Choose user delight over implementation convenience; ship fewer polished features over more rough ones.
---

# Experience First

When implementation convenience conflicts with the experience, choose the experience.

- Every feature, control, and option must justify itself.
- Ship less, ship better. Three polished features beat ten rough ones.
- Prototype before committing. Design decisions are cheaper in throwaway code than in production.
- Get the details right: transitions, alignment, spacing, feedback, empty states, error states, the loading state nobody designed.
- Tighten the core loop. Every feature serves the central workflow or gets out of the way.

**The user is whoever consumes the work.** For a UI that is the end user. For an API it is the engineer who integrates against it, so a confusing field name is a UX bug. For a library it is the colleague who imports it. For an agent-facing tool it is the agent, and a vague tool description is a UX bug too. The engineer who maintains this next is a user. Weigh their experience the same way and explain impact from their perspective.

**Foundations serve the experience.** Foundational thinking governs the *sequence* of the work. This principle governs the *target*. A beautiful architecture that makes the product worse has failed.
