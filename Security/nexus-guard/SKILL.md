---
name: nexus-guard
description: The last gate before anything reaches production: secret and dependency risk, security scan, AI-generated-code review, cost delta, observability, rollback. Returns a ships / doesn't-ship verdict with the failing line. Use for /nexus-guard, "gate this", "is this safe to merge", "¿esto puede salir a producción?", or before any merge or deploy.
---

# Nexus Guard

The validation layer that catches what humans miss before anything touches production. One gate, one verdict, named failures.

This runs at the head that will actually land, not at the commit you happened to review. A gate run on a stale head verified a different change.

**It does not fix anything.** It reports. Fixing is the author's job, under whichever skill owns the finding.

---

## The seven checks

Each one is `pass`, `fail`, or `not applicable`, and `not applicable` needs a reason.

### 1. Secrets and credentials

- No secret in the diff, in a test fixture, in a committed `.env`, in a snapshot, or in a log line the change adds. Scan the diff, and scan the history of any file the change moved.
- No credential widened: a new wildcard IAM action, a bucket policy opened, a security group with `0.0.0.0/0`, a service account given a role it did not need, a token's scope expanded, a public read added.
- Every new secret is read from the secret store at runtime, never baked into an image, a build arg, or a client bundle.
- **A found secret is an incident, not a review comment.** Rotate first, then clean history, then continue.

### 2. Dependency and supply-chain risk

- Every added or bumped dependency: why it was added, what it pulls in transitively, its license, its last release date, and its known advisories.
- A new direct dependency for something the standard library or an existing dependency already does is a `fail`. The cheapest dependency is the one you did not add.
- Lockfile present and consistent with the manifest. A lockfile-only diff nobody can explain is a `fail`.
- Install scripts in a new transitive dependency are worth reading, not trusting.

### 3. Security scan and the boundary

- Injection at every boundary the change touches: SQL and NoSQL query construction, shell invocation, template rendering, path construction, deserialization.
- AuthZ at the object level, not just the route. The classic hole: the endpoint checks that you are logged in and never checks that the record is yours.
- Input parsed into a typed model at the boundary (principle-boundary-discipline). Output encoded for its sink.
- For an LLM path, run **llm-threat-model** instead of improvising here. Prompt injection and data exfiltration have their own surface and this check does not cover them.

### 4. AI-generated code review

Any diff an agent wrote, yours included, goes through **ai-diff-review** for its risk tier before this gate. Nexus Guard checks that it happened and that tier-appropriate review was done.

The specific things to confirm, because they are what generated code gets wrong: an invented API or flag that happens to typecheck, a plausible-looking error path that swallows the error, a test that asserts on mocks, a retry with no backoff and no cap, an unbounded loop or query, a copied pattern from elsewhere in the repo that was already wrong.

### 5. Cost delta

- **Every change that adds a model call, a cloud resource, a cron, a queue, or a fan-out reports its cost per request** via **cost-per-request**, with the traffic assumption behind the number. No number, no merge.
- Named guards for the unbounded cases: a retry cap, a max token setting, a concurrency limit, a pagination bound, a timeout. An unbounded loop around a paid call is the standard way a bill triples overnight.
- For an infrastructure change, the plan's cost delta, not a guess.

### 6. Observability

- The change is debuggable from production without a redeploy: a structured log with the ids needed to trace one request, a metric for the thing that can degrade, a trace span across the new boundary.
- An alert on what actually matters to a user, not on CPU. For an LLM path, token spend, latency, and the failure and refusal rates are the ones that matter.
- No new silent failure path: nothing swallowed, nothing defaulted on error without a counter.
- See **observability-baseline** for what the floor is.

### 7. Rollback

- Stated before merge: the trigger (which number, on which dashboard, past which threshold), the command, and who can run it.
- A migration is reversible, or expand-migrate-contract with each step independently safe. An irreversible migration behind a feature flag is still irreversible.
- A feature flag with a default that is safe when the flag service is unreachable.

---

## The verdict

```
NEXUS GUARD — <repo>@<sha>

1 Secrets & credentials      pass
2 Dependency risk            pass
3 Security & boundaries      FAIL   src/api/invoices.ts:88 — record fetched by id with no owner check
4 AI-generated code review   pass   tier 2, reviewed by interrogate, 1 finding fixed
5 Cost delta                 FAIL   no cost per request for the new summarization call
6 Observability              pass
7 Rollback                   pass   flag invoices.v2, default off

VERDICT: DOESN'T SHIP — 2 failures
```

**Any `fail` means it does not ship.** Name the file, the line, and the one move that fixes it. Never soften a finding because the change is urgent: say the risk plainly and let the human override it in writing. An override is recorded in the PR with who approved it and what they accepted.

A `pass` says what was checked, on which head, and with what. It never claims more. "No secrets found by `<tool>` in the diff" is honest; "this change is secure" is not.
