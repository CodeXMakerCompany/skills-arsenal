---
name: principle-encode-lessons-in-structure
description: Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction. Encode the rule as a type, lint, runtime check, CI gate, or script instead of more prose.
---

# Encode Lessons in Structure

The second time you write an instruction, the instruction is the symptom. Encode the rule instead.

The ladder, highest first:

1. **Architecture.** Make the wrong thing unreachable. One owner per piece of state, one supported way per task, internals that fail to import.
2. **Types.** Make the bad state impossible to write.
3. **A lint or CI check whose error names the fix.** Not "invalid pattern" but "use `parseInvoice()` from `domain/invoice.ts` instead of casting the row".
4. **A test** that fails on the real past mistake.
5. **Prose, last**, and only for judgment calls. Nothing fails when an agent skips prose.

**Corollary:** if the fix is structural, use only the structural fix. Keeping the instruction next to the lint is clutter that rots.

If the lesson genuinely needs judgment and cannot be encoded, make the instruction more prominent and attach an example of the failure mode. An abstract rule with no example gets read and ignored.

When the operator corrects the same thing twice, that is the trigger. Route it to the **correct** skill and fix the class, not the instance.
