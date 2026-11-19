---
name: architect
description: Sketch types, signatures, module boundaries and the cost per request before any code, then stay in the loop while implementation fills it in. Use for /architect, "architect this", "design this", "diseña esto", or non-trivial work where jumping to code would lock in the wrong shape.
---

# Architect

Before writing code, trace every system the change touches. Then sketch two different shapes for it and pick deliberately. One sketch is not a design, it is the first idea.

## The sketch

For each shape, write down:

- **The data.** The core types, with illegal states unrepresentable and semantic primitives branded. Name the shape before the behavior (principle-foundational-thinking).
- **The signatures.** What each boundary accepts and returns. External data is `unknown` until a parse function at the boundary turns it into a domain type.
- **The modules.** Who owns which state, and what a caller has to know to use it.
- **The cost per request.** Model calls, round trips, queue hops, storage writes. Run **cost-per-request** on each shape. Two designs that look equivalent on a whiteboard routinely differ 10x on the bill, and that difference is a design input, not a surprise for month end.

## Picking

Pick the shape where each piece of state has one owner, each task has one supported way to do it, and callers need to know least. When two feel tied, take the smaller API and the cleaner boundary (principle-laziness-protocol).

If workarounds repeat across the sketch, the design is wrong. Redesign as if the new requirement had been foundational from day one (principle-redesign-from-first-principles) rather than patching around it.

For a large, contested, or precedent-free design, run **arena** instead of sketching alone. For a decision a run could settle, prototype it per the Prototype playbook rather than arguing it.

## Staying in the loop

Hand the sketch to implementation as the contract, with the fence and the verification bar. Then review the diff against the sketch yourself. A sketch nobody checked against is a wish.

**Reply:** both shapes, the pick and why, the cost per request of the picked shape with its assumption, and what the sketch deliberately leaves open.
