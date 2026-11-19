---
name: principle-separate-before-serializing-shared-state
description: Apply when concurrent actors might write to the same file, branch, key, row, or state object. Eliminate the sharing first; serialize structurally only when one shared writer is a real invariant.
---

# Separate Before Serializing Shared State

When concurrent actors might write the same file, branch, key, row, or object, first ask whether they need one shared object or are publishing independent facts.

Default to giving each actor its own file, key, branch, prefix, or state directory, and merge only where the state is read. Two workers each writing their own field into one `state.json` is still shared mutation, and so is two agents committing to one branch, two Lambdas incrementing one counter, and two jobs writing one Terraform state.

Only when one shared write target is a real invariant do you serialize access, and then do it structurally: a lock with an owner and a timeout, a single writer, sequential phases, compare-and-swap, a conditional write on a version attribute. Not a comment, not an instruction, not a convention. **Instructions are not concurrency control.**

"We need a lock" is a smell worth checking first. Most of the time the shared write target was an accident of convenience.

**The test:** if two actors run at the exact same millisecond, what is the end state? If you have to reason about interleaving to answer, separate them. If you cannot separate them, make the invariant explicit and prove the mechanism holds (the **statechart** skill model-checks exactly this class of question).
