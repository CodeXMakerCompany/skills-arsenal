# Refactoring

**You own the contract. The structure changes. The behavior does not.**

Distinct from Feature, which adds behavior, and Bug fix, which corrects it. If the cleanup reveals a missing feature or a real bug, split it out and ship the structural change first against the pinned contract. Large or cross-cutting structural work belongs to **figure-it-out**.

1. **Pin the contract.** Write down what callers can observe and must keep observing: signatures, response bodies, emitted events, DB shape, wire format. That written contract is the spec for the whole run.
2. **Capture the baseline.** The tests that must stay green, and for a UI the screenshots that must stay identical. No baseline, no parity claim.
3. **Subtract first** (principle-subtract-before-you-add). Delete dead code, redundant validators, and stubs before reshaping what is left. That deletion is its own commit.
4. **Migrate callers and delete the old API in the same wave** (principle-migrate-callers-then-delete-legacy-apis). No compatibility shim survives the PR unless an external consumer needs it, and then say who.
5. **One unit at a time, each ending green.** A refactor that is red in the middle for twenty files is not reviewable.
6. **Fix the tests that pin internals.** A test that breaks when only the internals change was testing the implementation. Rewrite it against observable behavior, do not loosen it to pass.
7. **Prove the behavior did not move.** The pinned contract still holds, the baseline still matches, and you show both. A refactor PR whose diff includes a behavior change has failed this playbook.
