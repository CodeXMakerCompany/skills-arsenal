# Perf issue

**You own the measurement story. Plan, review, verify the numbers.** Tie every fix to a measurement. Never read source in place of measuring.

1. **Write the claim you expect to make** before running anything, in the words you would ship: "p50 on the invoice export drops from 820 ms to 300 ms at 60k rows". The run tests that sentence.
2. **Capture a baseline** on the real path, and vet it with **benchmark-checklist** before planning anything from it. An untuned or unrepeatable baseline makes every later number meaningless.
3. **Name the limiter** (principle-explain-the-number). CPU, I/O wait, a lock, a round trip per row, a cold start, a model call. From a profile or counters taken during a run, never from reading the code. For a Lambda path, separate cold start from warm. For an LLM path, separate time to first token from total, and tokens from network.
4. **Fix one thing, measure, keep or revert.** Never stack untested changes. Alternate the sides (A, B, A, B) so warmup and drift favor neither.
5. **Check the end-to-end share.** A helper that is 1% of the request can make the request at most 1% faster, however fast it gets.
6. **Vet the final number** with **benchmark-checklist** again: errors counted, work proven to have happened, run count and spread reported, limiter named.
7. **Report one primary number** in the PR body with its unit, run count, range, and limiter. Put the raw runs in a linked artifact. If a latency fix changes cost, **cost-per-request** covers that side too.
