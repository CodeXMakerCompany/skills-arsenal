---
name: monthly-skills-checkup
description: Monthly audit and rewrite of the whole arsenal, category by category, against what changed in models, harness features, and the stack. Asks which model to tune for, scores every skill, rewrites the ones the new capabilities make weaker, and records what it did. Use for /monthly-skills-checkup, "skills checkup", "revisión mensual de skills", "are my skills still current", "update my skills for the new model".
---

# Monthly skills checkup

A skill is a prompt, and a prompt written for last quarter's model is quietly worse on this quarter's. The model got better at the thing the skill is hand-holding it through, a feature arrived that the skill works around, a model id in a table no longer exists, two skills drifted into saying the same thing, and the gap that mattered last month now has a tool for it.

This is the pass that fixes that, on a cadence, with a record. It rewrites skills. It is not a read-only audit.

**Run it monthly.** It takes real time and real tokens, so budget for it rather than squeezing it in.

---

## Step 0: Ask what to tune for

Ask first, before reading a single skill. Everything downstream depends on the answer.

**Question 1, the target model.** The arsenal is tuned for one primary model, with named exceptions per role.

- The strongest model currently available (the usual answer).
- A specific model the user names.
- The current target, unchanged, auditing only for drift and staleness.

List the models this environment actually offers before presenting the options. Never offer a model id you have not seen offered, and never construct one by appending a date or a version to a name you remember.

**Question 2, the depth.**

- **Full.** Every category, every skill, rewrites applied. The monthly default.
- **Targeted.** One or two categories the user names.
- **Staleness only.** Dead model ids, broken links, deprecated parameters, duplicate skills. No rewrites for capability.

**Question 3, the appetite.** How much rewriting is in scope: tighten in place, or restructure a skill whose shape no longer fits. Restructuring a skill the user relies on daily is a decision they get to make.

Record all three answers in the report. A checkup whose target model is not stated cannot be compared with the next one.

---

## Step 1: Inventory

Build the real list from disk, never from memory or from the README, which is itself an artifact that drifts.

```bash
find . -name SKILL.md | sed 's|/SKILL.md||' | sort
```

For each skill record: its category, its name, its description, its line count, the date of its last substantive commit (`git log -1 --format=%cI -- <path>`), and every cross-reference it makes to another skill.

Then reconcile three lists that should be identical: the directories on disk, the rows in `README.md`, and the rows in `SKILL-SELECTOR.md` and each `MAP.md`. **Any difference is a finding**, because a skill missing from the maps is a skill nobody reaches, and a map row pointing at nothing is a dead end mid-task.

---

## Step 2: Gather what changed

Fan out, one subagent per source, in parallel, on a mid-tier model. Each returns a short list of changes with a date and a citation. Null results are findings. **This step is evidence gathering, not recall**: a change you remember but cannot cite does not enter the report.

Sources, in order of how much they move the arsenal:

1. **The target model's own capabilities and prompting guidance.** New parameters, retired parameters, effort and thinking behavior, context window, caching rules, tool-use restrictions, output limits, pricing, and above all the model's documented prompting shifts. Load the `claude-api` skill for this rather than answering from memory, and read its migration guidance for the target model specifically.
2. **The harness.** New tool types, new slash commands, subagent and background capabilities, scheduling, artifacts, MCP, hooks, settings. A skill that tells an agent to do by hand what the harness now does natively is the most common rot in this arsenal.
3. **Pricing and model lineup.** Per-million input and output, cache read price, batch discount, what got cheaper, what was retired. Every model table and every cost example in the arsenal is downstream of this.
4. **The stack.** Whatever the arsenal's skills actually name: the cloud services, the frameworks, the IaC tooling, the observability and eval tooling, the engine versions. A deprecated API in a skill becomes a deprecated API in the code an agent writes from it.
5. **Upstream sources the arsenal was ported from.** Where a skill came from an upstream project, diff against its current version and decide per change whether to take it. Say which upstream commit you compared against.
6. **This arsenal's own record.** The last checkup's report, every `reflect` finding since, and the `correct` backlog. Learnings already captured do not need rediscovering.

---

## Step 3: Score every skill

Six axes, each one word: `ok`, `weak`, or `broken`.

| Axis | The question | `broken` looks like |
|------|--------------|---------------------|
| **Trigger** | Does the description fire when it should, and not otherwise? | Two skills that both answer to the same phrase, or a skill nobody has invoked since it was written |
| **Currency** | Does it name anything that no longer exists? | A retired model id, a removed parameter, a deprecated API, a renamed tool, a dead link |
| **Capability fit** | Does it hand-hold the target model through something it is now good at, or miss a feature that would make it stronger? | A step-by-step procedure for something the model now one-shots, or a manual workaround for a native feature |
| **Evidence bar** | Does it demand proof, or accept a claim? | "Verify the change works" with no named artifact, command, or output |
| **Overlap** | Does another skill already own this? | Two skills with the same first paragraph in different words |
| **Reach** | Is it findable from the maps and from the mode skill? | Present on disk, absent from every map |

Score the category too, not only its skills: a category where every skill is `ok` but the set has an obvious hole is a `weak` category, and that hole is the most valuable finding this pass produces.

---

## Step 4: Rewrite

One category at a time, worst-scoring first. Apply the smallest edit that fixes the finding (principle-laziness-protocol). Do not rewrite a skill that scored `ok` on all six axes, however tempting the prose is.

**The rewrite rules, in the order they usually bite:**

1. **Cut the scaffolding a stronger model no longer needs.** This is the biggest and least obvious win. Guidance written for a weaker model is over-prescriptive for a stronger one, and over-prescription measurably lowers output quality: it narrows the approach space and spends the model's attention on following steps rather than solving the problem. Replace a nine-step procedure with the goal, the constraints, and the bar. **Keep every step that encodes a fact the model cannot derive**: a real path, a required flag, a gotcha, an ordering that matters, a rule about what not to do.
2. **Delete the workarounds.** A feature arrived, so the workaround is now a detour that produces worse results than the native path.
3. **Fix every stale name.** Model ids, parameters, tool types, commands, file paths, prices, links. Grep the whole arsenal for each one rather than fixing the instance you happened to see.
4. **Raise the bar where the model can now clear it.** A check that was too expensive to demand last quarter may be routine now: a real run instead of a reasoned argument, a second model's review, a generated repro, a model-checked invariant.
5. **Tighten the trigger.** Rewrite the description so it names the phrases the user actually says, in both languages where they switch, and so it says what *not* to use it for when a sibling skill is the better route. A trigger fix is a description fix, not a body fix.
6. **Merge or split.** Two skills that overlap become one, with the loser deleted and its references repointed, not left as a stub. A skill doing three jobs badly splits.
7. **Leave the opinion alone.** The judgment calls in these skills are the point. Do not sand a strong position into a balanced survey because the prose felt sharp. The arsenal's value is that it decides things.

Then run **unslop** over every file you touched, and re-verify its frontmatter.

---

## Step 5: Fill the gaps

The holes Step 3 found in each category become proposals, not silent additions. For each: the gap, the trigger phrase that currently lands nowhere, what the skill would own, and which existing skill it would borrow from. The user picks. Writing a skill nobody asked for is how an arsenal gets to sixty skills with twelve that fire.

---

## Step 6: Verify

A checkup that breaks the arsenal is worse than no checkup.

- **Frontmatter parses** on every file touched, with a `name` matching its directory and a non-empty `description`.
- **Every cross-reference resolves.** Check every skill name mentioned in bold or in a path against the inventory from Step 1.
- **No duplicate names** anywhere in the tree.
- **The three lists match again:** disk, README, maps.
- **Spot-run two rewritten skills** end to end on a real task and compare against what the old version produced. A rewrite nobody ran is a draft (principle-prove-it-works). For a skill whose output is judgment rather than an artifact, run both versions on the same input and read them side by side.
- **Check the triggers you tightened** by naming, for each one, the phrase that should now fire it and the sibling phrase that should not.

---

## Step 7: Record it

Append to `Meta/monthly-skills-checkup/CHANGELOG.md`, newest first. Next month's run starts by reading this, so write it for that reader.

```
## 2026-11-18
Target model: <model id>   Depth: full   Appetite: tighten in place
Sources compared: <model guidance + date>, <harness changelog + date>, <upstream commit>
Scored: 71 skills, 13 categories
Rewritten: 9 (list, one line each with the axis that triggered it)
Merged: 1 (what into what)
Deleted: 0
Gaps proposed: 3 (list)   Accepted: 1
Verified: frontmatter, references, maps, 2 spot-runs
Left alone deliberately: <skill> because <reason>
```

Then report to the user: the three answers from Step 0, the score table by category, what you rewrote and why, what you proposed, what you verified and how, and the one thing in the arsenal you would change next month if nothing else changed.

---

## What this pass does not do

- **It does not touch the creative-pipeline skills' voice.** The Spanish content skills (`anti-slop` and the script skills) encode a register, and a model upgrade is not a reason to rewrite how someone sounds. Audit them for currency and triggers only, unless the user says otherwise.
- **It does not chase every upstream change.** A diff against an upstream project is input, not instruction. Take what fits this arsenal and say what you rejected.
- **It does not add a skill per finding.** Most findings are edits. A new skill needs a trigger phrase that currently lands nowhere.
- **It does not rewrite on taste.** Every edit traces to a scored axis, with the evidence from Step 2 attached. An edit you cannot trace that way is the one to skip.
