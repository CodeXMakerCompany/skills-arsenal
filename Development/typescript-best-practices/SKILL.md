---
name: typescript-best-practices
description: TypeScript rules that make the compiler do the work: discriminated unions, branded types, boundary parsing, exhaustiveness, no casts. Use when reading or editing any .ts or .tsx file, reviewing TypeScript, or deciding how to type a boundary.
---

# TypeScript best practices

Apply the **principle-type-system-discipline** skill first. This is the syntax layer under it.

| Rule | Summary |
|------|---------|
| Discriminated unions | Model variants with a `kind` or `status` literal discriminant so impossible states cannot be represented. No optional-field bags. |
| Branded types | Brand primitives with `& { readonly __brand: "X" }` so they cannot be mixed up. Validate once at the boundary. A brand comes from a verifying type guard (`input is UserId`), never from `as`. |
| Constructive modeling | Build the shape so the illegal value cannot be constructed: `[T, ...T[]]` for non-empty, `[T, T][]` for pairs, `start` plus `duration` for a range. Not a runtime guard, not a wish for refinement types. |
| Simplest total type | Keep `T[]` while every operation on it stays total. Strengthen to `NonEmpty<T>` only where the loose type forces a `!`, a cast, or a "should never happen" throw. |
| `unknown` over `any` | External data is `unknown`. `any` disables the compiler exactly where you most need it. |
| Schemas before guards | Before hand-writing a property-by-property type guard, use the repo's runtime schema library and infer the type from the schema (`z.infer`). One source of truth beats two that drift. |
| No `as` casts | Every `as` is a runtime crash waiting for the right payload. Cast only after validation, and then prefer a guard that returns the branded type. |
| Narrowing hierarchy | Discriminant switch, then `in`, then `typeof`/`instanceof`, then a user-defined guard, then `as` as the admission of defeat. |
| Type guards must verify | A guard that lies is worse than `as`, because the bug now hides behind a name that says it is safe. Name them `isX` or `hasX`. |
| Exhaustiveness | End every switch over a union with `const _exhaustive: never = x;` so adding a variant is a compile error, not a silent fallthrough. |
| `satisfies` over `as` | Validates the value against the type without widening the literal types you wanted. |
| Boundary validation | Parse where data crosses in, into a named domain type. `Record<string, unknown>` stops at that parse. Trust the types inside (**principle-boundary-discipline**). |
| Derive, do not redeclare | Reach for `Pick`, `Omit`, `Parameters`, `ReturnType`, `Awaited`, `typeof` before declaring a parallel interface that will drift. |
| `readonly` by default | `readonly` fields and `readonly T[]` unless something must mutate. Mutability is a claim, so make someone state it. |
| Object args | Pass objects, not positional arguments, so call sites document themselves and boolean parameters disappear. Skip on genuinely hot paths. |
| No enums | Use a `const` object plus `typeof`-derived union, or a literal union. TypeScript `enum` has runtime weight and nominal surprises; `const enum` breaks under `isolatedModules`. |
| Errors are typed | Return a result union or throw a typed error class. `catch (e)` gives you `unknown`, so narrow it before reading `.message`. Assert on the error type callers branch on, never its text. |
| Real tests | Do not mock what you can run. Prefer the framework's real primitives and verify UI against a running build. Mock only what cannot run locally. |
| Structured telemetry | A structured logger with enough context to debug from an id. No `console.log` in shipped code. |
| `strict` is the floor | `strict: true`, plus `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, and `noFallthroughCasesInSwitch`. A codebase without these is typed by vibes. |

## React and Next.js specifics

- Type props as an explicit interface, never `React.FC`, which blocks generics and adds an implicit `children`.
- Server and client boundaries are boundaries: data crossing from a server component, a route handler, or a server action gets parsed, not asserted.
- A hook's return value is a tuple only when the order is obvious. Otherwise return an object, so a refactor cannot silently swap two values.
- `useState` with two booleans that must agree is a discriminated union waiting to be written (**principle-model-the-domain**).

## What this buys

Every rule here deletes a class of runtime error or a comment. If a rule in a review feels like ceremony, check which failure it removes. If it removes none in this codebase, say so and skip it (**principle-laziness-protocol**).
