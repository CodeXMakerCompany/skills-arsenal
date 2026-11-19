---
name: principle-sequence-verifiable-units
description: Apply to multi-step work (sweeps, migrations, runs of similar edits) and to how you stack commits and PRs. Break work into small units that each end in a verifiable state, check each before the next, and order delivery so the sequence proves itself to a reviewer.
---

# Sequence Verifiable Units

Order work as small units that each end in a state you can check, and do not advance until the current one is green.

In a sweep, migration, or run of similar edits, each unit is a bracket: known-good state, one change, run the check, proceed. Run the per-unit check even when a tool does the edits, because a codemod that works on file 1 can produce nonsense on file 17.

**Deliver in the order that proves the work:**

- the failing test, then the fix,
- the baseline, then the treatment,
- the deletion, then the reshape,
- the harness, then the thing it measures,
- the types, then the logic that depends on them.

Each commit lands on its own and is green on its own. A PR of 14 commits where only the last one compiles is one commit wearing a costume, and it cannot be bisected or reverted.

**The reviewer test:** can someone read your commits in order and watch the work prove itself, without taking anything on faith? If the proof only exists at the end, the sequence was wrong.

Batching the checks to the end feels faster and is slower. The failure you find at unit 17 is a failure you now have to locate across 17 changes.
