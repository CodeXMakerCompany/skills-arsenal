---
name: setup-arsenal
description: Configure which model and reasoning effort the arsenal uses per role, and write the rule file that overrides every skill default. Use for /setup-arsenal, "configure arsenal models", "set the model budget", or when a model id in a skill no longer exists.
---

# Set up the arsenal

Skills in this arsenal name a model per role. This skill writes the file that overrides those defaults in one place, so a model change is one edit rather than sixty.

## 1. Detect what is available

List the models this environment actually offers before proposing anything. Never write a model id you have not seen offered, and never invent a date suffix for one.

If a skill or an older rule file names a model that no longer exists, say so and replace it. A rejected model id silently falls back, which is how a cheap model ends up doing the work that needed the expensive one.

## 2. Ask for the budget

One question, four options, with the cost consequence stated for each:

- **Ceiling.** Every judgment role on the strongest available model at `xhigh`. For a week where correctness beats cost.
- **Balanced.** Judgment on the strongest model at `high`, bulk on the cheapest. The default.
- **Lean.** Judgment at `medium`, bulk and verification on the cheapest, panels cut to two seats.
- **Custom.** Walk the roles one at a time.

Then confirm whether a non-Anthropic model is configured, because **arena**, **interrogate**, and the cross-model review in **show-me-your-work** are weaker without a second vendor, and they must know to say so rather than quietly running single-vendor.

## 3. Write the rule file

Write `~/.claude/arsenal-models.md` with one line per role. Skills read these lines by name.

```
# defaults: 1
code and design: claude-opus-5-5 high
judgment and prose: claude-opus-5-5 high
hardest single task: claude-opus-5-5 xhigh
swarm workers: claude-haiku-5-5 medium
bulk summarization: claude-sonnet-5-5 medium
verification: claude-haiku-5-5 medium
arena runners: claude-opus-5-5 high, claude-sonnet-5-5 high
arena cross-judge pool: claude-sonnet-5-5 high
interrogate reviewers: claude-opus-5-5 high, claude-sonnet-5-5 high
deep reasoning: claude-fable-5-2 high
second vendor: none
```

Rules the file itself carries:

- `inherit-parent` or `auto` on a line means spawn without a model, on the parent's.
- A role with no line keeps the skill's own default.
- Effort is one of `low`, `medium`, `high`, `xhigh`, `max`. No role runs above `xhigh` except on an explicit request.
- Verification never runs on the same model as the code it checks, so that an author's blind spot is not also the checker's.
- Keep the `# defaults:` version line. A skill that finds an older version tells the user once per session to rerun this skill.

## 4. Say what changed

The file path, each role's line, what it costs relative to the previous setting, and which skills read which lines. Then name the one thing that will degrade at this budget, because every budget degrades something: lean budgets lose panel diversity first, and `medium` judgment loses the subtle design calls.
