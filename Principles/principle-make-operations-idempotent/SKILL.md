---
name: principle-make-operations-idempotent
description: Apply when designing commands, lifecycle steps, handlers, or processing loops that run amid crashes, restarts, retries, and at-least-once delivery. Converge to the same end state regardless of partial prior runs.
---

# Make Operations Idempotent

Design every state-changing operation to converge to the correct state however many times it runs and wherever the previous run stopped.

This is not optional in an event-driven system. SQS, SNS, EventBridge, webhooks, and every retrying client deliver at least once, which means your handler will see the same message twice in production. A handler that is correct only on the first delivery is a bug waiting for a retry.

- **Derive each step from the state that exists**, not from what the previous run meant to do. Read the current state, compare it to the goal, apply only the difference.
- **Carry an idempotency key** where the operation has an external effect: charge, send, provision, publish. The key comes from the event, not from the clock or a random value.
- **Make leftovers recognizable as stale.** A lock, a temporary file, a half-written record, a claimed job must be identifiable by the next run from evidence that holds wherever the previous run stopped. Write to a temporary path and rename it into place.
- **Prefer upsert over insert, and declarative over imperative.** This is why Terraform's model works and a sequence of `aws` CLI calls does not.

The test: what happens if this runs twice? What if the previous run crashed at every possible point? If the answer depends on what was left behind, add a reconciliation step.
