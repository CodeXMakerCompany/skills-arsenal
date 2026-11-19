---
name: principle-type-system-discipline
description: Apply when designing types, reviewing a function signature, or writing code in any statically typed language. Make illegal states unrepresentable, brand semantic primitives, parse external data at boundaries, exhaust variants, derive from authoritative schemas.
---

# Type System Discipline

Make the compiler reject impossible states, mismatched primitives, and unhandled variants. A rule the compiler enforces is a rule that holds on every build; a rule in a comment holds until someone is in a hurry.

- **Make illegal states unrepresentable.** Model variants as a discriminated union rather than a bag of optional fields that can disagree with each other.
- **Brand semantic primitives.** If two arguments share a primitive type and mean different things (`userId` and `accountId`, both `string`; `priceCents` and `priceDollars`, both `number`), give each its own type and validate once at creation. The compiler then finds the argument you swapped.
- **External data is untyped until parsed.** JSON bodies, RPC payloads, CLI args, config, environment variables, database rows, queue messages, and model output all go through a parse function at the boundary that returns the typed model (principle-boundary-discipline).
- **Derive types from authoritative schemas.** Where a schema file, an OpenAPI document, or a migration owns a shape, derive the type from it rather than hand-rolling a parallel one that drifts.
- **Exhaust variants.** Every switch over a union has a final arm that fails to compile when a new variant is added.
- **Units in the type or the name.** `timeoutMs`, `sizeBytes`, `amountCents`. A bare `number` crossing three function boundaries will be interpreted in two units.

For TypeScript syntax, see the **typescript-best-practices** skill. For killing the comments this discipline makes redundant, see **comment-psycho**.
