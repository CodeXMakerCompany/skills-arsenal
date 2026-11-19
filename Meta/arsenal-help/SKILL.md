---
name: arsenal-help
description: Route a task to the right skill in this arsenal, explain how the categories fit together, and answer "which skill do I use for this". Use for /arsenal-help, "which skill", "what skills do I have", "qué skill uso", "how do I use this arsenal", or when a task could match several skills.
---

# Arsenal help

Route the task. Do not do the task.

Read `ARSENAL-MAP.md` at the repo root for the category graph, then the `MAP.md` of whichever category the task lands in. Those two files are the source of truth for what exists, and this skill is the reasoning over them.

## Routing

Ask one question: **what is the shape of the work?** Not what domain it is in.

| The work is... | Start at |
|----------------|----------|
| Anything non-trivial, and you want it run well | **codex-mode**, then its playbook |
| Understanding something that exists | `Communication`: **how** for mechanism, **why** for rationale, **teach** for a person |
| Deciding a shape before writing code | `Agentic`: **architect**, or **arena** when it is contested |
| Writing or changing code | `Development`, under the relevant `Principles` |
| Proving something works, or breaking it on purpose | `Verification` |
| Shipping, reviewing, or gating a change | `Security`: **ai-diff-review**, then **nexus-guard** |
| An LLM feature going to production | `AIEngineering`, with `Security`'s **llm-threat-model** |
| What something costs | `FinOps`: **cost-per-request** |
| Pipelines, infrastructure, deploys, observability | `Platform` |
| Parallel work, long runs, picking up where you left off | `Agentic` |
| A recurring job that should run itself | `Automations` |
| The arsenal itself | `Meta` |
| Video, scripts, narration, content | the root content skills, listed in `ARSENAL-MAP.md` |
| Games, 3D, audio, sprites | `Videogames`, `3DModeling`, `Audio`, `Graphics2D` |

## When several skills match

- **Name the one that owns the deliverable**, then the ones that gate it. A feature is `Development` work gated by `Verification` and `Security`, not a three-way tie.
- **Prefer the narrower skill.** **tdd** beats **figure-it-out** for a bug with an obvious test. **figure-it-out** is for work no narrower skill fits, and reaching for it first is how a 20-minute task becomes a phased program.
- **Say when the answer is no skill.** A one-line question, a typo, a quick read: answer it. Routing a trivial task through a playbook is overhead with ceremony.

## When nothing matches

Say so plainly, answer the task directly, and name the gap. Collect it for **monthly-skills-checkup**, which decides whether it earns a new skill. Do not invent a skill name that does not exist, and do not stretch an existing skill's description to cover something it does not do.

## Answering "what do I have"

Give the category, the count, and the two or three skills in it they would actually reach for. Nobody wants a list of seventy. If they ask what a specific skill does, give its one-line purpose and the phrase that triggers it.
