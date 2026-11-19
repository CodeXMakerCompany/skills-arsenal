---
name: tdd
description: Make a bug's broken behavior executable before changing production code, when the test path is cheap and obvious. Use when the user asks for TDD, a failing test, or a regression test, or when a bug has an obvious cheap local test target. Skip when the test path is unclear, expensive, integration-heavy, or not requested.
---

# TDD bug fix

When fixing a bug with a clear, cheap test path, make the broken behavior executable before changing production code. The goal is a focused regression test that fails before the fix and passes after it.

Do not force a test when it would be impractical. If the available test needs broad harness setup, brittle mocks, slow end-to-end infrastructure, production-only state, vague reproduction steps, or large unrelated fixture churn, skip the new test and use the closest useful verification instead.

## Workflow

1. **Understand the bug.** The intended behavior, the current behavior, the affected path, and the smallest observable reproduction.
2. **Choose the narrowest executable check.** Prefer the test type already used for that code path. If no practical path is obvious, do not invent one to satisfy the workflow.
3. **Write the failing test first.** The smallest focused test that would have caught this bug. It encodes the intended behavior, never the current implementation.
4. **Run it before fixing.** Confirm it fails *for the intended reason*. A test that passes, or fails for an unrelated reason, means the test or the reproduction is wrong, and fixing production code now would be fixing the wrong thing.
5. **Fix the bug.** The smallest production change that satisfies the intended behavior while preserving nearby contracts.
6. **Rerun.** Confirm it passes, and that nothing nearby broke.

## If a failing test is impractical

Use the closest executable regression check: a targeted script, a curl against the real endpoint, a browser automation, a snapshot comparison, a log assertion, a focused integration check.

**Prefer no new test over a bad test.** A bad test mostly asserts on mocks, encodes implementation details, depends on timing or global state, needs expensive infrastructure for a small fix, or would be deleted right after proving the fix.

## Guardrails

- Never change a test to match a wrong implementation.
- Never weaken an existing assertion unless the expected behavior genuinely changed, and then say why.
- Keep the regression test focused on this bug. No fixture churn, no unrelated coverage expansion.
- If the bug is flaky, make the test deterministic where possible and say which signal you locked down.
- If the bug exposes a broader class, land the focused regression first, then consider sibling coverage.

## Final response

Report the evidence, not the outcome.

- The failing-before test or check, and the failure it produced.
- The passing-after run, and any nearby validation.
- If failing-before evidence was impossible, why, and the closest regression check you used instead.
