---
name: automate-me
description: Turn the user's working conventions into a skill agents follow. Drafts or revises a personal -mode skill from evidence in recent sessions plus a short structured interview. Use for "automate me", "create or update my mode skill", "capture how I work", "quiero que trabajes como yo".
---

# Automate me

A guided flow for turning the user's working conventions into a skill agents will follow. The output is one `-mode` skill tailored to them. In this arsenal that skill is **codex-mode**, so a repeat run usually revises it rather than creating a new one.

This skill sequences three things: a mining pass over recent sessions, the authoring itself, and **unslop** over the prose. It does not replace them.

## 0. Check for an existing mode skill

Look for `*-mode/SKILL.md` in the arsenal and under `~/.claude/skills/`. If one exists, confirm the intent unless the user already said "update my skill":

- **Update it** (the default for a repeat run).
- **Start fresh** (rare, so ask why first).

Update mode changes the rest of the flow. Step 1 mines only history since the skill was last edited. Step 2 asks what changed or is missing, not what to capture from zero. Step 4 edits in place, preserving sections the user has not contradicted, revising the ones with new evidence, and adding sections only for genuinely new rules.

## 1. Mine their history

Survey recent sessions for recurring patterns. Fan out parallel subagents on `claude-sonnet-5-5` across slices of history, two to four weeks split three ways, so each slice has enough material. Each returns a short structured list of patterns with evidence pointers. Raw transcripts stay in the subagents.

Signals worth hunting:

- **Response preferences.** Length, tone, format, the "dumb it down" corrections.
- **Delegation habits.** Subagents, models per role, parallelism, what they always do themselves.
- **Verification posture.** What "done" means to them, unit tests against live repro, who reviews.
- **Code and prose discipline.** Style, principles they cite, lint tools, the thing they always rename.
- **Process conventions.** Branches, commits, PRs, review and merge tooling, how they ship.
- **Domain defaults.** The constraint they attach to every design, such as cost per request, the security gate, the observability baseline.
- **Meta preferences.** Fixing the skill mid-task, proposing new skills.

**Cross-check across slices.** A pattern in two or more slices is high confidence. A lone signal is weak and usually gets dropped.

## 2. Ask the user directly

Mining misses intent that has not come up yet. Use a structured question tool rather than asking them to type from scratch: one or two questions, four to six options each, multi-select for category questions. Start broad ("which areas matter most"), then follow up on what they picked. One free-form question at the end catches what the options missed.

Do not dump twenty questions.

## 3. Cluster the findings

Group the combined signals into sections. Use only what applies: response style, autonomy, understand-first, subagents and models, code and prose discipline, review and verification, process, domain non-negotiables, skills.

**codex-mode** shows the shape and the granularity. Read it for that, not for its content: the user's rules are not a copy of anyone else's.

## 4. Write it

Author the skill, then run **unslop** over it. Requirements:

- **Frontmatter that triggers.** The description names the phrases the user actually says, in both languages where they switch.
- **Every rule is actionable.** "Prefers quality" is not a rule. "Any design that calls a model ships with its cost per request" is.
- **Evidence behind each rule**, kept out of the skill but reported to the user, so they can overrule a pattern you misread.
- **No invented preferences.** A section you could not ground goes to the user as a question, not into the file.

## 5. Hand back

The skill's path, its sections, which rules came from mining and which from the interview, and what you dropped as low confidence. Then tell them the trigger phrase and suggest they run **reflect** at the end of a session that teaches it something new.
