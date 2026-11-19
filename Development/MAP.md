# Development

Code craft at the keyboard. Language-level and shape-level, under the rules in [`Principles`](../Principles/MAP.md).

```
Development/
├── comment-psycho/            ship with zero comments: facts go in names and types
├── typescript-best-practices/ the compiler does the work: unions, brands, boundaries
└── state-machine-architect/   FSMs: when, transition tables, async-safe, testing
```

## Route

| Situation | Skill |
|---|---|
| Reading or editing any `.ts` / `.tsx` | `typescript-best-practices` |
| A comment you are about to write, or a diff full of them | `comment-psycho` |
| Phases, modes, turns, lifecycles, UI flows | `state-machine-architect` |
| Deciding the shape before any of this | `architect` in [`Agentic`](../Agentic/MAP.md) |
| The rule behind a review comment | the leaf in [`Principles`](../Principles/MAP.md) |

## How the three fit together

They are one argument in three places: **put the fact where it is enforced.**

- `state-machine-architect` puts it in a **structure**, so invalid states cannot be reached.
- `typescript-best-practices` puts it in a **type**, so the compiler rejects it.
- `comment-psycho` removes the **prose** that was standing in for both, and names what is left.

Run them in that order on new code. A comment that survives a correct state machine and a correct type is usually one of the few that earns its place.

## comment-psycho has two modes

- **The standard**, which is the body of the skill: the exemption list, the five moves, the naming and typing laws, and the ship gate.
- **The adversarial pass**, which spawns a reviewer that has never seen your intent, because the author of a comment is its worst judge. You then judge the report rather than applying it.

## Where the other half lives

This category is deliberately small. Most "development" work in this arsenal is owned elsewhere, because the hard part is rarely the syntax:

| Work | Lives in |
|---|---|
| Deciding the shape | `architect`, `arena` in [`Agentic`](../Agentic/MAP.md) |
| Proving it works | [`Verification`](../Verification/MAP.md) |
| Reviewing the diff | `ai-diff-review` in [`Security`](../Security/MAP.md) |
| Unreal and C++ patterns | [`Videogames`](../Videogames/MAP.md), which has its own 35 |
| The 24 rules | [`Principles`](../Principles/MAP.md) |

## Known gap

No Python equivalent of `typescript-best-practices`, despite Python being half the stack. The same discipline applies (`NewType`, `Literal`, frozen dataclasses, `Protocol`, `assert_never`, strict type checking in CI) and it currently lives scattered across `principle-type-system-discipline` and `principle-boundary-discipline` rather than in one place. Logged for `monthly-skills-checkup`.
