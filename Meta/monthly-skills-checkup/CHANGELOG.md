# Checkup log

Newest first. Each entry is one run of `monthly-skills-checkup`. The next run reads this first.

## 2026-11-18 (baseline, not a checkup)

Target model: `claude-opus-5-5`   Depth: n/a   Appetite: n/a

Not an audit. This is the entry that records the state the first real checkup starts from.

- The arsenal was restructured into categories: `Agentic`, `Principles`, `Verification`, `Security`, `AIEngineering`, `FinOps`, `Platform`, `Communication`, `Meta`, `Automations`, alongside the existing `Development`, `3DModeling`, `Audio`, `Graphics2D`, `Narrative`, `Videogames` and the root content skills.
- 58 skills were ported from the upstream `pstack` plugin (`cursor/plugins`, subdirectory `pstack`, version 0.15.43) and rebalanced: model routing moved to the Claude 5 family, Cursor-specific paths moved to `~/.claude/`, and the cost, security, and AI-production triggers were added to the mode skill.
- `poteto-mode` became `codex-mode`. Ten skills were written fresh for the AI-production, security, FinOps, and platform categories, which the upstream plugin does not cover.
- Five more were written fresh afterwards, from the operator's own list: `clarity` (the requirements gate, which deliberately overrides `principle-never-block-on-the-human` for requirement-level ambiguity and states the boundary), plus `heatmap`, `forever-learning`, `feeling` and `enjoyable-talk` in `Communication`. `COMBOS.md` was added at the root for the small everyday sets. 130 skills at baseline.
- Known gaps at baseline, for the first checkup to judge: `statechart` documents the TLA+ method but ships none of upstream's model-checking scripts; `Automations` was adapted from upstream's Slack-specific triage bot and has never been run end to end; no skill covers data or analytics engineering.
- Nothing in this entry was scored on the six axes. The first checkup scores everything.
