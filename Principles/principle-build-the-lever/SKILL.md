---
name: principle-build-the-lever
description: Apply to any non-trivial work, not just bulk work: edits, migrations, analyses, checks. Build the tool that does it or proves it (a codemod, script, generator, or a skill your subagents follow) instead of working by hand. The tool is the artifact a reviewer can rerun.
---

# Build the Lever

When the work is not trivial, build the tool that does it rather than doing it by hand. The bar is triviality, not repetition. Skip the tool only for a couple of obvious edits.

- **Do the first unit by hand, then build the tool and prove it** by rerunning it on that unit and getting the same result. Make it safe to rerun (principle-make-operations-idempotent).
- **A deterministic tool beats fan-out.** Ten agents doing the same mechanical edit is ten chances to do it ten ways. When you do fan out, write the recipe, the verification contract, and the fences as one brief the workers follow and cannot edit.
- **Applying this produces a file.** No script, codemod, generator, or worker brief in the diff means you did not apply it. Commit it when the work outlives the session.
- **Build the smallest thing that does or proves the job**, never a framework. A 20-line script with no dependencies beats a configurable tool nobody will run twice.

The reviewer's question is not "did you do this correctly 41 times". It is "can I rerun this and get the same answer". Only the tool answers that.
