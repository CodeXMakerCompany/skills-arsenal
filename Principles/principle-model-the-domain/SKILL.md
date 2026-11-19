---
name: principle-model-the-domain
description: Apply when writing stateful logic, or when code branches a lot or repeats a shape assumption across files. Encode the domain in a structure instead of scattering it across conditionals.
---

# Model the Domain

Encode the domain in a data structure instead of scattering it across conditionals. The right structure makes invalid states unrepresentable and deletes branches.

Reach for:

- a **state machine** instead of scattered booleans or phase checks,
- a **typed model** instead of loose parameters,
- a **discriminated union** instead of an optional-field bag,
- a **map, registry, or table** instead of a branch chain spread across files,
- a **reducer** instead of ad hoc mutations,
- an **index, queue, or normalized collection** where the access pattern calls for it.

**The sign you skipped this:** a feature that grows an if/else chain by one more branch, or a second boolean that must stay in sync with the first. `isLoading` plus `isError` plus `data` can represent loading-and-error-at-once, a state that cannot happen and that someone will eventually render.

**Do not force it.** Keep boring code when the shape is clear, local, and unlikely to grow. Distrust an abstraction that adds indirection without removing branches or invalid states.

For phase and mode logic, the **state-machine-architect** skill has the transition-table method. For a flow where the order of events is the risk, **statechart** model-checks it.
