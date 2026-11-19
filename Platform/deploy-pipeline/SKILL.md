---
name: deploy-pipeline
description: Cut deploy time and make deploys boring: find where the pipeline's minutes go, parallelize and cache what is safe, add the gates that belong there, and keep rollback one command. Use for /deploy-pipeline, "the pipeline is slow", "set up CI/CD", "el deploy tarda muchísimo", or when a deploy needs someone watching it.
---

# Deploy pipeline

Two goals, and they are not in conflict. **Fast**, so a fix reaches production in minutes and nobody batches up changes to avoid the pain. **Boring**, so nobody has to watch it.

Deploy time is a culture variable disguised as a technical one. A two-hour deploy means people deploy once a week, which means every deploy carries a week of changes, which means every failure is hard to attribute. Cutting it to fifteen minutes changes how the team works, not just how long they wait.

---

## 1. Measure the pipeline before changing it

Get the per-stage durations from the last 20 runs, not from the one you remember. Then:

- **Find the critical path.** Which stages are actually sequential, and which are sequential only because nobody questioned the order.
- **Find the waste.** Cold dependency installs with no cache, a full build when nothing in that package changed, a container image rebuilt from scratch, the whole test suite for a one-line copy change, a serial matrix that could be parallel, a queue wait for a runner.
- **Find the flakes.** A test that fails 5% of the time, retried twice, is a 10% tax on every deploy plus the trust cost. Quarantine it today and fix it as its own task.

Vet each measurement with **benchmark-checklist** before planning from it. A pipeline number from one run on a quiet afternoon is not a baseline.

## 2. Cut the time

In the order that usually pays:

1. **Cache the dependencies** on a lockfile hash key, and make the cache actually hit. Verify the hit rate rather than assuming it.
2. **Build once, promote the artifact.** Build the image or bundle a single time and move that exact artifact through the environments. Rebuilding per environment means production runs something that was never tested.
3. **Parallelize independent work.** Lint, typecheck, unit tests, and the build do not need each other.
4. **Split the slow suite** by timing, not by folder, and run only what the change can affect where you can determine that reliably. Where you cannot, keep the full suite and make it fast.
5. **Layer the container properly.** Dependencies in a layer above the source, so a source change does not reinstall anything.
6. **Shrink the deploy step itself.** A rolling deploy that waits for serial health checks across many instances is often most of the clock.

## 3. Put the right gates in the right place

Fast is not an excuse for an unguarded pipeline. Each gate goes where it is cheapest to fail:

- **On the PR:** lint, typecheck, unit and integration tests, the dependency and secret scan, **nexus-guard**, and for an LLM feature the eval set from **llm-evals**.
- **Before production:** migrations applied and verified, the artifact promoted (not rebuilt), smoke tests against the deployed thing.
- **After deploy:** the real signal read, not assumed. Error rate, p95, and the specific dashboard this change affects, over a stated window.

**A gate that is routinely skipped is not a gate.** Either make it fast enough to keep or delete it honestly.

## 4. Make failure cheap

- **Rollback is one command**, documented, tested, and runnable by anyone on call. A rollback nobody has rehearsed is a plan, not a capability.
- **Expand, migrate, contract** for every schema change, each step independently safe and reversible.
- **Feature flags for risky behavior**, with a default that is safe when the flag service is unreachable.
- **Progressive delivery where the stakes justify it:** a canary or a percentage rollout with an automatic trigger to halt.
- **The rollback trigger is written before the merge**, not improvised during an incident: which number, which dashboard, which threshold, who runs what.

## 5. Keep the pipeline honest

- **The pipeline is code**, in the repo, reviewed like any other change.
- **No credential in a pipeline variable** that a short-lived federated identity could provide instead.
- **The pipeline's own cost counts.** Runner minutes, build caches, artifact storage, and egress are a line on the bill (**cloud-cost-forecast**).
- **No manual step in the happy path.** Every manual step is a step someone will do differently at 2am.

## 6. Report

The before and after per stage, with the run count behind each number. What you parallelized, cached, or deleted. The gates and where each one runs. The rollback command and when it was last rehearsed. The flakes you quarantined. Then the one remaining bottleneck and what it would take to remove it.
