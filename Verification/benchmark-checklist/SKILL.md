---
name: benchmark-checklist
description: Vet a performance measurement (limiter, tuning, limits, errors, repeatability, relevance, and whether the work happened) before you report or act on it. Use whenever you run a benchmark or report a speedup, a regression, a latency, or a throughput you measured.
---

# Benchmark checklist

Use this whenever you produce a performance number: a PR's before and after, a regression claim, a library or config choice, a load test. Answer each question with evidence from a run, not a guess about the code.

For a ballpark the user asked for, one run is enough. Still check questions 4 and 7, and say it is one run. Skip the rest unless that run looks wrong. **A choice between options is never a ballpark.**

## Before you run anything

- Write the claim you expect to make, in the words you would ship: "the invoice export is 30% faster at p50 on the 60k-row dataset". The questions test that sentence.
- Read the measurement script. Note what it times, what it counts, and what it ignores.
- Check the machine. Load average and core count. If it is busy, find out what is running. If you cannot stop it, interleave the sides so both see the same noise, and say so in the report.

## The questions

1. **Why not double?** Name the limiter. Profile in a run you do not report, because profilers slow the work down. CPU per process, a runtime profiler, I/O wait, syscall counts, then map the hot spot to source. Watch the load generator: if it saturates first, you measured the load generator. If a change did not move the number, the limiter explains why.
2. **Was it tuned?** Run every side the way production runs it: release build, production flags and env, connection pools, batching, caches as warm or cold as production sees them, same versions, same data. If one side runs on defaults, you compared configurations, not implementations. A limiter that is a setting (a commit per row, a debug build, a missing index, a 128 MB Lambda) means that side is untuned. Tune it and measure again before picking a winner.
3. **Did it break limits?** Do the arithmetic. Bytes per second against disk and network bandwidth, operations per second times cost per operation against your cores, time saved against the time the changed piece took. Removing a piece that is 10% of the run can make the run at most about 11% faster. A result past a limit measured something else: a cache, a no-op, or a bug.
4. **Did it error?** Count failures and non-success responses, and check the outputs are correct, not just present. Rejections are often fast and timeouts are slow, so errors move the number in both directions. If the script does not count errors, add the count.
5. **Does it reproduce?** At least 5 runs a side, alternating A, B, A, B, so warmup, lazy initialization, caches, and drift favor neither. Report the median and the range. **A gap smaller than the run-to-run variation is no measurable difference.**
6. **Does it matter?** Next to any micro result, measure the end-to-end path a user waits on, with realistic data and concurrency, and report the micro result as a share of the whole. A helper that is 1% of a request can make the request at most 1% faster.
7. **Did it even happen?** Confirm the work ran inside the timed region: the request reached the server, the rows were written, the bytes were read, the result was used. Lazy code and timeouts produce numbers for work that never happened.

## Report

- **Lead with the verdict:** faster, slower, no measurable difference, or inconclusive.
- **Give the number with its unit, the run count, the range, and the limiter.** For example: "p50 820 ms to 300 ms, median of 7 runs a side, range 290 to 315 ms after, bound by one round trip per row."
- **Call it inconclusive** when you claim a difference but cannot name the limiter, when a side ran untuned, or when you could not check questions 4 and 7. Name the gap.
- **Keep a PR body to one primary number.** Put the runs, the range, and the limiter evidence in a linked artifact.

For a latency number on a model call, separate time to first token from total, and tokens generated from network time. For the money side of the same change, run **cost-per-request**.
