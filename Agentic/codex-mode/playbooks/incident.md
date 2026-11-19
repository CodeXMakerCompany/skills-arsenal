# Incident

**You own the clock and the record. Stop the bleeding, then find the cause.** Mitigation and diagnosis are separate steps, in that order.

1. **Say what is broken, for whom, since when.** The user-visible symptom, the blast radius, the start time from the first bad signal, not from when someone noticed.
2. **Mitigate before you understand.** Roll back, disable the flag, drain the queue, raise the limit, fail over. A mitigation that is reversible and reduces harm does not wait for a root cause. Propose the irreversible one and get the human's yes.
3. **Preserve the evidence first.** Capture the logs, the traces, the metrics window, and the failing payloads before a restart or a rollback erases them. A restart that loses the only copy of the signal turns an incident into a mystery.
4. **One owner, one timeline.** Append every action with its timestamp and its effect, through **show-me-your-work**. The timeline is what the postmortem is written from and what tells you whether your mitigation did anything.
5. **Then diagnose** under `bug-fix.md`, from the preserved signal. Trace to the first wrong decision. A mitigation is not a fix and the incident is not closed by it.
6. **Close with the facts, blameless.** What happened, the timeline, the user impact with a number, the root cause, why the existing monitoring did not catch it, and the one change that makes this class of failure impossible or visible in the first minute. Route that change to **correct** or **encode-lessons-in-structure** so it becomes a check rather than a resolution.

Never report an incident resolved on the strength of a quiet dashboard alone. Name the signal you read and the window you read it over.
