---
name: principle-boundary-discipline
description: Apply when wiring validation, error handling, or framework adapters. Concentrate guards at system boundaries (HTTP handlers, CLI, config, queues, external APIs, model output); trust internal types and keep business logic in pure functions.
---

# Boundary Discipline

Validate, narrow types, and handle errors where data crosses a system boundary. Inside, trust the types: no re-validation, no redundant null checks.

The boundaries in a typical service: the HTTP handler, the queue consumer, the CLI args, the config and environment, every external API response, every database row, and every model output. A model's response is untrusted input like any other, and schema-validating it at the boundary is what turns a hallucinated field into a handled error instead of a crash three layers down.

Parse raw data into a domain type at the boundary. Keep transport and framework types out of the public surface: no `Request`, no `APIGatewayProxyEvent`, no ORM row shape in a function another module calls. Business logic lives in pure functions with no framework dependency, and the shell that calls them is thin.

Two tests:

- **Is this data crossing a boundary right now?** If not, the validation is redundant. Delete it.
- **Can this be a pure function the shell just calls?** If yes, extract it. The test suite stops needing a server.

The payoff shows up when the handler changes. Moving from Express to a Lambda handler, or from a queue to a webhook, should touch the shell and nothing else.
