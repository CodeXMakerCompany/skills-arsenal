# Bug fix

**You own this task. Plan, review, verify.** Delegate the investigation and the fix, stay in the lead.

Be scientific. Every shipped line traces to runtime evidence. A belt-and-suspenders change that "might help" is a hypothesis, not a fix, and it does not ship. When evidence refutes a hypothesis, revert what it motivated.

1. **Reproduce before you theorize.** A failing command, a request that returns the wrong body, a log line with a trace ID. No repro, no fix: say so and go gather one. For a production-only bug, pull the real signal first (CloudWatch Logs Insights, the trace, the Langfuse span) with the **aws-log-insights** skill where the logs are on AWS.
2. **Trace to the first wrong decision** (principle-fix-root-causes). Ask why until the answer is a line that decided wrongly. Instrument and read the real state rather than reasoning about what the code should hold.
3. **Decide whether the triggering state is legitimate.** If it is, handle it where the code broke. If it should never exist, a guard there hides the bug, so find what produced it.
4. **Write the failing test first** where the test path is cheap and obvious, per the **tdd** skill. Where it is not, name the executable check you will use instead and why a test would cost more than it proves.
5. **Ship the smallest change the evidence justifies.** Then find every other place with the same fault and say whether you fixed them or listed them.
6. **Prove it.** The test that failed now passes, the repro command now returns the right thing, and you paste both. Then **blast-radius** if the fix touches a shared path.
7. **Close the loop.** If the deciding fact took a deep dig, propose the always-on signal that would have shown it in the first minute. If an agent could repeat this mistake, route it to **correct**.
