# Meta

Skills about the skills. How the arsenal gets navigated, configured, corrected, and kept current.

```
Meta/
├── arsenal-help/              route a task to the right skill
├── setup-arsenal/             which model and effort per role
├── correct/                   make a repeated mistake impossible
├── reflect/                   turn this session's learnings into skill edits
├── automate-me/               turn how you work into a mode skill
└── monthly-skills-checkup/    audit and rewrite the whole arsenal, monthly
    └── CHANGELOG.md           what each run did. The next run reads this first
```

## Route

| Situation | Skill |
|---|---|
| "Which skill do I use for this?" | `arsenal-help` |
| A model id in a skill no longer exists | `setup-arsenal` |
| Changing the cost or quality budget | `setup-arsenal` |
| You corrected an agent for the same thing twice | `correct` |
| This session taught you something durable | `reflect` |
| `codex-mode` no longer matches how you work | `automate-me` |
| It has been a month, or a new model shipped | `monthly-skills-checkup` |

## The two feedback loops

They look similar and do different work. Using the wrong one is how a lesson ends up as prose nobody enforces.

**`reflect` → the skills.** A learning about *how to work* becomes an edit to a skill, usually its description. Session-scoped, run at the end of a session, needs approval before editing.

**`correct` → the repo.** A mistake that *agents keep making in one codebase* becomes architecture, a type, a lint, or a test in that repo. Repo-scoped, and it proves each new check fails on a real past mistake.

The test for which: would this stop a future agent in *any* repo (`reflect`), or only in *this* one (`correct`)? A rule that a lint could enforce always goes to `correct`, never into more prose. See [`principle-encode-lessons-in-structure`](../Principles/principle-encode-lessons-in-structure/SKILL.md).

## The cadence

| When | Run |
|---|---|
| End of a session that taught you something | `reflect` |
| The second time you correct the same mistake | `correct` |
| Monthly, or when a new model ships | `monthly-skills-checkup` |
| When the mode skill drifts from reality | `automate-me` |
| When a model id breaks or the budget changes | `setup-arsenal` |

## monthly-skills-checkup is the one with teeth

It asks three things first (the target model, the depth, the rewrite appetite), then scores all 125 skills on six axes: trigger, currency, capability fit, evidence bar, overlap, reach. Then it rewrites what scored badly and records the run in `CHANGELOG.md`.

Its most valuable rewrite rule is the least obvious: **cut the scaffolding a stronger model no longer needs.** Guidance written for a weaker model is over-prescriptive for a stronger one, and over-prescription measurably lowers output quality. Keep every step that encodes a fact the model cannot derive, and delete the rest.

Read `CHANGELOG.md` before running it. The baseline entry lists the known gaps the first real checkup should judge.

## Not here

- The style the arsenal runs on: `codex-mode` in [`Agentic`](../Agentic/MAP.md).
- Extracting a subset of skills into a project: [`SKILL-SELECTOR.md`](../SKILL-SELECTOR.md) at the root.
- The map this category navigates: [`ARSENAL-MAP.md`](../ARSENAL-MAP.md).
