---
name: principle-minimize-reader-load
description: Apply when reviewing or shaping code that is hard to trace. Count the layers between question and answer, and the hidden state the reader must hold; collapse one-caller wrappers and shrink mutable scope.
---

# Minimize Reader Load

Reader load is the work someone must do to understand code. It has two independent axes: **layers** to trace between the question and the answer, and **hidden or mutable state** to hold in their head. Guard both.

- **Collapse layers that only forward.** A wrapper with one caller, an adapter with no second implementation, a pass-through method, a service class whose every method calls one repository method. Inline them.
- **Shrink state scope.** Returns over mutations, locals over fields, fields over module state, module state over globals. Derive instead of syncing two things that must agree.
- **Name an invariant once, at the boundary**, not in every consumer. Five functions each checking the same precondition means the type is wrong.
- **One name per thing.** A value called `user` here, `account` there, and `profile` in the third place costs the reader a translation table.

**The test:** can a new reader answer "where does X come from?" and "what can change X?" in under 30 seconds? If not, cut layers or cut state.

The reader includes the next agent. An agent sees only the files it opened and copies the nearest example, so a confusing shape does not just slow it down, it propagates.
