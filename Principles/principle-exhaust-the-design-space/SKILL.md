---
name: principle-exhaust-the-design-space
description: Apply when facing an interaction, architecture, or prompt design decision with no precedent in the codebase. Build two or three competing prototypes and compare side by side before committing.
---

# Exhaust the Design Space

With no precedent to copy, one attempt is the first idea, not the best one. Build two or three and compare.

This applies to more than UI. A retrieval strategy, an agent's tool surface, a prompt structure, a queue topology, and an error-handling shape are all design decisions where the first idea is rarely the right one and a cheap run settles it.

- **Make them genuinely different**, not three variations on the same shape. Two prototypes that differ in a parameter teach you about the parameter.
- **Compare side by side on the same input.** Same data, same traffic, same eval set. A comparison across different inputs compares the inputs.
- **Record what each one actually did**, not how it felt: the latency, the output quality on the set, the token count, the cost per request, the diff size, the screenshot.
- **Throw the losers away.** Keeping two of them "for later" is how a codebase ends up with three ways to do one thing.

It also applies where experience depends on feel rather than logic. There, the prototype is the only honest evidence, because nobody can predict feel from a spec.

Where the decision is large or contested, run **arena** so different models produce the candidates.
