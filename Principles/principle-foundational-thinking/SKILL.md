---
name: principle-foundational-thinking
description: Apply before writing logic: choosing core types and data structures, sequencing scaffold-versus-feature work, asking what concurrent actors share. Get the data structures right so downstream code becomes obvious.
---

# Foundational Thinking

Get the data shape right before writing logic. The right structure deletes branches; the wrong one multiplies them.

- **Define the core types early.** Trace every access pattern, then choose structures that match the dominant paths. A list you always search by id wants a map. A set of states you branch on wants a discriminated union. A sequence you always process in order wants a queue, not an array someone sorts twice.
- **DRY the structure, not every line.** Two functions that look alike and mean different things should stay apart.
- **Before sharing state between actors, ask what happens if another writes it concurrently.** If the answer is not "nothing", isolate (principle-separate-before-serializing-shared-state).
- **Scaffold first.** Whatever helps every later phase goes first, after removing dead code: the types, the migrations, the CI wiring, the test harness, the verification path. Building the feature before the harness means measuring it from memory.
- **Keep commits small and single-purpose.** A commit that moves files and changes behavior cannot be reviewed or reverted.

The test: once the types are right, does the function body become obvious? If the logic still needs a diagram, the shape is still wrong.
