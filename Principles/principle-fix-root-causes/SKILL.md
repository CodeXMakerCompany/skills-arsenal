---
name: principle-fix-root-causes
description: Apply when debugging. Trace each symptom back to the first place the system went wrong and fix it there. A guard is a fix only when the state it handles is legitimate.
---

# Fix Root Causes

Fix the fault, not the place where it surfaced. The root cause is the first place the system did something it should not, or failed to handle a state it should.

- **Reproduce first.** Then ask why until the answer is a wrong decision in the code. When stuck, instrument and read the actual state. Reasoning about what the code should hold is how you fix the wrong thing.
- **Ask whether the triggering state is legitimate.** If it is, handle it where the code broke. If it should never exist, a check there hides the bug, so find what produced it. Guards, retries, swallowed errors, clamped values, defaulted nulls, and discarded state are the usual ways to hide a bug and the usual way a bug comes back a month later wearing a different stack trace.
- **Fix the pattern, not the instance.** Find every place with the same fault. Say which ones you fixed and which you listed.
- **If the deciding fact took a deep dig**, propose the cheap always-on signal that would have shown it at first look: a structured log field, a metric dimension, a trace attribute, an assertion in development.

A retry around a call that fails for a deterministic reason is not resilience. It is three times the latency and the same bug.
