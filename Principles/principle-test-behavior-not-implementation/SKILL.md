---
name: principle-test-behavior-not-implementation
description: Apply when you write, change, or keep a test. Assert what the code's users can observe, so the test fails when that behavior breaks and keeps passing when only the internals change.
---

# Test Behavior, Not Implementation

A test is a claim about what users of the code can observe through its interface: return values, errors, state they can read back, and effects on outside systems. Private helpers, internal call order, and intermediate data are implementation.

Judge every test against two imagined edits:

- **Break the behavior** (a wrong value, a skipped or doubled effect). If the test still passes, it proves nothing. The usual causes are a loose assertion, an expected value computed by the code under test, and an assertion on data the test built itself.
- **Change the internals** and keep every observable result identical. If the test fails, it is pinned to the implementation.

Keep the test that catches the first edit and survives the second. Rewrite or delete the rest.

- Drive the code through its public interface with a concrete input, and derive the expected value from the requirement, not from what the code currently returns.
- **What an external service receives is behavior.** A call to an internal helper is not. Asserting that the right message hit the queue is a behavior test; asserting that `buildPayload` was called is not.
- Pair "this never happens" with a case where it does happen.
- Assert the error type callers branch on, not the message text.
- A test that mostly asserts on mocks tests your mocks. Where a real dependency can run locally, run it.
