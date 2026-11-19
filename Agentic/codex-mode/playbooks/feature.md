# Feature

**You own the design. Plan, review, verify.** Delegate the implementation and stay in the lead.

1. **Trace every system the feature touches** before sketching. Name the data shape first.
2. **Run architect** for the types, signatures, and module boundaries. A contested or precedent-free design runs **arena** instead of one sketch.
3. **Price it** with **cost-per-request** before implementation, not after. A feature that calls a model, adds a queue, or fans out to a new service ships with its cost per request and the assumption behind the number.
4. **Scaffold before features** (principle-foundational-thinking). Types, migrations, CI wiring, and the verification path land first, in their own commits.
5. **Sequence into verifiable units.** Each unit ends green before the next starts. Deliver in the order that proves the work.
6. **Delegate implementation** with the architect sketch, the fence, and the verification contract in the brief. Review every diff yourself.
7. **Verify on the real thing.** Drive the feature the way a user does, through the project's verification skill where one exists, and capture the evidence.
8. **Gate it.** **comment-psycho** before review, **ai-diff-review** for the risk tier, **nexus-guard** before merge. An LLM-facing feature also needs **llm-evals** and **llm-threat-model**.
9. Open the PR per `opening-a-pr.md`.
