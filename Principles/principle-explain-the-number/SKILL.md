---
name: principle-explain-the-number
description: Apply before you measure, and before you trust, report, or act on a number you measured: a speedup, a regression, a throughput, a latency, a cost per request, or an eval result. Find what limits it, and rule out that it measured something other than the work you think.
---

# Explain the Number

- **Write the decision before you run.** Name the result that would change it, and the noise floor. Stop when the run-to-run spread is larger than the effect.
- **Ask "why not double?"** Name the resource or code path that bounds the result, from a profile or counters taken during a run. A guess from reading the code is not a limiter. Watch the load generator too: if it saturates first, you measured the load generator.
- **List what else the number could be measuring** and rule out each with evidence: errors returning fast, cached or skipped work, code that never ran, an untuned side, noise, a piece too small to matter, a cold start averaged in with warm ones.
- **Keep the run count, the spread, and the limiter with the number.** "40% faster" with none of those attached is a rumor. "p50 820 ms to 300 ms, median of 7 runs a side, range 290 to 315, bound by one round trip per row" is a result.

For a performance number, run the **benchmark-checklist** skill. For a cost number, run **cost-per-request**: the same discipline applies, and a cost measured on one request shape says nothing about the traffic mix. For an eval result, ask whether every run did the task, whether the gap holds across trials and models, and whether the scenario matters.

A number nobody can explain is worse than no number, because people act on it.
