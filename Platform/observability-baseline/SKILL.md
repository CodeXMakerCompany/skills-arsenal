---
name: observability-baseline
description: Make a service debuggable from production without a redeploy: structured logs with a trace id, the four metrics that matter, traces across boundaries, and alerts on user-visible symptoms. Use for /observability-baseline, "add observability", "we cannot debug this in prod", "no tenemos visibilidad", or when a new service or LLM path goes live.
---

# Observability baseline

The test for whether a service is observable: **when it breaks at 2am, can you find out why without deploying anything?**

Not "do we have logs". Logs you cannot query by request id are a transcript of a conversation you cannot find.

---

## 1. Structured logs, correlated

- **JSON, one event per line, not a formatted sentence.** A grep-friendly log is a query-hostile log.
- **A trace id on every line**, generated at the edge and propagated through every call, every queue message, and every background job. This is the single highest-value thing on this list: without it you have logs from several services and no way to line them up.
- **The ids that let you find one case:** the request id, the user or tenant id, the resource id. Never the whole payload, because that is both a cost line and a data-protection problem.
- **Levels that mean something.** `error` is something a human must act on. Everything that is merely unusual is `warn` or `info`. A log at `error` for a handled validation failure trains everyone to ignore errors.
- **Never log a secret, a token, a full prompt with user data, or a complete request body.** Redact at the logging boundary, not by remembering to.
- **A retention you chose**, per log group, because indefinite retention is a recurring bill and a liability.

## 2. The metrics that matter

Start from what a user feels, not from what a machine reports. For any request-serving component:

- **Rate.** Requests per second, by route.
- **Errors.** The failure rate, with the error class as a dimension, separated from 4xx that are the client's fault.
- **Duration.** p50, p95, p99. **Never the average**, which hides the tail where the pain is.
- **Saturation.** The resource closest to full: connections, queue depth, memory, concurrency limit.

For a queue or an event path, add the consumer lag and the age of the oldest message, which is the metric that tells you a backlog is building before anyone notices.

**For an LLM path, four more are non-negotiable:** tokens in and out per request, cost per request, the failure and refusal rates, and time to first token. Without these, a model change is invisible until the bill or a complaint arrives (**inference-tuning**, **cost-per-request**).

Tag every metric with the environment, the version, and the route. A metric you cannot slice by deploy version cannot answer "did the deploy do this".

## 3. Traces across boundaries

Trace every hop a request makes: the gateway, the service, the database call, the queue publish and consume, the external API, the model call. The span that matters most is the one you did not instrument, because that is where the unexplained latency is.

Attach to each span the ids from the logs, so a slow trace leads to its log lines and back.

## 4. Alerts on symptoms, not causes

- **Alert on what a user experiences:** the error rate on a route, the p95 past a threshold they would notice, the queue age, the success rate of the one business transaction that matters. Not CPU. CPU is a dashboard, not a page.
- **Every alert names what to do.** A link to the runbook, the dashboard, and the rollback command. An alert that says only "p95 high" wakes someone up to go looking.
- **Every alert has an owner and a severity**, and a severity that does not page outside work hours unless it should.
- **A budget alarm is an alert**, with a threshold and a destination. Cost is an operational signal, especially where spend scales with traffic or with tokens.
- **Delete the alerts nobody acts on.** An alert that has fired 200 times and been acknowledged 200 times is noise with a pager attached, and it is why the real one gets missed.

## 5. Prove it

Pick a failure the service could plausibly have, then answer it from the tooling alone, with no new deploy: a single user reporting a slow request, a 2% error rate on one route, a backlog building, a cost spike. Walk from the alert to the dashboard to the trace to the log line.

**Where you cannot complete that walk, that gap is the finding**, and it is worth more than any amount of additional instrumentation added on principle.

## 6. Report

What exists now, what you added, the trace id's path through the system, the alert list with owners and thresholds, the retention and the cost of the telemetry itself, and the one failure you walked end to end as proof.
