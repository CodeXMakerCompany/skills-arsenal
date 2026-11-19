---
name: statechart
description: Model-check a system that moves between states (a checkout flow, a retry path, a lease, a protocol, an agent loop) with TLA+ and TLC, then draw it as a Mermaid statechart whose report gives the shortest path to each state that breaks a rule. Use for /statechart, "model check this", or to show a bug as a path through states.
---

# Statechart

A test checks the orders of events you thought of. A model checker checks every order in the model. Use this when the risk is sequencing: a retry that duplicates a charge, a lease whose holder changes mid-write, a webhook that arrives before the record it refers to, a flow that can reach "paid" twice.

The chart shows how the system moves between states, in the words of the person who reads it. That reader decides whether the behavior is right.

## Setup

Work in a scratch folder outside the repo. You need Java and TLC (`tla2tools.jar`). Install them with the repo's own tool manager where it has one (`mise`, `asdf`, `brew`, or a pinned container), record the exact version you used, and keep that version with the model so a rerun means the same thing.

## Write the spec

- **One variable per fact the reader cares about.** If a rule is about something the model has no variable for, add the variable. Never weaken a rule to make it hold.
- **Write each rule the reader agrees to as an `INVARIANT`.** "The customer is never charged twice." "A paid order always has a payment record." "Only the lease holder writes."
- **Write `Next` as a disjunction of named actions**, such as `PressPay \/ PaymentWebhookArrives \/ RetryTimerFires`. Without that, TLC labels every step `Next` and the output is unreadable.
- **A state with no step out breaks deadlock checking**, even when it is a correct end state. Add an action that is true only in the end states and changes nothing, such as `Done == phase \in {"paid", "failed"} /\ UNCHANGED vars`.
- **Keep the constants small.** Two users, three retries, one partition. A model checker explores every combination, so the state space explodes and a model that runs for an hour will not be rerun by anybody.

## Read the result

- **A counterexample is a sequence of steps, and that is the whole value.** Translate it into the code's own words before showing it to anyone: "the webhook arrives, the retry timer fires, the second charge goes out". A trace in TLA+ syntax lands with nobody.
- **A violation found means TLC prints the shortest path to it.** Shortest matters: it is the simplest story that produces the bug.
- **A pass covers the model and the bounds, not the system.** Say what the model leaves out: the network, the clock, the database's actual isolation level, the retry your HTTP client does on its own.
- **No violation with a tiny bound is weak evidence.** Say the bound.

## Draw the chart

Render the reachable states as a Mermaid `stateDiagram-v2`, labeling each state with what the reader can see or cares about ("Paying", "Lease held, write pending"), never with variable names. Label each arrow as the user experiences it ("you press pay", "the webhook arrives", "the connection drops").

Aim for about 20 arrows. Above that, merge states that behave the same and drop steps the reader does not need, such as a reset every state has. Two rules: keep every state on a bug path, and never merge two states that break different rules, because the reader then cannot see which rule breaks where. Say in the handoff which steps the chart hides.

## Hand off

Give the chart as a `mermaid` block to the person who has to decide. Add one line per bug: the rule, the reader's sentence for it, and the path. Give the command that regenerates the files, and the pinned tool version.

**Then replay each bug path against the real code**, as a test or a live repro, one step per action. If the bug does not occur, assume the model is wrong until you have shown it is not. A model-checker finding that nobody reproduced is a hypothesis with good manners.

Related: **state-machine-architect** designs the machine, this skill proves it, and **principle-separate-before-serializing-shared-state** is usually what a violation here is telling you.
