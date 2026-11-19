---
name: principle-redesign-from-first-principles
description: Apply when integrating a new requirement into an existing design. Redesign as if the requirement had been foundational from the start, then deliver it incrementally.
---

# Redesign From First Principles

When integrating a change, do not bolt it onto the existing design. Redesign as if the requirement had been a foundational assumption from day one.

1. Read every affected file and understand the current design, including why it is shaped that way (the **why** skill answers that from the record).
2. Ask: if we were writing this from scratch with this requirement included, what would we build?
3. Propagate the change through every reference: types, call sites, tests, docs, examples, the rationale section that explains the old shape.
4. Think about the whole redesign, then deliver it incrementally (principle-sequence-verifiable-units).

**The signal that you skipped this:** the new requirement needs a flag to tell it apart from the old behavior, or a special case that mentions the feature by name, or a second code path that does almost the same thing.

**The limit:** this is a method for preserving option value, not a license to rewrite the system every sprint. If the redesign is larger than the requirement justifies, write it down as the target, ship the smallest step toward it, and say what the step does not fix. A redesign you cannot land is a design document.
